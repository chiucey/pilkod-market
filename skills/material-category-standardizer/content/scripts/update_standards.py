#!/usr/bin/env python3
"""
材料标准自动更新脚本
从外部数据源获取最新标准参数并更新映射表
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class StandardUpdater:
    """材料标准自动更新器"""

    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent
        self.base_path = Path(base_path)
        self.categories_file = self.base_path / "references" / "material_categories.json"
        self.custom_standards_file = self.base_path / "references" / "custom_standards.json"
        self.backup_file = self.base_path / "references" / f"material_categories_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    def load_categories(self) -> Dict:
        """加载材料类别映射表"""
        with open(self.categories_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_categories(self, data: Dict) -> None:
        """保存材料类别映射表"""
        # 先备份
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.load_categories(), f, ensure_ascii=False, indent=2)

        # 保存更新后的数据
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_custom_standards(self) -> Optional[Dict]:
        """加载自定义标准文件"""
        if self.custom_standards_file.exists():
            with open(self.custom_standards_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def find_category_by_code(self, data: Dict, code: str) -> Optional[Dict]:
        """根据编码查找类别"""
        for cat in data.get('categories', []):
            if cat.get('code') == code:
                return cat
        return None

    def find_category_by_keywords(self, data: Dict, keyword: str) -> Optional[Dict]:
        """根据关键词查找类别"""
        for cat in data.get('categories', []):
            keywords = cat.get('keywords', [])
            aliases = cat.get('aliases', [])
            if keyword in keywords or keyword in aliases:
                return cat
        return None

    def merge_standards(self, existing: Dict, new: Dict) -> Dict:
        """合并标准参数，new覆盖existing"""
        merged = existing.copy()
        for key, value in new.items():
            if key == 'last_updated':
                continue  # 不覆盖更新时间
            if isinstance(value, list) and isinstance(merged.get(key), list):
                # 合并列表，去重
                merged[key] = list(set(merged.get(key, []) + value))
            elif isinstance(value, dict) and isinstance(merged.get(key), dict):
                # 递归合并字典
                merged[key] = self.merge_standards(merged.get(key, {}), value)
            else:
                merged[key] = value
        merged['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        return merged

    def update_category(self, data: Dict, code: str, new_standards: Dict) -> bool:
        """更新指定类别的标准参数"""
        for cat in data.get('categories', []):
            if cat.get('code') == code:
                if 'standards' not in cat:
                    cat['standards'] = {}
                cat['standards'] = self.merge_standards(cat['standards'], new_standards)
                return True
        return False

    def update_from_custom_file(self, data: Dict, confirm: bool = True) -> Dict:
        """从自定义标准文件更新"""
        custom_data = self.load_custom_standards()
        if not custom_data:
            return {'success': False, 'message': '自定义标准文件不存在'}

        updates = []
        errors = []

        # 支持两种格式：直接是更新列表 或 嵌套在update_data中
        update_list = custom_data.get('update_data', custom_data)

        for item in update_list.get('updates', []):
            code = item.get('category_code')
            standards = item.get('standards', {})

            if not code:
                errors.append({'item': item, 'error': '缺少category_code'})
                continue

            if self.update_category(data, code, standards):
                updates.append(code)
            else:
                errors.append({'code': code, 'error': '未找到对应类别'})

        return {
            'success': True,
            'updates_count': len(updates),
            'updated_codes': updates,
            'errors': errors,
            'timestamp': datetime.now().isoformat()
        }

    def update_all_standards_version(self, data: Dict) -> Dict:
        """批量更新所有标准的版本标记"""
        for cat in data.get('categories', []):
            if 'standards' in cat:
                cat['standards']['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        data['version'] = self._increment_version(data.get('version', '1.0.0'))
        data['last_updated'] = datetime.now().strftime('%Y-%m-%d')
        data['update_source']['last_sync'] = datetime.now().isoformat()

        return data

    def _increment_version(self, version: str) -> str:
        """递增版本号"""
        parts = version.split('.')
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
        return '.'.join(parts)

    def search_standard_updates(self, keyword: str) -> List[Dict]:
        """搜索标准更新信息"""
        data = self.load_categories()
        results = []

        for cat in data.get('categories', []):
            # 检查类别名称
            if keyword in cat.get('name', ''):
                results.append({
                    'code': cat.get('code'),
                    'name': cat.get('name'),
                    'standard': cat.get('standards', {}).get('execution_standard', 'N/A'),
                    'last_updated': cat.get('standards', {}).get('last_updated', 'N/A')
                })
                continue

            # 检查关键词
            for kw in cat.get('keywords', []):
                if keyword in kw:
                    results.append({
                        'code': cat.get('code'),
                        'name': cat.get('name'),
                        'standard': cat.get('standards', {}).get('execution_standard', 'N/A'),
                        'last_updated': cat.get('standards', {}).get('last_updated', 'N/A')
                    })
                    break

        return results

    def get_update_report(self) -> Dict:
        """获取更新报告"""
        data = self.load_categories()

        categories_with_standards = 0
        total_inspection_items = 0
        standards_map = {}

        for cat in data.get('categories', []):
            if 'standards' in cat and cat['standards']:
                categories_with_standards += 1
                std = cat['standards']
                if 'inspection_items' in std:
                    total_inspection_items += len(std['inspection_items'])
                if 'execution_standard' in std:
                    std_code = std['execution_standard']
                    if std_code not in standards_map:
                        standards_map[std_code] = []
                    standards_map[std_code].append(cat['name'])

        return {
            'total_categories': len(data.get('categories', [])),
            'categories_with_standards': categories_with_standards,
            'total_inspection_items': total_inspection_items,
            'unique_standards': len(standards_map),
            'standards_map': standards_map,
            'last_updated': data.get('last_updated'),
            'version': data.get('version'),
            'last_sync': data.get('update_source', {}).get('last_sync')
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='材料标准自动更新工具')
    parser.add_argument('--action', '-a', choices=['update', 'report', 'search', 'batch-update'],
                        default='report', help='操作类型')
    parser.add_argument('--keyword', '-k', help='搜索关键词')
    parser.add_argument('--code', '-c', help='指定类别编码')
    parser.add_argument('--file', '-f', help='自定义标准文件路径')
    parser.add_argument('--confirm', '-y', action='store_true', help='跳过确认提示')

    args = parser.parse_args()

    updater = StandardUpdater()

    if args.action == 'report':
        # 生成更新报告
        report = updater.get_update_report()
        print("\n" + "=" * 60)
        print("材料标准更新报告")
        print("=" * 60)
        print(f"总类别数: {report['total_categories']}")
        print(f"含标准参数类别: {report['categories_with_standards']}")
        print(f"总检测项目数: {report['total_inspection_items']}")
        print(f"唯一标准数: {report['unique_standards']}")
        print(f"当前版本: {report['version']}")
        print(f"最后更新: {report['last_updated']}")
        print(f"最后同步: {report['last_sync'] or '从未同步'}")
        print("\n标准分布:")
        for std, cats in report['standards_map'].items():
            print(f"  {std}: {', '.join(cats[:3])}{'...' if len(cats) > 3 else ''}")
        print("=" * 60)

    elif args.action == 'search':
        if not args.keyword:
            print("错误: 搜索操作需要 --keyword 参数")
            sys.exit(1)

        results = updater.search_standard_updates(args.keyword)
        if results:
            print(f"\n找到 {len(results)} 个匹配:")
            for r in results:
                print(f"  [{r['code']}] {r['name']} - {r['standard']} (更新: {r['last_updated']})")
        else:
            print(f"未找到包含 '{args.keyword}' 的类别")

    elif args.action == 'update':
        data = updater.load_categories()

        # 从自定义文件更新
        result = updater.update_from_custom_file(data, args.confirm)

        if result['success']:
            print(f"\n更新成功:")
            print(f"  更新类别数: {result['updates_count']}")
            print(f"  更新编码: {result['updated_codes']}")
            if result['errors']:
                print(f"  错误: {result['errors']}")

            # 保存更新
            updater.save_categories(data)
            print(f"\n已保存到: {updater.categories_file}")
            print(f"备份文件: {updater.backup_file}")
        else:
            print(f"更新失败: {result['message']}")

    elif args.action == 'batch-update':
        data = updater.load_categories()
        print("\n执行批量更新...")
        data = updater.update_all_standards_version(data)
        updater.save_categories(data)
        print(f"批量更新完成")
        print(f"新版本: {data['version']}")
        print(f"更新日期: {data['last_updated']}")
        print(f"备份文件: {updater.backup_file}")


if __name__ == '__main__':
    main()
