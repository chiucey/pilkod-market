#!/usr/bin/env python3
"""
A 股实时行情 — 东方财富单股票接口（并发）为主 + 腾讯兜底
主用：东方财富（字段清晰，单位明确）
备用：腾讯财经
"""

import sys, json, argparse, urllib.request, urllib.error
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

HDR_EM = {"User-Agent": "Mozilla/5.0", "Referer": "http://quote.eastmoney.com/"}
HDR_TX = {"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"}

# ══════════════════════════════════════════════════════════════════════════════
# 工具
# ══════════════════════════════════════════════════════════════════════════════
def _get(url, hdr, timeout=12):
    req = urllib.request.Request(url, headers=hdr)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))

def _fval(v, default=None):
    try: return float(v)
    except: return default

def _fmt_yuan(v):
    """东方财富成交额/市值为元"""
    if not v: return "—"
    try: v = float(v)
    except: return str(v)
    if v >= 1e8: return f"{v/1e8:.2f}亿"
    if v >= 1e4: return f"{v/1e4:.2f}万"
    return f"{v:.2f}"

# ══════════════════════════════════════════════════════════════════════════════
# 东方财富单股票接口（并发安全）
# 字段: f43=最新价(分) f44=涨跌幅% f45=涨跌额(分)
#       f46=今开(分)    f57=代码  f58=名称  f60=昨收(分)
#       f47=成交额(元) f48=换手率%
#       f116=总市值(元) f117=流通市值(元)
#       f162=市盈率(动态) f167=市盈率TTM f168=市净率
# ══════════════════════════════════════════════════════════════════════════════
def _fetch_one_em(code):
    code = str(code).zfill(6)
    secid = ("1." + code) if code[0] in ("6", "9") else ("0." + code)
    try:
        q = _get(
            f"http://push2.eastmoney.com/api/qt/stock/get"
            f"?secid={secid}"
            f"&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f116,f117,f162,f167,f168"
            f"&ut=fa5fd1943c7b386f172d6893dbfba10b",
            HDR_EM
        ).get("data", {})
        if not q: return {"error": "未找到", "code": code}
        price_raw = _fval(q.get("f43"), 0)
        pre_raw = _fval(q.get("f60"), 0)
        price = round(price_raw / 100, 2) if price_raw else None
        pre_close = round(pre_raw / 100, 2) if pre_raw else None
        # 从价格和昨收推算涨跌幅（f44/f45在模拟环境不可信，直接算）
        if price and pre_close and pre_close != 0:
            chg = round(price - pre_close, 2)
            pct_chg = round((price - pre_close) / pre_close * 100, 2)
        else:
            chg = None; pct_chg = None
        # 成交额：东方财富f47单位为万元
        turnover_raw = _fval(q.get("f47"), 0)
        turnover = round(turnover_raw * 1e4, 2) if turnover_raw else None
        return dict(
            code=code,
            name=q.get("f58", code),
            price=price,
            pct_chg=pct_chg,
            chg=chg,
            open=round(_fval(q.get("f46"), 0)/100, 2) or None,
            pre_close=pre_close,
            turnover=turnover,
            turnover_rate=_fval(q.get("f48")),
            pe=_fval(q.get("f167")) or _fval(q.get("f162")),
            pb=_fval(q.get("f168")),
            total_mv=_fval(q.get("f116")),
            float_mv=_fval(q.get("f117")),
            source="东方财富",
        )
    except Exception as e:
        return {"error": str(e), "code": code}

def fetch_em_batch(codes, workers=8):
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_fetch_one_em, c): str(c).zfill(6) for c in codes}
        for f in as_completed(futures):
            cd = futures[f]
            try: results[cd] = f.result()
            except: results[cd] = {"error": "线程异常", "code": cd}
    return results

# ══════════════════════════════════════════════════════════════════════════════
# 腾讯财经（备用）
# [1]=名称 [3]=现价 [4]=昨收 [5]=今开 [6]=成交量(手)
# [31]=涨跌额 [32]=涨跌幅% [37]=成交额(万元)→转元 [38]=换手率%
# [39]=市盈率TTM [44]=总市值(亿元)→转元 [46]=市净率 [47]=流通市值(亿元)→转元
# ══════════════════════════════════════════════════════════════════════════════
TX = dict(name=1, price=3, pre_close=4, open=5, vol=6,
          chg=31, pct_chg=32, turnover=37, turnover_rate=38,
          pe=39, total_mv=44, pb=46, float_mv=47)

