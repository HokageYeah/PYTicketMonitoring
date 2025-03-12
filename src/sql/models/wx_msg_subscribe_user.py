from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WxMsgSubscribeUse(Base):
    __tablename__ = "wx_msg_subscribe_user"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    user_id = Column(Integer, index=True, unique=True)
    openid = Column(String(50), index=True, unique=True)
    template_id = Column(String(50), index=True, unique=False, nullable=False)
    subscribe_status = Column(String(50), nullable=True, index=True, unique=False)
    status = Column(Integer, default=1)
    create_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))