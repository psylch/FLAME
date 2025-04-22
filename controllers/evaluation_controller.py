from flask import Blueprint, request, jsonify
from services.agent_service import AgentService

bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluation')

@bp.route('/agent', methods=['POST'])
def create_agent():
    """创建评估Agent"""
    data = request.json
    
    if not data or 'name' not in data or 'dimension_id' not in data or \
       'model_name' not in data or 'fewshot_example_ids' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    agent = AgentService.create_agent(
        name=data['name'],
        dimension_id=data['dimension_id'],
        model_name=data['model_name'],
        fewshot_example_ids=data['fewshot_example_ids']
    )
    
    if not agent:
        return jsonify({"error": "维度不存在"}), 404
    
    return jsonify({
        "id": agent.id,
        "name": agent.name,
        "dimension_id": agent.dimension_id,
        "model_name": agent.model_name,
        "version": agent.version,
        "is_active": agent.is_active,
        "created_at": agent.created_at.isoformat()
    }), 201

@bp.route('/agent/<int:agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """更新Agent"""
    data = request.json
    
    if not data:
        return jsonify({"error": "缺少更新数据"}), 400
    
    agent = AgentService.update_agent(
        agent_id=agent_id,
        name=data.get('name'),
        model_name=data.get('model_name'),
        fewshot_example_ids=data.get('fewshot_example_ids'),
        is_active=data.get('is_active')
    )
    
    if not agent:
        return jsonify({"error": "Agent不存在"}), 404
    
    return jsonify({
        "id": agent.id,
        "name": agent.name,
        "dimension_id": agent.dimension_id,
        "model_name": agent.model_name,
        "version": agent.version,
        "is_active": agent.is_active,
        "updated_at": agent.updated_at.isoformat()
    }), 200

@bp.route('/agent/dimension/<int:dimension_id>', methods=['GET'])
def get_active_agent(dimension_id):
    """获取指定维度的激活Agent"""
    agent = AgentService.get_active_agent_by_dimension(dimension_id)
    
    if not agent:
        return jsonify({"error": "未找到激活的Agent"}), 404
    
    return jsonify({
        "id": agent.id,
        "name": agent.name,
        "dimension_id": agent.dimension_id,
        "model_name": agent.model_name,
        "version": agent.version,
        "is_active": agent.is_active,
        "created_at": agent.created_at.isoformat()
    }), 200

@bp.route('/evaluate', methods=['POST'])
def evaluate_content():
    """评估内容"""
    data = request.json
    
    if not data or 'content' not in data or 'dimension_id' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    result = AgentService.evaluate_content(
        content=data['content'],
        dimension_id=data['dimension_id'],
        agent_id=data.get('agent_id')
    )
    
    if "error" in result:
        return jsonify(result), 400
    
    return jsonify(result), 200