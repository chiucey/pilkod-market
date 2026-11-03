"""
fetch_api.py v3 — 限速版
========================
Tushare API 调用频率：200次/分钟

限速策略：
  • TokenBucket：滑动窗口60秒，不超过200次
  • 批量优先：能用批量接口就不用单只接口
  • 指数退避：遇限速自动等一轮窗口

每日配额 100,000 次：
  • 持仓13只：约70次/天（几乎零消耗）
  • 全量扫描200只：约1010次/天（占1%配额）

调用顺序（持仓优先）：
  Step 1  拉股票列表        → 5次
  Step 2  批量日线（全部）   → 1次（all in one call）
  Step 3  北向持股（持仓）   → 13次
  Step 4  资金流向（持仓）   → 13次
  Step 5  融资余额（持仓）   → 13次
  Step 6  券商评级（持仓）   → 13次
  Step 7  全量扫描日线      → 1次（用于筛选）
  ─────────────────────────────
  总计持仓13只：58次  |  全量扫描+持仓：~1068次
"""

import os, json, logging, sqlite3, time, threading
from datetime import datetime, timedelta
from urllib import request, error

TOKEN = "a78cbdbee9fe610ed43aeefb9d5355445f7cbf3da72f20323f443b5e"
TUSHARE_API = "https://api.tushare.pro"
DB_PATH = "/workspace/stock-scout/data/scout.db"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────
# TokenBucket 限速器（滑动窗口，200次/分钟）
# ───────────────────────────────────────────────

class TokenBucket:
    """
    滑动窗口限速：
      • capacity = 200（每分钟上限）
      • refill_rate = 200/60 ≈ 3.33次/秒
      • 线程安全
    """
    def __init__(self, capacity: int = 200, window_secs: float = 60.0):
        self.capacity = capacity
        self.window = window_secs
        self._lock = threading.Lock()
        self._tokens = capacity
        self._last_refill = time.monotonic()

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self._last_refill
        if elapsed >= self.window:
            self._tokens = self.capacity
            self._last_refill = now

    def acquire(self, n: int = 1) -> bool:
        """尝试获取 n 个 token，阻塞直到成功或超时（30s）"""
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            with self._lock:
                self._refill()
                if self._tokens >= n:
                    self._tokens -= n
                    return True
                # 还剩多少token，等多久能补满
                needed = n - self._tokens
                wait_time = (needed / (self.capacity / self.window)) + 0.1
                remaining = self.capacity - self._tokens
                sleep_time = (remaining / (self.capacity / self.window))
            time.sleep(min(sleep_time, deadline - time.monotonic()))
        return False

_bucket = TokenBucket(capacity=200, window_secs=60.0)

# ───────────────────────────────────────────────
# API 调用器
# ───────────────────────────────────────────────

def call(api_name: str, params: dict, fields: str = "") -> dict:
    """
    带限速 + 退避的 Tushare API 调用。
    失败自动重试3次，每次等一个完整窗口。
    """
    # 构造 payload（注意：ts_code 多值时用逗号分隔）
    payload = json.dumps({
        "api_name": api_name,
        "token": TOKEN,
        "params": params,
        "fields": fields
    }).encode()

    for attempt in range(4):
        # 申请 token（阻塞直到有额度）
        ok = _bucket.acquire(1)
        if not ok:
            logger.warning(f"[{api_name}] 等待token超时，跳过")
            return {}

        try:
            req = request.Request(
                TUSHARE_API,
                data=payload,
                headers={"Content-Type": "application/json", "User-Agent": "StockScout/1.0"}
            )
            with request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
                result = json.loads(raw.decode())

            # 成功
            if result.get("code") == 0:
                return result
            # 限速重试
            msg = str(result.get("msg", ""))
            if "超限" in msg or "limit" in msg.lower() or result.get("code") in [-1, 4012]:
                logger.warning(f"[{api_name}] 触发限速，等待一轮窗口... ({attempt+1}/3)")
                time.sleep(62)   # 等一个完整60秒窗口
                continue
            # 其他错误
            logger.debug(f"[{api_name}] API错误: {result.get('msg')}")
            return {}

        except error.HTTPError as e:
            if e.code == 429:
                logger.warning(f"[{api_name}] HTTP 429，等60秒... ({attempt+1}/3)")
                time.sleep(62)
                continue
            logger.warning(f"[{api_name}] HTTP {e.code}: {e.reason}")
            return {}
        except Exception as e:
            logger.warning(f"[{api_name}] 请求异常: {e}")
            return {}

    return {}

