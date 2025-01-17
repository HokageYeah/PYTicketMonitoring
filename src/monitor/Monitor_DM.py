import json
import logging
import os
from pathlib import Path
import urllib.parse
from hashlib import md5
from time import time

import requests
from requests import Response

from src.monitor.Monitor import Monitor


# _m_h5_tk = "b7abff586651e36b8adb7f386dfdae82_1736156531034"
# _m_h5_tk_enc = "2ebd2007350c6461032cfc3b2dc63db5"
# cookie2 = "1c1f0f2f03cad5559fd93b6afc8ef4d4"
# sgcookie = "E100yEqPPb7ui1QE0%2FB99Q0wMHDsqKauE%2BCdZhac%2BDCIMY9wUaMCCD8zcXBHIU16OldHPv2YuMI1XwK7lc%2F%2BxOflfaw6d7jmnT9JNQBmHw2lqzU%3D"

class DM(Monitor):
    def __init__(self, perform: dict) -> None:
        super().__init__()
        # 获取当前文件的绝对路径
        self.current_dir = Path(__file__).resolve().parent
        print('current_dir---', Path(__file__).resolve())
        print('current_dir---os.getcwd()', os.getcwd())
        # 记录请求信息的路径
        self.seat_info_dir = self.current_dir / 'request_logs' / 'formatted_seat_info.json'
        self.show_info_dir = self.current_dir / 'request_logs' / 'formatted_show_info.json'
        self.show_url = DM.get_show_url()
        self.seat_url = DM.get_seat_url()
        self.request = self.do_request()
        self._m_h5_tk = perform.get('_m_h5_tk') or ''
        self._m_h5_tk_enc = perform.get('_m_h5_tk_enc') or ''
        self.cookie2 = perform.get('cookie2') or ''
        self.sgcookie = perform.get('sgcookie') or ''
        self.show_info = {
            "platform": "大麦",
            "seat_info": list(),
            "session_info": list(),
            "show_id": perform.get('show_id'),
            "show_name": perform.get('show_name')
        }
        logging.info(f"大麦 {perform.get('show_name')} 开始加载")
        self.get_show_infos()
        logging.info(f"大麦 {self.show_info.get('show_name')} 加载成功")

    def get_show_infos(self):
        show_id = self.show_info.get('show_id')
        response = self.request(self.show_url(show_id, self._m_h5_tk+';'+self._m_h5_tk_enc), {
            '_m_h5_tk': self._m_h5_tk,
            '_m_h5_tk_enc': self._m_h5_tk_enc,
        })
        data = self.get_data_from_response(response)
        show_info = data.get("detailViewComponentMap").get("item")
        for session in show_info.get("item").get("performBases"):
            session_id = session.get("performs")[0].get("performId")
            session_name = session.get("performs")[0].get("performName")
            self.show_info["session_info"].append({
                "session_id": session_id,
                "session_name": session_name,
            })
            response = self.request(self.seat_url(show_id, session_id, self._m_h5_tk), {
                '_m_h5_tk': self._m_h5_tk,
                '_m_h5_tk_enc': self._m_h5_tk_enc,
                'cookie2': self.cookie2,
                'sgcookie': self.sgcookie,
            })
            show_session_info = self.get_data_from_response(response, session_id)
            for seat in show_session_info.get("perform").get("skuList"):
                self.show_info["seat_info"].append({
                    "session_id": session_id,
                    "session_name": session_name,
                    "seat_plan_id": seat.get("skuId"),
                    "seat_plan_name": seat.get("priceName"),
                })

    def monitor(self) -> list:
        logging.info(f"大麦 {self.show_info.get('show_name')} 监控中")
        can_buy_list = list()
        show_id = self.show_info.get('show_id')
        for session in self.show_info["session_info"]:
            session_id = session.get("session_id")
            response = self.request(self.seat_url(show_id, session_id))
            show_session_info = self.get_data_from_response(response, session_id)
            for seat in show_session_info.get("perform").get("skuList"):
                if seat.get("skuSalable") == "false":
                    continue
                can_buy_list.append(seat.get("skuId"))
        return can_buy_list

    def get_data_from_response(self, response, ext="show"):
        show_id = self.show_info.get('show_id')
        if "SUCCESS::调用成功" not in response.json().get("ret"):
            print('get_data_from_response----notSuccess----', response.json())
            if ext == "show":
                # 判断是否有c，没有的话不走
                if response.json().get("c"):
                    response = self.request(self.show_url(show_id, c=response.json().get("c")))
            else:
                cookies = requests.utils.dict_from_cookiejar(response.cookies)
                # print('get_data_from_response----cookies----', cookies, cookies.get("_m_h5_tk"))
                # 此处先手动新增cookie2=1f56672a98cc42c47546c91473a322d3; sgcookie=E100JIyltUJPAjTx3DYs2QzajRuhE8Rh49DNzCJ79gAVVnP4GTQM26rHxWQiaY8%2FoIFTxIQLzPJWpYG3Gfcs2x%2F2ukBswjUZU0VauQJ%2Fz5YabEY%3D; 
                # cookies["cookie2"] = "12f638562826222299599e475cdd39e1"
                # cookies["sgcookie"] = "E100%2BcUPFBhYsGevVrtacjzRm5YQQ5n5JuMbLX07MmFVefW6%2F9AF3%2B%2BLp50F6uTCNz0HgNvgHVURIrFKlXJkkYorG%2F%2FVJ2S5e%2Fzwec5xne7XsN8%3D"
                response = self.request(self.seat_url(show_id, ext, c=cookies.get("_m_h5_tk")), cookies=cookies)
        else:
            print('get_data_from_response----response----', response)
            print('get_data_from_response----successcookie----', response.cookies)
            cookies = requests.utils.dict_from_cookiejar(response.cookies)
            print('get_data_from_response----successcookies----dict_from_cookiejar', cookies)
            print('get_data_from_response----success', ext)
        # return response.json().get("data",{}).get("legacy",{}) if ext == "show" else json.loads(response.json().get("data").get("result"))
        data = json.loads(response.json().get("data",{}).get("legacy",{})) if ext == "show" else json.loads(response.json().get("data").get("result"))
        # 判断data的数据格式，并打印
        print('get_data_from_response----data----1', type(data))
        fileName = self.show_info_dir if ext == "show" else self.seat_info_dir
        self.save_formatted_json(data, fileName)
        return data
    
    # 将数据处理成文件好查看
    def save_formatted_json(self, data, filename=None):
        try:
            # 如果data是DM类实例，转换为字典
            if isinstance(data, DM):
                data = data.__dict__  # 或者其他方式获取要保存的数据
            # 确保数据是可序列化的
            if not isinstance(data, (dict, list, str, int, float, bool)):
                raise TypeError(f"数据类型 {type(data)} 不支持JSON序列化")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"JSON数据已成功保存到 {filename}")
        except Exception as e:
            print(f"保存文件时出错: {e}")

    @staticmethod
    def get_show_url():
        # inner_c = '5441487fd096478b73f9b299562eb789_1731931246634;150179d8faf5815c2f70b06bd9a82bc4'
        inner_c = 'fa9fab6fa48214a57044f341b3b4d8fe_1735103108001;371ef2f09bc7f39c177b055cc1a76457'
        def inner_show_url(show_id: str, c=""):
            nonlocal inner_c
            inner_c = inner_c if not c else c
            # 大麦的场次接口地址
            url = 'https://mtop.damai.cn/h5/mtop.damai.item.detail.getdetail/1.0/'
            # 当前时间往后延迟一个小时
            current_time_ms = str(int(time() * 1000) + 3600000)
            print('current_time_ms---', current_time_ms)
            params = {
                'jsv': '2.7.4',
                'appKey': '12574478',
                't': current_time_ms,
                'sign': '4aa0548d1e42d11b1a4bc4eaddde4da5',
                'api': 'mtop.damai.item.detail.getdetail',
                'v': '1.0',
                'H5Request': 'true',
                'type': 'json',
                'timeout': '10000',
                'dataType': 'json',
                'valueType': 'string',
                'forceAntiCreep': 'true',
                'AntiCreep': 'true',
                'useH5': 'true',
                'data': '{"itemId":"'+show_id+'","platform":"8","comboChannel":"2","dmChannel":"damai@damaih5_h5"}',
                'AntiFlood': 'true',
                'url': 'mtop.damai.item.detail.getdetail',
                'env': 'm',
                '_bx-m': '0.0.11',
                 'c': inner_c,
            }
            params["sign"] = DM.get_sign(params["c"], params["t"], params["data"])
            print("sign----", params["sign"])
            return f"{url}?{urllib.parse.urlencode(params)}"
        return inner_show_url

    @staticmethod
    def get_seat_url():
        # inner_c = 'e1ff1f67d9bd7570c338aabd651c011d_1731992988831'
        inner_c = 'fa9fab6fa48214a57044f341b3b4d8fe_1735103108001'
        def inner_seat_url(show_id: str, session_id: str, c=""):
            # print('inner_seat_url----show_id----', show_id)
            # print('inner_seat_url----session_id----', session_id)
            # print('inner_seat_url----c----', c)
            nonlocal inner_c
            inner_c = inner_c if not c else c
            # 大麦的坐次接口地址
            url = 'https://mtop.damai.cn/h5/mtop.alibaba.detail.subpage.getdetail/2.0/'
            current_time_ms = str(int(time() * 1000) + 3600000)
            params = {
                'jsv': '2.7.4',
                'appKey': '12574478',
                't': current_time_ms,
                'sign': 'cfcc345ab6871c74f3b1d45ff536d261',
                'api': 'mtop.alibaba.detail.subpage.getdetail',
                'v': '2.0',
                'H5Request': 'true',
                'type': 'originaljson',
                'timeout': '10000',
                'dataType': 'json',
                'valueType': 'original',
                'forceAntiCreep': 'true',
                'AntiCreep': 'true',
                'useH5': 'true',
                'data': '{"itemId":"' + show_id + '","bizCode":"ali.china.damai","scenario":"itemsku","exParams":"{\\"dataType\\":2,\\"dataId\\":\\"' + session_id + '\\"}","platform":"8","comboChannel":"2","dmChannel":"damai@damaih5_h5"}',
            }
            params["sign"] = DM.get_sign(inner_c, params["t"], params["data"])
            # print('get_seat_url----allParams----', params)
            # print('get_seat_url----allParams----', params)
            print('get_seat_url----url----', f"{url}?{urllib.parse.urlencode(params)}")
            return f"{url}?{urllib.parse.urlencode(params)}"
        return inner_seat_url

    @staticmethod
    def get_sign(c: str, t: str, data: str):
        plain = f"{c.split('_')[0]}&{t}&12574478&{data}"
        return md5(plain.encode(encoding='utf-8')).hexdigest()
    def do_request(self):
        inner_cookies = dict()
        def inner_request(url: str, cookies=None) -> Response:
            nonlocal inner_cookies
            inner_cookies = inner_cookies if not cookies else cookies
            print('inner_cookies----url---', url)
            print('inner_cookies----cookies---', inner_cookies)
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
                # cookies={
                #     'csg': '354a0bd6',
                #     '_hvn_login': '18',
                #     'munb': '2218951629204',
                #     'usercode': '532127652',
                #     '_samesite_flag_': 'true',
                #     'havanaId': '2218951629204',
                #     '_tb_token_': 'ee5b537387ee1',
                #     't': '0bdf4d2eef5a59975c4922c8c7f6e4e9',
                #     'dm_nickname': '%E9%BA%A6%E5%AD%90acCkX',
                #     'cookie2': '1318094fd8689145b9831b581c396fd7',
                #     'isg': 'BHNzJUGRECbwetx5Cy3BQP_hCHOdqAdqdBfSKyUQwxLpJJLGrXi_uPTm2NLKn19i',
                #     'sgcookie': 'E1003SPW8GLYK1h1JSPuDtsWj%2BRUfcdScMMELTEgntdA8gUL8jBP6A%2FNdboy6gkOaXqPqMfWZ4pDm8%2F8y67DAT2YyXEGgIPKriLaP3KRUtQrBvY%3D',
                #     'tfstk': 'fxqZg89Eor4eA6jl1Ao2Ylpt4Gftmcf53oGjn-2mCfcgC-Dq0WN4CqfThWl06Wd6fc210rPSOStbCS9TJ7wkfl_tcnosDmf5NgsSBRnxmV-vqolTKJHmnF6dDRetDpILjVB3BIkL0VzmmSm3KYHmmC00iHxn9xHDsxxGL9kxthcmmnmHKYkriCVmm9yn9xA9m40XqAgGeAe0o1fVOVhuIfvHKyDyNbyign-VhAuw8Rcemnq3RXMsbfCwQbz7eoPattxmgy4QEXPhnnc4-rqsWmIyEnHnMfEY7IYmSnMEN9WEVMjVfZ9P3ELvkVFtLb6nUELxSvHEN9WekE3T6vl5KY5..',
                #     '_m_h5_tk': inner_cookies.get("_m_h5_tk"),
                #     '_m_h5_tk_enc': inner_cookies.get("_m_h5_tk_enc"),
                # },
                cookies={
                    # 'csg': '65eb8881',
                    # '_hvn_login': '18',
                    # 'munb': '2219122728592',
                    # 'usercode': '536207651',
                    # '_samesite_flag_': 'true',
                    # 'havanaId': '2219122728592',
                    # '_tb_token_': '733e3fb7689de',
                    # 't': '90c92e61ca34b9175dc77a3fff3bd0f9',
                    # 'dm_nickname': '%E9%BA%A6%E5%AD%90ak2hm',
                    # 'cookie2': '16b917d789757c4bf097659b2645b32c',
                    # 'isg': 'BDc3n5HRHGWPCZjoDbwurrW3xi2B_AteVqbVcInkaIZqOFN6kc2rrpZSHphm0OPW',
                    # 'sgcookie': 'E100zyPQRZoZ0%2F9pOQ5s7TQuJTY8iHoRmRWMKcCcmIhC7akyJfdcyivyfYTLGAb5F6dpyT3Wqz%2BHABoZuTySIhaCQb9%2BcDqre3L4XKTWnPBe3QY%3D',
                    # 'tfstk': 'futmCz08d_NQMlalE4Sj7-6bck3RS-s16CEO6GCZz_55kNlslhjMM_KAWi5YICveCsJA6xtMrI9FkGKMClXwQCMf6xgJhKs1bXhpjDpXhrzt6wMdgLWyFt22E0DeKKs1bXe8b2nHhBRbCh-NbYjPItyVboSN4YXGK1SNgNPzz95Pb1RNg_zPhOWVQl5V4YX1a1SNbUQx86SNS3lY6pfb-9l9JtbcslCuj-MOeZfe3MGEZ3qfo6JVZlcdO3LPa9xr1SC6qL-VCQo8mGvPIBj2rbrDsK8B19RqqSWDupvdrhGUjTTyGaBDrAzPgp5V0_xsCl12kd-OSnlUBs-XM3bBfScR6epJ0aAEwuA1SE8F0hcn4gzTzyJlSl6rB3z_5ZW5E6IJ3YvHTuDeNYDu8F_VFTkqEY4_5ZW5E6HoEy81uT6r3',
                    '_m_h5_tk': inner_cookies.get("_m_h5_tk"),
                    '_m_h5_tk_enc': inner_cookies.get("_m_h5_tk_enc"),
                    'cookie2': inner_cookies.get("cookie2"),
                    'sgcookie': inner_cookies.get("sgcookie"),
                    # '_m_h5_tk': 'd0777ba711abbe09eee2b410311a4dca_1735116601617',
                    # '_m_h5_tk_enc': '9451cacaac912223084d05a9801d5a89',
                },
                proxies=self._proxy,
                verify=False,
                timeout=10
            )
        return inner_request
