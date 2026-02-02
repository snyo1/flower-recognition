from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..services.db import get_db
from ..models.tables import User, RecognitionRecord
from ..core.security import settings
from jose import jwt
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/api/user", tags=["用户"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")
        
    result = await db.execute(select(User).filter(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "registration_date": current_user.registration_date
    }

@router.get("/stats")
async def stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 识别次数
    rec_count = (await db.execute(select(func.count(RecognitionRecord.id)).filter(RecognitionRecord.user_id == current_user.id))).scalar() or 0
    # 收藏次数
    from ..models.tables import Favorite
    fav_count = (await db.execute(select(func.count(Favorite.id)).filter(Favorite.user_id == current_user.id))).scalar() or 0
    # 问答次数
    from ..models.tables import QAHistory
    qa_count = (await db.execute(select(func.count(QAHistory.id)).filter(QAHistory.user_id == current_user.id))).scalar() or 0
    return {
        "recognitionCount": rec_count,
        "favoritesCount": fav_count,
        "qaCount": qa_count,
    }
