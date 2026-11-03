#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上传处理模块 - 支持手动CSV上传和不定时追加
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from .updater import IncrementalUpdater


class CSVUploader:
    """CSV上传处理器"""

    # 支持的字段映射
    FIELD_MAPPING = {
        # 标准字段
        '姓名': 'name',
        'name': 'name',
        '姓名': 'name',

        '职务': 'position',
        'position': 'position',
        'position_title': 'position',

        '任命/免去': 'action',
        'action': 'action',
        '类型': 'action',
        '任免类型': 'action',

        '时间': 'date',
        'date': 'date',
        '日期': 'date',
        '任职时间': 'date',

        '文号': 'doc_no',
        'doc_no': 'doc_no',
        'document_number': 'doc_no',
        '文编号': 'doc_no',

        '来源': 'source',
        'source': 'source',

        '说明': 'note',
        '备注': 'note',
        'note': 'note',
    }

    def __init__(self, data_dir: str = './data'):
        self.data_dir = Path(data_dir)
        self.updater = IncrementalUpdater(data_dir)

    def validate_csv(self, file_path: str) -> Dict:
        """
        验证CSV文件格式

        Returns:
            验证结果，包含是否有效和错误信息
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'fields_found': [],
            'rows_count': 0,
            'suggestions': []
        }

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                # 尝试多种分隔符
                content = f.read()
                if '\t' in content and ',' not in content:
                    delimiter = '\t'
                elif ';' in content:
                    delimiter = ';'
                else:
                    delimiter = ','

                f.seek(0)
                reader = csv.DictReader(f, delimiter=delimiter)

                if not reader.fieldnames:
                    result['errors'].append('文件为空或无法解析')
                    return result

                result['fields_found'] = reader.fieldnames

                # 检查必需字段
                first_row = next(reader, None)
                if first_row:
                    result['rows_count'] = 1

                    # 尝试匹配字段
                    matched_fields = []
                    for field in reader.fieldnames:
                        mapped = self.FIELD_MAPPING.get(field.strip(), '')
                        if mapped:
                            matched_fields.append(mapped)
                        else:
                            # 尝试模糊匹配
                            for key, value in self.FIELD_MAPPING.items():
                                if key in field or field in key:
                                    result['warnings'].append(f"字段 '{field}' 可能对应 '{value}'")
                                    break

                    # 必需字段检查
                    required = ['name', 'position', 'action']
                    missing = [r for r in required if r not in matched_fields]

                    if missing:
                        result['warnings'].append(f"缺少建议字段: {', '.join(missing)}")

                    result['suggestions'] = self._generate_field_mapping_suggestion(reader.fieldnames)

                # 统计行数
                f.seek(0)
                next(f)  # 跳过表头
                result['rows_count'] = sum(1 for _ in f)

                result['valid'] = True

        except UnicodeDecodeError:
            result['errors'].append('文件编码错误，请使用UTF-8或UTF-8-sig编码')
        except Exception as e:
            result['errors'].append(f'读取文件失败: {str(e)}')

        return result

    def _generate_field_mapping_suggestion(self, fields: List[str]) -> List[Dict]:
        """生成字段映射建议"""
        suggestions = []
        for field in fields:
            mapped = self.FIELD_MAPPING.get(field.strip(), '')
            if not mapped:
                # 尝试智能匹配
                for key, value in self.FIELD_MAPPING.items():
                    if key in field.lower() or field.lower() in key:
                        mapped = value
                        break
            suggestions.append({
                'original': field,
                'mapped': mapped or '(未识别)',
                'required': value in ['name', 'action'] if mapped else False
            })
        return suggestions

    def parse_csv(self, file_path: str) -> Tuple[List[Dict], Dict]:
        """
        解析CSV文件

        Returns:
            (记录列表, 解析统计)
        """
        records = []
        stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'missing_name': 0,
            'missing_action': 0
        }

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if '\t' in content and ',' not in content:
                    delimiter = '\t'
                elif ';' in content and ',' not in content:
                    delimiter = ';'
                else:
                    delimiter = ','

                f.seek(0)
                reader = csv.DictReader(f, delimiter=delimiter)

                if not reader.fieldnames:
                    return [], stats

                # 建立字段映射
                field_map = {}
                for field in reader.fieldnames:
                    mapped = self.FIELD_MAPPING.get(field.strip())
                    if mapped:
                        field_map[field] = mapped
                    else:
                        # 尝试模糊匹配
                        for key, value in self.FIELD_MAPPING.items():
                            if key in field.lower() or field.lower() in key:
                                field_map[field] = value
                                break

                for row in reader:
                    stats['total'] += 1

                    # 映射字段
                    record = {}
                    for orig_field, mapped_field in field_map.items():
                        record[mapped_field] = row.get(orig_field, '').strip()

                    # 验证必需字段
                    name = record.get('name', '').strip()
                    action = record.get('action', '').strip()

                    if not name:
                        stats['missing_name'] += 1
                        stats['invalid'] += 1
                        continue

                    if not action:
                        # 智能推断action
                        position = record.get('position', '')
                        if '任' in position or '任命' in position:
                            record['action'] = '任命'
                        elif '免' in position or '免去' in position:
                            record['action'] = '免去'
                        else:
                            stats['missing_action'] += 1

                    # 标准化action
                    action = record.get('action', '')
                    if '任命' in action or '上任' in action or '担任' in action:
                        record['action'] = '任命'
                    elif '免' in action:
                        record['action'] = '免去'
                    else:
                        record['action'] = action

                    # 设置默认值
                    record.setdefault('position', '')
                    record.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
                    record.setdefault('doc_no', '')
                    record.setdefault('source', 'manual_upload')

                    records.append(record)
                    stats['valid'] += 1

        except Exception as e:
            print(f"[上传] 解析CSV失败: {e}")

        return records, stats

    def upload(self, file_path: str, dry_run: bool = False) -> Dict:
        """
        上传CSV文件

        Args:
            file_path: CSV文件路径
            dry_run: 是否为试运行（不实际写入）

        Returns:
            上传结果统计
        """
        result = {
            'success': False,
            'file': file_path,
            'validation': None,
            'parse_stats': None,
            'update_stats': None,
            'errors': []
        }

        # 验证文件
        print(f"[上传] 验证文件: {file_path}")
        validation = self.validate_csv(file_path)
        result['validation'] = validation

        if not validation['valid']:
            result['errors'] = validation['errors']
            return result

        if validation['warnings']:
            print(f"[上传] 警告: {', '.join(validation['warnings'])}")

        # 解析CSV
        print(f"[上传] 解析CSV文件...")
        records, parse_stats = self.parse_csv(file_path)
        result['parse_stats'] = parse_stats

        if not records:
            result['errors'].append('未解析到有效记录')
            return result

        print(f"[上传] 解析完成 - 有效记录: {parse_stats['valid']}/{parse_stats['total']}")

        if dry_run:
            print("[上传] 试运行模式，不执行写入")
            result['success'] = True
            result['preview'] = records[:5]  # 返回前5条预览
            return result

        # 执行增量更新
        print(f"[上传] 执行增量更新...")
        update_stats = self.updater.update(records, 'upload')
        result['update_stats'] = update_stats

        if update_stats['added'] > 0:
            result['success'] = True
            print(f"[上传] 成功 - 新增: {update_stats['added']}, 跳过: {update_stats['skipped']}")
        else:
            result['errors'].append('没有新增记录（可能全部重复）')

        return result

    def batch_upload(self, directory: str) -> List[Dict]:
        """
        批量上传目录中的CSV文件

        Args:
            directory: 目录路径

        Returns:
            各文件上传结果列表
        """
        results = []
        csv_files = list(Path(directory).glob('*.csv'))

        print(f"[批量上传] 发现 {len(csv_files)} 个CSV文件")

        for csv_file in csv_files:
            print(f"\n[批量上传] 处理: {csv_file.name}")
            result = self.upload(str(csv_file))
            result['filename'] = csv_file.name
            results.append(result)

        return results

    def generate_template(self, output_path: str):
        """生成CSV模板"""
        template_data = [
            {
                '姓名': '张三',
                '职务': '副市长',
                '任命/免去': '任命',
                '时间': '2026-03-26',
                '文号': '国任〔2026〕001号',
                '备注': ''
            },
            {
                '姓名': '李四',
                '职务': '市教育局局长',
                '任命/免去': '免去',
                '时间': '2026-03-25',
                '文号': '',
                '备注': ''
            }
        ]

        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['姓名', '职务', '任命/免去', '时间', '文号', '备注'])
            writer.writeheader()
            writer.writerows(template_data)

        print(f"[上传] 模板文件已生成: {output_path}")


def test_uploader():
    """测试上传器"""
    uploader = CSVUploader('./data')

    # 生成模板
    uploader.generate_template('./data/template.csv')
    print("模板生成完成")


if __name__ == '__main__':
    test_uploader()
