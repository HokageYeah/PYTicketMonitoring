
# 微信小程序登录
from fastapi import APIRouter
from src.server.schemas.wxMiniLoginSchema import WxMiniLoginParams, WxPlatformEnum, WxMiniApiResponse
from fastapi import Query, Body, Depends
from src.server.api.endpoints.validate_params import validate_wx_mini_login_params
from src.server.services.wx import WxService
from src.sql import SqlConnectDb

wx_router = APIRouter()
wx_service = WxService()

@wx_router.post('/wx/mini.login.by.code', response_model=WxMiniApiResponse)
async def wx_mini_login(
    platform: str = Query(WxPlatformEnum.WX_MINI.value, description="平台名称"),
    params: WxMiniLoginParams = Depends(validate_wx_mini_login_params)
):
    print('params---------', params)
    print('platform---------', platform)
    print('params.platform---------', WxPlatformEnum.WX_MINI.value)
    if platform == WxPlatformEnum.WX_MINI.value:
        login_data = wx_service.wx_mini_login_code2Session(params.code)
        # 将登录数据写入到数据库
        sql_connect_db = SqlConnectDb()
        sql_connect_db.connect()
        # sql_connect_db.insert_wx_mini_login_data(login_data)
        return login_data
    return None


