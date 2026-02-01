from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from ..services.db import get_db
from ..models.tables import User, VerificationCode
from ..core.security import verify_password, get_password_hash, create_access_token
from ..services.email_service import send_verification_email
from datetime import datetime, timedelta
import random
import string
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/auth", tags=["认证"])

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    code: str

class UserLogin(BaseModel):
    username: str
    password: str
    remember: bool = False

class StartReset(BaseModel):
    email: EmailStr
    code: str

class DoReset(BaseModel):
    email: EmailStr
    code: str
    password: str

class EmailRequest(BaseModel):
    email: EmailStr

@router.get("/check-username")
async def check_username(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.username == username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    return {"message": "用户名可用"}

@router.post("/valid-register-email")
async def valid_register_email(data: EmailRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(User).filter(User.email == data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="该邮箱已被注册")
    
    code = ''.join(random.choices(string.digits, k=6))
    vc = VerificationCode(
        email=data.email,
        code=code,
        type="register",
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(vc)
    await db.commit()
    
    await send_verification_email(data.email, code, "register")
    return "验证码已发送"

@router.post("/valid-reset-email")
async def valid_reset_email(data: EmailRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(User).filter(User.email == data.email))
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="该邮箱未注册")
        
    code = ''.join(random.choices(string.digits, k=6))
    vc = VerificationCode(
        email=data.email,
        code=code,
        type="reset",
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(vc)
    await db.commit()
    
    try:
        await send_verification_email(data.email, code, "reset")
    except Exception as e:
        print(f"Email send error: {e}")
        raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(e)}")
    return "验证码已发送"

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verify code
    result = await db.execute(
        select(VerificationCode)
        .filter(
            VerificationCode.email == user.email,
            VerificationCode.code == user.code,
            VerificationCode.type == "register",
            VerificationCode.is_used == False,
            VerificationCode.expires_at > datetime.utcnow()
        )
        .order_by(VerificationCode.created_at.desc())
    )
    vc = result.scalars().first()
    if not vc:
        raise HTTPException(status_code=400, detail="验证码无效或已过期")
    
    vc.is_used = True
    
    # Check username again
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
         raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role="user"
    )
    db.add(new_user)
    await db.commit()
    return "注册成功"

@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    # Allow login by username or email
    result = await db.execute(
        select(User).filter(or_(User.username == data.username, User.email == data.username))
    )
    user = result.scalars().first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    
    access_token = create_access_token(
        subject=user.username,
        expires_delta=timedelta(days=7) if data.remember else timedelta(minutes=30)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "登录成功"
    }

@router.post("/start-reset")
async def start_reset(data: StartReset, db: AsyncSession = Depends(get_db)):
    # Verify code
    result = await db.execute(
        select(VerificationCode)
        .filter(
            VerificationCode.email == data.email,
            VerificationCode.code == data.code,
            VerificationCode.type == "reset",
            VerificationCode.is_used == False,
            VerificationCode.expires_at > datetime.utcnow()
        )
        .order_by(VerificationCode.created_at.desc())
    )
    vc = result.scalars().first()
    if not vc:
        raise HTTPException(status_code=400, detail="验证码无效或已过期")
    return "验证成功"

@router.post("/do-reset")
async def do_reset(data: DoReset, db: AsyncSession = Depends(get_db)):
    # Verify code again
    result = await db.execute(
        select(VerificationCode)
        .filter(
            VerificationCode.email == data.email,
            VerificationCode.code == data.code,
            VerificationCode.type == "reset",
            VerificationCode.is_used == False, # Should we mark used in start-reset? No, better in do-reset.
            VerificationCode.expires_at > datetime.utcnow()
        )
        .order_by(VerificationCode.created_at.desc())
    )
    vc = result.scalars().first()
    if not vc:
        raise HTTPException(status_code=400, detail="验证码无效或已过期")
    
    vc.is_used = True
    
    result = await db.execute(select(User).filter(User.email == data.email))
    user = result.scalars().first()
    if not user:
         raise HTTPException(status_code=404, detail="用户不存在")
         
    user.password_hash = get_password_hash(data.password)
    await db.commit()
    return "密码重置成功"
