from pydantic import BaseModel, Field
from enum import Enum
class WxPlatformEnum(Enum):
    WX_MINI = "WX_MINI" # 微信小程序

class WxMiniApiResponse(BaseModel):
    platform: WxPlatformEnum
    ret: str
    data: str

class WxMiniLoginParams(BaseModel):
    code: str
