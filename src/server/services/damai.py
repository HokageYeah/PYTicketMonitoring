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
from time import time
import json
from src.monitor.Monitor_DM import DM
from src import monitor
from requests import Response
from src.server.schemas.concert import RecordMonitorParams
logger = logging.getLogger(__name__)

class DamaiService:
    # 大麦的base url（初步，不同服务的base url不一样）
    BASE_URL = "https://search.damai.cn/searchajax.html"
    def __init__(self):
        self.login_dm = Login_DM()
        # 读取获取db_config.json文件
        self.db_config_path = Path(monitor.__file__).resolve().parent / 'config' / 'db_config.json'
        self.db_config = {}
        self.get_db_config()
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
    # 查询读取获取db_config.json文件中的数据信息
    def get_db_config(self):
        with open(self.db_config_path, 'r', encoding='utf-8') as f:
            # 将f转为字符串 在转换为json
            self.db_config = json.load(f)
    # 更新获取大麦网写入到db_config.json文件中的数据信息
    def update_db_config(self):
        # 将RecordMonitorParams类型转换为字典
        json_str = str(self.db_config)
        # 将json_str转换为字典
        config_dict = json.loads(json_str)
        print('update_db_config----json_str----', config_dict)
        # config_dict = {}
        # for key, value in self.db_config.items():
        #     config_dict[key] = value
        with open(self.db_config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False)
    def do_request(self):
        inner_cookies = dict()
        def inner_request(url: str, cookies=None) -> Response:
            nonlocal inner_cookies
            # 更新获取大麦网写入到db_config.json文件中的数据信息
            self.get_db_config()
            inner_cookies['_m_h5_tk'] = self.db_config["DM"]["_m_h5_tk"]
            inner_cookies['_m_h5_tk_enc'] = self.db_config["DM"]["_m_h5_tk_enc"]
            inner_cookies['cookie2'] = self.db_config["DM"]["cookie2"]
            inner_cookies['sgcookie'] = self.db_config["DM"]["sgcookie"]
            # 有cookies则更新，没有则使用默认的，有cookies将cookies追加到inner_cookies中
            inner_cookies = inner_cookies if not cookies else { **inner_cookies, **cookies }
            # print('inner_cookies----', inner_cookies)
            return requests.get(
                url=url,
                headers={
                    'x-tap': 'wx',
                    'Host': 'mtop.damai.cn',
                    'Accept': 'application/json',
                    'content-type': 'application/x-www-form-urlencoded',
                    'Referer': 'https://servicewechat.com/wx938b41d0d7e8def0/350/page-frame.html',
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.53(0x18003531) NetType/WIFI Language/zh_CN',
                },
                cookies=inner_cookies,
                verify=False,
                timeout=10
            )
        return inner_request
    # 网站搜索演唱会接口请求
    def search_concert_web(
            self, 
            cty: Optional[str] = '北京', 
            keyword: Optional[str] = '', 
            ctl: Optional[str] = '演唱会',
            sctl: Optional[str] = '', 
            tsg: Optional[int] = 0, # 表示是否有其他限制条件，通常为 0 表示没有额外的条件。
            st: Optional[int] = '', # 为空，表示没有开始时间。
            et: Optional[int] = '', # 为空，表示没有结束时间。
            order: Optional[int] = 1, # 通常表示排序方式，1 可能代表按某种默认方式排序。
            currPage: Optional[int] = 1,
            pageSize: Optional[int] = 30,
            tn: Optional[int] = '', # 通常表示是否需要返回总数，0 表示不需要。
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
            url = DM.get_show_url()
            _m_h5_tk_str = self.db_config["DM"]["_m_h5_tk"]+';'+self.db_config["DM"]["_m_h5_tk_enc"]
            response = self.do_request()(url(show_id, _m_h5_tk_str))
            print('response----', response)
            res_data = response.json()
            ret = res_data.get('ret')
            if response.status_code != 200 or 'SUCCESS::调用成功' not in ret:
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'item.detail.by.platform',
                    "data": response.json(),
                    "ret": [f"ERROR::获取大麦网数据失败{ret}"],
                    "v": 1
                }
            legacy = res_data.get('data',{}).get('legacy','')
            # 去除转义自负
            legacy = json.loads(legacy)
            return {
                "platform": PlatformEnum.DM,
                "api": 'item.detail.by.platform',
                "data": {
                    "legacy": legacy,
                    "traceId": res_data.get('traceId','')
                },
                "ret": ["SUCCESS::调用成功"],
                "v": 1
            }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: get_item_detail_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'item.detail.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    # 检测当前场次是否有坐次（是否又票）
    def check_ticket_web(self, show_id, session_id):
        try:
            url = DM.get_seat_url()
            _m_h5_tk_str = self.db_config["DM"]["_m_h5_tk"]
            response = self.do_request()(url(show_id, session_id, _m_h5_tk_str))
            print('response----', response)
            res_data = response.json()
            ret = res_data.get('ret')
            if response.status_code != 200 or 'SUCCESS::调用成功' not in ret:
                return {
                    "platform": PlatformEnum.DM,
                    "api": 'check.ticket.by.platform',
                    "data": response.json(),
                    "ret": [f"ERROR::获取大麦网数据失败{ret}"],
                    "v": 1
                }
            result = res_data.get('data',{}).get('result','')
            result = json.loads(result)
            return {
                "platform": PlatformEnum.DM,
                "api": 'check.ticket.by.platform',
                "data": {
                    "result": result,
                    "traceId": res_data.get('traceId','')
                },
                "ret": ["SUCCESS::调用成功"],
                "v": 1
            }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: check_ticket_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'check.ticket.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    # 转换参数为指定格式
    def convert_params_to_format(self, params: RecordMonitorParams):
        return {
            "show_id": params.show_id,
            "show_name": params.show_name,
            "monitor_person": [
                {
                    "wx_token": params.wx_token,
                    "deadline": params.deadline,
                    "ticket_perform": params.ticket_perform
                }
            ]
        }
    # 记录用户需要监控的演唱会、场次、座次、时间、微信token、 监控时间
    def post_record_monitor_web(self, params: RecordMonitorParams):
        # 更新获取大麦网写入到db_config.json文件中的数据信息
        self.get_db_config()
        if not self.db_config["DM"].get("monitor_list",[]):
            self.db_config["DM"]["monitor_list"] = []
        monitor_list = self.db_config["DM"]["monitor_list"]
        # params转字符串
        # params_str = json.dumps(params)
        # params转字典
        # params_dict = json.loads(params_str)
        # 判断monitor_list中是否存在params.show_id
        # 使用 enumerate 找到第一个符合条件的元素的下标
        show_id_item_index = next((i for i, item in enumerate(monitor_list) if item.get('show_id') == params.show_id), -1)
        if show_id_item_index == -1:
            monitor_item = self.convert_params_to_format(params)
            monitor_list.append(monitor_item)
        else:
            monitor_person_list = monitor_list[show_id_item_index].get('monitor_person',[])
            monitor_item = self.convert_params_to_format(params)
            if not monitor_person_list:
                monitor_list[show_id_item_index]['monitor_person'] = [monitor_item.get('monitor_person')]
            else:
                wx_token_item_index = next((i for i, item in enumerate(monitor_person_list) if item.get('wx_token') == params.wx_token), -1)
                if wx_token_item_index == -1:
                    monitor_person_list.append(monitor_item.get('monitor_person'))
                else:
                    monitor_person_list[wx_token_item_index]['ticket_perform'] = monitor_item.get('monitor_person')[0].get('ticket_perform')
                monitor_list[show_id_item_index]['monitor_person'] = monitor_person_list
        # 将monitor_list转换为字符串
        self.db_config["DM"]["monitor_list"] = monitor_list
        print('post_record_monitor_web----db_config----', self.db_config)
        print('post_record_monitor_web----monitor_list----', type(self.db_config))
        # 更新获取大麦网写入到db_config.json文件中的数据信息
        self.update_db_config()
        return {
            "platform": PlatformEnum.DM,
            "api": 'record.monitor.by.platform',
            "data": {},
            "ret": ["SUCCESS::调用成功"],
            "v": 1
        }

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