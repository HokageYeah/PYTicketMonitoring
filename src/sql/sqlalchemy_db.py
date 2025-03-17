# src/sql/sql_connect_db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging
from src.config.database_config import get_database_config, DATABASE_URL
# 创建基类，用于声明模型
Base = declarative_base()

class Database:
    def __init__(self):
        self.db_config = get_database_config()
        self.db_url = DATABASE_URL
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
                max_overflow=self.db_config['max_overflow'],
                pool_timeout=self.db_config['pool_timeout'],
                pool_recycle=self.db_config['pool_recycle'],
                echo=self.db_config['echo']
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
    """获取数据库会话"""
    db = next(database.get_session())
    try:
        return db
    except Exception as e:
        db.close()
        logging.error(f"获取数据库会话失败: {e}")
        raise
    finally:
        print('数据库会话关闭')
        db.close()
