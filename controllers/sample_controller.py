from flask import Blueprint, request, jsonify
from services.sample_service import SampleService

bp = Blueprint('sample', __name__, url_prefix='/api/samples')

@bp.route('/', methods=['POST'])
def create_sample():
    """创建新样本"""
    data = request.json
    
    if not data or 'content' not in data or 'dimension_id' not in data:
        return jsonify({"error": "缺少必要参数"}), 400
    
    sample = SampleService.create_sample(
        content=data['content'],
        dimension_id=data['dimension_id'],
        metadata=data.get('metadata')
    )
    
    return jsonify({
        "id": sample.id,
        "content": sample.content,
        "dimension_id": sample.dimension_id,
        "metadata": sample.metadata,
        "created_at": sample.created_at.isoformat()
    }), 201

@bp.route('/dimension/<int:dimension_id>', methods=['GET'])
def get_samples_by_dimension(dimension_id):
    """获取指定维度的所有样本"""
    samples = SampleService.get_samples_by_dimension(dimension_id)
    
    return jsonify([{
        "id": sample.id,
        "content": sample.content,
        "dimension_id": sample.dimension_id,
        "metadata": sample.metadata,
        "created_at": sample.created_at.isoformat()
    } for sample in samples]), 200

@bp.route('/<int:sample_id>', methods=['GET'])
def get_sample(sample_id):
    """获取指定ID的样本"""
    sample = SampleService.get_sample(sample_id)
    
    if not sample:
        return jsonify({"error": "样本不存在"}), 404
    
    return jsonify({
        "id": sample.id,
        "content": sample.content,
        "dimension_id": sample.dimension_id,
        "metadata": sample.metadata,
        "created_at": sample.created_at.isoformat()
    }), 200

@bp.route('/<int:sample_id>', methods=['PUT'])
def update_sample(sample_id):
    """更新样本"""
    data = request.json
    
    if not data:
        return jsonify({"error": "缺少更新数据"}), 400
    
    sample = SampleService.update_sample(
        sample_id=sample_id,
        content=data.get('content'),
        metadata=data.get('metadata')
    )
    
    if not sample:
        return jsonify({"error": "样本不存在"}), 404
    
    return jsonify({
        "id": sample.id,
        "content": sample.content,
        "dimension_id": sample.dimension_id,
        "metadata": sample.metadata,
        "updated_at": sample.updated_at.isoformat()
    }), 200

@bp.route('/<int:sample_id>', methods=['DELETE'])
def delete_sample(sample_id):
    """删除样本"""
    result = SampleService.delete_sample(sample_id)
    
    if not result:
        return jsonify({"error": "样本不存在或删除失败"}), 404
    
    return jsonify({"message": "样本删除成功"}), 200