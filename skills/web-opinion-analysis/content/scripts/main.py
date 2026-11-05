#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页舆情分析 - 主入口模块
整合爬取、分析、可视化、报告生成全流程
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from crawler import WebCrawler
from analyzer import OpinionAnalyzer
from visualizer import OpinionVisualizer
from report_generator import ReportGenerator


class OpinionAnalysisPipeline:
    """舆情分析流水线"""

    def __init__(self, output_dir="output"):
        """
        初始化流水线

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化各模块
        self.crawler = WebCrawler()
        self.analyzer = OpinionAnalyzer()
        self.visualizer = OpinionVisualizer()
        self.report_generator = ReportGenerator()

    def run(self, url):
        """
        执行完整分析流程

        Args:
            url: 网页URL

        Returns:
            分析结果字典
        """
        print("=" * 60)
        print("🌐 网页舆情分析系统")
        print("=" * 60)
        print(f"目标URL: {url}")
        print()

        # Step 1: 网页爬取
        print("【Step 1/4】网页内容爬取...")
        crawl_result = self.crawler.crawl(url)

        if not crawl_result["success"]:
            print(f"❌ 爬取失败: {crawl_result['error']}")
            return None

        print(f"   ✅ 成功获取标题: {crawl_result['title'][:50]}...")
        print(f"   ✅ 正文长度: {crawl_result['text_length']} 字符")

        # 保存爬取结果
        crawl_file = self.output_dir / "crawl_result.json"
        with open(crawl_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "url": crawl_result["url"],
                    "final_url": crawl_result["final_url"],
                    "title": crawl_result["title"],
                    "text": crawl_result["text"],
                    "paragraphs": crawl_result["paragraphs"],
                    "paragraph_count": crawl_result["paragraph_count"],
                    "text_length": crawl_result["text_length"],
                    "crawl_time": crawl_result["crawl_time"],
                },
                f,
                ensure_ascii=False,
                indent=2,
            )
        print(f"   💾 爬取结果已保存")

        # Step 2: 舆情分析
        print("\n【Step 2/4】多维度舆情分析...")
        analysis_result = self.analyzer.analyze(crawl_result["text"])

        # 添加基础信息到分析结果
        analysis_result["title"] = crawl_result["title"]
        analysis_result["url"] = crawl_result["url"]
        analysis_result["crawl_time"] = crawl_result["crawl_time"]

        # 保存分析结果
        analysis_file = self.output_dir / "analysis_result.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"   💾 分析结果已保存")

        # 打印分析预览
        print("\n   📊 分析结果预览:")
        print(
            f"      情感倾向: {analysis_result['sentiment']['sentiment']} ({analysis_result['sentiment']['score']:.2f})"
        )
        print(
            f"      行业分类: {analysis_result['industry']['industry']} ({analysis_result['industry']['confidence']:.1%})"
        )
        print(
            f"      垃圾文本: {'是' if analysis_result['spam']['is_spam'] else '否'} (得分: {analysis_result['spam']['spam_score']})"
        )

        # Step 3: 可视化生成
        print("\n【Step 3/4】生成可视化图表...")
        viz_file = self.output_dir / "opinion_analysis.png"
        self.visualizer.generate_visualization(analysis_result, viz_file)

        # Step 4: 报告生成
        print("\n【Step 4/4】生成分析报告...")
        report_file = self.output_dir / "opinion_analysis_report.md"
        self.report_generator.generate_report(
            crawl_result, analysis_result, report_file
        )

        # 打印摘要
        print("\n" + "=" * 60)
        print("✅ 分析完成!")
        print("=" * 60)
        print(f"\n📁 输出文件:")
        print(f"   1. 爬取结果: {crawl_file}")
        print(f"   2. 分析结果: {analysis_file}")
        print(f"   3. 可视化图表: {viz_file}")
        print(f"   4. 分析报告: {report_file}")

        # 打印文本摘要
        if analysis_result["summary"]["summary"]:
            print(f"\n📝 文本摘要:")
            for i, sent in enumerate(analysis_result["summary"]["summary"][:3], 1):
                print(f"   {i}. {sent[:80]}{'...' if len(sent) > 80 else ''}")

        return analysis_result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="网页舆情分析 - 一站式分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py https://news.sina.com.cn/c/2024-01-01/001.html
  python main.py https://example.com/article -o ./results
  python main.py https://news.baidu.com -o /tmp/analysis --timeout 60
        """,
    )
    parser.add_argument("url", help="要分析的网页URL")
    parser.add_argument(
        "-o", "--output", default="output", help="输出目录 (默认: output)"
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=30, help="请求超时时间 (秒, 默认: 30)"
    )

    args = parser.parse_args()

    # 验证URL
    if not args.url.startswith(("http://", "https://")):
        print("❌ 错误: URL必须以 http:// 或 https:// 开头")
        sys.exit(1)

    # 创建流水线并运行
    pipeline = OpinionAnalysisPipeline(output_dir=args.output)

    # 修改超时设置
    pipeline.crawler.timeout = args.timeout

    try:
        result = pipeline.run(args.url)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断分析")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 分析出错: {str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
