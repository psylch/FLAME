from flask import Blueprint, request, jsonify
from services.expert_service import ExpertService

bp = Blueprint('expert', __name__, url_prefix='/api/experts')

@bp.route('/evaluate', methods=['POST'])
def evaluate_sample():
    """专家评估样本"""
    data = request.json
    
    if not data or 'sample_id' not in data or 'dimension_id' not in data or \
       'score' not in data or 'rationale' not in data or 'expert_name' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    evaluation = ExpertService.evaluate_sample(
        sample_id=data['sample_id'],
        dimension_id=data['dimension_id'],
        score=data['score'],
        rationale=data['rationale'],
        expert_name=data['expert_name']
    )
    
    if not evaluation:
        return jsonify({"error": "样本或维度不存在"}), 404
    
    return jsonify({
        "id": evaluation.id,
        "sample_id": evaluation.sample_id,
        "dimension_id": evaluation.dimension_id,
        "score": evaluation.score,
        "rationale": evaluation.rationale,
        "expert_name": evaluation.expert_name,
        "created_at": evaluation.created_at.isoformat()
    }), 201

@bp.route('/sample/<int:sample_id>', methods=['GET'])
def get_evaluations_by_sample(sample_id):
    """获取指定样本的所有专家评估"""
    evaluations = ExpertService.get_evaluations_by_sample(sample_id)
    
    return jsonify([{
        "id": evaluation.id,
        "sample_id": evaluation.sample_id,
        "dimension_id": evaluation.dimension_id,
        "score": evaluation.score,
        "rationale": evaluation.rationale,
        "expert_name": evaluation.expert_name,
        "created_at": evaluation.created_at.isoformat()
    } for evaluation in evaluations]), 200

@bp.route('/dimension/<int:dimension_id>', methods=['GET'])
def get_evaluations_by_dimension(dimension_id):
    """获取指定维度的所有专家评估"""
    evaluations = ExpertService.get_evaluations_by_dimension(dimension_id)
    
    return jsonify([{
        "id": evaluation.id,
        "sample_id": evaluation.sample_id,
        "dimension_id": evaluation.dimension_id,
        "score": evaluation.score,
        "rationale": evaluation.rationale,
        "expert_name": evaluation.expert_name,
        "created_at": evaluation.created_at.isoformat()
    } for evaluation in evaluations]), 200