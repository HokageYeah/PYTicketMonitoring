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
        self.config_path = Path(config_path) # 配置文件路径
        self.callback_func = callback_func # 回调函数
        self.last_monitor_list_hash: Optional[str] = None # 上次监控的列表哈希值
        self.is_running = False # 是否正在运行
        self.monitor_thread: Optional[Thread] = None # 监控线程
        self._initialize() # 初始化
    
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
    def _update_monitor_list_hash(self) -> bool:
        """更新监控列表哈希值
        
        Returns:
            bool: 如果哈希值发生变化返回 True，否则返回 False
        """
        try:
            config_data = self._read_config()
            print('DB_Monitor------config_data------', config_data)
            current_hash = self._calculate_monitor_list_hash(config_data)
            
            if self.last_monitor_list_hash is None:
                self.last_monitor_list_hash = current_hash
                return False
            
            if current_hash != self.last_monitor_list_hash:
                self.last_monitor_list_hash = current_hash
                return True
            
            return False
        except Exception as e:
            logging.error(f"更新监控 moitor_list 列表哈希值失败: {e}")
            raise
    def _calculate_monitor_list_hash(self, config_data: Dict[str, Any]) -> str:
        """计算监控列表哈希值"""
        try:
            monitor_lists = []
            for platform_data in config_data.values():
                if 'monitor_list' in platform_data:
                    monitor_lists.append(platform_data['monitor_list'])
            # 将 monitor_lists 转换为字符串并计算哈希值
            monitor_lists_str = json.dumps(monitor_lists, sort_keys=True)
            return hashlib.md5(monitor_lists_str.encode()).hexdigest()
        except Exception as e:
            logging.error(f"计算监控列表哈希值失败: {e}")
            raise
