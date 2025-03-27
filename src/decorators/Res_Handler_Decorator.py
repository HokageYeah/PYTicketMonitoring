import functools
import asyncio
import inspect
import logging
import asyncio
from src.server.core.confing import settings
from src.server.untiles.Email_Sender import EmailSender
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
from datetime import datetime
from src.server.schemas import PlatformEnum
from functools import wraps
import time

# def wx_mini_response_handler(platform=WxPlatformEnum.WX_MINI.value, api_path=None, error_msg=None, success_msg=None):
#     def decorator(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             # 如果没有提供API路径，则从函数名生成
#             nonlocal api_path
#             if api_path is None:
#                 # 将函数名转换为API路径格式
#                 func_name = func.__name__
#                 api_name = '.'.join(func_name.split('_'))
#                 api_path = f'/api.{api_name}'
#             try:
#                 # 检查函数是否是协程函数
#                 if asyncio.iscoroutinefunction(func):
#                     # 获取当前事件循环
#                     try:
#                         loop = asyncio.get_event_loop()
#                     except RuntimeError:
#                         # 如果没有事件循环，创建一个新的
#                         loop = asyncio.new_event_loop()
#                         asyncio.set_event_loop(loop)
                    
#                     # 检查事件循环是否正在运行
#                     if loop.is_running():
#                         # 如果事件循环正在运行，我们需要使用 run_coroutine_threadsafe
#                         # 但这在同步上下文中不起作用，所以我们需要一个替代方案
#                         # 在这种情况下，我们返回协程对象，让调用者处理它
#                         logging.warning(f"{func.__name__} 返回协程对象，需要在异步上下文中使用 await")
#                         return {
#                             'platform': platform,
#                             'ret': ["ERROR::" + f"{error_msg}: 需要在异步上下文中调用"],
#                             'data': {},
#                             'v': 1,
#                             'api': api_path + 'test------1'
#                         }
#                     else:
#                         # 如果事件循环没有运行，我们可以运行协程
#                         try:
#                             result = loop.run_until_complete(func(*args, **kwargs))
#                         except Exception as e:
#                             logging.error(f"{func.__name__} 执行失败: {str(e)}")
#                             return {
#                                 'platform': platform,
#                                 'ret': ["ERROR::" + f"{error_msg}: {str(e)}"],
#                                 'data': {},
#                                 'v': 1,
#                                 'api': api_path + 'test------2'
#                             }
#                 else:
#                     # 如果是普通函数，直接调用
#                     result = func(*args, **kwargs)
                
#                 # 处理结果
#                 if result and isinstance(result, dict) and result.get('errcode', 0) == 0:
#                     return {
#                         'platform': platform,
#                         'ret': [f"SUCCESS::{success_msg}"],
#                         'data': result,
#                         'v': 1,
#                         'api': api_path + 'test------3'
#                     }
#                 else:
#                     return {
#                         'platform': platform,
#                         'ret': ["ERROR::" + result.get('errmsg', error_msg)],
#                         'data': result,
#                         'v': 1,
#                         'api': api_path + 'test------4'
#                     }
#             except Exception as e:
#                 logging.error(f"{func.__name__}::error--------- {str(e)}")
#                 return {
#                     'platform': platform,
#                     'ret': ["ERROR::" + f"{error_msg}: {str(e)}"],
#                     'data': {},
#                     'v': 1,
#                     'api': api_path + 'test------5'
#                 }
        
#         # 创建一个异步包装器
#         @functools.wraps(func)
#         async def async_wrapper(*args, **kwargs):
#             try:
#                 # 直接等待异步函数
#                 result = await func(*args, **kwargs)
                
#                 # 处理结果
#                 if result and isinstance(result, dict) and result.get('errcode', 0) == 0:
#                     return {
#                         'platform': platform,
#                         'ret': [f"SUCCESS::{success_msg}"],
#                         'data': result,
#                         'v': 1,
#                         'api': api_path + 'test------6'
#                     }
#                 else:
#                     return {
#                         'platform': platform,
#                         'ret': ["ERROR::" + result.get('errmsg', error_msg)],
#                         'data': result,
#                         'v': 1,
#                         'api': api_path + 'test------7'
#                     }
#             except Exception as e:
#                 logging.error(f"{func.__name__}::error--------- {str(e)}")
#                 return {
#                     'code': -1,
#                     'msg': f"{error_msg}: {str(e)}",
#                     'data': {}
#                 }
        
#         # 根据原函数是否为协程函数返回相应的包装器
#         if asyncio.iscoroutinefunction(func):
#             return async_wrapper
#         else:
#             return wrapper
    
#     return decorator



