
from src.sql.sqlalchemy_db import get_sqlalchemy_db

class MonitorDbOperate:
    def __init__(self):
        self.sqlalchemy_db = get_sqlalchemy_db()
    
    def add_show_sql(self):
        self.sqlalchemy_db.engine.echo = True
