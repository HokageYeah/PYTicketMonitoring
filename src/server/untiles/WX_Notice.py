import requests
from src.decorators.Res_Handler_Decorator import wx_mini_response_handler
# 微信通知（测试公众号）
class WX_Notice:
    def __init__(self):
        # 公众号appid
        self.public_app_id = 'wxa88c9b80089f3171'
        # 公众号appsecret
        self.public_app_secret = '4f5f6a6e5319b2a0ff1476c7c8062cc0'
        # 获取 access_token 的 URL
        self.public_access_token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.public_app_id}&secret={self.public_app_secret}'
    @wx_mini_response_handler(api_path='https://api.weixin.qq.com/cgi-bin/token', success_msg='获取access_token成功', error_msg='获取access_token调用失败', error_email=True)
    def get_access_token(self):
        try:
            # 获取 access_token 的 URL
            access_token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.public_app_id}&secret={self.public_app_secret}'
            print('WX_Notice---get_access_token---access_token_url---', access_token_url)
            # 发送请求获取 access_token
            response = requests.get(access_token_url)
            access_token_data = response.json()
            print('WX_Notice---get_access_token---response---', response.json().get('access_token'))
                 # 判断小程序接口请求是否报错
            if 'errcode' in access_token_data and access_token_data.get('errcode') != 0:
                errcode = access_token_data.get('errcode')
                errmsg = access_token_data.get('errmsg')
                print('wx_notice---get_access_token---api---------', errcode, errmsg)
                return {
                    'ret': ["ERROR::"+errmsg, "ERRORCODE::"+str(errcode)],
                }
            return response.json().get('access_token','')
        except Exception as e:
            print('WX_Notice---get_access_token---error---', e)
            return ''
    def send_public_notice(self, access_token, content, user_wx_code, template_id):
        # 发送公众号通知
        send_notice_url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
        # 发送请求获取 access_token'
        print('WX_Notice---send_public_notice---send_notice_url---', send_notice_url)
        try:
            response = requests.post(url=send_notice_url, json={
                'touser': user_wx_code,
                'template_id': template_id,
                'data': content
            }, headers={
                'Content-Type': 'application/json'
            }, timeout=10)
            print('WX_Notice---send_public_notice---response---', response.json())
            return True
        except Exception as e:
            print('WX_Notice---send_public_notice---error---', e)
            return False
    @wx_mini_response_handler(api_path='https://api.weixin.qq.com/cgi-bin/user/get', success_msg='获取用户微信openid列表成功', error_msg='获取用户微信openid列表调用失败', error_email=True)
    def get_user_wx_openid_list(self, access_token:str, next_openid:str = '') -> dict:
        # 获取用户微信openid列表
        get_user_wx_openid_list_url = f'https://api.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&next_openid={next_openid}'
        response = requests.get(get_user_wx_openid_list_url)
        response_data = response.json()
        # 判断小程序接口请求是否报错
        if 'errcode' in response_data and response_data.get('errcode') != 0:
            errcode = response_data.get('errcode')
            errmsg = response_data.get('errmsg')
            print('wx_notice---get_user_wx_openid_list---api---------', errcode, errmsg)
            return {
                'ret': ["ERROR::"+errmsg, "ERRORCODE::"+str(errcode)],
            }
        print('WX_Notice---get_user_wx_openid_list---response---', response_data)
        return response_data


