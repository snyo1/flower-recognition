from minio import Minio
from ..core.config import settings
import io
import uuid
import datetime

class MinioService:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def upload_image(self, content: bytes, content_type: str = "image/jpeg") -> str:
        """上传图片并返回对象名称"""
        file_name = f"{datetime.date.today()}/{uuid.uuid4()}.jpg"
        self.client.put_object(
            self.bucket_name,
            file_name,
            io.BytesIO(content),
            length=len(content),
            content_type=content_type
        )
        return file_name

    def get_url(self, object_name: str) -> str:
        """获取图片的临时访问链接"""
        return self.client.presigned_get_object(
            self.bucket_name,
            object_name,
            expires=datetime.timedelta(hours=24)
        )

minio_service = MinioService()
