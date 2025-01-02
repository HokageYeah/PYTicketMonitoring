import json
import logging
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Union

from Monitor_DM import DM
from Monitor_FWD import FWD
from Monitor_MY import MY
from Monitor_PXQ import PXQ


def get_task(show: dict) -> Union[DM, MY, FWD, PXQ, None]:
    if show.get("platform") == 0:
        return DM(show)
    elif show.get("platform") == 1:
        return MY(show)
    elif show.get("platform") == 2:
        return FWD(show)
    elif show.get("platform") == 3:
        return PXQ(show)
    else:
        return None


class Runner:
    # 创建线程池，最多100个线程同时运行
    threadPool = ThreadPoolExecutor(max_workers=100, thread_name_prefix="ticket_monitor_")

    @staticmethod
    def loop_monitor(monitor: Union[DM, MY, FWD, PXQ], show: dict) -> None:
        # 在截止时间前持续监控
        while datetime.strptime(show.get("deadline"), "%Y-%m-%d %H:%M:%S") > datetime.now():
            try:
                # 如果监控到票
                if monitor.monitor():
                    info = f"{monitor.show_info.get('platform')} {show.get('show_name')} 已回流，请及时购票！"
                    logging.info(info)
                    monitor.bark_alert(info) # 发送提醒
            except Exception as e:
                logging.info(f"发生错误：{e}")
            finally:
                time.sleep(1)

    def start(self):
        # 获取当前文件的绝对路径
        current_dir = Path(__file__).resolve().parent
        file = open(current_dir / 'config' / "config.json", "r", encoding="utf-8")
        print('config.json', file)
        show_list = json.load(file).get("monitor_list")
        file.close()

        for show in show_list:
            task = get_task(show)
            if task:
                # 提交监控任务到线程池
                self.threadPool.submit(self.loop_monitor, task, show)
            else:
                logging.error(f"监控对象 {show.get('show_name')} 加载失败 show_id: {show.get('show_id')}")
        self.threadPool.shutdown(wait=True)


if __name__ == '__main__':
    runner = Runner()
    runner.start()
