from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import select
from app.api import flower, qa, knowledge, auth, user, favorites, comments, feedbacks, admin
from app.services.db import engine, AsyncSessionFactory
from app.models.tables import Base, User, Flower, RecognitionRecord, Comment, CommentReply, Feedback, QAHistory, AuditLog, FlowerVersion
from app.core.security import verify_password, get_password_hash
from app.services.storage import minio_service
from markupsafe import Markup

load_dotenv()

app = FastAPI(title="花卉识别与科普系统API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("JWT_SECRET_KEY", "seelevollerei"),
    max_age=1800,
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
app.include_router(admin.router)


# ========== 审计日志工具函数 ==========
async def log_audit(admin_id: int, action: str, target_type: str, target_id: int = None, details: str = None, ip_address: str = None):
    """记录管理员操作到审计日志"""
    try:
        async with AsyncSessionFactory() as session:
            log_entry = AuditLog(
                admin_id=admin_id,
                action=action,
                target_type=target_type,
                target_id=target_id or 0,
                details=details,
                ip_address=ip_address,
            )
            session.add(log_entry)
            await session.commit()
    except Exception as e:
        print(f"[AuditLog] 写入失败: {e}")


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

        request.session.update({"token": "admin_token", "user_id": user.id, "username": user.username})
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

admin_app = Admin(
    app,
    engine,
    title="花世界后台管理",
    authentication_backend=authentication_backend,
    templates_dir=os.path.join(os.path.dirname(__file__), "templates"),
)


# ========== 带审计日志的 ModelView 基类 ==========
class AuditModelView(ModelView):
    async def _get_admin_id(self, request: Request) -> int:
        return request.session.get("user_id", 0)

    async def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def after_model_change(self, data, model, is_created, request: Request) -> None:
        admin_id = await self._get_admin_id(request)
        if not admin_id:
            return
        ip = await self._get_client_ip(request)
        action = "新增" if is_created else "编辑"
        target_type = model.__class__.__name__
        target_id = getattr(model, "id", None)
        # 生成可读的描述
        model_str = str(model)
        details = f"{action}了 {target_type}（ID:{target_id}，内容：{model_str[:100]}）"
        await log_audit(admin_id, action, target_type, target_id, details, ip)

    async def after_model_delete(self, model, request: Request) -> None:
        admin_id = await self._get_admin_id(request)
        if not admin_id:
            return
        ip = await self._get_client_ip(request)
        target_type = model.__class__.__name__
        target_id = getattr(model, "id", None)
        model_str = str(model)
        details = f"删除了 {target_type}（ID:{target_id}，内容：{model_str[:100]}）"
        await log_audit(admin_id, "删除", target_type, target_id, details, ip)


class UserAdmin(AuditModelView, model=User):
    column_default_sort = [("registration_date", True)]
    column_list = [
        "id",
        "username",
        "email",
        "role",
        "status",
        "registration_date",
        "last_login_at",
        "last_login_ip",
        "recognition_count"
    ]
    column_labels = {
        "id": "ID",
        "username": "用户名",
        "email": "邮箱",
        "password_hash": "密码",
        "role": "角色",
        "status": "状态",
        "registration_date": "注册日期",
        "last_login_at": "上次登录",
        "last_login_ip": "上次登录IP",
        "recognition_count": "识别次数",
        "profile": "用户资料",
        "recognitions": "识别记录",
        "comments": "评论",
        "feedbacks": "反馈",
        "qa_histories": "问答历史",
        "expert_application": "专家申请",
    }
    column_searchable_list = ["username", "email"]
    column_details_list = [
        "id",
        "username",
        "email",
        "role",
        "status",
        "registration_date",
        "last_login_at",
        "last_login_ip",
        "recognition_count",
    ]
    column_filters = []
    name = "用户"
    name_plural = "用户管理"
    icon = "fa-solid fa-users"
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True

    form_excluded_columns = [
        "recognitions",
        "comments",
        "feedbacks",
        "qa_histories",
        "expert_application",
        "profile",
        "registration_date",
        "last_login_at",
        "last_login_ip",
    ]

    form_include_pk = False

    async def on_model_change(self, data, model, is_created, request):
        current_admin_id = request.session.get("user_id", 0)
        # 禁止修改其他管理员账号（本人除外）
        if not is_created and hasattr(model, "role") and model.role == "admin":
            if model.id != current_admin_id:
                raise Exception("权限不足：不允许修改其他管理员账号")
        if is_created:
            if "password_hash" in data and data["password_hash"]:
                data["password_hash"] = get_password_hash(data["password_hash"])
                model.password_hash = data["password_hash"]
            else:
                model.password_hash = get_password_hash("123456")
        elif "password_hash" in data and data["password_hash"]:
            if not data["password_hash"].startswith("$2b$"):
                data["password_hash"] = get_password_hash(data["password_hash"])
                model.password_hash = data["password_hash"]

    async def delete_model(self, request: Request, pk: str):
        current_admin_id = request.session.get("user_id", 0)
        async with AsyncSessionFactory() as session:
            target = await session.get(User, int(pk))
            if target and target.role == "admin" and target.id != current_admin_id:
                raise Exception("权限不足：不允许删除其他管理员账号")
        return await super().delete_model(request, pk)

    def get_query(self):
        return super().get_query().options(selectinload(User.recognitions))

    column_formatters = {
        "recognition_count": lambda m, a: len(m.recognitions) if m.recognitions else 0,
        "email": lambda m, a: f"{m.email[:3]}****{m.email[-4:]}" if m.email and "@" in m.email and len(m.email) > 7 else m.email,
        "role": lambda m, a: {"user": "普通用户", "expert": "专家", "admin": "管理员"}.get(m.role, m.role),
        "status": lambda m, a: {"active": "正常", "disabled": "已禁用"}.get(m.status, m.status),
    }

    column_formatters_detail = column_formatters


class FlowerAdmin(AuditModelView, model=Flower):
    column_default_sort = [("created_at", True)]
    column_list = [
        "id",
        "name",
        "family",
        "plant_type",
        "status",
        "created_at",
    ]
    column_labels = {
        "id": "ID",
        "name": "名称",
        "family": "科属",
        "color": "颜色",
        "blooming_period": "花期",
        "plant_type": "类型",
        "status": "状态",
        "created_at": "录入时间",
        "updated_at": "更新时间",
        "description": "描述",
        "care_guide": "养护指南",
        "flower_language": "花语",
        "tags": "标签",
        "recognitions": "识别记录",
        "comments": "评论",
    }
    column_searchable_list = ["name", "family", "tags"]
    column_filters = []
    can_export = True
    can_create = True
    can_edit = True
    can_delete = True
    name = "花卉"
    name_plural = "花卉百科"
    icon = "fa-solid fa-seedling"

    form_excluded_columns = ["recognitions", "comments", "created_at", "updated_at"]

    form_widget_args = {
        "description": {"rows": 10},
        "care_guide": {"rows": 10},
        "flower_language": {"rows": 5},
    }

    column_formatters = {
        "status": lambda m, a: {"draft": "草稿", "pending": "待审核", "published": "已发布"}.get(m.status, m.status),
    }


class RecognitionAdmin(AuditModelView, model=RecognitionRecord):
    column_default_sort = [("created_at", True)]
    column_list = [
        "id",
        "user_name",
        "flower_name",
        "confidence",
        "image_preview",
        "is_corrected",
        "created_at",
    ]
    column_labels = {
        "id": "ID",
        "user_name": "用户",
        "flower_name": "识别结果",
        "confidence": "置信度",
        "image_preview": "图片预览",
        "image_url": "图片地址",
        "is_corrected": "已纠错",
        "created_at": "时间",
        "user": "用户",
        "flower": "花卉",
        "corrected_flower": "纠正后花卉",
        "plant_id": "花卉ID",
        "user_id": "用户ID",
        "corrected_plant_id": "纠正后花卉ID",
    }
    column_sortable_list = ["id", "confidence", "created_at"]
    column_searchable_list = []
    column_filters = []
    can_create = False
    can_edit = True
    can_delete = True
    can_export = True
    name = "识别"
    name_plural = "识别记录管理"
    icon = "fa-solid fa-magnifying-glass"

    def get_query(self):
        return super().get_query().options(
            selectinload(RecognitionRecord.user),
            selectinload(RecognitionRecord.flower),
        )

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "游客",
        "flower_name": lambda m, a: m.flower.name if m.flower else "未知",
        "image_preview": lambda m, a: Markup(
            f'<img src="{minio_service.get_url(m.image_url)}" width="100" />'
        )
        if m.image_url
        else "",
    }


