from src.server.schemas.concert import RecordMonitorParams
from fastapi import HTTPException, Body
from src.server.schemas.wxMiniLoginSchema import WxMiniLoginParams, CreateUserParams, WxMiniSendSubscribeMessageParams, WxMiniGetUserSubscribeMonitorListParams, WxMiniDeleteUserSubscribeMonitorParams
from pydantic import BaseModel
from src.server.schemas.wxMiniLoginSchema import WxMiniGetAccessTokenParams

def validate_common_method(params: BaseModel, required_fields: list):
    print('validate_params::required_fields---------', required_fields)
    # 检查必需字段是否在请求参数中
    for field in required_fields:
        print('validate_params::field---------', field)
        if getattr(params, field) is None:
            raise HTTPException(
                status_code=422,
                detail=f"缺少必需的参数: {field}"
            )
    return params
# 创建自定义的依赖项(进行参数教研)
async def validate_record_monitor_params(params: RecordMonitorParams = Body(...)) -> RecordMonitorParams:
    # 获取必需字段
    required_fields = [name for name, field in RecordMonitorParams.model_fields.items() if field.default is ...]
    # print('validate_params::required_fields---------', required_fields)
    # # 检查必需字段是否在请求参数中
    # for field in required_fields:
    #     print('validate_params::field---------', field)
    #     if getattr(params, field) is None:
    #         raise HTTPException(
    #             status_code=422,
    #             detail=f"缺少必需的参数: {field}"
    #         )
    # return params
    return validate_common_method(params, required_fields)

async def validate_wx_mini_login_params(params: WxMiniLoginParams = Body(...)) -> WxMiniLoginParams:
    # 获取必需字段
    required_fields = [name for name, field in WxMiniLoginParams.model_fields.items() if field.default is ...]
    return validate_common_method(params, required_fields)

async def validate_wx_mini_send_subscribe_message_params(params: WxMiniSendSubscribeMessageParams = Body(...)) -> WxMiniSendSubscribeMessageParams:
    # 获取必需字段
    required_fields = [name for name, field in WxMiniSendSubscribeMessageParams.model_fields.items() if field.default is ...]
    return validate_common_method(params, required_fields)

async def validate_wx_mini_get_user_subscribe_monitor_list_params(params: WxMiniGetUserSubscribeMonitorListParams = Body(...)) -> WxMiniGetUserSubscribeMonitorListParams:
    # 获取必需字段
    required_fields = [name for name, field in WxMiniGetUserSubscribeMonitorListParams.model_fields.items() if field.default is ...]
    return validate_common_method(params, required_fields)

async def validate_create_user_params(params: CreateUserParams = Body(...)) -> CreateUserParams:
    # 获取必需字段
    required_fields = [name for name, field in CreateUserParams.model_fields.items() if field.default is ...]
    return validate_common_method(params, required_fields)

async def validate_wx_mini_get_access_token_params(params: WxMiniGetAccessTokenParams = Body(...)) -> WxMiniGetAccessTokenParams:
    # 获取必需字段
    required_fields = [name for name, field in WxMiniGetAccessTokenParams.model_fields.items() if field.default is ...]
    return validate_common_method(params, required_fields)

async def validate_wx_mini_delete_user_subscribe_monitor_params(params: WxMiniDeleteUserSubscribeMonitorParams = Body(...)) -> WxMiniDeleteUserSubscribeMonitorParams:
    # 获取必需字段
    required_fields = [name for name, field in WxMiniDeleteUserSubscribeMonitorParams.model_fields.items() if field.default is ...]
    return validate_common_method(params, required_fields)

# 一下AI生成代码，可以通过装饰器优化上面代码
# T = TypeVar('T', bound=BaseModel)

# def validate_params(model_class: Type[T]):
#     """
#     通用的参数验证装饰器
    
#     用法示例：
#     @validate_params(WxMiniLoginParams)
#     async def wx_mini_login(params: WxMiniLoginParams = Body(...)) -> WxMiniLoginParams:
#         return params
#     """
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(params: T = Body(...)) -> T:
#             # 获取必需字段
#             required_fields = [
#                 name for name, field in model_class.model_fields.items() 
#                 if field.default is ...
#             ]
#             return validate_common_method(params, required_fields)
#         return wrapper
#     return decorator
# 如果你想添加更多验证规则,可以修改装饰器如下
# def validate_params(model_class: Type[T], additional_validations: list = None):
#     """
#     带额外验证规则的装饰器
    
#     用法示例：
#     @validate_params(WxMiniLoginParams, [
#         lambda params: params.age >= 18,  # 检查年龄
#     ])
#     async def wx_mini_login(params: WxMiniLoginParams = Body(...)) -> WxMiniLoginParams:
#         return params
#     """
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(params: T = Body(...)) -> T:
#             # 基本字段验证
#             required_fields = [
#                 name for name, field in model_class.model_fields.items() 
#                 if field.default is ...
#             ]
#             validated_params = validate_common_method(params, required_fields)
            
#             # 额外验证规则
#             if additional_validations:
#                 for validation in additional_validations:
#                     if not validation(validated_params):
#                         raise HTTPException(
#                             status_code=422,
#                             detail="参数验证失败"
#                         )
            
#             return validated_params
#         return wrapper
#     return decorator
# 使用装饰器重写原有函数
# @validate_params(WxMiniLoginParams)
# async def validate_wx_mini_login_params(params: WxMiniLoginParams = Body(...)) -> WxMiniLoginParams:
#     return params

# @validate_params(WxMiniSendSubscribeMessageParams)
# async def validate_wx_mini_send_subscribe_message_params(
#     params: WxMiniSendSubscribeMessageParams = Body(...)
# ) -> WxMiniSendSubscribeMessageParams:
#     return params

# @validate_params(CreateUserParams)
# async def validate_create_user_params(params: CreateUserParams = Body(...)) -> CreateUserParams:
#     return params