import requests
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
from src.sql.models.user import User
from src.server.services.userService import UserService

user_service = UserService()

class WxService:
    def __init__(self):
        self.BASE_URL = "https://api.weixin.qq.com"
        self.data = {
            "appid": "wxcce30ba44a2065a5",
            "secret": "c49f74d704577e5842e84ab43ff3333d",
        }
    # 小程序登录
    def wx_mini_login_code2Session(self, code):
        try:
            url = f"{self.BASE_URL}/sns/jscode2session"
            params = {
                **self.data,
                "js_code": code,
                "grant_type": "authorization_code"
            }
            print('WxService---wx_mini_login_code2Session---params-----', params)
            response = requests.get(url, params=params)
            login_data = response.json()
            print('WxService---wx_mini_login_code2Session---response-----', login_data)
            session_key = login_data['session_key']
            openid = login_data['openid']
            user = User(session_key=session_key, openid=openid)
            user = user_service.create_user(user)
            tokenStr = user_service.generate_token(user)
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["SUCCESS::调用成功"],
                'data': {
                    'token': "Bearer " + tokenStr,
                    'user_id': user.user_id,
                    # 'openid': user.openid,
                    'username': user.username,
                    # 'password': user.password,
                    'status': user.status,
                    'create_time': user.create_time,
                    'update_time': user.update_time,
                },
                'v': 1,
                'api': 'wx.mini.login.by.code'
            }
        except Exception as e:
            print('WxService---wx_mini_login_code2Session---error-----', e)
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["ERROR::微信登录调用失败"],
                'data': {},
                'v': 1,
                'api': 'wx.mini.login.by.code'
            }
