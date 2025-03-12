from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class WxMsgSubscribeTemplate(Base):
    __tablename__ = "wx_msg_subscribe_template"

    id = Column(Integer, primary_key=True, index=True, unique=True)
    entry = Column(String(50), index=True, unique=False, nullable=False)
    # template_id 不是唯一，不能为空
    template_id = Column(String(50), index=True, unique=False, nullable=False)
    template_name = Column(String(255), index=True, unique=False, nullable=False)
    template_content = Column(String(255), index=True, unique=False, nullable=False)
    page = Column(String(255), index=True, unique=False, nullable=False)
    miniprogram_state = Column(String(255), index=True, unique=False, nullable=False)
    status = Column(Integer, default=1)
    create_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))