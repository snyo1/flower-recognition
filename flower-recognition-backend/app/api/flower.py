from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..models.schemas import FlowerIdentification, BatchIdentificationResponse
from ..services.ai import identify_and_generate
from ..services.db import get_db
from ..models.tables import Flower, RecognitionRecord, User
from .user import get_current_user

router = APIRouter(prefix="/api/flower", tags=["花卉识别"])

async def _process_single_image(image_data: bytes, db: AsyncSession, current_user: User | None) -> FlowerIdentification:
    try:
        ai_result = identify_and_generate(image_data=image_data)
        if not ai_result:
            raise Exception("AI识别返回空结果")
        
        # 查找或创建花卉知识
        result = await db.execute(select(Flower).filter(Flower.name == ai_result["name"]))
        existing = result.scalars().first()

        if not existing:
            f = Flower(
                name=ai_result["name"],
                family=ai_result["family"],
                color=ai_result["color"],
                blooming_period=ai_result["bloomingPeriod"],
                description=ai_result["description"],
                care_guide=ai_result["careGuide"],
                flower_language=ai_result["flowerLanguage"],
            )
            db.add(f)
            await db.flush()
            plant_id = f.id
        else:
            plant_id = existing.id
            
        # 记录识别历史
        rec = RecognitionRecord(
            image_url=None,  # 实际项目中应保存到云存储并记录URL
            plant_id=plant_id,
            user_id=current_user.id if current_user else None,
            confidence=ai_result.get("confidence", 90.0)
        )
        db.add(rec)
        return FlowerIdentification(**ai_result)
    except Exception as e:
        print(f"Process image error: {str(e)}")
        # 失败时返回兜底数据
        return FlowerIdentification(
            name="识别失败",
            family="未知",
            color="未知",
            bloomingPeriod="未知",
            description=f"识别过程中出现错误: {str(e)}",
            careGuide="请重试",
            flowerLanguage="无",
            confidence=0.0
        )

@router.post("/identify", response_model=FlowerIdentification)
async def identify_flower(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User | None = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    
    image_data = await file.read()
    result = await _process_single_image(image_data, db, current_user)
    await db.commit()
    return result

@router.post("/batch-identify", response_model=BatchIdentificationResponse)
async def batch_identify_flowers(files: List[UploadFile] = File(...), db: AsyncSession = Depends(get_db), current_user: User | None = Depends(get_current_user)):
    results = []
    for file in files:
        if not file.content_type.startswith("image/"):
            continue
        image_data = await file.read()
        result = await _process_single_image(image_data, db, current_user)
        results.append(result)
    
    await db.commit()
    return BatchIdentificationResponse(results=results)
