from src.server.core import setup_logging
import os
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.sql.sqlalchemy_db import database

from src.server.core import settings
import logging
from src.server.api.endpoints.concerts import router
from pydantic import ValidationError
from src.server.api.wxMiniLogin import wx_router
from src.server.middleware.exception_handlers import http_exception_handler, request_validation_error_handler
import uvicorn
from contextlib import asynccontextmanager
import multiprocessing
# from src.sql import sql_connect_db
# 最开始添项目根目录到python的路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 设置日志
setup_logging()

def new_callback_func():
    # 调用web/start.monitor.by.platform接口
    print('更改了user_show_monitor表，调用票务监控接口')
    # damai.post_start_new_monitor_web(threadStop=True)

# 定义应用的生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行（原 startup 事件的代码）
    print("应用启动")
    try:
        # -----------------------新增代码开始-----------------------
        # 检查当前进程是否是工作进程, 解决uvicorn 的 reload=True 选项会创建两个独立的进程（监控进程和工作进程），每个进程都有自己的 Python 解释器和内存空间。
        # 导致线程监控会启动两次，一个是在工作主进程中，一个是在文件监控进程中
        current_process = multiprocessing.current_process()
        if current_process.name != 'MainProcess' or os.environ.get('UVICORN_RELOAD_PROCESS') != 'true':
            # 只在工作进程中启动监控
            from src.server.untiles.New_DB_Mointor import NewDBDataMonitor
            from src.server.services.damai import DamaiService
            # 正确传递回调函数：使用lambda或者partial创建一个可调用对象
            from functools import partial
            callback = partial(DamaiService().post_start_new_monitor_web, threadStop=True)
            print(f"在进程 {current_process.name} 中启动监控")
            # todo 先暂停监控，测试用户信息登录
            # monitor = NewDBDataMonitor(callback)
            # monitor.start_monitor()
        else:
            print(f"在监控进程 {current_process.name} 中不启动监控")
        # -----------------------新增代码结束-----------------------
        yield
    finally:
        # 关闭时执行（原 shutdown 事件的代码）
        print("应用关闭")

# 创建fastapi 应用
app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG, lifespan=lifespan)

# 创建数据库连接池
# sql_connect_db.connect()
print('database.connect()3')
database.connect()
# 定义全局请求参数异常处理器exception_class : 要处理的异常类型、handler : 处理异常的函数
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
# 定义全局请求参数异常处理器（可选） 上下两种不同的方式
# @app.exception_handler(RequestValidationError)
# async def request_validation_error_handler(request: Request, exc: RequestValidationError):
#     print('request_validation_error_handler----exc----', exc)
#     # 提示缺少哪个参数
#     missing_fields = exc.errors()   
#     print('missing_fields----', missing_fields)
#     missing_field_names = [error['loc'][1] for error in missing_fields]
#     missing_field_names_str = ', '.join(missing_field_names)
#     print('missing_field_names_str----', missing_field_names_str)
#     request_method = request.method
#     request_url = request.url.path
#     return JSONResponse(
#         status_code=422,
#         content={
#             "platform": "WX_MINI",
#             "ret": [f"ERROR::缺少必需的参数: {missing_field_names_str}"],
#             "data": {request_method: request_method},
#             "v": 1,
#             "api": request_url.strip("/")
#         }
#     )

# 定义全局错误处理器，单独封装成一个中间价，并且统一返回相同的格式
app.add_exception_handler(HTTPException, http_exception_handler)
# # 定义全局错误处理器（老的处理方式）
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request, exc: HTTPException):
#     print('http_exception_handler----exc----', exc)
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detailHokageYeah": exc.detail}
#     )
    

# 添加路由  tags: API 文档中的标签分类
app.include_router(router, prefix=settings.API_V1_STR, tags=["concerts"])
app.include_router(wx_router, prefix=settings.API_V1_STR, tags=["wx"])

# @app.on_event() 装饰器已经被废弃， 建议使用新的 lifespan 事件处理器
# @app.on_event("startup")
# async def startup():
#     setup_logging()
#     logging.info("FastAPI 应用启动")

# @app.on_event("shutdown")
# async def shutdown():
#     logging.info("FastAPI 应用关闭")


# 运行 python main.py 启动服务,代替 运行命令：uvicorn main:app --reload --port 8001， 此命令适合再开发环境使用
if __name__ == "__main__":
    uvicorn.run('main:app', host="localhost", port=8001, reload=True)
