from sqlalchemy import Column, Integer, String, DateTime, text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from datetime import datetime
from src.sql.sqlalchemy_db import Base

# 演出场次
class Performance(Base):
    __tablename__ = "performances"

    perform_id = Column(String(20), primary_key=True, comment='场次唯一ID')
    show_id = Column(String(20), ForeignKey('shows.show_id', ondelete='CASCADE'), nullable=False, comment='关联演出ID')
    perform_name = Column(String(100), nullable=False, comment='场次名称（含时间）')
    perform_time = Column(DateTime, nullable=True, comment="演出时间")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # 关系
    show = relationship("Show", back_populates="performances")
    # 场次票种 一对多，级联删除
    ticket_prices = relationship("TicketPrice", back_populates="performance", cascade="all, delete-orphan")
    user_ticket_monitors = relationship("UserTicketMonitor", back_populates="performance", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_show_id', 'show_id'),
        {'comment': '演出场次表'}
    )