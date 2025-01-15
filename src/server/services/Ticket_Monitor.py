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
class Ticket_Monitor:
    def __init__(self):
        self.db_config_path = Path(monitor.__file__).resolve().parent / 'config' / 'db_config.json'
        self.db_config = {}
        self.damaiServe = None
        self.get_db_config()
        self.semaphore = asyncio.Semaphore(10)  # 限制并发请求的数量
    # 查询读取获取db_config.json文件中的数据信息
    def get_db_config(self):
        with open(self.db_config_path, 'r', encoding='utf-8') as f:
            # 将f转为字符串 在转换为json
            self.db_config = json.load(f)
    # 更新获取大麦网写入到db_config.json文件中的数据信息
    def update_db_config(self):
        # 将RecordMonitorParams类型转换为字典
        data_to_save = self.convert_params_to_dict(self.db_config)
        with open(self.db_config_path, 'w', encoding='utf-8') as f:
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
        notification_content = f"\n演唱会名称：{show_name}\n演唱会场次时间：{ticket_perform.get('perform_name')}\n演唱会地点：{venue_city_name} {venue_name}\n演唱会票价：{price_name}\n 已回流，请及时购票！通知人：{wx_token}"
        print('notification_content------', notification_content)
        pass
    # 监控演唱会
    def monitor(self, damaiServe):
        self.damaiServe = damaiServe
        logging.info("开始监控演唱会...")
        # 不同平台使用不同线程池
        with ThreadPoolExecutor() as executor:
            future_to_platform = {
                executor.submit(self.monitor_platform, platform, data): platform
                for platform, data in self.db_config.items()
            }
            print('future_to_platform------', future_to_platform)
            # 处理每个平台的监控结果
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    future.result()  # 处理每个平台的监控结果
                except Exception as e:
                    logging.error(f"监控平台 {platform} 时出错: {e}")
    def monitor_platform(self, platform, data):
        # 获取不同平台的监控列表
        monitor_list = data.get("monitor_list", [])
        task_list = []
        can_buy_list = []
        # 如果monitor_list不是空 则以
        while True:
            try:
                for monitor_item in monitor_list:
                    show_id = monitor_item.get('show_id')
                    # 根据show_id获取演唱会信息（并发请求）
                    # task_list.append(self.check_ticket(show_id, monitor_item.get('ticket_perform'), platform))
                    response = self.check_ticket(show_id, '', monitor_item.get('ticket_perform'), platform)
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
                    combined_index_list_item = index.split('-')
                    print('combined_index_list_item------', combined_index_list_item)
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
                self.db_config[platform]['monitor_list'] = monitor_list
                self.update_db_config()
            except Exception as e:
                logging.error(f"监控平台 {platform} 时出错方法: {e}")
            finally:
                time.sleep(2)
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
        print('platform------', platform)
        print('PlatformEnum.DM.value------', PlatformEnum.DM.value)
        response = None
        if platform == PlatformEnum.DM.value:
            response  = self.damaiServe.check_ticket_web(show_id, session_id)
        return response