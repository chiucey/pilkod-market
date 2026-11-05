#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股涨停股分析和报告生成脚本
基于获取的市场数据生成复盘报告
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


# 板块分类映射（可根据实际数据调整）
SECTOR_KEYWORDS = {
    '半导体': ['半导体', '芯片', '集成电路', '晶圆', '封测', '光刻', '蚀刻', '硅片', 'PCB'],
    '锂电': ['锂电', '锂电池', '锂', '正极', '负极', '电解液', '隔膜', '储能', '新能源车'],
    '算力': ['算力', 'AI', '人工智能', '服务器', '云计算', '数据中心', 'GPU', 'CPU'],
    '机器人': ['机器人', '人形机器人', '工业机器人', '自动化', '电机', '传感器'],
    '光通信': ['光通信', '光模块', '光纤', '光缆', '光器件'],
    '商业航天': ['商业航天', '卫星', '火箭', '航天', '低轨'],
    '汽车': ['汽车', '整车', '零部件', '新能源车'],
    '消费': ['消费', '食品', '饮料', '家电', '纺织', '服装'],
    '医药': ['医药', '医疗', '生物', '中药', '器械'],
    '有色': ['有色', '铜', '铝', '锂', '稀土', '钨', '钼'],
    '化工': ['化工', '化学', '新材料'],
    '房地产': ['房地产', '地产', '建筑', '装修'],
    '金融': ['金融', '证券', '银行', '保险', '多元金融'],
    '公告涨停': []  # 需要通过其他方式判断
}


