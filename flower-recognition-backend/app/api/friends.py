from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from ..services.db import get_db
from ..models.tables import User, FriendRequest, Friend, PrivacySettings, RecognitionRecord, Favorite
from .user import get_current_user

router = APIRouter(prefix="/api/friends", tags=["好友"])

@router.get("/search")
async def search_users(q: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).filter(or_(User.username.like(f"%{q}%"), User.email.like(f"%{q}%"))).limit(50)
    )
    rows = result.scalars().all()
    return [{"id": u.id, "username": u.username, "email": u.email} for u in rows]

@router.post("/request/{target_id}")
async def send_request(target_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.id == target_id:
        raise HTTPException(status_code=400, detail="不能向自己发起好友请求")
    req = FriendRequest(requester_id=current_user.id, target_id=target_id)
    db.add(req)
    await db.commit()
    return {"message": "好友请求已发送"}

@router.post("/respond/{request_id}")
async def respond_request(request_id: int, accept: bool, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FriendRequest).filter(FriendRequest.id == request_id))
    req = result.scalars().first()
    if not req or req.target_id != current_user.id:
        raise HTTPException(status_code=404, detail="请求不存在")
    req.status = "accepted" if accept else "rejected"
    if accept:
        db.add(Friend(user_id=current_user.id, friend_user_id=req.requester_id))
        db.add(Friend(user_id=req.requester_id, friend_user_id=current_user.id))
    await db.commit()
    return {"message": "已处理"}

@router.get("/list")
async def list_friends(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Friend, User).join(User, Friend.friend_user_id == User.id).filter(Friend.user_id == current_user.id)
    )
    rows = result.all()
    return [{"id": f.id, "user_id": u.id, "username": u.username, "email": u.email} for f, u in rows]

@router.get("/requests")
async def my_requests(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FriendRequest).filter(FriendRequest.target_id == current_user.id, FriendRequest.status == "pending"))
    reqs = result.scalars().all()
    return [{"id": r.id, "from_user_id": r.requester_id} for r in reqs]

@router.delete("/remove/{friend_user_id}")
async def remove_friend(friend_user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Friend).where(Friend.user_id == current_user.id, Friend.friend_user_id == friend_user_id))
    await db.execute(delete(Friend).where(Friend.user_id == friend_user_id, Friend.friend_user_id == current_user.id))
    await db.commit()
    return {"message": "好友已删除"}

@router.get("/info/{user_id}")
async def friend_info(user_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 必须是好友关系
    result = await db.execute(select(Friend).filter(Friend.user_id == current_user.id, Friend.friend_user_id == user_id))
    rel = result.scalars().first()
    if not rel:
        raise HTTPException(status_code=403, detail="仅好友可查看信息")
    # 获取隐私设置
    result = await db.execute(select(PrivacySettings).filter(PrivacySettings.user_id == user_id))
    ps = result.scalars().first()
    ps = ps or PrivacySettings(user_id=user_id)
    # 基础信息
    result = await db.execute(select(User).filter(User.id == user_id))
    u = result.scalars().first()
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    # 统计
    rec_count = 0
    fav_count = 0
    qa_count = 0
    if ps.show_recognition_count:
        rec_count = (await db.execute(select(RecognitionRecord).filter(RecognitionRecord.user_id == user_id))).scalars().unique().count()
    if ps.show_favorites_count:
        fav_count = (await db.execute(select(Favorite).filter(Favorite.user_id == user_id))).scalars().unique().count()
    # qa_count 通过历史表
    from ..models.tables import QAHistory
    if ps.show_qa_count:
        qa_count = (await db.execute(select(QAHistory).filter(QAHistory.user_id == user_id))).scalars().unique().count()
    info = {
        "username": u.username,
        "email": u.email if ps.show_email else None,
        "recognitionCount": rec_count if ps.show_recognition_count else None,
        "favoritesCount": fav_count if ps.show_favorites_count else None,
        "qaCount": qa_count if ps.show_qa_count else None,
    }
    return info

@router.post("/privacy/save")
async def save_privacy(settings: dict, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PrivacySettings).filter(PrivacySettings.user_id == current_user.id))
    ps = result.scalars().first()
    if not ps:
        ps = PrivacySettings(user_id=current_user.id)
        db.add(ps)
    ps.show_email = bool(settings.get("show_email", True))
    ps.show_recognition_count = bool(settings.get("show_recognition_count", True))
    ps.show_favorites_count = bool(settings.get("show_favorites_count", True))
    ps.show_qa_count = bool(settings.get("show_qa_count", True))
    ps.show_favorites_list = bool(settings.get("show_favorites_list", True))
    await db.commit()
    return {"message": "隐私设置已保存"}
