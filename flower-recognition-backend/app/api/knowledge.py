from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from ..models.schemas import FlowerKnowledge, FlowerKnowledgeList
from ..models.tables import Flower
from ..services.db import get_db

router = APIRouter(prefix="/api/knowledge", tags=["知识库"])

@router.get("/", response_model=FlowerKnowledgeList)
async def get_all_knowledge(keyword: str = "", db: AsyncSession = Depends(get_db)):
    try:
        q = select(Flower)
        if keyword:
            kw = f"%{keyword}%"
            q = q.filter((Flower.name.like(kw)) | (Flower.family.like(kw)) | (Flower.description.like(kw)))
        result = await db.execute(q)
        rows = result.scalars().all()
        flowers = [FlowerKnowledge(
            id=row.id,
            name=row.name,
            family=row.family,
            color=row.color,
            bloomingPeriod=row.blooming_period,
            description=row.description,
            careGuide=row.care_guide,
            flowerLanguage=row.flower_language,
        ) for row in rows]
        return FlowerKnowledgeList(flowers=flowers)
    except SQLAlchemyError:
        return FlowerKnowledgeList(flowers=[])

@router.post("/", response_model=FlowerKnowledge)
async def create_flower(flower: FlowerKnowledge, db: AsyncSession = Depends(get_db)):
    try:
        row = Flower(
            name=flower.name,
            family=flower.family,
            color=flower.color,
            blooming_period=flower.bloomingPeriod,
            description=flower.description,
            care_guide=flower.careGuide,
            flower_language=flower.flowerLanguage,
        )
        db.add(row)
        await db.commit()
        return flower
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="数据库错误")

@router.put("/{flower_id}", response_model=FlowerKnowledge)
async def update_flower(flower_id: int, flower: FlowerKnowledge, db: AsyncSession = Depends(get_db)):
    try:
        row = await db.get(Flower, flower_id)
        if not row:
            raise HTTPException(status_code=404, detail="花卉知识不存在")
        row.name = flower.name
        row.family = flower.family
        row.color = flower.color
        row.blooming_period = flower.bloomingPeriod
        row.description = flower.description
        row.care_guide = flower.careGuide
        row.flower_language = flower.flowerLanguage
        await db.commit()
        return flower
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="数据库错误")

@router.delete("/{flower_id}")
async def delete_flower(flower_id: int, db: AsyncSession = Depends(get_db)):
    try:
        row = await db.get(Flower, flower_id)
        if not row:
            raise HTTPException(status_code=404, detail="花卉知识不存在")
        await db.delete(row)
        await db.commit()
        return {"message": "删除成功"}
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="数据库错误")
