### 创建 models/init.py 文件
# 为了确保模型之间的关系正确建立，我们需要在 __init__.py 文件中导入所有模型，并确保它们按正确的顺序初始化。
# 按依赖顺序导入模型
from src.sql.models.user import User
from src.sql.models.show import Show
from src.sql.models.performance import Performance
from src.sql.models.ticket_price import TicketPrice
from src.sql.models.user_show_monitor import UserShowMonitor
from src.sql.models.user_ticket_monitor import UserTicketMonitor
from src.sql.models.wx_msg_subscribe_user import WxMsgSubscribeUse
from src.sql.models.wx_msg_subscribe_template import WxMsgSubscribeTemplate
# 导出所有模型
__all__ = [
    'User',
    'Show',
    'Performance',
    'TicketPrice',
    'UserShowMonitor',
    'UserTicketMonitor',
    'WxMsgSubscribeUse',
    'WxMsgSubscribeTemplate'
]