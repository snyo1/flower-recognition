from fastapi import APIRouter, HTTPException, Depends, Request
from ..models.schemas import QARequest, QAResponse
from ..services.ai import generate_text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..services.db import get_db
from ..models.tables import QAHistory, User
from jose import jwt
from ..core.security import settings

router = APIRouter(prefix="/api/qa", tags=["智能问答"])

@router.post("/chat", response_model=QAResponse)
async def chat(request: QARequest, req: Request, db: AsyncSession = Depends(get_db)):
    try:
        # 尝试获取当前用户
        from .user import get_current_user
        current_user = None
        try:
            current_user = await get_current_user(req)
        except:
            pass

        # 构造提示词和历史记录
        prompt = request.question
        history = request.history or []
        
        # 调用AI
        ai_answer = generate_text(prompt, history=history)
        
        if ai_answer:
            # 记录历史到数据库
            if current_user:
                row = QAHistory(user_id=current_user.id, question=request.question, answer=ai_answer)
                db.add(row)
                await db.commit()
            return QAResponse(answer=ai_answer)
        
        # 兜底逻辑
        answer = "抱歉，我现在无法回答这个问题。建议您咨询专业花卉技师。"
        return QAResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")
