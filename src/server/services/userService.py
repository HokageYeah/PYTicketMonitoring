from src.sql.sqlalchemy_db import get_sqlalchemy_db
from sqlalchemy.orm import joinedload, load_only
from src.sql.models.user import User
import uuid
import jwt
from datetime import datetime, timedelta
from src.server.untiles.Src_Path import private_key_path
from src.server.schemas.wxMiniLoginSchema import \
    WxMiniSendSubscribeMessageParams, \
    WxMiniGetUserSubscribeMonitorListParams, \
    WxMiniDeleteUserSubscribeMonitorParams
from src.sql.models.wx_msg_subscribe_user import WxMsgSubscribeUse
from src.server.untiles.custom_exceptions import SaveSubscribeTemplateException, SendSubscribeMsgUserException
from src.sql.models.wx_msg_subscribe_template import WxMsgSubscribeTemplate
from src.sql.models import Show, Performance, TicketPrice, UserShowMonitor, UserTicketMonitor
from src.server.untiles.res_handler import wx_mini_response_handler
from collections import defaultdict
import cachetools
from src.decorators.Cache_Decorator import cache_result, clear_cache
# 创建一个TTLCache实例，最大容量为100个项目，过期时间为1分钟
cache = cachetools.TTLCache(maxsize=100, ttl=60)
# 所有用户操作的服务service都放在这个类里里面
class UserService:
    def __init__(self):
        self.sqlalchemy_db = None
    def create_user(self, user: User):
        self.sqlalchemy_db = get_sqlalchemy_db()
        # 根据openid查询用户是否存在
        user_exist = self.sqlalchemy_db.query(User).filter(User.openid == user.openid).first()
        if user_exist:
            print('user_data---------user--create_user--user_exist', user_exist.username, user_exist.password, user_exist.openid)
            print('user_data---------user--create_user--user_exist', user_exist)
            return user_exist
        else:
            # 用户不存在，则创建用户
            # 判断是否有用户名或者密码。如果没有则随机生成一个不唯一的用户名和密码
            if not user.username or not user.password:
                user.username = 'user_' + str(uuid.uuid4())
                user.password = 'password_' + str(uuid.uuid4())
            print('user_data---------user--create_user--', user.username, user.password, user.openid)
            self.sqlalchemy_db.add(user)
            self.sqlalchemy_db.commit()
            return user
    @wx_mini_response_handler(api_path='/wx/mini.login.by.code')
    def generate_token(self, user: User):
        print('user_data---------user--generate_token--', user.username, user.password, user.openid)
        with get_sqlalchemy_db() as db:
            """
            生成 JWT token
            
            Args:
                data: 要编码的数据
                secret_key: 密钥
            
            Returns:
                token字符串
            """
            self.sqlalchemy_db = get_sqlalchemy_db()
            # 读取用户信息
            # user = self.sqlalchemy_db.query(User).filter(User.user_id == user.user_id).first()
            # 读取私钥文件
            with open(private_key_path, 'r') as f:
                private_key = f.read()
            user_data = {
                "username": user.username,
                "password": user.password,
                "user_id": user.user_id,
                "openid": user.openid,
                "status": user.status,
                "user_avatar_pic": user.user_avatar_pic,
                "user_address": user.user_address,
                "user_role": user.user_role
            }
            print('user_data---------', user_data)
            # 添加过期时间（2小时）
            user_data.update({
                "exp": datetime.now() + timedelta(hours=2)  # 过期时间
            })
            #  RS256:非对称加密 HS256:对称加密
            token = jwt.encode(user_data, key=private_key, algorithm='RS256')
            print('token---------', token)
            return token
        # try:
        #     """
        #     生成 JWT token
            
        #     Args:
        #         data: 要编码的数据
        #         secret_key: 密钥
            
        #     Returns:
        #         token字符串
        #     """
        #     self.sqlalchemy_db = get_sqlalchemy_db()
        #     # 读取用户信息
        #     # user = self.sqlalchemy_db.query(User).filter(User.user_id == user.user_id).first()
        #     # 读取私钥文件
        #     with open(private_key_path, 'r') as f:
        #         private_key = f.read()
        #     user_data = {
        #         "username": user.username,
        #         "password": user.password,
        #         "user_id": user.user_id,
        #         "openid": user.openid,
        #         "status": user.status,
        #         "user_avatar_pic": user.user_avatar_pic,
        #         "user_address": user.user_address,
        #         "user_role": user.user_role
        #     }
        #     print('user_data---------', user_data)
        #     # 添加过期时间（2小时）
        #     user_data.update({
        #         "exp": datetime.now() + timedelta(hours=2)  # 过期时间
        #     })
        #     #  RS256:非对称加密 HS256:对称加密
        #     token = jwt.encode(user_data, key=private_key, algorithm='RS256')
        #     print('token---------', token)
        #     return token
        # except Exception as e:
        #     print('generate_token::error---------', e)
        #     return None
    # 存储用户消息订阅到数据库, 接口已经鉴权判断用户是否存在
    @wx_mini_response_handler(api_path='/wx/mini.save.subscribe.template', error_msg=f'订阅消息模板存储异常 (openid: {User.openid})')
    def save_user_subscribe_template(self, params: WxMiniSendSubscribeMessageParams, user: User):
        with get_sqlalchemy_db() as db:
            self.sqlalchemy_db = db
            # 判断WxMsgSubscribeUse表是否存在
            wx_msg_subscribe_use_exist = self.sqlalchemy_db.query(WxMsgSubscribeUse).filter(WxMsgSubscribeUse.openid == user.openid).first()
            template_id = params.templateList[0].get('templateId')
            subscribe_status = params.templateList[0].get('subscribeStatus')
            # 不存在则创建
            wx_msg_subscribe_use = WxMsgSubscribeUse(
                user_id=user.user_id,
                openid=user.openid,
                template_id=template_id,
                subscribe_status=subscribe_status
            )
            if not wx_msg_subscribe_use_exist:
                print('wx_msg_subscribe_use_exist---------模板不存在', wx_msg_subscribe_use)
                self.sqlalchemy_db.add(wx_msg_subscribe_use)
            else:
                # 存在则更新
                print('wx_msg_subscribe_use_exist---------模板存在', wx_msg_subscribe_use)
                # 更新
                wx_msg_subscribe_use_exist.template_id = template_id
                wx_msg_subscribe_use_exist.subscribe_status = subscribe_status
            self.sqlalchemy_db.commit()
            return {
                'template_id': template_id,
                'subscribe_status': subscribe_status
            }
        # try:
        #     self.sqlalchemy_db = get_sqlalchemy_db()
        #     # 判断WxMsgSubscribeUse表是否存在
        #     wx_msg_subscribe_use_exist = self.sqlalchemy_db.query(WxMsgSubscribeUse).filter(WxMsgSubscribeUse.openid == user.openid).first()
        #     template_id = params.templateList[0].get('templateId')
        #     subscribe_status = params.templateList[0].get('subscribeStatus')
        #     # 不存在则创建
        #     wx_msg_subscribe_use = WxMsgSubscribeUse(
        #         user_id=user.user_id,
        #         openid=user.openid,
        #         template_id=template_id,
        #         subscribe_status=subscribe_status
        #     )
        #     if not wx_msg_subscribe_use_exist:
        #         print('wx_msg_subscribe_use_exist---------模板不存在', wx_msg_subscribe_use)
        #         self.sqlalchemy_db.add(wx_msg_subscribe_use)
        #     else:
        #         # 存在则更新
        #         print('wx_msg_subscribe_use_exist---------模板存在', wx_msg_subscribe_use)
        #         # 更新
        #         wx_msg_subscribe_use_exist.template_id = template_id
        #         wx_msg_subscribe_use_exist.subscribe_status = subscribe_status
        #     self.sqlalchemy_db.commit()
        #     return wx_msg_subscribe_use_exist
        # except Exception as e:
        #     print('save_user_subscribe_template::error---------', e)
        #     raise SaveSubscribeTemplateException(user.openid)
    @wx_mini_response_handler(api_path='/wx/mini.create.subscribe.template', success_msg='模板创建成功')
    def create_subscribe_template(self, miniprogram_state):
        with get_sqlalchemy_db() as db:
            template_id = 'YcOF2JL-yxU5rHL3oAhZq_srkY5epENXsMqgYbXNJiU'
            page = 'pages/home/concert-detail'
            self.sqlalchemy_db = db
            subscribe_template = self.sqlalchemy_db.query(WxMsgSubscribeTemplate).filter(WxMsgSubscribeTemplate.template_id == template_id).first()
            # 创建模板数据
            template_data = WxMsgSubscribeTemplate(
                template_id=template_id,
                entry='wxmp_xbsm',
                template_name='演出名称 {{thing1.DATA}} 时间 {{time2.DATA}} 地点 {{thing3.DATA}} 场次 {{thing6.DATA}} 备注 {{thing4.DATA}}',
                template_content='演出名称 {{thing1.DATA}} 时间 {{time2.DATA}} 地点 {{thing3.DATA}} 场次 {{thing6.DATA}} 备注 {{thing4.DATA}}',
                page=page,
                status=1,
                miniprogram_state=miniprogram_state
            )
            if not subscribe_template:
                self.sqlalchemy_db.add(template_data)
                print('模板创建成功')
            else:
                subscribe_template.miniprogram_state = miniprogram_state
                print('模板已存在')
            self.sqlalchemy_db.commit()
            return {}
    # 查询获取用户的模板信息
    @wx_mini_response_handler( api_path='/wx/mini.send.subscribe.message')
    def get_user_subscribe_template(self, user: User):
        with get_sqlalchemy_db() as db:
            self.sqlalchemy_db = db
            # 关联表查询 根据用户id查询WxMsgSubscribeUse获取template_id, 在根据template_id查询WxMsgSubscribeTemplate获取模板信息
            subscribe_template = self.sqlalchemy_db.query(WxMsgSubscribeUse).filter(WxMsgSubscribeUse.user_id == user.user_id).first()
            if subscribe_template:
                subscribe_template_id = subscribe_template.template_id
                template_info = self.sqlalchemy_db.query(WxMsgSubscribeTemplate).filter(WxMsgSubscribeTemplate.template_id == subscribe_template_id).first()
                print('template_info---------', template_info)
                return {
                    'template_id': template_info.template_id,
                    'template_name': template_info.template_name,
                    'template_content': template_info.template_content,
                    'page': template_info.page,
                    'miniprogram_state': template_info.miniprogram_state
                }
            else:
                raise SendSubscribeMsgUserException(user.openid)
    # 获取用户订阅监控列表
    @wx_mini_response_handler(api_path='/wx/mini.get.user.subscribe.monitor.list', error_msg='获取用户订阅监控列表调用失败', success_msg='获取用户订阅监控列表调用成功')
    @cache_result(cache, 'subscribe_monitor_list')
    def get_user_subscribe_monitor_list(self, user: User, params: WxMiniGetUserSubscribeMonitorListParams):
        with get_sqlalchemy_db() as db:
            self.sqlalchemy_db = db
            query = self.sqlalchemy_db.query(UserShowMonitor) \
                .filter(UserShowMonitor.user_id == user.user_id) \
                .options(
                     # 使用 load_only 优化查询，只加载需要的字段
                     # 只加载 UserShowMonitor 需要的字段（字段投影优化）
                    load_only(
                        UserShowMonitor.monitor_id,
                        UserShowMonitor.wx_token,
                        UserShowMonitor.show_id,
                        UserShowMonitor.platform,
                        UserShowMonitor.deadline,
                        UserShowMonitor.created_at
                    ),
                    # 只加载 Show 需要的字段
                    joinedload(UserShowMonitor.show).load_only(
                        Show.show_id,
                        Show.show_name,
                        Show.venue_city_name,
                        Show.venue_name
                    ),
                    # 只加载 UserTicketMonitor 需要的字段
                    joinedload(UserShowMonitor.ticket_monitors).load_only(
                        UserTicketMonitor.monitor_ticket_id,
                        UserTicketMonitor.user_show_monitor_id,
                        UserTicketMonitor.perform_id,
                        UserTicketMonitor.sku_id
                    ),
                    # 只加载 Performance 需要的字段
                    joinedload(UserShowMonitor.ticket_monitors).joinedload(UserTicketMonitor.performance).load_only(
                        Performance.perform_id,
                        Performance.perform_name
                    ),
                    # 只加载 TicketPrice 需要的字段
                    joinedload(UserShowMonitor.ticket_monitors).joinedload(UserTicketMonitor.ticket_price).load_only(
                        TicketPrice.sku_id,
                        TicketPrice.price_id,
                        TicketPrice.price_name
                    )
                         )
            # 分页加载
            query = query.offset((params.page - 1) * params.pageSize).limit(params.pageSize)
            user_monitors = query.all()
            print('user_monitors---------', user_monitors)
             # 最终结果字典，按平台分组
            result = defaultdict(lambda: {"monitor_list": []})
            # 按平台分组
            platform_show_map = defaultdict(lambda: defaultdict(list))
            for monitor in user_monitors:
                platform_show_map[monitor.platform][monitor.show_id].append(monitor)
            # 处理每个平台的数据
            for platform, shows in platform_show_map.items():
                platform_data = []
                for show_id, monitors in shows.items():
                    # 获取第一个监控记录中的演出信息（所有记录的演出信息应该相同）
                    show = monitors[0].show
                    show_entry = {
                        "show_id": show.show_id,
                        "show_name": show.show_name,
                        "venue_city_name": show.venue_city_name,
                        "venue_name": show.venue_name,
                        "deadline": None,
                        "performances": []  # 直接在演出层级包含场次信息
                    }
                    # 收集所有场次和票种信息
                    perform_map = {}
                    latest_deadline = datetime.min
                     # 遍历该演出的所有监控记录
                    for monitor in monitors:
                        # 更新最晚截止时间
                        if monitor.deadline and monitor.deadline > latest_deadline:
                            latest_deadline = monitor.deadline
                            show_entry["deadline"] = latest_deadline.strftime("%Y-%m-%d %H:%M:%S")
                        # 收集所有场次和票种信息
                        for ticket_monitor in monitor.ticket_monitors:
                            performance = ticket_monitor.performance
                            ticket_price = ticket_monitor.ticket_price
                            perform_map[performance.perform_id] = {
                                "perform_id": performance.perform_id,
                                "perform_name": performance.perform_name,
                                "tickets": []  # 直接在场次层级包含票种信息
                            }
                            # 创建票种信息
                            ticket_info = {
                                "sku_id": ticket_price.sku_id,
                                "price_name": ticket_price.price_name
                            }
                            print('ticket_info---------', ticket_info)
                            print('perform_map[performance.perform_id]---------', perform_map[performance.perform_id])
                            # 避免重复添加相同的票种
                            if not any(
                                existing["sku_id"] == ticket_info["sku_id"] and 
                                existing["price_id"] == ticket_info["price_id"]
                                for existing in perform_map[performance.perform_id]["tickets"]
                            ):
                                perform_map[performance.perform_id]["tickets"].append(ticket_info)
                    # 将场次信息添加到演出条目中
                    print('perform_map---------', perform_map)
                    print('show_entry---------', show_entry)
                    print('platform_data.values---------', perform_map.values())
                    show_entry["performances"] = list(perform_map.values())
                    platform_data.append(show_entry)
                result[platform] = platform_data
            print('result---------', result)
            return result
    # 删除用户订阅监控
    @wx_mini_response_handler(api_path='/wx/mini.delete.user.subscribe.monitor', error_msg='删除用户订阅监控调用失败', success_msg='删除用户订阅监控调用成功')
    @clear_cache(cache, 'subscribe_monitor_list')
    def delete_user_subscribe_monitor(self, user: User, params: WxMiniDeleteUserSubscribeMonitorParams):
        with get_sqlalchemy_db() as db:
            self.sqlalchemy_db = db
            user_id = user.user_id
            show_id = params.show_id
            perform_id = params.perform_id
            sku_ids = params.sku_ids if hasattr(params, 'sku_ids') else []
            print('sku_ids---------', sku_ids)
            # 初始化删除计数器
            deleted_counts = {
                "user_ticket_monitors": 0,
                "user_show_monitors": 0,
                "ticket_prices": 0,
                "performances": 0,
                "shows": 0
            }
            user_show_monitors = self.sqlalchemy_db.query(UserShowMonitor).filter(
                UserShowMonitor.user_id == user_id,
                UserShowMonitor.show_id == show_id
            ).options(joinedload(UserShowMonitor.ticket_monitors).load_only(
                UserTicketMonitor.monitor_ticket_id,
                UserTicketMonitor.user_show_monitor_id,
                UserTicketMonitor.perform_id,
                UserTicketMonitor.sku_id
            )).all()
            if not user_show_monitors:
                return {
                    'ret': ['ERROR::未找到监控记录'],
                }
            # 获取用户监控ID列表
            monitor_ids = [monitor.monitor_id for monitor in user_show_monitors]
            # 构建删除条件
            delete_conditions = [UserTicketMonitor.user_show_monitor_id.in_(monitor_ids)]
            if perform_id:
                delete_conditions.append(UserTicketMonitor.perform_id == perform_id)
            if sku_ids:
                delete_conditions.append(UserTicketMonitor.sku_id.in_(sku_ids))
            # 3. 删除符合条件的监控详情
            # 先获取要删除的记录，用于后续清理
            to_delete_monitors = db.query(UserTicketMonitor).filter(*delete_conditions).all()
            print('to_delete_monitors---------', [monitor.monitor_ticket_id for monitor in to_delete_monitors])
            # 删除监控详情
            # 执行删除
            deleted_counts["user_ticket_monitors"] = db.query(UserTicketMonitor).filter(
                *delete_conditions
            ).delete(synchronize_session=False)
            # 检查并清理孤立的用户监控记录
            orphaned_monitors = db.query(UserShowMonitor).outerjoin(
                UserTicketMonitor,
                UserShowMonitor.monitor_id == UserTicketMonitor.user_show_monitor_id
            ).filter(
                UserShowMonitor.user_id == user_id,
                UserShowMonitor.show_id == show_id,
                UserTicketMonitor.monitor_ticket_id == None
            ).all()
            for monitor in orphaned_monitors:
                print('monitor---------', monitor.monitor_id)
                print('monitor_ticket_id---monitor---------', monitor.ticket_monitors)
                for ticket_monitor in monitor.ticket_monitors:
                    print('ticket_monitor---------', ticket_monitor.monitor_ticket_id)
            print('orphaned_monitors---------', orphaned_monitors)
            orphaned_monitor_ids = [monitor.monitor_id for monitor in orphaned_monitors]
            if orphaned_monitor_ids:
                deleted_counts["user_show_monitors"] = db.query(UserShowMonitor).filter(
                    UserShowMonitor.monitor_id.in_(orphaned_monitor_ids)
                ).delete(synchronize_session=False)
               # 5. 检查是否需要清理票种
            if sku_ids and perform_id:
                for sku_id in sku_ids:
                    # 检查该票种是否还有其他用户在监控
                    has_monitors = db.query(UserTicketMonitor).filter(
                        UserTicketMonitor.perform_id == perform_id,
                        UserTicketMonitor.sku_id == sku_id
                    ).first() is not None
                    
                    if not has_monitors:
                        # 删除该票种
                        deleted_counts["ticket_prices"] += db.query(TicketPrice).filter(
                            TicketPrice.perform_id == perform_id,
                            TicketPrice.sku_id == sku_id
                        ).delete(synchronize_session=False)
            
            # 6. 检查是否需要清理场次
            if perform_id:
                # 检查该场次是否还有监控
                has_monitors = db.query(UserTicketMonitor).filter(
                    UserTicketMonitor.perform_id == perform_id
                ).first() is not None
                
                if not has_monitors:
                    # 删除该场次
                    deleted_counts["performances"] += db.query(Performance).filter(
                        Performance.perform_id == perform_id
                    ).delete(synchronize_session=False)
            
            # 7. 检查是否需要清理演出
            # 检查该演出是否还有监控
            has_show_monitors = db.query(UserShowMonitor).filter(
                UserShowMonitor.show_id == show_id
            ).first() is not None
            
            if not has_show_monitors:
                # 删除该演出
                deleted_counts["shows"] += db.query(Show).filter(
                    Show.show_id == show_id
                ).delete(synchronize_session=False)
            
            # 提交事务
            db.commit()
            return {
                "message": "删除成功",
                "deleted": deleted_counts
            }
   

            print('user_show_monitors---------', user_show_monitors)
            return {

            }