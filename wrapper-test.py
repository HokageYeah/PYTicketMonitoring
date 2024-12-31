# def decorator(func):
#     def wrapper(*args, **kwargs):
#         """这是wrapper函数的文档字符串"""
#         print("函数执行前")
#         result = func(*args, **kwargs)
#         print("函数执行后")
#         return result
#     return wrapper

# @decorator
# def hello(name):
#     """这是hello函数的文档字符串"""
#     print(f"Hello, {name}!")

# # 查看函数信息
# print(hello.__name__)  # 输出: wrapper
# print(hello.__doc__)   # 输出: 这是wrapper函数的文档字符串


from functools import wraps

def decorator(func):
    @wraps(func)  # 保留原始函数的元数据
    def wrapper(*args, **kwargs):
        """这是wrapper函数的文档字符串"""
        print("函数执行前")
        result = func(*args, **kwargs)
        print("函数执行后")
        return result
    return wrapper

@decorator
def hellos(name):
    """这是hello函数的文档字符串"""
    print(f"Hello, {name}!")

# 查看函数信息
print(hellos.__name__)  # 输出: hellos
print(hellos.__doc__)   # 输出: 这是hellos函数的文档字符串
