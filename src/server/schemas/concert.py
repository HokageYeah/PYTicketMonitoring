from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
from typing_extensions import TypedDict, NotRequired
class PlatformEnum(Enum):
    DM = "DM" # 大麦
    MY = "MY" # 猫眼

class City(BaseModel):
    city_id: int
    name: str
    platform: PlatformEnum # 这个类型是枚举

class ApiResponseData(BaseModel):
    platform: PlatformEnum
    api: str
    data: dict
    ret: list
    v: int

class SkuList(BaseModel):
    sku_id: str # 座次id
    price_id: str # 价格id
    price_name: str # 座次名字 （价格名字）

class TicketPerform(BaseModel):
    perform_id: str # 场次id （表演id）
    perform_name: str # 场次名字 （表演名字）
    sku_list: List[SkuList] # 座次

# 记录用户需要监控的演唱会、场次、座次、时间、微信token、 监控时间 参数类型
class RecordMonitorParams(BaseModel):
    show_id: str # 演唱会id
    show_name: str # 演唱会名字
    venue_city_name: str # 演唱会城市
    venue_name: str # 演唱会场馆
    ticket_perform: List[TicketPerform] # 场次
    time: Optional[str] = Field(None, description="可选参数") # 将 time 标记为可选
    wx_token: str # 微信token (发送监控通知)
    deadline: str # 监控时间持续时间
    @field_validator('wx_token')
    def validate_wx_token(cls, v):
        if not v:
            raise ValueError("wx_token 不能为空")
        return v