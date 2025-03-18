
# import logging
# from typing import Optional, Dict, Any
# from threading import Thread
# from src.sql.monitor.monitor_db_operate import MonitorDbOperate
# from src.server.untiles import thread_timer, retry_on_exception
# import time
# from src.sql.models import UserTicketMonitor
# import json
# import hashlib
# from src.sql.sqlalchemy_db import get_sqlalchemy_db
# from typing import List
# from sqlalchemy import func
# from datetime import datetime

# logger = logging.getLogger(__name__)

# class NewDBDataMonitor:
#     def __init__(self, callback_func: callable):
#         self.callback_func = callback_func # 回调函数
#         self.is_running = False # 是否正在运行
#         self.monitor_thread: Optional[Thread] = None # 监控线程
#         self.last_monitor_listids_hash: Optional[str] = None # 上次监控的列表哈希值
#         self.last_record_count: int = 0  # 记录上次查询的记录数量
#     # 检查user_show_monitor表中是否存在数据
#     def _check_user_show_monitor(self):
#         """检查监控列表哈希值是否发生变化
        
#         Returns:
#             bool: 如果哈希值发生变化返回 True，否则返回 False
#         """
#         try:
#             with get_sqlalchemy_db() as db:
#                 # 每次都重新获取数据库连接，避免使用缓存
#                 # 使用count查询获取当前记录数，这样更轻量级
#                 current_count = db.query(func.count(UserTicketMonitor.monitor_ticket_id)).scalar()
#                 # 如果记录数发生变化，说明有新增或删除
#                 if current_count != self.last_record_count:
#                     logger.info(f"检测到记录数变化: {self.last_record_count} -> {current_count}")
#                     self.last_record_count = current_count
#                     return True
#                 # 如果记录数没变，再检查具体内容是否变化
#                 # 获取所有记录的ID并排序
#                 user_ticket_monitor_exist = db.query(UserTicketMonitor).all()
#                 if not user_ticket_monitor_exist:
#                     logger.info("没有监控记录")
#                     self.last_record_count = 0
#                     self.last_monitor_listids_hash = None
#                     return False
#                 # 获取所有记录ID和更新时间，确保能检测到记录内容的变化
#                 monitor_data = [(monitor.monitor_ticket_id, str(monitor.updated_at)) 
#                             for monitor in user_ticket_monitor_exist]
#                 monitor_data.sort()  # 排序确保顺序一致
#                 # 生成哈希值
#                 monitor_data_str = json.dumps(monitor_data)
#                 current_hash = hashlib.md5(monitor_data_str.encode()).hexdigest()
#                 logger.debug(f"当前哈希值: {current_hash}")
#                 logger.debug(f"上次哈希值: {self.last_monitor_listids_hash}")
#                 # 首次运行或哈希值变化
#                 if self.last_monitor_listids_hash is None:
#                     self.last_monitor_listids_hash = current_hash
#                     return True
                    
#                 if current_hash != self.last_monitor_listids_hash:
#                     logger.info("检测到记录内容变化")
#                     self.last_monitor_listids_hash = current_hash
#                     return True
                    
#                 return False

