#!/usr/bin/env python3
"""
AShare Data Skill - 中国A股行情数据获取工具

使用方式:
    python3 ashare_data.py <command> [options]

命令:
    code        查询股票代码
    eod         获取日行情数据
    finance     获取财务指标
    income      获取利润表
    balance     获取资产负债表
    moneyflow   获取资金流向
    list        列出支持的表

示例:
    python3 ashare_data.py code --keyword 茅台
    python3 ashare_data.py eod --code 600519.SH --start 20240101 --end 20240301
    python3 ashare_data.py finance --code 600519.SH --period 20231231
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Optional, Any
import pymysql
from pathlib import Path

# 数据库配置 - 从环境变量读取
DB_CONFIG = {
    "host": os.getenv("ASHARE_DB_HOST"),
    "user": os.getenv("ASHARE_DB_USER"),
    "password": os.getenv("ASHARE_DB_PASSWORD"),
    "database": os.getenv("ASHARE_DB_NAME"),
    "port": int(os.getenv("ASHARE_DB_PORT")),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# Schema 目录
SCHEMA_DIR = Path(__file__).parent.parent / "schema"


class AShareDataClient:
    """A股数据客户端"""
    
    # 支持的A股数据表（基于 MinerU 提取的数据字典）
    # 注意：表名与文件名保持一致（混合大小写）
    SUPPORTED_TABLES = {
        # 基础信息
        "AShareDescription": "股票基本资料",
        
        # 行情数据
        "AShareEODPrices": "日行情",
        "AShareEODDerivativeIndicator": "日行情衍生指标",
        "AShareMoneyFlow": "资金流向",
        
        # 财务数据
        "AShareBalanceSheet": "资产负债表",
        "AShareIncome": "利润表",
        "AShareCashFlow": "现金流量表",
        "AShareFinancialIndicator": "财务指标",
        "AShareTTMHis": "TTM财务数据",
        
        # 行业分类
        "AShareIndustriesCode": "行业代码",
        "AShareSWNIndustriesClass": "申万行业分类",
        
        # 指数数据
        "AIndexDescription": "A股指数基本资料",
        "AIndexHS300FreeWeight": "A股指数月权重（沪深300、上证50等）",
    }
    
    def __init__(self):
        self.conn = None
        self._schema_cache = {}
    
    def connect(self):
        """连接数据库"""
        if not self.conn:
            self.conn = pymysql.connect(**DB_CONFIG)
        return self.conn
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def load_schema(self, table_name: str) -> Optional[Dict]:
        """加载表结构定义"""
        if table_name in self._schema_cache:
            return self._schema_cache[table_name]
        
        schema_file = SCHEMA_DIR / f"{table_name}.json"
        if not schema_file.exists():
            return None
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = json.load(f)
            self._schema_cache[table_name] = schema
            return schema
    
    def search_codes(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索股票代码
        
        Args:
            keyword: 搜索关键词（名称、拼音、代码）
            limit: 返回数量限制
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # 支持多种匹配方式
        sql = """
            SELECT 
                S_INFO_WINDCODE as wind_code,
                S_INFO_CODE as code,
                S_INFO_NAME as name,
                S_INFO_COMPNAME as full_name,
                S_INFO_EXCHMARKET as exchange,
                S_INFO_LISTBOARDNAME as board,
                S_INFO_LISTDATE as list_date,
                S_INFO_PINYIN as pinyin
            FROM asharedescription
            WHERE S_INFO_NAME LIKE %s 
               OR S_INFO_PINYIN LIKE %s
               OR S_INFO_WINDCODE LIKE %s
               OR S_INFO_CODE LIKE %s
            ORDER BY S_INFO_WINDCODE
            LIMIT %s
        """
        
        pattern = f"%{keyword}%"
        cursor.execute(sql, (pattern, pattern, pattern, pattern, limit))
        results = cursor.fetchall()
        cursor.close()
        
        return results
    
    def get_stock_info(self, wind_code: str) -> Optional[Dict]:
        """获取单只股票基本信息"""
        conn = self.connect()
        cursor = conn.cursor()
        
        sql = """
            SELECT * FROM asharedescription
            WHERE S_INFO_WINDCODE = %s
            LIMIT 1
        """
        cursor.execute(sql, (wind_code,))
        result = cursor.fetchone()
        cursor.close()
        
        return result
    
    def query_table(
        self,
        table_name: str,
        wind_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        report_period: Optional[str] = None,
        columns: Optional[List[str]] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        查询指定表的数据
        
        Args:
            table_name: 表名
            wind_code: Wind代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            report_period: 报告期 (YYYYMMDD)
            columns: 指定列名，None则返回所有
            limit: 返回数量限制
        """
        # 安全检查：只允许查询支持的A股表
        # 注意：SUPPORTED_TABLES 中的表名是大写的，但数据库中的表名是小写的
        if table_name.upper() not in [t.upper() for t in self.SUPPORTED_TABLES.keys()]:
            raise ValueError(f"不支持的表: {table_name}. 使用 'list' 命令查看支持的表。")
        
        conn = self.connect()
        cursor = conn.cursor()
        
        # 构建查询
        if columns:
            col_str = ", ".join(columns)
        else:
            col_str = "*"
        
        sql = f"SELECT {col_str} FROM {table_name} WHERE S_INFO_WINDCODE = %s"
        params = [wind_code]
        
        # 添加日期过滤
        if start_date and end_date:
            # 判断表使用哪个日期字段
            if table_name in ["ashareeodprices", "asharemoneyflow", "asharest"]:
                sql += " AND TRADE_DT BETWEEN %s AND %s"
            elif table_name in ["asharebalancesheet", "ashareincome", "asharecashflow", 
                               "asharefinancialindicator", "asharettmhis"]:
                sql += " AND REPORT_PERIOD BETWEEN %s AND %s"
            else:
                sql += " AND OPDATE BETWEEN %s AND %s"
            params.extend([start_date, end_date])
        
        elif report_period:
            if table_name in ["asharebalancesheet", "ashareincome", "asharecashflow",
                           "asharefinancialindicator", "asharettmhis"]:
                sql += " AND REPORT_PERIOD = %s"
            else:
                sql += " AND OPDATE = %s"
            params.append(report_period)
        
        # 添加排序和限制
        if table_name in ["ashareeodprices", "asharemoneyflow"]:
            sql += " ORDER BY TRADE_DT DESC"
        elif table_name in ["asharebalancesheet", "ashareincome", "asharecashflow",
                           "asharefinancialindicator", "asharettmhis"]:
            sql += " ORDER BY REPORT_PERIOD DESC"
        else:
            sql += " ORDER BY OPDATE DESC"
        
        sql += " LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        cursor.close()
        
        return results
    
    def get_eod_prices(
        self,
        wind_code: str,
        start_date: str,
        end_date: str,
        adjust: bool = False
    ) -> List[Dict]:
        """
        获取日行情数据
        
        Args:
            wind_code: Wind代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 是否使用复权价格
        """
        if adjust:
            columns = [
                "TRADE_DT", "S_DQ_ADJPRECLOSE", "S_DQ_ADJOPEN",
                "S_DQ_ADJHIGH", "S_DQ_ADJLOW", "S_DQ_ADJCLOSE",
                "S_DQ_VOLUME", "S_DQ_AMOUNT", "S_DQ_ADJFACTOR"
            ]
        else:
            columns = [
                "TRADE_DT", "S_DQ_PRECLOSE", "S_DQ_OPEN",
                "S_DQ_HIGH", "S_DQ_LOW", "S_DQ_CLOSE",
                "S_DQ_CHANGE", "S_DQ_PCTCHANGE",
                "S_DQ_VOLUME", "S_DQ_AMOUNT"
            ]
        
        return self.query_table(
            "ashareeodprices",
            wind_code,
            start_date=start_date,
            end_date=end_date,
            columns=columns
        )
    
    def get_financial_indicator(
        self,
        wind_code: str,
        report_period: Optional[str] = None,
        key_metrics_only: bool = True
    ) -> List[Dict]:
        """
        获取财务指标
        
        Args:
            wind_code: Wind代码
            report_period: 报告期，None则返回最新
            key_metrics_only: 只返回关键指标
        """
        if key_metrics_only:
            columns = [
                "REPORT_PERIOD", "ANN_DT",
                "S_FA_EPS_BASIC", "S_FA_BPS",
                "S_FA_ROE", "S_FA_ROA", "S_FA_ROIC",
                "S_FA_GROSSPROFITMARGIN", "S_FA_NETPROFITMARGIN",
                "S_FA_DEBTTOASSETS", "S_FA_CURRENT", "S_FA_QUICK",
                "S_FA_YOYNETPROFIT", "S_FA_YOYOR"
            ]
        else:
            columns = None
        
        return self.query_table(
            "asharefinancialindicator",
            wind_code,
            report_period=report_period,
            columns=columns,
            limit=10
        )
    
    def get_money_flow(
        self,
        wind_code: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """
        获取资金流向数据
        
        Args:
            wind_code: Wind代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        """
        columns = [
            "TRADE_DT",
            "BUY_VALUE_EXLARGE_ORDER", "SELL_VALUE_EXLARGE_ORDER",
            "BUY_VALUE_LARGE_ORDER", "SELL_VALUE_LARGE_ORDER",
            "BUY_VALUE_MED_ORDER", "SELL_VALUE_MED_ORDER",
            "BUY_VALUE_SMALL_ORDER", "SELL_VALUE_SMALL_ORDER"
        ]
        
        return self.query_table(
            "asharemoneyflow",
            wind_code,
            start_date=start_date,
            end_date=end_date,
            columns=columns
        )


def format_output(data: List[Dict], format_type: str = "table") -> str:
    """格式化输出"""
    if not data:
        return "无数据"
    
    if format_type == "json":
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)
    
    # 表格格式
    if not data:
        return "无数据"
    
    headers = list(data[0].keys())
    
    # 计算列宽
    col_widths = {}
    for h in headers:
        col_widths[h] = max(len(str(h)), max(len(str(row.get(h, ""))) for row in data))
    
    lines = []
    
    # 表头
    header_line = " | ".join(f"{h:<{col_widths[h]}}" for h in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # 数据行
    for row in data:
        row_line = " | ".join(f"{str(row.get(h, '')):<{col_widths[h]}}" for h in headers)
        lines.append(row_line)
    
    return "\n".join(lines)


def cmd_code(args):
    """查询股票代码"""
    client = AShareDataClient()
    try:
        results = client.search_codes(args.keyword, args.limit)
        
        if not results:
            print(f"未找到匹配 '{args.keyword}' 的股票")
            return
        
        print(f"找到 {len(results)} 条结果:\n")
        
        for r in results:
            exchange_map = {"SSE": "上交所", "SZSE": "深交所", "BSE": "北交所"}
            exchange = exchange_map.get(r.get('exchange'), r.get('exchange'))
            print(f"{r['wind_code']:<12} {r['name']:<10} {exchange:<6} {r.get('board', '-'):<6} {r.get('list_date', '-'):<8}")
            if args.verbose:
                print(f"  全称: {r.get('full_name', '-')}")
                print(f"  拼音: {r.get('pinyin', '-')}")
                print()
    finally:
        client.close()


def cmd_eod(args):
    """获取日行情"""
    client = AShareDataClient()
    try:
        data = client.get_eod_prices(
            args.code,
            args.start,
            args.end,
            adjust=args.adjust
        )
        
        if not data:
            print(f"未找到 {args.code} 在 {args.start} 至 {args.end} 的行情数据")
            return
        
        print(format_output(data, args.format))
    finally:
        client.close()


def cmd_finance(args):
    """获取财务指标"""
    client = AShareDataClient()
    try:
        data = client.get_financial_indicator(
            args.code,
            report_period=args.period,
            key_metrics_only=not args.full
        )
        
        if not data:
            print(f"未找到 {args.code} 的财务指标数据")
            return
        
        print(format_output(data, args.format))
    finally:
        client.close()


def cmd_moneyflow(args):
    """获取资金流向"""
    client = AShareDataClient()
    try:
        data = client.get_money_flow(args.code, args.start, args.end)
        
        if not data:
            print(f"未找到 {args.code} 在 {args.start} 至 {args.end} 的资金流向数据")
            return
        
        print(format_output(data, args.format))
    finally:
        client.close()


def cmd_list(args):
    """列出支持的表"""
    client = AShareDataClient()
    print("支持的A股数据表:\n")
    print(f"{'表名':<35} {'中文名':<20}")
    print("-" * 55)
    for table, name in sorted(client.SUPPORTED_TABLES.items()):
        # 检查是否有对应的 Markdown 数据字典文件
        # 文件名现在是 {表名}.md 格式（表名是混合大小写）
        schema_file = SCHEMA_DIR / f"{table}.md"
        marker = "✓" if schema_file.exists() else " "
        print(f"[{marker}] {table:<32} {name:<20}")
    
    print(f"\n注: [✓] 表示已有数据字典定义")


def cmd_index(args):
    """获取指数成分股信息"""
    client = AShareDataClient()
    
    # 指数代码映射
    index_names = {
        '000300.SH': '沪深300',
        '000016.SH': '上证50',
        '000905.SH': '中证500',
        '000852.SH': '中证1000',
        '399006.SZ': '创业板指',
        '399001.SZ': '深证成指',
        '000001.SH': '上证指数',
        '399005.SZ': '中小板指'
    }
    
    index_name = index_names.get(args.code, args.code)
    
    try:
        # 获取指数成分股
        query = """
        SELECT DISTINCT
            S_CON_WINDCODE as wind_code,
            I_WEIGHT as weight
        FROM aindexhs300freeweight
        WHERE S_INFO_WINDCODE = %s
            AND TRADE_DT = %s
        ORDER BY I_WEIGHT DESC
        """
        
        conn = client.connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (args.code, args.date))
            results = cursor.fetchall()
        
        if not results:
            print(f"未找到 {index_name}({args.code}) 在 {args.date} 的成分股数据")
            return
        
        # 如果有top参数，只取前N名
        if args.top and args.top > 0:
            results = results[:args.top]
            print(f"{index_name}前{args.top}大权重股 ({args.date}):\n")
        else:
            print(f"{index_name}成分股 ({args.date}):\n")
        
        print(f"{'股票代码':<12} {'权重(%)':>12}")
        print("-" * 30)
        
        total_weight = 0.0
        for r in results:
            wind_code = r['wind_code']
            weight = float(r['weight']) if r['weight'] is not None else 0.0
            total_weight += weight
            
            print(f"{wind_code:<12} {weight:>12.4f}")
        
        print("-" * 30)
        print(f"{'总计':<12} {total_weight:>12.4f}")
        
        if not args.top:
            print(f"\n成分股数量: {len(results)} 只")
            print(f"总权重: {total_weight:.4f}% (应接近100%)")
        else:
            print(f"\n前{args.top}大权重股合计权重: {total_weight:.4f}%")
        
    finally:
        client.close()