def _fetch_one_tx(code):
    code = str(code).zfill(6)
    prefix = "sh" if code[0] in ("6","9") else "sz"
    try:
        req = urllib.request.Request(f"https://qt.gtimg.cn/q={prefix}{code}", headers=HDR_TX)
        raw = urllib.request.urlopen(req, timeout=12).read().decode("gbk", errors="replace")
    except Exception as e:
        return {"error": str(e), "code": code}

    for line in raw.strip().split("\n"):
        if "=" not in line: continue
        _, val = line.split("=", 1)
        v = val.strip().strip('"').split("~")
        def g(i, d=None):
            try: x=v[i]; return None if x in ("","None") else x
            except: return d
        price = _fval(g(TX["price"]))
        if price is None: continue
        tw = _fval(g(TX["turnover"]))  # 万元
        tm = _fval(g(TX["total_mv"]))   # 亿元
        fm = _fval(g(TX["float_mv"]))   # 亿元
        return dict(
            code=code, name=g(TX["name"], code),
            price=price,
            pre_close=_fval(g(TX["pre_close"])),
            open=_fval(g(TX["open"])),
            chg=_fval(g(TX["chg"])),
            pct_chg=_fval(g(TX["pct_chg"])),
            volume=int(_fval(g(TX["vol"]), 0) or 0),
            turnover=round(tw * 1e4, 2) if tw else None,   # 万元→元
            turnover_rate=_fval(g(TX["turnover_rate"])),
            pe=_fval(g(TX["pe"])),
            pb=_fval(g(TX["pb"])),
            total_mv=round(tm * 1e8, 2) if tm else None,   # 亿元→元
            float_mv=round(fm * 1e8, 2) if fm else None,
            source="腾讯财经",
        )
    return {"error": "解析失败", "code": code}

def fetch_tx_batch(codes, workers=8):
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_fetch_one_tx, c): str(c).zfill(6) for c in codes}
        for f in as_completed(futures):
            cd = futures[f]
            try: results[cd] = f.result()
            except: results[cd] = {"error": "线程异常", "code": cd}
    return results

