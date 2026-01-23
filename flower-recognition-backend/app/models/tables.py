from sqlalchemy import Column, BigInteger, String, Text, DateTime, DECIMAL, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(128))
    registration_date = Column(DateTime, server_default=func.now())

class Flower(Base):
    __tablename__ = "flowers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    family = Column(String(128), nullable=False)
    color = Column(String(256), nullable=False)
    blooming_period = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    care_guide = Column(Text, nullable=False)
    flower_language = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class RecognitionRecord(Base):
    __tablename__ = "recognition_records"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    image_url = Column(String(512))
    plant_id = Column(BigInteger, ForeignKey("flowers.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    confidence = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, server_default=func.now())
    flower = relationship("Flower", backref="recognitions")
    user = relationship("User", backref="recognitions")
