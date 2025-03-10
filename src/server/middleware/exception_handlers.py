from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

# 自定义HTTP异常处理器
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    统一处理HTTP异常，转换为指定格式
    """
    # 检查是否已包含自定义格式
    if isinstance(exc.detail, dict) and 'platform' in exc.detail and 'ret' in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    
    # 获取路径信息
    path = request.url.path
    platform = "unknown"
    
    # 根据路径判断平台
    if "wx/mini" in path:
        platform = "WX_MINI"
    
    # 构建标准响应格式
    response_content = {
        'platform': platform,
        'ret': [f"ERROR::{exc.detail}"],
        'data': {},
        'v': 1,
        'api': path.strip("/")
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_content
    ) 