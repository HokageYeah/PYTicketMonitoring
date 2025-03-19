from functools import wraps
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum

def api_error_handler(platform=WxPlatformEnum.WX_MINI.value, api_path=None, error_msg=None):
    """
    API错误处理装饰器
    
    参数:
        platform: 平台标识，默认为微信小程序
        api_path: API路径，如果为None则会尝试从函数名生成
        
    用法:
        @api_error_handler(api_path='/custom/api/path')
        def your_function():
            # 业务逻辑
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 执行原始函数
                return func(*args, **kwargs)
            except Exception as e:
                # 如果没有提供API路径，则从函数名生成
                nonlocal api_path
                if api_path is None:
                    # 将函数名转换为API路径格式
                    # 例如: get_user_subscribe_monitor_list -> /wx/mini.get.user.subscribe.monitor.list
                    func_name = func.__name__
                    api_name = '.'.join(func_name.split('_'))
                    api_path = f'/wx/mini.{api_name}'
                
                # 记录错误
                print(f'{func.__name__}::error---------', e)
                
                # 返回标准化的错误响应
                return {
                    'platform': platform,
                    'ret': ["ERROR::" + (error_msg if error_msg is not None else str(e))],
                    'data': {},
                    'v': 1,
                    'api': api_path
                }
        return wrapper
    return decorator