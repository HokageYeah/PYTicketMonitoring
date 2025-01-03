
import json
import re
import requests

login_id = 18838280615
class Login_DM:
    def __init__(self):
        # mini_login.htm接口地址
        self.loginFormData = ''
        self._csrf_token = ''
        self.umidToken = ''
        self.hsiz = ''
        self.mini_data = self.get_mini_login_url()
        self.post_check_login()
        print('mini_data----', self._csrf_token, self.umidToken, self.hsiz)
    def get_mini_login_url(self):
       url = "https://ipassport.damai.cn/mini_login.htm?lang=zh_cn&appName=damai&appEntrance=default&styleType=vertical&bizParams=&notLoadSsoView=true&notKeepLogin=false&isMobile=false&showSnsLogin=false&regUrl=https%3A%2F%2Fpassport.damai.cn%2Fregister&plainReturnUrl=https%3A%2F%2Fpassport.damai.cn%2Flogin&returnUrl=https%3A%2F%2Fpassport.damai.cn%2Fdologin.htm%3FredirectUrl%3Dhttps%253A%252F%252Fwww.damai.cn%26platform%3D106002&rnd=0.08763263121488252"
       response = requests.get(
           url=url,
           headers={
               'Referer': 'https://passport.damai.cn/',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
           },
       )
       #根据正则获取到window.viewData 中包裹的数据
       view_data = re.search(r'window\.viewData\s*=\s*({.*})', response.text)
       if view_data:
           view_data = json.loads(view_data.group(1))
           self.loginFormData = view_data.get('loginFormData', {})
           self._csrf_token = self.loginFormData.get('_csrf_token', '')
           self.umidToken = self.loginFormData.get('umidToken', '')
           self.hsiz = self.loginFormData.get('hsiz', '')
           return view_data
       return {}
    # 生成验证码
    def get_generate_code(self):
        pass
    # 下面的方法是滑块验证、此逻辑没有走通
    def post_check_login(self):
        url = 'https://ipassport.damai.cn/newlogin/account/check.do?appName=damai&fromSite=18'
        data = {
            "appName": "damai",
            "fromSite": 18,
            "loginId": "18838280615",
            "_csrf_token": self._csrf_token,
            "umidToken": self.umidToken,
            "hsiz": self.hsiz,
            }
        try:
            response = requests.post(
                url=url,
                data=data,
            headers={
                'Referer': 'https://passport.damai.cn/',
                'origin': 'https://passport.damai.cn',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            },
        )
            print('response----', response.text)
        except Exception as e:
            print('post_check_login----error----', e)
if __name__ == '__main__':
    login_dm = Login_DM()
    print('login_dm----', login_dm)