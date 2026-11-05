#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股/港股实时行情查询核心模块
基于 AkShare 接口，适配 OpenClaw 框架
"""

import re
import time
import akshare as ak
import pandas as pd

# ---------- 缓存配置 ----------
CACHE_TTL = 30  # 秒
_cache = {}     # {(func_name, args_key): (timestamp, result)}

def cached(ttl=CACHE_TTL):
    """
    装饰器：实现带 TTL 的缓存
    防止频繁请求API，提升响应速度
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in _cache:
                ts, result = _cache[key]
                if now - ts < ttl:
                    return result
            result = func(*args, **kwargs)
            _cache[key] = (now, result)
            return result
        return wrapper
    return decorator

# ---------- 重试机制 ----------
def with_retry(func, retries=3, delay=1):
    """
    简单重试函数
    处理网络异常，提高稳定性
    """
    for i in range(retries):
        try:
            return func()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(delay)
    return None

# ---------- 数据获取（带缓存） ----------
@cached(ttl=CACHE_TTL)
def get_a_spot_data():
    """获取A股全量实时数据（缓存）"""
    return ak.stock_zh_a_spot_em()

@cached(ttl=CACHE_TTL)
def get_hk_spot_data():
    """获取港股全量实时数据（缓存）"""
    return ak.stock_hk_spot()

# ---------- 新闻获取 ----------
def get_a_news(symbol: str):
    """
    获取个股新闻（东方财富）
    symbol: 6位数字代码，如 '000001'
    """
    try:
        df = with_retry(lambda: ak.stock_news_em(symbol=symbol))
        if df is None or df.empty:
            return "未找到相关新闻"
        # 取前5条
        news = df.head(5)[['标题', '发布时间', '来源']]
        lines = []
        for _, row in news.iterrows():
            lines.append(f"【{row['发布时间']}】{row['标题']} ({row['来源']})")
        return "\n".join(lines) if lines else "暂无新闻"
    except Exception as e:
        return f"新闻查询失败：{str(e)}"

# ---------- 行情查询 ----------
def _get_a_stock_quote(code: str) -> str:
    """获取A股行情"""
    df = get_a_spot_data()
    df['代码'] = df['代码'].astype(str)
    # 支持代码或名称匹配
    match = df[(df['代码'] == code) | (df['名称'].str.contains(code, na=False))]
    if match.empty:
        return f"未找到 A股 代码或名称 '{code}'"

    row = match.iloc[0]
    name = row['名称']
    price = row['最新价']
    change = row['涨跌额']
    change_pct = row['涨跌幅']
    volume = row['成交量']
    turnover = row['成交额']
    return (f"{name}({code}) 实时行情：\n"
            f"最新价：{price}\n"
            f"涨跌额：{change}\n"
            f"涨跌幅：{change_pct}%\n"
            f"成交量：{volume} 手\n"
            f"成交额：{turnover} 元")

def _get_hk_stock_quote(code: str) -> str:
    """获取港股行情"""
    df = get_hk_spot_data()
    df['代码'] = df['代码'].astype(str)
    # 港股代码可能含前缀，支持纯数字匹配
    if code.isdigit():
        match = df[df['代码'].str.endswith(code)]
    else:
        match = df[df['代码'] == code]
    if match.empty:
        return f"未找到港股代码 '{code}'"

    row = match.iloc[0]
    name = row['名称']
    price = row['现价']
    change = row['涨跌']
    change_pct = row['涨跌幅']
    volume = row['成交量']
    turnover = row['成交额']
    return (f"{name}({code}) 实时行情：\n"
            f"现价：{price}\n"
            f"涨跌：{change}\n"
            f"涨跌幅：{change_pct}%\n"
            f"成交量：{volume} 股\n"
            f"成交额：{turnover} 元")

# ---------- 主入口 ----------
def run(query: str) -> str:
    """
    入口函数，接收 OpenClaw 传入的自然语言查询。
    支持：
      - 行情查询：股票行情 000001、港股 00700、股价 贵州茅台
      - 新闻查询：股票新闻 000001、新闻 平安银行
    """
    query = query.strip()
    if not query:
        return "请输入股票代码或名称，例如：股票行情 000001"

    # 判断是否查询新闻
    is_news = re.search(r'新闻|公告', query, re.I) is not None
    # 判断是否港股
    is_hk = re.search(r'港股|hk|HK', query, re.I) is not None

    # 提取股票代码或名称
    # 优先匹配纯数字（6位A股或任意港股数字）
    code_match = re.search(r'\b\d{5,6}\b', query)
    if not code_match:
        # 尝试匹配汉字名称（中文股票名称）
        name_match = re.search(r'[\u4e00-\u9fa5]{2,10}', query)
        if not name_match:
            return "未能识别股票代码或名称，请提供如 000001 或 平安银行"
        code_or_name = name_match.group()
    else:
        code_or_name = code_match.group()

    # 如果是新闻查询
    if is_news:
        if is_hk:
            return "港股新闻暂未支持，请使用A股新闻（如：新闻 00700 暂不支持）"
        # 对于A股，如果是名称，需要先转换为代码
        if not code_or_name.isdigit():
            # 通过全量数据查找名称对应的代码
            try:
                df = get_a_spot_data()
                df['名称'] = df['名称'].astype(str)
                match = df[df['名称'].str.contains(code_or_name, na=False)]
                if match.empty:
                    return f"未找到名称为 '{code_or_name}' 的股票"
                symbol = match.iloc[0]['代码']
            except Exception as e:
                return f"转换股票代码失败：{str(e)}"
        else:
            symbol = code_or_name
        # 确保是6位数字
        if len(symbol) != 6:
            return f"无效的A股代码：{symbol}"
        return get_a_news(symbol)

    # 行情查询
    if is_hk:
        return _get_hk_stock_quote(code_or_name)
    else:
        # 如果是名称，直接传入名称查询
        return _get_a_stock_quote(code_or_name)


# ---------- OpenClaw 适配 ----------
if __name__ == "__main__":
    # 测试用例
    test_queries = [
        "股票行情 000001",
        "股价 贵州茅台",
        "港股 00700",
        "新闻 平安银行"
    ]

    print("=" * 50)
    print("股票查询 Skill 测试")
    print("=" * 50)

    for q in test_queries:
        print(f"\n>>> {q}")
        print(run(q))
        print("-" * 50)
