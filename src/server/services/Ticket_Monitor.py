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
    def send_notification(self):
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
                    print('response------new----', response)
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
                        print('skuSalable------skuSalable', skuSalable)
                        if skuSalable == "false":
                            continue
                        # for item in can_buy_list:
                        #     if item.get('show_id') == show_id:
                        #         for perform_item in item.get('ticket_perform'):
                        #             if perform_item.get('perform_id') == perform_id:
                        #                 for sku_item in perform_item.get('sku_list'):
                        #                     if sku_item.get('sku_id') == sku_id:
                        #                         sku_item.update({
                        #                             "price_id": price_id,
                        #                             'sku_id': sku_id
                        #                         })
                        #                         break
                        #                     else:
                        #                         perform_item.get('sku_list').append({
                        #                             "sku_id": sku_id,
                        #                             "price_id": price_id,
                        #                         })
                        #                 break
                        #             else:
                        #                 item.get('ticket_perform').append({
                        #                     "perform_id": perform_id,
                        #                     "perform_name": perform_name,
                        #                     "sku_list": [
                        #                         {
                        #                             "sku_id": sku_id,
                        #                             "price_id": price_id,
                        #                         }
                        #                     ]
                        #                 })
                        #         break
                        #     else:
                        #         can_buy_list.append({
                        #             "show_id": show_id,
                        #             "platform": platform,
                        #             "ticket_perform": [
                        #                 {
                        #                     "perform_id": perform_id,
                        #                     "perform_name": perform_name,
                        #                     "sku_list": [
                        #                         {
                        #                             "sku_id": sku_id,
                        #                             "price_id": price_id,
                        #                         }
                        #                     ]
                        #                 }
                        #             ]
                        #         })
                        # if len(can_buy_list) <= 0:
                        #     can_buy_list.append({
                        #         "show_id": show_id,
                        #         "platform": platform,
                        #         "ticket_perform": [
                        #             {
                        #                 "perform_id": perform_id,
                        #                 "perform_name": perform_name,
                        #                 "sku_list": [
                        #                     {
                        #                         "sku_id": sku_id,
                        #                         "price_id": price_id,
                        #                     }
                        #                 ]
                        #             }
                        #         ]
                        #     })
                        show_id_index = next((i for i, item in enumerate(can_buy_list) if item.get('show_id') == show_id), -1)
                        if show_id_index == -1:
                            can_buy_list.append({
                                "show_id": show_id,
                                "platform": platform,
                                "ticket_perform": [
                                    {
                                        "perform_id": perform_id,
                                        "perform_name": perform_name,
                                        "sku_list": [
                                            {
                                                "sku_id": sku_id,
                                                "price_id": price_id,
                                            }
                                        ]
                                    }
                                ]
                            })
                        else:
                            perform_id_index = next((i for i, item in enumerate(can_buy_list[show_id_index].get('ticket_perform')) if item.get('perform_id') == perform_id), -1)
                            if perform_id_index == -1:
                                can_buy_list[show_id_index].get('ticket_perform').append({
                                    "perform_id": perform_id,
                                    "perform_name": perform_name,
                                    "sku_list": [
                                        {
                                            "sku_id": sku_id,
                                            "price_id": price_id,
                                        }
                                    ]
                                })
                            else:
                                sku_list_index = next((i for i, item in enumerate(can_buy_list[show_id_index].get('ticket_perform')[perform_id_index].get('sku_list')) if item.get('sku_id') == sku_id), -1)
                                if sku_list_index == -1:
                                    can_buy_list[show_id_index].get('ticket_perform')[perform_id_index].get('sku_list').append({
                                        "sku_id": sku_id,
                                        "price_id": price_id,
                                    })
                                else:
                                    can_buy_list[show_id_index].get('ticket_perform')[perform_id_index].get('sku_list')[sku_list_index].update({
                                        "price_id": price_id,
                                        'sku_id': sku_id
                                    })
        except Exception as e:
            logging.error(f"监控平台 {platform} 时出错: {e}")
        # can_buy_list去重 去掉show_id、sku_id、perform_id、price_id 一样的数组
        # can_buy_list = [dict(t) for t in {tuple(d.items()) for d in can_buy_list}]
        # 根据can_buy_list 找到db_config.json文件中的数据信息
        # for index, itemData in enumerate(can_buy_list):
        #     print('itemData------', itemData)
        #     monitor_list_item_index = next(i for i, item in enumerate(monitor_list) if item.get('show_id') == itemData.get('show_id'))
        #     print('monitor_list_item_index------', monitor_list_item_index)
        print('can_buy_list------', can_buy_list)
        # await asyncio.gather(*task_list)
    # 检查票务情况
    def check_ticket(self, show_id, session_id, ticket_perform: TicketPerform, platform):
        # 获取大麦网监控对象
        logging.info(f"{platform} 监控中")
        print('platform------', platform)
        print('PlatformEnum.DM.value------', PlatformEnum.DM.value)
        print('ticket_perform------', platform == PlatformEnum.DM.value)
        response = None
        if platform == PlatformEnum.DM.value:
            print('response------response----in---1')
            response  = self.damaiServe.check_ticket_web(show_id, session_id)
            print('response------response----in---2')
        return response