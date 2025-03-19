
# 微信小程序登录
from fastapi import APIRouter
from src.server.schemas.wxMiniLoginSchema import WxMiniLoginParams, WxPlatformEnum, WxMiniApiResponse
from fastapi import Query, Body, Depends
from src.server.api.endpoints.validate_params import validate_wx_mini_login_params, validate_create_user_params, validate_wx_mini_send_subscribe_message_params
from src.server.services.wx import WxService
from src.sql.models.user import User
from sqlalchemy.orm import Session
from src.sql.sqlalchemy_db import get_sqlalchemy_db
from src.server.schemas.wxMiniLoginSchema import CreateUserParams
from src.server.services.userService import UserService
from src.sql.models.user import User
from src.server.schemas.wxMiniLoginSchema import WxMiniSendSubscribeMessageParams
from src.server.middleware.jwt_auth import get_current_user, require_role
from src.server.schemas.wxMiniLoginSchema import WxMiniGetAccessTokenParams
from src.server.api.endpoints.validate_params import validate_wx_mini_get_access_token_params
wx_router = APIRouter()
wx_service = WxService()
user_service = UserService()

# 微信code登录 获取session_key 和 openid
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
        return login_data
    return None
# 调用微信API凭证接口，获取access_token
@wx_router.get('/wx/mini.get.access.token', response_model=WxMiniApiResponse)
async def wx_mini_get_access_token(
    platform: str = Query(WxPlatformEnum.WX_MINI.value, description="平台名称"),
):
    print('wx_mini_get_access_token---platform---------', platform)
    print('wx_mini_get_access_token---params.platform---------', WxPlatformEnum.WX_MINI.value)
    if platform == WxPlatformEnum.WX_MINI.value:
        access_token_data = wx_service.wx_mini_get_access_token()
        return access_token_data
    return None

# 微信订阅消息模板存储
@wx_router.post('/wx/mini.save.subscribe.template', response_model=WxMiniApiResponse)
async def wx_mini_save_subscribe_template(
    platform: str = Query(WxPlatformEnum.WX_MINI.value, description="平台名称"),
    params: WxMiniSendSubscribeMessageParams = Depends(validate_wx_mini_send_subscribe_message_params),
    user: User = Depends(get_current_user)
):
    if platform == WxPlatformEnum.WX_MINI.value:
        res = wx_service.wx_mini_save_subscribe_template(params, user)
        return res
    return None
# 微信发送订阅消息 subscribe-wx-template
@wx_router.post('/wx/mini.send.subscribe.message', response_model=WxMiniApiResponse)
async def wx_mini_send_subscribe_message(
    platform: str = Query(WxPlatformEnum.WX_MINI.value, description="平台名称"),
    user: User = Depends(get_current_user)
):
    print('wx_mini_send_subscribe_message---platform---------', platform)
    print('wx_mini_send_subscribe_message---params.platform---------', WxPlatformEnum.WX_MINI.value)
    if platform == WxPlatformEnum.WX_MINI.value:
        send_subscribe_message_data = wx_service.wx_mini_send_subscribe_message(user)
        return send_subscribe_message_data
    return None

# 创建订阅消息模板
@wx_router.get("/wx/mini.create.subscribe.template", response_model=WxMiniApiResponse)
def create_subscribe_template(miniprogram_state: str):
    return user_service.create_subscribe_template(miniprogram_state)

# 获取当前用户的订阅监控列表
@wx_router.post('/wx/mini.get.user.subscribe.monitor.list', response_model=WxMiniApiResponse)
async def get_user_subscribe_monitor_list(
    platform: str = Query(WxPlatformEnum.WX_MINI.value, description="平台名称"),
    user: User = Depends(get_current_user)
):
    if platform.value == WxPlatformEnum.WX_MINI.value:
        return wx_service.get_user_subscribe_monitor_list(user)
    return None

@wx_router.get("/wx/mini.get.users")
def get_users(db: Session = Depends(get_sqlalchemy_db)):
    print('db---------', db)
    return db.query(User).all()

@wx_router.post("/wx/mini.create.user")
def create_user(db: Session = Depends(get_sqlalchemy_db), params: CreateUserParams = Depends(validate_create_user_params)):
    user = User(username=params.username, password=params.password, openid=params.openid)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 需要JWT认证的路由（例子）
# Depends(get_current_user) 是 FastAPI 的依赖注入模式。这表示这个路由函数依赖于 get_current_user 函数的返回结果。
@wx_router.post("/wx/mini.profile.detail")
async def get_user_profile(data: dict, current_user: User = Depends(get_current_user)):
    """获取当前用户的个人资料"""
    print('get_user_profile---current_user-----data---', data)
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "openid": current_user.openid,
        "user_avatar_pic": current_user.user_avatar_pic,
        "user_address": current_user.user_address,
        "user_role": current_user.user_role,
        "status": current_user.status
    }

# 需要管理员角色的路由
@wx_router.post("/wx/mini.admin.users")
async def get_all_users(
    current_user: User = Depends(require_role(WxPlatformEnum.WX_MINI.value, '/wx/mini.admin.users', 2)),  # 假设2是管理员角色
    db: Session = Depends(get_sqlalchemy_db)
):
    """获取所有用户（仅管理员）"""
    users = db.query(User).all()
    return users