def cmd_indexinfo(args):
    """查询指数基本信息"""
    client = AShareDataClient()
    
    try:
        conn = client.connect()
        with conn.cursor() as cursor:
            # 构建查询条件
            conditions = []
            params = []
            
            if args.code:
                conditions.append("S_INFO_WINDCODE = %s")
                params.append(args.code)
            
            if args.name:
                conditions.append("S_INFO_NAME LIKE %s")
                params.append(f"%{args.name}%")
            
            if args.publisher:
                conditions.append("S_INFO_PUBLISHER LIKE %s")
                params.append(f"%{args.publisher}%")
            
            if args.type:
                conditions.append("S_INFO_INDEXTYPE = %s")
                params.append(args.type)
            
            if args.market:
                conditions.append("S_INFO_EXCHMARKET = %s")
                params.append(args.market)
            
            # 如果没有指定条件，显示一些常用A股指数
            if not conditions:
                conditions.append("S_INFO_EXCHMARKET IN ('SH', 'SZ') AND S_INFO_INDEXTYPE = '股票类'")
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
            SELECT 
                S_INFO_WINDCODE as wind_code,
                S_INFO_NAME as index_name,
                S_INFO_COMPNAME as short_name,
                S_INFO_PUBLISHER as publisher,
                S_INFO_LISTDATE as list_date,
                S_INFO_INDEX_BASEPER as base_period,
                S_INFO_INDEX_BASEPT as base_point,
                S_INFO_INDEXTYPE as index_type,
                S_INFO_EXCHMARKET as market
            FROM aindexdescription
            WHERE {where_clause}
            ORDER BY S_INFO_LISTDATE DESC, S_INFO_WINDCODE
            LIMIT %s
            """
            
            params.append(args.limit)
            cursor.execute(query, params)
            results = cursor.fetchall()
        
        if not results:
            print("未找到符合条件的指数")
            return
        
        if args.format == "json":
            import json
            import decimal
            import datetime
            
            # 自定义 JSON 编码器，处理 Decimal 和 Date 类型
            class CustomJSONEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, decimal.Decimal):
                        return float(obj)
                    if isinstance(obj, (datetime.date, datetime.datetime)):
                        return obj.isoformat()
                    return super().default(obj)
            
            print(json.dumps(results, ensure_ascii=False, indent=2, cls=CustomJSONEncoder))
            return
        
        # 表格格式输出
        print(f"找到 {len(results)} 个指数:\n")
        print(f"{'指数代码':<15} {'指数名称':<30} {'发布机构':<20} {'类型':<10} {'市场':<5}")
        print("-" * 85)
        
        for row in results:
            wind_code = row['wind_code'] or ''
            index_name = (row['index_name'] or '')[:28]
            publisher = (row['publisher'] or '')[:18]
            index_type = (row['index_type'] or '')[:8]
            market = row['market'] or ''
            
            print(f"{wind_code:<15} {index_name:<30} {publisher:<20} {index_type:<10} {market:<5}")
        
        # 显示更多信息
        if len(results) == 1:
            row = results[0]
            print(f"\n详细信息:")
            print(f"  简称: {row['short_name']}")
            print(f"  发布日期: {row['list_date']}")
            print(f"  基期: {row['base_period']}")
            print(f"  基点: {row['base_point']}")
        
    except Exception as e:
        print(f"查询失败: {e}")
        sys.exit(1)
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(
        description="AShare Data Skill - 中国A股行情数据获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查询股票代码
  python3 ashare_data.py code --keyword 茅台
  
  # 获取日行情
  python3 ashare_data.py eod --code 600519.SH --start 20240101 --end 20240301
  
  # 获取财务指标
  python3 ashare_data.py finance --code 600519.SH --period 20231231
  
  # 获取资金流向
  python3 ashare_data.py moneyflow --code 600519.SH --start 20240101 --end 20240301
  
  # 获取指数成分股
  python3 ashare_data.py index --code 000300.SH --date 20240201
  python3 ashare_data.py index --code 000016.SH --date 20240201 --top 10
  
  # 查询指数基本信息
  python3 ashare_data.py indexinfo --code 000300.SH
  python3 ashare_data.py indexinfo --name 沪深300
  python3 ashare_data.py indexinfo --publisher 中证指数有限公司 --limit 50
  
  # 列出所有支持的表
  python3 ashare_data.py list
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # code 命令
    code_parser = subparsers.add_parser("code", help="查询股票代码")
    code_parser.add_argument("--keyword", "-k", required=True, help="搜索关键词")
    code_parser.add_argument("--limit", "-l", type=int, default=20, help="返回数量限制")
    code_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细信息")
    code_parser.set_defaults(func=cmd_code)
    
    # eod 命令
    eod_parser = subparsers.add_parser("eod", help="获取日行情数据")
    eod_parser.add_argument("--code", "-c", required=True, help="Wind代码，如 600519.SH")
    eod_parser.add_argument("--start", "-s", required=True, help="开始日期 (YYYYMMDD)")
    eod_parser.add_argument("--end", "-e", required=True, help="结束日期 (YYYYMMDD)")
    eod_parser.add_argument("--adjust", "-a", action="store_true", help="使用复权价格")
    eod_parser.add_argument("--format", "-f", choices=["table", "json"], default="table", help="输出格式")
    eod_parser.set_defaults(func=cmd_eod)
    
    # finance 命令
    finance_parser = subparsers.add_parser("finance", help="获取财务指标")
    finance_parser.add_argument("--code", "-c", required=True, help="Wind代码")
    finance_parser.add_argument("--period", "-p", help="报告期 (YYYYMMDD)，默认最新")
    finance_parser.add_argument("--full", action="store_true", help="返回所有指标，不只是关键指标")
    finance_parser.add_argument("--format", "-f", choices=["table", "json"], default="table", help="输出格式")
    finance_parser.set_defaults(func=cmd_finance)
    
    # moneyflow 命令
    mf_parser = subparsers.add_parser("moneyflow", help="获取资金流向")
    mf_parser.add_argument("--code", "-c", required=True, help="Wind代码")
    mf_parser.add_argument("--start", "-s", required=True, help="开始日期 (YYYYMMDD)")
    mf_parser.add_argument("--end", "-e", required=True, help="结束日期 (YYYYMMDD)")
    mf_parser.add_argument("--format", "-f", choices=["table", "json"], default="table", help="输出格式")
    mf_parser.set_defaults(func=cmd_moneyflow)
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出支持的表")
    list_parser.set_defaults(func=cmd_list)
    
    # index 命令
    index_parser = subparsers.add_parser("index", help="获取指数成分股信息")
    index_parser.add_argument("--code", "-c", required=True, help="指数Wind代码，如 000300.SH（沪深300）")
    index_parser.add_argument("--date", "-d", required=True, help="查询日期 (YYYYMMDD)")
    index_parser.add_argument("--top", "-t", type=int, help="返回前N名成分股（默认返回全部）")
    index_parser.set_defaults(func=cmd_index)
    
    # indexinfo 命令 - 查询指数基本信息
    indexinfo_parser = subparsers.add_parser("indexinfo", help="查询指数基本信息")
    indexinfo_parser.add_argument("--code", "-c", help="指数Wind代码，如 000300.SH")
    indexinfo_parser.add_argument("--name", "-n", help="指数名称关键词（模糊匹配）")
    indexinfo_parser.add_argument("--publisher", "-p", help="发布机构")
    indexinfo_parser.add_argument("--type", "-t", help="指数类型，如股票类、债券类等")
    indexinfo_parser.add_argument("--market", "-m", help="交易市场，如SH、SZ")
    indexinfo_parser.add_argument("--limit", "-l", type=int, default=20, help="返回数量限制")
    indexinfo_parser.add_argument("--format", "-f", choices=["table", "json"], default="table", help="输出格式")
    indexinfo_parser.set_defaults(func=cmd_indexinfo)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
