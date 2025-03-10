from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, unique=True)
    # 不允许为空
    username = Column(String(50), unique=True, index=True, nullable=False)
    # 不允许为空
    password = Column(String(100), nullable=False)
    # 不允许为空
    openid = Column(String(50), nullable=False, unique=True)
    # 允许为空
    session_key = Column(String(100), nullable=True)
    # 允许为空
    status = Column(Integer, default=1)
    # 创建时间 - 自动设置为当前时间
    create_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    # 更新时间 - 创建和更新时都会自动设置为当前时间
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # 允许为空
    user_avatar_pic = Column(String(255))
    # 允许为空
    user_address = Column(String(255))
    # 允许为空
    user_role = Column(Integer, default=1)
