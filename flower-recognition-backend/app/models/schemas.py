from pydantic import BaseModel
from typing import Optional, List

class FlowerIdentification(BaseModel):
    name: str
    family: str
    color: str
    bloomingPeriod: str
    description: str
    careGuide: str
    flowerLanguage: str
    confidence: float

class QARequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []

class QAResponse(BaseModel):
    answer: str

class FlowerKnowledge(BaseModel):
    name: str
    family: str
    color: str
    bloomingPeriod: str
    description: str
    careGuide: str
    flowerLanguage: str

class FlowerKnowledgeList(BaseModel):
    flowers: List[FlowerKnowledge]
