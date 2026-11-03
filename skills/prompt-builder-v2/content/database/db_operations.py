#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提示词巧匠升级版 - 数据库操作核心类
版本：v2.0.0 - 数据库增强版
创建日期：2025-03-19
基于项目：机关接待信息自动化处理系统的成功实践
"""

import pymysql
from datetime import datetime
import json
from typing import List, Dict, Any, Optional


class PromptDatabase:
    """提示词数据库操作类"""
    
    def __init__(self, host='localhost', user='root', password='', database='prompt_builder_db', port=3306):
        """
        初始化数据库连接
        
        参数:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
            port: 数据库端口
        """
        try:
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print(f"✅ 数据库连接成功：{database}")
        except Exception as e:
            print(f"❌ 数据库连接失败：{str(e)}")
            raise
    
    def _generate_prompt_id(self) -> str:
        """生成唯一的提示词ID"""
        return f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def save_prompt(self, user_id: str, scenario: str, goal_orientation: str, 
                    prompt_content: str, score: int, mode: str, 
                    dimensions: Dict[str, str], tags: Optional[str] = None,
                    is_efficiency_priority: bool = False, is_accuracy_priority: bool = False) -> Optional[str]:
        """
        保存提示词到数据库
        
        参数:
            user_id: 用户ID
            scenario: 使用场景
            goal_orientation: 目标导向
            prompt_content: 提示词全文
            score: 评分(0-100)
            mode: 生成模式(fast/precision)
            dimensions: 14个维度字典
            tags: 标签(逗号分隔)
            is_efficiency_priority: 是否效率优先
            is_accuracy_priority: 是否准确性优先
            
        返回:
            提示词ID，失败返回None
        """
        try:
            with self.connection.cursor() as cursor:
                # 生成唯一ID
                prompt_id = self._generate_prompt_id()
                
                # 保存到prompts表
                sql = """
                INSERT INTO prompts (prompt_id, user_id, scenario, goal_orientation, 
                                   prompt_content, score, mode, tags, 
                                   is_efficiency_priority, is_accuracy_priority)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (prompt_id, user_id, scenario, goal_orientation,
                                   prompt_content, score, mode, tags,
                                   is_efficiency_priority, is_accuracy_priority))
                
                # 保存维度数据
                sql = """
                INSERT INTO prompt_dimensions (prompt_id, identity, target_audience, 
                                              style, structure, output_format, 
                                              thinking_depth, creativity, professionalism, 
                                              practicality, operability, clarity, 
                                              completeness, flexibility, adaptability)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (prompt_id, 
                                   dimensions.get('identity', ''),
                                   dimensions.get('target_audience', ''),
                                   dimensions.get('style', ''),
                                   dimensions.get('structure', ''),
                                   dimensions.get('output_format', ''),
                                   dimensions.get('thinking_depth', ''),
                                   dimensions.get('creativity', ''),
                                   dimensions.get('professionalism', ''),
                                   dimensions.get('practicality', ''),
                                   dimensions.get('operability', ''),
                                   dimensions.get('clarity', ''),
                                   dimensions.get('completeness', ''),
                                   dimensions.get('flexibility', ''),
                                   dimensions.get('adaptability', '')))
                
                # 保存版本历史
                sql = """
                INSERT INTO prompt_versions (prompt_id, version_number, prompt_content, 
                                            score, change_reason)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (prompt_id, 1, prompt_content, score, '初始版本'))
                
                self.connection.commit()
                print(f"✅ 提示词保存成功：{prompt_id}")
                return prompt_id
                
        except Exception as e:
            self.connection.rollback()
            print(f"❌ 保存提示词失败：{str(e)}")
            return None
    
    def get_user_prompts(self, user_id: str, filters: Optional[Dict[str, Any]] = None, 
                        page: int = 1, page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        获取用户历史提示词
        
        参数:
            user_id: 用户ID
            filters: 过滤条件字典
                - scenario: 场景
                - min_score: 最低评分
                - max_score: 最高评分
                - is_favorite: 是否收藏
                - tags: 标签
            page: 页码
            page_size: 每页数量
            
        返回:
            包含提示词列表和分页信息的字典
        """
        try:
            with self.connection.cursor() as cursor:
                # 构建查询条件
                where_clauses = ["user_id = %s"]
                params = [user_id]
                
                if filters:
                    if filters.get('scenario'):
                        where_clauses.append("scenario = %s")
                        params.append(filters['scenario'])
                    if filters.get('min_score'):
                        where_clauses.append("score >= %s")
                        params.append(filters['min_score'])
                    if filters.get('max_score'):
                        where_clauses.append("score <= %s")
                        params.append(filters['max_score'])
                    if filters.get('is_favorite'):
                        where_clauses.append("is_favorite = TRUE")
                    if filters.get('tags'):
                        where_clauses.append("tags LIKE %s")
                        params.append(f"%{filters['tags']}%")
                
                # 获取总数
                count_sql = f"""
                SELECT COUNT(*) as total 
                FROM prompts 
                WHERE {' AND '.join(where_clauses)}
                """
                cursor.execute(count_sql, params)
                total = cursor.fetchone()['total']
                
                # 分页查询
                offset = (page - 1) * page_size
                sql = f"""
                SELECT p.*, d.* 
                FROM prompts p
                LEFT JOIN prompt_dimensions d ON p.prompt_id = d.prompt_id
                WHERE {' AND '.join(where_clauses)}
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
                """
                cursor.execute(sql, params + [page_size, offset])
                results = cursor.fetchall()
                
                return {
                    'total': total,
                    'prompts': results,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }
                
        except Exception as e:
            print(f"❌ 查询提示词失败：{str(e)}")
            return None
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        根据提示词ID获取详细信息
        
        参数:
            prompt_id: 提示词ID
            
        返回:
            提示词详细信息字典
        """
        try:
            with self.connection.cursor() as cursor:
                sql = """
                SELECT p.*, d.* 
                FROM prompts p
                LEFT JOIN prompt_dimensions d ON p.prompt_id = d.prompt_id
                WHERE p.prompt_id = %s
                """
                cursor.execute(sql, [prompt_id])
                result = cursor.fetchone()
                
                if result:
                    # 获取版本历史
                    version_sql = """
                    SELECT * FROM prompt_versions 
                    WHERE prompt_id = %s 
                    ORDER BY version_number DESC
                    """
                    cursor.execute(version_sql, [prompt_id])
                    versions = cursor.fetchall()
                    result['versions'] = versions
                
                return result
                
        except Exception as e:
            print(f"❌ 获取提示词详情失败：{str(e)}")
            return None
    
    def get_recommended_prompts(self, user_id: str, scenario: Optional[str] = None, 
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取优质提示词推荐
        
        参数:
            user_id: 用户ID
            scenario: 场景(可选)
            limit: 返回数量限制
            
        返回:
            提示词列表
        """
        try:
            with self.connection.cursor() as cursor:
                if scenario:
                    sql = """
                    SELECT p.*, d.* 
                    FROM prompts p
                    LEFT JOIN prompt_dimensions d ON p.prompt_id = d.prompt_id
                    WHERE p.score >= 90
                    AND p.user_id = %s
                    AND p.scenario = %s
                    ORDER BY p.use_count DESC, p.score DESC
                    LIMIT %s
                    """
                    cursor.execute(sql, [user_id, scenario, limit])
                else:
                    sql = """
                    SELECT p.*, d.* 
                    FROM prompts p
                    LEFT JOIN prompt_dimensions d ON p.prompt_id = d.prompt_id
                    WHERE p.score >= 90
                    AND p.user_id = %s
                    ORDER BY p.use_count DESC, p.score DESC
                    LIMIT %s
                    """
                    cursor.execute(sql, [user_id, limit])
                
                results = cursor.fetchall()
                return results
                
        except Exception as e:
            print(f"❌ 获取推荐提示词失败：{str(e)}")
            return []
    
    def update_prompt_stats(self, prompt_id: str, action: str = 'use') -> bool:
        """
        更新提示词使用统计
        
        参数:
            prompt_id: 提示词ID
            action: 操作类型('use'/'favorite')
            
        返回:
            是否成功
        """
        try:
            with self.connection.cursor() as cursor:
                if action == 'use':
                    sql = "UPDATE prompts SET use_count = use_count + 1 WHERE prompt_id = %s"
                elif action == 'favorite':
                    sql = "UPDATE prompts SET is_favorite = NOT is_favorite WHERE prompt_id = %s"
                else:
                    print(f"❌ 不支持的操作类型：{action}")
                    return False
                
                cursor.execute(sql, [prompt_id])
                self.connection.commit()
                print(f"✅ 提示词统计更新成功：{action}")
                return True
                
        except Exception as e:
            print(f"❌ 更新统计失败：{str(e)}")
            return False
    
    def save_prompt_version(self, prompt_id: str, prompt_content: str, 
                           score: int, change_reason: str) -> bool:
        """
        保存提示词新版本
        
        参数:
            prompt_id: 提示词ID
            prompt_content: 提示词内容
            score: 评分
            change_reason: 修改原因
            
        返回:
            是否成功
        """
        try:
            with self.connection.cursor() as cursor:
                # 获取当前版本号
                version_sql = """
                SELECT MAX(version_number) as max_version 
                FROM prompt_versions 
                WHERE prompt_id = %s
                """
                cursor.execute(version_sql, [prompt_id])
                result = cursor.fetchone()
                version_number = (result['max_version'] or 0) + 1
                
                # 插入新版本
                sql = """
                INSERT INTO prompt_versions (prompt_id, version_number, prompt_content, 
                                           score, change_reason)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (prompt_id, version_number, prompt_content, 
                                   score, change_reason))
                
                self.connection.commit()
                print(f"✅ 提示词版本保存成功：版本 {version_number}")
                return True
                
        except Exception as e:
            print(f"❌ 保存提示词版本失败：{str(e)}")
            return False
    
    def get_user_statistics(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        获取用户统计信息
        
        参数:
            user_id: 用户ID
            
        返回:
            统计信息字典
        """
        try:
            with self.connection.cursor() as cursor:
                sql = """
                SELECT * FROM prompt_statistics 
                WHERE user_id = %s
                """
                cursor.execute(sql, [user_id])
                result = cursor.fetchone()
                
                if result:
                    # 获取最近30天新增数量
                    recent_sql = """
                    SELECT COUNT(*) as recent_count 
                    FROM prompts 
                    WHERE user_id = %s 
                    AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    """
                    cursor.execute(recent_sql, [user_id])
                    recent_result = cursor.fetchone()
                    result['recent_count'] = recent_result['recent_count']
                
                return result
                
        except Exception as e:
            print(f"❌ 获取用户统计失败：{str(e)}")
            return None
    
    def search_prompts(self, user_id: str, keyword: str, page: int = 1, 
                      page_size: int = 20) -> Optional[Dict[str, Any]]:
        """
        全文搜索提示词
        
        参数:
            user_id: 用户ID
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            
        返回:
            搜索结果字典
        """
        try:
            with self.connection.cursor() as cursor:
                # 获取总数
                count_sql = """
                SELECT COUNT(*) as total 
                FROM prompts 
                WHERE user_id = %s 
                AND (prompt_content LIKE %s OR tags LIKE %s)
                """
                search_pattern = f"%{keyword}%"
                cursor.execute(count_sql, [user_id, search_pattern, search_pattern])
                total = cursor.fetchone()['total']
                
                # 分页查询
                offset = (page - 1) * page_size
                sql = """
                SELECT p.*, d.* 
                FROM prompts p
                LEFT JOIN prompt_dimensions d ON p.prompt_id = d.prompt_id
                WHERE p.user_id = %s 
                AND (p.prompt_content LIKE %s OR p.tags LIKE %s)
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
                """
                cursor.execute(sql, [user_id, search_pattern, search_pattern, page_size, offset])
                results = cursor.fetchall()
                
                return {
                    'total': total,
                    'prompts': results,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size,
                    'keyword': keyword
                }
                
        except Exception as e:
            print(f"❌ 搜索提示词失败：{str(e)}")
            return None
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """
        删除提示词（级联删除相关数据）
        
        参数:
            prompt_id: 提示词ID
            
        返回:
            是否成功
        """
        try:
            with self.connection.cursor() as cursor:
                sql = "DELETE FROM prompts WHERE prompt_id = %s"
                cursor.execute(sql, [prompt_id])
                self.connection.commit()
                print(f"✅ 提示词删除成功：{prompt_id}")
                return True
                
        except Exception as e:
            print(f"❌ 删除提示词失败：{str(e)}")
            return False
    
    def batch_delete_prompts(self, prompt_ids: List[str]) -> bool:
        """
        批量删除提示词
        
        参数:
            prompt_ids: 提示词ID列表
            
        返回:
            是否成功
        """
        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(prompt_ids))
                sql = f"DELETE FROM prompts WHERE prompt_id IN ({placeholders})"
                cursor.execute(sql, prompt_ids)
                self.connection.commit()
                print(f"✅ 批量删除提示词成功：{len(prompt_ids)} 个")
                return True
                
        except Exception as e:
            print(f"❌ 批量删除提示词失败：{str(e)}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("✅ 数据库连接已关闭")


# 使用示例
if __name__ == '__main__':
    # 初始化数据库连接
    db = PromptDatabase(
        host='localhost',
        user='root',
        password='',
        database='prompt_builder_db'
    )
    
    # 测试保存提示词
    test_prompt_id = db.save_prompt(
        user_id='U001',
        scenario='文案撰写',
        goal_orientation='创造性优先',
        prompt_content='你是一位拥有10年经验的资深营销专家...',
        score=95,
        mode='precision',
        dimensions={
            'identity': '资深营销专家',
            'target_audience': '25-35岁年轻白领',
            'style': '轻松活泼',
            'structure': '段落式',
            'output_format': '小红书社交媒体',
            'thinking_depth': '明确产品核心卖点',
            'creativity': '突出差异化优势',
            'professionalism': '营销专业视角',
            'practicality': '具体参数支持',
            'operability': '明确的字数和结构要求',
            'clarity': '要素完整，逻辑清晰',
            'completeness': '涵盖所有关键要素',
            'flexibility': '可适配类似产品',
            'adaptability': '精准匹配目标平台'
        },
        tags='营销,小红书,产品文案'
    )
    
    print(f"\n📋 提示词ID：{test_prompt_id}")
    
    # 测试查询
    results = db.get_user_prompts('U001', page=1, page_size=10)
    if results:
        print(f"\n📊 查询结果：共 {results['total']} 条记录")
    
    # 测试推荐
    recommended = db.get_recommended_prompts('U001', limit=5)
    print(f"\n⭐ 推荐提示词：{len(recommended)} 条")
    
    # 关闭连接
    db.close()
