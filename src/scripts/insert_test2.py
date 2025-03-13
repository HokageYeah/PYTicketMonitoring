import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from src.sql.models.test2 import Test2
import random
from src.sql.sqlalchemy_db import get_sqlalchemy_db
from src.sql.sqlalchemy_db import database

# 手动添加 测试数据
# 创建会话
print('database.connect()1')
database.connect()
session = get_sqlalchemy_db()
try:
    # 准备插入10条用户数据
    test2_to_insert = []
    for i in range(1, 11):
        test2 = Test2(
            test2_name=f"test2_{i}",
            test2_age=random.randint(1, 100),
        )
        test2_to_insert.append(test2)
    
    # 批量插入数据
    session.add_all(test2_to_insert)
    session.commit()
    print(f"成功插入 {len(test2_to_insert)} 条用户数据")

except Exception as e:
    session.rollback()
    print(f"插入数据失败: {e}")
finally:
    session.close()