def rows(result: dict) -> list:
    """从API结果提取行列表"""
    if not result or result.get("code") != 0:
        return []
    data = result.get("data") or {}
    items = data.get("items") or []
    fields = data.get("fields") or []
    return [dict(zip(fields, item)) for item in items]

def sf(v, default=0.0):
    try:
        return float(v)
    except:
        return default

# ───────────────────────────────────────────────
# 日期工具
# ───────────────────────────────────────────────

def prev_trade_date() -> str:
    """前一交易日 YYYYMMDD"""
    d = datetime.now()
    if d.weekday() >= 5:
        d -= timedelta(days=d.weekday() - 4)
    return (d - timedelta(days=1)).strftime("%Y%m%d")

# ───────────────────────────────────────────────
# 数据获取
# ───────────────────────────────────────────────

def get_tech_stocks(limit: int = 300) -> list[dict]:
    """获取科技行业股票列表（约5次调用）"""
    logger.info("获取股票列表...")
    result = call("stock_basic", {"list_status": "L"},
                  "ts_code,symbol,name,industry,market")
    all_stocks = rows(result)
    if not all_stocks:
        return []

    TECH_KW = [
        "电子","计算机","通信","传媒","机械设备","国防军工","汽车","医药生物",
        "电力设备","有色金属","半导体","元件","光学光电子","消费电子","计算机设备",
        "IT服务","软件开发","互联网电商","通信设备","通信服务","广告营销",
        "影视院线","游戏","出版","航空装备","地面兵装","医药商业","医疗器械",
        "化学制药","中药","生物制品","医疗服务","通用设备","专用设备",
        "电机","电气自动化设备","电池","风电设备","光伏设备","军工电子"
    ]
    stocks = [
        {"ts_code": s.get("ts_code",""), "name": s.get("name",""), "industry": s.get("industry","")}
        for s in all_stocks
        if any(kw in str(s.get("industry","")) for kw in TECH_KW)
    ]
    logger.info(f"科技股共 {len(stocks)} 只，截取前 {limit} 只")
    return stocks[:limit]


def batch_daily(trade_date: str) -> dict:
    """
    批量日线（一次调用拿全部股票价格）
    Tushare 支持 ts_code 用逗号分隔批量查询
    """
    result = call("daily",
                  {"trade_date": trade_date},
                  "ts_code,trade_date,close,pct_chg,turnover_rate,amount")
    data = rows(result)
    return {d.get("ts_code",""): d for d in data if d.get("ts_code")}


def get_northbound(ts_code: str, trade_date: str) -> dict:
    """北向持股（沪深港通）"""
    result = call("hk_hold",
                  {"ts_code": ts_code, "trade_date": trade_date},
                  "ts_code,trade_date,hold_ratio,close")
    data = rows(result)
    return data[0] if data else {}


def get_moneyflow(ts_code: str, trade_date: str) -> dict:
    """资金流向"""
    result = call("moneyflow",
                  {"ts_code": ts_code, "trade_date": trade_date},
                  "ts_code,trade_date,net_mf_amt,large_net_amt,pct_change")
    data = rows(result)
    return data[0] if data else {}


def get_margin(ts_code: str, trade_date: str) -> dict:
    """融资融券"""
    result = call("margin",
                  {"ts_code": ts_code, "trade_date": trade_date},
                  "ts_code,trade_date,balance,pbuyl_amt")
    data = rows(result)
    return data[0] if data else {}


