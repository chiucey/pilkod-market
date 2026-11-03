#!/usr/bin/env python3
"""
智能字段匹配器
自动分析源表列内容，匹配到目标模板字段
"""

import re
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    """识别到的数据类型"""
    PHONE = "phone"           # 手机号
    EMAIL = "email"           # 邮箱
    ID_CARD = "id_card"       # 身份证
    NAME = "name"             # 姓名
    ADDRESS = "address"       # 地址
    DATE = "date"             # 日期
    NUMBER = "number"         # 数字
    TEXT = "text"             # 通用文本


@dataclass
class FieldMatch:
    """字段匹配结果"""
    target_field: str          # 目标字段名（A系统模板）
    source_field: str          # 源字段名（B系统导出）
    match_type: str            # 匹配方式（exact/semantic/pinyin/fuzzy）
    confidence: float          # 置信度 0-1


class SmartFieldMatcher:
    """智能字段匹配器"""

    # 数据类型识别模式
    PATTERNS = {
        DataType.PHONE: [
            r'^1[3-9]\d{9}$',                    # 中国手机号
            r'^\d{11}$',                         # 11位数字
            r'^1[3-9]-\d{4}-\d{4}$',             # 分隔格式
        ],
        DataType.EMAIL: [
            r'^[\w\.-]+@[\w\.-]+\.\w+$',         # 标准邮箱
        ],
        DataType.ID_CARD: [
            r'^\d{17}[\dXx]$',                   # 18位身份证
            r'^\d{15}$',                         # 15位身份证
        ],
        DataType.DATE: [
            r'^\d{4}-\d{2}-\d{2}',              # YYYY-MM-DD
            r'^\d{4}/\d{2}/\d{2}',              # YYYY/MM/DD
            r'^\d{4}年\d{1,2}月\d{1,2}日',       # 中文日期
        ],
    }

    # 字段名关键词映射
    FIELD_KEYWORDS = {
        DataType.PHONE: ["手机", "电话", "mobile", "phone", "tel", "telephone"],
        DataType.EMAIL: ["邮箱", "邮件", "email", "mail"],
        DataType.ID_CARD: ["身份证", "证件号", "id_card", "idno", "identity"],
        DataType.NAME: ["姓名", "名字", "name", "username", "uname"],
        DataType.ADDRESS: ["地址", "住址", "address", "addr", "location"],
        DataType.DATE: ["日期", "时间", "date", "time", "created", "updated"],
    }

    def __init__(self, target_columns: List[str], source_df, sample_size: int = 10):
        """
        初始化匹配器
        :param target_columns: 目标表字段名列表（A系统模板）
        :param source_df: 源数据DataFrame（B系统导出）
        :param sample_size: 用于类型识别的样本数量
        """
        self.target_columns = target_columns
        self.source_df = source_df
        self.source_columns = list(source_df.columns)
        self.sample_size = sample_size
        self.matches: List[FieldMatch] = []

    def detect_column_type(self, column_name: str, data_series) -> DataType:
        """检测列的数据类型"""
        # 1. 先根据字段名判断
        col_lower = column_name.lower()
        for dtype, keywords in self.FIELD_KEYWORDS.items():
            for kw in keywords:
                if kw in col_lower:
                    return dtype

        # 2. 根据内容模式判断
        samples = data_series.dropna().head(self.sample_size).astype(str)
        if len(samples) == 0:
            return DataType.TEXT

        # 检查每种模式
        for dtype, patterns in self.PATTERNS.items():
            match_count = 0
            for value in samples:
                if any(re.match(p, str(value).strip()) for p in patterns):
                    match_count += 1
            # 超过50%匹配则认定为该类型
            if match_count / len(samples) > 0.5:
                return dtype

        return DataType.TEXT

    def exact_match(self, target: str, source: str) -> Tuple[bool, float]:
        """精确匹配"""
        if target == source:
            return True, 1.0
        if target.lower() == source.lower():
            return True, 0.95
        return False, 0.0

    def pinyin_match(self, target: str, source: str) -> Tuple[bool, float]:
        """拼音匹配（需要pypinyin库）"""
        try:
            from pypinyin import lazy_pinyin
            target_pinyin = ''.join(lazy_pinyin(target))
            source_pinyin = ''.join(lazy_pinyin(source))
            if target_pinyin == source_pinyin:
                return True, 0.9
            # 模糊拼音匹配
            if target_pinyin in source_pinyin or source_pinyin in target_pinyin:
                return True, 0.7
        except ImportError:
            pass
        return False, 0.0

    def fuzzy_match(self, target: str, source: str) -> Tuple[bool, float]:
        """模糊匹配（关键词包含）"""
        target_lower = target.lower()
        source_lower = source.lower()

        # 检查关键词重叠
        for dtype, keywords in self.FIELD_KEYWORDS.items():
            target_match = any(kw in target_lower for kw in keywords)
            source_match = any(kw in source_lower for kw in keywords)
            if target_match and source_match:
                return True, 0.6

        # 任意一方包含另一方
        if target_lower in source_lower or source_lower in target_lower:
            return True, 0.5

        return False, 0.0

    def semantic_match(self, target: str, source: str, target_dtype: DataType,
                       source_dtype: DataType) -> Tuple[bool, float]:
        """语义匹配（数据类型相同）"""
        if target_dtype == source_dtype and target_dtype != DataType.TEXT:
            return True, 0.85
        return False, 0.0

    def find_best_match(self, target_field: str, target_dtype: DataType = None) -> FieldMatch:
        """为目标字段找到最佳匹配的源字段"""
        best_match = None
        best_score = 0.0

        # 如果未指定目标类型，尝试从字段名推断
        if target_dtype is None:
            target_dtype = DataType.TEXT
            for dtype, keywords in self.FIELD_KEYWORDS.items():
                if any(kw in target_field.lower() for kw in keywords):
                    target_dtype = dtype
                    break

        for source_col in self.source_columns:
            source_dtype = self.detect_column_type(source_col, self.source_df[source_col])
            total_score = 0.0
            match_type = "none"

            # 1. 精确匹配（权重最高）
            matched, score = self.exact_match(target_field, source_col)
            if matched:
                total_score = max(total_score, score)
                match_type = "exact"

            # 2. 语义匹配（数据类型相同）
            matched, score = self.semantic_match(target_field, source_col, target_dtype, source_dtype)
            if matched and score > total_score:
                total_score = score
                match_type = "semantic"

            # 3. 模糊匹配
            matched, score = self.fuzzy_match(target_field, source_col)
            if matched and score > total_score:
                total_score = score
                match_type = "fuzzy"

            # 4. 拼音匹配
            matched, score = self.pinyin_match(target_field, source_col)
            if matched and score > total_score:
                total_score = score
                match_type = "pinyin"

            if total_score > best_score and total_score >= 0.5:
                best_score = total_score
                best_match = FieldMatch(
                    target_field=target_field,
                    source_field=source_col,
                    match_type=match_type,
                    confidence=total_score
                )

        return best_match

    def match_all(self) -> List[FieldMatch]:
        """匹配所有目标字段"""
        self.matches = []
        for target_col in self.target_columns:
            match = self.find_best_match(target_col)
            if match:
                self.matches.append(match)

        return self.matches

    def get_mapping_dict(self) -> Dict[str, str]:
        """获取字段映射字典 {目标字段: 源字段}"""
        return {m.target_field: m.source_field for m in self.matches}

    def generate_report(self) -> str:
        """生成匹配报告"""
        lines = ["=" * 60]
        lines.append("智能字段匹配报告")
        lines.append("=" * 60)

        # 统计
        matched = len([m for m in self.matches if m.source_field])
        unmatched = len(self.target_columns) - matched

        lines.append(f"\n目标字段数: {len(self.target_columns)}")
        lines.append(f"源字段数: {len(self.source_columns)}")
        lines.append(f"成功匹配: {matched}")
        lines.append(f"未匹配: {unmatched}")

        lines.append("\n" + "-" * 60)
        lines.append("匹配详情:")
        lines.append("-" * 60)

        for m in self.matches:
            if m.source_field:
                lines.append(f"✓ {m.target_field} ← {m.source_field}")
                lines.append(f"  类型: {m.match_type}, 置信度: {m.confidence:.0%}")
            else:
                lines.append(f"✗ {m.target_field} [未找到匹配]")

        return "\n".join(lines)


