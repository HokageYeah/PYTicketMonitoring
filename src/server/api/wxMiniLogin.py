
# 微信小程序登录
from fastapi import APIRouter
from src.server.schemas.wxMiniLoginSchema import WxMiniLoginParams, WxPlatformEnum, WxMiniApiResponse
from fastapi import Query, Body, Depends
from src.server.api.endpoints.validate_params import validate_wx_mini_login_params
wx_router = APIRouter()

@wx_router.post('/wx/mini.login.by.code', response_model=WxMiniApiResponse)
async def wx_mini_login(
    platform: WxPlatformEnum = Query(WxPlatformEnum.WX_MINI, description="平台名称"),
    params: WxMiniLoginParams = Depends(validate_wx_mini_login_params)
):
    print('platform---------', platform)
    print('params---------', params)
    if platform.value == WxPlatformEnum.WX_MINI.value:
        return WxMiniApiResponse(platform=platform.value, ret='123', data=params.code)
        # return {
        #     'platform': platform.value,
        #     'ret': '123',
        #     'data': params.code
        # }
    return None


