from pydantic_settings import BaseSettings
from functools import lru_cache
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
class EmailSettings(BaseSettings):
    """邮件配置"""
    QQ_MAIL_SERVER: str
    QQ_MAIL_PORT: int
    QQ_MAIL_USERNAME: str
    QQ_MAIL_PASSWORD: str
    QQ_MAIL_FROM: str
    QQ_MAIL_SSL_TLS: bool
    QQ_MAIL_STARTTLS: bool
    QQ_MAIL_USE_CREDENTIALS: bool

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 缓存邮件配置
@lru_cache()
def get_email_settings():
    """获取邮件配置（使用缓存）"""
    return EmailSettings()

def get_mail_config(settings: EmailSettings = None):
    """获取邮件连接配置"""
    print(f"获取邮件连接配置: {settings}")
    if settings is None:
        settings = get_email_settings()
    
    return ConnectionConfig(
        MAIL_USERNAME=settings.QQ_MAIL_USERNAME,
        MAIL_PASSWORD=settings.QQ_MAIL_PASSWORD,
        MAIL_FROM=settings.QQ_MAIL_FROM,
        MAIL_FROM_NAME=settings.QQ_MAIL_FROM,
        MAIL_SERVER=settings.QQ_MAIL_SERVER,
        MAIL_PORT=settings.QQ_MAIL_PORT,
        MAIL_SSL_TLS=settings.QQ_MAIL_SSL_TLS,
        MAIL_STARTTLS=settings.QQ_MAIL_STARTTLS,
        # MAIL_TIMEOUT=10,  # 设置10秒超时
        # 移除 MAIL_USE_CREDENTIALS，因为 ConnectionConfig 不支持这个字段
        # MAIL_USE_CREDENTIALS=settings.QQ_MAIL_USE_CREDENTIALS,
        # TEMPLATE_FOLDER=None  # 可以设置邮件模板目录
    )


