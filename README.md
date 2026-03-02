# 花世界 - 智能花卉识别与科普系统

基于大模型的智能花卉识别与科普系统，支持多模态花卉图片识别、深度科普信息生成、智能问答、知识库管理以及云端存储功能。

## 最新更新 (2024-03-02)
- **多模态识别**: 集成多模态大模型 API，支持图片直接识别花卉种类、颜色和特征。
- **MinIO 集成**: 所有上传的识别图片均自动持久化存储至 MinIO 私有云。
- **首页重构**: 采用左侧上传、右侧结果的响应式布局，支持批量识别与滚动查看。
- **历史记录**: 实现真实的识别与问答历史持久化，每个用户自动保留最近 10 条记录。
- **后台完善**: 全面完善了知识库、用户、反馈、评论等模块的增删改查功能。

## 技术栈

### 前端
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus (核心组件响应式适配)
- **状态管理**: Pinia
- **构建工具**: Vite

### 后端
- **框架**: FastAPI (Python 3.8+)
- **AI 引擎**: LangChain + DeepSeek-V3 / 多模态 Vision 模型
- **数据库**: SQLAlchemy (支持异步操作)
- **存储**: MinIO (对象存储)
- **认证**: JWT (JSON Web Token)

## 项目结构

```text
HuaShiJie/
├── flower-recognition-frontend/     # 前端 Vue 3 项目
│   ├── src/
│   │   ├── api/                     # 后端 API 调用封装
│   │   ├── components/              # 通用业务组件
│   │   ├── layout/                  # 页面布局组件
│   │   ├── router/                  # 路由配置 (含导航守卫)
│   │   ├── stores/                  # Pinia 状态管理
│   │   └── views/                   # 页面视图 (首页、识别、问答等)
│   └── vite.config.ts               # Vite 配置文件
├── flower-recognition-backend/      # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/                     # 业务路由接口
│   │   ├── core/                    # 核心配置与安全逻辑
│   │   ├── models/                  # 数据库表与 Schema 定义
│   │   └── services/                # AI、存储、数据库等核心服务
│   ├── main.py                      # 后端应用启动入口
│   └── requirements.txt             # 项目依赖列表
└── README.md                        # 项目说明文档
```

## 核心功能

### 1. 智能花卉识别
- **多模态分析**: 自动识别图片中的花卉名称、科属、颜色、花期等。
- **批量处理**: 支持一次上传多张图片进行并发识别。
- **置信度评分**: AI 自动计算识别结果的置信度。

### 2. 深度科普生成
- **全方位信息**: 包含特征描述、专业养护方法（光照、水分、施肥）、花语文化。
- **交互式查看**: 结果以折叠面板形式展现，保持界面简洁。

### 3. 智能问答 (AI Chat)
- **上下文感知**: 支持基于识别结果的深度追问。
- **历史回溯**: 自动保存用户最近的问答足迹。

### 4. 知识库与社区
- **全局搜索**: 快速检索各类花卉知识。
- **互动评论**: 用户可对花卉知识进行评论和点赞。
- **收藏夹**: 跨设备同步用户喜爱的花卉。

## 配置说明

### 1. 环境变量 (.env)
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=你的JWT密钥
DEEPSEEK_API_KEY=你的DeepSeek_API_KEY
DEEPSEEK_BASE_URL=https://api.deepseek.com
ZHIPU_API_KEY=你的智谱AI_API_KEY
```

### 2. MinIO 配置 (config.py)
```python
MINIO_ENDPOINT="192.168.42.101:9000"
MINIO_ACCESS_KEY="minioadmin"
MINIO_SECRET_KEY="minioadmin"
MINIO_BUCKET="flower-images"
```

## 推荐模型建议

对于**花卉识别 (Vision)** 任务，项目已默认接入：
1. **智谱 AI (GLM-4.6V)**: 接入 `zai-sdk` 实现高精度的多模态花卉识别，支持思考过程（Thinking）输出。
2. **DeepSeek-V3**: 用于处理文本科普生成与智能问答。

## 启动方式

### 前端
```bash
cd flower-recognition-frontend
npm install
npm run dev
```

### 后端
```bash
cd flower-recognition-backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## 许可证
MIT License
