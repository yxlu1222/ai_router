from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .service import Service
import pathlib

app = FastAPI(title="AI Model Benchmark Router")
service = Service()

# 动态获取 static 目录路径
current_dir = pathlib.Path(__file__).parent.resolve()
static_dir = current_dir / "static"

# 挂载静态文件 (HTML)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
def read_root():
    # 访问根目录直接返回 HTML
    return FileResponse(str(static_dir / "index.html"))

@app.get("/api/stats")
def get_stats():
    """获取所有模型的当前统计数据"""
    return service.get_models_data()

@app.post("/api/refresh")
async def trigger_refresh():
    """触发新一轮测试"""
    return await service.run_refresh()

# --- 智能路由代理接口 ---

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """
    OpenAI 兼容的 Chat Completions 接口
    自动路由到最佳服务商
    """
    try:
        response = await service.route_chat_completion(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

