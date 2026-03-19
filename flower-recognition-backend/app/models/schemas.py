from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FlowerIdentification(BaseModel):
    name: str
    family: str
    color: str
    bloomingPeriod: str
    description: str
    careGuide: str
    flowerLanguage: str
    confidence: float
    type: Optional[str] = "未知"

class BatchIdentificationResponse(BaseModel):
    results: List[FlowerIdentification]

class QARequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []

class QAResponse(BaseModel):
    answer: str

class FlowerKnowledge(BaseModel):
    id: int
    name: str
    family: str
    color: str
    bloomingPeriod: str
    description: str
    careGuide: str
    flowerLanguage: str
    plantType: Optional[str] = "未知"

class FlowerKnowledgeList(BaseModel):
    flowers: List[FlowerKnowledge]

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    role: str
    registration_date: datetime
    # Add other fields as necessary, e.g., avatar, nickname, bio from UserProfile

class FeedbackSchema(BaseModel):
    id: int
    user_id: int
    content: str
    timestamp: datetime
    # Add other fields as necessary

class CommentSchema(BaseModel):
    id: int
    user_id: int
    flower_id: int # Assuming comments are related to flowers
    content: str
    timestamp: datetime
    # Add other fields as necessary