class QAHistoryAdmin(AuditModelView, model=QAHistory):
    column_default_sort = [("created_at", True)]
    column_list = ["id", "user_name", "question_preview", "answer_preview", "created_at"]
    column_labels = {
        "id": "ID",
        "user_name": "用户",
        "question": "提问内容",
        "question_preview": "提问内容",
        "answer": "回答内容",
        "answer_preview": "回答内容",
        "created_at": "提问时间",
        "user": "用户",
        "user_id": "用户ID",
    }
    column_searchable_list = ["question", "user.username"]
    column_sortable_list = ["id", "created_at"]
    can_create = False
    can_edit = False
    can_delete = True
    can_export = True
    can_view_details = True
    name = "问答"
    name_plural = "问答历史管理"
    icon = "fa-solid fa-comments"

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "游客",
        "question_preview": lambda m, a: Markup(
            f'<div style="max-width:300px;white-space:normal;word-break:break-all;line-height:1.5;">{(m.question[:100] + "...") if m.question and len(m.question) > 100 else (m.question or "")}</div>'
        ),
        "answer_preview": lambda m, a: Markup(
            f'<div style="max-width:400px;white-space:normal;word-break:break-all;line-height:1.5;">{(m.answer[:150] + "...") if m.answer and len(m.answer) > 150 else (m.answer or "")}</div>'
        ),
    }

    column_formatters_detail = {
        "question": lambda m, a: Markup(
            f'<div style="white-space:pre-wrap;word-break:break-all;line-height:1.8;max-width:600px;">{m.question or ""}</div>'
        ),
        "answer": lambda m, a: Markup(
            f'<div style="white-space:pre-wrap;word-break:break-all;line-height:1.8;max-width:600px;">{m.answer or ""}</div>'
        ),
        "user_name": lambda m, a: m.user.username if m.user else "游客",
    }

    def get_query(self):
        return super().get_query().options(selectinload(QAHistory.user))

