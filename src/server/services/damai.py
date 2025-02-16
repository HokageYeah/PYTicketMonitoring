import logging
from typing import Optional
from urllib.parse import urlencode, quote
import requests
from src.server.schemas import PlatformEnum
from src.simulateLogin.Login_DM import Login_DM
import os
from pathlib import Path
from src import simulateLogin
import base64
from datetime import datetime
import json
from src.monitor.Monitor_DM import DM
from requests import Response
from src.server.schemas.concert import RecordMonitorParams, TicketPerform
from pydantic import BaseModel
from src.server.untiles.Ticket_Monitor import Ticket_Monitor
import asyncio
from src.server.untiles.Monitor_Thread_Manager import MonitorThreadManager
import time
import re
logger = logging.getLogger(__name__)

class DamaiService:
    # 大麦的base url（初步，不同服务的base url不一样）
    BASE_URL = "https://search.damai.cn/searchajax.html"
    def __init__(self):
        self.login_dm = Login_DM()
        # 读取获取db_config.json文件
        self.ticket_monitor = Ticket_Monitor()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://search.damai.cn/searchajax.html",
            "Origin": "https://search.damai.cn",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "search.damai.cn"
        }
        self.monitor_thread_manager = MonitorThreadManager()
        pass
    def do_request(self):
        inner_cookies = dict()
        def inner_request(url: str, cookies=None) -> Response:
            nonlocal inner_cookies
            # 更新获取大麦网写入到db_config.json文件中的数据信息
            self.ticket_monitor.get_db_config()
            inner_cookies['_m_h5_tk'] = self.ticket_monitor.db_config["DM"]["_m_h5_tk"]
            inner_cookies['_m_h5_tk_enc'] = self.ticket_monitor.db_config["DM"]["_m_h5_tk_enc"]
            inner_cookies['cookie2'] = self.ticket_monitor.db_config["DM"]["cookie2"]
            inner_cookies['sgcookie'] = self.ticket_monitor.db_config["DM"]["sgcookie"]
            # 有cookies则更新，没有则使用默认的，有cookies将cookies追加到inner_cookies中
            inner_cookies = inner_cookies if not cookies else { **inner_cookies, **cookies }
            print('inner_cookies----', inner_cookies)
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
                    "data": [],
                    "ret": [f"ERROR::获取大麦网数据失败{response.status_code}"],
                }
                # raise Exception(f"获取大麦网数据失败，\n接口: {self.BASE_URL}, \n错误: {response.status_code}")
            data = response.json()
            pageData = data.get('pageData', {})
            # currentPage 当前页码
            currentPage = pageData.get('currentPage', 0)
            # maxPage 最大页码
            maxPage = pageData.get('maxPage', 0)
            # nextPage 下一页
            nextPage = pageData.get('nextPage', 0)
            # onePageSize 每页条数
            onePageSize = pageData.get('onePageSize', 0)
            # resultData 结果数据
            resultData = pageData.get('resultData', [])
            # 遍历resultData
            concert_list = []
            for item in resultData:
                cityname = item.get('cityname', '')
                cityid = item.get('cityid', '')
                description = item.get('description', '')
                showid = item.get('projectid', '')
                showname = item.get('name', '')
                showtime = item.get('showtime', '')
                venue = item.get('venue', '')
                venuecity = item.get('venuecity', '')
                venueid = item.get('venueid', '')
                verticalPic = item.get('verticalPic', '')
                price_str = item.get('price_str', '')
                showstatus = item.get('showstatus', '')
                obj = {
                    'cityname': cityname,
                    'cityid': cityid,
                    'description': description,
                    'showid': showid,
                    'showname': showname,
                    'showtime': showtime,
                    'venue': venue,
                    'venuecity': venuecity,
                    'venueid': venueid,
                    'verticalPic': verticalPic,
                    'price_str': price_str,
                    'showstatus': showstatus,
                    'platform': PlatformEnum.DM
                }
                concert_list.append(obj)
            return {
                "data": {
                    "currentPage": currentPage,
                    "maxPage": maxPage,
                    "nextPage": nextPage,
                    "onePageSize": onePageSize,
                    "resultData": concert_list
                },
                "ret": ["SUCCESS::调用成功"],
            }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: {self.BASE_URL}, \n错误: {e}")
            return {
                "data": [],
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
            }
    # h5接口下搜索演唱会接口请求
    def search_concert_h5(self, cty: Optional[str] = '北京', keyword: Optional[str] = '', ctl: Optional[str] = '演唱会'):
        # 更新获取大麦网写入到db_config.json文件中的数据信息
        self.ticket_monitor.get_db_config()
        # 获取_m_h5_tk
        _m_h5_tk = self.ticket_monitor.db_config["DM"]["_m_h5_tk"]
        # 获取_m_h5_tk_enc
        _m_h5_tk_enc = self.ticket_monitor.db_config["DM"]["_m_h5_tk_enc"]
        # 如果_m_h5_tk或_m_h5_tk_enc为空，则获取临时_m_h5_tk、_m_h5_tk_enc
        if not _m_h5_tk or not _m_h5_tk_enc:
            res_data = self.get_temp_tk_h5()
            _m_h5_tk = res_data.get('data',{}).get('_m_h5_tk','')
            _m_h5_tk_enc = res_data.get('data',{}).get('_m_h5_tk_enc','')
            self.ticket_monitor.db_config["DM"]["_m_h5_tk"] = _m_h5_tk
            self.ticket_monitor.db_config["DM"]["_m_h5_tk_enc"] = _m_h5_tk_enc
            self.ticket_monitor.update_db_config()
        # 获取大麦网数据
        # 一分钟
        current_time_ms = str(int(time.time() * 1000))
        print('current_time_ms----', current_time_ms)
        date_time = datetime.fromtimestamp(int(current_time_ms) / 1000)
        print('date_time----', date_time)
        formatted_date1 = date_time.strftime('%Y-%m-%d %H:%M:%S')
        print('formatted_date1----', formatted_date1)
        data_text = '{"args":"{\\"comboConfigRule\\":\\"true\\",\\"sortType\\":\\"3\\",\\"latitude\\":\\"0\\",\\"longitude\\":\\"0\\",\\"groupId\\":\\"2394\\",\\"comboCityId\\":\\"852\\",\\"currentCityId\\":\\"852\\",\\"platform\\":\\"8\\",\\"comboChannel\\":\\"2\\",\\"dmChannel\\":\\"damai@damaih5_h5\\"}","patternName":"category_solo","patternVersion":"4.0","platform":"8","comboChannel":"2","dmChannel":"damai@damaih5_h5"}'
        # 判断如果是window环境
        if os.name == 'nt':
            data_text = '{"args":"{\\"comboConfigRule\\":\\"true\\",\\"sortType\\":\\"3\\",\\"latitude\\":\\"0\\",\\"longitude\\":\\"0\\",\\"groupId\\":\\"2394\\",\\"comboCityId\\":852,\\"currentCityId\\":852,\\"platform\\":\\"8\\",\\"comboChannel\\":\\"2\\",\\"dmChannel\\":\\"damai@damaih5_h5\\"}","patternName":"category_solo","patternVersion":"4.0","platform":"8","comboChannel":"2","dmChannel":"damai@damaih5_h5"}'
        sign = self.login_dm.get_sign('a194526cc6b4f5d851878ea53c63ce8d', '1739718333946', data_text)
        # b16eec219057eda9636a29c8c89a833f
        print('sign----', sign)
        print('_m_h5_tk----', _m_h5_tk)
        query_string = quote(data_text)
        print('query_string-----', query_string)
        # current_time_ms = '1739601438384'
        # sign_text = self.login_dm.get_sign('a194526cc6b4f5d851878ea53c63ce8d', current_time_ms, data_text)
        sign_text = self.login_dm.get_sign(_m_h5_tk, current_time_ms, data_text)
        # 测试用的
        # sign_text = '1a82b8a90f4216d6c887f1e573ed08e7'
        # current_time_ms = '1739715420271'
        print('sign_text----', sign_text)
        url = f'https://mtop.damai.cn/h5/mtop.damai.mec.aristotle.get/3.0/?jsv=2.7.4&appKey=12574478&t={current_time_ms}&sign={sign_text}&api=mtop.damai.mec.aristotle.get&v=3.0&H5Request=true&type=json&timeout=10000&dataType=json&valueType=string&forceAntiCreep=true&AntiCreep=true&useH5=true&data={query_string}'
        # url = f'https://mtop.damai.cn/h5/mtop.damai.mec.aristotle.get/3.0/?jsv=2.7.4&appKey=12574478&t={current_time_ms}&sign=cf082527f15487767127965059bf5190&api=mtop.damai.mec.aristotle.get&v=3.0&H5Request=true&type=json&timeout=10000&dataType=json&valueType=string&forceAntiCreep=true&AntiCreep=true&useH5=true&data=%7B%22args%22%3A%22%7B%5C%22comboConfigRule%5C%22%3A%5C%22true%5C%22%2C%5C%22sortType%5C%22%3A%5C%223%5C%22%2C%5C%22latitude%5C%22%3A%5C%220%5C%22%2C%5C%22longitude%5C%22%3A%5C%220%5C%22%2C%5C%22groupId%5C%22%3A%5C%222394%5C%22%2C%5C%22comboCityId%5C%22%3A%5C%22852%5C%22%2C%5C%22currentCityId%5C%22%3A%5C%22852%5C%22%2C%5C%22platform%5C%22%3A%5C%228%5C%22%2C%5C%22comboChannel%5C%22%3A%5C%222%5C%22%2C%5C%22dmChannel%5C%22%3A%5C%22damai%40damaih5_h5%5C%22%7D%22%2C%22patternName%22%3A%22category_solo%22%2C%22patternVersion%22%3A%224.0%22%2C%22platform%22%3A%228%22%2C%22comboChannel%22%3A%222%22%2C%22dmChannel%22%3A%22damai%40damaih5_h5%22%7D'
        # url = f'https://mtop.damai.cn/h5/mtop.damai.mec.aristotle.get/3.0/?jsv=2.7.4&appKey=12574478&t=1739715420271&sign=1a82b8a90f4216d6c887f1e573ed08e7&api=mtop.damai.mec.aristotle.get&v=3.0&H5Request=true&type=json&timeout=10000&dataType=json&valueType=string&forceAntiCreep=true&AntiCreep=true&useH5=true&data=%7B%22args%22%3A%22%7B%5C%22comboConfigRule%5C%22%3A%5C%22true%5C%22%2C%5C%22sortType%5C%22%3A%5C%223%5C%22%2C%5C%22latitude%5C%22%3A%5C%220%5C%22%2C%5C%22longitude%5C%22%3A%5C%220%5C%22%2C%5C%22groupId%5C%22%3A%5C%222394%5C%22%2C%5C%22comboCityId%5C%22%3A852%2C%5C%22currentCityId%5C%22%3A852%2C%5C%22platform%5C%22%3A%5C%228%5C%22%2C%5C%22comboChannel%5C%22%3A%5C%222%5C%22%2C%5C%22dmChannel%5C%22%3A%5C%22damai%40damaih5_h5%5C%22%7D%22%2C%22patternName%22%3A%22category_solo%22%2C%22patternVersion%22%3A%224.0%22%2C%22platform%22%3A%228%22%2C%22comboChannel%22%3A%222%22%2C%22dmChannel%22%3A%22damai%40damaih5_h5%22%7D'
        # url = f'https://mtop.damai.cn/h5/mtop.damai.mec.aristotle.get/3.0/?jsv=2.7.4&appKey=12574478&t=1739715420271&sign=1a82b8a90f4216d6c887f1e573ed08e7&api=mtop.damai.mec.aristotle.get&v=3.0&H5Request=true&type=json&timeout=10000&dataType=json&valueType=string&forceAntiCreep=true&AntiCreep=true&useH5=true&data={query_string}'
        response = requests.get(url,
                                headers={
                                    'Accept': 'application/json',
                                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.53(0x18003531) NetType/WIFI Language/zh_CN',
                                    'Referer': 'https://m.damai.cn/' 
                                },
                                cookies={
                                    # '_m_h5_tk': 'a194526cc6b4f5d851878ea53c63ce8d_1739725133797',
                                    # '_m_h5_tk_enc': 'fcceaa6db66175664430c152bded4585',
                                    '_m_h5_tk': _m_h5_tk,
                                    '_m_h5_tk_enc': _m_h5_tk_enc
                                },
                                verify=False,
                                timeout=10
        )
        # response = self.do_request()(url)
        print('search_concert_h5----response----', response.json())
        return {
            "data": {},
            "ret": ["SUCCESS::调用成功"],
        }
    # H5接口，获取未登录情况下的临时_m_h5_tk、_m_h5_tk_enc
    def get_temp_tk_h5(self):
        current_time_ms = str(int(time.time() * 1000))
        date_time = datetime.fromtimestamp(int(current_time_ms) / 1000)
        formatted_date1 = date_time.strftime('%Y-%m-%d %H:%M:%S')
        print('search_concert_h5----current_time_ms----', current_time_ms)
        data = {
            "apiVersion": "2.6",
            "platform": "8",
            "comboChannel": "2",
            "dmChannel": "damai@damaih5_h5"
        }
        # query_string = urlencode(data,encoding='utf-8')
        data_text = '{"apiVersion":"2.6","platform":"8","comboChannel":"2","dmChannel":"damai@damaih5_h5"}'
        sign = self.login_dm.get_sign('undefined', current_time_ms, data_text)
        # sign = self.login_dm.get_sign('undefined', '1739719160168', data_text)
        print('search_concert_h5----sign----', sign)
        query_string = quote(data_text)
        print('get_temp_tk_h5----query_string----', query_string)
        url = f"https://mtop.damai.cn/h5/mtop.damai.wireless.search.cms.category.get/2.0/?jsv=2.7.4&appKey=12574478&t={current_time_ms}&sign={sign}&api=mtop.damai.wireless.search.cms.category.get&v=2.0&H5Request=true&type=jsonp&timeout=10000&forceAntiCreep=true&AntiCreep=true&useH5=true&dataType=jsonp&callback=mtopjsonp1&data={query_string}"
        try:
            response = requests.get(url, headers={
                'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.53(0x18003531) NetType/WIFI Language/zh_CN',
            'Referer': 'https://m.damai.cn/'
            },timeout=10)
            responseText = response.text
            data = {}
            # 判断mtopjsonp1 是否存在
            if 'mtopjsonp1' in responseText:
                try:
                    match = re.search(r'mtopjsonp\d*\((.*)\)', responseText)
                    if not match:
                        raise ValueError("无效的 JSONP 格式")
                    json_data = match.group(1)
                    data = json.loads(json_data)
                    print('get_temp_tk_h5----data----', data)
                except Exception as e:
                    logger.error(f"获取大麦临时_m_h5_tk、_m_h5_tk_enc失败，\n接口: {url}, \n错误: {e}")
                    return {
                        "data": {},
                        "ret": [f"ERROR::获取大麦临时_m_h5_tk、_m_h5_tk_enc失败{e}"],
                    }
            else:
                data = json.loads(responseText)
            ret = data.get('ret')
            print('get_temp_tk_h5----ret----', ret, isinstance(ret, list), 'FAIL_SYS_TOKEN_EMPTY' in ret[0])
            # 判断ret是否是列表，并且是否包含FAIL_SYS_TOKEN_EMPTY
            if isinstance(ret, list) and 'FAIL_SYS_TOKEN_EMPTY' in ret[0]:
                print('---------------')
                print('get_temp_tk_h5----response.cookies----', response.cookies)
                cookies = requests.utils.dict_from_cookiejar(response.cookies)
                _m_h5_tk = cookies.get('_m_h5_tk')
                _m_h5_tk_enc = cookies.get('_m_h5_tk_enc')
                print('get_temp_tk_h5----_m_h5_tk----', _m_h5_tk)
                print('get_temp_tk_h5----_m_h5_tk_enc----', _m_h5_tk_enc)
                return {
                    "data": {
                        "_m_h5_tk": _m_h5_tk,
                        "_m_h5_tk_enc": _m_h5_tk_enc,
                    },
                    "ret": ["SUCCESS::调用成功"],
                }
        except Exception as e:
            logger.error(f"获取大麦临时_m_h5_tk、_m_h5_tk_enc失败，\n接口: {url}, \n错误: {e}")
            return {
                "data": {},
                "ret": [f"ERROR::获取大麦临时_m_h5_tk、_m_h5_tk_enc失败{e}"],
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
            _m_h5_tk_str = self.ticket_monitor.db_config["DM"]["_m_h5_tk"]+';'+self.ticket_monitor.db_config["DM"]["_m_h5_tk_enc"]
            response = self.do_request()(url(show_id, _m_h5_tk_str))
            res_data = response.json()
            print('res_data----', res_data)
            ret = res_data.get('ret')
            print('res_data----ret', ret)
            print('response.status_code----', response.status_code)
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
            _m_h5_tk_str = self.ticket_monitor.db_config["DM"]["_m_h5_tk"]
            response = self.do_request()(url(show_id, session_id, _m_h5_tk_str))
            print("响应 Cookies:", response.cookies.get_dict())
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
            "venue_city_name": params.venue_city_name,
            "venue_name": params.venue_name,
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
        try:
            # 更新获取大麦网写入到db_config.json文件中的数据信息
            self.ticket_monitor.get_db_config()
            if not self.ticket_monitor.db_config["DM"].get("monitor_list",[]):
                self.ticket_monitor.db_config["DM"]["monitor_list"] = []
            monitor_list = self.ticket_monitor.db_config["DM"]["monitor_list"]
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
                        monitor_person_list.append(monitor_item.get('monitor_person')[0])
                    else:
                        monitor_person_list[wx_token_item_index]['ticket_perform'] = monitor_item.get('monitor_person')[0].get('ticket_perform',[])
                    monitor_list[show_id_item_index]['monitor_person'] = monitor_person_list
            # 将monitor_list转换为字符串
            self.ticket_monitor.db_config["DM"]["monitor_list"] = monitor_list
            # 更新获取大麦网写入到db_config.json文件中的数据信息
            self.ticket_monitor.update_db_config()
            return {
                "platform": PlatformEnum.DM,
                "api": 'record.monitor.by.platform',
                "data": {
                    "monitor_list": monitor_list
                },
                "ret": ["SUCCESS::调用成功"],
                "v": 1
                }
        except Exception as e:
            logger.error(f"获取大麦网数据失败，\n接口: post_record_monitor_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'record.monitor.by.platform',
                "data": {},
                "ret": [f"ERROR::获取大麦网数据失败{e}"],
                "v": 1
            }
    def monitor_ticket(self, show_id, ticket_perform: TicketPerform):
        # 获取大麦网监控对象
        logging.info(f"大麦 {self.show_info.get('show_name')} 监控中")
        can_buy_list = list()
        for ticket_perform_item in ticket_perform:
            # 获取ticket_perform中的perform_id
            perform_id = ticket_perform_item.get('perform_id')
            response = self.check_ticket_web(show_id, perform_id)
            if response.json().get("ret") == ["SUCCESS::调用成功"]:
                result = json.loads(response.json().get("data").get("result"))  
                # 遍历result
                for sku_item in result.get("perform").get("skuList"):
                    # 获取sku_item中的sku_id
                    sku_id = sku_item.get('skuId')
                    # 获取sku_item中的skuSalable
                    skuSalable = sku_item.get('skuSalable')
                    if skuSalable == "false":
                        continue
                    can_buy_list.append(sku_id)
        return can_buy_list

    # 调用票务监控开始、检测数据库中存储的演唱会票务情况
    def post_start_monitor_web(self, threadStop: bool = False):
        try:
            # 方案一、采用多线程
            # threading.Thread 是创建新线程的构造函数。
            # target=damai.post_start_monitor_web 指定了线程要执行的目标函数，即 damai 对象的 post_start_monitor_web 方法。
            # daemon=True 表示这个线程是一个守护线程。守护线程在主程序退出时会自动终止，而不需要等待它完成。这通常用于后台任务。
            # self.thread = threading.Thread(target=self.ticket_monitor.monitor, args=(self,), daemon=True)
            # 判断线程是否存在、且self.thread线程是否不在运行
            self.monitor_thread_manager.start_monitor(self.ticket_monitor.monitor, args=(self, self.monitor_thread_manager))
            # 方案二、采用异步任务
            # asyncio.create_task(self.ticket_monitor.monitor_async(self))
        except Exception as e:
            logger.error(f"调用票务监控失败，\n接口: start_monitor_web, \n错误: {e}")
            return {
                "platform": PlatformEnum.DM,
                "api": 'start.monitor.by.platform',
                "data": {},
                "ret": [f"ERROR::调用票务监控数据失败{e}"],
                "v": 1
            }
        