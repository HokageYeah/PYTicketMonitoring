from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from src.sql.sqlalchemy_db import Base
# 不同的 Base 类 ：每个模型文件都创建了自己的 Base = declarative_base() ，导致模型之间无法建立关系。
class Show(Base):
    __tablename__ = "shows"

    show_id = Column(String(20), primary_key=True, comment='演出全局唯一ID')
    show_name = Column(String(100), nullable=False, comment='演出名称')
    venue_city_name = Column(String(50), nullable=False, comment='场馆所在城市')
    venue_name = Column(String(50), nullable=False, comment='场馆名称')
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # 平台
    platform = Column(String(20), nullable=False, comment='平台')
    # 关系定义
    performances = relationship('Performance', back_populates='show', cascade='all, delete-orphan')
    user_show_monitors = relationship('UserShowMonitor', back_populates='show', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_venue', 'venue_city_name', 'venue_name'),
        {'comment': '演出主表'}
    )