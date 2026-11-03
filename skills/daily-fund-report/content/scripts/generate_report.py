#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金收益报表生成主程序
整合数据获取、收益分析、飞书推送
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from fetch_fund_data import FundDataFetcher
from analyze_returns import ReturnsAnalyzer
from send_feishu import FeishuNotifier


class FundReportGenerator:
    """基金收益报表生成器"""

    def __init__(
        self,
        portfolio_file: str,
        feishu_webhook: str,
        output_dir: str = "data/reports"
    ):
        """
        初始化生成器

        Args:
            portfolio_file: 持仓配置文件路径
            feishu_webhook: 飞书Webhook地址
            output_dir: 报表输出目录
        """
        self.portfolio_file = portfolio_file
        self.feishu_webhook = feishu_webhook
        self.output_dir = output_dir

        # 创建数据目录
        os.makedirs(output_dir, exist_ok=True)

        # 初始化组件
        self.fetcher = FundDataFetcher()

    def load_portfolio(self) -> List[Dict]:
        """加载持仓数据"""
        with open(self.portfolio_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("holdings", [])

    def generate(self, send_to_feishu: bool = True) -> Dict:
        """
        生成报表

        Args:
            send_to_feishu: 是否推送到飞书

        Returns:
            报表数据字典
        """
        print("=" * 50)
        print("📊 基金收益报表生成器")
        print("=" * 50)

        # 1. 加载持仓
        print("\n📂 步骤1: 加载持仓数据...")
        holdings = self.load_portfolio()
        fund_codes = [h.get("code") for h in holdings]
        print(f"   共 {len(holdings)} 只基金")

        # 2. 获取净值
        print("\n🌐 步骤2: 获取基金净值数据...")
        fund_data = {}
        for code in fund_codes:
            print(f"   正在获取 {code}...", end=" ")
            data = self.fetcher.get_realtime_nav(code)
            if data:
                fund_data[code] = data
                print(f"✓ 净值: {data['nav']:.4f} ({data['change_pct']:+.2f}%)")
            else:
                print("✗ 获取失败")

        print(f"   成功获取 {len(fund_data)}/{len(fund_codes)} 只基金数据")

        # 3. 分析收益
        print("\n📈 步骤3: 分析收益情况...")
        analyzer = ReturnsAnalyzer(holdings)
        analyses = analyzer.analyze(fund_data)

        # 4. 保存报表
        print("\n💾 步骤4: 保存报表...")
        report_data = analyzer.to_dict()
        date_str = datetime.now().strftime("%Y%m%d")
        report_file = os.path.join(self.output_dir, f"report_{date_str}.json")

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"   报表已保存: {report_file}")

        # 5. 打印摘要
        print("\n" + "=" * 50)
        print("📊 报表摘要")
        print("=" * 50)
        print(analyzer.format_summary())

        # 6. 推送飞书
        if send_to_feishu:
            print("\n📤 步骤5: 推送到飞书...")
            notifier = FeishuNotifier(self.feishu_webhook)
            result = notifier.send_fund_report_card(report_data)

            if result.get("success"):
                print("   ✅ 飞书消息发送成功!")
            else:
                print(f"   ❌ 发送失败: {result.get('message')}")

        print("\n" + "=" * 50)
        print("✨ 报表生成完成!")
        print("=" * 50)

        return report_data


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="基金收益报表生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python generate_report.py --portfolio assets/portfolio.json --feishu-webhook "https://..."

  # 仅生成报表，不发送飞书
  python generate_report.py --portfolio assets/portfolio.json --feishu-webhook "https://..." --no-send

  # 指定输出目录
  python generate_report.py --portfolio assets/portfolio.json --feishu-webhook "https://..." --output data/my_reports
        """
    )

    parser.add_argument(
        "--portfolio",
        required=True,
        help="持仓配置文件路径 (JSON格式)"
    )
    parser.add_argument(
        "--feishu-webhook",
        required=True,
        help="飞书Webhook地址"
    )
    parser.add_argument(
        "--output",
        default="data/reports",
        help="报表输出目录 (默认: data/reports)"
    )
    parser.add_argument(
        "--no-send",
        action="store_true",
        help="仅生成报表，不发送飞书"
    )

    args = parser.parse_args()

    # 检查持仓文件
    if not os.path.exists(args.portfolio):
        print(f"❌ 持仓文件不存在: {args.portfolio}")
        sys.exit(1)

    # 生成报表
    generator = FundReportGenerator(
        portfolio_file=args.portfolio,
        feishu_webhook=args.feishu_webhook,
        output_dir=args.output
    )

    generator.generate(send_to_feishu=not args.no_send)


if __name__ == "__main__":
    main()
