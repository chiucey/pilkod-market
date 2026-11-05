#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页舆情分析 - 可视化图表生成模块
生成4维度可视化图表：情感占比饼图、关键词频次柱状图、实体TOP5横向图、垃圾文本判断图
"""

import json
import sys
import argparse
from pathlib import Path

import matplotlib

# 设置中文字体支持
matplotlib.use("Agg")  # 非交互式后端
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 配置中文字体
plt.rcParams["font.sans-serif"] = [
    "SimHei",
    "Microsoft YaHei",
    "WenQuanYi Micro Hei",
    "Noto Sans CJK SC",
    "DejaVu Sans",
]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


# 尝试查找系统中可用的中文字体
def find_chinese_font():
    """查找可用的中文字体"""
    font_list = fm.findSystemFonts()

    chinese_fonts = [
        "SimHei",
        "Microsoft YaHei",
        "WenQuanYi",
        "Noto Sans CJK",
        "Source Han Sans",
        "PingFang",
        "STHeiti",
        "STSong",
        "FangSong",
        "KaiTi",
    ]

    for font in font_list:
        font_name = Path(font).stem.lower()
        for cf in chinese_fonts:
            if cf.lower() in font_name:
                return font

    return None


# 设置字体
chinese_font = find_chinese_font()
if chinese_font:
    plt.rcParams["font.sans-serif"] = [chinese_font] + plt.rcParams["font.sans-serif"]


class OpinionVisualizer:
    """舆情可视化生成器"""

    # 配色方案
    COLORS = {
        "positive": ["#2ecc71", "#27ae60", "#82e0aa", "#abebc6"],
        "negative": ["#e74c3c", "#c0392b", "#f1948a", "#f5b7b1"],
        "neutral": ["#95a5a6", "#7f8c8d", "#bdc3c7", "#d5dbdb"],
        "spam": ["#e67e22", "#d35400", "#f0b27a", "#f5cba7"],
        "normal": ["#3498db", "#2980b9", "#85c1e9", "#aed6f1"],
        "default": ["#9b59b6", "#8e44ad", "#bb8fce", "#d2b4de"],
    }

    # 图表尺寸和DPI
    FIG_SIZE = (12, 10)
    DPI = 300

    def __init__(self):
        """初始化可视化器"""
        pass

    def plot_sentiment_pie(self, ax, sentiment_data):
        """
        绘制情感占比饼图

        Args:
            ax: matplotlib axes对象
            sentiment_data: 情感分析数据
        """
        sentiment = sentiment_data.get("sentiment", "中性")
        score = sentiment_data.get("score", 0.5)
        confidence = sentiment_data.get("confidence", 0.5)

        # 根据情感倾向设置颜色
        if sentiment == "正面":
            colors = self.COLORS["positive"]
            explode = (0.05, 0, 0)
        elif sentiment == "负面":
            colors = self.COLORS["negative"]
            explode = (0, 0.05, 0)
        else:
            colors = self.COLORS["neutral"]
            explode = (0, 0, 0.05)

        # 构建数据
        sizes = [score, 0.5 - abs(score - 0.5), 1 - score]
        labels = [f"{sentiment}\n({score:.2f})", "中性", "对立面"]
        sizes = [max(0.01, s) for s in sizes]  # 避免0值

        # 绘制饼图
        wedges, texts, autotexts = ax.pie(
            sizes,
            explode=explode,
            labels=labels,
            colors=colors[:3],
            autopct="%1.1f%%",
            startangle=90,
            shadow=False,
        )

        # 设置样式
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(9)
            autotext.set_weight("bold")

        ax.set_title(
            f"情感分析结果\n({sentiment}, 置信度: {confidence:.1%})",
            fontsize=12,
            fontweight="bold",
        )

    def plot_keywords_bar(self, ax, trends_data):
        """
        绘制关键词频次柱状图

        Args:
            ax: matplotlib axes对象
            trends_data: 趋势分析数据
        """
        keywords = trends_data.get("keywords", [])[:10]

        if not keywords:
            ax.text(0.5, 0.5, "无关键词数据", ha="center", va="center", fontsize=12)
            ax.set_title("关键词频次", fontsize=12, fontweight="bold")
            return

        # 准备数据
        words = [k["word"][:8] for k in keywords]  # 限制长度
        counts = [k["count"] for k in keywords]

        # 颜色渐变
        colors = plt.cm.Blues([0.4 + 0.5 * (i / len(words)) for i in range(len(words))])

        # 绘制水平柱状图
        y_pos = range(len(words))
        bars = ax.barh(y_pos, counts, color=colors, edgecolor="white", height=0.7)

        # 设置标签
        ax.set_yticks(y_pos)
        ax.set_yticklabels(words, fontsize=9)
        ax.invert_yaxis()  # 最高频的在上面

        # 添加数值标签
        for bar, count in zip(bars, counts):
            ax.text(
                bar.get_width() + 0.5,
                bar.get_y() + bar.get_height() / 2,
                str(count),
                va="center",
                fontsize=8,
            )

        ax.set_xlabel("出现频次", fontsize=10)
        ax.set_title("关键词频次 TOP10", fontsize=12, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    def plot_entities_bar(self, ax, ner_data):
        """
        绘制实体TOP5横向图

        Args:
            ax: matplotlib axes对象
            ner_data: 命名实体识别数据
        """
        entities = ner_data.get("top_entities", [])[:5]

        if not entities:
            ax.text(0.5, 0.5, "无实体数据", ha="center", va="center", fontsize=12)
            ax.set_title("命名实体 TOP5", fontsize=12, fontweight="bold")
            return

        # 准备数据
        entity_names = [e["text"][:10] for e in entities]  # 限制长度
        entity_counts = [e["count"] for e in entities]

        # 颜色
        colors = plt.cm.Purples(
            [0.4 + 0.5 * (i / len(entities)) for i in range(len(entities))]
        )

        # 绘制水平柱状图
        y_pos = range(len(entities))
        bars = ax.barh(
            y_pos, entity_counts, color=colors, edgecolor="white", height=0.7
        )

        # 设置标签
        ax.set_yticks(y_pos)
        ax.set_yticklabels(entity_names, fontsize=9)
        ax.invert_yaxis()

        # 添加数值标签
        for bar, count in zip(bars, entity_counts):
            ax.text(
                bar.get_width() + 0.1,
                bar.get_y() + bar.get_height() / 2,
                str(count),
                va="center",
                fontsize=8,
            )

        ax.set_xlabel("出现频次", fontsize=10)
        ax.set_title("命名实体 TOP5", fontsize=12, fontweight="bold")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    def plot_spam_detection(self, ax, spam_data):
        """
        绘制垃圾文本判断图

        Args:
            ax: matplotlib axes对象
            spam_data: 垃圾文本检测数据
        """
        is_spam = spam_data.get("is_spam", False)
        spam_score = spam_data.get("spam_score", 0)
        confidence = spam_data.get("confidence", 0)

        # 创建仪表盘样式
        # 绘制背景
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 1)

        # 绘制刻度背景
        for i, (start, end, color) in enumerate(
            [
                (0, 30, self.COLORS["normal"][0]),
                (30, 60, self.COLORS["neutral"][0]),
                (60, 80, self.COLORS["spam"][0]),
                (80, 100, self.COLORS["negative"][0]),
            ]
        ):
            ax.barh(0.3, end - start, left=start, height=0.4, color=color, alpha=0.7)

        # 绘制指针
        ax.annotate(
            "",
            xy=(spam_score, 0.5),
            xytext=(spam_score, 0.1),
            arrowprops=dict(arrowstyle="->", color="red", lw=3),
        )

        # 添加分数标签
        ax.text(
            spam_score,
            0.7,
            f"{spam_score}",
            ha="center",
            fontsize=20,
            fontweight="bold",
        )

        # 添加判断结果
        result = "垃圾文本" if is_spam else "正常文本"
        result_color = self.COLORS["spam"][0] if is_spam else self.COLORS["normal"][0]

        ax.text(
            50,
            0.9,
            result,
            ha="center",
            fontsize=14,
            fontweight="bold",
            color=result_color,
        )

        # 添加置信度
        ax.text(50, -0.1, f"置信度: {confidence:.1%}", ha="center", fontsize=10)

        ax.set_title(
            f"垃圾文本检测 (得分: {spam_score})", fontsize=12, fontweight="bold"
        )
        ax.axis("off")

    def generate_visualization(self, analysis_result, output_path):
        """
        生成可视化图表

        Args:
            analysis_result: 分析结果字典
            output_path: 输出文件路径
        """
        print(f"🎨 正在生成可视化图表...")

        # 创建画布 - 2x2布局
        fig, axes = plt.subplots(2, 2, figsize=self.FIG_SIZE)
        fig.suptitle("网页舆情分析报告", fontsize=16, fontweight="bold", y=0.98)

        # 1. 情感分析饼图
        self.plot_sentiment_pie(axes[0, 0], analysis_result.get("sentiment", {}))

        # 2. 关键词频次柱状图
        self.plot_keywords_bar(axes[0, 1], analysis_result.get("trends", {}))

        # 3. 命名实体横向图
        self.plot_entities_bar(axes[1, 0], analysis_result.get("ner", {}))

        # 4. 垃圾文本检测
        self.plot_spam_detection(axes[1, 1], analysis_result.get("spam", {}))

        # 调整布局
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # 保存图片
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            output_path,
            dpi=self.DPI,
            bbox_inches="tight",
            facecolor="white",
            edgecolor="none",
        )

        print(f"✅ 可视化图表已保存到: {output_path}")

        # 关闭画布释放内存
        plt.close(fig)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="网页舆情分析 - 可视化图表生成工具")
    parser.add_argument("input", help="分析结果JSON文件路径")
    parser.add_argument(
        "-o", "--output", default="opinion_analysis.png", help="输出图片路径"
    )

    args = parser.parse_args()

    # 读取分析结果
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        analysis_result = json.load(f)

    # 生成可视化
    visualizer = OpinionVisualizer()
    visualizer.generate_visualization(analysis_result, args.output)


if __name__ == "__main__":
    main()
