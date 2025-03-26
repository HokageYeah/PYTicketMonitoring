from functools import wraps
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
from src.server.schemas import PlatformEnum
import logging
import inspect

def api_response_handler(platform=WxPlatformEnum.WX_MINI.value, api_path=None, error_msg=None, success_msg=None, business_error_key='ret'):
    """
    API 统一响应处理装饰器
    
    参数:
        platform: 平台标识，默认为微信小程序
        api_path: API路径，如果为None则会尝试从函数名生成
        error_msg: 自定义错误消息，如果为None则使用异常信息
        success_msg: 自定义成功消息，如果为None则使用默认的"操作成功"
        business_error_key: 业务错误的键名，用于检查业务逻辑错误
        
    用法:
        @api_response_handler(api_path='/custom/api/path', success_msg="查询成功")
        def your_function():
            # 业务逻辑
            return result  # 可以返回任何数据，装饰器会自动格式化
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果没有提供API路径，则从函数名生成
            nonlocal api_path
            if api_path is None:
                # 将函数名转换为API路径格式
                func_name = func.__name__
                api_name = '.'.join(func_name.split('_'))
                api_path = f'/api.{api_name}'
            
            try:
                # 执行原始函数
                result = func(*args, **kwargs)
                
                # 检查结果是否已经是标准格式
                if isinstance(result, dict) and all(key in result for key in ['platform', 'ret', 'data', 'v', 'api']):
                    return result
                
                # 检查业务错误
                if isinstance(result, dict) and business_error_key in result:
                    error_value = result.get(business_error_key)
                    if isinstance(error_value, list) and any(isinstance(err, str) and err.startswith("ERROR::") for err in error_value):
                        # 记录业务错误
                        business_error = next((err for err in error_value if err.startswith("ERROR::")), "ERROR::未知业务错误")
                        print(f'{func.__name__}::business_error---------', business_error)
                        logging.error(f"{func.__name__} 业务错误: {business_error}")
                        
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
                
                # 如果结果是字典且包含data键，使用它作为data
                if isinstance(result, dict) and 'data' in result:
                    data = result.get('data')
                else:
                    # 否则整个结果作为data
                    data = result
                
                return {
                    'platform': platform,
                    'ret': [f"SUCCESS::{success_message}"],
                    'data': data,
                    'v': 1,
                    'api': api_path
                }
                
            except Exception as e:
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
                
                # 返回标准化的错误响应
                return {
                    'platform': platform,
                    'ret': ["ERROR::" + error_message],
                    'data': error_data,
                    'v': 1,
                    'api': api_path
                }
        return wrapper
    return decorator

# # 添加平台特定的响应处理装饰器
# def wx_mini_response_handler(api_path=None, error_msg=None, success_msg=None):
#     """微信小程序API响应处理装饰器"""
#     return api_response_handler(
#         platform=WxPlatformEnum.WX_MINI.value,
#         api_path=api_path,
#         error_msg=error_msg,
#         success_msg=success_msg
#     )

def damai_response_handler(api_path=None, error_msg=None, success_msg=None):
    """大麦网API响应处理装饰器"""
    return api_response_handler(
        platform=PlatformEnum.DM.value,
        api_path=api_path,
        error_msg=error_msg,
        success_msg=success_msg
    )

def maoyan_response_handler(api_path=None, error_msg=None, success_msg=None):
    """猫眼API响应处理装饰器"""
    return api_response_handler(
        platform=PlatformEnum.MY.value,
        api_path=api_path,
        error_msg=error_msg,
        success_msg=success_msg
    )

def weipiao_response_handler(api_path=None, error_msg=None, success_msg=None):
    """微票API响应处理装饰器"""
    return api_response_handler(
        platform=PlatformEnum.WP.value,
        api_path=api_path,
        error_msg=error_msg,
        success_msg=success_msg
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







import functools
import asyncio
import inspect
import logging

def wx_mini_response_handler(platform=WxPlatformEnum.WX_MINI.value, api_path=None, error_msg=None, success_msg=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 如果没有提供API路径，则从函数名生成
            nonlocal api_path
            if api_path is None:
                # 将函数名转换为API路径格式
                func_name = func.__name__
                api_name = '.'.join(func_name.split('_'))
                api_path = f'/api.{api_name}'
            try:
                # 检查函数是否是协程函数
                if asyncio.iscoroutinefunction(func):
                    # 获取当前事件循环
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        # 如果没有事件循环，创建一个新的
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # 检查事件循环是否正在运行
                    if loop.is_running():
                        # 如果事件循环正在运行，我们需要使用 run_coroutine_threadsafe
                        # 但这在同步上下文中不起作用，所以我们需要一个替代方案
                        # 在这种情况下，我们返回协程对象，让调用者处理它
                        logging.warning(f"{func.__name__} 返回协程对象，需要在异步上下文中使用 await")
                        return {
                            'platform': platform,
                            'ret': ["ERROR::" + f"{error_msg}: 需要在异步上下文中调用"],
                            'data': {},
                            'v': 1,
                            'api': api_path
                        }
                    else:
                        # 如果事件循环没有运行，我们可以运行协程
                        try:
                            result = loop.run_until_complete(func(*args, **kwargs))
                        except Exception as e:
                            logging.error(f"{func.__name__} 执行失败: {str(e)}")
                            return {
                                'platform': platform,
                                'ret': ["ERROR::" + f"{error_msg}: {str(e)}"],
                                'data': {},
                                'v': 1,
                                'api': api_path
                            }
                else:
                    # 如果是普通函数，直接调用
                    result = func(*args, **kwargs)
                
                # 处理结果
                if result and isinstance(result, dict) and result.get('errcode', 0) == 0:
                    return {
                        'platform': platform,
                        'ret': [f"SUCCESS::{success_msg}"],
                        'data': result,
                        'v': 1,
                        'api': api_path
                    }
                else:
                    return {
                        'platform': platform,
                        'ret': ["ERROR::" + result.get('errmsg', error_msg)],
                        'data': result,
                        'v': 1,
                        'api': api_path
                    }
            except Exception as e:
                logging.error(f"{func.__name__}::error--------- {str(e)}")
                return {
                    'platform': platform,
                    'ret': ["ERROR::" + f"{error_msg}: {str(e)}"],
                    'data': {},
                    'v': 1,
                    'api': api_path
                }
        
        # 创建一个异步包装器
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # 直接等待异步函数
                result = await func(*args, **kwargs)
                
                # 处理结果
                if result and isinstance(result, dict) and result.get('errcode', 0) == 0:
                    return {
                        'platform': platform,
                        'ret': [f"SUCCESS::{success_msg}"],
                        'data': result,
                        'v': 1,
                        'api': api_path
                    }
                else:
                    return {
                        'platform': platform,
                        'ret': ["ERROR::" + result.get('errmsg', error_msg)],
                        'data': result,
                        'v': 1,
                        'api': api_path
                    }
            except Exception as e:
                logging.error(f"{func.__name__}::error--------- {str(e)}")
                return {
                    'code': -1,
                    'msg': f"{error_msg}: {str(e)}",
                    'data': {}
                }
        
        # 根据原函数是否为协程函数返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator