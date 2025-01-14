import json
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

class TicketMonitor:
    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        # 读取配置文件
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.db_config = json.load(f)

    def check_ticket(self, platform, show_id, perform_id):
        # 根据平台检查票务的实现
        if platform == "DM":
            url = f"https://api.damai.cn/check_ticket?show_id={show_id}&perform_id={perform_id}"  # 替换为实际的 API URL
        elif platform == "猫眼":
            url = f"https://api.maoyan.com/check_ticket?show_id={show_id}&perform_id={perform_id}"  # 替换为实际的 API URL
        else:
            raise ValueError("不支持的平台")

        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()

    def notify_person(self, wx_token, message):
        # 发送通知的实现
        logging.info(f"通知用户 {wx_token}: {message}")
        # 这里可以实现具体的通知逻辑，比如发送消息到微信

    def monitor_show(self, platform, monitor_item):
        show_id = monitor_item.get('show_id')
        monitor_person = monitor_item.get('monitor_person')

        with ThreadPoolExecutor() as executor:
            future_to_person = {
                executor.submit(self.monitor_person, platform, show_id, person_item): person_item
                for person_item in monitor_person
            }

            for future in as_completed(future_to_person):
                person_item = future_to_person[future]
                try:
                    future.result()  # 处理每个监控人员的结果
                except Exception as e:
                    logging.error(f"监控演出时出错: {e}")

    def monitor_person(self, platform, show_id, person_item):
        ticket_perform = person_item.get('ticket_perform')
        for perform in ticket_perform:
            perform_id = perform.get('perform_id')
            response = self.check_ticket(platform, show_id, perform_id)

            if response.get("ret") == ["SUCCESS::调用成功"]:
                result = json.loads(response.get("data").get("result"))
                for sku_item in result.get("perform").get("skuList"):
                    sku_id = sku_item.get('skuId')
                    skuSalable = sku_item.get('skuSalable')
                    price_id = sku_item.get('price_id')  # 假设有这个字段

                    if skuSalable == "true":  # 如果有票
                        message = f"演出 {perform['perform_name']} 有票，SKU ID: {sku_id}, Price ID: {price_id}"
                        self.notify_person(person_item['wx_token'], message)

                        # 删除已通知的演出通知
                        person_item['ticket_perform'].remove(perform)
                        if not person_item['ticket_perform']:
                            # 如果此人没有剩余的演出通知，删除此人
                            return  # 直接返回，外层会处理删除

    def monitor(self):
        logging.info("开始监控演唱会...")
        with ThreadPoolExecutor() as executor:
            future_to_platform = {
                executor.submit(self.monitor_platform, platform, data): platform
                for platform, data in self.db_config.items()
            }

            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    future.result()  # 处理每个平台的监控结果
                except Exception as e:
                    logging.error(f"监控平台 {platform} 时出错: {e}")

    def monitor_platform(self, platform, data):
        monitor_list = data.get("monitor_list", [])
        for monitor_item in monitor_list:
            self.monitor_show(platform, monitor_item)

# 运行监控
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor = TicketMonitor('src/monitor/config/db_config.json')
    monitor.monitor()