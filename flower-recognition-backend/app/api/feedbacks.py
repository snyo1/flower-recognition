from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..services.db import get_db
from ..models.tables import Feedback, User
from .user import get_current_user

router = APIRouter(prefix="/api/feedbacks", tags=["反馈"])

@router.post("/add/{flower_id}")
async def add_feedback(flower_id: int, content: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    row = Feedback(user_id=current_user.id, flower_id=flower_id, content=content)
    db.add(row)
    await db.commit()
    return {"message": "反馈已提交"}
