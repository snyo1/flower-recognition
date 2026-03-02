from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    
    # Zhipu AI 配置
    ZHIPU_API_KEY: str = "e94f01773d884e7898edef9c0fce916b.fa3uL0i0pv6g335p"
    ZHIPU_MODEL: str = "glm-4.6v"

    # MinIO 配置
    MINIO_ENDPOINT: str = "192.168.42.101:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "flower-images"
    MINIO_SECURE: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
