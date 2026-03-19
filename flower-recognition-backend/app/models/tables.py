from typing import List, Optional
from datetime import datetime
from sqlalchemy import BigInteger, String, Text, DateTime, DECIMAL, ForeignKey, func, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    email: Mapped[Optional[str]] = mapped_column(String(128), unique=True, index=True)
    role: Mapped[str] = mapped_column(Enum("user", "expert", "admin"), default="user")
    status: Mapped[str] = mapped_column(Enum("active", "disabled"), default="active")
    registration_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(64))
    
    # 个人资料（通过 profile 关联存储）
    profile: Mapped[Optional["UserProfile"]] = relationship(back_populates="user", uselist=False)

    recognitions: Mapped[List["RecognitionRecord"]] = relationship(back_populates="user", lazy="selectin")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")
    feedbacks: Mapped[List["Feedback"]] = relationship(back_populates="user")
    qa_histories: Mapped[List["QAHistory"]] = relationship(back_populates="user")
    expert_application: Mapped[Optional["ExpertApplication"]] = relationship(back_populates="user", uselist=False)

class Flower(Base):
    __tablename__ = "flowers"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    family: Mapped[str] = mapped_column(String(128), nullable=False)
    color: Mapped[str] = mapped_column(String(256), nullable=False)
    blooming_period: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    care_guide: Mapped[str] = mapped_column(Text, nullable=False)
    flower_language: Mapped[str] = mapped_column(Text, nullable=False)
    plant_type: Mapped[Optional[str]] = mapped_column(String(64)) # 草本/木本/多肉/藤本
    status: Mapped[str] = mapped_column(Enum("draft", "pending", "published"), default="published")
    tags: Mapped[Optional[str]] = mapped_column(String(256)) # 逗号分隔的标签
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    recognitions: Mapped[List["RecognitionRecord"]] = relationship(
        back_populates="flower",
        foreign_keys="RecognitionRecord.plant_id"
    )
    comments: Mapped[List["Comment"]] = relationship(back_populates="flower")

class RecognitionRecord(Base):
    __tablename__ = "recognition_records"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    plant_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("flowers.id"))
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"))
    confidence: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    is_corrected: Mapped[bool] = mapped_column(default=False)
    corrected_plant_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("flowers.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    flower: Mapped[Optional["Flower"]] = relationship(
        back_populates="recognitions",
        foreign_keys=[plant_id],
        lazy="selectin"
    )
    corrected_flower: Mapped[Optional["Flower"]] = relationship(
        foreign_keys=[corrected_plant_id]
    )
    user: Mapped[Optional["User"]] = relationship(back_populates="recognitions", lazy="selectin")

class Comment(Base):
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    flower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("flowers.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Enum("pending", "approved", "rejected"), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    user: Mapped["User"] = relationship(back_populates="comments", lazy="selectin")
    flower: Mapped["Flower"] = relationship(back_populates="comments", lazy="selectin")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    flower_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("flowers.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Enum("pending", "processing", "resolved", "closed"), default="pending")
    reply_content: Mapped[Optional[str]] = mapped_column(Text)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    user: Mapped["User"] = relationship(back_populates="feedbacks", lazy="selectin")

class ExpertApplication(Base):
    __tablename__ = "expert_applications"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    proof_material: Mapped[str] = mapped_column(Text, nullable=False, comment="证明材料或图片链接")
    status: Mapped[str] = mapped_column(Enum("pending", "approved", "rejected"), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    user: Mapped["User"] = relationship(back_populates="expert_application")

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    type: Mapped[str] = mapped_column(Enum("register", "reset"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False)

class Favorite(Base):
    __tablename__ = "favorites"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    flower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("flowers.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    user: Mapped["User"] = relationship()
    flower: Mapped["Flower"] = relationship()

class CommentLike(Base):
    __tablename__ = "comment_likes"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    comment_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("comments.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class QAHistory(Base):
    __tablename__ = "qa_history"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id"), index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[Optional[str]] = mapped_column(Text)
    user: Mapped[Optional["User"]] = relationship(back_populates="qa_histories", lazy="selectin")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    nickname: Mapped[Optional[str]] = mapped_column(String(64))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user: Mapped["User"] = relationship(back_populates="profile")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False) # e.g., "update_flower", "disable_user"
    target_type: Mapped[str] = mapped_column(String(64), nullable=False) # e.g., "Flower", "User"
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    details: Mapped[Optional[str]] = mapped_column(Text) # JSON string of changes
    ip_address: Mapped[Optional[str]] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    admin: Mapped["User"] = relationship()

class FlowerVersion(Base):
    __tablename__ = "flower_versions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    flower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("flowers.id"), nullable=False)
    data: Mapped[str] = mapped_column(Text, nullable=False) # JSON snapshot of flower data
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_by: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
