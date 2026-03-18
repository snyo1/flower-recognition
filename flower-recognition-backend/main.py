from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy import select
from app.api import flower, qa, knowledge, auth, user, favorites, comments, feedbacks
from app.services.db import engine, AsyncSessionFactory
from app.models.tables import Base, User, Flower, RecognitionRecord, Comment, Feedback, QAHistory, AuditLog, FlowerVersion
from app.core.security import verify_password
from app.services.storage import minio_service
from markupsafe import Markup

load_dotenv()

app = FastAPI(title="花卉识别与科普系统API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库（如缺少新表则创建）
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 注册API路由
app.include_router(flower.router)
app.include_router(qa.router)
app.include_router(knowledge.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(favorites.router)
app.include_router(comments.router)
app.include_router(feedbacks.router)

# Admin Authentication
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        async with AsyncSessionFactory() as session:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalars().first()
        
        if not user:
            return False
            
        if not verify_password(password, user.password_hash):
            return False
            
        # Only allow admin role
        if user.role != "admin":
            return False

        request.session.update({"token": "admin_token", "user_id": user.id})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True

authentication_backend = AdminAuth(secret_key=os.getenv("JWT_SECRET_KEY", "seelevollerei"))

from sqlalchemy.orm import selectinload

# Admin Interface Configuration
admin = Admin(app, engine, title="花世界后台管理", authentication_backend=authentication_backend)

class UserAdmin(ModelView, model=User):
    column_list = [
        "id", 
        "username", 
        "email", 
        "role", 
        "status",
        "registration_date",
        "recognition_count"
    ]
    column_labels = {
        "id": "ID",
        "username": "用户名",
        "email": "邮箱",
        "role": "角色",
        "status": "状态",
        "registration_date": "注册时间",
        "recognition_count": "识别次数"
    }
    column_searchable_list = ["username", "email"]
    column_filters = [] # 暂时清空以恢复访问
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True
    name = "用户"
    name_plural = "1. 用户管理"

    def get_query(self):
        return super().get_query().options(selectinload(User.recognitions))

    column_formatters = {
        "recognition_count": lambda m, a: len(m.recognitions) if m.recognitions else 0,
        "email": lambda m, a: f"{m.email[:3]}****{m.email[-4:]}" if m.email and "@" in m.email else m.email
    }

class FlowerAdmin(ModelView, model=Flower):
    column_list = [
        "id", 
        "name", 
        "family", 
        "plant_type",
        "status",
        "created_at"
    ]
    column_labels = {
        "id": "ID",
        "name": "名称",
        "family": "科属",
        "plant_type": "类型",
        "status": "状态",
        "created_at": "录入时间",
        "description": "描述",
        "care_guide": "养护指南",
        "flower_language": "花语",
        "tags": "标签"
    }
    column_searchable_list = ["name", "family", "tags"]
    column_filters = []
    can_export = True
    can_create = True
    can_edit = True
    can_delete = True
    name = "花卉"
    name_plural = "2. 知识库管理"
    
    form_widget_args = {
        "description": {"rows": 10},
        "care_guide": {"rows": 10},
        "flower_language": {"rows": 5},
    }

class RecognitionAdmin(ModelView, model=RecognitionRecord):
    column_list = [
        "id", 
        "user_name",
        "flower_name", 
        "confidence", 
        "image_preview",
        "is_corrected",
        "created_at"
    ]
    column_labels = {
        "id": "ID",
        "user_name": "用户",
        "flower_name": "识别结果",
        "confidence": "置信度",
        "image_preview": "图片预览",
        "is_corrected": "已纠错",
        "created_at": "时间"
    }
    column_sortable_list = ["id", "confidence", "created_at"]
    column_filters = []
    can_edit = True # 用于人工纠错
    name = "识别"
    name_plural = "3. 识别记录管理"

    def get_query(self):
        return super().get_query().options(selectinload(RecognitionRecord.user), selectinload(RecognitionRecord.flower))

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "游客",
        "flower_name": lambda m, a: m.flower.name if m.flower else "未知",
        "image_preview": lambda m, a: Markup(f'<img src="{minio_service.get_url(m.image_url)}" width="100" />') if m.image_url else ""
    }

class QAHistoryAdmin(ModelView, model=QAHistory):
    column_list = ["id", "user_name", "question", "created_at"]
    column_labels = {
        "id": "ID",
        "user_name": "用户",
        "question": "提问内容",
        "created_at": "提问时间"
    }
    column_searchable_list = ["question"]
    name = "问答"
    name_plural = "4. 问答历史管理"

    def get_query(self):
        return super().get_query().options(selectinload(QAHistory.user))

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "游客"
    }

class CommentAdmin(ModelView, model=Comment):
    column_list = ["id", "user_name", "flower_name", "content", "status", "created_at"]
    column_labels = {
        "id": "ID",
        "user_name": "用户",
        "flower_name": "关联花卉",
        "content": "评论内容",
        "status": "状态",
        "created_at": "时间"
    }
    column_filters = []
    name = "评论"
    name_plural = "5. 内容审核管理"

    def get_query(self):
        return super().get_query().options(selectinload(Comment.user), selectinload(Comment.flower))

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "系统",
        "flower_name": lambda m, a: m.flower.name if m.flower else "未知"
    }

class FeedbackAdmin(ModelView, model=Feedback):
    column_list = ["id", "user_name", "content", "status", "created_at"]
    column_labels = {
        "id": "ID",
        "user_name": "反馈用户",
        "content": "反馈内容",
        "status": "状态",
        "created_at": "时间"
    }
    column_filters = []
    name = "反馈"
    name_plural = "6. 反馈与工单管理"

    def get_query(self):
        return super().get_query().options(selectinload(Feedback.user))

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "匿名"
    }

class AuditLogAdmin(ModelView, model=AuditLog):
    column_list = ["id", "admin_name", "action", "target_type", "created_at"]
    column_labels = {
        "id": "ID",
        "admin_name": "管理员",
        "action": "动作",
        "target_type": "目标类型",
        "created_at": "时间"
    }
    name = "审计"
    name_plural = "7. 系统操作日志"

    def get_query(self):
        return super().get_query().options(selectinload(AuditLog.admin))

    column_formatters = {
        "admin_name": lambda m, a: m.admin.username if m.admin else "未知"
    }

admin.add_view(UserAdmin)
admin.add_view(FlowerAdmin)
admin.add_view(RecognitionAdmin)
admin.add_view(QAHistoryAdmin)
admin.add_view(CommentAdmin)
admin.add_view(FeedbackAdmin)
admin.add_view(AuditLogAdmin)


@app.get("/api/health")
async def health():
    return {"status": "ok"}

# 根路由直接重定向到 admin (或者保持空，让用户访问 /admin)
# 用户要求后端启动后直接进入后台管理员页面，这里我们让 / 重定向到 /admin
from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    return RedirectResponse(url="/admin")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
