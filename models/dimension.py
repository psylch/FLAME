from .base import db, BaseModel
from sqlalchemy.orm import relationship

class Dimension(BaseModel):
    """评估维度模型"""
    __tablename__ = 'dimensions'
    
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    scoring_guide = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Float, default=1.0)
    
    # 关系定义 - 使用backref实现双向关系
    samples = relationship('Sample', backref='dimension', lazy='dynamic',
                           cascade='all, delete-orphan')
    agents = relationship('Agent', backref='dimension', lazy='dynamic',
                          cascade='all, delete-orphan')
    
    @classmethod
    def get_by_name(cls, name):
        """通过名称获取维度"""
        return cls.query.filter_by(name=name).first()
    
    def __repr__(self):
        return f'<Dimension {self.name}>'