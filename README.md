# 花百科

## 智能花卉识别与科普系统

基于大模型的智能花卉识别与科普系统，支持花卉图片识别、科普信息生成、智能问答和知识库管理功能。

## 技术栈

### 前端
- **框架**: Vue 3 + TypeScript
- **UI组件库**: Element Plus
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 后端
- **框架**: FastAPI (Python)
- **数据验证**: Pydantic
- **CORS**: FastAPI CORS Middleware

## 项目结构

```
workspace/projects/
├── .coze                          # 项目配置文件
├── flower-recognition-frontend/    # 前端项目
│   ├── src/
│   │   ├── views/                  # 页面组件
│   │   │   ├── HomeView.vue       # 首页（花卉识别）
│   │   │   ├── QAView.vue         # 智能问答
│   │   │   ├── KnowledgeView.vue  # 知识库管理
│   │   │   └── HistoryView.vue    # 历史记录
│   │   ├── router/
│   │   │   └── index.ts           # 路由配置
│   │   ├── App.vue                # 根组件
│   │   └── main.ts                # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── flower-recognition-backend/     # 后端项目
│   ├── main.py                     # 应用入口
│   ├── app/
│   │   ├── api/                    # API路由
│   │   │   ├── flower.py          # 花卉识别接口
│   │   │   ├── qa.py              # 智能问答接口
│   │   │   └── knowledge.py       # 知识库接口
│   │   └── models/
│   │       └── schemas.py         # 数据模型
│   └── requirements.txt
└── README.md
```

## 核心功能

### 1. 花卉图片识别
- 支持上传花卉图片进行识别
- 显示识别结果：花卉名称、科属分类、特征描述等
- 支持批量图片识别（预留接口）

### 2. 花卉科普信息生成
- 基于识别结果生成科普信息
- 包括：生长习性、养护方法、浇水施肥要求、病虫害防治等
- 提供花语和文化内涵信息

### 3. 智能问答
- 支持自然语言提问
- 支持多轮对话
- 记录问答历史
- 快速问答标签

### 4. 花卉知识库管理
- 增删改查功能
- 关键词搜索
- 数据验证

### 5. 识别历史记录
- 查看历史识别记录
- 查看详细信息
- 删除历史记录

## API接口文档

### 基础接口

#### 健康检查
```
GET /health
```

### 花卉识别接口

#### 识别花卉
```
POST /api/flower/identify
Content-Type: multipart/form-data

参数:
- file: 图片文件

响应:
{
  "name": "月季花",
  "family": "蔷薇科",
  "color": "红色、粉色、黄色等",
  "bloomingPeriod": "5月-10月",
  "description": "...",
  "careGuide": "...",
  "flowerLanguage": "...",
  "confidence": 95.5
}
```

### 智能问答接口

#### 问答
```
POST /api/qa/chat
Content-Type: application/json

请求体:
{
  "question": "如何浇水？",
  "history": []
}

响应:
{
  "answer": "浇水要根据土壤干湿情况来决定..."
}
```

### 知识库接口

#### 获取所有花卉知识
```
GET /api/knowledge/?keyword=搜索关键词
```

#### 添加花卉知识
```
POST /api/knowledge/
Content-Type: application/json

请求体:
{
  "name": "月季",
  "family": "蔷薇科",
  "color": "红色、粉色、黄色等",
  "bloomingPeriod": "5月-10月",
  "description": "...",
  "careGuide": "...",
  "flowerLanguage": "..."
}
```

#### 更新花卉知识
```
PUT /api/knowledge/{flower_id}
```

#### 删除花卉知识
```
DELETE /api/knowledge/{flower_id}
```

## 启动方式

### 前端启动
```bash
cd flower-recognition-frontend
npm install
npm dev --port 5000 --host
```

### 后端启动
```bash
cd flower-recognition-backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## 环境变量

创建 `.env` 文件（如需要）：
```
# 后端配置
API_KEY=your_api_key
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 开发说明

### 前端开发
1. 修改代码后，Vite 会自动热更新
2. 访问 http://localhost:5000 查看前端页面

### 后端开发
1. 修改代码后，需要重启后端服务
2. 访问 http://localhost:8000/docs 查看API文档（Swagger UI）
3. 访问 http://localhost:8000/health 检查服务状态

## 后续优化方向

1. **大模型集成**: 集成真实的大模型API，替换模拟数据
2. **数据库集成**: 使用PostgreSQL存储知识库和历史记录
3. **对象存储**: 使用对象存储服务管理图片文件
4. **用户认证**: 添加用户登录和权限管理
5. **批量识别**: 实现批量图片识别功能
6. **流式响应**: 实现智能问答的流式输出
7. **性能优化**: 缓存、CDN、图片压缩等

## 注意事项

1. 当前版本使用模拟数据，大模型集成需要配置相应的API Key
2. 前端运行在 5000 端口，后端运行在 8000 端口
3. 已配置CORS，支持跨域请求
4. 使用Element Plus组件库，确保样式正确加载

## 许可证

MIT License