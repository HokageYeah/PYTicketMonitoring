# src/sql/sql_connect_db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging

# 创建基类，用于声明模型
Base = declarative_base()

class Database:
    def __init__(self):
        self.db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'aa123456',
            'database': 'ticket_monitor_db',
            "pool_name": "mypool", # 连接池名称
            "pool_size": 5 # 连接池大小
        }
        self.db_url = f"mysql+mysqlconnector://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}"
        self._engine = None
        self._session_factory = None

    def connect(self) -> None:
        """初始化数据库连接"""
        try:
            # 创建引擎，配置连接池
            self._engine = create_engine(
                self.db_url,
                poolclass=QueuePool,
                pool_size=self.db_config['pool_size'],
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600,
                echo=False
            )
            
            # 创建会话工厂
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )

            # 测试连接
            session = self._session_factory()
            try:
                session.execute(text("SELECT 1"))
                logging.info("sqlalchemy数据库连接成功")
            finally:
                session.close()

        except Exception as e:
            logging.error(f"sqlalchemy数据库连接失败: {e}")
            raise

    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话"""
        if not self._session_factory:
            raise RuntimeError("sqlalchemy数据库未初始化，请先调用 connect()")
            
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def close(self) -> None:
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()
            logging.info("sqlalchemy数据库连接已关闭")

# 创建全局数据库实例
database = Database()

# 获取数据库会话的依赖函数
def get_sqlalchemy_db() -> Generator[Session, None, None]:
    return next(database.get_session())
