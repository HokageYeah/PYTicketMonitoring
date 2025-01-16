import json
import time
import logging
import hashlib
from pathlib import Path
from threading import Thread
from typing import Optional, Dict, Any

class DBConfigMonitor:
    def __init__(self, config_path: str, callback_func: callable):
        """
        初始化配置文件监控器
        
        Args:
            config_path: db_config.json 文件的路径
            callback_func: 当配置发生变化时要调用的回调函数
        """
        self.config_path = Path(config_path)
        self.callback_func = callback_func
        self.last_monitor_list_hash: Optional[str] = None
        self.is_running = False
        self.monitor_thread: Optional[Thread] = None
        self._initialize()

    def _initialize(self):
        """初始化，读取配置文件并计算初始哈希值"""
        try:
            self._update_monitor_list_hash()
        except Exception as e:
            logging.error(f"初始化配置文件监控器失败: {e}")
            raise

    def _read_config(self) -> Dict[str, Any]:
        """读取配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"读取配置文件失败: {e}")
            raise

    def _calculate_monitor_list_hash(self, config_data: Dict[str, Any]) -> str:
        """计算 monitor_list 的哈希值"""
        try:
            # 获取所有平台的 monitor_list
            monitor_lists = []
            for platform_data in config_data.values():
                if 'monitor_list' in platform_data:
                    monitor_lists.append(platform_data['monitor_list'])
            
            # 将 monitor_lists 转换为字符串并计算哈希值
            monitor_lists_str = json.dumps(monitor_lists, sort_keys=True)
            return hashlib.md5(monitor_lists_str.encode()).hexdigest()
        except Exception as e:
            logging.error(f"计算 monitor_list 哈希值失败: {e}")
            raise

    def _update_monitor_list_hash(self) -> bool:
        """
        更新 monitor_list 的哈希值
        
        Returns:
            bool: 如果哈希值发生变化返回 True，否则返回 False
        """
        try:
            config_data = self._read_config()
            current_hash = self._calculate_monitor_list_hash(config_data)
            
            if self.last_monitor_list_hash is None:
                self.last_monitor_list_hash = current_hash
                return False
                
            if current_hash != self.last_monitor_list_hash:
                self.last_monitor_list_hash = current_hash
                return True
                
            return False
        except Exception as e:
            logging.error(f"更新 monitor_list 哈希值失败: {e}")
            raise

    def _monitor_loop(self):
        """监控循环"""
        while self.is_running:
            try:
                if self._update_monitor_list_hash():
                    logging.info("检测到 monitor_list 发生变化")
                    self.callback_func()
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                logging.error(f"监控循环发生错误: {e}")
                time.sleep(5)  # 发生错误时等待较长时间再重试

    def start(self):
        """启动监控"""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logging.info("配置文件监控器已启动")

    def stop(self):
        """停止监控"""
        if self.is_running:
            self.is_running = False
            if self.monitor_thread:
                self.monitor_thread.join()
            logging.info("配置文件监控器已停止")

# 使用示例
def monitor_tickets():
    """余票监控的回调函数"""
    logging.info("开始执行余票监控...")
    # 在这里实现余票监控的逻辑
    pass

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    # 创建配置文件监控器实例
    config_monitor = DBConfigMonitor(
        config_path="path/to/db_config.json",
        callback_func=monitor_tickets
    )

    try:
        # 启动监控
        config_monitor.start()
        
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 优雅地停止监控
        config_monitor.stop()