from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from ..services.db import get_db
from ..models.tables import Comment, CommentLike, CommentReply, Flower, User
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
    await db.execute(delete(CommentReply).where(CommentReply.comment_id == comment_id))
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
    items = []
    for c, likes in rows:
        username = c.user.username if c.user else "匿名用户"
        items.append({
            "id": c.id,
            "user_id": c.user_id,
            "username": username,
            "flower_id": c.flower_id,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
            "likes": likes,
            "reply_count": len(c.replies) if c.replies else 0,
        })
    return items

@router.post("/{comment_id}/reply")
async def add_reply(comment_id: int, content: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    reply = CommentReply(comment_id=comment_id, user_id=current_user.id, content=content)
    db.add(reply)
    await db.commit()
    return {"message": "回复已发布"}

@router.get("/{comment_id}/replies")
async def list_replies(
    comment_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    count_result = await db.execute(
        select(func.count(CommentReply.id)).filter(CommentReply.comment_id == comment_id)
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(CommentReply)
        .filter(CommentReply.comment_id == comment_id)
        .order_by(CommentReply.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    replies = result.scalars().all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "username": r.user.username if r.user else "匿名用户",
                "content": r.content,
                "created_at": r.created_at.isoformat(),
            }
            for r in replies
        ],
    }

@router.delete("/reply/{reply_id}")
async def remove_reply(reply_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CommentReply).filter(CommentReply.id == reply_id))
    reply = result.scalars().first()
    if not reply or reply.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该回复")
    await db.execute(delete(CommentReply).where(CommentReply.id == reply_id))
    await db.commit()
    return {"message": "回复已删除"}
