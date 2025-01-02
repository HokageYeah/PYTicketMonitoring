import json
import logging
from pathlib import Path
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import wraps
from typing import Union

from Monitor_DM import DM
from Monitor_FWD import FWD
from Monitor_MY import MY
from Monitor_PXQ import PXQ

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 线程统计类
class ThreadStats:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.stats = defaultdict(lambda: {
                    'success_count': 0,
                    'error_count': 0,
                    'total_time': 0
                })
            return cls._instance
    
    def record_success(self, thread_name, execution_time):
        with self._lock:
            self.stats[thread_name]['success_count'] += 1
            self.stats[thread_name]['total_time'] += execution_time
    
    def record_error(self, thread_name):
        with self._lock:
            self.stats[thread_name]['error_count'] += 1
    
    def get_stats(self):
        return dict(self.stats)

# 装饰器：计时器
def thread_timer(func):
    def wrapper(*args, **kwargs):
        thread_name = threading.current_thread().name
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"线程 {thread_name} 执行耗时: {end_time - start_time:.2f}秒")
        return result
    return wrapper

# 装饰器：异常重试
def retry_on_exception(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            thread_name = threading.current_thread().name
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    logging.error(f"[{thread_name}] 第{retries}次重试，错误：{e}")
                    if retries == max_retries:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

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

# 线程状态监控
def monitor_thread_status():
    while True:
        active_threads = threading.enumerate()
        for thread in active_threads:
            if thread.name.startswith('ticket_monitor_'):
                logging.info(f"线程 {thread.name} 状态: {'活跃' if thread.is_alive() else '已结束'}")
        time.sleep(60)  # 每分钟检查一次

class Runner:
    def __init__(self):
        self.stats = ThreadStats()
        self.threadPool = ThreadPoolExecutor(
            max_workers=100, 
            thread_name_prefix="ticket_monitor_"
        )
        
        # 启动线程状态监控
        threading.Thread(
            target=monitor_thread_status, 
            name="thread_monitor", 
            daemon=True
        ).start()

    @staticmethod
    @thread_timer
    @retry_on_exception(max_retries=3)
    def loop_monitor(monitor: Union[DM, MY, FWD, PXQ], show: dict) -> None:
        current_thread_name = threading.current_thread().name
        
        while datetime.strptime(show.get("deadline"), "%Y-%m-%d %H:%M:%S") > datetime.now():
            try:
                if monitor.monitor():
                    info = f"[{current_thread_name}] {monitor.show_info.get('platform')} {show.get('show_name')} 已回流"
                    logging.info(info)
                    monitor.bark_alert(info)
                    
                    # 记录成功
                    ThreadStats().record_success(current_thread_name, 1)
            except Exception as e:
                logging.error(f"[{current_thread_name}] 发生错误：{e}")
                # 记录错误
                ThreadStats().record_error(current_thread_name)
            finally:
                time.sleep(1)

    def start(self):
        try:
            # 获取当前文件的绝对路径
            current_dir = Path(__file__).resolve().parent
            with open(current_dir / 'config' / "config.json", "r", encoding="utf-8") as file:
                show_list = json.load(file).get("monitor_list")

            for show in show_list:
                task = get_task(show)
                if task:
                    self.threadPool.submit(self.loop_monitor, task, show)
                else:
                    logging.error(f"监控对象 {show.get('show_name')} 加载失败 show_id: {show.get('show_id')}")
            
            self.threadPool.shutdown(wait=True)
            
            # 输出统计信息
            logging.info("线程统计信息：")
            logging.info(self.stats.get_stats())
            
        except Exception as e:
            logging.error(f"程序运行出错：{e}")

if __name__ == '__main__':
    runner = Runner()
    runner.start() 