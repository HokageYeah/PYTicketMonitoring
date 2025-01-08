from fastapi import APIRouter, Query
import logging
from src.server.schemas import Concert, PlatformEnum, City

logger = logging.getLogger(__name__)
router = APIRouter()

# 列一个枚举表示不同的平台：比如大麦、猫眼等
# class Platform(Enum):
#     DM = "大麦"
#     MM = "猫眼"

# 获取所有地市 参数不是必填的
@router.get('/get-all-city/by-platforms', response_model=City)
async def get_concerts_by_city(
    city: str = Query('北京', description="城市名称"),
    platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")
    ):
    return {"city_id": 1, "name": "北京", "platform": platform}

# @router.post('/get-all-city/by-platforms2')
# async def get_concerts_by_city2(body: str):
#     return {"message": "Hello, World!"}
