
# 微信小程序登录
from fastapi import APIRouter
from src.server.schemas.wxMiniLoginSchema import WxMiniLoginParams, WxPlatformEnum, WxMiniApiResponse
from fastapi import Query, Body, Depends
from src.server.api.endpoints.validate_params import validate_wx_mini_login_params, validate_create_user_params
from src.server.services.wx import WxService
from src.sql.models.user import User
from sqlalchemy.orm import Session
from src.sql.sqlalchemy_db import get_sqlalchemy_db
from src.server.schemas.wxMiniLoginSchema import CreateUserParams
from src.server.services.userService import UserService
from src.sql.models.user import User


wx_router = APIRouter()
wx_service = WxService()
user_service = UserService()

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


