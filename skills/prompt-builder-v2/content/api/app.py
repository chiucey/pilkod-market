#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词巧匠升级版 - Flask API服务
版本：v2.0.0 - 数据库增强版
创建日期：2025-03-19
基于项目：机关接待信息自动化处理系统的成功实践
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_operations import PromptDatabase

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化数据库连接（请根据实际情况修改配置）
db = PromptDatabase(
    host='localhost',
    user='root',
    password='',
    database='prompt_builder_db',
    port=3306
)


# =====================================================
# 健康检查接口
# =====================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'service': 'Prompt Builder API',
        'version': '2.0.0'
    })


# =====================================================
# 提示词管理接口
# =====================================================
@app.route('/api/prompts', methods=['POST'])
def save_prompt():
    """保存提示词"""
    try:
        data = request.json
        
        # 验证必填字段
        required_fields = ['user_id', 'scenario', 'goal_orientation', 
                          'prompt_content', 'score', 'mode', 'dimensions']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必填字段：{field}'
                }), 400
        
        # 保存提示词
        prompt_id = db.save_prompt(
            user_id=data.get('user_id'),
            scenario=data.get('scenario'),
            goal_orientation=data.get('goal_orientation'),
            prompt_content=data.get('prompt_content'),
            score=data.get('score'),
            mode=data.get('mode'),
            dimensions=data.get('dimensions'),
            tags=data.get('tags'),
            is_efficiency_priority=data.get('is_efficiency_priority', False),
            is_accuracy_priority=data.get('is_accuracy_priority', False)
        )
        
        if prompt_id:
            return jsonify({
                'prompt_id': prompt_id,
                'status': 'success',
                'message': '提示词保存成功'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': '提示词保存失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/api/prompts/<user_id>', methods=['GET'])
def get_prompts(user_id):
    """获取用户提示词列表"""
    try:
        # 获取过滤条件
        filters = {}
        if request.args.get('scenario'):
            filters['scenario'] = request.args.get('scenario')
        if request.args.get('min_score'):
            filters['min_score'] = int(request.args.get('min_score'))
        if request.args.get('max_score'):
            filters['max_score'] = int(request.args.get('max_score'))
        if request.args.get('is_favorite'):
            filters['is_favorite'] = True
        if request.args.get('tags'):
            filters['tags'] = request.args.get('tags')
        
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 查询提示词
        results = db.get_user_prompts(user_id, filters, page, page_size)
        
        if results:
            return jsonify({
                'status': 'success',
                'data': results
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '查询失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/api/prompts/detail/<prompt_id>', methods=['GET'])
def get_prompt_detail(prompt_id):
    """获取提示词详细信息"""
    try:
        result = db.get_prompt_by_id(prompt_id)
        
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '提示词不存在'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """删除提示词"""
    try:
        success = db.delete_prompt(prompt_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '提示词删除成功'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '提示词删除失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/api/prompts/batch-delete', methods=['POST'])
def batch_delete_prompts():
    """批量删除提示词"""
    try:
        data = request.json
        prompt_ids = data.get('prompt_ids', [])
        
        if not prompt_ids:
            return jsonify({
                'status': 'error',
                'message': '请提供要删除的提示词ID列表'
            }), 400
        
        success = db.batch_delete_prompts(prompt_ids)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'成功删除 {len(prompt_ids)} 个提示词'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '批量删除失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


# =====================================================
# 推荐与统计接口
# =====================================================
@app.route('/api/prompts/<user_id>/recommend', methods=['GET'])
def get_recommendations(user_id):
    """获取推荐提示词"""
    try:
        scenario = request.args.get('scenario')
        limit = int(request.args.get('limit', 10))
        
        prompts = db.get_recommended_prompts(user_id, scenario, limit)
        
        return jsonify({
            'status': 'success',
            'data': {
                'prompts': prompts,
                'count': len(prompts)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/api/prompts/<user_id>/search', methods=['GET'])
def search_prompts(user_id):
    """全文搜索提示词"""
    try:
        keyword = request.args.get('keyword')
        if not keyword:
            return jsonify({
                'status': 'error',
                'message': '请提供搜索关键词'
            }), 400
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        results = db.search_prompts(user_id, keyword, page, page_size)
        
        if results:
            return jsonify({
                'status': 'success',
                'data': results
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '搜索失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/api/users/<user_id>/statistics', methods=['GET'])
def get_user_statistics(user_id):
    """获取用户统计信息"""
    try:
        stats = db.get_user_statistics(user_id)
        
        if stats:
            return jsonify({
                'status': 'success',
                'data': stats
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '获取统计信息失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


# =====================================================
# 统计更新接口
# =====================================================
@app.route('/api/prompts/<prompt_id>/stats', methods=['PUT'])
def update_stats(prompt_id):
    """更新提示词统计"""
    try:
        data = request.json
        action = data.get('action', 'use')
        
        if action not in ['use', 'favorite']:
            return jsonify({
                'status': 'error',
                'message': '不支持的操作类型'
            }), 400
        
        success = db.update_prompt_stats(prompt_id, action)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '统计更新成功'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '统计更新失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


# =====================================================
# 版本管理接口
# =====================================================
@app.route('/api/prompts/<prompt_id>/versions', methods=['POST'])
def save_prompt_version(prompt_id):
    """保存提示词新版本"""
    try:
        data = request.json
        
        # 验证必填字段
        required_fields = ['prompt_content', 'score', 'change_reason']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必填字段：{field}'
                }), 400
        
        success = db.save_prompt_version(
            prompt_id=prompt_id,
            prompt_content=data.get('prompt_content'),
            score=data.get('score'),
            change_reason=data.get('change_reason')
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': '版本保存成功'
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': '版本保存失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'服务器错误：{str(e)}'
        }), 500


# =====================================================
# 错误处理
# =====================================================
@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'status': 'error',
        'message': '请求的资源不存在'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误'
    }), 500


# =====================================================
# 主程序入口
# =====================================================
if __name__ == '__main__':
    print('🚀 启动提示词巧匠升级版API服务...')
    print('📡 API服务地址：http://localhost:5000')
    print('📚 API文档：http://localhost:5000/api/documentation')
    print('\n可用的API端点：')
    print('  POST   /api/prompts                    - 保存提示词')
    print('  GET    /api/prompts/<user_id>           - 获取提示词列表')
    print('  GET    /api/prompts/detail/<prompt_id>  - 获取提示词详情')
    print('  DELETE /api/prompts/<prompt_id>          - 删除提示词')
    print('  POST   /api/prompts/batch-delete        - 批量删除提示词')
    print('  GET    /api/prompts/<user_id>/recommend  - 获取推荐提示词')
    print('  GET    /api/prompts/<user_id>/search     - 搜索提示词')
    print('  GET    /api/users/<user_id>/statistics  - 获取用户统计')
    print('  PUT    /api/prompts/<prompt_id>/stats    - 更新提示词统计')
    print('  POST   /api/prompts/<prompt_id>/versions  - 保存提示词版本')
    print('\n按 Ctrl+C 停止服务')
    
    app.run(host='0.0.0.0', port=5000, debug=True)
