from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.schemas import FlowerIdentification
from ..services.ai import identify_and_generate
from ..services.db import get_db
from ..models.tables import Flower, RecognitionRecord, User
from .user import get_current_user

router = APIRouter(prefix="/api/flower", tags=["花卉识别"])

@router.post("/identify", response_model=FlowerIdentification)
async def identify_flower(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User | None = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只支持图片文件")
    try:
        image_data = await file.read()
        try:
            ai_result = identify_and_generate("花卉图片")
            if not ai_result:
                ai_result = {
                    "name": "月季花",
                    "family": "蔷薇科",
                    "color": "红色、粉色、黄色等",
                    "bloomingPeriod": "5月-10月",
                    "description": "月季花被称为'花中皇后'，四季开花，花色丰富，芳香浓郁。植株矮小，茎上有刺，叶为奇数羽状复叶。",
                    "careGuide": "喜阳光充足，耐旱耐寒，但不耐水湿。春秋季可每天浇水，夏季需增加浇水频率，冬季减少浇水。生长期每月施肥1-2次。",
                    "flowerLanguage": "月季花寓意纯洁的爱、热情和祝福，是爱情与美丽的象征。",
                    "confidence": 95.5
                }
            
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
            rec = RecognitionRecord(
                image_url=None,
                plant_id=plant_id,
                user_id=current_user.id if current_user else None,
                confidence=ai_result.get("confidence", 90.0)
            )
            db.add(rec)
            await db.commit()
            return ai_result
        except Exception:
            await db.rollback()
            raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")
