from src.server.schemas.concert import RecordMonitorParams
from fastapi import HTTPException, Body
from src.server.schemas.wxMiniLoginSchema import WxMiniLoginParams
from pydantic import BaseModel

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
