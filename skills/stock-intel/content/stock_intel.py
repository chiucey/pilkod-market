#!/usr/bin/env python3
"""
股票信息三合一引擎
Baostock + AKShare + QVERIS 联合查询脚本

用法:
  python3 stock_intel.py 000001          # 基本分析
  python3 stock_intel.py 000001 full     # 完整分析(含QVERIS)
  python3 stock_intel.py 000001 fundflow # 资金流向分析
"""

import sys
import json
import subprocess
import os
from datetime import datetime, timedelta

# ─── Baostock Layer ────────────────────────────────────────────────────────────

def get_baostock_kline(code: str, days: int = 90) -> dict:
    """获取历史K线数据（Baostock 涓流API）"""
    try:
        import baostock as bs
        bs.login()
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        # 格式: sh.600519 或 sz.000001（自动转换纯数字代码）
        bs_code = code
        if not ('.' in code):
            bs_code = ('sh.' + code) if code.startswith('6') else ('sz.' + code)
        rs = bs.query_history_k_data_plus(
            bs_code,
            'date,code,open,high,low,close,volume,turn,pctChg',
            start_date=start_date, end_date=end_date, frequency='d'
        )
        rows = [r for r in rs.get_row_data() if r and len(r) >= 9]
        bs.logout()
        if not rows:
            return {"status": "no_data", "code": bs_code}
        closes = [float(r[5]) for r in rows if r[5]]
        volumes = [float(r[6]) for r in rows if r[6]]
        pctChgs = [float(r[8]) for r in rows if r[8]]
        return {
            "status": "success",
            "source": "baostock",
            "data_points": len(rows),
            "latest": rows[-1],
            "ma5":  round(sum(closes[-5:]) / 5, 2) if len(closes) >= 5 else None,
            "ma20": round(sum(closes[-20:]) / 20, 2) if len(closes) >= 20 else None,
            "ma60": round(sum(closes[-60:]) / 60, 2) if len(closes) >= 60 else None,
            "avg_volume": round(sum(volumes) / len(volumes), 0),
            "recent_change": round(sum(pctChgs[-5:]), 2),
            "recent_volumes": volumes[-5:],
            "recent_closes": closes[-10:],
        }
    except Exception as e:
        return {"status": "error", "source": "baostock", "error": str(e)}

def get_baostock_financial(code: str) -> dict:
    """获取财务摘要（Baostock）"""
    try:
        import baostock as bs
        bs.login()
        # 格式转换
        bs_code = code.replace('sh.', 'sz.') if not code.startswith('sh') and not code.startswith('sz') else code
        if not ('sh' in code or 'sz' in code):
            bs_code = 'sz.' + code if code.startswith('0') else 'sh.' + code
        rs = bs.query财务摘要(start_date='2025-12-31')
        rows = [r for r in rs.get_row_data() if r]
        bs.logout()
        return {"status": "success", "financial_data": rows[:5]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ─── AKShare Layer ────────────────────────────────────────────────────────────

def get_akshare_realtime(code: str) -> dict:
    """获取实时行情（AKShare）"""
    try:
        import akshare as ak
        # 格式化代码
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code]
        if row.empty:
            return {"status": "no_match", "code": code}
        r = row.iloc[0]
        return {
            "status": "success",
            "source": "akshare",
            "name": r.get('名称', ''),
            "price": r.get('最新价', 0),
            "change_pct": r.get('涨跌幅', 0),
            "volume": r.get('成交量', 0),
            "amount": r.get('成交额', 0),
            "amplitude": r.get('振幅', 0),
            "high": r.get('最高', 0),
            "low": r.get('最低', 0),
            "open": r.get('今开', 0),
            "prev_close": r.get('昨收', 0),
            "mkt_cap": r.get('总市值', ''),
            "float_mkt_cap": r.get('流通市值', ''),
            "pe": r.get('市盈率-动态', ''),
            "pb": r.get('市净率', ''),
        }
    except Exception as e:
        return {"status": "error", "source": "akshare", "error": str(e)}

