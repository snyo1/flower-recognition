from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from ..services.db import get_db
from ..models.tables import User, Feedback, Comment, Flower # Assuming Flower is used for knowledge
from ..models.schemas import UserSchema, FeedbackSchema, CommentSchema, FlowerKnowledge # Import schemas
from ..core.security import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])

# Knowledge Management (example from prompt, using Flower model as knowledge)
@router.get("/knowledge/list", response_model=list[FlowerKnowledge])
async def get_knowledge_list_admin(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if current_admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    result = await db.execute(select(Flower).order_by(desc(Flower.created_at)))
    flowers = result.scalars().all()
    return flowers

# User Management
@router.get("/user/list", response_model=list[UserSchema])
async def get_user_list_admin(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if current_admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    result = await db.execute(select(User).order_by(desc(User.registration_date)))
    users = result.scalars().all()
    return users

@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if current_admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    user_to_delete = await db.get(User, user_id)
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await db.delete(user_to_delete)
    await db.commit()
    return

# Feedback Management
@router.get("/feedback/list", response_model=list[FeedbackSchema])
async def get_feedback_list_admin(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if current_admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    result = await db.execute(select(Feedback).order_by(desc(Feedback.created_at)))
    feedbacks = result.scalars().all()
    return feedbacks

# Comment Management
@router.get("/comment/list", response_model=list[CommentSchema])
async def get_comment_list_admin(
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if current_admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    result = await db.execute(select(Comment).order_by(desc(Comment.created_at)))
    comments = result.scalars().all()
    return comments

@router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_admin(
    comment_id: int,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if current_admin.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    comment_to_delete = await db.get(Comment, comment_id)
    if not comment_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    await db.delete(comment_to_delete)
    await db.commit()
    return