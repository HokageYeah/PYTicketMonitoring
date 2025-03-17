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
from collections import defaultdict
from src.sql.models import Show, Performance, TicketPrice, UserShowMonitor, UserTicketMonitor
from sqlalchemy.orm import joinedload
from src.sql.sqlalchemy_db import get_sqlalchemy_db
from sqlalchemy import delete, not_, and_, or_
class New_Ticket_Monitor:
    def __init__(self):
        self.db_config = {}
        self.damaiServe = None
        self.sqlalchemy_db = None
        self.monitor_thread_manager = None
        self.semaphore = asyncio.Semaphore(10)  # 限制并发请求的数量
        self.wx_notice = WX_Notice()
        self.access_token = ''
        self.delete_monitor_list = []
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
        notification_content = f"\n当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n演唱会名称：{show_name}\n演唱会场次时间：{ticket_perform.get('perform_name')}\n演唱会地点：{venue_city_name} {venue_name}\n演唱会票价：{price_name}\n已回流，请及时购票！通知人：{wx_token}\n监控持续时间：{deadline}\n"
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
        self.access_token = self.wx_notice.get_access_token()
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
        # return
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
        self.delete_monitor_list = []
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
                        self.delete_monitor_list.append({
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
                                    print('show_id_index------', show_id_index)
                                    print('perform_index------', perform_index)
                                    print('can_buy_list------', can_buy_list)
                                    # can_buy_list[show_id_index].get('ticket_perform')[perform_index].update(ticket_perform_str)
                                    can_buy_list[show_id_index].get('ticket_perform')[perform_index:perform_index+1] = [ticket_perform_str]
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
                    # 需要通知的wx_token 此处代码先注释掉，因为微信的接口调用失败
                    # self.send_notification(delete_item, {
                    #     "show_name": show_name,
                    #     "venue_city_name": venue_city_name,
                    #     "venue_name": venue_name,
                    # }, delete_ticket_perform_index, delete_sku_perform_index)
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
                for delete_monitor_item in self.delete_monitor_list:
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
                    self.access_token = self.wx_notice.get_access_token()
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
    def get_db_config(self):
        # 读取数据库 shows，performances，ticket_prices，user_show_monitors，user_ticket_monitors
        # 最终结果字典
        result = defaultdict(lambda: {"monitor_list": []})
        with get_sqlalchemy_db() as db:
            self.sqlalchemy_db = db
            # 查询所有平台分类
            print('self.sqlalchemy_db------', self.sqlalchemy_db)
            platforms = self.sqlalchemy_db.query(Show.platform).distinct().all()
            print('platforms------', platforms)
            for (platform,) in platforms:
                # 查询当前平台的所有演出及关联数据
                show: Show = self.sqlalchemy_db.query(Show).options(joinedload(Show.user_show_monitors).joinedload(UserShowMonitor.ticket_monitors)).filter(Show.platform == platform).all()
                platform_data = []
                for item in show:
                    show_entry = {
                        "show_id": item.show_id,
                        "show_name": item.show_name,
                        "venue_city_name": item.venue_city_name,
                        "venue_name": item.venue_name,
                        "monitor_person": []
                    }
                    # 按用户分组监控记录
                    user_monitor_map = defaultdict(list)
                    for um in item.user_show_monitors:
                        user_monitor_map[um.wx_token].append(um)
                    # 处理每个用户的监控记录
                    for wx_token, monitors in user_monitor_map.items():
                        person_entry = {
                            "wx_token": wx_token,
                            "deadline": None,
                            "ticket_perform": []
                        }
                        print('person_entry------', person_entry)
                        # 合并同一用户对同一演出的多个监控
                        perform_map = defaultdict(lambda: {"sku_list": []})
                        latest_deadline = datetime.min
                        for monitor in monitors:
                             # 更新最晚截止时间
                            if monitor.deadline > latest_deadline:
                                latest_deadline = monitor.deadline
                                person_entry["deadline"] = latest_deadline.strftime("%Y-%m-%d %H:%M:%S")
                            # 收集场次和票种信息
                            for ticket_monitor in monitor.ticket_monitors:
                                performance = ticket_monitor.performance
                                ticket_price = ticket_monitor.ticket_price
                                perform_entry = perform_map[ticket_monitor.perform_id]
                                if not perform_entry.get("perform_id"): 
                                    perform_entry.update({
                                        "perform_id": performance.perform_id,
                                        "perform_name": performance.perform_name
                                    })
                                sku_entry = {
                                    "sku_id": ticket_price.sku_id,
                                    "price_id": ticket_price.price_id,
                                    "price_name": ticket_price.price_name
                                }
                                if sku_entry not in perform_entry["sku_list"]:
                                    perform_entry["sku_list"].append(sku_entry)
                            # 填充场次数据
                        person_entry["ticket_perform"] = list(perform_map.values())
                        show_entry["monitor_person"].append(person_entry)
                    platform_data.append(show_entry)
                result[platform]["monitor_list"] = platform_data
            self.db_config = json.loads(json.dumps(result, ensure_ascii=False))
            print('监控整理数据result查看------', self.db_config)
            print('监控整理数据result查看------end')
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
    # 将数据还原到数据库中
    def update_db_config(self):
        '''
        graph TD
        A[删除不存在的监控详情] --> B[删除孤立的用户监控]
        B --> C[删除无关联的票种]
        C --> D[删除无用的场次]
        D --> E[删除废弃的演出]
        '''
        print('监控整理数据result查看-------更新', self.db_config)
        print('监控整理数据result查看-------删除', self.delete_monitor_list)
        with get_sqlalchemy_db() as db:
            self.sqlalchemy_db = db
            data_to_save = self.convert_params_to_dict(self.db_config)
            # 说明监控列表不为空，需要将monitor_list中的数据，更新到user_show_monitors表中
            result = restore_data(self.sqlalchemy_db, data_to_save)
            print('监控整理数据result查看-------更新---result------', result)
            # for platform, data in data_to_save.items():
            #     print('监控整理数据result查看-------更新---platform------', platform)
            #     print('监控整理数据result查看-------更新---data------', data)
            #     monitor_list = data.get('monitor_list', [])
            #     if len(monitor_list) <= 0:
            #         # 说明监控列表为空，需要show表中，platform一样的数据，
            #         show_list = self.sqlalchemy_db.query(Show).filter(Show.platform == platform).delete(synchronize_session='fetch')
            #         self.sqlalchemy_db.commit()  # 提交事务
            #         print(f"已删除 platform 为 {platform} 的所有 show 数据")
            #     else:
            #         # 说明监控列表不为空，需要将monitor_list中的数据，更新到user_show_monitors表中
            #         restore_data(self.sqlalchemy_db, data_to_save)

def restore_data(session: any, json_data: dict):
    try:
        deleted_counts = {
            "shows": 0,
            "performs": 0,
            "skus": 0,
            "user_monitors": 0,
            "monitor_details": 0
        }
        print('restore_data------json_data------', json_data)
        for platform, platform_data in json_data.items():
            print('restore_data------platform------', platform)
            print('restore_data------platform_data------', platform_data)
            # ================== 1. 准备所有需要保留的标识 ==================
            keep_show_ids = set()
            keep_perform_ids = set()
            keep_sku_ids = set()
            keep_wx_tokens = set()
            keep_monitor_details = set()

            # 收集需要保留的ID
            for show_info in platform_data["monitor_list"]:
                show_id = show_info["show_id"]
                keep_show_ids.add(show_id)

                for person in show_info["monitor_person"]:
                    wx_token = person["wx_token"]
                    keep_wx_tokens.add((wx_token, show_id))

                    for perform in person["ticket_perform"]:
                        perform_id = perform["perform_id"]
                        keep_perform_ids.add((show_id, perform_id))

                        for sku in perform["sku_list"]:
                            sku_id = sku["sku_id"]
                            keep_sku_ids.add((perform_id, sku_id))
                            keep_monitor_details.add(
                                (wx_token, show_id, perform_id, sku_id)
                            )

            # ================== 2. 删除不再需要的数据 ==================
            # 删除监控详情
            print('keep_monitor_details------', keep_monitor_details)
            if keep_monitor_details:
                delete_conditions = or_(
                    and_(
                        UserTicketMonitor.user_show_monitor_id == UserShowMonitor.monitor_id,
                        UserShowMonitor.wx_token == tuple_[0],
                        UserShowMonitor.show_id == tuple_[1],
                        UserTicketMonitor.perform_id == tuple_[2],
                        UserTicketMonitor.sku_id == tuple_[3]
                    )
                    for tuple_ in keep_monitor_details
                )
                print('keep_monitor_details------delete_conditions------', delete_conditions)
                deleted_counts["monitor_details"] += session.query(UserTicketMonitor).filter(
                    not_(delete_conditions)
                ).delete(synchronize_session=False)
                print('keep_monitor_details------deleted_counts------', deleted_counts)
            # 删除用户监控
            if keep_wx_tokens:
                delete_conditions = or_(
                    and_(
                        UserShowMonitor.wx_token == tuple_[0],
                        UserShowMonitor.show_id == tuple_[1]
                    )
                    for tuple_ in keep_wx_tokens
                )
                print('keep_wx_tokens------delete_conditions------', delete_conditions)
                deleted_counts["user_monitors"] += session.query(UserShowMonitor).filter(
                    UserShowMonitor.platform == platform,
                    not_(delete_conditions)
                ).delete(synchronize_session=False)
                print('keep_wx_tokens------deleted_counts------', deleted_counts)
            # 删除票种
            if keep_sku_ids:
                delete_conditions = or_(
                    and_(
                        TicketPrice.perform_id == tuple_[0],
                        TicketPrice.sku_id == tuple_[1]
                    )
                    for tuple_ in keep_sku_ids
                )
                print('keep_sku_ids------delete_conditions------', delete_conditions)
                deleted_counts["skus"] += session.query(TicketPrice).filter(
                    TicketPrice.platform == platform,
                    not_(delete_conditions)
                ).delete(synchronize_session=False)
                
            # 删除场次
            if keep_perform_ids:
                delete_conditions = or_(
                    and_(
                        Performance.show_id == tuple_[0],
                        Performance.perform_id == tuple_[1]
                    )
                    for tuple_ in keep_perform_ids
                )
                print('keep_perform_ids------delete_conditions------', delete_conditions)
                deleted_counts["performs"] += session.query(Performance).filter(
                    Performance.platform == platform,
                    not_(delete_conditions)
                ).delete(synchronize_session=False)
                print('keep_perform_ids------deleted_counts------', deleted_counts)
            # 删除演出
            if keep_show_ids:
                deleted_counts["shows"] += session.query(Show).filter(
                    Show.platform == platform,
                    Show.show_id.not_in(keep_show_ids)
                ).delete(synchronize_session=False)
                print('keep_show_ids------deleted_counts------', deleted_counts)
            # ================== 3. 插入/更新数据 ==================
            # （保持原有数据插入逻辑，此处省略重复代码）
            # ... [保持之前的插入逻辑]
            # A[开始] --> B[遍历平台数据]
            # B --> C[处理演出表]
            # C --> D[处理场次表]
            # D --> E[处理票种表]
            # E --> F[处理用户监控表]
            # F --> G[处理监控详情]
            # G --> H{还有下一个监控人员?}
            # H -->|是| F
            # H -->|否| I{还有下一个演出?}
            # I -->|是| C
            # I -->|否| J[提交事务]
            # J --> K[结束]

        session.commit()
        return {"status": "success", "deleted": deleted_counts}
    
    except Exception as e:
        session.rollback()
        logging.error(f"数据还原失败: {str(e)}")
        return {"status": "error", "message": str(e)}








# def restore_data(session: Session, json_data: Dict):
#     try:
#         # 遍历每个平台
#         for platform, platform_data in json_data.items():
#             # 处理每个演出
#             for show_info in platform_data["monitor_list"]:
#                 # ================= 1. 处理演出表 =================
#                 show = session.query(Show).get(show_info["show_id"])
#                 if not show:
#                     show = Show(
#                         show_id=show_info["show_id"],
#                         show_name=show_info["show_name"],
#                         venue_city_name=show_info["venue_city_name"],
#                         venue_name=show_info["venue_name"],
#                         platform=platform  # 新增平台字段
#                     )
#                     session.add(show)
#                     session.flush()  # 立即生成ID但不提交事务
                
#                 # ================= 2. 处理场次表 =================
#                 perform_map = {}
#                 for person in show_info["monitor_person"]:
#                     for perform_info in person["ticket_perform"]:
#                         perform_id = perform_info["perform_id"]
#                         if perform_id not in perform_map:
#                             perform = session.query(Perform).get(perform_id)
#                             if not perform:
#                                 perform = Perform(
#                                     perform_id=perform_id,
#                                     perform_name=perform_info["perform_name"],
#                                     show_id=show.show_id
#                                 )
#                                 session.add(perform)
#                             perform_map[perform_id] = perform
                
#                 # ================= 3. 处理票种表 =================
#                 sku_map = {}
#                 for person in show_info["monitor_person"]:
#                     for perform_info in person["ticket_perform"]:
#                         for sku_info in perform_info["sku_list"]:
#                             sku_id = sku_info["sku_id"]
#                             if sku_id not in sku_map:
#                                 sku = session.query(Sku).get(sku_id)
#                                 if not sku:
#                                     sku = Sku(
#                                         sku_id=sku_id,
#                                         price_id=sku_info["price_id"],
#                                         price_name=sku_info["price_name"],
#                                         perform_id=perform_info["perform_id"]
#                                     )
#                                     session.add(sku)
#                                 sku_map[sku_id] = sku
                
#                 session.flush()  # 确保所有依赖关系已生成
                
#                 # ================= 4. 处理用户监控表 =================
#                 for person_info in show_info["monitor_person"]:
#                     # 创建或更新用户监控记录
#                     monitor = session.query(UserMonitor).filter_by(
#                         wx_token=person_info["wx_token"],
#                         show_id=show.show_id
#                     ).first()
                    
#                     deadline = datetime.strptime(
#                         person_info["deadline"], 
#                         "%Y-%m-%d %H:%M:%S"
#                     )
                    
#                     if not monitor:
#                         monitor = UserMonitor(
#                             wx_token=person_info["wx_token"],
#                             show_id=show.show_id,
#                             deadline=deadline,
#                             platform=platform  # 新增平台字段
#                         )
#                         session.add(monitor)
#                         session.flush()  # 生成监控ID
#                     else:
#                         # 更新最晚截止时间
#                         if deadline > monitor.deadline:
#                             monitor.deadline = deadline
                    
#                     # ================= 5. 处理监控详情表 =================
#                     existing_details = {
#                         (d.perform_id, d.sku_id) 
#                         for d in monitor.details
#                     }
                    
#                     # 添加新关联
#                     for perform_info in person_info["ticket_perform"]:
#                         perform_id = perform_info["perform_id"]
#                         for sku_info in perform_info["sku_list"]:
#                             sku_id = sku_info["sku_id"]
                            
#                             if (perform_id, sku_id) not in existing_details:
#                                 detail = MonitorDetail(
#                                     monitor_id=monitor.monitor_id,
#                                     perform_id=perform_id,
#                                     sku_id=sku_id
#                                 )
#                                 session.add(detail)
        
#         session.commit()
#         return {"status": "success", "message": "数据还原完成"}
    
#     except IntegrityError as e:
#         session.rollback()
#         return {"status": "error", "message": f"数据完整性错误: {str(e)}"}
#     except Exception as e:
#         session.rollback()
#         return {"status": "error", "message": f"系统错误: {str(e)}"}