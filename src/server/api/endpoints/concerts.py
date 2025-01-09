from fastapi import APIRouter, Query
import logging
import json
from src.server.schemas import PlatformEnum, SearchConcert
from src.server.services.damai import DamaiService

logger = logging.getLogger(__name__)
router = APIRouter()
damai = DamaiService()
# 列一个枚举表示不同的平台：比如大麦、猫眼等
# class Platform(Enum):
#     DM = "大麦"
#     MM = "猫眼"

# 获取网页平台下的演唱会搜索所有数据
@router.get('/web/get-search-concert/by-platform', response_model=SearchConcert)
async def get_search_concerts(
    cty: str = Query('北京', description="城市名称"),
    keyword: str = Query('', description="搜索关键字"),
    ctl: str = Query('演唱会', description="搜索类型"),
    platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")
    ):
    print('platform---------', platform)
    if platform == PlatformEnum.DM:
        return damai.search_concert_web(cty, keyword, ctl)
    return None

# 调用网站登录生成二维码接口，返回二维码图片
@router.get('/web/get-login-qrcode/by-platform')
async def get_login_qrcode(platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")):
    if platform == PlatformEnum.DM:
        base64_data = damai.get_generate_code_web()
        if base64_data:
            return base64_data
    return None

# 调用网站验证查询是否扫码登录
@router.get('/web/get-login-query/by-platform')
async def get_login_query(platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")):
    if platform == PlatformEnum.DM:
        json_data = damai.post_login_query_web()
        print('json_data---------', json_data)
        return json_data
    return None