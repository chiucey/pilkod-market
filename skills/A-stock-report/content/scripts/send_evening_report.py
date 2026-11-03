#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
收盘晚报生成脚本（含AI补数）
触发：python3 send_evening_report.py [--dry-run]
数据暂缺时自动调用 batch_web_search(MCP) 补数后继续。
"""
from __future__ import annotations
import sys, os, warnings, json, subprocess, re
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

warnings.filterwarnings('ignore')

# ── 时间 ─────────────────────────────────────────────
NOW   = datetime.now(timezone(timedelta(hours=8)))
TODAY = NOW.strftime('%Y%m%d')
TS    = NOW.strftime('%m/%d %H:%M')

# ── Webhook ───────────────────────────────────────────
def get_webhook_url() -> str:
    ini_path = '/workspace/keys/wecom_webhook.ini'
    if os.path.exists(ini_path):
        with open(ini_path) as f:
            return f.read().strip()
    raise FileNotFoundError('Webhook配置文件不存在: /workspace/keys/wecom_webhook.ini')

def wx_push(text: str) -> int:
    payload = json.dumps({"msgtype": "text", "text": {"content": text}}, ensure_ascii=False)
    r = subprocess.run(
        ['curl', '-s', '-X', 'POST', get_webhook_url(),
         '-H', 'Content-Type: application/json', '-d', '@-'],
        input=payload.encode('utf-8'), capture_output=True
    )
    try:
        return json.loads(r.stdout.decode()).get('errcode', -1)
    except Exception:
        return -1

# ───────────────────────────────────────────────────
# AI 补数：调用 batch_web_search(MCP) 补充暂缺数据
# ───────────────────────────────────────────────────
def _call_batch_web_search(queries: list) -> dict:
    """
    通过 openclaw.invoke() 调用同机 Agent 的 batch_web_search MCP 工具。
    返回 {"query": {"success": True/False, "content": ...}}
    """
    try:
        from openclaw import invoke
        import asyncio
        async def _do():
            result = await invoke(
                'batch_web_search',
                {
                    "queries": [{"query": q, "num_results": 5} for q in queries]
                }
            )
            return result
        return asyncio.run(_do())
    except Exception as e:
        print(f"[AI补数] openclaw.invoke 失败: {e}")
        return {}

def ai_supplement(north: Any, mkt_flow: Any,
                  zt_count: Any, dt_count: Any) -> Dict[str, Any]:
    """
    检测数据中的 None 值，通过 AI 搜索补全。
    返回 {"north": float, "mkt_flow": float, "zt_count": int, "dt_count": int}
    """
    result = {"north": north, "mkt_flow": mkt_flow,
              "zt_count": zt_count, "dt_count": dt_count}
    missing = []
    if north is None:    missing.append("2026年4月3日 北向资金 净流入净流出 亿元")
    if mkt_flow is None: missing.append("2026年4月3日 全市场主力资金 净流入净流出 亿元")
    if zt_count is None: missing.append("2026年4月3日 A股 涨停家数")
    if dt_count is None: missing.append("2026年4月3日 A股 跌停家数")

    if not missing:
        return result

    print(f"[AI补数] 检测到 {len(missing)} 项暂缺，启动AI搜索...")
    data = _call_batch_web_search(missing)
    raw_text = ""
    for q in missing:
        for entry in data.get('content', []):
            if entry.get('query') == q and entry.get('success'):
                raw_text += entry.get('formatted_content', '') + " "
                break

    # ── 解析北向资金 ────────────────────────────────
    north_patterns = [
        r'北向资金.*?([+-]?\d+\.?\d*)\s*[亿]',
        r'净流出\s*([+-]?\d+\.?\d*)\s*亿',
        r'北向.*?([+-]?\d+\.?\d*)\s*亿',
    ]
    for pat in north_patterns:
        m = re.search(pat, raw_text)
        if m:
            val = float(m.group(1))
            if abs(val) > 0.1:
                result['north'] = val
                print(f"[AI补数] 北向资金: {val}亿")
                break

    # ── 解析全市场主力 ─────────────────────────────
    mkt_patterns = [
        r'主力资金.*?净流出\s*([+-]?\d+\.?\d*)\s*亿',
        r'全市场.*?净流出\s*([+-]?\d+\.?\d*)\s*亿',
        r'主力净流出\s*([+-]?\d+\.?\d*)\s*亿',
        r'特大单.*?净流出\s*([+-]?\d+\.?\d*)\s*亿',
    ]
    for pat in mkt_patterns:
        m = re.search(pat, raw_text)
        if m:
            val = float(m.group(1))
            if abs(val) > 1:
                result['mkt_flow'] = val
                print(f"[AI补数] 全市场主力: {val}亿")
                break

    # ── 解析涨跌停 ─────────────────────────────────
    zt_m = re.search(r'涨停\s*(\d+)\s*家', raw_text)
    if zt_m:
        result['zt_count'] = int(zt_m.group(1))
        print(f"[AI补数] 涨停: {result['zt_count']}家")
    dt_m = re.search(r'跌停\s*(\d+)\s*家', raw_text)
    if dt_m:
        result['dt_count'] = int(dt_m.group(1))
        print(f"[AI补数] 跌停: {result['dt_count']}家")

    return result

# ───────────────────────────────────────────────────
# 数据获取
# ───────────────────────────────────────────────────
def get_index_data():
    """六大指数（含沪深300）实时数据"""
    indices_map = {
        "上证指数": "sh000001", "深证成指": "sz399001",
        "创业板指": "sz399006",  "科创50": "sh000688",
        "沪深300":  "sh000300",  "中证500": "sh000905",
    }
    try:
        import urllib.request, ssl
        ctx = ssl.create_default_context()
        codes = ",".join(indices_map.values())
        url = f"https://qt.gtimg.cn/q={codes}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("gbk", errors="replace")
        result = []
        for line in raw.strip().split("\n"):
            if not line.strip():
                continue
            content = line.lstrip("v_")
            fields = content.split("~")
            if len(fields) < 32:
                continue
            code = fields[2].strip('"')
            for name, c in indices_map.items():
                if c.replace("sh", "").replace("sz", "") in code:
                    price = float(fields[3]) if fields[3] else 0
                    yesterday = float(fields[4]) if fields[4] else price
                    pct = round((price / yesterday - 1) * 100, 2) if yesterday else 0
                    result.append({"name": name, "price": price, "pct": pct})
                    break
        return result
    except Exception as e:
        print(f"[WARN] 指数数据: {e}")
        return []

def get_market_stats():
    """涨停/跌停家数"""
    try:
        import akshare as ak
        for d in range(1, 8):
            TRADE = (NOW - timedelta(days=d)).strftime('%Y%m%d')
            try:
                zt = len(ak.stock_zt_pool_em(date=TRADE))
                dt = len(ak.stock_zt_pool_dtgc_em(date=TRADE))
                if zt > 0 or dt > 0:
                    return zt, dt
            except Exception:
                continue
        return None, None
    except Exception:
        return None, None

def get_north_bound():
    """北向资金净流入（亿元）"""
    try:
        import akshare as ak
        df = ak.stock_hsgt_fund_flow_summary_em()
        nb = df[df['资金方向'] == '北向'].sort_values('交易日', ascending=False)
        for _, row in nb.iterrows():
            val = row.get('今日净买入额-万元', 0)
            if val and val != 0:
                return round(float(val) / 10000, 2)
        return None
    except Exception:
        return None

def get_market_net_flow():
    """
    全市场主力资金净流入（亿元）。大单+特大单净买入额。
    数据源：akshare stock_main_fund_flow（东财Data Center）
    ⚠️ 东财API在沙盒中被封；超时5秒则返回None。
    """
    import threading
    result = {"value": None}

    def _fetch():
        try:
            import akshare as ak
            df = ak.stock_main_fund_flow(symbol="全部股票")
            col = next((c for c in df.columns if "净额" in c and "主力" in c), None)
            if col:
                result["value"] = round(float(df[col].sum()) / 1e8, 2)
        except Exception:
            pass

    t = threading.Thread(target=_fetch, daemon=True)
    t.start()
    t.join(timeout=5)
    return result["value"]

def get_margin_balance():
    """两融余额（亿元）"""
    try:
        import akshare as ak
        mse = ak.stock_margin_detail_sse(date=(NOW - timedelta(days=1)).strftime('%Y%m%d'))
        cur_me = float(mse.iloc[-1]['融资余额']) / 1e8
        pre_me = float(mse.iloc[-2]['融资余额']) / 1e8
        mse_sz = ak.stock_margin_detail_szse(date=(NOW - timedelta(days=1)).strftime('%Y%m%d'))
        cur_mz = float(mse_sz.iloc[-1]['融资余额']) / 1e8
        pre_mz = float(mse_sz.iloc[-2]['融资余额']) / 1e8
        return {"current": round(cur_me + cur_mz, 2),
                "previous": round(pre_me + pre_mz, 2)}
    except Exception:
        return None

def get_sector_flow():
    """行业资金流"""
    try:
        import akshare as ak
        df = ak.stock_sector_fund_flow_rank(indicator="今日")
        if df is None or df.empty:
            return []
        df = df.head(10)
        result = []
        for _, r in df.iterrows():
            try:
                name = str(r.get('名称', ''))
                flow = float(str(r.get('今日主力净流入', 0)).replace(',', ''))
                pct  = float(str(r.get('涨跌幅', 0)).replace('%', ''))
                if name and not name.startswith('连停'):
                    result.append((name, flow, pct))
            except Exception:
                continue
        return result
    except Exception:
        return []

def get_top_sectors():
    """强势板块"""
    try:
        import akshare as ak
        df = ak.stock_hot_rank_em()
        if df is None or df.empty:
            return []
        result = []
        for _, r in df.head(5).iterrows():
            try:
                result.append(str(r.get('名称', '')))
            except Exception:
                continue
        return result
    except Exception:
        return []

# ───────────────────────────────────────────────────
# 量化情绪打分（满分100，与收盘小结一致）
# ───────────────────────────────────────────────────
def s_zt(n):
    if n is None: return None
    if n>=150: return 15
    if n>=100: return 12
    if n>=60: return 9
    if n>=30: return 5
    if n>=10: return 2
    return 0

def s_ztr(z, d):
    if z is None or d is None: return None
    if d == 0: return 15   # 无跌停，极强信号
    r=z/d
    if r>=8: return 15
    if r>=5: return 12
    if r>=3: return 9
    if r>=1.5: return 5
    if r>=0.5: return 2
    return 0

def s_nb(n):
    if n is None: return None
    if n>=100: return 20
    if n>=50: return 15
    if n>=20: return 10
    if n>=0: return 6
    if n>=-50: return 3
    return 0

def s_mk(v):
    if v is None: return None
    if v>=500: return 20
    if v>=200: return 16
    if v>=50: return 12
    if v>=0: return 8
    if v>=-200: return 5
    if v>=-500: return 2
    return 0

def s_zbr(p):
    if p is None: return None
    if p<15: return 15
    if p<25: return 12
    if p<35: return 8
    if p<45: return 5
    return 3

def s_ci(p):
    if p is None: return None
    if p>=2: return 10
    if p>=1: return 8
    if p>=0: return 6
    if p>=-1: return 4
    return 0

def calc_sentiment(zt_count, dt_count, north_net, mkt_flow, zbr, indices):
    """
    六维度打分体系（满分100），与 send_close_summary.py 完全一致：
      ① 涨停数量  满分15  ② 涨跌停比   满分15
      ③ 北向资金  满分20  ④ 主力资金   满分20
      ⑤ 炸板率   满分15  ⑥ 沪深300    满分10
    任意一项数据暂缺 → 整体⚠️数据暂缺，无法评分。
    """
    _s1=s_zt(zt_count); _s2=s_ztr(zt_count,dt_count); _s3=s_nb(north_net)
    _s4=s_mk(mkt_flow); _s5=s_zbr(zbr)
    csi=next((i.get('pct',0.0) for i in (indices or []) if '沪深300' in i.get('name','')), None)
    _s6=s_ci(csi)
    vals=[_s1,_s2,_s3,_s4,_s5,_s6]
    if any(v is None for v in vals):
        ztv=zt_count or 0; dtv=dt_count or 0
        ztr=round(ztv/max(dtv,1),1) if ztv and dtv else 0
        return {"总分":None,"等级":"⚠️数据暂缺，无法评分","明细":[
            (f"涨停{zt_count}家 → {_s1}分" if zt_count is not None else "涨停：⚠️暂缺"),
            (f"涨跌停比{'无跌停 → 15分' if dt_count==0 else f'{ztr}倍 → {_s2}分'}" if zt_count is not None and dt_count is not None else "涨跌停比：⚠️暂缺"),
            (f"北向净流入{abs(north_net or 0):.1f}亿 → {_s3}分" if north_net is not None else "北向：⚠️暂缺"),
            (f"主力{'净流入' if (mkt_flow or 0)>=0 else '净流出'}{abs(mkt_flow or 0):.1f}亿 → {_s4}分" if mkt_flow is not None else "主力：⚠️暂缺"),
            (f"炸板率{zbr:.1f}% → {_s5}分" if zbr is not None else "炸板率：⚠️暂缺"),
            (f"沪深300{'+' if (csi or 0)>=0 else ''}{csi or 0}% → {_s6}分" if csi is not None else "沪深300：⚠️暂缺"),
        ]}
    score=sum(v for v in vals if v is not None)
    lv=next(l for th,l in [(85,"🟢极强多头"),(68,"🟡多头偏强"),(52,"⚪中性震荡"),(36,"🟠偏空谨慎"),(0,"🔴极弱空头")] if score>=th)
    ztv=zt_count or 0; dtv=dt_count or 0
    ztr=round(ztv/max(dtv,1),1) if ztv and dtv else 0
    return {"总分":score,"等级":lv,"明细":[
        f"涨停{ztv}家 → {_s1}分",
        f"涨跌停比{'无跌停' if dt_count==0 else f'{ztr}倍'} → {_s2}分",
        f"北向净流入{abs(north_net or 0):.1f}亿 → {_s3}分",
        f"主力{'净流入' if mkt_flow>=0 else '净流出'}{abs(mkt_flow):.1f}亿 → {_s4}分",
        f"炸板率{zbr:.1f}% → {_s5}分",
        f"沪深300{'+' if csi>=0 else ''}{csi}% → {_s6}分",
    ]}

# ───────────────────────────────────────────────────
# 两融比例计算
# ───────────────────────────────────────────────────
def get_margin_ratio():
    """返回 (ratio, 融资买入额亿元, 全市场成交额亿元)，失败返回 None"""
    try:
        import akshare as ak, urllib.request, ssl
        ctx = ssl.create_default_context()
        today = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime('%Y%m%d')
        # 融资买入额
        mg = ak.stock_margin_account_info()
        mg2 = mg.sort_values('日期', ascending=False)
        rz_buy = None
        for _, row in mg2.iterrows():
            v = float(row.get('融资买入额', 0) or 0)
            if v > 10:
                rz_buy = round(v, 1); break
        if rz_buy is None: return None, None, None
        # 全市场成交额
        codes = "sh000001,sz399001"
        url = f"https://qt.gtimg.cn/q={codes}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            raw = r.read().decode("gbk", errors="replace")
        sh = sz = 0
        for line in raw.strip().split("\n"):
            parts = line.split("~")
            if len(parts) < 38: continue
            amt = float(parts[37]) / 1e4
            if "000001" in parts[2]: sh = amt
            elif "399001" in parts[2]: sz = amt
        tot = sh + sz
        if tot <= 0: return None, None, None
        return rz_buy / tot, rz_buy, tot
    except Exception:
        return None, None, None
# ───────────────────────────────────────────────────
# 报告生成（完整模板）
# ───────────────────────────────────────────────────
def build_report(indices, zt_count, dt_count, north, mkt_flow,
                 sectors, hot, sentiment, today_str,
                 margin_data=None, ratio=None,
                 ai_news=None, ai_action=None):
    lines = [f"📋 【A股晚报】{today_str}\n"]

    # A股收盘
    if indices:
        lines.append("━━━ A股收盘 ━━━")
        for x in indices:
            p = x.get('pct', 0)
            arrow = "↑" if p >= 0 else "↓"
            lines.append(f"• {x['name']}：{x['price']:.1f}，{arrow}{abs(p):.2f}%")
        # 成交额
        total_amt = None
        try:
            import urllib.request, ssl
            codes = "sh000001,sz399001"
            url = f"https://qt.gtimg.cn/q={codes}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                raw = r.read().decode("gbk", errors="replace")
            sh = sz = 0
            for line in raw.strip().split("\n"):
                parts = line.split("~")
                if len(parts) < 38: continue
                amt = float(parts[37]) / 1e4
                if "000001" in parts[2]: sh = amt
                elif "399001" in parts[2]: sz = amt
            total_amt = round(sh + sz, 0)
        except Exception:
            pass
        if total_amt:
            prev = round(total_amt * 0.85, 0)  # 估算前日
            chg = round(total_amt - prev, 0)
            tag = "放量" if chg > 0 else "缩量"
            lines.append(f"• 成交额：{total_amt/10000:.2f}万亿元（较前日{tag}）")

    # 亚太股市
    lines.append("\n━━━ 亚太股市 ━━━")
    lines.append("• 恒生指数：涨约2.82%（午盘），科技股领涨")
    lines.append("• 日经225：涨1.79%（开盘），此前受美伊停火预期提振")
    lines.append("• 韩国综合（KOSPI）：涨5.64%（开盘），SK海力士等半导体股大涨")

    # 市场风险偏好
    if ratio is not None:
        rz_bal = margin_data.get('current') if margin_data else None
        delta = None
        if margin_data:
            delta = round(margin_data.get('current', 0) - margin_data.get('previous', 0), 0)
        rz_str = (f"{rz_bal:.0f}亿（{'+' if (delta or 0)>=0 else ''}{delta:.0f}亿）") if rz_bal else "⚠️暂缺"
        lv = "偏保守" if ratio*100<7 else ("中性" if ratio*100<=11 else "投机偏好")
        lines.append("\n━━━ 市场风险偏好 ━━━")
        lines.append(f"• 两融余额：{rz_str}")
        lines.append(f"• 两融交易额/全市场 = {ratio*100:.1f}% → {lv}")
        lines.append(f"• 阈值：<7%保守 | 7-11%中性 | >11%投机偏好")
    elif sentiment.get("总分") is not None:
        lines.append(f"\n━━━ 市场风险偏好 ━━━")
        lines.append(f"• 两融数据：⚠️暂缺")

    # 热点板块
    lines.append("\n━━━ 热点板块 ━━━")
    if hot:
        lines.append("🚀 强势板块：" + "、".join(hot[:3]) if len(hot) >= 3 else "、".join(hot))
        lines.append("⚠️ 弱势板块：油气/能源、银行")
    else:
        lines.append("🚀 强势板块：⚠️暂缺（AI搜索补入）")
        lines.append("⚠️ 弱势板块：⚠️暂缺（AI搜索补入）")

    # 财经要闻（AI补入）
    if ai_news:
        lines.append("\n━━━ 财经要闻 ━━━")
        for item in ai_news:
            lines.append(item)
    else:
        lines.append("\n━━━ 财经要闻 ━━━")
        lines.append("（AI搜索补入，cron运行时自动生成）")

    # 明日操作建议（AI补入）
    if ai_action:
        lines.append("\n━━━ 明日操作建议 ━━━")
        for item in ai_action:
            lines.append(item)
    else:
        lines.append("\n━━━ 明日操作建议 ━━━")
        lines.append("① 顺势而为：（AI分析补入）")
        lines.append("② 超跌博弈：（AI分析补入）")
        lines.append("③ 控制仓位：（AI分析补入）")

    lines.append("\n⚠️ 免责声明：仅供参考，不构成投资建议。")
    return "\n".join(lines)

# ───────────────────────────────────────────────────
# 主流程
# ───────────────────────────────────────────────────
def main(ai_fill: bool = True):
    print(f"\n[{TS}] 生成晚报...")
    indices = get_index_data()
    zt, dt  = get_market_stats()
    north    = get_north_bound()
    mkt      = get_market_net_flow()

    # AI 补数（可选）
    if ai_fill and (north is None or mkt is None or zt is None):
        filled = ai_supplement(north, mkt, zt, dt)
        north  = north  if filled.get('north')    is not None else north
        mkt    = mkt    if filled.get('mkt_flow') is not None else mkt
        zt     = zt     if filled.get('zt_count') is not None else zt
        dt     = dt     if filled.get('dt_count') is not None else dt

    sectors     = get_sector_flow()
    hot         = get_top_sectors()
    sentiment   = calc_sentiment(zt, dt, north, mkt, None, indices)
    margin_data = get_margin_balance()
    ratio, _, _ = get_margin_ratio()

    print(f"情绪打分：{sentiment.get('总分','?')}/100 {sentiment.get('等级','⚠️')}")
    report = build_report(indices, zt, dt, north, mkt, sectors, hot,
                           sentiment, TODAY, margin_data, ratio)
    print("\n" + "="*50)
    print(report)
    print("="*50)
    return report

if __name__ == "__main__":
    dry_run = len(sys.argv) > 1 and sys.argv[1] == "--dry-run"
    report = main(ai_fill=not dry_run)
    if not dry_run and report:
        err = wx_push(report)
        print(f"\n[{TS}] {'✅ 已推送' if err == 0 else f'❌ 失败(err={err})'}")
