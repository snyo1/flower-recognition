from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..services.db import get_db
from ..models.tables import User, RecognitionRecord, UserProfile
from ..core.security import settings
from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from ..services.storage import minio_service
import base64, re

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

async def get_current_user_optional(req: Request, db: AsyncSession = Depends(get_db)):
    auth = req.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except jwt.JWTError:
        return None
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 避免懒加载导致的会话分离错误，显式查询 UserProfile
    profile = (await db.execute(select(UserProfile).filter(UserProfile.user_id == current_user.id))).scalars().first()
    
    avatar_url = None
    if profile and profile.avatar_url:
        # 如果 avatar_url 是 MinIO 对象名，则生成预签名 URL
        if not profile.avatar_url.startswith("http"):
            avatar_url = minio_service.get_url(profile.avatar_url)
        else:
            avatar_url = profile.avatar_url

    return {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": (profile.nickname if profile and profile.nickname else current_user.username),
        "email": current_user.email,
        "role": current_user.role,
        "registration_date": current_user.registration_date,
        "avatar": avatar_url,
        "bio": (profile.bio if profile else "")
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

@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(UserProfile).filter(UserProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    
    avatar_url = None
    if profile and profile.avatar_url:
        if not profile.avatar_url.startswith("http"):
            avatar_url = minio_service.get_url(profile.avatar_url)
        else:
            avatar_url = profile.avatar_url
            
    return {
        "avatar": avatar_url,
        "nickname": profile.nickname or current_user.username if profile else current_user.username,
        "bio": profile.bio if profile else ""
    }

class UpdateProfileRequest(BaseModel):
    avatar: str | None = None
    nickname: str | None = None
    bio: str | None = None

def _save_avatar_if_data_url(avatar: str | None) -> str | None:
    if not avatar:
        return None
    # data URL: data:image/png;base64,....
    # 修复正则表达式，使其更通用且能处理各种图片类型
    m = re.match(r'^data:(image/[^;]+);base64,(.+)$', avatar)
    if not m:
        return avatar
    content_type = m.group(1)
    b64 = m.group(2)
    content = base64.b64decode(b64)
    # 调用 MinIO 服务上传
    object_name = minio_service.upload_image(content, content_type=content_type)
    return object_name

@router.put("/profile")
async def update_profile(req: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(UserProfile).filter(UserProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        avatar_obj = _save_avatar_if_data_url(req.avatar)
        profile = UserProfile(user_id=current_user.id, avatar_url=avatar_obj, nickname=req.nickname or current_user.username, bio=req.bio or "")
        db.add(profile)
    else:
        if req.avatar is not None:
            profile.avatar_url = _save_avatar_if_data_url(req.avatar)
        if req.nickname is not None:
            profile.nickname = req.nickname
        if req.bio is not None:
            profile.bio = req.bio
    await db.commit()
    return {"message": "个人信息已更新"}
