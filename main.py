from src.server.core import setup_logging
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.server.core import settings
import logging
from src.server.api.endpoints.concerts import router
from pydantic import ValidationError

# 最开始添项目根目录到python的路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 设置日志
setup_logging()

# 创建fastapi 应用
app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

# 定义全局请求参数异常处理器（可选）
@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request, exc: RequestValidationError):
    print('request_validation_error_handler----exc----', exc)
    # 提示缺少哪个参数
    missing_fields = exc.errors()   
    print('missing_fields----', missing_fields)
    missing_field_names = [error['loc'][1] for error in missing_fields]
    missing_field_names_str = ', '.join(missing_field_names)
    print('missing_field_names_str----', missing_field_names_str)
    request_method = request.method
    request_url = str(request.url)
    return JSONResponse(
        status_code=422,
        content={
            "error_detail": f"缺少必需的参数: {missing_field_names_str}",
            "request_method": request_method,
            "request_url": request_url,
        }
    )

# 定义全局错误处理器
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    print('http_exception_handler----exc----', exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    

# 添加路由
app.include_router(router, prefix=settings.API_V1_STR, tags=["concerts"])

@app.on_event("startup")
async def startup():
    setup_logging()
    logging.info("FastAPI 应用启动")

@app.on_event("shutdown")
async def shutdown():
    logging.info("FastAPI 应用关闭")

