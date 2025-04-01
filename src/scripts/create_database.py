#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# 导入必要的模块
try:
    from sqlalchemy import create_engine, text
    from src.config.database_config import get_database_config
except Exception as e:
    print(f"导入模块失败: {str(e)}")
    sys.exit(1)

def create_database():
    """创建数据库"""
    print("开始创建数据库...")
    
    # 获取数据库配置
    config = get_database_config()
    print(f"数据库配置: {config}")
    
    # 创建不包含数据库名的连接URL
    url_without_db = f"{config['driver']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
    print(f"连接URL: {url_without_db}")
    
    try:
        # 创建数据库引擎
        engine = create_engine(url_without_db)
        
        # 连接并执行创建数据库的SQL
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        
        print(f"数据库 {config['database']} 创建成功")
        return True
    except Exception as e:
        print(f"创建数据库失败: {str(e)}")
        return False

if __name__ == '__main__':
    create_database()