from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import FlowerKnowledge, FlowerKnowledgeList

router = APIRouter(prefix="/api/knowledge", tags=["知识库"])

# 模拟知识库数据
KNOWLEDGE_DB = [
    {
        "id": 1,
        "name": "月季",
        "family": "蔷薇科",
        "color": "红色、粉色、黄色等",
        "bloomingPeriod": "5月-10月",
        "description": "月季花被称为'花中皇后'，四季开花，花色丰富，芳香浓郁。",
        "careGuide": "喜阳光充足，耐旱耐寒，但不耐水湿。春秋季可每天浇水。",
        "flowerLanguage": "寓意纯洁的爱、热情和祝福。"
    },
    {
        "id": 2,
        "name": "玫瑰",
        "family": "蔷薇科",
        "color": "红色、粉色、白色等",
        "bloomingPeriod": "5月-10月",
        "description": "玫瑰是世界著名的观赏植物，花形优美，香气浓郁。",
        "careGuide": "喜温暖、阳光充足的环境，耐寒性较强，需要充足的阳光。",
        "flowerLanguage": "象征爱情、美丽和热情。"
    },
    {
        "id": 3,
        "name": "郁金香",
        "family": "百合科",
        "color": "红色、黄色、白色等",
        "bloomingPeriod": "3月-5月",
        "description": "郁金香是荷兰的国花，花形优美，色彩艳丽，寓意美好。",
        "careGuide": "喜凉爽湿润的气候，耐寒性强，适宜在排水良好的砂质土壤中生长。",
        "flowerLanguage": "象征爱情、荣誉和祝福。"
    },
    {
        "id": 4,
        "name": "康乃馨",
        "family": "石竹科",
        "color": "红色、粉色、白色等",
        "bloomingPeriod": "4月-6月",
        "description": "康乃馨是世界著名的切花之一，花色丰富，花期长。",
        "careGuide": "喜温暖、阳光充足的环境，耐寒性较差，冬季需移入室内。",
        "flowerLanguage": "象征母爱、温馨和祝福。"
    }
]

@router.get("/", response_model=FlowerKnowledgeList)
async def get_all_knowledge(keyword: str = ""):
    """
    获取所有花卉知识库数据
    支持关键词搜索
    """
    if keyword:
        filtered = [f for f in KNOWLEDGE_DB if keyword.lower() in f["name"].lower() or keyword.lower() in f["family"].lower()]
        flowers = [FlowerKnowledge(**f) for f in filtered]
    else:
        flowers = [FlowerKnowledge(**f) for f in KNOWLEDGE_DB]

    return FlowerKnowledgeList(flowers=flowers)

@router.post("/", response_model=FlowerKnowledge)
async def create_flower(flower: FlowerKnowledge):
    """
    添加花卉知识
    """
    new_id = max([f["id"] for f in KNOWLEDGE_DB], default=0) + 1
    new_flower = flower.dict()
    new_flower["id"] = new_id
    KNOWLEDGE_DB.append(new_flower)

    return FlowerKnowledge(**new_flower)

@router.put("/{flower_id}", response_model=FlowerKnowledge)
async def update_flower(flower_id: int, flower: FlowerKnowledge):
    """
    更新花卉知识
    """
    for i, f in enumerate(KNOWLEDGE_DB):
        if f["id"] == flower_id:
            updated_flower = flower.dict()
            updated_flower["id"] = flower_id
            KNOWLEDGE_DB[i] = updated_flower
            return FlowerKnowledge(**updated_flower)

    raise HTTPException(status_code=404, detail="花卉知识不存在")

@router.delete("/{flower_id}")
async def delete_flower(flower_id: int):
    """
    删除花卉知识
    """
    for i, f in enumerate(KNOWLEDGE_DB):
        if f["id"] == flower_id:
            KNOWLEDGE_DB.pop(i)
            return {"message": "删除成功"}

    raise HTTPException(status_code=404, detail="花卉知识不存在")
