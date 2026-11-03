#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
政府人事任免信息爬取与管理系统 - 主入口
"""

import sys
import argparse
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper_v6 import FinalGovScraperV6 as GovScraper
from src.updater import IncrementalUpdater
from src.uploader import CSVUploader
from src.ranker import PersonnelRanker
from src.scheduler import Scheduler, setup_signal_handlers


class PersonnelManagementSystem:
    """人事任免管理系统主类"""

    def __init__(self, data_dir: str = './data'):
        self.data_dir = Path(data_dir)
        self.scraper = GovScraper()
        self.updater = IncrementalUpdater(data_dir)
        self.uploader = CSVUploader(data_dir)
        self.ranker = PersonnelRanker(data_dir)
        self.scheduler = Scheduler()

    def run_scrape(self):
        """执行单次爬取任务"""
        print("=" * 60)
        print("开始执行爬取任务")
        print("=" * 60)

        # 初始化文件
        self.updater.ensure_files_exist()

        # 执行爬取
        records = self.scraper.scrape()

        if records:
            # 执行增量更新
            stats = self.updater.update(records, 'scrape')
            print(f"\n爬取完成 - 新增: {stats['added']}, 跳过: {stats['skipped']}")
        else:
            print("\n未发现新的任免信息")

        # 显示统计
        print("\n" + "=" * 60)
        print("当前统计信息")
        print("=" * 60)
        stats = self.updater.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")

    def run_schedule(self):
        """启动定时任务"""
        print("=" * 60)
        print("启动定时任务模式")
        print("=" * 60)

        # 设置信号处理
        setup_signal_handlers(self.scheduler)

        # 立即执行一次
        self.scheduler.run_once(self.run_scrape)

        # 启动调度器
        self.scheduler.start(self.run_scrape, hour=8, minute=0)

        # 主线程保持运行
        try:
            while self.scheduler.running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            self.scheduler.stop()

    def run_upload(self, file_path: str, dry_run: bool = False):
        """执行上传任务"""
        print("=" * 60)
        print(f"开始上传文件: {file_path}")
        print("=" * 60)

        if not Path(file_path).exists():
            print(f"错误: 文件不存在 - {file_path}")
            return

        result = self.uploader.upload(file_path, dry_run=dry_run)

        print("\n上传结果:")
        print(f"  成功: {result['success']}")

        if result['validation']:
            print(f"  有效记录: {result['parse_stats']['valid'] if result['parse_stats'] else 0}")
            print(f"  无效记录: {result['parse_stats']['invalid'] if result['parse_stats'] else 0}")

        if result['update_stats']:
            print(f"  新增到数据库: {result['update_stats']['added']}")
            print(f"  跳过的重复: {result['update_stats']['skipped']}")

        if result['errors']:
            print("\n错误信息:")
            for error in result['errors']:
                print(f"  - {error}")

        if dry_run:
            print("\n[试运行模式] 未实际写入数据库")

    def run_rank(self, names: list, file_path: str = None):
        """执行排序任务"""
        print("=" * 60)
        print(f"开始排序: {', '.join(names)}")
        print("=" * 60)

        # 从CSV查找并排序
        ranked = self.ranker.rank_by_names(
            names,
            from_csv=True if file_path else False,
            csv_path=file_path
        )

        if not ranked:
            print("未找到匹配的记录")
            return

        # 生成报告
        report = self.ranker.generate_ranking_report(ranked, "人员排序报告")
        print("\n" + report)

        return ranked

    def show_statistics(self):
        """显示统计信息"""
        print("=" * 60)
        print("人事任免数据库统计")
        print("=" * 60)

        stats = self.updater.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")

    def list_recent(self, days: int = 7):
        """列出最近记录"""
        print("=" * 60)
        print(f"最近 {days} 天的任免记录")
        print("=" * 60)

        records = self.updater.list_recent_records(days=days)

        if not records:
            print("暂无记录")
            return

        for i, record in enumerate(records, 1):
            print(f"{i:3d}. {record.get('name', ''):8s} | {record.get('action', ''):4s} | "
                  f"{record.get('position', ''):15s} | {record.get('date', '')} | "
                  f"文号: {record.get('doc_no', '无')}")

    def export_data(self, output_path: str, days: int = None):
        """导出数据"""
        print(f"导出数据到: {output_path}")
        count = self.updater.export_csv(output_path, days=days)
        print(f"已导出 {count} 条记录")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='政府人事任免信息爬取与管理系统',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--mode',
        choices=['scrape', 'schedule', 'upload', 'rank', 'stats', 'list', 'export', 'template'],
        default='scrape',
        help='运行模式'
    )

    parser.add_argument(
        '--file',
        help='CSV文件路径（用于上传或导出）'
    )

    parser.add_argument(
        '--names',
        help='姓名列表，逗号分隔（用于排序）'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='天数（用于列表或导出）'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式，不实际写入'
    )

    parser.add_argument(
        '--data-dir',
        default='./data',
        help='数据目录'
    )

    args = parser.parse_args()

    # 创建系统实例
    system = PersonnelManagementSystem(args.data_dir)

    # 根据模式执行
    if args.mode == 'scrape':
        system.run_scrape()

    elif args.mode == 'schedule':
        system.run_schedule()

    elif args.mode == 'upload':
        if not args.file:
            print("错误: 上传模式需要指定 --file 参数")
            sys.exit(1)
        system.run_upload(args.file, dry_run=args.dry_run)

    elif args.mode == 'rank':
        if not args.names:
            print("错误: 排序模式需要指定 --names 参数")
            sys.exit(1)
        names = [n.strip() for n in args.names.split(',')]
        system.run_rank(names, file_path=args.file)

    elif args.mode == 'stats':
        system.show_statistics()

    elif args.mode == 'list':
        system.list_recent(args.days)

    elif args.mode == 'export':
        output = args.file or f'appointments_export_{datetime.now().strftime("%Y%m%d")}.csv'
        system.export_data(output, days=args.days if args.days < 365 else None)

    elif args.mode == 'template':
        template_path = Path(args.data_dir) / 'template.csv'
        system.uploader.generate_template(str(template_path))


if __name__ == '__main__':
    main()
