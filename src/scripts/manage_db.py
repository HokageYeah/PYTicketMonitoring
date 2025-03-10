import click
import os

# 创建一个命令行接口
@click.group()
def cli():
    pass

@cli.command()
def migrate():
    """创建迁移"""
    os.system('alembic revision --autogenerate -m "auto migration"')

@cli.command()
def upgrade():
    """应用迁移"""
    os.system('alembic upgrade head')

@cli.command()
def downgrade():
    """回滚迁移"""
    os.system('alembic downgrade -1')

if __name__ == '__main__':
    cli() 