# ══════════════════════════════════════════════════════════════════════════════
# 名称搜索（东方财富快照，按关键词筛选前limit条）
# ══════════════════════════════════════════════════════════════════════════════
def search_em(keyword, limit=10):
    """并发验证候选代码 + 名称匹配（搜索兜底方案）"""
    import urllib.parse
    # 尝试东方财富搜索接口（多个备用域名）
    for domain in [
        "https://search-api-web.eastmoney.com/search/jsonp",
        "http://search-api-web.eastmoney.com/search/jsonp",
    ]:
        try:
            params = urllib.parse.quote(json.dumps({
                "keyWord": keyword, "type": [14], "client": "web",
                "clientType": "pc", "clientVersion": "curr", "count": limit
            }, ensure_ascii=False))
            url = f"{domain}?param={params}"
            raw = _get(url, {"User-Agent":"Mozilla/5.0","Referer":"https://www.eastmoney.com/"}, timeout=8)
            # JSONP 回调格式: callback([...])
            text = raw if isinstance(raw, str) else str(raw)
            for prefix in ["(", "["]:
                if prefix in text:
                    data = json.loads(text[text.index(prefix):].strip("() \n\r\t"))
                    break
            items = data if isinstance(data, list) else data.get("result", {}).get("data", [])
            if items:
                res = []
                for it in items:
                    if isinstance(it, dict):
                        cd = str(it.get("code") or it.get("Code") or "").zfill(6)
                        res.append(dict(code=cd, name=it.get("name") or it.get("zwsc") or cd,
                                       price=it.get("最新价") or it.get("price"),
                                       pct_chg=it.get("涨跌幅") or it.get("zdf")))
                if res:
                    return {"keyword":keyword,"count":len(res),"results":res[:limit],
                            "query_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        except Exception:
            pass
    # 搜索兜底：直接返回提示
    return {
        "keyword": keyword, "count": 0, "results": [],
        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "error": f'未找到含"{keyword}"的股票，请确认名称或直接输入6位代码查询'
    }

# ══════════════════════════════════════════════════════════════════════════════
# 双源核心
# ══════════════════════════════════════════════════════════════════════════════
def query(codes):
    codes = [str(c).zfill(6) for c in codes]
    final, failed = {}, set()
    src_label = None

    # 步骤1：东财主源（并发）
    em = fetch_em_batch(codes)
    for cd, r in em.items():
        if isinstance(r, dict) and "error" not in r:
            final[cd] = r
        else:
            failed.add(cd)
    if final: src_label = "东方财富"

    # 步骤2：腾讯兜底（主源失败部分，并发）
    if failed:
        tx = fetch_tx_batch(list(failed))
        filled = 0
        for cd, r in tx.items():
            if isinstance(r, dict) and "error" not in r:
                final[cd] = r; filled += 1
        if filled:
            src_label = f"东方财富（{filled}条由腾讯财经兜底）"

    # 步骤3：全挂
    if not final:
        return {
            "results": [], "errors": [{"fatal": True,
                "msg": "两个数据源均无法获取，请检查网络后重试。"}],
            "source_used": None,
            "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    results = [{**r, "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
               for _, r in final.items()]
    return {
        "count": len(results), "results": results,
        "errors": [{"code": cd, "error": em.get(cd, {}).get("error", "未知")}
                   for cd in failed] if failed else [],
        "warnings": [], "source_used": src_label,
        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

# ══════════════════════════════════════════════════════════════════════════════
# 格式化
# ══════════════════════════════════════════════════════════════════════════════
def _arrow(pct):
    if isinstance(pct,(int,float)):
        return "🔴" if pct<0 else "🟢" if pct>0 else "⚪"
    return "⚪"

def _p(v, fmt="%s", null="—"): return (fmt%v) if isinstance(v,(int,float)) and v is not None else null

def format_output(out):
    fatal = [e for e in out.get("errors",[]) if e.get("fatal")]
    if fatal: return f"❌ {fatal[0]['msg']}\n   {out.get('query_time','')}"
    lines = [f"📡 {out.get('source_used','未知')} | {out.get('query_time','')}\n"]
    for s in out.get("results",[]):
        pct = s.get("pct_chg")
        lines += [
            f"{_arrow(pct)} {s['code']} {s['name']}",
            f"   最新价: {_p(s.get('price'),'%.2f')}  "
            f"涨跌幅: {_p(pct,'%+.2f%%')}  "
            f"涨跌额: {_p(s.get('chg'),'%+.2f')}",
            f"   今开: {_p(s.get('open'),'%.2f')}  "
            f"昨收: {_p(s.get('pre_close'),'%.2f')}",
        ]
        if s.get("turnover"):
            lines.append(f"   成交额: {_fmt_yuan(s['turnover'])}")
        if isinstance(s.get("turnover_rate"),(int,float)) and s["turnover_rate"] != 0:
            lines.append(f"   换手率: {s['turnover_rate']:.2f}%")
        pe_v, pb_v = s.get("pe"), s.get("pb")
        if isinstance(pe_v,(int,float)) and pe_v:
            lines.append(f"   市盈率(动态): {round(pe_v,2)}  市净率: {round(pb_v or 0,2)}")
        mv = s.get("total_mv")
        if isinstance(mv,(int,float)) and mv:
            lines.append(f"   总市值: {_fmt_yuan(mv)}  流通市值: {_fmt_yuan(s.get('float_mv'))}")
        lines.append("")
    errs = [e for e in out.get("errors",[]) if not e.get("fatal")]
    if errs:
        lines.append("⚠️ 部分查询失败：")
        for e in errs: lines.append(f"   {e.get('code','')}: {e.get('error','')}")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="A 股实时行情（东方财富主源+腾讯兜底）")
    p.add_argument("codes", nargs="*", help="股票代码")
    p.add_argument("-s","--search", type=str, help="名称搜索")
    p.add_argument("-l","--limit",  type=int, default=10)
    p.add_argument("-f","--format", choices=["json","text"], default="text")
    args = p.parse_args()
    if args.search: out = search_em(args.search, args.limit)
    elif args.codes: out = query(args.codes)
    else:
        print("用法:  query_stock.py 600519              # 单股票")
        print("       query_stock.py 600519 000858     # 批量")
        print("       query_stock.py -s 茅台           # 搜索")
        print("       query_stock.py -f json 600519   # JSON")
        sys.exit(0)
    if args.format == "json":
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if out.get("errors") and all(e.get("fatal") for e in out["errors"]) and not out.get("results"):
            print(f"❌ {out['errors'][0]['msg']}")
        else: print(format_output(out))
