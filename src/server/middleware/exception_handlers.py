from fastapi import Request, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
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

# 自定义请求参数异常处理器
async def request_validation_error_handler(request: Request, exc: RequestValidationError):
    """
    统一处理请求参数异常，转换为指定格式
    """
    print('request_validation_error_handler----exc----', exc)
    # 提示缺少哪个参数
    missing_fields = exc.errors()   
    print('missing_fields----', missing_fields)
    missing_field_names = [error['loc'][1] for error in missing_fields]
    missing_field_names_str = ', '.join(missing_field_names)
    print('missing_field_names_str----', missing_field_names_str)
    request_method = request.method
    request_url = request.url.path
    return JSONResponse(
        status_code=422,
        content={
            "platform": "WX_MINI",
            "ret": [f"ERROR::缺少必需的参数: {missing_field_names_str}"],
            "data": {request_method: request_method},
            "v": 1,
            "api": request_url.strip("/")
        }
    )