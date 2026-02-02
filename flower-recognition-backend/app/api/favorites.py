from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..services.db import get_db
from ..models.tables import Favorite, Flower, User
from .user import get_current_user

router = APIRouter(prefix="/api/favorites", tags=["收藏"])

@router.post("/add/{flower_id}")
async def add_favorite(flower_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Favorite).filter(Favorite.user_id == current_user.id, Favorite.flower_id == flower_id))
    exists = result.scalars().first()
    if exists:
        return {"message": "已收藏"}
    fav = Favorite(user_id=current_user.id, flower_id=flower_id)
    db.add(fav)
    await db.commit()
    return {"message": "收藏成功"}

@router.delete("/remove/{flower_id}")
async def remove_favorite(flower_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Favorite).where(Favorite.user_id == current_user.id, Favorite.flower_id == flower_id))
    await db.commit()
    return {"message": "取消收藏成功"}

@router.get("/list")
async def list_favorites(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Favorite, Flower)
        .join(Flower, Favorite.flower_id == Flower.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": fav.id,
            "flower_id": flower.id,
            "name": flower.name,
            "family": flower.family,
            "color": flower.color,
            "bloomingPeriod": flower.blooming_period,
            "description": flower.description,
            "timestamp": fav.created_at.isoformat(),
        }
        for fav, flower in rows
    ]
