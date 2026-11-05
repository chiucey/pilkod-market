#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A 股行情 + 资金流 + 事件风险统一取数(野人哥交易体系 skill 配套)

用法:
    python3 fetch.py 002614                # 6 位数字,自动识别沪深
    python3 fetch.py SH600760              # 带市场前缀
    python3 fetch.py 002201 --days 14      # 近 14 个交易日
    python3 fetch.py 002201 --events       # 追加事件风险快检
    python3 fetch.py 002201 --json         # 机器可读输出

数据源优先级(用户明确要求):
    1) 恒生金融数据库(MiniMax Finance)  ← 首选,字段口径明确、自带守恒校验
    2) 东方财富                            ← 降级,需自行校验 f52~f56 口径
    3) 腾讯行情                            ← 降级,实时+全天分时最稳
    4) 新浪行情                            ← 降级,日线/资金流兜底

每个模块独立降级,输出里标注**实际**用了哪个源。不同源口径不可直接比数值,只可比方向与相对变化。

已验证的坑(别改):
  * 恒生 6 位代码必须补后缀(000032.SZ / 600760.SH / 300589.SZ / 8xx→.BJ)
  * 恒生分时只返回最近 30 分钟,pageNo>1 为空 → 全天轨迹必须用腾讯补
  * 东财 f51~f57: f52=主力净额(大单+超大单) / f53=小单 / f54=中单 / f55=大单 / f56=超大单
    校验式: f53+f54+f55+f56≈0 且 f55+f56==f52。把 f53/f54 当超大单/大单会让结论完全反向。
  * 新浪日 K 成交量单位是股,腾讯是手,统一输出"万手"
  * 缺值一律显示 "-",不显示 0.00(会被误读成真实数据)
