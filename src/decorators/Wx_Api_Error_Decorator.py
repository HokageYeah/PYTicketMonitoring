# from functools import wraps
# from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
# import time
# from datetime import datetime
# import logging
# def wx_api_error_decorator(platform=WxPlatformEnum.WX_MINI.value, api_path=None, error_msg=None, success_msg=None, errcode='errcode', errmsg='errmsg'):
#     """
#     微信API错误装饰器
#     参数:
#     platform: 平台类型，默认为微信小程序
#     api_path: API路径
#     error_msg: 错误信息
#     success_msg: 成功信息
#     business_error_key: 业务错误键
#     功能:
#     1. 捕获微信API调用过程中的异常
#     2. 记录错误信息
#     3. 发送邮件通知开发者
#     """
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             # 判断是否为类方法调用
#             is_method = len(args) > 0 and hasattr(args[0], '__class__')
#             # 如果是类方法，获取实例对象
#             instance = args[0] if is_method else None
#             try:
#                 # 记录开始时间
#                 start_time = time.time()
#                 result = func(*args, **kwargs)
#                 # 记录结束时间
#                 end_time = time.time()
#                 # 计算执行时间
#                 execution_time = end_time - start_time
#                 print(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
#                 # 检查业务错误
#                 if isinstance(result, dict) and errcode in result:
#                     error_code_key = result.get(errcode)
#                     if error_code_key != 0 and error_code_key != "0":
#                         # 构建错误信息
#                         error_info = {
#                             "error_msg": result.get("errmsg", error_msg or "微信API业务错误"),
#                             "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                             "error_platform": platform,
#                             "error_api": api_path or func.__name__,
#                             "error_code": error_code_key,
#                             "execution_time": f"{execution_time:.2f}秒"
#                         }
#                         print('wx_api_error_decorator---error_info---------', error_info)
#                         # 记录错误日志
#                         logging.error(f"微信API业务错误: {error_info}")
#                         # 发送邮件通知
#                         if instance and hasattr(instance, 'api_error_send_email'):
#                             try:
#                                 print('wx_api_error_decorator---instance---------', instance)
#                                 email_result = instance.api_error_send_email(error_info)
#                                 logging.info(f"错误邮件发送结果: {email_result}")
#                             except Exception as e:
#                                 print('wx_api_error_decorator---e---------', e)
#                                 logging.error(f"发送错误邮件失败: {str(e)}")
#                 return result
#             except Exception as e:
#                 # 构建异常信息
#                 exception_info = {
#                     "error_msg": str(e),
#                     "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#                     "error_platform": platform,
#                     "error_api": api_path or func.__name__,
#                     "error_type": type(e).__name__
#                 }
#                 # 记录异常日志
#                 print('wx_api_error_decorator---Exception---------', exception_info)
#                 logging.error(f"微信API调用异常: {exception_info}")
#                 # 发送邮件通知
#                 if instance and hasattr(instance, 'api_error_send_email'):
#                     try:
#                         email_result = instance.api_error_send_email(exception_info)
#                         logging.info(f"异常邮件发送结果: {email_result}")
#                     except Exception as email_error:
#                         logging.error(f"发送异常邮件失败: {str(email_error)}")
#                 return result
#         return wrapper
#     return decorator



import asyncio
from functools import wraps
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
import time
from datetime import datetime
import logging

def wx_api_error_decorator(platform=WxPlatformEnum.WX_MINI.value, api_path=None, 
                         error_msg=None, success_msg=None, 
                         errcode='errcode', errmsg='errmsg'):
    """
    支持异步的微信API错误装饰器
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            is_method = len(args) > 0 and hasattr(args[0], '__class__')
            instance = args[0] if is_method else None
            
            try:
                start_time = time.time()
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"Function {func.__name__} executed in {execution_time:.2f} seconds")

                if isinstance(result, dict) and errcode in result:
                    error_code_key = result.get(errcode)
                    if error_code_key != 0 and error_code_key != "0":
                        error_info = {
                            "error_msg": result.get(errmsg, error_msg or "微信API业务错误"),
                            "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "error_platform": platform,
                            "error_api": api_path or func.__name__,
                            "error_code": error_code_key,
                            "execution_time": f"{execution_time:.2f}秒"
                        }
                        logging.error(f"微信API业务错误: {error_info}")
                        
                        if instance and hasattr(instance, 'api_error_send_email'):
                            try:
                                email_result = await instance.api_error_send_email(error_info)
                                logging.info(f"错误邮件发送结果: {email_result}")
                            except Exception as e:
                                logging.error(f"发送错误邮件失败: {str(e)}")

                return result
            except Exception as e:
                exception_info = {
                    "error_msg": str(e),
                    "error_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "error_platform": platform,
                    "error_api": api_path or func.__name__,
                    "error_type": type(e).__name__
                }
                logging.error(f"微信API调用异常: {exception_info}")
                
                if instance and hasattr(instance, 'api_error_send_email'):
                    try:
                        email_result = await instance.api_error_send_email(exception_info)
                        logging.info(f"异常邮件发送结果: {email_result}")
                    except Exception as email_error:
                        logging.error(f"发送异常邮件失败: {str(email_error)}")
                raise  # 重新抛出异常或返回错误结果

        return async_wrapper
    return decorator