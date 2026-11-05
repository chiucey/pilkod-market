#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
恒生金融数据库(MiniMax Finance)封装 —— yeren-stock-analysis skill 的**首选数据源**。

数据源优先级:恒生(MiniMax Finance) > 东方财富 > 腾讯行情 > 新浪行情
本模块只负责恒生;降级逻辑见 fetch.py。

调用方式(经 mcode-tools CLI):
    mcode-tools connector call connector__hengsheng__call_api \
        --args '{"api_id":"...","format":"json","params":{...}}'

已验证的字段口径(恒生自带守恒结构,不需要猜):
    特大单 hugenetbuyvalue / 大单 largenetbuyvalue
    主力DDE largenetbuyvaluedde = 特大单 + 大单   ← 这就是"主力净额"
    中单 mediumnetbuyvalue / 小单 smallnetbuyvalue
    守恒:主力DDE + 中单 + 小单 == 0

坑:
  * 6 位代码必须补后缀(000032.SZ / 600760.SH / 300589.SZ / 8xx→.BJ),裸 6 位会被当聚源内码打错标的
  * 返回值是 [{"type":"text","text":"<json字符串>"}],需要二次 json.loads
  * 数值字段是字符串,自行转 float
  * AShareTickQuote 分时**只返回最近 30 分钟**,pageNo>1 为空 → 全天分时轨迹必须另配腾讯接口
  * 复权参数名是 restorationStatus(区间行情)/fuquan(日行情),枚举传中文名