def apply_mapping_to_template(source_df, matches: List[FieldMatch]) -> any:
    """
    将匹配结果应用到模板
    :param source_df: 源数据
    :param matches: 匹配结果列表
    :return: 填充好的DataFrame
    """
    import pandas as pd

    result = pd.DataFrame()

    for match in matches:
        if match.source_field and match.source_field in source_df.columns:
            result[match.target_field] = source_df[match.source_field]
        else:
            result[match.target_field] = None

    return result


# ==================== 使用示例 ====================

def main():
    """命令行使用示例"""
    import pandas as pd
    import argparse

    parser = argparse.ArgumentParser(description="智能字段匹配工具")
    parser.add_argument("--target", required=True, help="目标模板文件路径")
    parser.add_argument("--source", required=True, help="源数据文件路径")
    parser.add_argument("--target-sheet", default=0, help="目标文件sheet索引")
    parser.add_argument("--source-sheet", default=0, help="源文件sheet索引")
    parser.add_argument("--output", default="matched_output.xlsx", help="输出文件路径")
    args = parser.parse_args()

    # 读取文件
    print("正在读取文件...")
    if args.target.endswith('.xlsx'):
        target_df = pd.read_excel(args.target, sheet_name=args.target_sheet, nrows=0)
    else:
        target_df = pd.read_csv(args.target, nrows=0)

    if args.source.endswith('.xlsx'):
        source_df = pd.read_excel(args.source, sheet_name=args.source_sheet)
    else:
        source_df = pd.read_csv(args.source)

    target_columns = list(target_df.columns)

    # 执行匹配
    print("正在智能匹配字段...")
    matcher = SmartFieldMatcher(target_columns, source_df)
    matches = matcher.match_all()

    # 输出报告
    print(matcher.generate_report())

    # 生成填充结果
    print("\n正在生成填充后的文件...")
    result_df = apply_mapping_to_template(source_df, matches)

    # 保存结果
    if args.output.endswith('.xlsx'):
        result_df.to_excel(args.output, index=False)
    else:
        result_df.to_csv(args.output, index=False)

    print(f"已完成！输出文件: {args.output}")


if __name__ == "__main__":
    main()
