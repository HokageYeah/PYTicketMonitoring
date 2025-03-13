import os
from typing import Dict, Any
from dotenv import load_dotenv


# 获取当前环境变量，默认为开发环境
ENV = os.getenv("ENV", "development")
print('database_config.py---- ENV:', ENV)
# 数据库配置
DATABASE_CONFIG = {
    "development": {
        "driver": os.getenv("DEV_DB_DRIVER", "mysql+mysqlconnector"),
        "username": os.getenv("DEV_DB_USER", "root"),
        "password": os.getenv("DEV_DB_PASSWORD", "aa123456"),
        "host": os.getenv("DEV_DB_HOST", "localhost"),
        "port": os.getenv("DEV_DB_PORT", "3306"),
        "database": os.getenv("DEV_DB_NAME", "ticket_monitor_db"),
        "charset": "utf8mb4",
        "echo": True,  # 开发环境打印SQL语句
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 3600,
        "pool_timeout": 30,
    },
    "production": {
        "driver": os.getenv("PROD_DB_DRIVER", "mysql+mysqlconnector"),
        "username": os.getenv("PROD_DB_USER", "root"),
        "password": os.getenv("PROD_DB_PASSWORD", "aa123456"),
        "host": os.getenv("PROD_DB_HOST", "localhost"),
        "port": os.getenv("PROD_DB_PORT", "3306"),
        "database": os.getenv("PROD_DB_NAME", "ticket_monitor_db_prod"),
        "charset": "utf8mb4",
        "echo": False,  # 生产环境不打印SQL语句
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 3600,
        "pool_timeout": 30,
    },
    "test": {
        "driver": "mysql+mysqlconnector",
        "username": os.getenv("TEST_DB_USER", "root"),
        "password": os.getenv("TEST_DB_PASSWORD", "aa123456"),
        "host": os.getenv("TEST_DB_HOST", "localhost"),
        "port": os.getenv("TEST_DB_PORT", "3306"),
        "database": os.getenv("TEST_DB_NAME", "ticket_monitor_db_test"),
        "charset": "utf8mb4",
        "echo": True,
        "pool_size": 5,
        "max_overflow": 10,
        "pool_recycle": 3600,
        "pool_timeout": 30,
    }
}

def get_database_config() -> Dict[str, Any]:
    """获取当前环境的数据库配置"""
    return DATABASE_CONFIG[ENV]

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