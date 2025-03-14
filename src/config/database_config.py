import os
from typing import Dict, Any
from dotenv import load_dotenv
from src.server.core.confing import settings

# 获取当前环境变量，默认为开发环境
def get_database_config():
    """根据当前环境获取数据库配置"""
    env = os.getenv("ENV", "development").lower()
    print(f"database_config.py---- ENV: {env}")
    print(f"database_config.py---- settings.DB_NAME: {settings.DB_NAME}")
    print(f"database_config.py---- settings.DB_CHARSET: {settings.Config.env_file}")
    return {
        "driver": settings.DB_DRIVER,
        "username": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "database": settings.DB_NAME,
        "charset": settings.DB_CHARSET,
        "echo": settings.DB_ECHO,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_timeout": settings.DB_POOL_TIMEOUT,

    }


def get_database_url() -> str:
    """获取当前环境的数据库URL"""
    config = get_database_config()
    return f"{config['driver']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"

# 导出数据库URL供SQLAlchemy和Alembic使用
DATABASE_URL = get_database_url()



# import os
# from typing import Dict, Any
# from dotenv import load_dotenv

# # 加载 .env 文件
# load_dotenv()

# # 获取当前环境变量，默认为开发环境
# ENV = os.getenv("ENV", "development")
# print('ENV:', ENV)
# # 数据库配置
# DATABASE_CONFIG = {
#     "development": {
#         "driver": os.getenv("DEV_DB_DRIVER", "mysql+mysqlconnector"),
#         "username": os.getenv("DEV_DB_USER", "root"),
#         "password": os.getenv("DEV_DB_PASSWORD", "aa123456"),
#         "host": os.getenv("DEV_DB_HOST", "localhost"),
#         "port": os.getenv("DEV_DB_PORT", "3306"),
#         "database": os.getenv("DEV_DB_NAME", "ticket_monitor_db"),
#         "charset": "utf8mb4",
#         "echo": True,
#         "pool_size": 5,
#         "max_overflow": 10,
#         "pool_recycle": 3600,
#     },
#     "production": {
#         "driver": os.getenv("PROD_DB_DRIVER", "mysql+mysqlconnector"),
#         "username": os.getenv("PROD_DB_USER", "root"),
#         "password": os.getenv("PROD_DB_PASSWORD", "aa123456"),
#         "host": os.getenv("PROD_DB_HOST", "localhost"),
#         "port": os.getenv("PROD_DB_PORT", "3306"),
#         "database": os.getenv("PROD_DB_NAME", "ticket_monitor_db_prod"),
#         "charset": "utf8mb4",
#         "echo": False,
#         "pool_size": 10,
#         "max_overflow": 20,
#         "pool_recycle": 3600,
#     },
#     "test": {
#         "driver": os.getenv("TEST_DB_DRIVER", "mysql+mysqlconnector"),
#         "username": os.getenv("TEST_DB_USER", "root"),
#         "password": os.getenv("TEST_DB_PASSWORD", "aa123456"),
#         "host": os.getenv("TEST_DB_HOST", "localhost"),
#         "port": os.getenv("TEST_DB_PORT", "3306"),
#         "database": os.getenv("TEST_DB_NAME", "ticket_monitor_db_test"),
#         "charset": "utf8mb4",
#         "echo": True,
#         "pool_size": 5,
#         "max_overflow": 10,
#         "pool_recycle": 3600,
#     }
# }

# def get_database_config() -> Dict[str, Any]:
#     """获取当前环境的数据库配置"""
#     return DATABASE_CONFIG[ENV]

# def get_database_url() -> str:
#     """获取当前环境的数据库URL"""
#     config = get_database_config()
#     return f"{config['driver']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"

# # 导出数据库URL供SQLAlchemy和Alembic使用
# DATABASE_URL = get_database_url()
# print('DATABASE_URL:', DATABASE_URL)