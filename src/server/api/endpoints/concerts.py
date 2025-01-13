from fastapi import APIRouter, Body, Query, Depends
import logging
import json
from src.server.schemas.concert import RecordMonitorParams
from src.server.schemas import PlatformEnum, ApiResponseData
from src.server.services.damai import DamaiService
from typing import Optional
from src.server.api.endpoints.validate_params import validate_record_monitor_params
logger = logging.getLogger(__name__)
router = APIRouter()
damai = DamaiService()
# 列一个枚举表示不同的平台：比如大麦、猫眼等
# class Platform(Enum):
#     DM = "大麦"
#     MM = "猫眼"

# 获取网页平台下的演唱会搜索所有数据
@router.get('/web/search.concert.by.platform', response_model=ApiResponseData)
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
@router.get('/web/login.qrcode.by.platform', response_model=ApiResponseData)
async def get_login_qrcode(platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")):
    if platform == PlatformEnum.DM:
        return damai.get_generate_code_web()
    return None

# 调用网站验证查询是否扫码登录
@router.post('/web/login.query.by.platform', response_model=ApiResponseData)
async def post_login_query(platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")):
    if platform == PlatformEnum.DM:
        json_data = damai.post_login_query_web()
        # # 判断是否登录成功，登录成功直接调用登录 get_dologin接口
        # print('json_data---------', json_data)
        # msg = json_data.get('ret')[0]
        # if 'SUCCESS' in msg:
        #     res_data = damai.get_dologin_web()
        #     print('登录成功------', res_data)
        #     return res_data
        return json_data
    return None
# 扫码成功后调用登录
@router.get('/web/dologin.by.platform', response_model=ApiResponseData)
async def get_dologin(platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")):
    if platform == PlatformEnum.DM:
        return damai.get_dologin_web()
    return None
# 获取大麦网用户信息(主要获取_m_h5_tk 和 _m_h5_tk_enc)
@router.get('/web/userinfo.by.platform', response_model=ApiResponseData)
async def get_userinfo(platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称")):
    if platform == PlatformEnum.DM:
        return damai.get_user_info_web()
    return None
# 获取单个演唱会详情信息（鉴权、需要登录）
@router.get('/web/get.item.detail.by.platform', response_model=ApiResponseData)
async def get_concert_detail(
    platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称"),
    show_id: Optional[str] = Query(None, description="演唱会ID"), # show_id演唱会id必须有
    ):
    if platform == PlatformEnum.DM:
        return damai.get_item_detail_web(show_id)
    return None
# 检测当前场次是否有坐次（是否又票）
@router.get('/web/check.ticket.by.platform', response_model=ApiResponseData)
async def get_check_ticket(
    platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称"),
    show_id: str = Query('', description="演唱会ID"),
    session_id: str = Query('', description="场次ID")
    ):
    if platform == PlatformEnum.DM:
        return damai.check_ticket_web(show_id, session_id)
    return None
# 记录用户需要监控的演唱会、场次、座次、时间、微信token、 监控时间
@router.post('/web/record.monitor.by.platform', response_model=ApiResponseData)
async def post_record_monitor(
    platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称"),
    params: RecordMonitorParams = Depends(validate_record_monitor_params)
    ):
    if platform == PlatformEnum.DM:
        print('params---------', params)
        return damai.post_record_monitor_web(params)
    return None
# 调用票务监控开始 测试需要更改
@router.post('/web/start.monitor.by.platform')
async def post_start_monitor(
    platform: PlatformEnum = Query(PlatformEnum.DM, description="平台名称"),
    show_id: str = Query('', description="演出ID"),
    show_name: str = Query('', description="演出名称"),
    deadline: str = Query('', description="轮训截止时间") # 轮训截止时间
    ):
    if platform == PlatformEnum.DM:
        return damai.post_start_monitor_web(show_id, show_name, deadline)
    return None