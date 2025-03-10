from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from sqlalchemy import MetaData
import os
import importlib
import inspect

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# 自动导入所有模型并合并原数据
def combine_all_models_metadata():
    from sqlalchemy.ext.declarative import declarative_base
    
    # 定义元数据合并函数
    def combine_metadata(*args):
        m = MetaData()
        for metadata in args:
            for t in metadata.tables.values():
                t.tometadata(m)
        return m
    
    # 获取所有模型文件 mac方法可以，window上会报错
    # models_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src', 'sql', 'models')
    # 上面的方法models_path在window上会报错，所以使用下面的方法，兼容
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    models_path = os.path.join(project_root, 'src', 'sql', 'models')
    
    # 调试信息
    print(f"查找模型的路径: {models_path}")
    print(f"该路径是否存在: {os.path.exists(models_path)}")
    all_metadata = []
    
    # 导入模型目录下的所有 .py 文件
    for filename in os.listdir(models_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f'src.sql.models.{filename[:-3]}'
            module = importlib.import_module(module_name)
            
            # 查找模块中的 Base 类
            for item_name, item in inspect.getmembers(module):
                if item_name == 'Base' and isinstance(item, type(declarative_base())):
                    all_metadata.append(item.metadata)
                    print(f"找到并添加模型: {module_name}")
    
    if not all_metadata:
        raise Exception("未找到任何模型的元数据!")
    
    # 合并所有元数据
    return combine_metadata(*all_metadata)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = test.Base.metadata
target_metadata = combine_all_models_metadata()

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
