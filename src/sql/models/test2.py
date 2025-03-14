# 测试文件
from src.config.database_config import DATABASE_URL
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Test2(Base):
    __tablename__ = "test2"

    test2_id = Column(Integer, primary_key=True)
    test2_name = Column(String(50))
    test2_age = Column(Integer)
