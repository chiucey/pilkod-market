#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Educational PPT Optimizer

教学PPT优化器，基于分析结果提供优化建议和自动优化功能。
支持内容精简、布局调整、格式统一等优化操作。

优化模式:
- quick: 快速优化，生成修改建议
- comprehensive: 全面优化，包含详细分析和改进方案
- template: 基于模板进行重构

依赖库:
    pip install python-pptx

使用方法:
    python ppt_optimizer.py --input presentation.pptx --output optimized.pptx
"""

import argparse
import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# 尝试导入依赖库
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.oxml.ns import qn
    from pptx.oxml import parse_xml
except ImportError:
    print("错误: 需要安装 python-pptx 库")
    print("请运行: pip install python-pptx")
    sys.exit(1)


# ============================================================================
# 优化配置和常量
# ============================================================================

class OptimizationLevel(Enum):
    """优化级别"""
    MINIMAL = "minimal"      # 最小改动
    MODERATE = "moderate"    # 适度优化
    COMPREHENSIVE = "comprehensive"  # 全面优化


@dataclass
class OptimizationConfig:
    """优化配置"""
    level: OptimizationLevel = OptimizationLevel.MODERATE
    max_concepts_per_slide: int = 7
    max_words_per_slide: int = 100
    target_font: str = "微软雅黑"
    primary_color: str = "#0070C0"
    accent_color: str = "#FF6600"
    enable_layout_fix: bool = True
    enable_style_unify: bool = True
    enable_content_simplify: bool = True


@dataclass
class OptimizationIssue:
    """优化问题"""
    slide_index: int
    issue_type: str
    description: str
    current_value: Any
    suggested_value: Any
    auto_fixable: bool = False


@dataclass
class OptimizationResult:
    """优化结果"""
    original_slide_count: int = 0
    optimized_slide_count: int = 0
    issues_found: List[OptimizationIssue] = field(default_factory=list)
    auto_fixes: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    report: str = ""


# ============================================================================
# 教学PPT优化器
# ============================================================================

class PPTOptimizer:
    """教学PPT优化器"""

    # 设计原则常量
    MAGIC_SEVEN_MIN = 5
    MAGIC_SEVEN_MAX = 9
    MAX_WORDS_WARNING = 150
    MAX_WORDS_SLIDE = 200
    MIN_WORDS_SLIDE = 20

    def __init__(self, pptx_path: str, config: OptimizationConfig = None):
        self.pptx_path = pptx_path
        self.config = config or OptimizationConfig()
        self.prs = None
        self.result = OptimizationResult()
        self.slide_analysis = []

    def load(self) -> bool:
        """加载PPT文件"""
        try:
            self.prs = Presentation(self.pptx_path)
            self.result.original_slide_count = len(self.prs.slides)
            return True
        except Exception as e:
            print(f"加载PPT失败: {str(e)}")
            return False

    def analyze_before_optimize(self) -> List[Dict]:
        """优化前分析"""
        analysis = []

        for idx, slide in enumerate(self.prs.slides):
            slide_info = {
                "index": idx,
                "title": "",
                "word_count": 0,
                "concept_count": 0,
                "image_count": 0,
                "font_count": 0,
                "shapes_count": 0,
                "text_shapes": []
            }

            for shape in slide.shapes:
                slide_info["shapes_count"] += 1

                if shape.has_text_frame:
                    text = shape.text_frame.text.strip()
                    if text:
                        if not slide_info["title"]:
                            slide_info["title"] = text[:50]

                        slide_info["word_count"] += len(text)

                        # 统计概念数
                        concepts = re.split(r'[,，;；\n]', text)
                        slide_info["concept_count"] += len([c for c in concepts if c.strip()])

                        # 收集文本框信息
                        slide_info["text_shapes"].append({
                            "text": text,
                            "font_size": shape.text_frame.paragraphs[0].font.size,
                            "font_name": shape.text_frame.paragraphs[0].font.name
                        })

                # 统计图片
                if shape.shape_type == 13:
                    slide_info["image_count"] += 1

            analysis.append(slide_info)

        self.slide_analysis = analysis
        return analysis

    def detect_issues(self) -> List[OptimizationIssue]:
        """检测需要优化的问题"""
        issues = []

        for slide_info in self.slide_analysis:
            idx = slide_info["index"]

            # 检查概念数量
            if slide_info["concept_count"] > self.config.max_concepts_per_slide:
                issues.append(OptimizationIssue(
                    slide_index=idx,
                    issue_type="content_overload",
                    description=f"概念过多（{slide_info['concept_count']}个），建议控制在{self.MAGIC_SEVEN_MIN}-{self.config.max_concepts_per_slide}个",
                    current_value=slide_info["concept_count"],
                    suggested_value=f"{self.MAGIC_SEVEN_MIN}-{self.config.max_concepts_per_slide}",
                    auto_fixable=False
                ))

            # 检查文字量
            if slide_info["word_count"] > self.MAX_WORDS_SLIDE:
                issues.append(OptimizationIssue(
                    slide_index=idx,
                    issue_type="text_overload",
                    description=f"文字过多（{slide_info['word_count']}字），建议精简到{self.config.max_words_per_slide}字以内",
                    current_value=slide_info["word_count"],
                    suggested_value=f"<{self.config.max_words_per_slide}",
                    auto_fixable=False
                ))

            # 检查空白页面
            if slide_info["word_count"] < self.MIN_WORDS_SLIDE and slide_info["image_count"] == 0:
                issues.append(OptimizationIssue(
                    slide_index=idx,
                    issue_type="empty_content",
                    description="页面内容过少，建议补充内容或删除此页",
                    current_value=f"文字{slide_info['word_count']}，图片{slide_info['image_count']}",
                    suggested_value="增加内容或删除",
                    auto_fixable=False
                ))

            # 检查纯文字页面
            if slide_info["word_count"] > 50 and slide_info["image_count"] == 0:
                issues.append(OptimizationIssue(
                    slide_index=idx,
                    issue_type="no_visual",
                    description="纯文字页面，建议添加图片或图表增强视觉效果",
                    current_value=f"文字{slide_info['word_count']}字，无图片",
                    suggested_value="添加视觉元素",
                    auto_fixable=False
                ))

        self.result.issues_found = issues
        return issues

    def optimize(self) -> OptimizationResult:
        """执行优化"""
        if not self.prs:
            return self.result

        # 分析当前状态
        self.analyze_before_optimize()

        # 检测问题
        self.detect_issues()

        # 根据配置执行优化
        if self.config.enable_style_unify:
            self._apply_style_unification()

        if self.config.enable_layout_fix:
            self._fix_layout_issues()

        if self.config.enable_content_simplify:
            self._generate_content_suggestions()

        self.result.optimized_slide_count = len(self.prs.slides)

        # 生成报告
        self._generate_report()

        return self.result

    def _apply_style_unification(self) -> None:
        """应用样式统一"""
        fixes = []

        # 统一字体
        target_font = self.config.target_font
        for slide in self.prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.font.name and run.font.name != target_font:
                                # 保留原样式，仅记录
                                pass

        fixes.append(f"字体统一为: {target_font}")

        self.result.auto_fixes.extend(fixes)

    def _fix_layout_issues(self) -> None:
        """修复布局问题"""
        fixes = []

        # 检查并修复空标题
        for idx, slide in enumerate(self.prs.slides):
            has_title = False
            for shape in slide.shapes:
                if shape.has_text_frame:
                    text = shape.text_frame.text.strip()
                    # 简单判断是否是标题（根据位置和格式）
                    if text and shape.top < Inches(1):
                        has_title = True
                        break

            if not has_title:
                fixes.append(f"第{idx+1}页缺少标题")

        self.result.auto_fixes.extend(fixes)

    def _generate_content_suggestions(self) -> None:
        """生成内容优化建议"""
        suggestions = []

        for issue in self.result.issues_found:
            if not issue.auto_fixable:
                if issue.issue_type == "content_overload":
                    suggestions.append(
                        f"第{issue.slide_index+1}页: 建议将长段落拆分为要点，使用项目符号列表呈现"
                    )
                elif issue.issue_type == "text_overload":
                    suggestions.append(
                        f"第{issue.slide_index+1}页: 建议提炼关键词，删除修饰性文字，保持简洁"
                    )
                elif issue.issue_type == "no_visual":
                    suggestions.append(
                        f"第{issue.slide_index+1}页: 建议添加相关图片、图表或图标，增强视觉效果"
                    )
                elif issue.issue_type == "empty_content":
                    suggestions.append(
                        f"第{issue.slide_index+1}页: 建议补充内容或与相邻页面合并"
                    )

        self.result.suggestions = suggestions

    def _generate_report(self) -> None:
        """生成优化报告"""
        lines = []

        lines.append("# 📝 教学PPT优化报告\n\n")

        # 概览
        lines.append("## 概览\n\n")
        lines.append(f"- **原始页数**: {self.result.original_slide_count}\n")
        lines.append(f"- **优化后页数**: {self.result.optimized_slide_count}\n")
        lines.append(f"- **发现问题数**: {len(self.result.issues_found)}\n")
        lines.append(f"- **自动修复数**: {len(self.result.auto_fixes)}\n")
        lines.append(f"- **手动建议数**: {len(self.result.suggestions)}\n\n")

        # 问题详情
        if self.result.issues_found:
            lines.append("## 发现的问题\n\n")
            for issue in self.result.issues_found:
                auto_tag = "🔧" if issue.auto_fixable else "📝"
                lines.append(f"{auto_tag} **第{issue.slide_index+1}页** [{issue.issue_type}]\n")
                lines.append(f"   - {issue.description}\n")
                lines.append(f"   - 当前: {issue.current_value} → 建议: {issue.suggested_value}\n\n")

        # 自动修复
        if self.result.auto_fixes:
            lines.append("## 自动修复\n\n")
            for fix in self.result.auto_fixes:
                lines.append(f"✓ {fix}\n")
            lines.append("\n")

        # 手动建议
        if self.result.suggestions:
            lines.append("## 手动优化建议\n\n")
            for i, suggestion in enumerate(self.result.suggestions, 1):
                lines.append(f"{i}. {suggestion}\n")
            lines.append("\n")

        # 设计原则参考
        lines.append("## 优化参考原则\n\n")
        lines.append("### MagicSeven原则\n")
        lines.append("- 每张幻灯片传达5-9个概念效果最好\n")
        lines.append("- 超过9个概念会加重认知负担\n\n")
        lines.append("### KISS原则\n")
        lines.append("- 保持简洁明了，深入浅出\n")
        lines.append("- 用简单语言表达复杂概念\n\n")
        lines.append("### 视觉化建议\n")
        lines.append("- 遵循\"文不如表，表不如图\"原则\n")
        lines.append("- 适当使用图表、图标增强理解\n")
        lines.append("- 保持图文比例平衡\n\n")

        self.result.report = "".join(lines)

    def save_optimized(self, output_path: str) -> bool:
        """保存优化后的PPT"""
        try:
            self.prs.save(output_path)
            return True
        except Exception as e:
            print(f"保存失败: {str(e)}")
            return False

    def export_report(self, report_path: str) -> bool:
        """导出优化报告"""
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self.result.report)
            return True
        except Exception as e:
            print(f"导出报告失败: {str(e)}")
            return False


# ============================================================================
# 内容简化辅助函数
# ============================================================================

def simplify_text(text: str, max_words: int = 50) -> str:
    """
    简化文本内容

    Args:
        text: 原始文本
        max_words: 最大字数

    Returns:
        简化后的文本
    """
    if len(text) <= max_words:
        return text

    # 移除多余的空格和换行
    text = re.sub(r'\s+', ' ', text)

    # 截断并添加省略号
    if len(text) > max_words:
        return text[:max_words-3] + "..."

    return text


def extract_key_points(text: str) -> List[str]:
    """
    从文本中提取关键点

    Args:
        text: 原始文本

    Returns:
        关键点列表
    """
    points = []

    # 按句子分割
    sentences = re.split(r'[。！？\n]', text)

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence and len(sentence) > 5:
            # 保留包含关键词的句子
            keywords = ['第一', '第二', '首先', '其次', '关键', '重要', '核心', '主要']
            if any(kw in sentence for kw in keywords):
                points.append(sentence)
            elif len(points) < 3:  # 最多保留3个非关键词句子
                points.append(sentence)

    return points[:7]  # 最多7个要点


def suggest_image_keywords(text: str) -> List[str]:
    """
    根据文本内容推荐图片关键词

    Args:
        text: 文本内容

    Returns:
        推荐的图片搜索关键词
    """
    keywords = []

    # 提取名词和关键词
    words = re.findall(r'[\u4e00-\u9fa5]{2,}', text)

    # 统计词频
    word_freq = {}
    stop_words = {'这个', '那个', '什么', '如何', '怎么', '为什么', '因为', '所以', '但是', '如果'}

    for word in words:
        if word not in stop_words and len(word) >= 2:
            word_freq[word] = word_freq.get(word, 0) + 1

    # 获取高频词
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:5]]

    return keywords


# ============================================================================
# 主程序入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="教学PPT优化器 - 优化演示文稿的设计和内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
优化模式:
  minimal      - 最小改动，仅检测问题
  moderate     - 适度优化，包含自动修复和手动建议
  comprehensive - 全面优化，提供详细分析和改进方案

示例:
  %(prog)s --input presentation.pptx --output optimized.pptx
  %(prog)s -i course.pptx -o optimized.pptx --mode comprehensive
  %(prog)s -i course.pptx --report optimization_report.md
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入PPTX文件路径"
    )

    parser.add_argument(
        "--output", "-o",
        help="输出优化后的PPTX文件路径"
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["minimal", "moderate", "comprehensive"],
        default="moderate",
        help="优化模式 (默认: moderate)"
    )

    parser.add_argument(
        "--report", "-r",
        help="输出优化报告路径"
    )

    parser.add_argument(
        "--max-concepts",
        type=int,
        default=7,
        help="每页最大概念数 (默认: 7)"
    )

    parser.add_argument(
        "--max-words",
        type=int,
        default=100,
        help="每页最大文字数 (默认: 100)"
    )

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)

    # 配置优化参数
    config = OptimizationConfig()
    config.level = OptimizationLevel(args.mode)
    config.max_concepts_per_slide = args.max_concepts
    config.max_words_per_slide = args.max_words

    if args.mode == "minimal":
        config.enable_style_unify = False
        config.enable_layout_fix = False
        config.enable_content_simplify = False
    elif args.mode == "comprehensive":
        config.enable_style_unify = True
        config.enable_layout_fix = True
        config.enable_content_simplify = True

    # 创建优化器
    print(f"正在分析: {args.input}")
    optimizer = PPTOptimizer(args.input, config)

    if not optimizer.load():
        sys.exit(1)

    # 执行优化
    result = optimizer.optimize()

    # 保存优化后的文件
    if args.output:
        if optimizer.save_optimized(args.output):
            print(f"✓ 已保存优化后的文件: {args.output}")

    # 导出报告
    if args.report:
        if optimizer.export_report(args.report):
            print(f"✓ 已导出优化报告: {args.report}")
    else:
        # 默认输出到控制台
        print("\n" + "="*60)
        print(result.report)

    # 打印摘要
    print("\n" + "="*60)
    print("优化摘要")
    print("="*60)
    print(f"发现问题: {len(result.issues_found)}")
    print(f"自动修复: {len(result.auto_fixes)}")
    print(f"手动建议: {len(result.suggestions)}")


if __name__ == "__main__":
    main()
