from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from ..services.db import get_db
from ..models.tables import Comment, CommentLike, Flower, User
from .user import get_current_user

router = APIRouter(prefix="/api/comments", tags=["评论"])

@router.post("/add/{flower_id}")
async def add_comment(flower_id: int, content: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    row = Comment(user_id=current_user.id, flower_id=flower_id, content=content)
    db.add(row)
    await db.commit()
    return {"message": "评论已发布"}

@router.delete("/remove/{comment_id}")
async def remove_comment(comment_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    row = result.scalars().first()
    if not row or row.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该评论")
    await db.execute(delete(CommentLike).where(CommentLike.comment_id == comment_id))
    await db.execute(delete(Comment).where(Comment.id == comment_id))
    await db.commit()
    return {"message": "评论已删除"}

@router.post("/{comment_id}/like")
async def toggle_like(comment_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommentLike).filter(CommentLike.comment_id == comment_id, CommentLike.user_id == current_user.id))
    exists = result.scalars().first()
    if exists:
        await db.execute(delete(CommentLike).where(CommentLike.id == exists.id))
        await db.commit()
        return {"message": "已取消点赞"}
    like = CommentLike(comment_id=comment_id, user_id=current_user.id)
    db.add(like)
    await db.commit()
    return {"message": "已点赞"}

@router.get("/list/{flower_id}")
async def list_comments(flower_id: int, db: AsyncSession = Depends(get_db)):
    likes_count = func.count(CommentLike.id).label("likes")
    result = await db.execute(
        select(Comment, likes_count)
        .join(CommentLike, CommentLike.comment_id == Comment.id, isouter=True)
        .filter(Comment.flower_id == flower_id)
        .group_by(Comment.id)
        .order_by(likes_count.desc(), Comment.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": c.id,
            "user_id": c.user_id,
            "flower_id": c.flower_id,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
            "likes": likes,
        }
        for c, likes in rows
    ]