"""
import json
import subprocess
import sys
import time

TOOL = "connector__hengsheng__call_api"
TIMEOUT = 180


def _market_suffix(code):
    """6 位裸代码 → 恒生聚源代码(带交易所后缀)"""
    code = str(code).strip().upper()
    if "." in code:
        return code
    code = code.zfill(6)
    if code[0] == "6":
        return code + ".SH"
    if code[0] in ("8", "4", "9"):
        return code + ".BJ"
    return code + ".SZ"


def hs_call(api_id, params=None, fmt="json", retries=2):
    """调用恒生 API。返回 dict:{'columns':[{en,cn}], 'rows':[...]} 或 None。"""
    args = {"api_id": api_id, "format": fmt, "params": params or {}}
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                ["mcode-tools", "connector", "call", TOOL,
                 "--args", json.dumps(args, ensure_ascii=False)],
                capture_output=True, text=True, timeout=TIMEOUT)
            if r.returncode != 0:
                raise RuntimeError((r.stderr or r.stdout)[-300:])
            payload = json.loads(r.stdout)
            if isinstance(payload, list) and payload:
                t = payload[0].get("text", "")
                t = json.loads(t) if isinstance(t, str) else t
            else:
                t = payload
            data = (t or {}).get("data") or {}
            if not data.get("rows"):
                return {"columns": data.get("columns", []), "rows": []}
            return {"columns": data.get("columns", []), "rows": data["rows"]}
        except Exception as e:
            if attempt < retries:
                time.sleep(2.0)
                continue
            sys.stderr.write("[hengsheng] %s 调用失败: %s\n" % (api_id, e))
            return None
    return None


def _amt(v):
    """金额字段可能是 '11.42亿元' / '1.2万元' / '1234元' 字符串"""
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip()
    num = ""
    for ch in t:
        if ch.isdigit() or ch in ".-":
            num += ch
        else:
            break
    try:
        x = float(num)
    except ValueError:
        return None
    if "亿" in t:
        return x
    if "万" in t:
        return x / 1e4
    return x / 1e8


def _f(v):
    """安全转 float,空值/非数返回 None"""
    if v is None or v == "" or v == "-":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _rows(api_id, params):
    r = hs_call(api_id, params)
    return (r or {}).get("rows", []) or []


# ---------------------------------------------------------------- 行情

def live_quote(code):
    """A股实时行情:价格/均价/五档/内外盘/换手/量比/PE/PB/涨跌停价/市值"""
    rows = _rows("AShareLiveQuote", {"stockObject": [code], "pageSize": 5})
    if not rows:
        return None
    r = rows[0]
    return {
        "name": r.get("stockName"),
        "code": r.get("stockCode"),
        "time": r.get("tradingTimestamp"),
        "status": r.get("tradeStatus"),
        "price": _f(r.get("latestPrice")),
        "prev_close": _f(r.get("prevClosePrice")),
        "open": _f(r.get("openPrice")),
        "high": _f(r.get("highPrice")),
        "low": _f(r.get("lowPrice")),
        "avg_price": _f(r.get("avgPrice")),
        "change_pct": _f(r.get("changePCT")),
        "amplitude_pct": _f(r.get("rangePCT")),
        "turnover_pct": _f(r.get("turnoverRate")),
        "vol_ratio": _f(r.get("volumeRate")),
        "volume_wanshou": _f(r.get("turnoverVolumeLot")),
        "amount_yi": _amt(r.get("turnoverValue")),
        "inner_vol": _f(r.get("buyinVolumeLot")),     # 恒生命名:主动买入=内盘
        "outer_vol": _f(r.get("selloutVolumeLot")),   # 主动卖出=外盘
        "entrust_diff": _f(r.get("entrustDiff")),
        "entrust_rate": _f(r.get("entrustRate")),
        "bid_grp": r.get("bidGrp"),
        "offer_grp": r.get("offerGrp"),
        "limit_up": _f(r.get("limitUpPrice")),
        "limit_down": _f(r.get("limitDownPrice")),
        "pe_ttm": _f(r.get("pettm")),
        "pb": _f(r.get("pblf")),
        "ps": _f(r.get("psttm")),
        "dividend_yield": _f(r.get("dividendratiottm")),
        "negotiable_mv": _f(r.get("negotiableMV")),
        "total_mv": _f(r.get("totalMV")),
        "total_shares": _f(r.get("totalshares")),
        "float_shares": _f(r.get("floatshares")),
        "source": "恒生",
    }


def daily_quote(code, begin, end):
    """股票日行情:开高低收/均价/涨跌幅/振幅/换手率/量比/成交额/笔数/停牌"""
    rows = _rows("StockDailyQuote",
                 {"stockObject": [code], "beginDate": begin, "endDate": end,
                  "pageSize": 500, "fuquan": "不复权"})
    out = []
    for r in rows:
        out.append({
            "date": r.get("tradingday"),
            "open": _f(r.get("openprice")),
            "close": _f(r.get("closeprice")),
            "high": _f(r.get("highprice")),
            "low": _f(r.get("lowprice")),
            "avg_price": _f(r.get("avgprice")),
            "prev_close": _f(r.get("prevcloseprice")),
            "change_pct": _f(r.get("changepct")),
            "amplitude_pct": _f(r.get("rangepct")),
            "turnover_pct": _f(r.get("turnoverrate")),
            "vol_ratio": _f(r.get("volumeRatio")),
            "amount_wan": _f(r.get("turnovervalue")),
            "volume_wanshou": (_f(r.get("turnovervolume")) or 0) / 100.0,  # 万股→万手
            "deals": _f(r.get("turnoverdeals")),
            "suspended": r.get("ifsuspend"),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["date"] or "")
    return out


def cash_flow(code, begin, end):
    """个股资金流向(日频)。主力DDE = 特大单 + 大单,四档守恒。"""
    rows = _rows("AStockCashFlow",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 500})
    out = []
    for r in rows:
        huge = _f(r.get("hugenetbuyvalue")) or 0.0
        large = _f(r.get("largenetbuyvalue")) or 0.0
        mid = _f(r.get("mediumnetbuyvalue")) or 0.0
        small = _f(r.get("smallnetbuyvalue")) or 0.0
        dde = _f(r.get("largenetbuyvaluedde"))
        if dde is None:
            dde = huge + large
        out.append({
            "date": r.get("tradingday"),
            "close": _f(r.get("closeprice")),
            "change_pct": _f(r.get("changepct")),
            "main_wan": dde,                    # 主力净额(大单净额DDE)
            "super_wan": huge,                  # 特大单
            "big_wan": large,                   # 大单
            "mid_wan": mid,                     # 中单
            "small_wan": small,                 # 小单
            "amount_wan": _f(r.get("totalvalue")),
            "dde_ratio_pct": _f(r.get("largenetbuyvaluedderatio")),
            "rising_days": _f(r.get("risingupdays")),
            # 守恒校验:主力DDE + 中单 + 小单 应为 0
            "balance_ok": abs((dde + mid + small)) < max(1.0, abs(dde) * 0.02),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["date"] or "")
    return out


def tick_quote(code, end_time=None):
    """分时(恒生只给最近 30 分钟)。含均价 + 累计成交量。"""
    p = {"stockObject": [code], "pageSize": 240}
    if end_time:
        p["endTime"] = end_time
    rows = _rows("AShareTickQuote", p)
    out = []
    for r in rows:
        out.append({
            "time": r.get("tradingTimestamp"),
            "price": _f(r.get("latestPrice")),
            "avg_price": _f(r.get("avgPrice")),
            "change_pct": _f(r.get("changePCT")),
            "cum_volume_wanshou": _f(r.get("turnoverVolumeLot")),
            "amount": r.get("turnoverValue"),
        })
    return out


def real_time_flow(code):
    """实时资金流:主力净额/散户净额/5日10日主力/主力连续流入天数"""
    rows = _rows("RealStockFundFlow", {"stockObject": [code], "pageSize": 5})
    if not rows:
        return None
    r = rows[0]
    return {
        "time": r.get("tradetime"),
        "main_net_in": _f(r.get("mainNetIn")),
        "retail_net_in": _f(r.get("retailNetIn")),
        "main5_net_in": _f(r.get("main5NetIn")),
        "main10_net_in": _f(r.get("main10NetIn")),
        "retail5_net_in": _f(r.get("retail5NetIn")),
        "retail10_net_in": _f(r.get("retail10NetIn")),
        "continues_days": _f(r.get("continuesInDays")),
        "super_net": _f(r.get("superGrpNetTurnover")),
        "big_net": _f(r.get("largeNetTurnover")),
        "mid_net": _f(r.get("mediumNetTurnover")),
        "small_net": _f(r.get("littleNetTurnover")),
        "source": "恒生",
    }


def range_quote(code, begin, end):
    """区间行情:区间涨跌幅/最大回撤/涨停跌停天数/日均换手"""
    rows = _rows("StockRangeQuotation",
                 {"stockObject": [code], "restorationStatus": "不复权",
                  "beginDate": begin, "endDate": end, "pageSize": 10})
    if not rows:
        return None
    r = rows[0]
    return {
        "begin": r.get("begindate"), "end": r.get("enddate"),
        "change_pct": _f(r.get("changepctbt")),
        "high": _f(r.get("highpricebt")), "low": _f(r.get("lowpricebt")),
        "max_drawdown_pct": _f(r.get("maxdrawdown")),
        "max_drawdown_begin": r.get("maxdrawdownbegindate"),
        "max_drawdown_end": r.get("maxdrawdownenddate"),
        "limitup_days": _f(r.get("limitupdaysbt")),
        "limitdown_days": _f(r.get("limitdwondaysbt")),
        "up_days": _f(r.get("updaysbt")), "down_days": _f(r.get("dwondaysbt")),
        "turnover_pct": _f(r.get("turnoverratebt")),
        "turnover_perday_pct": _f(r.get("turnoverrateperdaybt")),
        "amount_perday_wan": _f(r.get("turnovervalueperdaybt")),
        "source": "恒生",
    }


# ---------------------------------------------------------------- 情绪周期

def limit_up_down(begin, end, market="沪深市场"):
    """市场涨跌停家数(情绪周期五阶段判定)"""
    rows = _rows("MarketLimitUpDownCount",
                 {"secuMarketCode": [market], "beginDate": begin,
                  "endDate": end, "pageSize": 100})
    out = []
    for r in rows:
        up = _f(r.get("upCount")) or 0
        down = _f(r.get("downCount")) or 0
        mem = _f(r.get("memberCount")) or 0
        out.append({
            "date": r.get("tradetime"),
            "up": up, "down": down,
            "flat": _f(r.get("flatCount")),
            "limitup": _f(r.get("uplimitCount")),
            "limitdown": _f(r.get("downlimitCount")),
            "members": mem,
            "up_ratio_pct": round(up / mem * 100, 1) if mem else None,
            "down_ratio_pct": round(down / mem * 100, 1) if mem else None,
            "source": "恒生",
        })
    out.sort(key=lambda x: x["date"] or "")
    return out


def sector_rank(sector_type="概念板块", sort_field="涨跌幅", method="降序", size=30):
    """板块排行(概念/地域/申万行业)"""
    rows = _rows("SectorRank",
                 {"sectorType": sector_type, "sectorSortingField": sort_field,
                  "fieldSortingMethod": method, "pageSize": size})
    out = []
    for r in rows:
        out.append({
            "name": r.get("prodName"), "code": r.get("prodCode"),
            "date": r.get("marketDate"),
            "change_pct": _f(r.get("pxChangeRate")),
            "up_count": _f(r.get("riseCount")),
            "down_count": _f(r.get("fallCount")),
            "limitup": _f(r.get("upLimitCount")),
            "limitdown": _f(r.get("downLimitCount")),
            "turnover_pct": _f(r.get("turnoverRatio")),
            "amount": r.get("businessBalance"),
            "source": "恒生",
        })
    return out


def belong_concept(code):
    """所属概念板块 + 纳入原因(主线五步法第一步"消息级别"的素材)"""
    rows = _rows("StockBelongConcept", {"stockObject": [code], "pageSize": 100})
    out = []
    for r in rows:
        out.append({
            "concept": r.get("conceptname"),
            "indate": r.get("indate"),
            "reason": (r.get("inreason") or "")[:300],
            "source": "恒生",
        })
    return out


# ---------------------------------------------------------------- 事件风险

def report_disclosure(code, begin="2026-01-01", end="2026-12-31"):
    """定期报告预约披露时间"""
    rows = _rows("FinanceReportDisclosure",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 20})
    out = []
    for r in rows:
        out.append({
            "report_period": r.get("reportdate"),
            "type": r.get("datetype"),
            "reserved_date": r.get("reservediscdate"),
            "actual_date": r.get("actualdate"),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["report_period"] or "")
    return out


def shareholder_num(code, begin="2023-01-01", end="2026-12-31"):
    """股东户数 + 较上期增减 + 户均持股"""
    rows = _rows("ShareholderNum",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 20})
    out = []
    for r in rows:
        out.append({
            "end_date": r.get("enddate"),
            "publish_date": r.get("infopubldate"),
            "holders": _f(r.get("shnum")),
            "holders_change": _f(r.get("shnumchange")),
            "avg_hold": _f(r.get("averageholdsum")),
            "avg_hold_change": _f(r.get("averageholdsumchange")),
            "top10_pct": _f(r.get("top10stockholdersamount")),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["end_date"] or "")
    return out


def restricted_lifting(code, begin="2026-01-01", end="2027-12-31"):
    """限售股解禁计划"""
    rows = _rows("RestrictedStockLifting",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 20})
    out = []
    for r in rows:
        out.append({
            "float_date": r.get("startdateforfloating"),
            "shares_wanshou": _f(r.get("newmarketableashares")),
            "pct_of_total": _f(r.get("newmarketableasharespercent")),
            "pct_of_float": _f(r.get("newmarketableasharespercenta")),
            "type": r.get("sourcetype"),
            "publish_date": r.get("infopubldate"),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["float_date"] or "")
    return out


def change_plan(code):
    """增减持计划"""
    rows = _rows("ShareholdingChangePlan", {"stockObject": [code], "pageSize": 20})
    out = []
    for r in rows:
        out.append({
            "holder": r.get("shname"),
            "type": r.get("transferplantype"),
            "progress": r.get("eventprocedure"),
            "begin": r.get("promisebegindate"),
            "end": r.get("promiseenddate"),
            "shares_wanshou": _f(r.get("shareceiling")),
            "pct_of_total": _f(r.get("ratioceiling")),
            "statement": (r.get("promisestatment") or "")[:300],
            "publish_date": r.get("infopubldate"),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["publish_date"] or "")
    return out


def key_holder_trade(code, begin="2025-01-01", end="2026-12-31"):
    """重要股东交易"""
    rows = _rows("KeyHolderTrande",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 30})
    out = []
    for r in rows:
        out.append({
            "holder": r.get("shareholdername"),
            "holder_type": r.get("shareholdertype"),
            "direction": r.get("trandetype"),
            "shares": _f(r.get("changevolume")),
            "avg_price": _f(r.get("avgprice")),
            "close_price": _f(r.get("closeprice")),
            "ratio_after": _f(r.get("holdratioafterchange")),
            "end_date": r.get("enddate"),
            "publish_date": r.get("infopubldate"),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["end_date"] or "")
    return out


def performance_forecast(code, begin="2025-01-01", end="2026-12-31"):
    """业绩预告"""
    rows = _rows("PerformanceForecast",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 10})
    out = []
    for r in rows:
        out.append({
            "report_period": r.get("forcastdate"),
            "type": r.get("forcasttype"),
            "min_profit_wan": _f(r.get("minnetprofit")),
            "max_profit_wan": _f(r.get("maxnetprofit")),
            "min_yoy": _f(r.get("minetprofityoy")),
            "max_yoy": _f(r.get("maxnetprofityoy")),
            "reason": (r.get("forcastreason") or "")[:300],
            "source": "恒生",
        })
    out.sort(key=lambda x: x["report_period"] or "")
    return out


def value_analysis(code, begin, end):
    """估值(PE/PB/PS/市值)"""
    rows = _rows("StockValueAnalysis",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 20})
    out = []
    for r in rows:
        out.append({
            "date": r.get("tradingday"),
            "pe_ttm": _f(r.get("pe")),
            "pb": _f(r.get("pb")),
            "ps": _f(r.get("psttm")),
            "pcf_ttm": _f(r.get("pcfttm")),
            "total_mv": _f(r.get("totalmv")),
            "float_mv": _f(r.get("negotiablemv")),
            "dividend_yield": _f(r.get("dividendratio")),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["date"] or "")
    return out


def hero_list(code, begin, end):
    """龙虎榜(含上榜原因与买卖金额)"""
    rows = _rows("DailyStockHeroDetails",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 20})
    out = []
    for r in rows:
        buy = _f(r.get("abnormalbuysum")) or 0
        sell = _f(r.get("abnormalsalesum")) or 0
        out.append({
            "begin": r.get("begindate"), "end": r.get("enddate"),
            "reason": r.get("rankingreason"),
            "change_pct": _f(r.get("changepct")),
            "buy_wan": buy, "sell_wan": sell, "net_wan": round(buy - sell, 2),
            "turnover_pct": _f(r.get("turnoverrate")),
            "source": "恒生",
        })
    out.sort(key=lambda x: x["begin"] or "")
    return out


def margin_trade(code, begin, end):
    """融资融券"""
    rows = _rows("StockSecuritiesMargin",
                 {"stockObject": [code], "beginDate": begin, "endDate": end, "pageSize": 30})
    out = []
    for r in rows:
        out.append({
            "date": r.get("tradingday"),
            "finance_balance_yi": (_f(r.get("financevalue")) or 0) / 1e8,
            "finance_net_buy_yi": (_f(r.get("financebuynetvalue")) or 0) / 1e8,
            "finance_cost": _f(r.get("financeprice")),
            "security_balance_yi": (_f(r.get("securityvalue")) or 0) / 1e8,
            "source": "恒生",
        })
    out.sort(key=lambda x: x["date"] or "")
    return out


def batch_daily(codes, begin, end):
    """批量日行情:一次拉多只(恒生支持 batch 扇出,返回 CSV 下载链接)"""
    r = hs_call("StockDailyQuote",
                {"stockObject": codes, "beginDate": begin, "endDate": end, "pageSize": 5000})
    return (r or {}).get("rows", [])