def load_data(filepath: str = 'a_stock_data.json') -> Dict[str, Any]:
    """加载市场数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"数据文件 {filepath} 不存在，请先运行 fetch_data.py")
        return {}


def analyze_limit_up_stocks(stocks: List[Dict]) -> Dict[str, Any]:
    """分析涨停股"""
    if not stocks or (len(stocks) == 1 and 'error' in stocks[0]):
        return {'error': '无数据'}

    # 按连板高度分组
    by_consecutive = defaultdict(list)
    for stock in stocks:
        days = stock.get('consecutive_days', 1)
        by_consecutive[days].append(stock)

    # 获取最高板
    max_consecutive = max(by_consecutive.keys()) if by_consecutive else 0

    # 获取首板
    first_board = by_consecutive.get(1, [])

    # 分析板块分布
    sector_distribution = defaultdict(list)
    announcement_stocks = []  # 公告涨停单独分类

    for stock in stocks:
        name = stock.get('name', '')
        reason = stock.get('reason', '')

        # 判断是否为公告涨停
        if '公告' in str(reason) or '业绩' in str(reason) or '收购' in str(reason):
            announcement_stocks.append(stock)
            sector_distribution['公告涨停'].append(stock)
            continue

        # 按关键词分类到板块
        classified = False
        for sector, keywords in SECTOR_KEYWORDS.items():
            if sector == '公告涨停':
                continue
            for keyword in keywords:
                if keyword in name:
                    sector_distribution[sector].append(stock)
                    classified = True
                    break
            if classified:
                break

        if not classified:
            sector_distribution['其他'].append(stock)

    return {
        'total': len(stocks),
        'by_consecutive': dict(by_consecutive),
        'max_consecutive': max_consecutive,
        'first_board': first_board,
        'sector_distribution': dict(sector_distribution),
        'announcement_stocks': announcement_stocks,
        'all_stocks': stocks
    }


def analyze_market_sentiment(overview: Dict) -> str:
    """分析市场情绪并生成寄语"""
    if 'error' in overview:
        return "数据获取失败"

    limit_up = overview.get('limit_up', 0)
    limit_down = overview.get('limit_down', 0)
    total_volume = overview.get('total_volume', 0)

    # 情绪判断
    if limit_up >= 80 and limit_up / max(limit_down, 1) > 5:
        sentiment = "市场情绪高涨，赚钱效应极好"
    elif limit_up >= 50:
        sentiment = "市场情绪较好，热点活跃"
    elif limit_up >= 30:
        sentiment = "市场情绪一般，热点分化"
    elif limit_up >= 10:
        sentiment = "市场情绪低迷，热点匮乏"
    else:
        sentiment = "市场情绪极差，亏钱效应明显"

    # 量能判断
    if total_volume > 15000:
        volume_comment = "量能充沛"
    elif total_volume > 10000:
        volume_comment = "量能适中"
    else:
        volume_comment = "量能萎缩"

    return f"{sentiment}，{volume_comment}"


def generate_matrix_report(analysis: Dict) -> str:
    """生成连板晋级矩阵图"""
    sector_dist = analysis.get('sector_distribution', {})
    by_consecutive = analysis.get('by_consecutive', {})
    max_consecutive = analysis.get('max_consecutive', 0)

    if 'error' in sector_dist:
        return "数据加载失败"

    # 获取所有板块名称
    sectors = list(sector_dist.keys())
    if '公告涨停' in sectors:
        sectors.remove('公告涨停')
        sectors.insert(0, '公告涨停')

    # 获取所有连板高度
    heights = sorted(by_consecutive.keys(), reverse=True)

    # 生成矩阵报告
    report = []
    report.append("### 连板晋级回顾推演图\n")
    report.append(f"| 连板高度 | {' | '.join(sectors[:6])} |")
    report.append(f"|----------|{'|'.join(['---' for _ in sectors[:6]])}|")

    for height in heights[:4]:  # 最多显示4个高度
        height_label = f"{height}连板" if height > 1 else "首板"
        row = [height_label]

        for sector in sectors[:6]:
            sector_stocks = sector_dist.get(sector, [])
            height_stocks = [s for s in sector_stocks if s.get('consecutive_days', 1) == height]
            stock_names = '、'.join([s['name'] for s in height_stocks[:2]])
            row.append(stock_names if stock_names else '-')

        report.append('| ' + ' | '.join(row) + ' |')

    return '\n'.join(report)


def generate_sector_report(sector_dist: Dict) -> str:
    """生成板块热点分析报告"""
    report = ["## 四、热点板块分析\n"]

    # 按涨停家数排序
    sorted_sectors = sorted(
        sector_dist.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for idx, (sector, stocks) in enumerate(sorted_sectors[:5], 1):
        if len(stocks) < 2:  # 至少2家涨停才分析
            continue

        report.append(f"### 板块{idx}：{sector}（{len(stocks)}家涨停）")

        # 连板梯队
        by_height = defaultdict(list)
        for s in stocks:
            by_height[s.get('consecutive_days', 1)].append(s)

        report.append("\n**连板梯队**：")
        for height in sorted(by_height.keys(), reverse=True):
            height_stocks = by_height[height]
            label = f"{height}连板" if height > 1 else "首板"
            names = '、'.join([s['name'] for s in height_stocks])
            report.append(f"- {label}：{names}")

        # 驱动逻辑（简化版，需要结合实际新闻）
        report.append("\n**驱动逻辑**：")
        report.append("1. [基于市场消息自动提取]")

        report.append("")

    return '\n'.join(report)


def generate_full_report(data: Dict) -> str:
    """生成完整复盘报告"""
    overview = data.get('market_overview', {})
    limit_up_stocks = data.get('limit_up_stocks', [])
    index_data = data.get('index_data', {})
    new_high = data.get('new_high_stocks', [])
    institution = data.get('institution_trades', {})
    hot_money = data.get('hot_money', {})

    report = []

    # 标题
    trade_date = overview.get('trade_date', datetime.now().strftime("%Y%m%d"))
    report.append(f"# A股每日复盘报告 - {trade_date}")
    report.append("")

    # 一、今日复盘要点
    report.append("## 一、今日复盘要点\n")

    # 情绪寄语
    sentiment = analyze_market_sentiment(overview)
    report.append(f"**今日寄语**：{sentiment}\n")

    # 涨跌停统计
    report.append("### 情绪概览")
    report.append(f"- 实际涨停：{overview.get('limit_up', 0)}家（过滤ST）")
    report.append(f"- 实际跌停：{overview.get('limit_down', 0)}家")
    report.append(f"- 上涨：{overview.get('up', 0)}家 | 下跌：{overview.get('down', 0)}家 | 平盘：{overview.get('flat', 0)}家")
    report.append("")

    # 涨跌幅分布
    report.append("### 涨跌幅分布")
    report.append("| 区间 | 家数 |")
    report.append("|------|------|")
    ranges = overview.get('range_distribution', {})
    for range_name in ['>7%', '5-7%', '3-5%', '2-3%', '0-2%', '-2-0%', '-3--2%', '-5--3%', '-7--5%', '<-7%']:
        report.append(f"| {range_name} | {ranges.get(range_name, 0)} |")
    report.append("")

    # 市场量能
    report.append("### 市场量能")
    report.append(f"- 沪市成交：{overview.get('shanghai_volume', 0)}亿")
    report.append(f"- 深市成交：{overview.get('shenzhen_volume', 0)}亿")
    report.append(f"- 合计：{overview.get('total_volume', 0)}亿")
    report.append("")

    # 主要指数
    if index_data and 'error' not in index_data:
        report.append("### 主要指数")
        for name, info in index_data.items():
            change = info.get('change_pct', 0)
            sign = '+' if change >= 0 else ''
            report.append(f"- {name}：{info.get('close', 0)}（{sign}{change}%）")
        report.append("")

    # 二、连板晋级
    report.append("## 二、连板晋级回顾推演图\n")
    analysis = analyze_limit_up_stocks(limit_up_stocks)

    if 'error' not in analysis and analysis.get('total', 0) > 0:
        matrix = generate_matrix_report(analysis)
        report.append(matrix)
        report.append("")
        report.append(f"**最高板**：{analysis.get('max_consecutive', 0)}连板")
        report.append("")

    # 三、涨停事件
    report.append("## 三、涨停事件\n")

    if 'error' not in analysis:
        announcement = analysis.get('announcement_stocks', [])
        if announcement:
            report.append(f"### 公告涨停（{len(announcement)}家）\n")
            report.append("按利好类型分类：\n")
            for stock in announcement[:10]:
                report.append(f"- **{stock.get('name', '')}**：{stock.get('reason', '个股利好')}（{stock.get('consecutive_days', 1)}板）")
            report.append("")
        else:
            report.append("今日暂无公告涨停事件\n")

    # 四、热点板块
    if 'error' not in analysis:
        sector_report = generate_sector_report(analysis.get('sector_distribution', {}))
        report.append(sector_report)
        report.append("")

    # 五、股价新高
    report.append("## 五、股价新高统计\n")
    if new_high and 'error' not in new_high[0]:
        report.append(f"今日收盘价创新高：{len(new_high)}家\n")
        report.append("")
        report.append("### 创新高个股明细")
        report.append("| 序号 | 代码 | 名称 | 现价 | 涨跌幅 |")
        report.append("|------|------|------|------|--------|")
        for idx, stock in enumerate(new_high[:10], 1):
            report.append(f"| {idx} | {stock.get('code', '')} | {stock.get('name', '')} | {stock.get('close', 0)} | {stock.get('change_pct', 0)}% |")
        report.append("")
    else:
        report.append("暂无创新高数据\n")

    # 六、机构席位
    report.append("## 六、机构席位动向\n")
    daily_inst = institution.get('daily', [])
    if daily_inst and 'error' not in daily_inst[0]:
        report.append("### 当日净买入TOP10")
        report.append("")
        report.append("| 序号 | 代码 | 名称 | 收盘价 | 涨跌幅 | 买方机构 | 净买入(万) |")
        report.append("|------|------|------|--------|--------|----------|------------|")
        for idx, stock in enumerate(daily_inst[:10], 1):
            report.append(f"| {idx} | {stock.get('code', '')} | {stock.get('name', '')} | {stock.get('close', 0)} | {stock.get('change_pct', 0)}% | {stock.get('buy_inst', 0)} | {stock.get('net_amount', 0)} |")

        total_net = sum(s.get('net_amount', 0) for s in daily_inst)
        report.append("")
        report.append(f"**当日机构总计**：净买入 {total_net:.2f}亿\n")
    else:
        report.append("暂无机构席位数据\n")

    # 七、游资席位
    report.append("## 七、游资席位动向\n")
    buy_trades = hot_money.get('buy', [])
    sell_trades = hot_money.get('sell', [])

    if buy_trades and 'error' not in buy_trades[0]:
        report.append("### 游资净买入TOP10")
        report.append("")
        report.append("| 席位名称 | 标的1 | 标的2 | 标的3 |")
        report.append("|----------|-------|-------|-------|")
        for trade in buy_trades[:5]:
            report.append(f"| {trade.get('seat', '')} | {trade.get('stock', '')}:{trade.get('amount', 0)}亿 | - | - |")
        report.append("")
    else:
        report.append("暂无游资席位数据\n")

    if sell_trades and 'error' not in sell_trades[0]:
        report.append("### 游资净卖出TOP10")
        report.append("")
        for trade in sell_trades[:5]:
            report.append(f"- {trade.get('seat', '')}：卖出 {trade.get('stock', '')} {trade.get('amount', 0)}亿")
        report.append("")

    # 结尾
    report.append("")
    report.append("---")
    report.append(f"*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return '\n'.join(report)


def save_report(report: str, filepath: str = 'daily_report.md'):
    """保存报告到Markdown文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"报告已保存到: {filepath}")


if __name__ == '__main__':
    # 加载数据
    data = load_data()

    if data:
        # 生成报告
        report = generate_full_report(data)

        # 保存报告
        save_report(report)

        # 打印报告
        print("\n" + "="*50)
        print(report)
    else:
        print("无数据可分析")
