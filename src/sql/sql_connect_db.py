import mysql.connector
from mysql.connector.pooling import PooledMySQLConnection
from typing import Optional
from mysql.connector.cursor import MySQLCursor
# 创建数据库连接类
class SqlConnectDb:
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
        self.pool = None
        self.connection = None
        self.cursor = None

    def connect(self) -> Optional[PooledMySQLConnection]:
        """
        创建数据库连接池并返回一个连接
        """
        try:
            # 创建连接池
            self.pool = mysql.connector.pooling.MySQLConnectionPool(**self.db_config)
            # 从连接池获取连接
            self.connection = self.pool.get_connection()
            # 创建一个数据库游标对象，用于执行SQL命令
            self.cursor = self.connection.cursor()
            # 执行一个简单的SQL测试查询：计算 1+1
            # 这是一个常用的数据库连接测试方法，因为它简单且能确保数据库正常响应
            self.cursor.execute("SELECT 1 + 1")
            # 获取查询结果
            # 如果连接正常，将返回 [(2,)]
            self.cursor.fetchall()
            # 打印连接成功信息
            print("数据库连接成功！")
            # 返回连接对象
            return self.connection
            
        except Exception as error:
            print("数据库连接失败：", error)
            raise error
    def get_cursor(self) -> Optional[MySQLCursor]:
        """
        获取数据库游标
        """
        if self.connection:
            return self.connection.cursor()
        return None

    def execute_query(self, query: str, params: tuple = None) -> list:
        """
        执行SQL查询
        """
        try:
            cursor = self.get_cursor()
            if cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
                return result
        except Exception as error:
            print(f"查询执行失败：{error}")
            raise error
        finally:
            if cursor:
                cursor.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        执行更新操作（INSERT, UPDATE, DELETE）
        """
        try:
            cursor = self.get_cursor()
            if cursor:
                cursor.execute(query, params)
                self.connection.commit()
                return cursor.rowcount
        except Exception as error:
            if self.connection:
                self.connection.rollback()
            print(f"更新执行失败：{error}")
            raise error
        finally:
            if cursor:
                cursor.close()

    def close(self):
        """
        关闭数据库连接
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            print("数据库连接已关闭")
        except Exception as error:
            print(f"关闭连接失败：{error}")
