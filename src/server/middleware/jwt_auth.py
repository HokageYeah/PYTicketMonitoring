from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Optional
from src.server.untiles.Src_Path import public_key_path
from src.sql.models.user import User
from src.sql.sqlalchemy_db import get_sqlalchemy_db
from sqlalchemy.orm import Session

security = HTTPBearer()

# 读取公钥
with open(public_key_path, 'r') as f:
    public_key = f.read()

# 获取当前用户
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_sqlalchemy_db)
) -> User:
    """
    验证JWT令牌并返回当前用户
    """
    token = credentials.credentials
    print('get_current_user---token-----', token)
    try:
        # 使用公钥验证JWT
        payload = jwt.decode(
            token,
            key=public_key,
            algorithms=['RS256']
        )
        print('get_current_user---payload-----', payload)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的身份验证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # 从数据库获取用户
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user
        
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"无效的身份验证凭据: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 检查用户角色的依赖
def require_role(platform: str, url: str, role: int):
    """
    检查用户是否具有指定角色
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.user_role != role:
            # 把下面的返回按照 如下写
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker 