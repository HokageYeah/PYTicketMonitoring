from src.sql.sqlalchemy_db import get_sqlalchemy_db
from src.sql.models.user import User
import uuid
import jwt
from datetime import datetime, timedelta
from src.server.untiles.Src_Path import private_key_path
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