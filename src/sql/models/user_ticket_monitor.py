from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, text
from sqlalchemy.orm import relationship
from src.sql.sqlalchemy_db import Base
from sqlalchemy import BigInteger
class UserTicketMonitor(Base):
    __tablename__ = "user_ticket_monitors"

    monitor_ticket_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='监控票务ID')
    user_show_monitor_id = Column(BigInteger, ForeignKey("user_show_monitors.monitor_id"), nullable=False)
    perform_id = Column(String(20), ForeignKey('performances.perform_id', ondelete='CASCADE'), primary_key=True, comment='关联场次ID')
    sku_id = Column(String(20), ForeignKey("ticket_prices.sku_id", ondelete='CASCADE'), primary_key=True, comment='关联票种ID')
    is_notified = Column(Boolean, default=False, comment="是否已通知")
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # 唯一约束
    __table_args__ = (
        {"comment": "用户票价监控表"},
    )

    # 关系
    user_show_monitor = relationship("UserShowMonitor", back_populates="ticket_monitors")
    performance = relationship("Performance")
    ticket_price = relationship("TicketPrice", back_populates="monitor_ticket_prices")



#  relationship：定义模型之间的关系。
# 'MonitorDetail'：关联的模型类名。
# back_populates='user_monitor'：双向关系，MonitorDetail 模型中需要定义对应的 user_monitor 字段。
# cascade='all, delete-orphan'：级联操作，当 UserMonitor 删除时，关联的 MonitorDetail 也会被删除。

# 在 relationship 中，cascade 参数用于控制父记录操作对子记录的影响。常用选项包括：
# save-update：当父记录被保存时，自动保存子记录。
# delete：当父记录被删除时，自动删除子记录。
# delete-orphan：当子记录不再与父记录关联时，自动删除子记录。
# all：包含 save-update、merge、expunge、delete、refresh-expire 和 delete-orphan。