from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from contextlib import contextmanager
import logging

# 创建全局数据库对象
db = SQLAlchemy()

# 基础模型类
class BaseModel(db.Model):
    """所有模型的基类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_by_id(cls, id):
        """通过ID获取对象"""
        return cls.query.get(id)
    
    @classmethod
    def list_all(cls):
        """获取所有对象"""
        return cls.query.all()
    
    def save(self):
        """保存当前对象"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """删除当前对象"""
        db.session.delete(self)
        db.session.commit()

# 事务管理工具
@contextmanager
def transaction():
    """事务管理上下文，使用方法:
    
    with transaction():
        # 数据库操作
        # 如果发生异常，自动回滚
    """
    try:
        yield
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"事务回滚: {str(e)}")
        raise