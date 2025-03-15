# 测试文件
from src.config.database_config import DATABASE_URL
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from src.sql.sqlalchemy_db import Base

class Test4(Base):
    __tablename__ = "test4"

    test4_id = Column(Integer, primary_key=True)
    test4_name = Column(String(50))
    test4_age = Column(Integer)
