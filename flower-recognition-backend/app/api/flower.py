import asyncio
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..models.schemas import FlowerIdentification, BatchIdentificationResponse
from ..services.ai import identify_flower_multimodal, generate_flower_info
from ..services.storage import minio_service
from ..services.db import get_db
from ..models.tables import Flower, RecognitionRecord, User
from .user import get_current_user, get_current_user_optional

router = APIRouter(prefix="/api/flower", tags=["花卉识别"])


def _parse_confidence(raw) -> float:
    """将AI返回的置信度（可能是字符串或数字）规范化为0-100的浮点数"""
    if isinstance(raw, (int, float)):
        return max(0.0, min(100.0, float(raw)))
    if isinstance(raw, str):
        nums = re.findall(r'\d+\.?\d*', raw)
        if nums:
            return max(0.0, min(100.0, float(nums[0])))
    return 70.0


async def _process_single_image(file: UploadFile, db: AsyncSession, current_user: User | None) -> dict:
    image_data = await file.read()

    # 1. 上传图片到 MinIO（失败不终止）
    object_name = None
    image_url = ""
    try:
        object_name = minio_service.upload_image(image_data, file.content_type)
        image_url = minio_service.get_url(object_name)
    except Exception as e:
        print(f"MinIO 上传失败: {e}")

    # 2. 调用多模态 AI 识别
    try:
        ai_result = await asyncio.to_thread(identify_flower_multimodal, image_data)
    except Exception as e:
        print(f"AI识别异常: {e}")
        ai_result = {"error": str(e)}

    # 识别失败时返回友好占位结果，前端根据 failed=True 显示未识别界面
    if "error" in ai_result:
        return {
            "name": "未识别",
            "family": "-",
            "color": "-",
            "bloomingPeriod": "-",
            "description": "-",
            "careGuide": "-",
            "flowerLanguage": "-",
            "confidence": 0.0,
            "type": "未知",
            "imagePreview": image_url,
            "isFavorite": False,
            "failed": True,
        }

    # 规范化置信度
    confidence = _parse_confidence(ai_result.get("confidence", 70.0))
    ai_result["confidence"] = confidence

    # 3. 查找或创建花卉知识库
    try:
        flower_name = ai_result.get("name", "未知") or "未知"
        flower_stmt = select(Flower).filter(Flower.name == flower_name)
        result_db = await db.execute(flower_stmt)
        existing = result_db.scalars().first()

        if not existing:
            f = Flower(
                name=flower_name,
                family=ai_result.get("family", "未知"),
                color=ai_result.get("color", "未知"),
                blooming_period=ai_result.get("bloomingPeriod", "未知"),
                description=ai_result.get("description", ""),
                care_guide=ai_result.get("careGuide", ""),
                flower_language=ai_result.get("flowerLanguage", ""),
                plant_type=ai_result.get("type", "未知"),
            )
            db.add(f)
            await db.flush()
            plant_id = f.id
        else:
            plant_id = existing.id
            if not existing.plant_type and ai_result.get("type"):
                existing.plant_type = ai_result["type"]

        # 4. 记录识别历史
        rec = RecognitionRecord(
            image_url=object_name,
            plant_id=plant_id,
            user_id=current_user.id if current_user else None,
            confidence=confidence,
        )
        db.add(rec)

        # 限制最近10条
        if current_user:
            history_stmt = select(RecognitionRecord).filter(
                RecognitionRecord.user_id == current_user.id
            ).order_by(RecognitionRecord.created_at.desc())
            history_res = await db.execute(history_stmt)
            user_history = history_res.scalars().all()
            if len(user_history) > 10:
                ids_to_keep = [h.id for h in user_history[:10]]
                del_stmt = delete(RecognitionRecord).filter(
                    RecognitionRecord.user_id == current_user.id,
                    ~RecognitionRecord.id.in_(ids_to_keep),
                )
                await db.execute(del_stmt)

        ai_result["id"] = plant_id
        ai_result["imagePreview"] = image_url
        ai_result["isFavorite"] = False
        ai_result["failed"] = False

        if current_user:
            from ..models.tables import Favorite
            fav_stmt = select(Favorite).filter(
                Favorite.user_id == current_user.id, Favorite.flower_id == plant_id
            )
            fav_res = await db.execute(fav_stmt)
            if fav_res.scalars().first():
                ai_result["isFavorite"] = True

    except Exception as e:
        print(f"数据库操作失败: {e}")
        ai_result.setdefault("imagePreview", image_url)
        ai_result.setdefault("isFavorite", False)
        ai_result.setdefault("failed", False)

    return ai_result


@router.post("/identify")
async def identify_flower(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    result = await _process_single_image(file, db, current_user)
    try:
        await db.commit()
    except Exception as e:
        print(f"commit失败: {e}")
    return result


@router.post("/batch-identify")
async def batch_identify_flowers(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    results = []
    for file in files:
        if not file.content_type.startswith("image/"):
            continue
        result = await _process_single_image(file, db, current_user)
        results.append(result)
    try:
        await db.commit()
    except Exception as e:
        print(f"commit失败: {e}")
    return {"results": results}


@router.get("/history")
async def list_recognitions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(RecognitionRecord, Flower)
        .join(Flower, RecognitionRecord.plant_id == Flower.id)
        .filter(RecognitionRecord.user_id == current_user.id)
        .order_by(RecognitionRecord.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()[:10]
    return [
        {
            "id": rec.id,
            "imageUrl": minio_service.get_url(rec.image_url) if rec.image_url else None,
            "flowerName": flower.name,
            "family": flower.family,
            "color": flower.color,
            "bloomingPeriod": flower.blooming_period,
            "description": flower.description,
            "careGuide": flower.care_guide,
            "flowerLanguage": flower.flower_language,
            "confidence": float(rec.confidence or 0),
            "timestamp": rec.created_at.isoformat(),
        }
        for rec, flower in rows
    ]


@router.delete("/history/{history_id}")
async def delete_recognition(
    history_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(RecognitionRecord).filter(
        RecognitionRecord.id == history_id,
        RecognitionRecord.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    row = result.scalars().first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(row)
    await db.commit()
    return {"message": "删除成功"}
