import threading
from collections import defaultdict
import time
import logging
from functools import wraps

# 装饰器：计时器
def thread_timer(func):
    def wrapper(*args, **kwargs):
        print('thread_stats------thread_timer')
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
        print('thread_stats------retry_on_exception')
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

# 线程状态监控
def monitor_thread_status():
    while True:
        active_threads = threading.enumerate()
        for thread in active_threads:
            if thread.name.startswith('ticket_monitor_'):
                logging.info(f"线程 {thread.name} 状态: {'活跃' if thread.is_alive() else '已结束'}")
        time.sleep(60)  # 每分钟检查一次

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