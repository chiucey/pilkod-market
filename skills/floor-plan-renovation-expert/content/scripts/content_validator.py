#!/usr/bin/env python3
"""
户型图装修方案内容审核脚本
功能：检查错别字、漏字、图片清晰度、数据合理性等
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from PIL import Image
import hashlib

# 中文常见错别字词典
COMMON_MISSPELLINGS = {
    "装修": ["装、休", "装、正", "装、布"],
    "设计": ["设、计", "设、纪"],
    "预算": ["预、算", "予、算"],
    "效果图": ["效、果图", "效果图"],
    "客厅": ["客、厅", "容、厅"],
    "卧室": ["卧、室", "床、室"],
    "厨房": ["厨、房", "橱、房"],
    "卫生间": ["卫、生间", "位、生间"],
    "阳台": ["阳、台", "阴、台"],
    "玄关": ["玄、关", "元、关"],
    "地板": ["地、扳", "地、般"],
    "瓷砖": ["瓷、砖", "次、砖", "词、砖"],
    "油漆": ["油、膝", "油、添"],
    "吊顶": ["吊、顶", "掉、顶"],
    "开关": ["开、关", "开、先"],
    "插座": ["插、座", "插、坐"],
    "甲醛": ["甲、醛", "钾、醛"],
    "通风": ["通、风", "痛、风"],
    "保洁": ["保、洁", "宝、洁"],
    "家具": ["家、俱", "家惧"],
    "窗帘": ["窗、帘", "创、帘"],
    "灯具": ["灯、具", "登、具"],
    "门": ["门", "闪"],
    "窗": ["窗", "突"],
    "墙": ["墙", "蕃"],
    "地": ["地", "也"],
    "水": ["水", "冰"],
    "电": ["电", "龟"],
    "米": ["米", ["来", "末"]],
    "元": ["元", "无"],
    "万": ["万", "方"],
    "平": ["平", "苹"],
    "方": ["方", "万"],
}

# 常见搭配错误
COMMON_PHRASE_ERRORS = [
    (r"一\s*平米", "平方米"),
    (r"一\s*个\s*月", "1个月"),
    (r"平米\s*米", "平方米"),
    (r"预算\s*在", "预算为"),
    (r"价格\s*惠", "价格优惠"),
    (r"装修\s*房", "装修房"),
    (r"整体\s*效果", "整体效果"),
    (r"现代\s*简约", "现代简约"),
    (r"品质\s*保证", "品质保证"),
]


@dataclass
class ValidationIssue:
    """验证问题"""
    issue_type: str  # typo, missing, image, data
    severity: str  # error, warning, info
    location: str  # file or section
    description: str
    original_text: str = ""
    suggested_fix: str = ""


@dataclass
class ValidationReport:
    """验证报告"""
    total_issues: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: bool = True


class ContentValidator:
    """内容审核器"""

    def __init__(self, content_dir: str = "."):
        self.content_dir = Path(content_dir)
        self.report = ValidationReport()

    def validate_all(self) -> ValidationReport:
        """执行完整验证"""
        # 验证文本内容
        self.validate_text_files()

        # 验证图片
        self.validate_images()

        # 验证数据
        self.validate_data()

        # 更新报告状态
        self.report.total_issues = len(self.report.issues)
        self.report.errors = len([i for i in self.report.issues if i.severity == "error"])
        self.report.warnings = len([i for i in self.report.issues if i.severity == "warning"])
        self.report.info = len([i for i in self.report.issues if i.severity == "info"])
        self.report.passed = self.report.errors == 0

        return self.report

    def validate_text_files(self):
        """验证文本文件中的错别字和漏字"""
        text_extensions = {'.txt', '.md', '.json'}

        for ext in text_extensions:
            for file_path in self.content_dir.rglob(f'*{ext}'):
                if file_path.name.startswith('.'):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    self._check_typos(content, str(file_path))
                    self._check_missing_chars(content, str(file_path))
                    self._check_phrase_errors(content, str(file_path))

                except Exception as e:
                    self.report.issues.append(ValidationIssue(
                        issue_type="file",
                        severity="error",
                        location=str(file_path),
                        description=f"无法读取文件: {str(e)}"
                    ))

    def _check_typos(self, content: str, location: str):
        """检查错别字"""
        for correct_word, wrong_words in COMMON_MISSPELLINGS.items():
            for wrong_word in wrong_words:
                if wrong_word in content:
                    # 避免误报：检查是否是完整词语
                    pattern = re.escape(wrong_word)
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        start = match.start()
                        end = match.end()
                        # 检查周围是否有中文
                        before = content[max(0, start-1):start]
                        after = content[end:min(len(content), end+1)]

                        if before.isalnum() or after.isalnum():
                            continue

                        self.report.issues.append(ValidationIssue(
                            issue_type="typo",
                            severity="error",
                            location=location,
                            description=f"疑似错别字",
                            original_text=wrong_word,
                            suggested_fix=correct_word
                        ))

    def _check_missing_chars(self, content: str, location: str):
        """检查漏字（常见的漏字模式）"""
        # 检查连续重复的标点
        patterns = [
            (r'[。，、；：]{2,}', "连续标点符号"),
            (r'\.{2,}', "连续句号"),
            (r',{2,}', "连续逗号"),
        ]

        for pattern, desc in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                self.report.issues.append(ValidationIssue(
                    issue_type="missing",
                    severity="warning",
                    location=location,
                    description=f"疑似漏字：{desc}",
                    original_text=match.group()
                ))

        # 检查数字格式不一致
        numbers = re.findall(r'\d+(?:\.\d+)?', content)
        if numbers:
            has_decimal = any('.' in n for n in numbers)
            has_integer = any('.' not in n for n in numbers)
            if has_decimal and has_integer:
                self.report.issues.append(ValidationIssue(
                    issue_type="format",
                    severity="warning",
                    location=location,
                    description="数字格式不一致（混合使用整数和小数）"
                ))

    def _check_phrase_errors(self, content: str, location: str):
        """检查常见搭配错误"""
        for pattern, replacement in COMMON_PHRASE_ERRORS:
            matches = re.finditer(pattern, content)
            for match in matches:
                self.report.issues.append(ValidationIssue(
                    issue_type="phrase",
                    severity="warning",
                    location=location,
                    description="疑似搭配不当",
                    original_text=match.group(),
                    suggested_fix=replacement
                ))

    def validate_images(self, min_width: int = 1920, min_height: int = 1080):
        """验证图片质量"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}

        for ext in image_extensions:
            for file_path in self.content_dir.rglob(f'*{ext}'):
                if file_path.name.startswith('.'):
                    continue

                try:
                    with Image.open(file_path) as img:
                        width, height = img.size

                        # 检查分辨率
                        if width < min_width or height < min_height:
                            self.report.issues.append(ValidationIssue(
                                issue_type="image",
                                severity="error",
                                location=str(file_path),
                                description=f"图片分辨率过低 ({width}x{height})",
                                suggested_fix=f"建议分辨率: {min_width}x{min_height}"
                            ))

                        # 检查是否模糊（通过分析图片特征）
                        if self._is_blurry(img):
                            self.report.issues.append(ValidationIssue(
                                issue_type="image",
                                severity="error",
                                location=str(file_path),
                                description="图片疑似模糊",
                                suggested_fix="请提供清晰图片或重新生成"
                            ))

                        # 检查水印
                        if self._has_watermark(img):
                            self.report.issues.append(ValidationIssue(
                                issue_type="image",
                                severity="error",
                                location=str(file_path),
                                description="图片包含水印",
                                suggested_fix="请使用无水印图片"
                            ))

                except Exception as e:
                    self.report.issues.append(ValidationIssue(
                        issue_type="image",
                        severity="error",
                        location=str(file_path),
                        description=f"无法读取图片: {str(e)}"
                    ))

    def _is_blurry(self, img: Image.Image) -> bool:
        """检测图片是否模糊"""
        # 简单的模糊检测：计算边缘锐利度
        from PIL import ImageFilter
        import statistics

        try:
            # 转换为灰度
            gray = img.convert('L')

            # 使用边缘检测滤波器
            edges = gray.filter(ImageFilter.FIND_EDGES)

            # 计算像素值方差
            pixels = list(edges.getdata())
            if len(pixels) > 0:
                variance = statistics.variance(pixels) if len(pixels) > 1 else 0
                # 如果方差太小，说明图片模糊
                return variance < 100
        except:
            pass

        return False

    def _has_watermark(self, img: Image.Image) -> bool:
        """检测图片水印（简化检测）"""
        # 简化版：检测角落是否有高对比度区域
        # 实际应用中可能需要更复杂的图像识别
        try:
            width, height = img.size
            # 检查四个角落
            corners = [
                img.crop((0, 0, width//4, height//4)),  # 左上
                img.crop((3*width//4, 0, width, height//4)),  # 右上
                img.crop((0, 3*height//4, width//4, height)),  # 左下
                img.crop((3*width//4, 3*height//4, width, height)),  # 右下
            ]

            for corner in corners:
                # 简化的水印检测
                extrema = corner.getextrema()
                # 如果角落区域对比度很高，可能是水印
                if extrema and len(extrema) >= 3:
                    r_range = extrema[0][1] - extrema[0][0]
                    g_range = extrema[1][1] - extrema[1][0]
                    b_range = extrema[2][1] - extrema[2][0]
                    if r_range > 200 and g_range > 200 and b_range > 200:
                        return True
        except:
            pass

        return False

    def validate_data(self):
        """验证数据合理性"""
        # 查找预算文件
        budget_files = list(self.content_dir.rglob('*budget*.json')) + \
                      list(self.content_dir.rglob('*预算*.json')) + \
                      list(self.content_dir.rglob('*budget*.csv')) + \
                      list(self.content_dir.rglob('*预算*.csv'))

        for file_path in budget_files:
            try:
                if file_path.suffix == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._validate_budget_data(data, str(file_path))
                elif file_path.suffix == '.csv':
                    self._validate_csv_data(file_path, str(file_path))
            except Exception as e:
                self.report.issues.append(ValidationIssue(
                    issue_type="data",
                    severity="error",
                    location=str(file_path),
                    description=f"无法读取数据文件: {str(e)}"
                ))

    def _validate_budget_data(self, data: dict, location: str):
        """验证预算数据合理性"""
        # 检查是否有总预算
        if 'total' in data or 'total_budget' in data:
            total = data.get('total') or data.get('total_budget')
            if total:
                try:
                    total = float(total)
                    if total < 10000:
                        self.report.issues.append(ValidationIssue(
                            issue_type="data",
                            severity="warning",
                            location=location,
                            description=f"总预算偏低: ¥{total:,.2f}",
                            suggested_fix="确认预算是否合理"
                        ))
                    elif total > 5000000:
                        self.report.issues.append(ValidationIssue(
                            issue_type="data",
                            severity="warning",
                            location=location,
                            description=f"总预算偏高: ¥{total:,.2f}",
                            suggested_fix="确认是否为豪宅装修"
                        ))
                except:
                    pass

        # 检查各项费用占比
        categories = ['design_fee', 'material_fee', 'labor_fee', 'furniture', 'appliances']
        found_categories = [c for c in categories if c in data]

        if len(found_categories) >= 2:
            try:
                total = sum(float(data.get(c, 0)) for c in found_categories)
                for c in found_categories:
                    amount = float(data.get(c, 0))
                    ratio = amount / total if total > 0 else 0

                    # 检查占比是否合理
                    if c in ['design_fee'] and ratio > 0.15:
                        self.report.issues.append(ValidationIssue(
                            issue_type="data",
                            severity="warning",
                            location=location,
                            description=f"设计费占比过高: {ratio:.1%}",
                            suggested_fix="设计费一般占总预算5-10%"
                        ))
                    elif c in ['labor_fee'] and ratio > 0.40:
                        self.report.issues.append(ValidationIssue(
                            issue_type="data",
                            severity="warning",
                            location=location,
                            description=f"人工费占比过高: {ratio:.1%}",
                            suggested_fix="人工费一般占总预算20-30%"
                        ))
            except:
                pass

    def _validate_csv_data(self, file_path: Path, location: str):
        """验证CSV数据"""
        try:
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)

                if len(rows) < 2:
                    self.report.issues.append(ValidationIssue(
                        issue_type="data",
                        severity="error",
                        location=location,
                        description="CSV文件为空或格式不正确"
                    ))
                    return

                # 检查是否有金额列
                has_amount = any('金额' in str(row) or '费用' in str(row) for row in rows[0])
                if not has_amount:
                    self.report.issues.append(ValidationIssue(
                        issue_type="data",
                        severity="warning",
                        location=location,
                        description="CSV文件可能缺少金额列"
                    ))

        except Exception as e:
            self.report.issues.append(ValidationIssue(
                issue_type="data",
                severity="error",
                location=location,
                description=f"CSV读取错误: {str(e)}"
            ))

    def generate_report(self) -> str:
        """生成验证报告"""
        output = []
        output.append("=" * 60)
        output.append("户型图装修方案内容审核报告")
        output.append("=" * 60)
        output.append("")
        output.append(f"审核结果: {'通过' if self.report.passed else '未通过'}")
        output.append(f"总问题数: {self.report.total_issues}")
        output.append(f"  - 错误: {self.report.errors}")
        output.append(f"  - 警告: {self.report.warnings}")
        output.append(f"  - 提示: {self.report.info}")
        output.append("")

        if self.report.issues:
            output.append("-" * 60)
            output.append("问题详情:")
            output.append("-" * 60)

            # 按类型分组
            by_type = {}
            for issue in self.report.issues:
                if issue.issue_type not in by_type:
                    by_type[issue.issue_type] = []
                by_type[issue.issue_type].append(issue)

            for issue_type, issues in by_type.items():
                output.append(f"\n[{issue_type.upper()}]")
                for issue in issues:
                    output.append(f"  位置: {issue.location}")
                    output.append(f"  严重程度: {issue.severity}")
                    output.append(f"  问题: {issue.description}")
                    if issue.original_text:
                        output.append(f"  原文: {issue.original_text}")
                    if issue.suggested_fix:
                        output.append(f"  建议修复: {issue.suggested_fix}")
                    output.append("")

        output.append("=" * 60)

        return "\n".join(output)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='户型图装修方案内容审核')
    parser.add_argument('directory', nargs='?', default='.', help='要审核的目录路径')
    parser.add_argument('--min-width', type=int, default=1920, help='图片最小宽度')
    parser.add_argument('--min-height', type=int, default=1080, help='图片最小高度')
    parser.add_argument('--output', '-o', help='输出报告文件路径')

    args = parser.parse_args()

    validator = ContentValidator(args.directory)
    validator.validate_all()

    report = validator.generate_report()

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存至: {args.output}")
    else:
        print(report)

    # 返回退出码
    exit(0 if validator.report.passed else 1)


if __name__ == '__main__':
    main()
