import functools
from src.sql.models.user import User
# 缓存装饰器
def cache_result(cache, start_cache_key):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 使用wx_token作为缓存键
            # 判断 args是不是user类型
            if isinstance(args[0], User):
                cache_key = f"{start_cache_key}_{args[0].user_id}"
            elif isinstance(kwargs[0], User):
                cache_key = f"{start_cache_key}_{kwargs[0].user_id}"
            else:
                cache_key = f"{start_cache_key}"
            print('cache_result------cache_key---------', cache_key)
            print('args---------', args)
            print('kwargs---------', kwargs)
            
            # 尝试从缓存获取结果
            if cache_key in cache:
                print('cache_key in cache---------', cache[cache_key])
                return cache[cache_key]
            
            # 如果缓存中没有，执行原始函数
            result = func(self, *args, **kwargs)
            
            # 将结果存入缓存
            cache[cache_key] = result
            
            return result
        return wrapper
    return decorator

# 清除缓存
def clear_cache(cache, start_cache_key):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 判断 args是不是user类型
            if isinstance(args[0], User):
                cache_key = f"{start_cache_key}_{args[0].user_id}"
            elif isinstance(kwargs[0], User):
                cache_key = f"{start_cache_key}_{kwargs[0].user_id}"
            else:
                cache_key = f"{start_cache_key}"
            # 清除缓存
            print('clear_cache------cache_key---------', cache_key)
            if cache_key in cache:
                del cache[cache_key]
            return func(self, *args, **kwargs)
        return wrapper
    return decorator