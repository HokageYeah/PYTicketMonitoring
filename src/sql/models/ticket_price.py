from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, text
from sqlalchemy.orm import relationship
from sqlalchemy import Index
from src.sql.sqlalchemy_db import Base

class TicketPrice(Base):
    __tablename__ = "ticket_prices"

    sku_id = Column(String(20), primary_key=True, comment='票种唯一ID')
    perform_id = Column(String(20), ForeignKey('performances.perform_id', ondelete='CASCADE'), nullable=False, comment='关联场次ID')
    price_id = Column(String(20), nullable=False, comment='价格体系ID')
    price_name = Column(String(50), nullable=False, comment='价格显示名称')
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # 平台
    platform = Column(String(20), nullable=False, comment='平台')
    # 关系
    performance = relationship("Performance", back_populates="ticket_prices")
    monitor_ticket_prices = relationship("UserTicketMonitor", back_populates="ticket_price")
    # 上面的替代方案
    # monitor_ticket_prices = relationship("UserTicketMonitor", foreign_keys="[UserTicketMonitor.sku_id]", back_populates="ticket_price")


    __table_args__ = (
        Index('idx_perform_id', 'perform_id'),
        {'comment': '票种表'}
    )