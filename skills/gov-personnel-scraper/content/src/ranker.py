#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
职务排序模块 - 按照职务职级大小对人员进行排序
"""

import re
import csv
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from .updater import IncrementalUpdater
from config.rank_config import POSITION_LEVELS, POSITION_PATTERNS, get_level_reason


class PersonnelRanker:
    """人员职务排序器"""

    def __init__(self, data_dir: str = './data'):
        self.data_dir = Path(data_dir)
        self.updater = IncrementalUpdater(data_dir)

    def classify_position(self, position: str) -> Tuple[int, str]:
        """
        分类职务并返回级别

        Args:
            position: 职务名称

        Returns:
            (级别数字, 标准化职务名称)
        """
        if not position:
            return 100, '未分类职务'

        position = position.strip()

        # 精确匹配
        if position in POSITION_LEVELS:
            return POSITION_LEVELS[position], position

        # 模式匹配
        for pattern, level, std_name in POSITION_PATTERNS:
            if re.search(pattern, position):
                return level, std_name

        # 部分匹配（关键词）
        keywords = {
            '总书记': (1, '中共中央总书记'),
            '国家主席': (1, '国家主席'),
            '总理': (1, '国务院总理'),
            '委员长': (1, '全国人大常委会委员长'),
            '政协主席': (1, '全国政协主席'),
            '纪委书记': (1, '中央纪委书记'),
            '省委书记': (10, '省委书记'),
            '自治区党委书记': (10, '自治区党委书记'),
            '直辖市市委书记': (10, '直辖市市委书记'),
            '副总理': (2, '国务院副总理'),
            '副委员长': (2, '全国人大常委会副委员长'),
            '副省级': (25, '副省级干部'),
            '副部长': (26, '副部级干部'),
            '副省长': (21, '副省长'),
            '自治区副主席': (21, '自治区副主席'),
            '副市长': (21, '副市长'),
            '省人大常委会副主任': (22, '省人大常委会副主任'),
            '省委常委': (24, '省委常委'),
            '市长': (31, '市长'),
            '市人大常委会主任': (32, '市人大常委会主任'),
            '市人大常委会副主任': (42, '市人大常委会副主任'),
            '市政协副主席': (43, '市政协副主席'),
            '厅 长': (34, '厅 长'),
            '副厅级': (44, '副厅级'),
            '副厅 长': (44, '副厅级干部'),
            '副厅': (44, '副厅级干部'),
            '副县级': (61, '副县级干部'),
            '副处长': (64, '副处 长'),
            '处长': (54, '处 长'),
            '局 长': (54, '局 长'),
            '副局长': (64, '副局长'),
            '副乡长': (81, '副乡长'),
            '副镇长': (81, '副镇长'),
            '乡长': (71, '乡 长'),
            '镇长': (73, '镇 长'),
            '乡党委书记': (70, '乡党委书记'),
            '镇党委书记': (72, '镇党委书记'),
            '科长': (75, '科 长'),
        }

        for keyword, (level, std_name) in keywords.items():
            if keyword in position:
                return level, std_name

        return 100, position

    def rank_records(self, records: List[Dict], use_date_tiebreaker: bool = True) -> List[Dict]:
        """
        对记录列表按职务排序

        Args:
            records: 人员记录列表
            use_date_tiebreaker: 是否使用日期作为平局决胜

        Returns:
            排序后的记录列表（添加了排序字段）
        """
        ranked = []

        for record in records:
            name = record.get('name', '').strip()
            position = record.get('position', '').strip()
            action = record.get('action', '').strip()
            date = record.get('date', '').strip()

            level, std_position = self.classify_position(position)
            reason = get_level_reason(level)

            # 党内职务优先（同级别）
            is_party = 1 if any(kw in position for kw in ['书记', '副书记', '常委', '委员']) else 0

            # 解析日期用于平局决胜
            date_sort_key = 0
            if use_date_tiebreaker and date:
                try:
                    date_parts = re.findall(r'\d+', date)
                    if len(date_parts) >= 3:
                        date_sort_key = int(date_parts[0]) * 10000 + int(date_parts[1]) * 100 + int(date_parts[2])
                except:
                    date_sort_key = 0

            ranked.append({
                **record,
                'level': level,
                'level_name': std_position,
                'rank_reason': reason,
                'is_party': is_party,
                'date_sort_key': date_sort_key
            })

        # 排序：先按级别，再按党内职务，再按日期
        ranked.sort(key=lambda x: (
            x['level'],
            x['is_party'],
            -x['date_sort_key']  # 日期越新越靠前
        ))

        # 添加排名序号
        for i, record in enumerate(ranked, 1):
            record['rank'] = i

        return ranked

    def rank_by_names(self, names: List[str], from_csv: bool = False, csv_path: Optional[str] = None) -> List[Dict]:
        """
        根据姓名列表进行排序

        Args:
            names: 姓名列表
            from_csv: 是否从CSV文件中查找记录
            csv_path: CSV文件路径

        Returns:
            排序结果
        """
        if not from_csv:
            # 仅根据姓名生成简化记录
            records = [{'name': name, 'position': '', 'action': '', 'date': ''} for name in names]
            for record in records:
                level, std_position = self.classify_position(record['position'])
                record['level'] = level
                record['level_name'] = std_position
                record['rank_reason'] = get_level_reason(level) if level < 100 else '职务信息缺失，无法确定级别'
            records.sort(key=lambda x: x['level'])
        else:
            # 从CSV文件查找
            path = csv_path or str(self.data_dir / 'appointments.csv')
            records = []

            if Path(path).exists():
                with open(path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        name = row.get('name', '').strip()
                        if name in names:
                            records.append(row)

            # 去重（保留最新的）
            seen = {}
            for record in records:
                name = record.get('name', '')
                if name not in seen:
                    seen[name] = record
                else:
                    # 比较日期，保留较新的
                    old_date = seen[name].get('date', '')
                    new_date = record.get('date', '')
                    if new_date > old_date:
                        seen[name] = record

            records = list(seen.values())

        return self.rank_records(records)

    def generate_ranking_report(self, ranked_records: List[Dict], title: str = "人员排序报告") -> str:
        """
        生成排序报告

        Args:
            ranked_records: 已排序的记录
            title: 报告标题

        Returns:
            格式化的报告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"{title}")
        lines.append("=" * 80)
        lines.append("")

        current_level = None

        for record in ranked_records:
            level = record.get('level', 100)
            rank = record.get('rank', 0)
            name = record.get('name', '未知')
            position = record.get('position', '未知')
            action = record.get('action', '')
            date = record.get('date', '未知')
            level_name = record.get('level_name', '')
            reason = record.get('rank_reason', '')

            # 级别分组标题
            if level != current_level:
                current_level = level
                lines.append("")
                lines.append(f"【{reason}】")
                lines.append("-" * 40)

            # 记录行
            action_str = f" {action}" if action else ""
            lines.append(f"  {rank:2d}. {name} - {position}{action_str} ({date})")

        lines.append("")
        lines.append("=" * 80)
        lines.append("排序说明：")
        lines.append("  1. 按职务层级从高到低排序")
        lines.append("  2. 同级别职务，党内职务优先")
        lines.append("  3. 同级别同类型，按任职时间倒序")
        lines.append("=" * 80)

        return "\n".join(lines)

    def compare_two(self, name1: str, info1: str, name2: str, info2: str) -> Dict:
        """
        比较两个人的职务高低

        Args:
            name1: 第一人姓名
            info1: 第一人职务信息
            name2: 第二人姓名
            info2: 第二人职务信息

        Returns:
            比较结果
        """
        level1, std1 = self.classify_position(info1)
        level2, std2 = self.classify_position(info2)

        result = {
            'person1': {'name': name1, 'position': info1, 'level': level1, 'level_name': std1},
            'person2': {'name': name2, 'position': info2, 'level': level2, 'level_name': std2},
            'comparison': '',
            'reason': ''
        }

        if level1 < level2:
            result['comparison'] = f'{name1} > {name2}'
            result['reason'] = f'{name1}的职务"{std1}"级别高于{name2}的职务"{std2}"'
        elif level1 > level2:
            result['comparison'] = f'{name2} > {name1}'
            result['reason'] = f'{name2}的职务"{std2}"级别高于{name1}的职务"{std1}"'
        else:
            result['comparison'] = f'{name1} = {name2}'
            result['reason'] = f'两人的职务"{std1}"级别相同'

        return result


