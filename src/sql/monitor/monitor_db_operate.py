# 从models包中导入模型，确保所有模型都已正确初始化
from src.sql.models import Performance, TicketPrice, Show, UserShowMonitor, UserTicketMonitor
from src.sql.models.user import User
from src.sql.sqlalchemy_db import get_sqlalchemy_db
from src.server.schemas.concert import RecordMonitorParams, TicketPerform

class MonitorDbOperate:
    def __init__(self):
        self.sqlalchemy_db = None
    def db_operate(self, params: RecordMonitorParams, platform: str, user: User):
        with get_sqlalchemy_db() as db:
            self.sqlalchemy_db = db
            # 判断show数据库中是否存在
            show_exist = self.sqlalchemy_db.query(Show).filter(Show.show_id == params.show_id).first()
            wx_token = user.openid
            deadline = params.deadline
            user_id = user.user_id
            if not show_exist:
                # 不存在数据库创建
                show_exist = self.add_show_sql(params, platform)
            # 根据wx_token和show_id查询user_show_monitor
            user_show_monitor_exist = self.sqlalchemy_db.query(UserShowMonitor).filter(
                UserShowMonitor.wx_token == wx_token,
                UserShowMonitor.show_id == params.show_id
            ).first()
            if not user_show_monitor_exist:
                # 不存在数据库创建
                user_show_monitor_exist = self.add_user_show_monitor_sql({
                    'wx_token': wx_token,
                    'show_id': params.show_id,
                    'deadline': deadline,
                    'user_id': user_id,
                    "is_active": 1,
                    "platform": platform
                })
                # 将user_show_monitor添加到show中
                show_exist.user_show_monitors.append(user_show_monitor_exist)
            ticket_perform: list[TicketPerform] = params.ticket_perform
            for ticket_perform_item in ticket_perform:
                # 查看performance场次 在数据库中是否存在
                performance_exist = self.sqlalchemy_db.query(Performance).filter(
                    Performance.show_id == params.show_id,
                    Performance.perform_id == ticket_perform_item.perform_id).first()
                if not performance_exist:
                    # 不存在数据库创建
                    performance_exist = self.add_performance_sql({
                        **ticket_perform_item.model_dump(),
                        'show_id': params.show_id,
                        'platform': platform
                    })
                    # 将演出场次添加到演出中
                    show_exist.performances.append(performance_exist)
                # 查看ticket_price 在数据库中是否存在
                for sku_list_item in ticket_perform_item.sku_list:
                    ticket_price_exist = self.sqlalchemy_db.query(TicketPrice).filter(
                        TicketPrice.perform_id == ticket_perform_item.perform_id,
                        TicketPrice.sku_id == sku_list_item.sku_id).first()
                    if not ticket_price_exist:
                        # 不存在数据库创建
                        ticket_price_exist = self.add_ticket_price_sql({
                            **sku_list_item.model_dump(),
                            'perform_id': performance_exist.perform_id,
                            'platform': platform
                        })
                        # 将票种添加到演出场次中
                        performance_exist.ticket_prices.append(ticket_price_exist)
                    # 查询user_ticket_monitors 表中是否存在监控票务数据
                    user_ticket_monitor_exist = self.sqlalchemy_db.query(UserTicketMonitor).filter(
                        UserTicketMonitor.user_show_monitor_id == user_show_monitor_exist.monitor_id,
                        UserTicketMonitor.perform_id == ticket_perform_item.perform_id,
                        UserTicketMonitor.sku_id == sku_list_item.sku_id,
                        UserTicketMonitor.platform == platform
                    ).first()
                    if not user_ticket_monitor_exist:
                        # 不存在数据库创建
                        user_ticket_monitor_exist = self.add_user_ticket_monitor_sql({
                            'user_show_monitor_id': user_show_monitor_exist.monitor_id,
                            'perform_id': ticket_perform_item.perform_id,
                            'sku_id': sku_list_item.sku_id,
                            'deadline': deadline,
                            'is_notified': 0,
                            'platform': platform
                        })
                        # 将user_ticket_monitor添加到user_show_monitor中
                        user_show_monitor_exist.ticket_monitors.append(user_ticket_monitor_exist)
                        performance_exist.user_ticket_monitors.append(user_ticket_monitor_exist)
                        ticket_price_exist.monitor_ticket_prices.append(user_ticket_monitor_exist)
        pass
    # 添加演出sql
    def add_show_sql(self, params: RecordMonitorParams, platform: str):
        show = Show(
            show_id=params.show_id,
            show_name=params.show_name,
            venue_city_name=params.venue_city_name,
            venue_name=params.venue_name,
            platform=platform,
            cover_url=params.cover_url
        )
        self.sqlalchemy_db.add(show)
        self.sqlalchemy_db.commit()
        return show
    # 添加场次sql
    def add_performance_sql(self, params: dict):
        print('params---------', params)
        performance = Performance(
            perform_id=params.get('perform_id'),
            perform_name=params.get('perform_name'),
            perform_time=params.get('perform_time', None),
            show_id=params.get('show_id'),
            platform=params.get('platform')
        )
        self.sqlalchemy_db.add(performance)
        self.sqlalchemy_db.commit()
        return performance  
    # 添加票种sql
    def add_ticket_price_sql(self, params: dict):
        ticket_price = TicketPrice(
            sku_id=params.get('sku_id'),
            perform_id=params.get('perform_id'),
            price_id=params.get('price_id'),
            price_name=params.get('price_name'),
            platform=params.get('platform')
        )
        self.sqlalchemy_db.add(ticket_price)
        self.sqlalchemy_db.commit()
        return ticket_price
    # 添加用户演出监控sql
    def add_user_show_monitor_sql(self, params: dict):
        user_show_monitor = UserShowMonitor(
            wx_token=params.get('wx_token'),
            show_id=params.get('show_id'),
            deadline=params.get('deadline'),
            user_id=params.get('user_id'),
            is_active=params.get('is_active'),
            platform=params.get('platform')
        )
        self.sqlalchemy_db.add(user_show_monitor)
        self.sqlalchemy_db.commit()
        return user_show_monitor
    # 添加用户票务监控sql
    def add_user_ticket_monitor_sql(self, params: dict):
        user_ticket_monitor = UserTicketMonitor(
            user_show_monitor_id=params.get('user_show_monitor_id'),
            perform_id=params.get('perform_id'),
            sku_id=params.get('sku_id'),
            deadline=params.get('deadline'),
            is_notified=params.get('is_notified'),
            platform=params.get('platform')
        )
        self.sqlalchemy_db.add(user_ticket_monitor)
        self.sqlalchemy_db.commit()
        return user_ticket_monitor