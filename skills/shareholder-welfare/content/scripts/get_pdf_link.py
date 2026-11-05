#!/usr/bin/env python3
"""
获取巨潮资讯网PDF公告链接
支持通过股票代码和日期获取官方PDF链接
"""

import argparse
import re
from datetime import datetime


def generate_pdf_link(stock_code: str, date: str) -> str:
    """
    根据股票代码和日期生成巨潮资讯网PDF链接

    Args:
        stock_code: 股票代码（如 300908）
        date: 公告日期（格式：YYYY-MM-DD 或 YYYYMMDD）

    Returns:
        PDF下载链接
    """
    # 清理日期格式
    date_str = date.replace("-", "")

    # 提取年份
    year = date_str[:4]

    # 生成PDF链接
    # 巨潮资讯网PDF链接格式: http://static.cninfo.com.cn/finalpage/{年份}/{日期}-{股票代码}-001.PDF
    pdf_link = f"http://static.cninfo.com.cn/finalpage/{year}/{date_str}-{stock_code}-001.PDF"

    return pdf_link


def validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式
    A股股票代码通常为6位数字
    """
    pattern = r"^\d{6}$"
    return bool(re.match(pattern, stock_code))


def validate_date(date_str: str) -> bool:
    """
    验证日期格式
    支持 YYYY-MM-DD 和 YYYYMMDD 格式
    """
    formats = ["%Y-%m-%d", "%Y%m%d"]
    for fmt in formats:
        try:
            datetime.strptime(date_str.replace("-", ""), fmt)
            return True
        except ValueError:
            continue
    return False


def main():
    """主函数：解析参数并生成PDF链接"""
    parser = argparse.ArgumentParser(
        description="获取巨潮资讯网股东福利公告PDF链接"
    )
    parser.add_argument(
        "--code",
        required=True,
        help="股票代码（如 300908）"
    )
    parser.add_argument(
        "--date",
        required=True,
        help="公告日期（格式：YYYY-MM-DD 或 YYYYMMDD）"
    )

    args = parser.parse_args()

    # 验证输入
    if not validate_stock_code(args.code):
        print(f"错误：无效的股票代码格式: {args.code}")
        print("股票代码应为6位数字，如 300908")
        return

    if not validate_date(args.date):
        print(f"错误：无效的日期格式: {args.date}")
        print("日期格式应为 YYYY-MM-DD 或 YYYYMMDD")
        return

    # 生成PDF链接
    pdf_link = generate_pdf_link(args.code, args.date)

    result = {
        "stock_code": args.code,
        "date": args.date.replace("-", ""),
        "pdf_link": pdf_link,
        "source": "巨潮资讯网 (cninfo.com.cn)"
    }

    print(pdf_link)


if __name__ == "__main__":
    main()
