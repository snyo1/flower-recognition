from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ..models.schemas import FlowerIdentification, BatchIdentificationResponse
from ..services.ai import identify_flower_multimodal, generate_flower_info
from ..services.storage import minio_service
from ..services.db import get_db
from ..models.tables import Flower, RecognitionRecord, User
from .user import get_current_user

router = APIRouter(prefix="/api/flower", tags=["花卉识别"])

async def _process_single_image(file: UploadFile, db: AsyncSession, current_user: User | None) -> dict:
    try:
        image_data = await file.read()
        
        # 1. 上传到 MinIO
        object_name = minio_service.upload_image(image_data, file.content_type)
        image_url = minio_service.get_url(object_name)
        
        # 2. 调用多模态 AI 识别
        ai_result = identify_flower_multimodal(image_data)
        
        # 如果多模态识别失败或由于 DeepSeek-V3 不支持 Vision，尝试备选方案：
        # 这里建议国内用户使用 智谱AI (GLM-4V) 或 通义千问 (Qwen-VL) 获取更好的多模态识别效果。
        # 如果 DeepSeek 识别出错误，我们返回一个基础结构。
        if "error" in ai_result:
            # 模拟识别（在没有真正 Vision 模型时）
            ai_result = {
                "name": "待人工确认",
                "family": "识别服务升级中",
                "color": "见图",
                "bloomingPeriod": "未知",
                "description": f"AI 识别暂时不可用: {ai_result['error']}",
                "careGuide": "建议咨询专业人士",
                "flowerLanguage": "未知",
                "confidence": 0.0
            }
        
        # 3. 查找或创建花卉知识
        flower_stmt = select(Flower).filter(Flower.name == ai_result["name"])
        result = await db.execute(flower_stmt)
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
            
        # 4. 记录识别历史（保存 MinIO 对象名作为 URL）
        rec = RecognitionRecord(
            image_url=object_name, 
            plant_id=plant_id,
            user_id=current_user.id if current_user else None,
            confidence=ai_result.get("confidence", 90.0)
        )
        db.add(rec)

        # 限制最近10条识别记录
        if current_user:
            history_stmt = select(RecognitionRecord).filter(RecognitionRecord.user_id == current_user.id).order_by(RecognitionRecord.created_at.desc())
            history_res = await db.execute(history_stmt)
            user_history = history_res.scalars().all()
            if len(user_history) > 10:
                ids_to_keep = [h.id for h in user_history[:10]]
                del_stmt = delete(RecognitionRecord).filter(RecognitionRecord.user_id == current_user.id, ~RecognitionRecord.id.in_(ids_to_keep))
                await db.execute(del_stmt)
        
        # 返回结果带上预览图
        ai_result["id"] = plant_id
        ai_result["imagePreview"] = image_url
        
        # 检查是否已收藏
        ai_result["isFavorite"] = False
        if current_user:
            from ..models.tables import Favorite
            fav_stmt = select(Favorite).filter(Favorite.user_id == current_user.id, Favorite.flower_id == plant_id)
            fav_res = await db.execute(fav_stmt)
            if fav_res.scalars().first():
                ai_result["isFavorite"] = True
                
        return ai_result
    except Exception as e:
        print(f"Process image error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/identify")
async def identify_flower(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User | None = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    
    result = await _process_single_image(file, db, current_user)
    await db.commit()
    return result

@router.post("/batch-identify")
async def batch_identify_flowers(files: List[UploadFile] = File(...), db: AsyncSession = Depends(get_db), current_user: User | None = Depends(get_current_user)):
    results = []
    for file in files:
        if not file.content_type.startswith("image/"):
            continue
        result = await _process_single_image(file, db, current_user)
        results.append(result)
    
    await db.commit()
    return {"results": results}

@router.get("/history")
async def list_recognitions(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(RecognitionRecord, Flower).join(Flower, RecognitionRecord.plant_id == Flower.id).filter(
        RecognitionRecord.user_id == current_user.id
    ).order_by(RecognitionRecord.created_at.desc())
    result = await db.execute(stmt)
    rows = result.all()
    # 限制最近10条
    rows = rows[:10]
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
            "timestamp": rec.created_at.isoformat()
        } for rec, flower in rows
    ]

@router.delete("/history/{history_id}")
async def delete_recognition(history_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(RecognitionRecord).filter(RecognitionRecord.id == history_id, RecognitionRecord.user_id == current_user.id)
    result = await db.execute(stmt)
    row = result.scalars().first()
    if not row:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(row)
    await db.commit()
    return {"message": "删除成功"}
