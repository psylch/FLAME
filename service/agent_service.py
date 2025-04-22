from models.base import db, transaction
from models.agent import Agent
from models.evaluation import ExpertEvaluation, UserEvaluation
from models.dimension import Dimension
from models.sample import Sample
from utils.openai_client import OpenAIClient

class AgentService:
    """Agent构建和评估服务"""
    
    @staticmethod
    def create_agent(name, dimension_id, model_name, evaluation_ids):
        """创建评估Agent
        
        Args:
            name: Agent名称
            dimension_id: 评估维度ID
            model_name: 使用的模型名称
            evaluation_ids: 专家评估ID列表
            
        Returns:
            Agent: 创建的Agent对象
        """
        # 检查维度是否存在
        dimension = Dimension.get_by_id(dimension_id)
        if not dimension:
            return None
            
        # 创建Agent
        with transaction():
            # 将当前维度的所有Agent设为非激活
            existing_agents = Agent.query.filter_by(dimension_id=dimension_id, is_active=True).all()
            for agent in existing_agents:
                agent.is_active = False
                agent.save()
                
            # 创建新Agent
            agent = Agent(
                name=name,
                dimension_id=dimension_id,
                model_name=model_name,
                version=1,
                is_active=True
            )
            agent.save()
            
            # 添加few-shot示例
            for eval_id in evaluation_ids:
                evaluation = ExpertEvaluation.get_by_id(eval_id)
                if evaluation:
                    agent.add_example(evaluation)
            
            db.session.commit()
            
        return agent
    
    @staticmethod
    def evaluate_content(content, dimension_id, agent_id=None):
        """使用Agent评估内容
        
        Args:
            content: 待评估内容
            dimension_id: 维度ID
            agent_id: Agent ID，若为None则使用该维度的激活Agent
            
        Returns:
            dict: 评估结果
        """
        # 获取Agent
        if agent_id:
            agent = Agent.get_by_id(agent_id)
        else:
            agent = Agent.get_active_for_dimension(dimension_id)
        
        if not agent:
            return {"error": "未找到可用的评估Agent"}
        
        # 获取维度
        dimension = Dimension.get_by_id(dimension_id)
        if not dimension:
            return {"error": "未找到评估维度"}
        
        # 获取few-shot示例
        examples = agent.get_examples()
        if not examples:
            return {"error": "未找到few-shot示例"}
        
        # 初始化OpenAI客户端
        openai_client = OpenAIClient(model=agent.model_name)
        
        # 准备few-shot示例数据
        fewshot_data = []
        for example in examples:
            sample = Sample.get_by_id(example.sample_id)
            if sample:
                fewshot_data.append({
                    "content": sample.content,
                    "score": example.score,
                    "rationale": example.rationale
                })
        
        # 调用评估
        result = openai_client.get_evaluation(content, fewshot_data, dimension)
        
        # 记录评估结果
        if "error" not in result:
            with transaction():
                evaluation = UserEvaluation(
                    content=content,
                    dimension_id=dimension_id,
                    agent_id=agent.id,
                    score=result["score"],
                    rationale=result["rationale"]
                )
                evaluation.save()
        
        return result