from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
from app.api import flower, qa, knowledge

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

# 挂载前端静态文件
frontend_path = os.path.join(os.path.dirname(__file__), "../flower-recognition-frontend/dist")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# 前端路由 - 服务SPA应用
@app.get("/")
async def serve_frontend():
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(
            frontend_index,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            }
        )
    return {"message": "请先构建前端项目: cd flower-recognition-frontend && pnpm run build"}

# 处理所有其他路由，返回前端index.html
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # 如果是API请求，不处理
    if full_path.startswith("api/"):
        return {"error": "API endpoint not found"}
    # 返回前端index.html
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": "前端未构建"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
