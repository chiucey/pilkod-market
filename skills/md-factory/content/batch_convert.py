#!/usr/bin/env python3
"""
批量文档转换脚本

批量将目录中的所有支持的文件转换为Markdown格式。
"""

import os
import sys
import argparse
from datetime import datetime

try:
    from markitdown import MarkItDown
except ImportError:
    print("错误：未找到markitdown库。请先安装：")
    print("  pip install markitdown")
    sys.exit(1)


SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".pptx",
    ".html", ".htm", ".csv", ".json", ".xml",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
    ".mp3", ".wav", ".m4a", ".flac", ".ogg",
    ".zip"
}


class BatchConverter:
    """批量转换器"""

    def __init__(self, verbose: bool = False, log_file: str = None):
        self.verbose = verbose
        self.log_file = log_file
        self.md = MarkItDown()
        self.stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}
        self.errors = []

    def log(self, message: str):
        """输出日志信息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)

        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(log_message + "\n")
            except Exception as e:
                print(f"警告：写入日志失败 - {str(e)}")

    def should_process(self, filename: str) -> bool:
        """检查文件是否应该被处理"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in SUPPORTED_EXTENSIONS

    def get_output_path(self, input_path: str, input_dir: str, output_dir: str) -> str:
        """计算输出文件路径"""
        rel_path = os.path.relpath(input_path, input_dir)
        output_name = os.path.splitext(rel_path)[0] + ".md"

        if rel_path.endswith(".zip"):
            base_name = os.path.splitext(os.path.splitext(rel_path)[0])[0]
            output_name = base_name + ".md"

        return os.path.join(output_dir, output_name)

    def convert_file(self, input_path: str, output_path: str) -> bool:
        """转换单个文件"""
        try:
            if self.verbose:
                self.log(f"正在转换：{input_path}")

            result = self.md.convert(input_path)

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.text_content)

            self.stats["success"] += 1
            return True

        except Exception as e:
            self.stats["failed"] += 1
            error_msg = f"{input_path}: {str(e)}"
            self.errors.append(error_msg)
            self.log(f"转换失败：{error_msg}")
            return False

    def convert_directory(self, input_dir: str, output_dir: str, recursive: bool = True) -> dict:
        """批量转换目录中的文件"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        self.log(f"开始批量转换...")
        self.log(f"输入目录：{input_dir}")
        self.log(f"输出目录：{output_dir}")
        self.log("-" * 50)

        for root, dirs, files in os.walk(input_dir):
            rel_root = os.path.relpath(root, input_dir)

            for filename in files:
                if not self.should_process(filename):
                    self.stats["skipped"] += 1
                    continue

                self.stats["total"] += 1

                input_path = os.path.join(root, filename)
                output_path = self.get_output_path(input_path, input_dir, output_dir)

                self.convert_file(input_path, output_path)

            if not recursive:
                break

        return self.stats

    def print_summary(self):
        """打印转换统计摘要"""
        self.log("-" * 50)
        self.log("转换完成！")
        self.log(f"总计：{self.stats['total']}")
        self.log(f"成功：{self.stats['success']}")
        self.log(f"失败：{self.stats['failed']}")
        self.log(f"跳过：{self.stats['skipped']}")

        if self.errors:
            self.log("\n失败文件列表：")
            for error in self.errors:
                self.log(f"  - {error}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="批量文档转Markdown工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s ./documents/ -o ./markdown/         # 批量转换目录
  %(prog)s ./docs/ -o ./output/ --verbose    # 显示详细输出
  %(prog)s ./files/ -o ./md/ --log log.txt   # 保存转换日志
        """
    )

    parser.add_argument("input_dir", help="输入目录路径")
    parser.add_argument("-o", "--output-dir", required=True, help="输出目录路径")
    parser.add_argument("--verbose", action="store_true", help="显示详细输出")
    parser.add_argument("--log", dest="log_file", help="日志文件路径")
    parser.add_argument("--no-recursive", action="store_true", help="不递归处理子目录")

    args = parser.parse_args()

    converter = BatchConverter(verbose=args.verbose, log_file=args.log_file)

    converter.convert_directory(args.input_dir, args.output_dir, recursive=not args.no_recursive)
    converter.print_summary()

    return 0 if converter.stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
