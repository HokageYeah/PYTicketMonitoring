from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv
# 获取当前环境
ENV = os.getenv("ENV", "development")
print(f"当前环境: {ENV}")
# 根据环境选择配置文件（老方法，根据文件名去拿文件配置，未使用dotenv库）以下使用dotenv库
# env_file = f".env.{ENV}" if os.path.exists(f".env.{ENV}") else ".env"
# 优先加载 .env 文件
env_file = ".env"
if ENV == "prod":
    env_file = ".env.production"
elif ENV == "test":
    env_file = ".env.test"
elif ENV == "dev":
    env_file = ".env.development"
print(f"加载配置文件: {env_file}")
load_dotenv(env_file)
# 配置类
class Settings(BaseSettings):
    # 应用配置
    # proxy: Optional[str] = None：定义一个名为 proxy 的可选字段，类型为字符串（str），默认值为 None。
    # 这通常用于存储代理服务器的地址。
    PROJECT_NAME: Optional[str] = "演唱会票务监控系统"
    API_V1_STR: Optional[str] = "/api/v1"
    DEBUG: Optional[bool] = True
    # 数据库暂时不配置
    # DATABASE_URL: str = "sqlite:///./concert_monitor.db"

    # 监控配置
    CHECK_INTERVAL: Optional[int] = 300  # 检查间隔（秒）
    REQUEST_TIMEOUT: Optional[int] = 30  # 请求超时时间（秒）
    MAX_RETRIES: Optional[int] = 3      # 最大重试次数

    # 邮件配置
    SMTP_SERVER: Optional[str] = "smtp.gmail.com" # 邮件服务器
    SMTP_PORT: Optional[int] = 587 # 邮件服务器端口
    SMTP_USERNAME: Optional[str] = "" # 邮件服务器用户名
    SMTP_PASSWORD: Optional[str] = "" # 邮件服务器密码
    NOTIFICATION_EMAIL: Optional[str] = "" # 通知邮件地址

    # 添加环境变量字段
    ENV: str = "development"
    # 数据库配置
    DB_DRIVER: Optional[str] = "mysql+mysqlconnector"
    DB_USER: Optional[str] = "root"
    DB_PASSWORD: Optional[str] = "aa123456"
    DB_HOST: Optional[str] = "localhost"
    DB_PORT: Optional[int] = 3306
    DB_NAME: Optional[str] = "ticket_monitor_db"
    DB_CHARSET: Optional[str] = "utf8mb4"
    DB_ECHO: Optional[bool] = True
    DB_POOL_SIZE: Optional[int] = 5
    DB_MAX_OVERFLOW: Optional[int] = 10
    DB_POOL_RECYCLE: Optional[int] = 3600
    DB_POOL_TIMEOUT: Optional[int] = 30

    # 配置文件
    class Config:
        env_file = ".env" # 初始化时指定环境变量文件
        env_file_encoding = "utf-8" # 指定环境变量文件编码
        case_sensitive = True # 指定环境变量文件是否区分大小写

# 使用lru_cache装饰器来缓存Settings类的实例，以提高性能
@lru_cache()
def get_settings():
    """获取配置实例"""
    print(f"setting.py加载配置文件: {Settings().DB_NAME}")
    return Settings()

# 获取配置实例
settings = get_settings()