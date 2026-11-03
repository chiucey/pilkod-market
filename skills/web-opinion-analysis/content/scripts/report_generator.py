#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页舆情分析 - 报告生成模块
生成结构化Markdown格式舆情分析报告
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """舆情分析报告生成器"""

    def __init__(self):
        """初始化报告生成器"""
        pass

    def generate_report(self, crawl_result, analysis_result, output_path):
        """
        生成舆情分析报告

        Args:
            crawl_result: 网页爬取结果
            analysis_result: 分析结果
            output_path: 输出文件路径
        """
        print(f"📝 正在生成分析报告...")

        # 构建报告内容
        report = self._build_report(crawl_result, analysis_result)

        # 保存报告
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ 分析报告已保存到: {output_path}")

        return report

    def _build_report(self, crawl_result, analysis_result):
        """构建报告内容"""
        # 基础信息
        title = crawl_result.get("title", "无标题")
        url = crawl_result.get("url", "")
        crawl_time = crawl_result.get(
            "crawl_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        text_length = crawl_result.get("text_length", 0)
        paragraph_count = crawl_result.get("paragraph_count", 0)

        # 情感分析
        sentiment = analysis_result.get("sentiment", {})
        sentiment_result = sentiment.get("sentiment", "未知")
        sentiment_score = sentiment.get("score", 0)
        sentiment_confidence = sentiment.get("confidence", 0)
        sentiment_desc = sentiment.get("description", "")

        # 垃圾文本检测
        spam = analysis_result.get("spam", {})
        is_spam = spam.get("is_spam", False)
        spam_score = spam.get("spam_score", 0)
        spam_confidence = spam.get("confidence", 0)
        spam_keywords = spam.get("matched_keywords", [])

        # 行业分类
        industry = analysis_result.get("industry", {})
        industry_name = industry.get("industry", "未知")
        industry_confidence = industry.get("confidence", 0)
        industry_keywords = industry.get("matched_keywords", [])

        # 命名实体识别
        ner = analysis_result.get("ner", {})
        top_entities = ner.get("top_entities", [])

        # 文本摘要
        summary = analysis_result.get("summary", {})
        summary_text = summary.get("summary", [])

        # 趋势分析
        trends = analysis_result.get("trends", {})
        keywords = trends.get("keywords", [])
        trend_desc = trends.get("description", "")

        # 构建Markdown报告
        report = f"""# 网页舆情分析报告

> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 基础信息

| 项目 | 内容 |
|------|------|
| **来源网页标题** | {title} |
| **网页URL** | {url} |
| **爬取时间** | {crawl_time} |
| **正文长度** | {text_length} 字符 |
| **段落数量** | {paragraph_count} 段 |

---

## 多维度分析

### 1. 情感分析

| 指标 | 结果 |
|------|------|
| **情感倾向** | {sentiment_result} |
| **情感得分** | {sentiment_score:.4f} (0-1) |
| **置信度** | {sentiment_confidence:.1%} |
| **分析说明** | {sentiment_desc} |

**情感解读**:
{"该文本整体情感积极，正面倾向明显" if sentiment_result == "正面" else "该文本整体情感消极，负面倾向明显" if sentiment_result == "负面" else "该文本情感较为中性，无明显倾向"}

---

### 2. 垃圾文本检测

| 指标 | 结果 |
|------|------|
| **检测结果** | {"⚠️ 疑似垃圾文本" if is_spam else "✅ 正常文本"} |
| **垃圾得分** | {spam_score} 分 |
| **置信度** | {spam_confidence:.1%} |
| **匹配关键词** | {", ".join(spam_keywords) if spam_keywords else "无"} |

**说明**: 垃圾文本检测基于文本长度、广告关键词占比、无意义字符占比等多维度判断。

---

### 3. 行业分类

| 指标 | 结果 |
|------|------|
| **所属行业** | {industry_name} |
| **置信度** | {industry_confidence:.1%} |
| **匹配关键词** | {", ".join(industry_keywords) if industry_keywords else "无"} |

**说明**: 基于预设行业关键词库进行匹配，判断内容所属行业领域。

---

### 4. 命名实体识别

| 排名 | 实体 | 出现频次 |
|------|------|----------|
"""

        # 添加实体列表
        for i, entity in enumerate(top_entities[:5], 1):
            report += f"| {i} | {entity['text']} | {entity['count']} |\n"

        if not top_entities:
            report += "| - | 无数据 | - |\n"

        report += f"""
**说明**: 识别网页中的人名、地名、机构名等命名实体。

---

### 5. 文本摘要

"""

        # 添加摘要内容
        for i, sent in enumerate(summary_text[:3], 1):
            report += f"{i}. {sent}\n"

        if not summary_text:
            report += "无摘要数据\n"

        report += f"""
**说明**: 提取网页核心内容生成的精准摘要。

---

### 6. 热点趋势

**核心关键词 TOP10**:

| 排名 | 关键词 | 频次 |
|------|--------|------|
"""

        # 添加关键词列表
        for i, kw in enumerate(keywords[:10], 1):
            report += f"| {i} | {kw['word']} | {kw['count']} |\n"

        if not keywords:
            report += "| - | 无数据 | - |\n"

        report += f"""
**趋势判断**: {trend_desc}

**说明**: 基于分词统计和TF-IDF算法提取核心关键词，分析热点趋势方向。

---

## 核心数据提炼

### 关键指标一览

- **情感倾向**: {sentiment_result} (得分: {sentiment_score:.2f}, 置信度: {sentiment_confidence:.1%})
- **行业分类**: {industry_name} (置信度: {industry_confidence:.1%})
- **内容安全**: {"存在风险" if is_spam else "正常"} (垃圾得分: {spam_score})
- **核心实体**: {", ".join([e["text"] for e in top_entities[:3]]) if top_entities else "无"}
- **关键词数量**: {len(keywords)} 个

---

## 延伸分析

### 内容特征分析

1. **文本长度**: {"较长" if text_length > 5000 else "中等" if text_length > 2000 else "较短"} (约 {text_length // 500} 分钟左右阅读量)
2. **信息密度**: {"较高" if paragraph_count > 20 else "中等" if paragraph_count > 10 else "较低"} ({paragraph_count} 个有效段落)
3. **专业程度**: {"较高" if industry_confidence > 0.7 else "中等" if industry_confidence > 0.4 else "较低"} (行业识别置信度: {industry_confidence:.1%})

### 舆情风险提示

{"⚠️ 该内容可能存在营销/广告性质，建议谨慎参考" if is_spam else "✅ 该内容为正常文本，信息价值较高"}

---

## 总结洞察

### 核心发现

1. **情感倾向**: 该网页内容整体呈现 **{sentiment_result}** 倾向，情感得分为 {sentiment_score:.2f}，置信度 {sentiment_confidence:.1%}。

2. **内容领域**: 内容主要涉及 **{industry_name}** 领域，匹配关键词包括 {", ".join(industry_keywords[:3]) if industry_keywords else "无明显关键词"}。

3. **信息要点**: {summary_text[0][:50] + "..." if summary_text and len(summary_text[0]) > 50 else summary_text[0] if summary_text else "无摘要"}

4. **热度话题**: 当前讨论热点集中在 **{", ".join([k["word"] for k in keywords[:3]]) if keywords else "无数据"}** 等话题。

### 建议

- {"内容情感偏正面，适合正面宣传场景使用" if sentiment_result == "正面" else "内容情感偏负面，需注意舆情引导" if sentiment_result == "负面" else "内容情感中性，可客观引用"}
- {"内容检测为正常文本，信息可信度较高" if not is_spam else "内容可能包含广告信息，需核实关键数据"}
- 建议结合行业背景和具体场景进行深度分析

---

> 报告生成工具: 网页舆情分析Agent Skill
> 分析时间: {analysis_result.get("analysis_time", "")}
"""

        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="网页舆情分析 - 报告生成工具")
    parser.add_argument("analysis_result", help="分析结果JSON文件路径")
    parser.add_argument("-c", "--crawl-result", help="爬取结果JSON文件路径")
    parser.add_argument(
        "-o", "--output", default="opinion_analysis_report.md", help="输出报告路径"
    )

    args = parser.parse_args()

    # 读取分析结果
    analysis_path = Path(args.analysis_result)
    if not analysis_path.exists():
        print(f"❌ 文件不存在: {args.analysis_result}")
        sys.exit(1)

    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis_result = json.load(f)

    # 读取爬取结果（可选）
    crawl_result = {}
    if args.crawl_result:
        crawl_path = Path(args.crawl_result)
        if crawl_path.exists():
            with open(crawl_path, "r", encoding="utf-8") as f:
                crawl_result = json.load(f)
    else:
        # 尝试从分析结果中推断
        crawl_result = {
            "title": analysis_result.get("title", "未知"),
            "url": analysis_result.get("url", ""),
            "crawl_time": analysis_result.get(
                "crawl_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
            "text_length": analysis_result.get("text_length", 0),
            "paragraph_count": 0,
        }

    # 生成报告
    generator = ReportGenerator()
    generator.generate_report(crawl_result, analysis_result, args.output)


if __name__ == "__main__":
    main()
