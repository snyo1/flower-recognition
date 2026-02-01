from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy import select
from app.api import flower, qa, knowledge, auth, user
from app.services.db import engine, AsyncSessionFactory
from app.models.tables import User, Flower, RecognitionRecord, Comment, Feedback, ExpertApplication
from app.core.security import verify_password

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

# 注册API路由
app.include_router(flower.router)
app.include_router(qa.router)
app.include_router(knowledge.router)
app.include_router(auth.router)
app.include_router(user.router)

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

# Admin Interface Configuration
admin = Admin(app, engine, title="花世界后台管理", authentication_backend=authentication_backend)

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.role, User.registration_date]
    column_searchable_list = [User.username, User.email]
    column_filters = [User.role]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "用户"
    name_plural = "用户管理"

class FlowerAdmin(ModelView, model=Flower):
    column_list = [Flower.id, Flower.name, Flower.family, Flower.blooming_period]
    column_searchable_list = [Flower.name, Flower.family]
    column_filters = [Flower.family, Flower.color]
    name = "花卉"
    name_plural = "花卉知识管理"

class ExpertApplicationAdmin(ModelView, model=ExpertApplication):
    column_list = [ExpertApplication.id, ExpertApplication.user_id, ExpertApplication.status, ExpertApplication.created_at]
    column_searchable_list = [ExpertApplication.user_id]
    column_filters = [ExpertApplication.status]
    name = "专家申请"
    name_plural = "专家申请审核"

class CommentAdmin(ModelView, model=Comment):
    column_list = [Comment.id, Comment.user_id, Comment.flower_id, Comment.content, Comment.created_at]
    name = "评论"
    name_plural = "评论管理"

class FeedbackAdmin(ModelView, model=Feedback):
    column_list = [Feedback.id, Feedback.user_id, Feedback.content, Feedback.status, Feedback.created_at]
    column_filters = [Feedback.status]
    name = "反馈"
    name_plural = "用户反馈"

admin.add_view(UserAdmin)
admin.add_view(FlowerAdmin)
admin.add_view(ExpertApplicationAdmin)
admin.add_view(CommentAdmin)
admin.add_view(FeedbackAdmin)


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
