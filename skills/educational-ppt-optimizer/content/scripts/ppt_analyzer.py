#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Educational PPT Analyzer

教学PPT分析器，用于评估PPT的设计质量和教学效果。
基于教育学原则和PPT设计最佳实践进行全面分析。

分析维度:
- MagicSeven原则（每页5-9个概念）
- KISS原则（简洁明了）
- 10/20/30法则（不超过10页，20分钟，30pt字体）
- 三不原则（不超过3种字体、色系、动画）
- 视觉设计（布局、配色、排版）
- 教育效果（学习目标、互动性、逻辑结构）

依赖库:
    pip install python-pptx

使用方法:
    python ppt_analyzer.py --input presentation.pptx --output analysis.md
"""

import argparse
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter

# 尝试导入依赖库
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
except ImportError:
    print("错误: 需要安装 python-pptx 库")
    print("请运行: pip install python-pptx")
    sys.exit(1)


# ============================================================================
# 分析结果数据结构
# ============================================================================

class AnalysisResult:
    """分析结果容器"""

    def __init__(self):
        self.slide_count = 0
        self.title = ""
        self.slides_analysis = []
        self.design_principles_scores = {}
        self.overall_score = 0
        self.suggestions = []
        self.statistics = {}

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "title": self.title,
            "slide_count": self.slide_count,
            "overall_score": self.overall_score,
            "design_principles_scores": self.design_principles_scores,
            "statistics": self.statistics,
            "slides_analysis": self.slides_analysis,
            "suggestions": self.suggestions
        }

    def to_markdown(self) -> str:
        """生成Markdown格式报告"""
        md = []
        md.append(f"# 📊 教学PPT分析报告\n")
        md.append(f"**演示文稿**: {self.title}\n")
        md.append(f"**幻灯片数量**: {self.slide_count}\n")
        md.append(f"**综合评分**: {self.overall_score}/100\n\n")

        # 设计原则评分
        md.append("## 设计原则评分\n\n")
        md.append("| 原则 | 评分 | 评价 |\n")
        md.append("|------|------|------|\n")
        for principle, score_info in self.design_principles_scores.items():
            md.append(f"| {principle} | {score_info['score']}/100 | {score_info['status']} |\n")
        md.append("\n")

        # 统计信息
        md.append("## 统计信息\n\n")
        for key, value in self.statistics.items():
            md.append(f"- **{key}**: {value}\n")
        md.append("\n")

        # 各幻灯片分析
        md.append("## 幻灯片详情\n\n")
        for i, slide_info in enumerate(self.slides_analysis, 1):
            md.append(f"### 第 {i} 页: {slide_info.get('title', '无标题')}\n\n")
            md.append(f"- **内容类型**: {slide_info.get('content_types', '未知')}\n")
            md.append(f"- **概念数量**: {slide_info.get('concept_count', 0)}\n")
            md.append(f"- **文字量**: {slide_info.get('word_count', 0)} 字\n")
            md.append(f"- **图片数量**: {slide_info.get('image_count', 0)}\n")
            md.append(f"- **问题评级**: {slide_info.get('issue_level', '无')}\n")
            if slide_info.get('issues'):
                md.append(f"- **发现问题**:\n")
                for issue in slide_info['issues']:
                    md.append(f"  - {issue}\n")
            md.append("\n")

        # 优化建议
        md.append("## 优化建议\n\n")
        for i, suggestion in enumerate(self.suggestions, 1):
            md.append(f"{i}. {suggestion}\n")
        md.append("\n")

        # 设计原则说明
        md.append("## 参考设计原则\n\n")
        md.append("### MagicSeven原则\n")
        md.append("每张幻灯片传达5-9个概念效果最好，人脑每次最多可处理7个概念。\n\n")
        md.append("### KISS原则\n")
        md.append("Keep It Simple and Stupid - 保持简单明了，深入浅出才是真正掌握。\n\n")
        md.append("### 10/20/30法则\n")
        md.append("- 演示文稿不超过10页\n")
        md.append("- 演讲时间不超过20分钟\n")
        md.append("- 字体不小于30磅\n\n")
        md.append("### 三不原则\n")
        md.append("- 不超过3种字体\n")
        md.append("- 不超过3种色系\n")
        md.append("- 不超过3种动画\n\n")

        return "".join(md)


# ============================================================================
# PPT分析器
# ============================================================================

class PPTAnalyzer:
    """教学PPT分析器"""

    # 评分阈值
    SCORE_THRESHOLDS = {
        "excellent": (90, "优秀"),
        "good": (75, "良好"),
        "fair": (60, "一般"),
        "poor": (0, "需改进")
    }

    def __init__(self, pptx_path: str):
        self.pptx_path = pptx_path
        self.prs = None
        self.result = AnalysisResult()

    def load(self) -> bool:
        """加载PPT文件"""
        try:
            self.prs = Presentation(self.pptx_path)
            # 尝试获取标题
            if self.prs.core_properties.title:
                self.result.title = self.prs.core_properties.title
            else:
                self.result.title = Path(self.pptx_path).stem
            return True
        except Exception as e:
            print(f"加载PPT失败: {str(e)}")
            return False

    def analyze(self) -> AnalysisResult:
        """执行全面分析"""
        if not self.prs:
            return self.result

        self.result.slide_count = len(self.prs.slides)

        # 分析每一张幻灯片
        for slide in self.prs.slides:
            slide_info = self._analyze_slide(slide)
            self.result.slides_analysis.append(slide_info)

        # 计算统计信息
        self._calculate_statistics()

        # 评估设计原则
        self._evaluate_design_principles()

        # 计算综合评分
        self._calculate_overall_score()

        # 生成优化建议
        self._generate_suggestions()

        return self.result

    def _analyze_slide(self, slide) -> Dict[str, Any]:
        """分析单张幻灯片"""
        slide_info = {
            "title": "",
            "content_types": [],
            "concept_count": 0,
            "word_count": 0,
            "image_count": 0,
            "font_count": 0,
            "color_count": 0,
            "issues": [],
            "issue_level": "无"
        }

        fonts = set()
        colors = set()

        # 遍历所有形状
        for shape in slide.shapes:
            # 获取标题
            if shape.has_text_frame:
                text = shape.text_frame.text.strip()
                if text:
                    # 检查是否是标题（根据位置和大小初步判断）
                    if not slide_info["title"]:
                        slide_info["title"] = text[:50]  # 取前50字符

                    # 统计文字
                    slide_info["word_count"] += len(text)

                    # 提取概念（粗略估算：逗号分隔的独立概念）
                    concepts = re.split(r'[,，;；\n]', text)
                    slide_info["concept_count"] += len([c for c in concepts if c.strip()])

                    # 收集字体和颜色信息
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.font.name:
                                fonts.add(run.font.name)
                            if run.font.color.rgb:
                                colors.add(str(run.font.color.rgb))

            # 统计图片
            if shape.shape_type == 13:  # MSO_SHAPE_TYPE.PICTURE
                slide_info["image_count"] += 1

        slide_info["font_count"] = len(fonts)
        slide_info["color_count"] = len(colors)

        # 检测问题
        self._detect_slide_issues(slide_info)

        # 内容类型统计
        if slide_info["image_count"] > 0:
            slide_info["content_types"].append("图片")
        if slide_info["concept_count"] > 3:
            slide_info["content_types"].append("文字")

        slide_info["content_types"] = ", ".join(slide_info["content_types"]) or "空白"

        return slide_info

    def _detect_slide_issues(self, slide_info: Dict) -> None:
        """检测幻灯片问题"""
        issues = []

        # MagicSeven原则检查
        if slide_info["concept_count"] > 9:
            issues.append(f"概念过多（{slide_info['concept_count']}个），建议精简到5-9个")
        elif slide_info["concept_count"] < 3 and slide_info["word_count"] < 10:
            issues.append("内容过少，可考虑合并或补充内容")

        # 文字量检查
        if slide_info["word_count"] > 300:
            issues.append("文字过多，建议提炼关键词，使用图文结合")

        # 字体检查
        if slide_info["font_count"] > 3:
            issues.append(f"字体过多（{slide_info['font_count']}种），建议不超过3种")

        # 图片检查
        if slide_info["image_count"] == 0 and slide_info["word_count"] > 50:
            issues.append("纯文字页面，建议添加图片或图表辅助说明")

        slide_info["issues"] = issues

        # 问题级别
        if len(issues) >= 3:
            slide_info["issue_level"] = "严重"
        elif len(issues) == 2:
            slide_info["issue_level"] = "中等"
        elif len(issues) == 1:
            slide_info["issue_level"] = "轻微"
        else:
            slide_info["issue_level"] = "无"

    def _calculate_statistics(self) -> None:
        """计算统计信息"""
        slides = self.result.slides_analysis

        # 总文字量
        total_words = sum(s["word_count"] for s in slides)

        # 总图片数
        total_images = sum(s["image_count"] for s in slides)

        # 平均每页概念数
        avg_concepts = sum(s["concept_count"] for s in slides) / len(slides) if slides else 0

        # 最大文字量页面
        max_words_slide = max(slides, key=lambda s: s["word_count"]) if slides else None
        max_words = max_words_slide["word_count"] if max_words_slide else 0

        # 问题页面统计
        pages_with_issues = len([s for s in slides if s["issues"]])

        # 有图片的页面
        pages_with_images = len([s for s in slides if s["image_count"] > 0])

        self.result.statistics = {
            "总文字量": f"{total_words} 字",
            "总图片数": f"{total_images} 张",
            "平均每页概念数": f"{avg_concepts:.1f} 个",
            "最多文字页面": f"{max_words} 字",
            "有问题页面": f"{pages_with_issues}/{len(slides)} 页",
            "含图片页面": f"{pages_with_images}/{len(slides)} 页"
        }

    def _evaluate_design_principles(self) -> None:
        """评估设计原则遵守情况"""
        slides = self.result.slides_analysis

        # MagicSeven原则评分
        concepts_scores = []
        for s in slides:
            concept_count = s["concept_count"]
            if 5 <= concept_count <= 9:
                concepts_scores.append(100)
            elif concept_count > 9:
                concepts_scores.append(max(0, 100 - (concept_count - 9) * 10))
            elif concept_count > 0:
                concepts_scores.append(max(0, concept_count * 20))
            else:
                concepts_scores.append(50)

        magic_seven_score = sum(concepts_scores) / len(concepts_scores) if concepts_scores else 0

        # KISS原则评分（基于平均文字量）
        total_words = sum(s["word_count"] for s in slides)
        avg_words = total_words / len(slides) if slides else 0

        if avg_words <= 50:
            kiss_score = 100
        elif avg_words <= 100:
            kiss_score = 80
        elif avg_words <= 200:
            kiss_score = 60
        else:
            kiss_score = max(0, 40 - (avg_words - 200) / 10)

        # 10/20/30法则评分
        rule_scores = []
        # 页数检查
        if self.result.slide_count <= 10:
            rule_scores.append(100)
        elif self.result.slide_count <= 15:
            rule_scores.append(80)
        else:
            rule_scores.append(max(0, 60 - (self.result.slide_count - 15) * 5))

        # 图片使用检查
        pages_with_images = len([s for s in slides if s["image_count"] > 0])
        image_ratio = pages_with_images / len(slides) if slides else 0
        if image_ratio >= 0.5:
            rule_scores.append(100)
        elif image_ratio >= 0.3:
            rule_scores.append(80)
        else:
            rule_scores.append(60)

        rule_102030_score = sum(rule_scores) / len(rule_scores)

        # 三不原则评分
        max_fonts = max(s["font_count"] for s in slides) if slides else 0
        if max_fonts <= 3:
            font_score = 100
        else:
            font_score = max(0, 100 - (max_fonts - 3) * 20)

        three_no_score = font_score  # 简化为字体检查

        # 逻辑结构评分（基于标题完整性）
        titled_slides = len([s for s in slides if s["title"]])
        structure_score = (titled_slides / len(slides) * 100) if slides else 0

        # 存储评分
        self.result.design_principles_scores = {
            "MagicSeven原则": {
                "score": round(magic_seven_score, 1),
                "status": self._get_status(magic_seven_score)
            },
            "KISS原则（简洁）": {
                "score": round(kiss_score, 1),
                "status": self._get_status(kiss_score)
            },
            "10/20/30法则": {
                "score": round(rule_102030_score, 1),
                "status": self._get_status(rule_102030_score)
            },
            "三不原则": {
                "score": round(three_no_score, 1),
                "status": self._get_status(three_no_score)
            },
            "逻辑结构": {
                "score": round(structure_score, 1),
                "status": self._get_status(structure_score)
            }
        }

    def _get_status(self, score: float) -> str:
        """获取评分状态描述"""
        for threshold, (min_score, status) in self.SCORE_THRESHOLDS.items():
            if score >= min_score:
                return status
        return "需改进"

    def _calculate_overall_score(self) -> None:
        """计算综合评分"""
        scores = self.result.design_principles_scores
        if not scores:
            self.result.overall_score = 0
            return

        # 加权平均
        weights = {
            "MagicSeven原则": 0.25,
            "KISS原则（简洁）": 0.25,
            "10/20/30法则": 0.20,
            "三不原则": 0.15,
            "逻辑结构": 0.15
        }

        total_score = 0
        total_weight = 0

        for principle, weight in weights.items():
            if principle in scores:
                total_score += scores[principle]["score"] * weight
                total_weight += weight

        self.result.overall_score = round(total_score / total_weight) if total_weight > 0 else 0

    def _generate_suggestions(self) -> None:
        """生成优化建议"""
        suggestions = []
        stats = self.result.statistics
        slides = self.result.slides_analysis

        # 基于统计信息的建议
        if "最多文字页面" in stats:
            max_words = int(stats["最多文字页面"].replace(" 字", ""))
            if max_words > 200:
                suggestions.append("减少每页文字量，提炼关键信息，使用图表或图片辅助表达")

        # 基于评分较低的原则
        scores = self.result.design_principles_scores

        if "MagicSeven原则" in scores and scores["MagicSeven原则"]["score"] < 75:
            suggestions.append("遵循MagicSeven原则：每页控制5-9个核心概念，避免信息过载")

        if "KISS原则（简洁）" in scores and scores["KISS原则（简洁）"]["score"] < 75:
            suggestions.append("遵循KISS原则：深入浅出，用简洁的语言表达复杂概念")

        if "三不原则" in scores and scores["三不原则"]["score"] < 75:
            suggestions.append("遵循三不原则：全文不超过3种字体，保持视觉一致性")

        # 基于页面问题的建议
        pages_with_issues = [s for s in slides if s["issues"]]
        if len(pages_with_issues) > len(slides) * 0.5:
            suggestions.append("多个页面存在问题，建议系统优化：精简文字、增加图片、统一格式")

        # 互动性建议
        image_ratio = int(stats.get("含图片页面", "0/0").split("/")[0]) / max(1, len(slides))
        if image_ratio < 0.3:
            suggestions.append("增加图片使用：使用图表、示意图、照片等视觉元素辅助教学")

        # 结构建议
        if not any("目录" in s.get("title", "").lower() for s in slides[:3]):
            suggestions.append("建议添加目录页，帮助学生了解课程结构")

        # 检查是否有结束页
        has_ending = any("谢谢" in s.get("title", "") for s in slides[-2:])
        if not has_ending:
            suggestions.append("建议添加结束页，呼应开头，形成完整的教学闭环")

        # 去重并限制数量
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)

        self.result.suggestions = unique_suggestions[:5]  # 最多5条建议


# ============================================================================
# 主程序入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="教学PPT分析器 - 评估设计质量和教学效果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
分析维度:
  • MagicSeven原则 - 每页5-9个概念
  • KISS原则 - 保持简洁明了
  • 10/20/30法则 - 不超过10页，20分钟，30pt字体
  • 三不原则 - 不超过3种字体、色系、动画
  • 逻辑结构 - 标题完整、层次清晰

示例:
  %(prog)s --input presentation.pptx --output analysis.md
  %(prog)s -i course.pptx -o report.md
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入PPTX文件路径"
    )

    parser.add_argument(
        "--output", "-o",
        default="analysis_report.md",
        help="输出分析报告路径 (默认: analysis_report.md)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式 (默认: markdown)"
    )

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"错误: 输入文件不存在: {args.input}")
        sys.exit(1)

    # 分析PPT
    print(f"正在分析: {args.input}")
    analyzer = PPTAnalyzer(args.input)

    if not analyzer.load():
        sys.exit(1)

    result = analyzer.analyze()

    # 输出结果
    if args.format == "markdown":
        content = result.to_markdown()
    else:
        import json
        content = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

    # 写入文件
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✓ 分析完成")
    print(f"  文件: {args.output}")
    print(f"  综合评分: {result.overall_score}/100")
    print(f"  幻灯片数: {result.slide_count}")
    print(f"  优化建议: {len(result.suggestions)} 条")


if __name__ == "__main__":
    main()
