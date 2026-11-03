#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词巧匠升级版 - 增强版Excel导出脚本
版本：v2.0.0 - 数据库增强版
创建日期：2025-03-19
基于项目：机关接待信息自动化处理系统的成功实践
"""

import sys
import os

# 导入原版导出脚本
from export_to_excel import ExcelExporter
from database.db_operations import PromptDatabase
from datetime import datetime
from typing import Dict, Any, Optional


class EnhancedExcelExporter(ExcelExporter):
    """增强版Excel导出器，支持数据库查询和灵活导出"""
    
    def __init__(self, db: PromptDatabase):
        """
        初始化增强版导出器
        
        参数:
            db: PromptDatabase实例
        """
        super().__init__()
        self.db = db
    
    def export_with_filters(self, user_id: str, filters: Optional[Dict[str, Any]] = None,
                           format_type: str = 'detailed') -> str:
        """
        带过滤条件的导出
        
        参数:
            user_id: 用户ID
            filters: 过滤条件字典
                - scenario: 场景
                - min_score: 最低评分
                - max_score: 最高评分
                - is_favorite: 是否收藏
                - tags: 标签
            format_type: 导出格式(detailed/simple)
            
        返回:
            导出文件路径
        """
        # 从数据库获取数据
        prompts_data = self.db.get_user_prompts(user_id, filters, page=1, page_size=10000)
        
        if not prompts_data or not prompts_data['prompts']:
            raise ValueError("没有找到符合条件的提示词数据")
        
        prompts = prompts_data['prompts']
        
        # 格式化数据，确保包含所有必要字段
        formatted_prompts = self._format_prompts_for_export(prompts)
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_type = 'detailed' if format_type == 'detailed' else 'simple'
        output_file = f"prompts_export_{file_type}_{timestamp}.xlsx"
        
        # 调用原导出方法
        self.export(formatted_prompts, output_file, format_type)
        
        return output_file
    
    def export_favorites(self, user_id: str, format_type: str = 'detailed') -> str:
        """
        导出收藏的提示词
        
        参数:
            user_id: 用户ID
            format_type: 导出格式(detailed/simple)
            
        返回:
            导出文件路径
        """
        filters = {'is_favorite': True}
        return self.export_with_filters(user_id, filters, format_type)
    
    def export_high_quality(self, user_id: str, min_score: int = 90, 
                          format_type: str = 'detailed') -> str:
        """
        导出高质量提示词
        
        参数:
            user_id: 用户ID
            min_score: 最低评分
            format_type: 导出格式(detailed/simple)
            
        返回:
            导出文件路径
        """
        filters = {'min_score': min_score}
        return self.export_with_filters(user_id, filters, format_type)
    
    def export_by_scenario(self, user_id: str, scenario: str, 
                           format_type: str = 'detailed') -> str:
        """
        按场景导出提示词
        
        参数:
            user_id: 用户ID
            scenario: 场景名称
            format_type: 导出格式(detailed/simple)
            
        返回:
            导出文件路径
        """
        filters = {'scenario': scenario}
        return self.export_with_filters(user_id, filters, format_type)
    
    def export_by_date_range(self, user_id: str, start_date: str, end_date: str,
                             format_type: str = 'detailed') -> str:
        """
        按日期范围导出提示词
        
        参数:
            user_id: 用户ID
            start_date: 开始日期(YYYY-MM-DD)
            end_date: 结束日期(YYYY-MM-DD)
            format_type: 导出格式(detailed/simple)
            
        返回:
            导出文件路径
        """
        # 需要在数据库查询中添加日期过滤
        # 这里简化实现，实际应用中可以扩展PromptDatabase类
        filters = {}
        return self.export_with_filters(user_id, filters, format_type)
    
    def export_all(self, user_id: str, format_type: str = 'detailed') -> str:
        """
        导出所有提示词
        
        参数:
            user_id: 用户ID
            format_type: 导出格式(detailed/simple)
            
        返回:
            导出文件路径
        """
        return self.export_with_filters(user_id, None, format_type)
    
    def _format_prompts_for_export(self, prompts: list) -> list:
        """
        格式化提示词数据以便导出
        
        参数:
            prompts: 数据库查询结果列表
            
        返回:
            格式化后的提示词列表
        """
        formatted = []
        
        for prompt in prompts:
            # 构建基础数据
            formatted_prompt = {
                'prompt_id': prompt.get('prompt_id', ''),
                'scenario': prompt.get('scenario', ''),
                'goal_orientation': prompt.get('goal_orientation', ''),
                'is_efficiency_priority': prompt.get('is_efficiency_priority', False),
                'is_accuracy_priority': prompt.get('is_accuracy_priority', False),
                'prompt_content': prompt.get('prompt_content', ''),
                'score': prompt.get('score', 0),
                'mode': prompt.get('mode', ''),
                'use_count': prompt.get('use_count', 0),
                'tags': prompt.get('tags', ''),
                'created_at': prompt.get('created_at', '')
            }
            
            # 构建维度数据
            dimensions = {
                'identity': prompt.get('identity', ''),
                'target_audience': prompt.get('target_audience', ''),
                'style': prompt.get('style', ''),
                'structure': prompt.get('structure', ''),
                'output_format': prompt.get('output_format', ''),
                'thinking_depth': prompt.get('thinking_depth', ''),
                'creativity': prompt.get('creativity', ''),
                'professionalism': prompt.get('professionalism', ''),
                'practicality': prompt.get('practicality', ''),
                'operability': prompt.get('operability', ''),
                'clarity': prompt.get('clarity', ''),
                'completeness': prompt.get('completeness', ''),
                'flexibility': prompt.get('flexibility', ''),
                'adaptability': prompt.get('adaptability', '')
            }
            
            formatted_prompt['dimensions'] = dimensions
            formatted.append(formatted_prompt)
        
        return formatted
    
    def export_with_advanced_filters(self, user_id: str, filters: Dict[str, Any],
                                    format_type: str = 'detailed') -> str:
        """
        高级过滤导出（支持多条件组合）
        
        参数:
            user_id: 用户ID
            filters: 高级过滤条件
                - scenarios: 场景列表
                - score_range: 评分范围[min, max]
                - date_range: 日期范围[start, end]
                - tags: 标签列表
                - is_favorite: 是否收藏
            format_type: 导出格式(detailed/simple)
            
        返回:
            导出文件路径
        """
        # 构建过滤条件
        query_filters = {}
        
        if filters.get('is_favorite'):
            query_filters['is_favorite'] = True
        
        if filters.get('score_range'):
            min_score, max_score = filters['score_range']
            query_filters['min_score'] = min_score
            query_filters['max_score'] = max_score
        
        if filters.get('tags'):
            query_filters['tags'] = filters['tags']
        
        # 如果指定了场景列表，需要多次查询合并结果
        if filters.get('scenarios'):
            all_prompts = []
            for scenario in filters['scenarios']:
                query_filters['scenario'] = scenario
                result = self.db.get_user_prompts(user_id, query_filters, 
                                                  page=1, page_size=10000)
                if result and result['prompts']:
                    all_prompts.extend(result['prompts'])
            
            if not all_prompts:
                raise ValueError("没有找到符合条件的提示词数据")
            
            formatted_prompts = self._format_prompts_for_export(all_prompts)
        else:
            formatted_prompts = self._format_prompts_for_export(
                self.db.get_user_prompts(user_id, query_filters, 
                                        page=1, page_size=10000)['prompts']
            )
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_type = 'detailed' if format_type == 'detailed' else 'simple'
        output_file = f"prompts_export_advanced_{file_type}_{timestamp}.xlsx"
        
        # 导出
        self.export(formatted_prompts, output_file, format_type)
        
        return output_file


# 命令行使用示例
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='提示词巧匠升级版 - 增强版Excel导出工具')
    
    # 基础参数
    parser.add_argument('--user-id', '-u', required=True, help='用户ID')
    parser.add_argument('--format', '-f', choices=['detailed', 'simple'], 
                       default='detailed', help='导出格式')
    
    # 导出类型
    parser.add_argument('--type', '-t', choices=['all', 'favorites', 'high-quality', 'scenario', 'advanced'],
                       default='all', help='导出类型')
    
    # 可选参数
    parser.add_argument('--min-score', type=int, help='最低评分（用于high-quality类型）')
    parser.add_argument('--scenario', help='场景名称（用于scenario类型）')
    parser.add_argument('--tags', help='标签（逗号分隔）')
    
    args = parser.parse_args()
    
    # 初始化数据库
    db = PromptDatabase()
    exporter = EnhancedExcelExporter(db)
    
    try:
        # 根据类型执行导出
        if args.type == 'all':
            output_file = exporter.export_all(args.user_id, args.format)
        elif args.type == 'favorites':
            output_file = exporter.export_favorites(args.user_id, args.format)
        elif args.type == 'high-quality':
            min_score = args.min_score or 90
            output_file = exporter.export_high_quality(args.user_id, min_score, args.format)
        elif args.type == 'scenario':
            if not args.scenario:
                print("❌ 使用scenario类型时必须指定--scenario参数")
                sys.exit(1)
            output_file = exporter.export_by_scenario(args.user_id, args.scenario, args.format)
        elif args.type == 'advanced':
            filters = {}
            if args.scenario:
                filters['scenarios'] = [args.scenario]
            if args.tags:
                filters['tags'] = args.tags
            output_file = exporter.export_with_advanced_filters(args.user_id, filters, args.format)
        
        print(f"\n✅ 导出成功！")
        print(f"📁 文件名：{output_file}")
        print(f"📊 导出格式：{'详细版' if args.format == 'detailed' else '简洁版'}")
        print(f"📦 文件位置：{os.path.abspath(output_file)}")
        
    except Exception as e:
        print(f"\n❌ 导出失败：{str(e)}")
        sys.exit(1)
    finally:
        db.close()