def get_akshare_market_summary() -> dict:
    """获取市场概貌（AKShare）"""
    try:
        import akshare as ak
        summary = ak.stock_sse_summary()
        index_df = ak.stock_zh_index_spot_em()
        sh = index_df[index_df['名称'] == '上证指数'].iloc[0] if not index_df[index_df['名称'] == '上证指数'].empty else None
        sz = index_df[index_df['名称'] == '深证成指'].iloc[0] if not index_df[index_df['名称'] == '深证成指'].empty else None
        cy = index_df[index_df['名称'] == '创业板指'].iloc[0] if not index_df[index_df['名称'] == '创业板指'].empty else None
        return {
            "status": "success",
            "source": "akshare",
            "market": {
                "上涨": int(summary.iloc[0, 1]) if len(summary) > 0 else 0,
                "下跌": int(summary.iloc[0, 2]) if len(summary) > 0 else 0,
            },
            "indices": {
                "上证指数": {"price": sh.get('最新价', ''), "change": sh.get('涨跌幅', '')} if sh is not None else {},
                "深证成指": {"price": sz.get('最新价', ''), "change": sz.get('涨跌幅', '')} if sz is not None else {},
                "创业板指": {"price": cy.get('最新价', ''), "change": cy.get('涨跌幅', '')} if cy is not None else {},
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def get_akshare_fundflow(code: str) -> dict:
    """获取资金流向（AKShare）"""
    try:
        import akshare as ak
        df = ak.stock_individual_fund_flow(stock=code, market="sh" if code.startswith('6') else "sz")
        return {"status": "success", "source": "akshare", "fundflow": df.tail(5).to_dict('records')}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ─── QVERIS Layer ─────────────────────────────────────────────────────────────

def discover_qveris(query: str, limit: int = 5) -> dict:
    """通过QVERIS发现专业API工具"""
    try:
        script = os.path.expanduser("~/.openclaw/skills/qveris-official/scripts/qveris_tool.mjs")
        result = subprocess.run(
            ["node", script, "discover", query],
            capture_output=True, text=True,
            env={**os.environ, "QVERIS_API_KEY": "sk-EWuBOIYNNql10MfrX4T4sELRjRHH53uZ2jzlsvDh0Wo"},
            timeout=30
        )
        lines = result.stdout.strip().split('\n')
        # 提取 search_id
        search_id = None
        for line in lines:
            if 'Discovery ID:' in line:
                search_id = line.split('Discovery ID:')[1].strip()
        return {"status": "success", "search_id": search_id, "raw": result.stdout[:2000]}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ─── 主程序入口 ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 stock_intel.py <股票代码> [模式]")
        print("模式: basic (默认) | full | fundflow | market")
        sys.exit(1)

    code = sys.argv[1].zfill(6)
    mode = sys.argv[2] if len(sys.argv) > 2 else 'basic'

    print(f"\n{'='*60}")
    print(f"  股票分析引擎  代码: {code}  模式: {mode}")
    print(f"{'='*60}\n")

    if mode == 'basic':
        bao = get_baostock_kline(code)
        aks = get_akshare_realtime(code)
        print(f"【Baostock K线】\n{json.dumps(bao, ensure_ascii=False, indent=2)}")
        print(f"\n【AKShare 实时】\n{json.dumps(aks, ensure_ascii=False, indent=2)}")

    elif mode == 'full':
        bao = get_baostock_kline(code, days=120)
        aks = get_akshare_realtime(code)
        summary = get_akshare_market_summary()
        qveris = discover_qveris("Chinese stock financial report API")
        print(f"【市场概貌】\n{json.dumps(summary, ensure_ascii=False, indent=2)}")
        print(f"\n【Baostock K线(120日)】\n{json.dumps(bao, ensure_ascii=False, indent=2)}")
        print(f"\n【AKShare 实时】\n{json.dumps(aks, ensure_ascii=False, indent=2)}")
        print(f"\n【QVERIS 工具发现】\n{json.dumps(qveris, ensure_ascii=False, indent=2)}")

    elif mode == 'fundflow':
        flow = get_akshare_fundflow(code)
        bao = get_baostock_kline(code)
        print(f"【资金流向】\n{json.dumps(flow, ensure_ascii=False, indent=2)}")
        print(f"\n【Baostock K线】\n{json.dumps(bao, ensure_ascii=False, indent=2)}")

    elif mode == 'market':
        summary = get_akshare_market_summary()
        print(f"【市场概貌】\n{json.dumps(summary, ensure_ascii=False, indent=2)}")

    else:
        print(f"未知模式: {mode}")
        sys.exit(1)
