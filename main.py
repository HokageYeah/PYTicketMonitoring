from src.server.core import setup_logging
import os
import sys
from fastapi import FastAPI
from src.server.core import settings
import logging
from src.server.api.endpoints.concerts import router

# 最开始添项目根目录到python的路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 设置日志
setup_logging()

# 创建fastapi 应用
app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

# 添加路由
app.include_router(router, prefix=settings.API_V1_STR, tags=["concerts"])

@app.on_event("startup")
async def startup():
    setup_logging()
    logging.info("FastAPI 应用启动")

@app.on_event("shutdown")
async def shutdown():
    logging.info("FastAPI 应用关闭")