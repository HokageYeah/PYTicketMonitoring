import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from src.server.core.confing import settings

# 设置日志
def setup_logging():
    # 在server文件下创建logs目录
    logs_dir = os.path.join(Path(__file__).resolve().parent, '..', 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # 设置日志级别
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # 设置日志格式
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s.%(msecs)03d [%(filename)s:%(lineno)d] : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            RotatingFileHandler(
                os.path.join(logs_dir, 'server.log'),
                maxBytes=1024*1024,
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    # 设置一些第三方库的日志级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
