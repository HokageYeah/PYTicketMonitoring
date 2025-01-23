from functools import wraps
from pathlib import Path
import json
from src import monitor
from pydantic import BaseModel
from src.server.schemas.concert import RecordMonitorParams
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.server.schemas.concert import TicketPerform
import asyncio
from src.server.schemas import PlatformEnum
from src.server.schemas.concert import ApiResponseData
import time
import threading
from datetime import datetime
from src.server.untiles import ThreadStats, monitor_thread_status, retry_on_exception, thread_timer
from src.server.untiles.Src_Path import db_config_path
from src.server.untiles.Monitor_Thread_Manager import MonitorThreadManager
from src.server.untiles.WX_Notice import WX_Notice
class Ticket_Monitor:
    def __init__(self):
        self.db_config = {}
        self.damaiServe = None
        self.monitor_thread_manager = None
        self.get_db_config()
        self.semaphore = asyncio.Semaphore(10)  # 限制并发请求的数量
        self.wx_notice = WX_Notice()
        self.access_token = self.wx_notice.get_access_token()
    # 查询读取获取db_config.json文件中的数据信息
    def get_db_config(self):
        with open(db_config_path, 'r', encoding='utf-8') as f:
            # 将f转为字符串 在转换为json
            self.db_config = json.load(f)
    # 更新获取大麦网写入到db_config.json文件中的数据信息
    def update_db_config(self):
        # 将RecordMonitorParams类型转换为字典
        data_to_save = self.convert_params_to_dict(self.db_config)
        with open(db_config_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False)
    # 创建递归函数，将RecordMonitorParams类型转换为字典
    def convert_params_to_dict(self, params: RecordMonitorParams):
         """递归地将字典中的 Pydantic 模型转换为字典"""
         if isinstance(params, dict):
             return {key: self.convert_params_to_dict(value) for key, value in params.items()}
         elif isinstance(params, list):
             return [self.convert_params_to_dict(item) for item in params]
         elif isinstance(params, BaseModel):
             return params.model_dump()
         return params
    # 发送通知的实现
    def send_notification(self, delete_item, send_info, delete_ticket_perform_index, delete_sku_perform_index):
        # 获取需要通知的wx_token
        wx_token = delete_item.get('wx_token')
        # 获取需要通知的deadline
        deadline = delete_item.get('deadline')
        # 获取需要通知的ticket_perform
        ticket_perform = delete_item.get('ticket_perform')[delete_ticket_perform_index]
        # 获取需要通知的perform_id
        perform_id = ticket_perform.get('perform_id')
        sku_list = ticket_perform.get('sku_list')
        # 获取需要通知的sku_id
        sku_id = sku_list[delete_sku_perform_index].get('sku_id')
        # 获取需要通知的price_id
        price_id = sku_list[delete_sku_perform_index].get('price_id')
        # 获取需要通知的price_name
        price_name = sku_list[delete_sku_perform_index].get('price_name')
        # 获取需要通知的show_name
        show_name = send_info.get('show_name')
        # 获取需要通知的venue_city_name
        venue_city_name = send_info.get('venue_city_name')
        # 获取需要通知的venue_name
        venue_name = send_info.get('venue_name')
        # 下面写通知到用户的逻辑
        # 通知文案
        notification_content = f"\n当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n演唱会名称：{show_name}\n演唱会场次时间：{ticket_perform.get('perform_name')}\n演唱会地点：{venue_city_name} {venue_name}\n演唱会票价：{price_name}\n已回流，请及时购票！通知人：{wx_token}\n"
        print('##########################回流票打印开始##########################')
        print(notification_content)
        print('##########################回流票打印结束##########################')
        # 发送通知（发送通知到用户微信公众号）
        notification_content = {
            'datetime': {
                "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "color": "#173177"
            },
            'show_name': {
                "value": show_name,
                "color": "#173177"
            },
            'perform_name': {
                "value": ticket_perform.get('perform_name'),
                "color": "#173177"
            },
            'venue_city_name': {
                "value": venue_city_name,
                "color": "#173177"
            },
            'venue_name': {
                "value": venue_name,
                "color": "#173177"
            },
            'price_name': {
                "value": price_name,
                "color": "#173177"
            }
        }
        # 获取用户微信openid列表
        user_wx_openid_dict = self.wx_notice.get_user_wx_openid_list(self.access_token, '')
        # 发送通知
        for wx_token in user_wx_openid_dict.get('data').get('openid'):
            self.wx_notice.send_public_notice(self.access_token, notification_content, user_wx_code=wx_token, template_id='CPHntQfk-7GchRhjbi22SsXP84Bndjlc4N4Q5oEFTp8')
        pass
    # 监控演唱会
    def monitor(self, damaiServe, thread_manager):
        self.damaiServe = damaiServe
        self.monitor_thread_manager = thread_manager
        logging.info("开始监控演唱会...")
        self.get_db_config()
        # 不同平台使用不同线程池
        with ThreadPoolExecutor(max_workers=20, thread_name_prefix="ticket_monitor_") as executor:
            # ThreadPoolExecutor 中使用 executor.submit 提交了这个协程。executor.submit 适用于普通的同步函数，而不是异步函数。
            future_to_platform = {
                executor.submit(self.monitor_platform, platform, data): platform
                for platform, data in self.db_config.items()
            }
            # print('future_to_platform------', future_to_platform)
            # 处理每个平台的监控结果
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    future.result()  # 处理每个平台的监控结果
                except Exception as e:
                    logging.error(f"监控平台 {platform} 时出错: {e}")
        # 启动线程状态监控
        threading.Thread(target=monitor_thread_status,name='thread_monitor', daemon=True).start()
    # 监控演唱会（异步任务） 
    async def monitor_async(self, damaiServe):
        self.damaiServe = damaiServe
        logging.info("开始监控演唱会...")
        self.get_db_config()
        # 采用异步任务的方式
        tasks = [self.monitor_platform(platform, data) for platform, data in self.db_config.items()]
        # 等待所有任务完成
        await asyncio.gather(*tasks)


    @thread_timer
    @retry_on_exception(max_retries=3)
    def monitor_platform(self, platform, data):
        # 获取不同平台的监控列表
        monitor_list = data.get("monitor_list", [])
        print('monitor_list------', len(monitor_list))
        print('monitor_list------', monitor_list)
        task_list = []
        can_buy_list = []
        delete_monitor_list = []
        start_time = time.time()
        # 如果monitor_list不是空 则以
        # 初始化轮训获取最新数据
        while len(monitor_list) > 0 and self.monitor_thread_manager.is_running:
            try:
                # 每次轮训都要获取最新的数据
                print('combined_index_list------while',len(monitor_list), self.monitor_thread_manager.is_running)
                self.get_db_config()
                monitor_list = self.db_config.get(platform).get('monitor_list')
                for monitor_item in monitor_list:
                    show_id = monitor_item.get('show_id')
                    # 根据show_id获取演唱会信息（并发请求）
                    # task_list.append(self.check_ticket(show_id, monitor_item.get('ticket_perform'), platform))
                    response = self.check_ticket(show_id, '', monitor_item.get('ticket_perform'), platform)
                    if response.get("ret") != ["SUCCESS::调用成功"]:
                        continue
                    if response.get("data").get("result").get("performCalendar") is None:
                        # 代表此演出已下架、删除本场所有监控
                        delete_monitor_list.append({
                            "show_id": show_id,
                            "platform": platform,
                            "ticket_perform": [None] 
                        })
                        continue
                    perform_views = response.get("data").get("result").get("performCalendar").get("performViews")
                    # 获取所有的perform_id
                    perform_id_list = [perform_view.get("performId") for perform_view in perform_views]
                    print('perform_id_list------', perform_id_list)
                    for perform_id in perform_id_list:
                        response = self.check_ticket(show_id, perform_id, monitor_item.get('ticket_perform'), platform)
                        # print('response------new----', response)
                        if response.get("ret") == ["SUCCESS::调用成功"]:
                            result = response.get("data").get("result")
                        # 遍历result
                        for sku_item in result.get("perform").get("skuList"):
                            # 获取sku_item中的sku_id
                            sku_id = sku_item.get('skuId')
                            # 获取sku_item中的skuSalable
                            skuSalable = sku_item.get('skuSalable')
                            perform_id = result.get("perform").get("performId")
                            perform_name = result.get("perform").get("performName")
                            price_id = sku_item.get("priceId")
                            ticket_perform_str = f'{perform_id}-{sku_id}-{price_id}'
                            if skuSalable == "false":
                                continue
                            show_id_index = next((i for i, item in enumerate(can_buy_list) if item.get('show_id') == show_id), -1)
                            if show_id_index == -1:
                                can_buy_list.append({
                                    "show_id": show_id,
                                    "platform": platform,
                                    "ticket_perform": [ticket_perform_str]
                                })
                            else:                
                                perform_index = next((i for i, item in enumerate(can_buy_list[show_id_index].get('ticket_perform')) if item == ticket_perform_str), -1)
                                if perform_index == -1:
                                    can_buy_list[show_id_index].get('ticket_perform').append(ticket_perform_str)
                                else:
                                    can_buy_list[show_id_index].get('ticket_perform')[perform_index].update(ticket_perform_str)
            except Exception as e:
                logging.error(f"监控平台 {platform} 时出错: {e}")
                # 记录错误
                ThreadStats().record_error(threading.current_thread().name)
            # 需要处理的数据下标集合
            combined_index_list = []
            # 根据can_buy_list 找到db_config.json文件中的数据信息
            for index, itemData in enumerate(can_buy_list):
                print('itemData------', itemData)
                monitor_list_item_index = next((i for i, item in enumerate(monitor_list) if item.get('show_id') == itemData.get('show_id')), -1)
                if monitor_list_item_index == -1:
                    continue
                buy_perform_list = itemData.get('ticket_perform')
                monitor_person_list = monitor_list[monitor_list_item_index].get('monitor_person')
                print('monitor_person_list------', monitor_person_list)
                combined_ids = [
                    f"{ticket_perform['perform_id']}-{buy_perform['sku_id']}-{buy_perform['price_id']}::{monitor_list_item_index}-{person_index}-{ticket_perform_index}-{buy_perform_index}"
                    for person_index, person in enumerate(monitor_person_list)
                    for ticket_perform_index, ticket_perform in enumerate(person['ticket_perform'])
                    for buy_perform_index, buy_perform in enumerate(ticket_perform['sku_list'])
                ]
                # combined_ids_str = '\n'.join(combined_ids)
                for combined_ids_str in combined_ids:
                    # 根据::分割，取第一个字符串
                    combined_list = combined_ids_str.split('::')
                    perform_index = next((person_index for person_index, person_item in enumerate(itemData['ticket_perform']) if person_item == combined_list[0]), -1)
                    if perform_index == -1:
                        continue
                    conbined_index = combined_list[1]
                    combined_index_list.append(conbined_index)
            print('combined_index_list------', combined_index_list)
            try:
                for index in combined_index_list:
                    # 此循环表示肯定有回流票了，打印一个分割线
                    combined_index_list_item = index.split('-')
                    delete_monitor_list_item_index = int(combined_index_list_item[0])
                    delete_person_index = int(combined_index_list_item[1])
                    delete_ticket_perform_index = int(combined_index_list_item[2])
                    delete_sku_perform_index = int(combined_index_list_item[3])
                    # 删除 monitor_list 中的数据
                    delete_item = monitor_list[delete_monitor_list_item_index].get('monitor_person')[delete_person_index]
                    show_name = monitor_list[delete_monitor_list_item_index].get('show_name')
                    venue_city_name = monitor_list[delete_monitor_list_item_index].get('venue_city_name')
                    venue_name = monitor_list[delete_monitor_list_item_index].get('venue_name')
                    # 需要通知的wx_token也是需要删除的delete_item
                    # 需要通知的wx_token
                    self.send_notification(delete_item, {
                        "show_name": show_name,
                        "venue_city_name": venue_city_name,
                        "venue_name": venue_name,
                    }, delete_ticket_perform_index, delete_sku_perform_index)
                    # 通知完成后删除通知后的数据
                    monitor_list[delete_monitor_list_item_index].get('monitor_person')[delete_person_index].get('ticket_perform')[delete_ticket_perform_index].get('sku_list')[delete_sku_perform_index] = None
                    if all(item is None for item in monitor_list[delete_monitor_list_item_index].get('monitor_person')[delete_person_index].get('ticket_perform')[delete_ticket_perform_index].get('sku_list')):
                        monitor_list[delete_monitor_list_item_index].get('monitor_person')[delete_person_index].get('ticket_perform')[delete_ticket_perform_index] = None
                    if all(item is None for item in monitor_list[delete_monitor_list_item_index].get('monitor_person')[delete_person_index].get('ticket_perform')):
                        monitor_list[delete_monitor_list_item_index].get('monitor_person')[delete_person_index] = None
                    if all(item is None for item in monitor_list[delete_monitor_list_item_index].get('monitor_person')):
                        monitor_list[delete_monitor_list_item_index] = None
                # 递归删除monitor_list中的None
                monitor_list = self.recursive_delete_none(monitor_list)
                # 根据delete_monitor_list删除monitor_list中的数据
                for delete_monitor_item in delete_monitor_list:
                    delete_show_id = delete_monitor_item.get('show_id')
                    delete_index = next((i for i, item in enumerate(monitor_list) if item.get('show_id') == delete_show_id), -1)
                    if delete_index == -1:
                        continue
                    show_name = monitor_list[delete_index].get('show_name')
                    venue_city_name = monitor_list[delete_index].get('venue_city_name')
                    venue_name = monitor_list[delete_index].get('venue_name')
                    # 通知文案
                    notification_content = f"\n当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n演唱会名称：{show_name}\n演唱会show_id：{delete_show_id}\n已下架，现在删除此条监控\n"
                    print('##########################演唱会已下架打印开始##########################')
                    print(notification_content)
                    print('##########################演唱会已下架打印结束##########################')
                    monitor_list[delete_index] = None
                            # 发送通知（发送通知到用户微信公众号）
                    notification_content = {
                        'datetime': {
                            "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "color": "#173177"
                        },
                        'show_name': {
                            "value": show_name,
                            "color": "#173177"
                        },
                        'delete_show_id': {
                            "value": delete_show_id,
                            "color": "#173177"
                        }
                    }
                    # 获取用户微信openid列表
                    user_wx_openid_dict = self.wx_notice.get_user_wx_openid_list(self.access_token, '')
                    # 发送通知
                    for wx_code in user_wx_openid_dict.get('data').get('openid'):
                        self.wx_notice.send_public_notice(self.access_token, notification_content, user_wx_code=wx_code, template_id='gNM1Hj4yVnpebScA_NZPB6qFwMWSrR2Jb6Ntg7VmFIE')
                # 递归删除monitor_list中的None
                monitor_list = self.recursive_delete_none(monitor_list)
                self.db_config[platform]['monitor_list'] = monitor_list
                self.update_db_config()
                # 记录成功
                ThreadStats().record_success(threading.current_thread().name, time.time() - start_time)
            except Exception as e:
                logging.error(f"监控平台 {platform} 时出错方法: {e}")
                # 记录错误
                ThreadStats().record_error(threading.current_thread().name)
            finally:
                if len(monitor_list) > 0 and self.monitor_thread_manager.is_running:
                    time.sleep(10)
                # 异步任务
                # await asyncio.sleep(2)
        print('self.monitor_thread_manager------', self.monitor_thread_manager)
        print('self.monitor_thread_manager------type----', type(self.monitor_thread_manager))
        if type(self.monitor_thread_manager) == MonitorThreadManager:
            print('self.monitor_thread_manager------input', self.monitor_thread_manager)
            self.monitor_thread_manager.stop_monitor()
        # await asyncio.gather(*task_list)
    # 递归删除monitor_list中的None
    def recursive_delete_none(self, monitor_list):
        if isinstance(monitor_list, list):
            return [self.recursive_delete_none(item) for item in monitor_list if item is not None]
        elif isinstance(monitor_list, dict):
            return {key: self.recursive_delete_none(value) for key, value in monitor_list.items() if value is not None}
        return monitor_list
    # 检查票务情况
    def check_ticket(self, show_id, session_id, ticket_perform: TicketPerform, platform):
        # 获取大麦网监控对象
        logging.info(f"{platform} 监控中")
        response = None
        if platform == PlatformEnum.DM.value:
            response  = self.damaiServe.check_ticket_web(show_id, session_id)
        return response