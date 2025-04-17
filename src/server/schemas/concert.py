from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union
from enum import Enum
from typing_extensions import TypedDict, NotRequired
class PlatformEnum(Enum):
    QB = "" # 全部
    DM = "DM" # 大麦
    MY = "MY" # 猫眼


class City(BaseModel):
    city_id: int
    name: str
    platform: PlatformEnum # 这个类型是枚举

class ApiResponseData(BaseModel):
    platform: PlatformEnum
    api: str
    # data: dict | list # python 3.10 以上支持
    data: Union[dict, list, None, str]
    ret: list[str]
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
    user_id: str = Field(None, description="可选参数") # 用户id 可以不用传递
    show_name: str # 演唱会名字
    venue_city_name: str # 演唱会城市
    venue_name: str # 演唱会场馆
    ticket_perform: List[TicketPerform] # 场次
    time: Optional[str] = Field(None, description="可选参数") # 将 time 标记为可选
    wx_token: str = Field(None, description="可选参数") # 微信token (发送监控通知) 可以不用传递
    deadline: str # 监控时间持续时间
    cover_url: str # 封面
    @field_validator('wx_token')
    def validate_wx_token(cls, v):
        if not v:
            raise ValueError("wx_token 不能为空")
        return v

# 写入db_config.json中_m_h5_tk、_m_h5_tk_enc、cookie2、sgcookie
class WriteDbConfigParams(BaseModel):
    m_h5_tk: str
    m_h5_tk_enc: str
    cookie2: str
    sgcookie: str
    appKey: Optional[str] = Field('12574478', description="可选参数")
    t: Optional[int] = Field(1744705294598, description="可选参数")