def get_broker(ts_code: str) -> dict:
    """券商评级（取最新月度）"""
    result = call("broker_recommend",
                  {"ts_code": ts_code},
                  "ts_code,month,mean_rating,target_price,count")
    data = rows(result)
    if data:
        latest = sorted(data, key=lambda x: str(x.get("month","")), reverse=True)
        return latest[0]
    return {}

def get_holder_trade(ts_code: str, trade_date: str) -> dict:
    """股东增减持（近30日）"""
    start = (datetime.now() - timedelta(days=35)).strftime("%Y%m%d")
    result = call("stk_holdertrade",
                  {"ts_code": ts_code, "start_date": start, "end_date": trade_date},
                  "ts_code,trade_date,action,vol")
    data = rows(result)
    if not data:
        return {}
    buy_vol = sum(sf(r.get("vol")) for r in data
                  if "增持" in str(r.get("action","")))
    sell_vol = sum(sf(r.get("vol")) for r in data
                    if "减持" in str(r.get("action","")))
    if buy_vol > sell_vol * 1.5:
        direction = "BUYING"
    elif sell_vol > buy_vol * 1.5:
        direction = "SELLING"
    else:
        direction = "NEUTRAL"
    return {"direction": direction, "buy_vol": buy_vol, "sell_vol": sell_vol}


# ───────────────────────────────────────────────
# 评分引擎（完整版，直接内联）
# ───────────────────────────────────────────────

W = {"nb": 0.25, "mf": 0.25, "mg": 0.15, "tc": 0.20, "br": 0.15}

def score_stock(s: dict) -> dict:
    nb = min(100, s["northbound_pct"] * 4
             + (20 if s["northbound_pct"] > 10 else 0)
             + (20 if s["northbound_pct"] > 5 else 0))

    large = s["moneyflow_large"]
    mf_base = 50 + (15 if large > 10000 else 10 if large > 5000 else 5 if large > 0 else 0)
    mf_base += (-20 if large < -10000 else -10 if large < -5000 else 0)
    mf = max(0, min(100, mf_base))

    mc = s["margin_change_pct"]
    mg = 50 + (15 if mc < -30 else 10 if mc < -20 else 5 if mc < -10 else 0)
    mg += (-25 if mc > 30 else -15 if mc > 20 else -8 if mc > 10 else 0)
    mg = max(0, min(100, mg))

    ch = s["change_pct"]; tr = s["turnover_rate"]; td = s.get("trend_5d", 0)
    tc = 50
    tc += (15 if 2 <= ch <= 6 else 8 if 6 < ch <= 9 else -10 if ch > 9
           else 5 if -8 <= ch < -5 else -15 if ch < -8 else 0)
    tc += (10 if tr > 10 else 7 if tr > 5 else 3 if tr > 2 else -5)
    tc += (8 if td > 5 else 4 if td > 0 else -8 if td < -5 else -4)
    tc = max(0, min(100, tc))

    br_raw = s["broker_rating"]
    br = 50
    br += (25 if br_raw >= 4.5 else 18 if br_raw >= 4.0
           else 10 if br_raw >= 3.5 else 5 if br_raw >= 3.0 else 0)
    tg = s.get("target_gap", 0)
    br += (15 if tg >= 50 else 10 if tg >= 30 else 5 if tg >= 15 else -15 if tg < -20 else 0)
    br = max(0, min(100, br))

    composite = round(nb*W["nb"] + mf*W["mf"] + mg*W["mg"] + tc*W["tc"] + br*W["br"])

    bullish = (s["northbound_pct"] > 5) + (s["moneyflow_net"] > 5000) + \
              (s["margin_change_pct"] < -20) + (br_raw >= 4.0) + \
              (ch > 2 and tr > 3)
    bearish = (s["margin_change_pct"] > 30) + (s["moneyflow_net"] < -5000) + \
              (ch < -5) + (0 < br_raw < 3.0) + (s.get("holder_direction") == "SELLING")

    if bullish >= 4 and bearish <= 1: sig = "资金流入"
    elif bullish >= 3 and s["northbound_pct"] > 3: sig = "北向加码"
    elif bullish >= 3: sig = "启动信号"
    elif bearish >= 4: sig = "高位警示"
    elif bullish <= 1 and bearish >= 3: sig = "下降趋势"
    elif s["margin_change_pct"] > 30: sig = "高位警示"
    else: sig = "观望"

    phase_map = {"资金流入":"🟢","北向加码":"🔵","启动信号":"🟡","高位警示":"🟠","下降趋势":"🔴","观望":"⚪"}
    s.update({
        "score": composite,
        "signal_type": sig,
        "phase": f"{phase_map.get(sig,'⚪')} {sig}",
        "_nb": nb, "_mf": mf, "_mg": mg, "_tc": tc, "_br": br,
    })
    return s

