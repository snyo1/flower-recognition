# 花世界 - 智能花卉识别与科普系统

基于多模态大模型的智能花卉识别与科普系统，支持图片识别、深度科普、智能问答、社区互动以及完整的后台管理功能。

---

## 最新更新 (2026-04-23)

### 前端优化
- **识别失败优雅降级**：识别服务不可用时不再弹出错误提示，而是为每张图片生成"未能识别"占位卡片，引导用户重新拍摄或前往问答。
- **置信度显示优化**：低于 60% 显示橙色"置信度低"警示，60% 以上显示正常置信度，失败时显示"未能识别"标签。
- **折叠面板独立展开**：首页识别结果的"特征描述"、"养护方法"、"花语文化"三个折叠面板改为独立展开，互不干扰，用户可同时查看多个内容。
- **问答记录用户隔离**：未登录用户不加载历史记录（显示空白对话）；已登录用户只加载自己的历史，不同账号数据完全隔离。
- **问答自动重试**：问答失败后自动重试一次，两次均失败时显示友好的默认回答，而非抛出报错。
- **问答时间显示**：消息时间今天只显示时分，非今天显示"月日 时分"。

### 后台管理优化
- **登录后自动跳转**：登录成功后自动重定向到用户管理列表，不再白屏。
- **操作日志修复**：系统操作日志不再报 500 错误，修复了虚拟列（`details_preview`/`admin_name`）导致的查询异常。
- **用户名列显示正确**：彻底修复了用户名被 JS 枚举翻译误伤的问题；role/status 列翻译改为 Python 端 `column_formatters` 处理，不再依赖 JS 匹配。
- **按钮全面中文化**："+New 用户"→"添加新用户"，"+New 花卉"→"添加新花卉"；删除确认弹窗改为中文提示（"确定要删除此记录吗？此操作不可撤销。"）；保存/取消/返回等按钮均已中文化。
- **编辑表单状态下拉**：角色（普通用户/专家/管理员）和状态（正常/已禁用/草稿/待审核/已发布）下拉选项均显示中文。
- **管理员权限隔离**：管理员不能编辑或删除其他管理员账号，只能操作自己和非管理员用户。
- **操作日志内容可读**：日志详情改为"编辑了 User（ID:5，内容：alice）"等友好描述，操作模块列显示中文名称。
- **识别置信度容错**：后端解析 AI 返回的置信度支持字符串格式（正则提取数字），兜底值为 70%。

---

## 技术栈

### 前端

| 技术 | 说明 |
|------|------|
| Vue 3 + TypeScript | 核心框架，Composition API |
| Element Plus | UI 组件库，响应式适配 |
| Pinia | 全局状态管理 |
| Vite | 构建工具 |
| Vue Router | 路由管理，含导航守卫与角色权限 |
| Axios | HTTP 请求，含 JWT 拦截器 |
| marked | Markdown 渲染（问答回复） |

### 后端

| 技术 | 说明 |
|------|------|
| FastAPI (Python 3.10+) | 异步 Web 框架 |
| SQLAlchemy (async) | ORM，`selectinload` 解决 N+1 |
| SQLAdmin | 后台管理界面 |
| aiosqlite / PostgreSQL | 数据库（可配置） |
| MinIO | 对象存储，持久化识别图片 |
| JWT | 用户认证 |
| LangChain | AI 调用框架 |
| 智谱 AI GLM-4.6V | 多模态花卉识别（Vision） |
| DeepSeek-V3 | 文本科普生成与智能问答 |

---

## 项目结构