def api_error_send_email(params):
    """
    同步版本的API错误邮件发送方法
    
    参数:
        params: 错误参数
    
    返回:
        发送结果
    """
    try:
        # 获取当前事件循环
        try:
            email_service = EmailSender(settings)
            loop = asyncio.get_event_loop()
            print(f"WxService api_error_send_email loop: {loop}")
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print(f"WxService api_error_send_email created new loop: {loop}")
        # 如果事件循环没有运行，我们可以运行异步函数
        async def send_email_async():
            await email_service.send_three_party_api_error_email(params)
        # 检查事件循环是否正在运行
        if loop.is_running():
            # 如果事件循环正在运行，我们不能再运行一个事件循环
            # 在这种情况下，我们可以选择跳过发送邮件或使用其他方式
            print(f"事件循环正在运行，使用当前事件循环发送邮件")
            # 如果事件循环正在运行，创建后台任务
            asyncio.create_task(send_email_async())
            logging.info(f"事件循环正在运行，发送邮件通知到 {settings.QQ_MAIL_FROM}")
            return '事件循环正在运行，发送邮件成功'
        else:
            try:
                # 如果事件循环没有运行，同步执行, 同步执行需要等待邮件发送完成
                loop.run_until_complete(send_email_async())
                logging.info(f"已发送邮件通知到 {settings.QQ_MAIL_FROM}")
                return '邮件发送成功'
            except Exception as e:
                logging.error(f"api_error_send_email 执行失败: {str(e)}")
                return f'邮件发送失败: {str(e)}'
    except Exception as e:
        logging.error(f"api_error_send_email 执行失败: {str(e)}")
        return f'邮件发送失败: {str(e)}'


def send_error_email(error_info):
    # 去掉ERROR::
    error_info['error_msg'] = error_info.get('error_msg', "微信API业务错误").replace("ERROR::", "") \
        if error_info.get('error_msg', "微信API业务错误").startswith("ERROR::") \
        else error_info.get('error_msg', "微信API业务错误")
    # 去掉ERRORCODE::
    error_info['error_code'] = error_info.get('error_code', "0").replace("ERRORCODE::", "")\
        if error_info.get('error_code', "").startswith("ERRORCODE::") \
        else error_info.get('error_code', "0")
    error_info = {
        "error_msg": error_info.get('error_msg', "微信API业务错误"),
        "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "error_platform": error_info.get('error_platform', ""),
        "error_api": error_info.get('error_api', ""),
        "error_code": error_info.get('error_code', ""),
        "execution_time": error_info.get('execution_time', "")
    }
    print('send_error_email---------', error_info)
    api_error_send_email(error_info)


def new_api_response_handler(platform=WxPlatformEnum.WX_MINI.value, api_path=None, error_msg=None, success_msg=None, business_error_key='ret', error_email=False):
    def decorator(func):
        # 检查是否为协程函数
        is_coroutine = inspect.iscoroutinefunction(func)
        # 如果没有提供API路径，则从函数名生成
        nonlocal_api_path = api_path
        if nonlocal_api_path is None:
            # 将函数名转换为API路径格式
            func_name = func.__name__
            api_name = '.'.join(func_name.split('_'))
            nonlocal_api_path = f'/wx/mini.{api_name}'
        # 处理响应的通用函数
        def process_response(result, execution_time):
            print('result---------1', result)
            # 检查结果是否已经是标准格式
            if isinstance(result, dict) and all(key in result for key in ['platform', 'ret', 'data', 'v', 'api']):
                return result
            print('result---------2', result)
            # 检查业务错误
            if isinstance(result, dict) and business_error_key in result:
                print('result---------3', result)
                error_value = result.get(business_error_key)
                if isinstance(error_value, list) and any(isinstance(err, str) and err.startswith("ERROR::") for err in error_value):
                    # 记录业务错误
                    business_error = next((err for err in error_value if err.startswith("ERROR::")), "ERROR::未知业务错误")
                    business_error_code = next((err for err in error_value if err.startswith("ERRORCODE::")), "ERRORCODE::0")
                    print(f'{func.__name__}::business_error---------', business_error)
                    print(f'{func.__name__}::business_error_code---------', business_error_code)
                    logging.error(f"{func.__name__} 业务错误: {business_error}")
                    # 如果需要发送邮件，则发送邮件
                    if error_email:
                        print('需要发送邮件------business_error------', business_error)
                        send_error_email({
                            "error_msg": business_error,
                            "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "error_platform": platform,
                            "error_api": api_path,
                            "error_code": business_error_code,
                            "execution_time": f"{execution_time:.2f}秒"
                        })
                    # 构建标准错误响应
                    data = result.get('data', {})
                    
                    return {
                        'platform': platform,
                        'ret': error_value,
                        'data': data,
                        'v': 1,
                        'api': api_path
                        }
            # 处理成功响应
            # 使用自定义成功消息或默认消息
            success_message = success_msg if success_msg else "操作成功"
            print('success_message---------', success_message)
            # 如果结果是字典且包含data键，使用它作为data
            if isinstance(result, dict) and 'data' in result:
                data = result.get('data')
            else:
                # 否则整个结果作为data
                data = result
            print('data---------', data)
            return {
                'platform': platform,
                'ret': [f"SUCCESS::{success_message}"],
                'data': data,
                'v': 1,
                'api': api_path
            }
        # 处理异常的通用函数
        def handle_exception(e, execution_time='', **kwargs):
            # 记录错误
            print(f'{func.__name__}::error---------', e)
            logging.error(f"{func.__name__} 执行失败: {str(e)}")
            # 使用自定义错误消息或异常信息
            error_message = error_msg + str(e) if error_msg else str(e)
            # 检查是否有额外的错误数据需要传递
            sig = inspect.signature(func)
            error_data = {}
            # 如果函数有 error_data 参数，并且在调用时提供了该参数
            if 'error_data' in sig.parameters and 'error_data' in kwargs:
                error_data = kwargs['error_data']
             # 如果需要发送邮件，则发送邮件
            if error_email:
                print('需要发送邮件------error_message------', error_message)
                send_error_email({
                    "error_msg": error_message,
                    "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "error_platform": platform,
                    "error_api": api_path,
                    "error_code": "0",
                    "execution_time": f"{execution_time:.2f}秒"
                })
            # 返回标准化的错误响应
            return {
                'platform': platform,
                'ret': ["ERROR::" + error_message],
                'data': error_data,
                'v': 1,
                'api': api_path
            }
        # 如果为协程函数，则返回异步包装器
        if is_coroutine:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    # 执行原始异步函数
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    return process_response(result, execution_time)
                except Exception as e:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    return handle_exception(e, execution_time=execution_time, **kwargs)
            return async_wrapper
        else:
            # 如果为同步函数，则返回同步包装器
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    # 执行原始同步函数
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    return process_response(result, execution_time)
                except Exception as e:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    return handle_exception(e, **kwargs, execution_time=execution_time)
            return sync_wrapper
    return decorator