#             # # 从user_ticket_monitors表中拿到所有的monitor_ticket_id，跟之前的做对比看看是否没有变
#             # user_ticket_monitor_exist: List[UserTicketMonitor] = self.sqlalchemy_db.query(UserTicketMonitor).all()
#             # print('user_ticket_monitor_exist', user_ticket_monitor_exist)
#             # if not user_ticket_monitor_exist:
#             #     print('user_ticket_monitor_exist is None')
#             #     return False
#             # monitor_ticket_ids = [monitor.monitor_ticket_id for monitor in user_ticket_monitor_exist]
#             # monitor_ids_str = json.dumps(monitor_ticket_ids, sort_keys=True)
#             # current_hash = hashlib.md5(monitor_ids_str.encode()).hexdigest()
#             # print('current_hash', current_hash)
#             # print('self.last_monitor_listids_hash', self.last_monitor_listids_hash)
#             # if self.last_monitor_listids_hash is None:
#             #     self.last_monitor_listids_hash = current_hash
#             #     return True
#             # if current_hash != self.last_monitor_listids_hash:
#             #     self.last_monitor_listids_hash = current_hash
#             #     return True
#             # return False
#         except Exception as e:
#             logger.error(f"检查监控列表哈希值失败: {e}")
#             raise
#     # 线程用时+重试
#     @thread_timer
#     @retry_on_exception(max_retries=3)
#     def _db_monitor_loop(self):
#         """监控循环"""
#         while self.is_running:
#             try:
#                 if self._check_user_show_monitor():
#                     logger.info("检测到 user_show_monitor 有数据，调用票务监控接口")
#                     self.callback_func()
#                 # 转换成正常时间
#                 print('循环检查的时间', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#                 time.sleep(10)  # 每20秒检查一次
#             except Exception as e:
#                 logger.error(f"监控循环发生错误: {e}")
#                 time.sleep(5)  # 发生错误时等待较长时间再重试
#     def start_monitor(self):
#         """启动监控"""
#         if not self.is_running:
#             self.is_running = True
#             self.monitor_thread = Thread(target=self._db_monitor_loop, daemon=True)
#             self.monitor_thread.start()
#             logger.info("配置文件监控器已启动")
#     def stop(self):
#         """停止监控"""
#         if self.is_running:
#             self.is_running = False
#             if self.monitor_thread:
#                 self.monitor_thread.join()
#             logger.info("配置文件监控器已停止")




import logging
from typing import Optional, Dict, Any
from threading import Thread
from src.sql.monitor.monitor_db_operate import MonitorDbOperate
from src.server.untiles import thread_timer, retry_on_exception
import time
from src.sql.models import UserTicketMonitor
import json
import hashlib
from src.sql.sqlalchemy_db import get_sqlalchemy_db
from typing import List
from sqlalchemy import func
from contextlib import contextmanager
from datetime import datetime
import uuid  # 添加uuid模块

logger = logging.getLogger(__name__)

