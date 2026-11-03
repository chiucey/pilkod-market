#!/usr/bin/env python3
"""
A股尾盘短线助手 - 每日14:55 尾盘低吸候选筛选
策略：尾盘低吸，次日冲高卖出（隔夜溢价逻辑）
"""

import sys
import json
import os
from datetime import datetime

HISTORY_DIR = "/workspace/skills/a-stock-closing-screener/history"
os.makedirs(HISTORY_DIR, exist_ok=True)


def clean_num(s):
    if isinstance(s, (int, float)):
        return float(s)
    if s is None:
        return None
    s = str(s).replace('%', '').replace(',', '').strip()
    try:
        return float(s)
    except:
        return None


def save_daily_report(stocks, data):
    """保存当日推荐记录，用于收盘后胜率复盘"""
    today = datetime.now().strftime('%Y-%m-%d')
    record = {
        "date": today,
        "strategy": "closing",  # 尾盘
        "market_style": _get_style(data),
        "position_advice": _get_position(data),
        "stocks": [
            {
                "name": s['name'],
                "code": s['code'],
                "tag": s['tag'],
                "conclusion": s.get('conclusion', '未知'),
                "fund_score": s.get('fund_score', 0),
                "momentum": s.get('momentum', '未知'),
            }
            for s in stocks
        ]
    }
    path = os.path.join(HISTORY_DIR, f"{today}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(f"[历史记录已保存] {path}", flush=True)


def _get_style(data):
    up = data.get('up_count', 0) or 0
    down = data.get('down_count', 0) or 0
    limit_up = data.get('limit_up', 0)
    if up + down == 0:
        return '数据获取中'
    ratio = up / (up + down)
    if limit_up >= 30 and ratio > 0.6:
        return '强势'
    elif ratio > 0.55:
        return '偏强'
    elif ratio >= 0.45:
        return '震荡'
    return '偏弱'


def _get_position(data):
    up = data.get('up_count', 0) or 0
    down = data.get('down_count', 0) or 0
    limit_up = data.get('limit_up', 0)
    if up + down == 0:
        return '控仓/观望'
    ratio = up / (up + down)
    if limit_up >= 30 and ratio > 0.6:
        return '半仓'
    elif ratio > 0.55:
        return '半仓/控仓'
    elif ratio >= 0.45:
        return '轻仓'
    return '尽量不买'


def get_data():
    """获取今日市场数据"""
    import akshare as ak

    results = {}

    # 1. 市场情绪
    try:
        market_extra = ak.stock的情绪指标market_extra()
        up_count = 0
        down_count = 0
        limit_up = 0
        limit_down = 0
        for _, row in market_extra.iterrows():
            change = clean_num(row.get('涨跌幅', 0))
            if change is None:
                continue
            if change > 0:
                up_count += 1
            elif change < 0:
                down_count += 1
            if change >= 9.5:
                limit_up += 1
            elif change <= -9.5:
                limit_down += 1
        results['up_count'] = up_count
        results['down_count'] = down_count
        results['limit_up'] = limit_up
        results['limit_down'] = limit_down
    except Exception:
        results['up_count'] = None
        results['down_count'] = None
        results['limit_up'] = 0
        results['limit_down'] = 0

    # 2. 昨日涨停（尾盘低吸核心）
    try:
        yesterday = datetime.now().strftime('%Y%m%d')
        zt_df = ak.stock_zt_pool_previous(date=yesterday)
        if zt_df is not None and len(zt_df) > 0:
            zt_df.columns = [str(c).strip() for c in zt_df.columns]
            fd_cols = [c for c in zt_df.columns if '封单' in c]
            hs_cols = [c for c in zt_df.columns if '换手' in c]
            amt_cols = [c for c in zt_df.columns if '成交' in c and '额' in c]
            chg_cols = [c for c in zt_df.columns if '涨跌幅' in c]
            zt_df['_score'] = 0.0
            if fd_cols:
                zt_df['_score'] += zt_df[fd_cols[0]].apply(lambda x: clean_num(x) or 0) / 1e9
            if hs_cols:
                zt_df['_score'] += zt_df[hs_cols[0]].apply(lambda x: clean_num(x) or 0)
            if amt_cols:
                zt_df['_score'] += zt_df[amt_cols[0]].apply(lambda x: clean_num(x) or 0) / 1e8
            if chg_cols:
                zt_df['_score'] += zt_df[chg_cols[0]].apply(lambda x: abs(clean_num(x) or 0)) * 0.5
            zt_df = zt_df.sort_values('_score', ascending=False)
            results['yesterday_zt'] = zt_df.head(20).to_dict('records')
            results['_cols'] = {
                'fd': fd_cols[0] if fd_cols else '',
                'hs': hs_cols[0] if hs_cols else '',
                'amt': amt_cols[0] if amt_cols else '',
                'chg': chg_cols[0] if chg_cols else ''
            }
        else:
            results['yesterday_zt'] = []
            results['_cols'] = {}
    except Exception:
        results['yesterday_zt'] = []
        results['_cols'] = {}

    # 3. 超跌股（尾盘反弹）
    try:
        df = ak.stock_zt_pool_strong(date=datetime.now().strftime('%Y%m%d'))
        if df is not None and len(df) > 0:
            df.columns = [str(c).strip() for c in df.columns]
            chg_cols = [c for c in df.columns if '涨跌幅' in c]
            hs_cols = [c for c in df.columns if '换手' in c]
            amt_cols = [c for c in df.columns if '成交' in c and '额' in c]
            df['_score'] = 0.0
            if chg_cols:
                df['_score'] += df[chg_cols[0]].apply(lambda x: abs(clean_num(x) or 0))
            if hs_cols:
                df['_score'] += df[hs_cols[0]].apply(lambda x: clean_num(x) or 0) * 0.5
            if amt_cols:
                df['_score'] += df[amt_cols[0]].apply(lambda x: clean_num(x) or 0) / 1e8
            if chg_cols:
                df = df[df[chg_cols[0]].apply(lambda x: clean_num(x) or 0) < -3.0]
            df = df.sort_values('_score', ascending=False)
            results['oversold'] = df.head(15).to_dict('records')
        else:
            results['oversold'] = []
    except Exception:
        results['oversold'] = []

    # 4. 板块资金
    try:
        sector_flow = ak.stock_sector_fund_flow_rank(indicator="今日")
        sector_flow.columns = [str(c).strip() for c in sector_flow.columns]
        main_cols = [c for c in sector_flow.columns if '主力' in c and '净' in c]
        if main_cols:
            sector_flow = sector_flow.sort_values(main_cols[0], ascending=False)
            results['top_sectors'] = sector_flow.head(10).to_dict('records')
            results['main_col'] = main_cols[0]
        else:
            results['top_sectors'] = []
            results['main_col'] = ''
    except Exception:
        results['top_sectors'] = []
        results['main_col'] = ''

    return results


def screen_stocks(data):
    """尾盘低吸量化精选"""
    candidates = []
    seen = set()
    cols = data.get('_cols', {})
    main_col = data.get('main_col', '')

    # 策略A：昨日涨停回调低吸
    for item in data.get('yesterday_zt', []):
        name = str(item.get('名称', ''))
        code = str(item.get('代码', ''))
        if not name or name in seen:
            continue
        score = float(item.get('_score', 0))
        fd = clean_num(item.get(cols.get('fd', ''), 0)) if cols.get('fd') else 0
        hs = clean_num(item.get(cols.get('hs', ''), 0)) if cols.get('hs') else 0
        amt = clean_num(item.get(cols.get('amt', ''), 0)) if cols.get('amt') else 0
        chg = clean_num(item.get(cols.get('chg', ''), 0)) if cols.get('chg') else 0
        if amt < 30000000:
            continue
        candidates.append({
            'name': name, 'code': code,
            'logic': f'昨日涨停（封单{fd/1e8:.1f}亿，换手{hs:.2f}%，成交额{amt/1e8:.1f}亿），尾盘回调至-3%至-5%区间为低吸买点，隔夜溢价概率高',
            'risk': '尾盘若不回调则无低吸机会，需14:50前确认价格位置',
            'score': score * 1.1, 'tag': '策略A-昨日涨停低吸',
            'fund_score': min(5, 3 + fd / 2e9 + hs / 5),
            'momentum': '高' if fd > 5e8 else '中'
        })
        seen.add(name)

    # 策略B：超跌反弹
    for item in data.get('oversold', []):
        name = str(item.get('名称', ''))
        code = str(item.get('代码', ''))
        if not name or name in seen:
            continue
        score = float(item.get('_score', 0))
        chg_cols = [v for k, v in item.items() if '涨跌幅' in str(k)]
        hs_cols = [v for k, v in item.items() if '换手' in str(k)]
        amt_cols = [v for k, v in item.items() if '成交' in str(k) and '额' in str(k)]
        chg = clean_num(chg_cols[0]) if chg_cols else 0
        hs = clean_num(hs_cols[0]) if hs_cols else 0
        amt = clean_num(amt_cols[0]) if amt_cols else 0
        if amt < 30000000:
            continue
        candidates.append({
            'name': name, 'code': code,
            'logic': f'今日跌幅{chg:.1f}%（超跌），换手{hs:.2f}%，成交额{amt/1e8:.2f}亿，尾盘若企稳有反弹预期，赔率好',
            'risk': '超跌股可能继续跌，止损必须严格执行（-3%以内）',
            'score': score * 1.0, 'tag': '策略B-超跌反弹',
            'fund_score': min(5, abs(chg) / 2 + hs / 3),
            'momentum': '中'
        })
        seen.add(name)

    # 策略C：板块龙头
    for item in data.get('top_sectors', []):
        sector = str(item.get('名称', '')) or str(item.get('板块', ''))
        main_flow = 0
        for k, v in item.items():
            if main_col and main_col in str(k):
                main_flow = clean_num(v) or 0
                break
        if main_flow < 1e8:
            continue
        try:
            import akshare as ak
            sector_stocks = ak.stock_sector_detail(symbol=sector)
            if sector_stocks is None or len(sector_stocks) == 0:
                continue
            sector_stocks.columns = [str(c).strip() for c in sector_stocks.columns]
            amt_cols = [c for c in sector_stocks.columns if '成交' in c and '额' in c]
            chg_cols = [c for c in sector_stocks.columns if '涨跌幅' in c]
            sector_stocks['_score'] = 0.0
            if amt_cols:
                sector_stocks['_score'] += sector_stocks[amt_cols[0]].apply(lambda x: clean_num(x) or 0) / 1e8
            if chg_cols:
                sector_stocks['_score'] += sector_stocks[chg_cols[0]].apply(lambda x: abs(clean_num(x) or 0))
            sector_stocks = sector_stocks.sort_values('_score', ascending=False)
            for _, row in sector_stocks.head(3).iterrows():
                name = str(row.get('名称', ''))
                if name in seen or not name:
                    continue
                code = str(row.get('代码', '')) if '代码' in sector_stocks.columns else ''
                chg = clean_num(chg_cols[0]) if chg_cols else 0
                amt = clean_num(amt_cols[0]) if amt_cols else 0
                score = float(row.get('_score', 0))
                if chg > 7:
                    continue
                candidates.append({
                    'name': name, 'code': code,
                    'logic': f'板块【{sector}】主力净流入{main_flow/1e8:.1f}亿；{name}涨幅{chg:.1f}%，成交额{amt/1e8:.2f}亿，尾盘回调均线低吸',
                    'risk': '板块轮动快，尾盘若走弱则低吸逻辑消失',
                    'score': score * 0.9 + main_flow / 4e9, 'tag': f'策略C-{sector}',
                    'fund_score': min(5, 3 + main_flow / 3e9 + amt / 1e9),
                    'momentum': '中'
                })
                seen.add(name)
        except Exception:
            pass

    seen_names = set()
    unique = []
    for c in sorted(candidates, key=lambda x: x['score'], reverse=True):
        name = c['name']
        if name not in seen_names:
            seen_names.add(name)
            unique.append(c)

    return unique[:6]


def score_single(stock):
    fund = stock.get('fund_score', 0)
    momentum = stock.get('momentum', '中')
    fund_label = '强' if fund >= 4 else '一般' if fund >= 3 else '弱'
    momentum_label = momentum
    tomorrow = '高' if momentum == '高' or fund >= 4 else '中' if momentum == '中' else '低'
    return fund_label, momentum_label, tomorrow


def format_report(stocks, data):
    """格式化尾盘报告"""
    up = data.get('up_count', '?')
    down = data.get('down_count', '?')
    limit_up = data.get('limit_up', 0)
    style = _get_style(data)
    position = _get_position(data)

    lines = [
        f"📊 LU，尾盘低吸精选（{datetime.now().strftime('%Y-%m-%d')}）",
        f"⏰ 报告时间：14:55（尾盘前5分钟）",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"🌡️ 今日盘面：涨 {up} 家 / 跌 {down} 家 | 涨停 {limit_up} 家",
        f"🎯 整体风格：**{style}**",
        f"━━━━━━━━━━━━━━━━━━━━",
        f"",
    ]

    emoji_map = {'策略A': '🔥', '策略B': '⚡', '策略C': '📈'}

    for i, s in enumerate(stocks, 1):
        tag = s['tag']
        icon = next((v for k, v in emoji_map.items() if k in tag), '📊')
        fund_label, momentum_label, tomorrow = score_single(s)

        if '低吸买点' in s['logic']:
            buy_reason = '昨日强势，尾盘回调提供低吸机会，赔率高'
        elif '反弹预期' in s['logic']:
            buy_reason = '超跌股，尾盘若企稳可博反弹，赔率好'
        else:
            buy_reason = '板块资金认可，尾盘回调均线低吸，胜率较稳定'

        if fund_label == '强' and tomorrow == '高':
            conclusion = '✅ 建议买入'
        elif fund_label == '强':
            conclusion = '🟡 可试探买入（控仓）'
        elif tomorrow == '高':
            conclusion = '🟡 轻仓考虑'
        else:
            conclusion = '⏸ 观望'

        lines.append(f"{i}. {s['name']}（{s['code']}）{icon}")
        lines.append(f"   资金与情绪：**{fund_label}** | 明日冲高概率：**{tomorrow}**")
        lines.append(f"   买入理由：{buy_reason}")
        lines.append(f"   风险点：{s['risk']}")
        lines.append(f"   结论：**{conclusion}**")
        lines.append("")

    lines.append(f"━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📋 今日整体尾盘适合：**{position}**")
    lines.append(f"⏰ 操作窗口：14:55 - 15:00（尾盘集合竞价）")
    lines.append(f"⚠️ 建议买入标的严格设止损位（-3%以内）")
    lines.append("")
    lines.append("⚠️ 仅逻辑分析，不构成投资建议，股市有风险，入市需谨慎")

    return "\n".join(lines)


def main():
    print("📊 开始今日尾盘低吸精选...", flush=True)
    try:
        data = get_data()
        stocks = screen_stocks(data)
        # 附加结论信息用于保存
        for s in stocks:
            fund_label, momentum_label, tomorrow = score_single(s)
            s['fund_score'] = {'强': 4, '一般': 3, '弱': 2}.get(fund_label, 2)
            s['momentum'] = momentum_label
            if fund_label == '强' and tomorrow == '高':
                s['conclusion'] = '✅ 建议买入'
            elif fund_label == '强':
                s['conclusion'] = '🟡 可试探买入（控仓）'
            elif tomorrow == '高':
                s['conclusion'] = '🟡 轻仓考虑'
            else:
                s['conclusion'] = '⏸ 观望'
        save_daily_report(stocks, data)
        report = format_report(stocks, data)
        print("REPORT_START")
        print(report)
        print("REPORT_END")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