class CommentAdmin(AuditModelView, model=Comment):
    column_default_sort = [("created_at", True)]
    column_list = ["id", "user_name", "flower_name", "content_preview", "status", "created_at"]
    column_labels = {
        "id": "ID",
        "user_name": "用户",
        "flower_name": "关联花卉",
        "content": "评论内容",
        "content_preview": "评论内容",
        "status": "状态",
        "created_at": "时间",
        "user": "用户",
        "flower": "花卉",
        "user_id": "用户ID",
        "flower_id": "花卉ID",
    }
    column_searchable_list = ["content"]
    column_sortable_list = ["id", "created_at"]
    column_filters = []
    can_create = False
    can_edit = True
    can_delete = True
    can_export = True
    can_view_details = True
    name = "评论"
    name_plural = "内容审核管理"
    icon = "fa-solid fa-shield-halved"

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "系统",
        "flower_name": lambda m, a: m.flower.name if m.flower else "未知",
        "status": lambda m, a: {"pending": "待审核", "approved": "已通过", "rejected": "已拒绝"}.get(m.status, m.status),
        "content_preview": lambda m, a: Markup(
            f'<div style="max-width:400px;white-space:normal;word-break:break-all;line-height:1.5;">{(m.content[:100] + "...") if m.content and len(m.content) > 100 else (m.content or "")}</div>'
        ),
    }

    column_formatters_detail = {
        "content": lambda m, a: Markup(
            f'<div style="white-space:pre-wrap;word-break:break-all;line-height:1.8;max-width:600px;">{m.content or ""}</div>'
        ),
        "user_name": lambda m, a: m.user.username if m.user else "系统",
        "flower_name": lambda m, a: m.flower.name if m.flower else "未知",
    }

    def get_query(self):
        return super().get_query().options(
            selectinload(Comment.user), selectinload(Comment.flower)
        )