```text
HuaShiJie/
├── flower-recognition-frontend/       # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/                       # API 调用封装
│   │   ├── components/                # 通用组件
│   │   ├── layout/                    # 页面布局
│   │   ├── router/                    # 路由与导航守卫
│   │   ├── stores/                    # Pinia 状态
│   │   └── views/                     # 页面视图
│   │       ├── HomeView.vue           # 首页（上传识别、科普展示）
│   │       ├── QAView.vue             # 智能问答
│   │       ├── KnowledgeView.vue      # 花卉知识库
│   │       ├── ProfileView.vue        # 个人中心
│   │       └── ...
│   └── vite.config.ts
├── flower-recognition-backend/        # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/                       # 路由接口
│   │   │   ├── flower.py              # 识别接口（单张/批量，失败优雅降级）
│   │   │   ├── qa.py                  # 问答接口
│   │   │   ├── user.py                # 用户接口
│   │   │   └── ...
│   │   ├── models/
│   │   │   └── tables.py              # 数据库表定义（含 AuditLog）
│   │   └── services/
│   │       ├── ai.py                  # AI 识别与问答服务
│   │       └── storage.py             # MinIO 存储服务
│   ├── templates/
│   │   └── sqladmin/                  # 后台管理自定义模板
│   │       ├── base.html              # 全局中文化脚本
│   │       ├── index.html             # 登录后自动跳转
│   │       ├── create.html            # 新增表单（中文按钮）
│   │       └── edit.html              # 编辑表单（中文按钮）
│   ├── main.py                        # 应用入口 + SQLAdmin 配置
│   └── requirements.txt
└── README.md
```

---

## 核心功能

### 1. 智能花卉识别

- 多模态大模型（GLM-4.6V）直接分析图片，识别花卉名称、科属、颜色、花期等。
- 支持批量上传多张图片，逐一识别。
- 识别失败时显示友好占位卡片，引导用户重拍或前往问答，不报错。
- 置信度分级显示（正常 / 偏低 / 未识别）。

### 2. 深度科普展示

- 识别成功后自动呈现特征描述、养护方法、花语文化三大模块。
- 三个折叠面板**独立展开**，互不干扰，可同时查看任意组合。
- 支持收藏、分享、跳转问答。

### 3. 智能问答

- 基于 DeepSeek-V3，支持上下文感知多轮对话。
- 已登录用户自动加载本人历史，不同账号数据隔离。
- 未登录用户每次会话从零开始。
- 失败自动重试，最终失败显示友好默认回答。
- 支持 Markdown 渲染回复内容。

### 4. 知识库与社区

- 花卉知识全文搜索。
- 评论、点赞、收藏功能。
- 收藏数据云端同步，跨设备访问。

### 5. 后台管理系统

访问地址：`http://localhost:8000/admin`（需管理员账号）

| 模块 | 功能 |
|------|------|
| 用户管理 | 查看、编辑用户资料；管理员权限隔离（不可互改） |
| 花卉百科管理 | 增删改查花卉知识库 |
| 识别记录管理 | 查看识别历史，支持人工纠错 |
| 问答历史管理 | 审核用户与 AI 的对话记录 |
| 内容审核管理 | 审核用户评论（待审核/通过/拒绝） |
| 反馈与工单管理 | 处理用户反馈，支持回复 |
| 系统操作日志 | 记录管理员所有操作（新增/编辑/删除），含操作人、模块、目标ID、时间、IP |

---

## 配置说明

### 环境变量（`flower-recognition-backend/.env`）

```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
JWT_SECRET_KEY=你的JWT密钥（请替换为强随机字符串）
DEEPSEEK_API_KEY=你的DeepSeek_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
ZHIPU_API_KEY=你的智谱AI_API_KEY
```

### MinIO 配置（`app/config.py`）

```python
MINIO_ENDPOINT   = "192.168.42.101:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET     = "flower-images"
```

---

## 启动方式

### 前端

```bash
cd flower-recognition-frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 后端

```bash
cd flower-recognition-backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
# API:   http://localhost:8000
# 后台:  http://localhost:8000/admin
```

> **提示**：若启动时遇到 `ModuleNotFoundError: No module named 'encodings'`，说明 Python 环境损坏，请重新安装 Python 或重建虚拟环境。

---

## 许可证

MIT License
