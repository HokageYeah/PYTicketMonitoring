import logging
from typing import Optional
from urllib.parse import urlencode
import requests
from src.server.schemas import PlatformEnum
from src.simulateLogin.Login_DM import Login_DM
import os
from pathlib import Path
from src import simulateLogin
import base64
logger = logging.getLogger(__name__)
class DamaiService:
    # 大麦的base url（初步，不同服务的base url不一样）
    BASE_URL = "https://search.damai.cn/searchajax.html"
    def __init__(self):
        self.login_dm = Login_DM()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://search.damai.cn/searchajax.html",
            "Origin": "https://search.damai.cn",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "search.damai.cn"
        }
        pass
    # 网站搜索演唱会接口请求
    def search_concert_web(
            self, 
            cty: Optional[str] = '北京', 
            keyword: Optional[str] = '', 
            ctl: Optional[str] = '演唱会',
            sctl: Optional[str] = '', 
            tsg: Optional[int] = 0, # 表示是否有其他限制条件，通常为 0 表示没有额外的条件。
            st: Optional[int] = 0, # 为空，表示没有开始时间。
            et: Optional[int] = 0, # 为空，表示没有结束时间。
            order: Optional[int] = 1, # 通常表示排序方式，1 可能代表按某种默认方式排序。
            currPage: Optional[int] = 1,
            pageSize: Optional[int] = 10,
            tn: Optional[int] = 0, # 通常表示是否需要返回总数，0 表示不需要。
            ):
        try:
            params = {
                "cty": cty,
                "keyword": keyword,
                "ctl": ctl,
                "sctl": sctl,
                "tsg": tsg,
                "st": st,
                "et": et,
                "order": order,
                "currPage": currPage,
                "pageSize": pageSize,
                "tn": tn,
            }
            query_string = urlencode(params,encoding='utf-8')
            url = f"{self.BASE_URL}?{query_string}"
            # request同步请求
            response = requests.get(url, headers=self.headers,timeout=10)
            if response.status_code != 200:
                logger.error(f"获取大麦网数据失败，\n接口: {self.BASE_URL}, \n错误: {response.status_code}")
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'search.concert.by.platform',
                    "data": {},
                    "ret": [f"ERROR::获取大麦网数据失败{response.status_code}"],
                    "v": 1
                }
                # raise Exception(f"获取大麦网数据失败，\n接口: {self.BASE_URL}, \n错误: {response.status_code}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'search.concert.by.platform',
                "data": response.json(),
                "ret": ["SUCCESS::调用成功"],
                "v": 1
            }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: {self.BASE_URL}, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'search.concert.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    # 网站生成二维码接口
    def get_generate_code_web(self):
        # 先删除存放二维码文件的目录
        save_img_path = Path(simulateLogin.__file__).resolve().parent / 'QRCode_DM.png'
        print('save_img_path----', save_img_path)
        if os.path.exists(save_img_path):
            print('删除二维码文件')
            os.remove(save_img_path)
        try:
            # 生成二维码
            self.login_dm.get_generate_code()
            # 返回二维码图片
            if os.path.exists(save_img_path):
                # 将文件转换为base64
                with open(save_img_path, 'rb') as file:
                    base64_data = base64.b64encode(file.read()).decode('utf-8')
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'login.qrcode.by.platform',
                    "data": {
                        "base64_data": base64_data
                    },
                    "ret": ["SUCCESS::调用成功"],
                    "v": 1
                }
            else:
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'login.qrcode.by.platform',
                    "data": {},
                    "ret": ["ERROR::二维码文件不存在"],
                    "v": 1
                }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: get_generate_code_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'login.qrcode.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    # 网站验证查询是否扫码登录
    def post_login_query_web(self):
        try:
            res_data = self.login_dm.post_query_login()
            msg = res_data.get('msg')
            if res_data.get('satus') == 'error':
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'login.query.by.platform',
                    "data": res_data,
                    "ret": [f"ERROR::调用失败{msg}"],
                    "v": 1
                }
            return {
                "platform": PlatformEnum.DM,
                "api": 'login.query.by.platform',
                "data": res_data,
                "ret": [f"SUCCESS::{msg}"],
                "v": 1
            }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: get_login_query_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'login.query.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    # 扫码成功后调用登录
    def get_dologin_web(self):
        try:
            res_data = self.login_dm.get_dologin()
            msg = res_data.get('msg')
            if res_data.get('status') == 'error':
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'login.dologin.by.platform',
                    "data": res_data,
                    "ret": [f"ERROR::{msg}"],
                    "v": 1
                }
            return {
                "platform": PlatformEnum.DM,
                "api": 'login.dologin.by.platform',
                "data": res_data,
                "ret": [f"SUCCESS::{msg}"],
                "v": 1
            }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: get_dologin_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'login.dologin.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    # 获取大麦网用户信息(主要获取_m_h5_tk 和 _m_h5_tk_enc) 用户信息写入到config.json文件中
    def get_user_info_web(self):
        try:
            res_data = self.login_dm.get_m_h5_tk()
            msg = res_data.get('msg')
            if res_data.get('status') == 'error':
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'login.userinfo.by.platform',
                    "data": res_data,
                    "ret": [f"ERROR::{msg}"],
                    "v": 1
                }
            return {
                "platform": PlatformEnum.DM,
                "api": 'login.userinfo.by.platform',
                "data": res_data,
                "ret": [f"SUCCESS::{msg}"],
                "v": 1
            }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: get_user_info_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'login.userinfo.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    # 获取单个演唱会详情信息（鉴权、需要登录）
    def get_item_detail_web(self, show_id):
        try:
            pass
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: get_item_detail_web, \n错误: {e}")
            return {}
    # 调用票务监控开始 测试代码需要更改
    def post_start_monitor_web(self, show_id, show_name, deadline):
        try:
            # 测试代码
            from src.monitor.start import Runner
            runner = Runner()
            runner.start()
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: start_monitor_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'start.monitor.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }