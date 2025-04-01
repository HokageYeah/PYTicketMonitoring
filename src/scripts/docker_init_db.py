#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# 设置环境变量
os.environ["ENV"] = "production"

# 导入必要的模块
from sqlalchemy import create_engine
from src.config.database_config import DATABASE_URL
from src.sql.sqlalchemy_db import Base
from src.sql.models import *  # 导入所有模型

def init_database():
    """初始化数据库，创建所有表"""
    print(f"使用连接URL: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    try:
        # 创建所有表
        Base.metadata.create_all(engine)
        print("所有表创建成功")
        return True
    except Exception as e:
        print(f"创建表失败: {str(e)}")
        return False

if __name__ == "__main__":
    init_database()