class FeedbackAdmin(AuditModelView, model=Feedback):
    column_default_sort = [("created_at", True)]
    column_list = ["id", "user_name", "content_preview", "status", "created_at"]
    column_labels = {
        "id": "ID",
        "user_name": "反馈用户",
        "content": "反馈内容",
        "content_preview": "反馈内容",
        "status": "状态",
        "created_at": "时间",
        "reply_content": "回复内容",
        "processed_at": "处理时间",
        "user": "用户",
        "user_id": "用户ID",
        "flower_id": "花卉ID",
    }
    column_filters = []
    can_create = False
    can_edit = True
    can_delete = True
    can_export = True
    can_view_details = True
    name = "反馈"
    name_plural = "反馈与工单管理"
    icon = "fa-solid fa-clipboard-list"

    column_formatters = {
        "user_name": lambda m, a: m.user.username if m.user else "匿名",
        "status": lambda m, a: {"pending": "待处理", "processing": "处理中", "resolved": "已解决", "closed": "已关闭"}.get(m.status, m.status),
        "content_preview": lambda m, a: Markup(
            f'<div style="max-width:400px;white-space:normal;word-break:break-all;line-height:1.5;">{(m.content[:100] + "...") if m.content and len(m.content) > 100 else (m.content or "")}</div>'
        ),
    }

    column_formatters_detail = {
        "content": lambda m, a: Markup(
            f'<div style="white-space:pre-wrap;word-break:break-all;line-height:1.8;max-width:600px;">{m.content or ""}</div>'
        ),
        "reply_content": lambda m, a: Markup(
            f'<div style="white-space:pre-wrap;word-break:break-all;line-height:1.8;max-width:600px;">{m.reply_content or ""}</div>'
        ),
        "user_name": lambda m, a: m.user.username if m.user else "匿名",
    }

    def get_query(self):
        return super().get_query().options(selectinload(Feedback.user))

class AuditLogAdmin(ModelView, model=AuditLog):
    column_default_sort = [("created_at", True)]
    # 只使用真实模型字段，不用虚拟列，避免 sqladmin 查询报错
    column_list = ["id", "admin_id", "action", "target_type", "target_id", "details", "ip_address", "created_at"]
    column_labels = {
        "id": "ID",
        "admin_id": "管理员",
        "action": "操作类型",
        "target_type": "操作模块",
        "target_id": "目标ID",
        "details": "操作详情",
        "ip_address": "IP地址",
        "created_at": "操作时间",
        "admin": "管理员",
    }
    column_sortable_list = ["id", "created_at"]
    column_searchable_list = ["action", "target_type"]
    name = "日志"
    name_plural = "系统操作日志"
    icon = "fa-solid fa-clock-rotate-left"
    can_create = False
    can_edit = False
    can_delete = False
    can_export = True

    # 模块名称映射
    _module_names = {
        "User": "用户管理",
        "Flower": "花卉百科",
        "RecognitionRecord": "识别记录",
        "QAHistory": "问答历史",
        "Comment": "内容审核",
        "Feedback": "反馈工单",
    }

    column_formatters = {
        "admin_id": lambda m, a: (m.admin.username if m.admin else f"管理员#{m.admin_id}"),
        "target_type": lambda m, a: AuditLogAdmin._module_names.get(m.target_type, m.target_type),
        "details": lambda m, a: Markup(
            f'<div style="max-width:350px;white-space:normal;word-break:break-all;line-height:1.5;">'
            f'{(m.details[:120] + "...") if m.details and len(m.details) > 120 else (m.details or "-")}'
            f'</div>'
        ),
    }

    column_formatters_detail = {
        "target_type": lambda m, a: AuditLogAdmin._module_names.get(m.target_type, m.target_type),
        "admin_id": lambda m, a: (m.admin.username if m.admin else f"管理员#{m.admin_id}"),
    }

    def get_query(self):
        return super().get_query().options(selectinload(AuditLog.admin))

admin_app.add_view(UserAdmin)
admin_app.add_view(FlowerAdmin)
admin_app.add_view(RecognitionAdmin)
admin_app.add_view(QAHistoryAdmin)
admin_app.add_view(CommentAdmin)
admin_app.add_view(AuditLogAdmin)


@app.get("/api/health")
async def health():
    return {"status": "ok"}

@app.get("/")
async def root():
    return RedirectResponse(url="/admin/user/list")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
