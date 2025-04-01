# import click
# import os

# # 创建一个命令行接口
# @click.group()
# def cli():
#     pass

# @cli.command()
# def migrate():
#     """创建迁移"""
#     os.system('alembic revision --autogenerate -m "auto migration"')

# @cli.command()
# def upgrade():
#     """应用迁移"""
#     os.system('alembic upgrade head')

# @cli.command()
# def downgrade():
#     """回滚迁移"""
#     os.system('alembic downgrade -1')

# @cli.command()
# def reset():
#     """重置数据库"""
#     os.system('alembic downgrade base')

# # 插入数据
# @cli.command()
# def insert_data():
#     """插入数据"""
#     os.system('alembic revision --autogenerate -m "insert data"')

# # 创建缺失的表
# #    alembic revision --autogenerate -m "create wx_msg_subscribe_user table"
# #    alembic upgrade head

# if __name__ == '__main__':
#     cli() 


#!/usr/bin/env python3
import os
import sys
import click
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, text
from src.config.database_config import DATABASE_URL, get_database_config
from src.sql.sqlalchemy_db import Base

# 创建一个命令行接口
@click.group()
def cli():
    """数据库管理工具"""
    pass

@cli.command()
def create_db():
    """创建数据库"""
    # 无法进入此方法 报错 Error: No such command 'create_db'. 暂时无法定位原因
    config = get_database_config()
    # 创建不包含数据库名的连接URL
    url_without_db = f"{config['driver']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
    engine = create_engine(url_without_db)
    
    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    
    click.echo(f"数据库 {config['database']} 创建成功")

@cli.command()
def drop_db():
    """删除数据库"""
    config = get_database_config()
    # 创建不包含数据库名的连接URL
    url_without_db = f"{config['driver']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
    engine = create_engine(url_without_db)
    
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {config['database']}"))
    
    click.echo(f"数据库 {config['database']} 删除成功")

@cli.command()
def create_tables():
    """创建所有表"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    click.echo("所有表创建成功")

@cli.command()
def drop_tables():
    """删除所有表"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.drop_all(engine)
    click.echo("所有表删除成功")

@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def migrate(args):
    """运行数据库迁移命令
    
    例如: python manage_db.py migrate revision --autogenerate -m "create new table"
    """
    import subprocess
    cmd = ['alembic'] + list(args)
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd)

@cli.command()
def upgrade():
    """应用迁移到最新版本"""
    os.system('alembic upgrade head')
    click.echo("数据库迁移已应用到最新版本")

@cli.command()
def downgrade():
    """回滚迁移到上一个版本"""
    os.system('alembic downgrade -1')
    click.echo("数据库已回滚到上一个版本")

@cli.command()
def reset():
    """重置数据库（删除并重新创建）"""
    click.echo("正在重置数据库...")
    # 先回滚到基础版本
    os.system('alembic downgrade base')
    # 删除数据库
    config = get_database_config()
    url_without_db = f"{config['driver']}://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
    engine = create_engine(url_without_db)
    
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {config['database']}"))
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    
    # 应用所有迁移
    os.system('alembic upgrade head')
    click.echo("数据库重置成功")

@cli.command()
def history():
    """查看迁移历史"""
    os.system('alembic history')

@cli.command()
def current():
    """查看当前迁移版本"""
    os.system('alembic current')

if __name__ == '__main__':
    cli()