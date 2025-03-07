from sqlalchemy import Column, Integer, String, DateTime
from src.sql.sqlalchemy_db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
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
    # 允许为空
    create_time = Column(DateTime, default=datetime.now)
    # 允许为空
    update_time = Column(DateTime, default=datetime.now)
    # 允许为空
    user_avatar_pic = Column(String(255))
    # 允许为空
    user_address = Column(String(255))
    # 允许为空
    user_role = Column(Integer, default=1)
