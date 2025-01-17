import threading
import logging
logger = logging.getLogger(__name__)
class MonitorThreadManager:
    def __init__(self):
        self.current_thread = None
        self.is_running = False

    def start_monitor(self, target_func, args=None):
        """
        启动监控线程
        
        Args:
            target_func: 要在线程中执行的函数
        """
        try:
            print('self.is_running------step1', self.is_running)
            if self.is_running and self.current_thread and self.current_thread.is_alive():
                return
            print('self.is_running------step2', self.is_running)
            # # 如果已有线程在运行，先停止它
            # self.stop_monitor()
            # 创建新的线程
            self.is_running = True
            self.current_thread = threading.Thread(
                target=target_func,
                daemon=True,
                args=args
            )
            self.current_thread.start()
            logger.info("监控线程已启动")
            
        except Exception as e:
            logger.error(f"启动监控线程失败: {e}")
            self.is_running = False
            raise

    def stop_monitor(self):
        """停止监控线程"""
        if self.current_thread and self.current_thread.is_alive():
            self.is_running = False
            self.current_thread.join(timeout=2)  # 等待线程结束，最多等待2秒
            self.current_thread = None
            logger.info("监控线程已停止")