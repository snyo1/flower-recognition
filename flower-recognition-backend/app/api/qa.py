import asyncio
from fastapi import APIRouter, HTTPException, Depends
from ..models.schemas import QARequest, QAResponse
from ..services.ai import generate_text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..services.db import get_db
from ..models.tables import QAHistory, User
from .user import get_current_user, get_current_user_optional

router = APIRouter(prefix="/api/qa", tags=["智能问答"])

@router.post("/chat", response_model=QAResponse)
async def chat(request: QARequest, current_user: User | None = Depends(get_current_user_optional), db: AsyncSession = Depends(get_db)):
    try:
        prompt = request.question
        history = request.history or []

        ai_answer = await asyncio.to_thread(generate_text, prompt, history)

        if ai_answer:
            if current_user:
                row = QAHistory(user_id=current_user.id, question=request.question, answer=ai_answer)
                db.add(row)

                history_stmt = select(QAHistory).filter(QAHistory.user_id == current_user.id).order_by(QAHistory.created_at.desc())
                history_res = await db.execute(history_stmt)
                user_history = history_res.scalars().all()
                if len(user_history) > 10:
                    ids_to_keep = [h.id for h in user_history[:10]]
                    del_stmt = delete(QAHistory).filter(QAHistory.user_id == current_user.id, ~QAHistory.id.in_(ids_to_keep))
                    await db.execute(del_stmt)

                await db.commit()
            return QAResponse(answer=ai_answer)

        answer = "抱歉，我现在无法回答这个问题。建议您咨询专业花卉技师。"
        return QAResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")

@router.get("/history")
async def get_qa_history(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(QAHistory).filter(QAHistory.user_id == current_user.id).order_by(QAHistory.created_at.desc()).limit(10)
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [
        {
            "id": row.id,
            "question": row.question,
            "answer": row.answer,
            "created_at": row.created_at.isoformat()
        }
        for row in rows
    ]

@router.delete("/history/{history_id}")
async def delete_qa_history(history_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(QAHistory).filter(QAHistory.id == history_id, QAHistory.user_id == current_user.id)
    result = await db.execute(stmt)
    row = result.scalars().first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(row)
    await db.commit()
    return {"message": "删除成功"}
