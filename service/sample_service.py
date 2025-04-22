from models.base import db, transaction
from models.sample import Sample
from models.dimension import Dimension

class SampleService:
    """样本管理服务"""
    
    @staticmethod
    def create_sample(content, dimension_id, metadata=None):
        """创建新样本
        
        Args:
            content: 样本内容
            dimension_id: 评估维度ID
            metadata: 样本元数据
            
        Returns:
            Sample: 创建的样本对象
        """
        # 检查维度是否存在
        dimension = Dimension.get_by_id(dimension_id)
        if not dimension:
            return None
            
        sample = Sample(
            content=content,
            dimension_id=dimension_id,
            metadata=metadata or {}
        )
        
        # 使用事务上下文
        with transaction():
            sample.save()
        
        return sample
    
    @staticmethod
    def get_samples_by_dimension(dimension_id):
        """获取指定维度的所有样本
        
        Args:
            dimension_id: 评估维度ID
            
        Returns:
            list: 样本列表
        """
        return Sample.get_by_dimension(dimension_id)
    
    @staticmethod
    def get_sample(sample_id):
        """获取指定ID的样本
        
        Args:
            sample_id: 样本ID
            
        Returns:
            Sample: 样本对象
        """
        return Sample.get_by_id(sample_id)
    
    @staticmethod
    def update_sample(sample_id, content=None, metadata=None):
        """更新样本
        
        Args:
            sample_id: 样本ID
            content: 新样本内容
            metadata: 新样本元数据
            
        Returns:
            Sample: 更新后的样本对象
        """
        sample = Sample.get_by_id(sample_id)
        if not sample:
            return None
        
        if content is not None:
            sample.content = content
        
        if metadata is not None:
            sample.metadata = metadata
        
        # 使用事务上下文
        with transaction():
            sample.save()
            
        return sample
    
    @staticmethod
    def delete_sample(sample_id):
        """删除样本
        
        Args:
            sample_id: 样本ID
            
        Returns:
            bool: 是否成功删除
        """
        sample = Sample.get_by_id(sample_id)
        if not sample:
            return False
        
        with transaction():
            sample.delete()
        
        return True