def test_ranker():
    """测试排序器"""
    ranker = PersonnelRanker('./data')

    # 测试职务分类
    test_positions = [
        '副总理',
        '省委书记',
        '副省长',
        '市委书记',
        '副市长',
        '县 长',
        '副局长',
        '乡党委书记',
    ]

    print("职务分类测试:")
    for pos in test_positions:
        level, std_name = ranker.classify_position(pos)
        reason = get_level_reason(level)
        print(f"  {pos:10s} -> 级别:{level}, 职务:{std_name}, 理由:{reason}")

    # 测试排序
    test_records = [
        {'name': '张三', 'position': '副县长', 'action': '任命', 'date': '2026-03-20'},
        {'name': '李四', 'position': '县委书记', 'action': '任命', 'date': '2026-03-15'},
        {'name': '王五', 'position': '副市长', 'action': '任命', 'date': '2026-03-18'},
        {'name': '赵六', 'position': '县人大常委会主任', 'action': '任命', 'date': '2026-03-22'},
        {'name': '钱七', 'position': '县政协主席', 'action': '任命', 'date': '2026-03-19'},
    ]

    print("\n排序测试:")
    ranked = ranker.rank_records(test_records)
    report = ranker.generate_ranking_report(ranked, "测试排序报告")
    print(report)


if __name__ == '__main__':
    test_ranker()
