from src.server.schemas.concert import RecordMonitorParams
from fastapi import HTTPException, Body

# 创建自定义的依赖项(进行参数教研)
async def validate_record_monitor_params(params: RecordMonitorParams = Body(...)) -> RecordMonitorParams:
    # 获取必需字段
    required_fields = [name for name, field in RecordMonitorParams.model_fields.items() if field.default is ...]
    print('required_fields---------', required_fields)
    # 检查必需字段是否在请求参数中
    for field in required_fields:
        print('field---------', field)
        if getattr(params, field) is None:
            raise HTTPException(
                status_code=422,
                detail=f"缺少必需的参数: {field}"
            )
    return params