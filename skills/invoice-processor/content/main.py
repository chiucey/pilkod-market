#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
发票处理智能体主入口
整合所有模块，提供完整的发票处理功能
"""
import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入模块
from core.scanner import FileScanner
from core.deduplicator import InvoiceDeduplicator
from core.extractor import InvoiceExtractor
from parsers.pdf_parser import PDFParser
from parsers.xml_parser import CtripXMLParser
from parsers.image_parser import ImageParser
from processors.travel_processor import TravelProcessor
from processors.rename_processor import RenameProcessor
from processors.report_generator import ReportGenerator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InvoiceProcessingAgent:
    """发票处理智能体"""

    def __init__(self, folder_path: str, base_city: str = "南京", llm_client=None):
        """
        初始化发票处理智能体

        Args:
            folder_path: 发票文件夹路径
            base_city: 出差基准城市（默认南京）
            llm_client: 大模型客户端（可选，用于增强提取）
        """
        self.folder_path = Path(folder_path)
        self.base_city = base_city
        self.llm_client = llm_client

        # 初始化组件
        self.scanner = FileScanner(folder_path)
        self.extractor = InvoiceExtractor(llm_client)
        self.deduplicator = InvoiceDeduplicator(llm_client)
        self.pdf_parser = PDFParser(self.extractor)
        self.xml_parser = CtripXMLParser()
        self.image_parser = ImageParser(self.extractor)
        self.travel_processor = TravelProcessor(base_city)
        self.rename_processor = RenameProcessor()
        self.report_generator = ReportGenerator()

        # 数据存储
        self.invoices: List[Dict] = []
        self.trips: List[Dict] = []
        self.summary: Dict[str, Any] = {}

        # 处理结果
        self.result = {
            "status": "success",
            "message": "",
            "files_scanned": 0,
            "files_deduplicated": 0,
            "invoices_extracted": 0,
            "trips_identified": 0,
            "files_renamed": 0,
            "report_path": "",
            "summary": {},
            "missing_items": [],
            "errors": []
        }

    def process(self) -> Dict[str, Any]:
        """
        执行完整的发票处理流程

        Returns:
            Dict: 处理结果
        """
        try:
            print("=" * 60)
            print("发票处理智能体启动")
            print(f"目标文件夹: {self.folder_path}")
            print(f"基准城市: {self.base_city}")
            print("=" * 60)

            # 1. 扫描文件
            print("\n[1/6] 扫描文件...")
            self._scan_files()

            # 2. 去重处理
            print("\n[2/6] 去重处理...")
            self._deduplicate_files()

            # 3. 解析发票
            print("\n[3/6] 解析发票内容...")
            self._parse_invoices()

            # 4. 处理出差行程
            print("\n[4/6] 分析出差行程...")
            self._process_travel()

            # 5. 生成报表
            print("\n[5/6] 生成报销报表...")
            self._generate_reports()

            # 6. 重命名文件
            print("\n[6/6] 重命名发票文件...")
            self._rename_files()

            # 生成汇总
            self._generate_summary()

            # 更新结果
            self.result["status"] = "success"
            self.result["message"] = "处理完成"

            # 打印汇总
            self._print_summary()

        except Exception as e:
            self.result["status"] = "error"
            self.result["message"] = str(e)
            self.result["errors"].append(str(e))
            logger.error(f"处理失败: {e}", exc_info=True)

        return self.result

    def _scan_files(self):
        """扫描文件夹"""
        try:
            files_by_type = self.scanner.scan()
            total_files = sum(len(files) for files in files_by_type.values())

            self.result["files_scanned"] = total_files
            self.result["files_by_type"] = self.scanner.get_summary()

            print(f"   发现文件总数: {total_files}")
            for category, count in self.result["files_by_type"].items():
                if category != '总计' and count > 0:
                    print(f"   - {category}: {count}")

        except Exception as e:
            logger.error(f"扫描文件失败: {e}")
            raise

    def _deduplicate_files(self):
        """去重文件"""
        try:
            all_files = self.scanner.get_all_files_list()
            unique_files = self.deduplicator.deduplicate(all_files, self._read_file_content)

            self.result["files_deduplicated"] = len(unique_files)
            self.result["duplicates_removed"] = len(all_files) - len(unique_files)

            print(f"   去重后保留: {len(unique_files)} 个文件")
            print(f"   删除重复文件: {len(all_files) - len(unique_files)} 个")

            self.unique_files = unique_files

        except Exception as e:
            logger.error(f"去重失败: {e}")
            self.unique_files = self.scanner.get_all_files_list()

    def _read_file_content(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            suffix = file_path.suffix.lower()

            if suffix == '.pdf':
                return self._read_pdf_content(file_path)
            elif suffix == '.xml':
                return self._read_xml_content(file_path)
            else:
                return ""

        except Exception as e:
            logger.warning(f"读取文件内容失败 {file_path}: {e}")
            return ""

    def _read_pdf_content(self, file_path: Path) -> str:
        """读取PDF文件内容"""
        try:
            with open(file_path, 'rb') as f:
                # 简单读取PDF文本
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                return text
        except:
            return ""

    def _read_xml_content(self, file_path: Path) -> str:
        """读取XML文件内容"""
        try:
            return file_path.read_text(encoding='utf-8')
        except:
            try:
                return file_path.read_text(encoding='gbk')
            except:
                return ""

    def _parse_invoices(self):
        """解析发票内容"""
        for i, file_path in enumerate(self.unique_files, 1):
            try:
                invoice_data = self._parse_file(file_path)
                if invoice_data:
                    invoice_data['file_path'] = str(file_path)
                    invoice_data['file_name'] = file_path.name
                    self.invoices.append(invoice_data)
                    print(f"   [{i}/{len(self.unique_files)}] {file_path.name} -> {invoice_data.get('type', 'unknown')}")
            except Exception as e:
                logger.warning(f"解析失败 {file_path}: {e}")
                self.result["errors"].append(f"解析失败: {file_path.name}")

        self.result["invoices_extracted"] = len(self.invoices)
        print(f"   成功提取: {len(self.invoices)} 条发票记录")

    def _parse_file(self, file_path: Path) -> Dict:
        """根据文件类型解析"""
        suffix = file_path.suffix.lower()

        if suffix == '.pdf':
            return self.pdf_parser.parse(file_path)
        elif suffix == '.ofd':
            # OFD暂用PDF解析器
            return self.pdf_parser.parse(file_path)
        elif suffix == '.xml':
            return self.xml_parser.parse(file_path)
        elif suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            return self.image_parser.parse(file_path)
        else:
            return None

    def _process_travel(self):
        """处理出差行程"""
        self.trips = self.travel_processor.process(self.invoices)
        self.result["trips_identified"] = len(self.trips)
        print(f"   识别出: {len(self.trips)} 次出差")

        # 收集缺失票据
        for trip in self.trips:
            for missing in trip.get('missing_items', []):
                self.result["missing_items"].append(f"行程{trip['trip_id']}: {missing}")

        if self.result["missing_items"]:
            print(f"   发现缺失票据: {len(self.result['missing_items'])} 项")

    def _generate_reports(self):
        """生成报表"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.folder_path / f"报销明细_{timestamp}.xlsx"

        # 生成各类报表
        main_report = self.report_generator.generate_main_report(self.invoices)
        type_reports = self.report_generator.generate_type_reports(self.invoices)
        travel_report = self.report_generator.generate_travel_report(self.trips, self.base_city)

        # 保存到Excel
        self.report_generator.save_to_excel(
            main_report, type_reports, travel_report,
            str(output_path), self.base_city
        )

        self.result["report_path"] = str(output_path)
        print(f"   报表已保存: {output_path.name}")

    def _rename_files(self):
        """重命名文件"""
        renamed_count = self.rename_processor.rename_files(self.invoices)
        self.result["files_renamed"] = renamed_count
        print(f"   重命名了 {renamed_count} 个文件")

    def _generate_summary(self):
        """生成汇总信息"""
        self.summary = self.report_generator.generate_summary(self.invoices, self.trips)
        self.result["summary"] = self.summary

    def _print_summary(self):
        """打印处理汇总"""
        print("\n" + "=" * 60)
        print("处理完成！")
        print("=" * 60)
        print(f"\n📊 统计信息:")
        print(f"   - 扫描文件数: {self.result['files_scanned']}")
        print(f"   - 去重后文件: {self.result['files_deduplicated']}")
        print(f"   - 提取发票数: {self.result['invoices_extracted']}")
        print(f"   - 识别出差数: {self.result['trips_identified']}")
        print(f"   - 重命名文件: {self.result['files_renamed']}")

        if self.summary:
            print(f"\n💰 费用汇总:")
            print(f"   - 发票总金额: ¥{self.summary['total_amount']:.2f}")
            for type_name, amount in self.summary.get('type_amounts', {}).items():
                if amount > 0:
                    print(f"     {type_name}: ¥{amount:.2f}")

        if self.result["missing_items"]:
            print(f"\n⚠️ 缺失票据:")
            for missing in self.result["missing_items"]:
                print(f"   - {missing}")

        if self.result["errors"]:
            print(f"\n❌ 处理错误:")
            for error in self.result["errors"]:
                print(f"   - {error}")

        print(f"\n📄 报表位置: {self.result['report_path']}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='发票处理智能体')
    parser.add_argument('folder_path', help='发票文件夹路径')
    parser.add_argument('--base-city', default='南京', help='出差基准城市')
    parser.add_argument('--output', help='输出结果JSON文件路径')

    args = parser.parse_args()

    # 检查文件夹是否存在
    if not os.path.exists(args.folder_path):
        print(f"错误: 文件夹不存在 - {args.folder_path}")
        sys.exit(1)

    # 创建智能体并处理
    agent = InvoiceProcessingAgent(args.folder_path, args.base_city)
    result = agent.process()

    # 输出结果JSON
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    # 返回状态码
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
