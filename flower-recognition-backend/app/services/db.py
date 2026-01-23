import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "")

def get_engine():
    if DATABASE_URL:
        return create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
    return create_engine("sqlite:///./local.db", pool_pre_ping=True)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
