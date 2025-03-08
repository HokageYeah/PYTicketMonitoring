from pydantic import BaseModel, Field
from enum import Enum
class WxPlatformEnum(Enum):
    WX_MINI = "WX_MINI" # 微信小程序
    WX_H5 = "WX_H5" # 微信H5

class WxMiniApiResponse(BaseModel):
    platform: str
    ret: list[str]
    data: dict
    v: int
    api: str

class WxMiniLoginParams(BaseModel):
    # platform: str = Field(default=WxPlatformEnum.WX_MINI.value) # 平台
    code: str # 微信小程序code  
    entry: str = Field(default='') # 入口

class CreateUserParams(BaseModel):
    username: str
    password: str
    openid: str

class WxMiniSendSubscribeMessageParams(BaseModel):
    template_id: list[str]
    entry: str = Field(default='') # 入口