"""
import sys
import json
import time
import argparse
import datetime
import urllib.request
import urllib.parse

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import hengsheng as HS  # noqa: E402

UA_TQ = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0 Safari/537.36",
         "Referer": "https://gu.qq.com/"}
UA_EM = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
         "Referer": "https://quote.eastmoney.com/"}
UA_SINA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0 Safari/537.36",
           "Referer": "https://finance.sina.com.cn/"}
UT = "7eea3edcaed734bea9cbfc24409ed989"
EM_HOSTS = ["push2his.eastmoney.com", "push2.eastmoney.com", "63.push2his.eastmoney.com",
            "48.push2.eastmoney.com", "29.push2his.eastmoney.com", "82.push2.eastmoney.com"]


def http(url, headers, timeout=12, retry=2, decode="utf-8"):
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode(decode, "ignore")
        except Exception:
            if i < retry:
                time.sleep(1.5)
    return None


def n(v, digits=2):
    if v is None or v == "":
        return "-"
    if isinstance(v, (int, float)):
        return f"{v:.{digits}f}"
    return str(v)


def v(vv):
    if vv is None:
        return "不适用"
    return "通过" if vv else "⚠️未通过"


def resolve(raw):
    """-> (code6, hengsheng_code, market)"""
    raw = raw.strip()
    if raw.isdigit():
        code = raw.zfill(6)
    elif "." in raw and raw.split(".")[-1].upper() in ("SH", "SZ", "BJ"):
        left, right = raw.split(".")
        code = (right if left.upper() in ("SH", "SZ", "BJ") else left).zfill(6)
    else:
        t = http(f"https://smartbox.gtimg.cn/s3/?q={urllib.parse.quote(raw)}&t=all",
                 UA_TQ, decode="gb18030")
        import re
        m = re.search(r'v_hint="(sh|sz|bj)~(\d{6})~', t or "")
        if not m:
            return None, None, None
        code = m.group(2)
    if code[0] == "6":
        mkt = "SH"
    elif code[:3] in ("000", "001", "002", "003", "300", "301"):
        mkt = "SZ"
    elif code[0] in ("8", "4", "9"):
        mkt = "BJ"
    else:
        mkt = "SZ"
    return code, code + "." + mkt, mkt


# ============================================================ 降级源:东方财富

def em_daily(code, mkt, days):
    sid = ("1." if mkt == "SH" else "0.") + code
    for host in EM_HOSTS:
        u = (f"https://{host}/api/qt/stock/kline/get?secid={sid}&ut={UT}"
             "&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
             f"&klt=101&fqt=1&beg=0&end=20500101&lmt={days + 4}")
        t = http(u, UA_EM, retry=1)
        if not t:
            continue
        try:
            kl = json.loads(t)["data"]["klines"]
        except Exception:
            continue
        out = []
        for r in kl[-days:]:
            p = r.split(",")
            out.append({"date": p[0], "open": float(p[1]), "close": float(p[2]),
                        "high": float(p[3]), "low": float(p[4]),
                        "avg_price": None, "prev_close": None,
                        "change_pct": float(p[8]), "amplitude_pct": float(p[7]),
                        "turnover_pct": float(p[10]), "vol_ratio": None,
                        "amount_wan": float(p[6]), "volume_wanshou": round(float(p[5]) / 1e6, 2),
                        "deals": None, "suspended": None, "source": "东财"})
        return out
    return None


def em_flow(code, mkt):
    sid = ("1." if mkt == "SH" else "0.") + code
    for host in EM_HOSTS:
        u = (f"https://{host}/api/qt/stock/fflow/kline/get?lmt=0&klt=101&secid={sid}&ut={UT}"
             "&fields1=f1,f2,f3,f7&fields2=f51,f52,f53,f54,f55,f56,f57")
        t = http(u, UA_EM, retry=1)
        if not t:
            continue
        try:
            ks = json.loads(t)["data"]["klines"]
        except Exception:
            continue
        out = []
        for r in ks[-12:]:
            p = r.split(",")
            f52, f53, f54, f55, f56 = (float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5]))
            tol = max(1000.0, abs(f52) * 0.02)
            ok = abs(f53 + f54 + f55 + f56) < tol and abs((f55 + f56) - f52) < tol
            out.append({"date": p[0][-10:], "close": None, "change_pct": None,
                        "main_wan": round(f52 / 1e4), "super_wan": round(f56 / 1e4),
                        "big_wan": round(f55 / 1e4), "mid_wan": round(f54 / 1e4),
                        "small_wan": round(f53 / 1e4), "amount_wan": None,
                        "dde_ratio_pct": None, "rising_days": None,
                        "balance_ok": ok, "source": "东财"})
        return out
    return None


# ============================================================ 降级源:腾讯 / 新浪

def tx_realtime(code, mkt):
    sym = ("sh" if mkt == "SH" else "sz") + code
    t = http(f"https://qt.gtimg.cn/q={sym}", UA_TQ, decode="gb18030")
    if not t or '="' not in t:
        return None
    try:
        f = t.split('="')[1].rsplit('"', 1)[0].split("~")
        if len(f) < 40:
            return None
        px, vol = float(f[3]), float(f[6])
        inner, outer = int(f[7]), int(f[8])
        return {"name": f[1], "code": code, "time": f[30], "status": None,
                "price": px, "prev_close": float(f[4]), "open": float(f[5]),
                "high": float(f[33]), "low": float(f[34]), "avg_price": None,
                "change_pct": float(f[32]), "amplitude_pct": None,
                "turnover_pct": float(f[38]), "vol_ratio": f[49] or None,
                "volume_wanshou": round(vol / 1e4, 2),
                "amount_yi": round(vol * px * 100 / 1e8, 2),
                "inner_vol": inner, "outer_vol": outer,
                "entrust_diff": None, "entrust_rate": None,
                "bid_grp": f"买一 {f[9]}x{f[10]}", "offer_grp": f"卖一 {f[19]}x{f[20]}",
                "limit_up": None, "limit_down": None,
                "pe_ttm": None, "pb": None, "ps": None, "dividend_yield": None,
                "negotiable_mv": None, "total_mv": None, "total_shares": None,
                "float_shares": None, "source": "腾讯"}
    except Exception:
        return None


def tx_minute(code, mkt):
    """腾讯全天分时:时间/价/累计量占比"""
    sym = ("sh" if mkt == "SH" else "sz") + code
    t = http(f"https://web.ifzq.gtimg.cn/appstock/app/minute/query?code={sym}", UA_TQ, decode="gb18030")
    if not t:
        return None
    try:
        data = json.loads(t)["data"][sym]["data"]["data"]
    except Exception:
        return None
    pts = []
    for s in data:
        p = s.split(" ")
        if len(p) >= 4:
            pts.append((p[0], float(p[1]), float(p[2])))
    if not pts:
        return None
    total = sum(x[2] for x in pts)
    if total <= 0:
        return None
    cum, marks = 0.0, []
    for tm, pr, vol in pts:
        cum += vol
        marks.append({"time": tm, "price": pr, "cum_pct": round(cum / total * 100, 1)})
    hi = max(pts, key=lambda x: x[1])
    lo = min(pts, key=lambda x: x[1])
    return {"points": marks[::5],
            "high": {"time": hi[0], "price": hi[1],
                     "cum_pct": round(sum(x[2] for x in pts if x[0] <= hi[0]) / total * 100, 1)},
            "low": {"time": lo[0], "price": lo[1],
                    "cum_pct": round(sum(x[2] for x in pts if x[0] <= lo[0]) / total * 100, 1)},
            "source": "腾讯分时"}


def sina_daily(code, mkt, days):
    sym = ("sh" if mkt == "SH" else "sz") + code
    u = ("https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/"
         f"CN_MarketData.getKLineData?symbol={sym}&scale=240&ma=no&datalen={days + 4}")
    t = http(u, UA_SINA)
    if not t:
        return None
    try:
        kl = json.loads(t)
    except Exception:
        return None
    out, prev = [], None
    for r in kl[-days:]:
        c = float(r["close"])
        out.append({"date": r["day"], "open": float(r["open"]), "close": c,
                    "high": float(r["high"]), "low": float(r["low"]),
                    "avg_price": None, "prev_close": prev,
                    "change_pct": round((c / prev - 1) * 100, 2) if prev else None,
                    "amplitude_pct": None, "turnover_pct": None, "vol_ratio": None,
                    "amount_wan": None,
                    "volume_wanshou": round(float(r["volume"]) / 1e6, 2),
                    "deals": None, "suspended": None, "source": "新浪"})
        prev = c
    return out


def sina_flow(code, mkt):
    sym = ("sh" if mkt == "SH" else "sz") + code
    u = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
         f"MoneyFlow.ssl_qsfx_zjlrqs?page=1&num=12&sort=opendate&asc=0&daima={sym}")
    t = http(u, UA_SINA)
    if not t:
        return None
    try:
        d = json.loads(t)
    except Exception:
        return None
    out = []
    for x in d:
        out.append({"date": x["opendate"], "close": None, "change_pct": None,
                    "main_wan": round(float(x["netamount"]) / 1e4),
                    "super_wan": round(float(x["r0_net"]) / 1e4),
                    "big_wan": None, "mid_wan": None, "small_wan": None,
                    "amount_wan": None, "dde_ratio_pct": None, "rising_days": None,
                    "balance_ok": None, "source": "新浪口径"})
    return out


# ============================================================ 编排

def fetch_all(code, hs_code, mkt, days, want_events=False):
    out = {"code": code, "hengsheng_code": hs_code, "market": mkt,
           "realtime": None, "kline": [], "kline_source": None,
           "flow": [], "flow_source": None, "flow_verified": None,
           "minute": None, "tick": [], "events": {}, "notes": []}
    today = datetime.date.today()
    begin = (today - datetime.timedelta(days=days * 3 + 20)).isoformat()
    end = today.isoformat()

    # ---- 实时行情:恒生 → 腾讯
    rt = HS.live_quote(hs_code)
    tx = tx_realtime(code, mkt)
    if rt:
        if not rt.get("price"):
            # 集合竞价前/停牌:恒生 price=0,用昨收占位,估值与市值仍有效
            rt["price"] = rt.get("prev_close")
            rt["status"] = rt.get("status") or "未开盘/无成交"
            if tx:
                rt["bid_grp"], rt["offer_grp"] = tx.get("bid_grp"), tx.get("offer_grp")
                rt["inner_vol"] = rt.get("inner_vol") or tx.get("inner_vol")
                rt["outer_vol"] = rt.get("outer_vol") or tx.get("outer_vol")
                rt["time"] = tx.get("time") or rt.get("time")
        out["realtime"] = rt
    elif tx:
        out["realtime"] = tx
        out["notes"].append("恒生实时不可用,已降级腾讯")
    else:
        out["notes"].append("实时行情:恒生与腾讯均不可用")

    # ---- 日线:恒生 → 东财 → 新浪
    kl = HS.daily_quote(hs_code, begin, end)
    if kl:
        out["kline"], out["kline_source"] = kl[-days:], "恒生"
    else:
        out["notes"].append("恒生日线不可用,降级东财/新浪")
        kl = em_daily(code, mkt, days) or sina_daily(code, mkt, days)
        if kl:
            out["kline"] = kl
            out["kline_source"] = kl[0].get("source")

    # ---- 资金流:恒生 → 东财(校验) → 新浪
    fl = HS.cash_flow(hs_code, begin, end)
    if fl:
        out["flow"], out["flow_source"] = fl[-12:], "恒生"
        out["flow_verified"] = all(x.get("balance_ok") for x in fl[-3:]) if fl else None
    else:
        out["notes"].append("恒生资金流不可用,降级东财/新浪")
        fl = em_flow(code, mkt)
        if fl:
            out["flow"], out["flow_source"] = fl, "东财"
            out["flow_verified"] = all(x["balance_ok"] for x in fl[-3:])
        else:
            fl = sina_flow(code, mkt)
            if fl:
                out["flow"], out["flow_source"], out["flow_verified"] = fl, "新浪口径", None

    # ---- 分时:恒生近30分钟 + 腾讯全天轨迹
    out["tick"] = HS.tick_quote(hs_code)
    mn = tx_minute(code, mkt)
    if mn:
        out["minute"] = mn

    # ---- 事件风险快检(仅恒生有)
    if want_events:
        out["events"] = {
            "report_disclosure": HS.report_disclosure(hs_code),
            "shareholder_num": HS.shareholder_num(hs_code),
            "restricted_lifting": HS.restricted_lifting(hs_code),
            "change_plan": HS.change_plan(hs_code),
            "key_holder_trade": HS.key_holder_trade(hs_code),
            "performance_forecast": HS.performance_forecast(hs_code),
            "value_analysis": HS.value_analysis(hs_code, begin, end)[-5:],
            "hero_list": HS.hero_list(hs_code, begin, end),
            "margin_trade": HS.margin_trade(hs_code, begin, end)[-5:],
            "range_quote": HS.range_quote(hs_code, begin, end),
            "real_time_flow": HS.real_time_flow(hs_code),
            "belong_concept": HS.belong_concept(hs_code)[:12],
        }
    return out


def print_human(o, want_events=False):
    rt = o["realtime"]
    print("=" * 86)
    if rt:
        print(f"{rt.get('name','')} ({o['code']}.{o['market']})  数据时间 {rt.get('time')}  "
              f"状态 {rt.get('status') or '-'}  来源 {rt.get('source')}")
        print(f"  现价 {n(rt['price'])}  涨跌 {n(rt['change_pct'])}%  昨收 {n(rt['prev_close'])}  "
              f"开 {n(rt['open'])}  高 {n(rt['high'])}  低 {n(rt['low'])}  均价 {n(rt['avg_price'])}")
        print(f"  量 {n(rt['volume_wanshou'])}万手  额 {n(rt['amount_yi'])}亿  换手 {n(rt['turnover_pct'])}%  "
              f"量比 {n(rt['vol_ratio'])}  振幅 {n(rt['amplitude_pct'])}%")
        print(f"  内盘 {n(rt['inner_vol'])}  外盘 {n(rt['outer_vol'])}  委比 {n(rt['entrust_rate'])}%  "
              f"涨停 {n(rt['limit_up'])} 跌停 {n(rt['limit_down'])}")
        print(f"  PE(TTM) {n(rt['pe_ttm'])}  PB {n(rt['pb'])}  PS {n(rt['ps'])}  "
              f"总市值 {n(rt['total_mv'])}亿  流通 {n(rt['negotiable_mv'])}亿")
        print(f"  买档 {rt.get('bid_grp') or '-'}   卖档 {rt.get('offer_grp') or '-'}")

    print(f"\n--- 近 {len(o['kline'])} 日日线 (来源 {o['kline_source']}) ---")
    print(f"{'日期':<12}{'收盘':>8}{'涨跌%':>8}{'最高':>8}{'最低':>8}{'均价':>8}{'量万手':>9}{'换手%':>8}{'量比':>7}")
    for r in o["kline"]:
        print(f"{r['date']:<12}{r['close']:>8.2f}{n(r['change_pct']):>8}{r['high']:>8.2f}{r['low']:>8.2f}"
              f"{n(r['avg_price']):>8}{r['volume_wanshou']:>9.1f}{n(r['turnover_pct']):>8}{n(r['vol_ratio']):>7}")

    print(f"\n--- 资金流 (来源 {o['flow_source']}, 口径校验 {v(o['flow_verified'])}) ---")
    print(f"{'日期':<12}{'主力万':>10}{'特大万':>10}{'大单万':>10}{'中单万':>10}{'小单万':>10}{'涨跌%':>8}")
    for r in o["flow"]:
        print(f"{r['date']:<12}{r['main_wan']:>10,.0f}{n(r['super_wan']):>10}{n(r['big_wan']):>10}"
              f"{n(r['mid_wan']):>10}{n(r['small_wan']):>10}{n(r['change_pct']):>8}")

    if o["tick"]:
        print(f"\n--- 恒生分时(最近 {len(o['tick'])} 分钟) 含均价 ---")
        for t in o["tick"][::3]:
            print(f"  {t['time']}  价 {n(t['price'])}  均价 {n(t['avg_price'])}  累计量 {n(t['cum_volume_wanshou'])}万手")
    if o["minute"]:
        mn = o["minute"]
        print(f"\n--- {mn['source']}(全天) 日高 {mn['high']['price']}@{mn['high']['time']} "
              f"(累计量{mn['high']['cum_pct']}%)  日低 {mn['low']['price']}@{mn['low']['time']} "
              f"(累计量{mn['low']['cum_pct']}%) ---")
        print("  " + "  ".join(f"{p['time']}:{p['price']}({p['cum_pct']}%)" for p in mn["points"]))

    if want_events and o["events"]:
        e = o["events"]
        print("\n" + "=" * 86)
        print("--- 事件风险快检 ---")
        if e.get("report_disclosure"):
            print("  [定期报告]")
            for x in e["report_disclosure"]:
                print(f"    {x['type']} 报告期 {x['report_period']}  预约 {x['reserved_date']}  实际 {x['actual_date'] or '-'}")
        if e.get("shareholder_num"):
            print("  [股东户数]")
            for x in e["shareholder_num"][-4:]:
                print(f"    {x['end_date']}  户数 {n(x['holders'],0)}  较上期 {n(x['holders_change'],0)}  "
                      f"户均 {n(x['avg_hold'],0)}  前十大 {n(x['top10_pct'])}%")
        if e.get("restricted_lifting"):
            print("  [限售解禁]")
            for x in e["restricted_lifting"]:
                print(f"    解禁日 {x['float_date']}  {n(x['shares_wanshou'])}万股  占总股本 {n(x['pct_of_total'])}%  {x['type'] or ''}")
        if e.get("change_plan"):
            print("  [增减持计划]")
            for x in e["change_plan"][-4:]:
                print(f"    {x['holder']}  {x['type']}  {x['progress']}  {x['begin']}~{x['end']}  上限 {n(x['pct_of_total'])}%")
        if e.get("key_holder_trade"):
            print("  [重要股东交易]")
            for x in e["key_holder_trade"][-5:]:
                print(f"    {x['end_date']}  {x['holder']}  {x['direction']}  {n(x['shares'],0)}股  均价 {n(x['avg_price'])}  变动后 {n(x['ratio_after'])}%")
        if e.get("performance_forecast"):
            print("  [业绩预告]")
            for x in e["performance_forecast"][-3:]:
                print(f"    {x['report_period']}  {x['type']}  净利 {n(x['min_profit_wan'])}~{n(x['max_profit_wan'])}万  同比 {n(x['min_yoy'])}~{n(x['max_yoy'])}%")
        if e.get("hero_list"):
            print("  [龙虎榜]")
            for x in e["hero_list"][-5:]:
                print(f"    {x['begin']}  {x['reason']}  买入 {n(x['buy_wan'])}万  卖出 {n(x['sell_wan'])}万  净 {n(x['net_wan'])}万")
        if e.get("margin_trade"):
            print("  [融资融券]")
            for x in e["margin_trade"]:
                print(f"    {x['date']}  融资余额 {n(x['finance_balance_yi'])}亿  净买入 {n(x['finance_net_buy_yi'])}亿")
        if e.get("value_analysis"):
            print("  [估值]")
            for x in e["value_analysis"][-3:]:
                print(f"    {x['date']}  PE(TTM) {n(x['pe_ttm'])}  PB {n(x['pb'])}  总市值 {n(x['total_mv'])}亿")
        if e.get("range_quote"):
            rq = e["range_quote"]
            print(f"  [区间统计] {rq['begin']}~{rq['end']}  区间涨跌 {n(rq['change_pct'])}%  "
                  f"最大回撤 {n(rq['max_drawdown_pct'])}%  涨停 {n(rq['limitup_days'],0)}天  "
                  f"跌停 {n(rq['limitdown_days'],0)}天  日均换手 {n(rq['turnover_perday_pct'])}%")
        if e.get("real_time_flow"):
            rf = e["real_time_flow"]
            print(f"  [实时资金] 主力净额 {n(rf['main_net_in'])}万  散户净额 {n(rf['retail_net_in'])}万  "
                  f"5日主力 {n(rf['main5_net_in'])}万  10日主力 {n(rf['main10_net_in'])}万  "
                  f"主力连续流入 {n(rf['continues_days'],0)}天")
        if e.get("belong_concept"):
            print("  [所属概念] " + "、".join(x["concept"] for x in e["belong_concept"] if x["concept"]))

    if o["notes"]:
        print("\n⚠️ " + " | ".join(o["notes"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stock")
    ap.add_argument("--days", type=int, default=12)
    ap.add_argument("--events", action="store_true", help="追加事件风险快检")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    code, hs_code, mkt = resolve(a.stock)
    if not code:
        print(f"❌ 无法解析: {a.stock}")
        return 1
    out = fetch_all(code, hs_code, mkt, a.days, a.events)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    else:
        print_human(out, a.events)
    return 0


if __name__ == "__main__":
    sys.exit(main())
