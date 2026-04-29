# 花世界（HuaShiJie）

一个面向花卉识别、知识科普、智能问答与社区互动的全栈项目。

项目由两部分组成：

- `flower-recognition-frontend`：基于 Vue 3 + TypeScript + Element Plus 的前端应用
- `flower-recognition-backend`：基于 FastAPI + SQLAlchemy + SQLAdmin 的后端服务

该系统支持图片识花、花卉知识展示、智能问答、评论收藏、反馈管理以及后台管理等完整功能。

---

## 项目概览

### 主要功能

- 智能花卉识别：支持上传图片进行花卉识别
- 花卉知识库：查看花卉名称、科属、花期、养护方式、花语等信息
- 智能问答：围绕花卉知识进行多轮对话
- 用户体系：注册、登录、个人信息与历史记录管理
- 社区互动：评论、回复、收藏、反馈
- 后台管理：用户、花卉、识别记录、问答历史、评论反馈、审计日志管理

### 最近功能更新

- 首页识别失败时改为优雅降级展示，不再直接报错
- 首页识别结果中的多个折叠面板可独立展开
- 问答历史按用户隔离，未登录用户不加载历史记录
- 问答失败时自动重试，并提供兜底回答
- 后台登录后自动跳转到管理列表页
- 后台按钮、状态、角色、删除弹窗等已做中文化处理
- 后台管理员权限进一步隔离，不能编辑或删除其他管理员账号
- 审计日志展示与查询异常已修复，日志内容更易读

---

## 技术栈

### 前端

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Element Plus
- Axios
- marked

### 后端

- FastAPI
- SQLAlchemy Async
- SQLAdmin
- Pydantic Settings
- JWT
- SQLite / PostgreSQL / MySQL（按 `DATABASE_URL` 配置）
- MinIO
- LangChain
- DeepSeek
- 智谱 AI GLM-4.6V

---

## 目录结构

```text
HuaShiJie/
├── flower-recognition-frontend/          # 前端项目
│   ├── public/
│   ├── src/
│   │   ├── api/                          # 接口地址与请求封装
│   │   ├── assets/                       # 静态资源
│   │   ├── components/                   # 公共组件
│   │   ├── layout/                       # 页面布局
│   │   ├── router/                       # 路由配置
│   │   ├── stores/                       # 状态管理
│   │   └── views/                        # 页面视图
│   ├── package.json
│   └── vite.config.ts
├── flower-recognition-backend/           # 后端项目
│   ├── app/
│   │   ├── api/                          # 路由模块
│   │   ├── core/                         # 配置与安全模块
│   │   ├── models/                       # ORM 模型与 schema
│   │   ├── services/                     # AI、数据库、存储、种子数据等服务
│   │   └── utils/
│   ├── alembic/                          # 数据库迁移
│   ├── db/
│   ├── scripts/                          # 辅助脚本
│   ├── templates/sqladmin/               # 后台管理模板
│   ├── main.py                           # 后端入口
│   └── requirements.txt
└── README.md
```

---

## 运行环境

### 前端

- Node.js `^20.19.0 || >=22.12.0`
- npm

### 后端

- Python 3.10+
- pip

### 可选依赖

- MinIO：用于图片对象存储
- DeepSeek API Key：用于智能问答
- 智谱 AI API Key：用于多模态识花

---

## 快速开始

## 1. 克隆项目

```bash
git clone <your-repo-url>
cd HuaShiJie
```

## 2. 启动后端

```bash
cd flower-recognition-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 配置后端环境变量

在 `flower-recognition-backend` 目录下创建 `.env` 文件，可参考下面示例：

```env
DATABASE_URL=sqlite+aiosqlite:///./local.db
SECRET_KEY=replace-with-a-random-secret
JWT_SECRET_KEY=replace-with-a-random-jwt-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.example.com
MAIL_FROM_NAME=花世界
MAIL_STARTTLS=true
MAIL_SSL_TLS=false

DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

ZHIPU_API_KEY=your-zhipu-api-key
ZHIPU_MODEL=glm-4.6v

MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=flower-images
MINIO_SECURE=false
```

说明：

- 本项目默认通过 `DATABASE_URL` 决定数据库类型
- 若仅想本地快速体验，推荐直接使用 SQLite：

```env
DATABASE_URL=sqlite+aiosqlite:///./local.db
```

### 启动后端服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

启动后可访问：

- API 文档：`http://localhost:8000/docs`
- 后台管理：`http://localhost:8000/admin`

## 3. 初始化演示数据（可选）

后端内置了花卉、用户、评论、收藏、反馈等种子数据脚本。

```bash
python app/services/seed.py
```

该脚本会尝试写入或同步：

- 花卉基础知识数据
- 测试用户与用户资料
- 评论与回复
- 收藏数据
- 反馈数据

## 4. 启动前端

```bash
cd ..\flower-recognition-frontend
npm install
npm run dev
```

启动后访问：

- 前端页面：`http://localhost:5173`

前端开发服务器已配置代理：

- `/api` -> `http://localhost:8000`

如果你希望前端直接请求其他后端地址，也可以在前端环境变量中配置：

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

当前代码默认优先读取 `VITE_API_BASE_URL`，未配置时使用 `/api`。

---

## 后台管理说明

后台入口：`http://localhost:8000/admin`

支持的管理内容包括：

- 用户管理
- 花卉百科管理
- 识别记录管理
- 问答历史管理
- 评论与反馈管理
- 管理员操作审计日志

系统已支持：

- 登录态校验
- 管理员权限控制
- 管理员操作日志记录
- 多处中文化界面优化

如果你执行了种子脚本，数据库中会生成若干演示管理员与普通用户账号，可直接用于本地联调。

---

## 开发说明

### 前端常用命令

```bash
npm run dev
npm run build
npm run preview
npm run type-check
```

### 后端常用命令

```bash
uvicorn main:app --reload
python app/services/seed.py
```

### 数据库迁移

项目包含 `alembic/` 目录，可按需执行迁移。若你当前只是本地调试，也可以依赖启动时的自动建表逻辑。

---

## 已知注意事项

- `app/core/config.py` 中部分字段为必填环境变量，若 `.env` 缺失，后端可能无法正常启动
- 图片对象存储依赖 MinIO，若未启动对应服务，涉及图片持久化的功能可能受影响
- 智能识别与问答依赖外部模型服务，未配置 API Key 时相关能力不可用
- 首次启动若数据库为空，建议先运行一次种子脚本以获得更完整的演示体验

---

## 推荐本地体验流程

1. 启动 MinIO（如需测试图片上传链路）
2. 配置后端 `.env`
3. 安装后端依赖并启动 FastAPI
4. 运行 `python app/services/seed.py` 初始化演示数据
5. 安装前端依赖并启动 Vite
6. 访问首页、问答页和后台管理页进行联调

---

## 许可证

MIT License
