# 花世界 - 智能花卉识别与科普系统

基于大模型的智能花卉识别与科普系统，支持多模态花卉图片识别、深度科普信息生成、智能问答、知识库管理以及云端存储功能。

## 最新更新 (2026-03-21)

- **多模态识别**: 集成多模态大模型 API，支持图片直接识别花卉种类、颜色和特征。
- **MinIO 集成**: 所有上传的识别图片均自动持久化存储至 MinIO 私有云。
- **首页重构**: 采用左侧上传、右侧结果的响应式布局，支持批量识别与滚动查看。
- **历史记录**: 实现真实的识别与问答历史持久化，每个用户自动保留最近 10 条记录。
- **后台管理系统完善**:
    - **修复多页管理功能**: 解决了用户管理、识别记录管理、问答历史管理、内容审核管理等页面的 `DetachedInstanceError`，通过调整 SQLAlchemy 的 `lazy="selectin"` 加载策略和 SQLAdmin `ModelView` 的 `get_one_query` 方法确保关联数据正确加载。
    - **UI 优化**: 隐藏了“反馈与工单管理”页面（不删除其功能），移除了侧边栏导航的序号，并将后台管理界面中的关键操作按钮和提示（如“导出”、“新增”、“编辑”、“删除”、“操作”等）本地化为中文，提升了用户体验。
    - **API 接口**: 完善了用户、反馈、评论等模块的后台 API 接口，并加强了管理员权限验证。

## 技术栈

### 前端

- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus (核心组件响应式适配)
- **状态管理**: Pinia
- **构建工具**: Vite
- **路由**: Vue Router (含导航守卫和角色权限管理)

### 后端

- **框架**: FastAPI (Python 3.8+)
- **AI 引擎**: LangChain + DeepSeek-V3 / 多模态 Vision 模型 (如智谱 AI GLM-4.6V)
- **数据库**: SQLAlchemy (支持异步操作，ORM 优化，如 `selectinload` 用于解决 N+1 问题)
- **管理界面**: SQLAdmin (基于 Starlette 的管理后台)
- **存储**: MinIO (对象存储，用于图片等文件)
- **认证**: JWT (JSON Web Token)
- **依赖管理**: `requirements.txt`

## 项目结构

```text
HuaShiJie/
├── flower-recognition-frontend/     # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/                     # 后端 API 调用封装 (包含 admin 模块)
│   │   ├── components/              # 通用业务组件
│   │   ├── layout/                  # 页面布局组件
│   │   ├── router/                  # 路由配置 (含导航守卫和 /admin 路由)
│   │   ├── stores/                  # Pinia 状态管理
│   │   └── views/                   # 页面视图 (首页、识别、问答、admin 等)
│   └── vite.config.ts               # Vite 配置文件
├── flower-recognition-backend/      # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/                     # 业务路由接口 (包含 admin 接口)
│   │   ├── core/                    # 核心配置与安全逻辑 (含 get_current_admin)
│   │   ├── models/                  # 数据库表与 Schema 定义 (Pydantic models for API)
│   │   ├── services/                # AI、存储、数据库等核心服务
│   ├── main.py                      # 后端应用启动入口 (FastAPI 应用、SQLAdmin 配置)
│   └── requirements.txt             # 项目依赖列表
└── README.md                        # 项目说明文档
```

## 核心功能

### 1. 智能花卉识别

- **多模态分析**: 利用先进的多模态大模型，自动识别图片中的花卉名称、科属、颜色、花期等详细信息。
- **批量处理**: 支持用户一次性上传多张图片，系统将进行并发识别，提高效率。
- **置信度评分**: AI 模型自动为每个识别结果提供置信度评分，帮助用户评估结果的可靠性。
- **历史记录**: 每个用户的识别记录都将持久化存储，方便用户随时回顾和管理。

### 2. 深度科普生成

- **全方位信息**: 为识别出的花卉提供详细的科普知识，包括其特征描述、生长习性、专业养护方法（如光照、水分、施肥等）、以及相关的花语文化背景。
- **交互式查看**: 科普内容以折叠面板（Accordion）的形式展现，既保持了界面的简洁美观，又方便用户按需展开查看详细信息。

