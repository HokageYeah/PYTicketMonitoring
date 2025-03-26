
# 微信小程序登录
from fastapi import APIRouter
from src.server.schemas.wxMiniLoginSchema import \
    WxMiniLoginParams, \
    WxPlatformEnum, \
    WxMiniApiResponse, \
    WxMiniGetUserSubscribeMonitorListParams, \
    WxMiniDeleteUserSubscribeMonitorParams
from fastapi import Query, Body, Depends
from src.server.api.endpoints.validate_params import \
    validate_wx_mini_login_params, validate_create_user_params, \
    validate_wx_mini_send_subscribe_message_params, \
    validate_wx_mini_get_user_subscribe_monitor_list_params, \
    validate_wx_mini_delete_user_subscribe_monitor_params
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
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List
from src.server.core.confing import settings

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
# 微信发送回流票的订阅消息 subscribe-wx-template
@wx_router.post('/wx/mini.send.subscribe.message', response_model=WxMiniApiResponse)
async def wx_mini_send_subscribe_message(
    platform: str = Query(WxPlatformEnum.WX_MINI.value, description="平台名称"),
    params: dict = Body(...),
    user: User = Depends(get_current_user)
):
    print('wx_mini_send_subscribe_message---platform---------', platform)
    print('wx_mini_send_subscribe_message---params.platform---------', WxPlatformEnum.WX_MINI.value)
    if platform == WxPlatformEnum.WX_MINI.value:
        send_subscribe_message_data = wx_service.wx_mini_send_subscribe_message(params)
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
    params: WxMiniGetUserSubscribeMonitorListParams = Depends(validate_wx_mini_get_user_subscribe_monitor_list_params),
    user: User = Depends(get_current_user)
):
    if platform == WxPlatformEnum.WX_MINI.value:
        return user_service.get_user_subscribe_monitor_list(user, params)
    return None
# 删除当前用户的正在订阅的监控
@wx_router.post('/wx/mini.delete.user.subscribe.monitor', response_model=WxMiniApiResponse)
async def delete_user_subscribe_monitor(
    platform: str = Query(WxPlatformEnum.WX_MINI.value, description="平台名称"),
    params: WxMiniDeleteUserSubscribeMonitorParams = Depends(validate_wx_mini_delete_user_subscribe_monitor_params),
    user: User = Depends(get_current_user)
):
    if platform == WxPlatformEnum.WX_MINI.value:
        return user_service.delete_user_subscribe_monitor(user, params)
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


conf = ConnectionConfig(
    MAIL_USERNAME = settings.QQ_MAIL_USERNAME,  # 必须与登录邮箱一致
    MAIL_PASSWORD = settings.QQ_MAIL_PASSWORD,    # 授权码(非邮箱密码)
    MAIL_FROM = settings.QQ_MAIL_FROM,       # 必须与MAIL_USERNAME一致
    MAIL_PORT = settings.QQ_MAIL_PORT,                      # SSL端口
    MAIL_SERVER = settings.QQ_MAIL_SERVER,
    MAIL_FROM_NAME = "测试",
    MAIL_STARTTLS = False,                # 关闭STARTTLS
    MAIL_SSL_TLS = True,                  # 启用SSL/TLS
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

class EmailSchema(BaseModel):
    email: List[EmailStr]

@wx_router.post("/wx/mini.test.email")
async def simple_send(email: EmailSchema) -> JSONResponse:
    html = """<p>你好，这是一封测试邮件</p> """
    message = MessageSchema(
        subject="服务通知",
        recipients=email.dict().get("email"),
        body=html,
        subtype=MessageType.html)
    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        print('email has been sent')
    except Exception as e:
        if "Malformed SMTP response line" in str(e):
            print(f"邮件已发送，但出现已知错误: {str(e)}")
        else:
            # 其他未知错误则抛出
            print(f"邮件发送错误: {str(e)}")
            return JSONResponse(status_code=500, content={"message": f"邮件发送失败: {str(e)}"})
    return JSONResponse(status_code=200, content={"message": "邮件已发送"})
