from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship
from src.sql.sqlalchemy_db import Base
from sqlalchemy import BigInteger, Index
from sqlalchemy import SmallInteger
class UserShowMonitor(Base):
    __tablename__ = "user_show_monitors"

    monitor_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='监控记录ID')
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    wx_token = Column(String(50), nullable=False, comment='用户微信openid')
    show_id = Column(String(20), ForeignKey('shows.show_id', ondelete='CASCADE'), nullable=False, comment='关联演出ID')
    deadline = Column(DateTime, nullable=False, comment="监控截止日期")
    is_active = Column(SmallInteger, server_default=text('1'), comment='是否有效（0-无效 1-有效）')
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    # 平台
    platform = Column(String(20), nullable=False, comment='平台')
    # 唯一约束
    __table_args__ = (
        Index('idx_wx_token', 'wx_token'),
        Index('idx_deadline', 'deadline'),
        Index('idx_show_user', 'show_id', 'wx_token'),
        {'comment': '用户监控主表'}
    )

    # 关系
    show = relationship("Show", back_populates="user_show_monitors")
    ticket_monitors = relationship("UserTicketMonitor", back_populates="user_show_monitor", cascade='all, delete-orphan')