class NewDBDataMonitor:
    # 添加类变量用于实现单例模式
    _instance = None
    _initialized = False
    def __new__(cls, *args, **kwargs):
        # 如果实例不存在，创建一个新实例
        if cls._instance is None:
            logger.info("创建 NewDBDataMonitor 单例")
            cls._instance = super(NewDBDataMonitor, cls).__new__(cls)
        return cls._instance
    def __init__(self, callback_func: callable):
        # 避免重复初始化
        if not NewDBDataMonitor._initialized:
            self.callback_func = callback_func # 回调函数
            self.is_running = False # 是否正在运行
            self.monitor_thread: Optional[Thread] = None # 监控线程
            self.last_monitor_listids_hash: Optional[str] = None # 上次监控的列表哈希值
            self.last_record_count: int = 0  # 记录上次查询的记录数量
            self.instance_id = str(uuid.uuid4())[:8]  # 生成唯一实例ID
            logger.info(f"创建监控实例 ID: {self.instance_id}")
            NewDBDataMonitor._initialized = True
        else:
            # 如果是第二次初始化，检查callback_func是否变化
            if self.callback_func != callback_func:
                logger.warning(f"尝试使用不同的回调函数重新初始化监控实例，但将被忽略")
            logger.info(f"复用已存在的监控实例 ID: {self.instance_id}")
    
    
    # 检查user_show_monitor表中是否存在数据
    def _check_user_show_monitor(self):
        """检查监控列表哈希值是否发生变化
        
        Returns:
            bool: 如果哈希值发生变化返回 True，否则返回 False
        """
        start_time = datetime.now()
        logger.debug(f"[实例 {self.instance_id}] 开始检查: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
        
        try:
            # 使用上下文管理器确保会话正确关闭
            with get_sqlalchemy_db() as db:
                # 使用count查询获取当前记录数，这样更轻量级
                current_count = db.query(func.count(UserTicketMonitor.monitor_ticket_id)).scalar()
                
                # 如果记录数发生变化，说明有新增或删除
                if current_count != self.last_record_count:
                    logger.info(f"[实例 {self.instance_id}] 检测到记录数变化: {self.last_record_count} -> {current_count}")
                    self.last_record_count = current_count
                    return True
                
                # 如果记录数没变且为0，则不需要进一步检查
                if current_count == 0:
                    return False
                
                # 获取所有记录的ID并排序
                user_ticket_monitor_exist = db.query(
                    UserTicketMonitor.monitor_ticket_id, 
                    UserTicketMonitor.updated_at
                ).all()
                
                # 获取所有记录ID和更新时间，确保能检测到记录内容的变化
                monitor_data = [(str(monitor.monitor_ticket_id), str(monitor.updated_at)) 
                               for monitor in user_ticket_monitor_exist]
                monitor_data.sort()  # 排序确保顺序一致
                
                # 生成哈希值
                monitor_data_str = json.dumps(monitor_data)
                current_hash = hashlib.md5(monitor_data_str.encode()).hexdigest()
                
                # 首次运行或哈希值变化
                if self.last_monitor_listids_hash is None:
                    self.last_monitor_listids_hash = current_hash
                    return True
                    
                if current_hash != self.last_monitor_listids_hash:
                    logger.info(f"[实例 {self.instance_id}] 检测到记录内容变化")
                    self.last_monitor_listids_hash = current_hash
                    return True
                    
                return False
        except Exception as e:
            logger.error(f"[实例 {self.instance_id}] 检查监控列表哈希值失败: {e}")
            # 出错时等待一段时间再重试
            time.sleep(5)
            raise
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.debug(f"[实例 {self.instance_id}] 检查完成: {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')}, 耗时: {duration}秒")
    
    # 线程用时+重试
    @thread_timer
    @retry_on_exception(max_retries=3)
    def _db_monitor_loop(self):
        """监控循环"""
        logger.info(f"[实例 {self.instance_id}] 监控循环启动")
        loop_count = 0
        
        while self.is_running:
            loop_count += 1
            loop_start_time = datetime.now()
            logger.info(f"[实例 {self.instance_id}] 循环 #{loop_count} 开始: {loop_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                has_changes = self._check_user_show_monitor()
                if has_changes:
                    logger.info(f"[实例 {self.instance_id}] 检测到 user_ticket_monitor 有变化，调用票务监控接口")
                    self.callback_func()
                
                # 计算实际需要休眠的时间
                elapsed = (datetime.now() - loop_start_time).total_seconds()
                sleep_time = max(20 - elapsed, 0)  # 确保总循环时间为20秒
                
                logger.info(f"[实例 {self.instance_id}] 循环 #{loop_count} 执行耗时: {elapsed:.2f}秒, 将休眠: {sleep_time:.2f}秒")
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
                loop_end_time = datetime.now()
                total_time = (loop_end_time - loop_start_time).total_seconds()
                logger.info(f"[实例 {self.instance_id}] 循环 #{loop_count} 结束: {loop_end_time.strftime('%Y-%m-%d %H:%M:%S')}, 总耗时: {total_time:.2f}秒")
                
            except Exception as e:
                logger.error(f"[实例 {self.instance_id}] 监控循环发生错误: {e}")
                time.sleep(15)  # 发生错误时等待较长时间再重试
    
    def start_monitor(self):
        """启动监控"""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread = Thread(target=self._db_monitor_loop, daemon=True, name=f"DBMonitor-{self.instance_id}")
            self.monitor_thread.start()
            logger.info(f"[实例 {self.instance_id}] 数据库监控器已启动")
    
    def stop(self):
        """停止监控"""
        if self.is_running:
            logger.info(f"[实例 {self.instance_id}] 正在停止数据库监控器")
            self.is_running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
                if self.monitor_thread.is_alive():
                    logger.warning(f"[实例 {self.instance_id}] 监控线程未能在5秒内停止")
                else:
                    logger.info(f"[实例 {self.instance_id}] 监控线程已成功停止")
            logger.info(f"[实例 {self.instance_id}] 数据库监控器已停止")