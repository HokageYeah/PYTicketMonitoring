from src.sql.sqlalchemy_db import get_sqlalchemy_db
from src.sql.models.user import User
import uuid
import jwt
from datetime import datetime, timedelta
from src.server.untiles.Src_Path import private_key_path
from src.server.schemas.wxMiniLoginSchema import WxMiniSendSubscribeMessageParams
from src.sql.models.wx_msg_subscribe_user import WxMsgSubscribeUse
from src.server.untiles.custom_exceptions import SaveSubscribeTemplateException, SendSubscribeMsgUserException
from src.sql.models.wx_msg_subscribe_template import WxMsgSubscribeTemplate
from src.server.schemas.wxMiniLoginSchema import WxPlatformEnum
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
    def generate_token(self, user: User):
        print('user_data---------user--generate_token--', user.username, user.password, user.openid)
        try:
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
        except Exception as e:
            print('generate_token::error---------', e)
            return None
    # 存储用户消息订阅到数据库, 接口已经鉴权判断用户是否存在
    def save_user_subscribe_template(self, params: WxMiniSendSubscribeMessageParams, user: User):
        try:
            self.sqlalchemy_db = get_sqlalchemy_db()
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
            return wx_msg_subscribe_use_exist
        except Exception as e:
            print('save_user_subscribe_template::error---------', e)
            raise SaveSubscribeTemplateException(user.openid)
    def create_subscribe_template(self, miniprogram_state):
        try:
            template_id = 'YcOF2JL-yxU5rHL3oAhZq_srkY5epENXsMqgYbXNJiU'
            page = 'pages/home/concert-detail'
            self.sqlalchemy_db = get_sqlalchemy_db()
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
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["SUCCESS::模板创建成功"],
                'data': {},
                'v': 1,
                'api': '/wx/mini.create.subscribe.template'
                
            }
        except Exception as e:
            print('create_subscribe_template::error---------', e)
            return {
                'platform': WxPlatformEnum.WX_MINI.value,
                'ret': ["ERROR::模板创建失败"],
                'data': {},
                'v': 1,
                'api': '/wx/mini.create.subscribe.template'
            }
    # 查询获取用户的模板信息
    def get_user_subscribe_template(self, user: User):
        self.sqlalchemy_db = get_sqlalchemy_db()
        # 关联表查询 根据用户id查询WxMsgSubscribeUse获取template_id, 在根据template_id查询WxMsgSubscribeTemplate获取模板信息
        subscribe_template = self.sqlalchemy_db.query(WxMsgSubscribeUse).filter(WxMsgSubscribeUse.user_id == user.user_id).first()
        if subscribe_template:
            subscribe_template_id = subscribe_template.template_id
            template_info = self.sqlalchemy_db.query(WxMsgSubscribeTemplate).filter(WxMsgSubscribeTemplate.template_id == subscribe_template_id).first()
            print('template_info---------', template_info)
            return template_info
        else:
            raise SendSubscribeMsgUserException(user.openid)