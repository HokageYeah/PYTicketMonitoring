from src.sql.models import user
from sqlalchemy import create_engine
from src.config.database_config import DATABASE_URL

# 简单方法：使用 create_tables.py 脚本直接创建表
# 高级方法：使用 Alembic 进行数据库迁移管理

def create_tables():
    engine = create_engine(DATABASE_URL)
    user.Base.metadata.create_all(engine)

if __name__ == "__main__":
    create_tables() 