# 添加平台特定的响应处理装饰器
def wx_mini_response_handler(api_path=None, error_msg=None, success_msg=None, business_error_key='ret', error_email=False):
    """微信小程序API响应处理装饰器"""
    return new_api_response_handler(
        platform=WxPlatformEnum.WX_MINI.value,
        api_path=api_path,
        error_msg=error_msg,
        success_msg=success_msg,
        business_error_key=business_error_key,
        error_email=error_email
    )

def damai_response_handler(api_path=None, error_msg=None, success_msg=None, business_error_key='ret', error_email=False):
    """大麦网API响应处理装饰器"""
    return new_api_response_handler(
        platform=PlatformEnum.DM.value,
        api_path=api_path,
        error_msg=error_msg,
        success_msg=success_msg,
        business_error_key=business_error_key,
        error_email=error_email
    )

def maoyan_response_handler(api_path=None, error_msg=None, success_msg=None, business_error_key='ret', error_email=False):
    """猫眼API响应处理装饰器"""
    return new_api_response_handler(
        platform=PlatformEnum.MY.value,
        api_path=api_path,
        error_msg=error_msg,
        success_msg=success_msg,
        business_error_key=business_error_key,
        error_email=error_email
    )

def weipiao_response_handler(api_path=None, error_msg=None, success_msg=None, business_error_key='ret', error_email=False):
    """微票API响应处理装饰器"""
    return new_api_response_handler(
        platform=PlatformEnum.WP.value,
        api_path=api_path,
        error_msg=error_msg,
        success_msg=success_msg,
        business_error_key=business_error_key,
        error_email=error_email
    )

def success_response(data=None, platform=WxPlatformEnum.WX_MINI.value, api_path=None, message="操作成功"):
    """
    生成成功响应
    
    参数:
        data: 响应数据
        platform: 平台标识
        api_path: API路径
        message: 成功消息
    """
    return {
        'platform': platform,
        'ret': [f"SUCCESS::{message}"],
        'data': data or {},
        'v': 1,
        'api': api_path or '/api'
    }

def error_response(message, data=None, platform=WxPlatformEnum.WX_MINI.value, api_path=None):
    """
    生成错误响应
    
    参数:
        message: 错误消息
        data: 错误相关数据
        platform: 平台标识
        api_path: API路径
    """
    # 确保错误消息以 ERROR:: 开头
    if not message.startswith("ERROR::"):
        message = f"ERROR::{message}"
        
    return {
        'platform': platform,
        'ret': [message],
        'data': data or {},
        'v': 1,
        'api': api_path or '/api'
    }