### 3. 智能问答 (AI Chat)

- **上下文感知**: 用户可以围绕识别结果进行深度追问，AI 问答系统能够理解上下文，提供更精准的解答。
- **历史回溯**: 用户的问答历史将自动保存，方便用户回顾过去的交流内容，持续学习。

### 4. 知识库与社区

- **全局搜索**: 提供强大的搜索功能，用户可以快速检索各类花卉知识。
- **互动评论**: 用户可以对花卉知识发表评论，与其他社区成员互动交流，并支持点赞功能。
- **收藏夹**: 用户可以将自己喜欢的花卉或重要知识添加到收藏夹，实现跨设备同步，方便个人管理。
- **后台管理**:
    - **用户管理**: 管理系统用户，包括查看、编辑用户资料、角色管理等。
    - **花卉百科管理**: 维护花卉知识库，进行花卉信息的增删改查。
    - **识别记录管理**: 查看和管理用户识别历史，支持人工纠错。
    - **问答历史管理**: 审核和管理用户与 AI 的问答记录。
    - **内容审核管理**: 对用户评论进行审核和管理。
    - **系统操作日志**: 记录管理员在后台的操作行为，便于审计。

## 配置说明

### 1. 环境变量 (.env)

在项目根目录 `flower-recognition-backend` 下创建 `.env` 文件，并配置以下变量：

```env
DATABASE_URL=sqlite+aiosqlite:///./test.db  # 数据库连接字符串，可配置 PostgreSQL, MySQL 等
SECRET_KEY=你的JWT密钥                     # 用于 JWT 认证的密钥，请替换为强随机字符串
DEEPSEEK_API_KEY=你的DeepSeek_API_KEY       # DeepSeek AI API 密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com # DeepSeek API 基础 URL
ZHIPU_API_KEY=你的智谱AI_API_KEY           # 智谱 AI API 密钥
```

### 2. MinIO 配置 (config.py)

MinIO 存储服务的配置位于 `flower-recognition-backend/app/config.py`，请根据您的 MinIO 部署进行修改：

```python
MINIO_ENDPOINT="192.168.42.101:9000" # MinIO 服务地址和端口
MINIO_ACCESS_KEY="minioadmin"       # MinIO Access Key
MINIO_SECRET_KEY="minioadmin"       # MinIO Secret Key
MINIO_BUCKET="flower-images"        # 存储花卉图片的桶名称
```

## 推荐模型建议

对于**花卉识别 (Vision)** 任务，项目已默认接入：

1.  **智谱 AI (GLM-4.6V)**: 通过 `zai-sdk` 实现高精度的多模态花卉识别，支持思考过程（Thinking）输出，提供详细的识别分析。
2.  **DeepSeek-V3**: 主要用于处理文本相关的任务，包括深度科普信息生成和智能问答。

## 启动方式

### 前端

1.  进入前端项目目录：
    ```bash
    cd flower-recognition-frontend
    ```
2.  安装依赖：
    ```bash
    npm install
    ```
3.  启动开发服务器：
    ```bash
    npm run dev
    ```
    应用将在 `http://localhost:5173/` (或根据端口占用情况自动分配) 启动。

### 后端

1.  进入后端项目目录：
    ```bash
    cd flower-recognition-backend
    ```
2.  安装依赖：
    ```bash
    pip install -r requirements.txt
    ```
    **重要提示**: 如果在执行此步骤或后续启动命令时遇到 `Fatal Python error: init_fs_encoding: failed to get the Python codec of the filesystem encoding ModuleNotFoundError: No module named 'encodings'` 错误，这表明您的 Python 环境存在问题。这通常需要手动修复 Python 安装（例如，重新安装 Python 或重新创建虚拟环境）。请确保您的 Python 环境能够正常导入标准库。

3.  启动 FastAPI 服务器：
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    后端 API 服务将在 `http://localhost:8000/` 启动。后台管理系统入口为 `http://localhost:8000/admin`。

## 许可证
MIT License