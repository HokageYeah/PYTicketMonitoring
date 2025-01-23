import requests
# 微信通知（测试公众号）
class WX_Notice:
    def __init__(self):
        # 公众号appid
        self.public_app_id = 'wxa88c9b80089f3171'
        # 公众号appsecret
        self.public_app_secret = '4f5f6a6e5319b2a0ff1476c7c8062cc0'
        # 获取 access_token 的 URL
        self.public_access_token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.public_app_id}&secret={self.public_app_secret}'
    def get_access_token(self):
        # 获取 access_token 的 URL
        access_token_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.public_app_id}&secret={self.public_app_secret}'
        # 发送请求获取 access_token
        response = requests.get(access_token_url)
        print('WX_Notice---get_access_token---response---', response.json().get('access_token'))
        return response.json().get('access_token','')
    def send_public_notice(self, access_token, content, user_wx_code, template_id):
        # 发送公众号通知
        send_notice_url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}'
        # 发送请求获取 access_token
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
    def get_user_wx_openid_list(self, access_token:str, next_openid:str = '') -> dict:
        # 获取用户微信openid列表
        get_user_wx_openid_list_url = f'https://api.weixin.qq.com/cgi-bin/user/get?access_token={access_token}&next_openid={next_openid}'
        response = requests.get(get_user_wx_openid_list_url)
        print('WX_Notice---get_user_wx_openid_list---response---', response.json())
        return response.json()


