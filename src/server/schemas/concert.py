from pydantic import BaseModel
from typing import List
from enum import Enum

class PlatformEnum(Enum):
    DM = "DM" # 大麦
    MY = "MY" # 猫眼

class City(BaseModel):
    city_id: int
    name: str
    platform: PlatformEnum # 这个类型是枚举

class Concert(BaseModel):
    cities: List[City]