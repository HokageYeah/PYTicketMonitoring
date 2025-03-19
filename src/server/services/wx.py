import requests
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
from src.sql.models.user import User
from src.server.services.userService import UserService
import time
from src.server.schemas.wxMiniLoginSchema import WxMiniSendSubscribeMessageParams
from src.server.untiles.custom_exceptions import SaveSubscribeTemplateException, SendSubscribeMsgUserException
user_service = UserService()

class WxService:
    def __init__(self):
        self.BASE_URL = "https://api.weixin.qq.com"
        self.data = {
            "appid": "wxcce30ba44a2065a5",
            "secret": "c49f74d704577e5842e84ab43ff3333d",
        }
        # 初始化数据
        self.access_token = ''
        self.expires_in = 0
        self.expires_time = time.time() + self.expires_in
        # 调用获取access_token
        self.wx_mini_get_access_token()
        # 调用access_token 记录次数，超过三次返回错误
        self.access_token_count = 0
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
    # 检查access_token是否过期
    def is_access_token_expired(self):
        return time.time() >= self.expires_time
        # 微信发送订阅消息
    def wx_mini_send_subscribe_message(self, user: User):
        # 调用access_token 记录次数，超过三次返回错误
        self.access_token_count += 1
        if self.access_token_count > 3:
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["ERROR::获取access_token超过最大次数"],
                'data': {},
                'v': 1,
                'api': 'wx.mini.send.subscribe.message'
            }
        if self.is_access_token_expired():
            print('WxService---wx_mini_send_subscribe_message---access_token过期-----')
            self.wx_mini_get_access_token()
            # 更新access_token后，重新调用
            return self.wx_mini_send_subscribe_message(user)
        else:
            try:
                print('WxService---wx_mini_send_subscribe_message---access_token未过期-----')
                # 调用发送订阅消息
                self.access_token_count = 0
                url = f"{self.BASE_URL}/cgi-bin/message/subscribe/send?access_token={self.access_token}"
                template_info = user_service.get_user_subscribe_template(user)
                params = {
                    "touser": user.openid,
                    "template_id": template_info['template_id'],
                    "page": template_info['page'],
                    "data": {
                        "thing1": {"value": "王瑛捷郑州演唱会"},
                        "time2": {"value": "2023-10-01 10:00"},
                        "thing3": {"value": "郑州｜ 郑州奥体中心"},
                        "thing6": {"value": "2025-03-12 10:00 场次"},
                        "thing4": {"value": "该场次的票已经回流，请及时购票"},
                    },
                }
                response = requests.post(url, json=params)
                print('WxService---wx_mini_send_subscribe_message---response-----', response)
                return {
                    'platform': WxPlatformEnum.WX_MINI.value,
                    'ret': ["SUCCESS::发送订阅消息成功"],
                    'data': response.json(),
                    'v': 1,
                    'api': '/wx/mini.send.subscribe.message'
                }
            except SendSubscribeMsgUserException as e:
                return e.to_response()
    # 微信订阅消息模板存储
    def wx_mini_save_subscribe_template(self, params, user):
        try:
            res = user_service.save_user_subscribe_template(params, user)
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["SUCCESS::订阅消息模板存储成功"],
                'data': res,
                'v': 1,
                'api': 'wx.mini.save.subscribe.template'
            }
        # 捕获用户不存在异常，此处走不到这里，因为接口已经统一鉴权了
        except SaveSubscribeTemplateException as e:
            return e.to_response()
        except Exception as e:
            # 捕获所有其他异常
            print('WxService---wx_mini_save_subscribe_template---error-----', e)
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["ERROR::订阅消息模板存储失败"],
                'data': {},
                'v': 1,
                'api': 'wx.mini.save.subscribe.template'
            }
    # 获取access_token
    def wx_mini_get_access_token(self):
        try:
            url = f"{self.BASE_URL}/cgi-bin/token"
            params = {
                **self.data,
                "grant_type": "client_credential"
            }
            response = requests.get(url, params=params)
            access_token_data = response.json() 
            print('WxService---wx_mini_get_access_token---access_token_data-----', access_token_data)
            self.access_token = access_token_data.get('access_token')  
            self.expires_in = access_token_data.get('expires_in')
            # self.expires_in = 0
            self.expires_time = time.time() + self.expires_in
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["SUCCESS::调用成功"],
                'data': access_token_data,
                'v': 1,
                'api': '/wx/mini.get.access.token'
            }
        except Exception as e:
            print('WxService---wx_mini_get_access_token---error-----', e)
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["ERROR::获取access_token失败"],
                'data': {},
                'v': 1,
                'api': '/wx/mini.get.access.token'
            }
