
from datetime import datetime
from hashlib import md5
import json
import os
from pathlib import Path
import re
import sys
import time
import requests
import qrcode
login_id = 18838280615
class Login_DM:
    def __init__(self):
        # mini_login.htm接口地址
        self.loginFormData = ''
        self._csrf_token = ''
        self.umidToken = ''
        self.hsiz = ''
        self.t = ''
        self.ck = ''
        self.pageTraceId = ''
        self._m_h5_tk = ''
        self._m_h5_tk_enc = ''
        self.cookie2 = ''
        self.sgcookie = ''
        self.st = ''
        self.h5token = ''
        self.loginkey = ''
        self.user_id = ''
        self._tb_token_ = ''
        self.appKey = '12574478'
        self.mini_data = self.get_mini_login_url()
        # # self.post_check_login() 此逻辑没有走通
        # # 生成二维码
        # self.get_generate_code()
        # # 验证查询是否扫码登录
        # self.post_query_login()
        # # 调用登录
        # self.get_dologin()
        # # 验证通过后：获取_m_h5_tk 和 _m_h5_tk_enc
        # self.get_m_h5_tk()
        # # 拿到大麦登录信息后将信息写入到config.json中
        # self.write_dm_config_json()
        # # 调用票务监控开始
        # self.start_monitor()
        # print('mini_data----', self._csrf_token, self.umidToken, self.hsiz)
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
       print('get_mini_login_url----response', response)
       # 从响应头获取pageTraceId 数据f
       self.pageTraceId = response.headers.get('eagleeye-traceid', '')
       # 获取_tb_token_从cookies中获取
       self._tb_token_ = response.cookies.get('_tb_token_', '')
       print('get_mini_login_url----_tb_token_----', self._tb_token_)
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
        bx_ua = ''
        url = f'https://ipassport.damai.cn/newlogin/qrcode/generate.do?appName=damai&fromSite=18&appName=damai&appEntrance=damai&_csrf_token={self._csrf_token}&umidToken={self.umidToken}&hsiz={self.hsiz}&bizParams=renderRefer%3Dhttps%253A%252F%252Fpassport.damai.cn%252F&mainPage=false&isMobile=false&lang=zh_CN&returnUrl=https:%2F%2Fpassport.damai.cn%2Fdologin.htm%3FredirectUrl%3Dhttps%253A%252F%252Fwww.damai.cn%26platform%3D106002&fromSite=18&umidTag=SERVER&bx-ua={bx_ua}&bx-umidtoken=T2gAkU3yFuVBJv8dESfbSoVMOXs7jU3HoShZPJWjOBDaWVJEUvr7S1kYDT1b6p8nfAg%3D'
        response = requests.get(
            url=url,
            headers={
                'Referer': 'https://passport.damai.cn/',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            },
        )
        print('get_generate_code----response----', response.text)
        result = response.json()
        codeContent = result.get('content',{}).get('data', {}).get('codeContent', '')
        self.t = result.get('content',{}).get('data', {}).get('t', '')
        self.ck = result.get('content',{}).get('data', {}).get('ck', '')
        # 生成一个二维码
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(codeContent)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # 设置图片二维码存放的路径
        save_img_path = Path(__file__).resolve().parent / 'QRCode_DM.png'
        img.save(save_img_path)
        img.show()
    # 验证查询是否扫码登录
    def post_query_login(self):
        url = 'https://ipassport.damai.cn/newlogin/qrcode/query.do?appName=damai&fromSite=18'
        data = {
            't': self.t,
            'ck': self.ck,
            '_csrf_token': self._csrf_token,
            'umidToken': self.umidToken,    
            'hsiz': self.hsiz,
            'appName': 'damai',
            'appEntrance': 'damai',
            'pageTraceId': self.pageTraceId,
        }
        try:
            start_time = time.time()
            res_all_data = {}
            # 轮询查询是否登录成功
            while True:
                response = requests.post(
                    url=url,
                    data=data,
                    headers={
                        'Referer': 'https://passport.damai.cn/',
                        'origin': 'https://ipassport.damai.cn',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                    },
                )
                print('post_query_login----response----', response.text)
                res_data = response.json().get('content',{}).get('data',{})
                if res_data.get('qrCodeStatus', '') == 'CONFIRMED':
                    self.cookie2 = res_data.get('cookie2', '')
                    self.sgcookie = response.cookies.get('sgcookie', '')
                    self.st = res_data.get('st', '')
                    print('扫码登录成功----headers', response.headers)
                    print('扫码登录成功----sgcookie', self.sgcookie)
                    print('扫码登录成功----cookie2', self.cookie2)
                    print('扫码登录成功----st', self.st)
                    res_all_data['status'] = 'success'
                    res_all_data['msg'] = '扫码登录成功'
                    break
                # 轮训最长30秒
                if time.time() - start_time > 10:
                    print('轮训超时')
                    res_all_data['status'] = 'error'
                    res_all_data['msg'] = '轮训超时'
                    break
                time.sleep(2)
            print('post_query_login----res_all_data----', res_all_data)
            return res_all_data
        except Exception as e:
            print('post_query_login----error----', e)
            res_all_data['status'] = 'error'
            res_all_data['msg'] = str(e)
            return res_all_data
    # 调用登录
    def get_dologin(self):
        url = f'https://passport.damai.cn/dologin.htm?st={self.st}&redirectUrl=https%253A%252F%252Fwww.damai.cn%252F&platform=106002'
        response = requests.get(
            url=url,
            headers={
                'Referer': 'https://passport.damai.cn/',
                'origin': 'https://passport.damai.cn',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            },
            # allow_redirects=False, # 禁止重定向
        )
        cookies = response.cookies
        # 方法1：转换为字典
        cookies_dict = requests.utils.dict_from_cookiejar(cookies)
        print("get_dologin----Cookies字典:", cookies_dict)
        print("get_dologin----response:", response)
        print('get_dologin----response.cookies----', response.cookies)
        # print('get_dologin----response.text----', response.text)
        self.h5token = cookies.get('h5token', '')
        self.loginkey = cookies.get('loginkey', '')
        self.user_id = cookies.get('user_id', '')
        print('get_dologin----h5token----', self.h5token)
        print('get_dologin----loginkey----', self.loginkey)
        print('get_dologin----user_id----', self.user_id)
        # print('get_dologin----response----', response.text)
    def write_dm_config_json(self):
        # 获取当前文件的绝对路径
        current_dir = Path(__file__).resolve().parent.parent
        # 获取config.json文件的路径
        config_path =  current_dir / 'monitor/config/config.json'
        # 读取config.json文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print('write_dm_config_json----config----', config)
            config.get('monitor_list',[])[0]['_m_h5_tk'] = self._m_h5_tk
            config.get('monitor_list',[])[0]['_m_h5_tk_enc'] = self._m_h5_tk_enc
            config.get('monitor_list',[])[0]['cookie2'] = self.cookie2
            config.get('monitor_list',[])[0]['sgcookie'] = self.sgcookie
            config.get('monitor_list',[])[0]['appKey'] = self.appKey
            config.get('monitor_list',[])[0]['t'] = self.t
            # 将config.json文件写入到config.json中
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False)
    # 调用票务监控开始
    def start_monitor(self):
        from src.monitor.start import Runner
        runner = Runner()
        runner.start()
    @staticmethod
    def get_sign(c: str, t: str, data: dict):
        plain = f"{c}&{t}&12574478&{data}"
        return md5(plain.encode(encoding='utf-8')).hexdigest()
    # 获取_m_h5_tk 和 _m_h5_tk_enc
    def get_m_h5_tk(self):
        print('get_m_h5_tk----self.t----', self.t)
        # current_time_ms = str(int(time.time() * 1000) + 3600000)
        # 当前时间戳
        current_time_ms = str(int(time.time() * 1000))
        print('current_time_ms----', current_time_ms)
        # 时间转换成年月日时分秒
        date_time = datetime.fromtimestamp(int(current_time_ms) / 1000)
        formatted_date1 = date_time.strftime('%Y-%m-%d %H:%M:%S')
        date_time2 = datetime.fromtimestamp(int(self.t) / 1000)
        formatted_date2 = date_time2.strftime('%Y-%m-%d %H:%M:%S')
        print('formatted_date1----', formatted_date1)
        print('formatted_date2----', formatted_date2)
        sign = Login_DM.get_sign('undefined', formatted_date1, {})
        print('get_m_h5_tk----sign----', sign)
        url = f'https://mtop.damai.cn/h5/mtop.damai.mxm.user.accesstoken.getbytbs/1.0/?jsv=2.7.2&appKey={self.appKey}&t={date_time}&sign={sign}&api=mtop.damai.mxm.user.accesstoken.getbytbs&v=1.0&type=jsonp&dataType=jsonp&callback=mtopjsonp1&data=%7B%7D'
        response = requests.get(
            url=url,
            headers={
                'referer': 'https://www.damai.cn/',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                'sec-ch-ua-mobile': '?0',
                'accept': '*/*',
                'sec-fetch-site': 'same-site',
                'sec-fetch-mode': 'no-cors',
                'sec-fetch-dest': 'script',
                'accept-language': 'zh-CN,zh;q=0.9',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'cookie': f'mtop_partitioned_detect=1; cna=Duf/H9GMc0QCAasPEWs/gUzO; xlly_s=1; _samesite_flag_=true; cookie2={self.cookie2};_tb_token_={self._tb_token_}; sgcookie={self.sgcookie};h5token={self.h5token};loginkey={self.loginkey}; user_id={self.user_id};'
            },
        )
        print('get_m_h5_tk----response----', response.text)
        # 正则处理数据
        data = re.search(r'mtopjsonp1\((.*)\)', response.text)
        if data:
            data = json.loads(data.group(1))
            print('get_m_h5_tk----data----', data)
        if "FAIL_SYS_TOKEN_EMPTY::令牌为空" in data.get('ret', []):
            print('get_m_h5_tk----response----ret', data.get('ret', [])[0])
            #  <RequestsCookieJar[] 转字符串
            self._m_h5_tk = response.cookies.get('_m_h5_tk', '')
            self._m_h5_tk_enc = response.cookies.get('_m_h5_tk_enc', '')
            print('get_m_h5_tk----_m_h5_tk----', self._m_h5_tk)
            print('get_m_h5_tk----_m_h5_tk_enc----', self._m_h5_tk_enc)
        pass
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


def get_sign(c, t, data):
    # c: token (undefined 转为空字符串)
    # t: 1735981325984
    # s: 12574478 (固定值)
    # n.data: "{}"
    plain = f"{c}&{t}&12574478&{data}"  # undefined&1735981325984&12574478&{}
    return md5(plain.encode(encoding='utf-8')).hexdigest()

if __name__ == '__main__':
    login_dm = Login_DM()
    # login_dm =  Login_DM.get_sign('', '1735981325984', "{}")
    print('login_dm----', login_dm)
    # 测试
    result = get_sign('undefined', '1736144551550', '{}')
    print('result----', result)