# ───────────────────────────────────────────────
# SQLite 写入
# ───────────────────────────────────────────────

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS stocks_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL, ts_code TEXT NOT NULL, name TEXT,
            score INTEGER, signal_type TEXT, phase TEXT,
            northbound_pct REAL, margin_change_pct REAL,
            moneyflow_net REAL, broker_rating REAL,
            target_gap_pct REAL, price REAL, change_pct REAL,
            turnover_rate REAL,
            UNIQUE(date, ts_code)
        )
    """)
    conn.commit(); conn.close()
    logger.info(f"DB: {DB_PATH}")


def save_signal(sig: dict, today: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT OR REPLACE INTO stocks_daily
            (date,ts_code,name,score,signal_type,phase,northbound_pct,
             margin_change_pct,moneyflow_net,broker_rating,target_gap_pct,
             price,change_pct,turnover_rate)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            today, sig["ts_code"], sig.get("name",""), sig["score"],
            sig["signal_type"], sig["phase"], sig.get("northbound_pct",0),
            sig.get("margin_change_pct",0), sig.get("moneyflow_net",0),
            sig.get("broker_rating",0), sig.get("target_gap",0),
            sig.get("price",0), sig.get("change_pct",0), sig.get("turnover_rate",0)
        ))
        conn.commit()
    except Exception as e:
        logger.debug(f"DB: {e}")
    conn.close()

# ───────────────────────────────────────────────
# 升爷持仓列表
# ───────────────────────────────────────────────

SHENGYE = [
    {"ts_code": "510500.SH", "name": "中证500ETF"},
    {"ts_code": "588080.SH", "name": "科创50ETF"},
    {"ts_code": "600410.SH", "name": "华胜天成"},
    {"ts_code": "600497.SH", "name": "驰宏锌锗"},
    {"ts_code": "601618.SH", "name": "中国中冶"},
    {"ts_code": "601788.SH", "name": "光大证券"},
    {"ts_code": "603501.SH", "name": "豪威集团"},
    {"ts_code": "000538.SZ", "name": "云南白药"},
    {"ts_code": "002230.SZ", "name": "科大讯飞"},
    {"ts_code": "002950.SZ", "name": "奥美医疗"},
    {"ts_code": "300172.SZ", "name": "中电环保"},
    # 港股暂不查（接口不同）
]

# ───────────────────────────────────────────────
# 主流程
# ───────────────────────────────────────────────

def run():
    init_db()
    today = prev_trade_date()
    logger.info(f"=" * 55)
    logger.info(f"Stock Scout A股 v3 — 限速版 200次/分钟")
    logger.info(f"查询日期: {today}")
    logger.info(f"=" * 55)

    # Step 1: 获取科技股列表（~5次调用）
    all_stocks = get_tech_stocks(limit=200)
    if not all_stocks:
        logger.error("股票列表为空，退出"); return

    all_codes = [s["ts_code"] for s in all_stocks]
    shengye_codes = [s["ts_code"] for s in SHENGYE]
    logger.info(f"科技股: {len(all_codes)} 只 | 升爷持仓: {len(SHENGYE)} 只")

    # Step 2: 批量日线，一次调用拿全部（~1次调用）
    logger.info("批量日线数据（全部科技股）...")
    daily_all = batch_daily(today)
    logger.info(f"日线数据: {len(daily_all)} 只")

    # Step 3-7: 逐只查持仓的5个维度
    logger.info(f"逐只查询持仓维度（{len(SHENGYE)}只 × 5接口 = ~{len(SHENGYE)*5}次）...")
    results = []
    api_calls = 0

    for stock in SHENGYE:
        ts = stock["ts_code"]
        name = stock["name"]
        d = daily_all.get(ts, {})

        price    = sf(d.get("close"))
        change_pct = sf(d.get("pct_chg"))
        turnover  = sf(d.get("turnover_rate"))

        # 北向持股
        nb = get_northbound(ts, today)
        nb_pct = sf(nb.get("hold_ratio"))
        nb_price = sf(nb.get("close"))
        if nb_price > 0: price = nb_price
        api_calls += 1

        # 资金流向
        mf = get_moneyflow(ts, today)
        mf_net = sf(mf.get("net_mf_amt"))
        mf_large = sf(mf.get("large_net_amt"))
        api_calls += 1

        # 融资余额
        mg = get_margin(ts, today)
        mg_bal = sf(mg.get("balance"))
        mg_prev = sf(mg.get("pbuyl_amt"))
        mg_change = ((mg_bal - mg_prev) / mg_prev * 100) if mg_prev > 0 else 0.0
        api_calls += 1

        # 券商评级
        br = get_broker(ts)
        br_rating = sf(br.get("mean_rating"))
        br_target = sf(br.get("target_price"))
        br_gap = ((br_target - price) / price * 100) if price > 0 and br_target > 0 else 0.0
        api_calls += 1

        # 股东增减持
        ht = get_holder_trade(ts, today)
        holder_dir = ht.get("direction", "NEUTRAL")
        api_calls += 1

        s = {
            "ts_code": ts, "name": name,
            "price": price, "change_pct": change_pct,
            "turnover_rate": turnover,
            "northbound_pct": nb_pct,
            "moneyflow_net": mf_net, "moneyflow_large": mf_large,
            "margin_change_pct": mg_change,
            "broker_rating": br_rating, "target_gap": br_gap,
            "holder_direction": holder_dir,
            "trend_5d": 0.0,
        }
        scored = score_stock(s)
        save_signal(scored, today)
        results.append(scored)

        # 日志（每个打完一行，不刷屏）
        bar = "█" * (scored["score"] // 5)
        print(f"  {name:<10} 评分:{scored['score']:3d} 信号:{scored['signal_type']:<6} "
              f"| 价:{price:>7} 涨:{change_pct:>+6.1f}% "
              f"| 北向:{nb_pct:>5.2f}% | 主力:{mf_net:>+10.0f}万 "
              f"| 融资变化:{mg_change:>+7.1f}% | 券商:{br_rating:.1f}")

    results.sort(key=lambda x: x["score"], reverse=True)
    print(f"\n今日API调用次数: ~{api_calls} 次（限额200次/分钟）")

    # 汇总
    print(f"\n{'='*60}")
    print(f"📊 升爷持仓 Scout 结果 | 日期:{today}")
    print(f"{'='*60}")
    print(f"{'排名':>4} {'股票':10} {'评分':6} {'信号':8} {'价格':8} {'涨跌幅':8} {'北向':8} {'主力净流入':12} {'融资变化':10}")
    print("-" * 80)
    for i, r in enumerate(results):
        print(f"  {i+1:2d}  {r['name']:<10} {r['score']:3d}分  {r['signal_type']:<8} "
              f"¥{r['price']:>6.2f}  {r['change_pct']:>+6.2f}%  "
              f"{r['northbound_pct']:>6.2f}%  {r['moneyflow_net']:>+10.0f}万  "
              f"{r['margin_change_pct']:>+8.1f}%")

    top = [r for r in results if r["score"] >= 65]
    print(f"\n{'='*60}")
    print(f"✅ 入围Scout（≥65分）: {len(top)} 只")
    for r in top:
        bar = "█" * (r["score"] // 5)
        print(f"  [{bar:12s}] {r['score']}分 | {r['name']} | {r['signal_type']}")

    logger.info(f"完成！DB已写入: {DB_PATH}")
    return results

if __name__ == "__main__":
    run()
