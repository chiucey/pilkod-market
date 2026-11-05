#!/usr/bin/env python3
"""
股票行情收集器 - 增强版
数据来源：
- 新浪财经 K线接口（静态JSON）
- 东方财富 主力资金流向 API
- 东方财富 北向资金 API
- 英为财情 VIX指数
章节：
  一、大盘环境（包含世界局势分析）
  二、自选股行情
  三、量能追踪
  四、技术指标
  五、主力资金（3日/5日/10日）
  六、重要公告
  七、走势研判与操作建议
"""

import subprocess, json, time, sys, os, re
from datetime import datetime, timedelta

# 工作目录（skill 目录）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR  = os.path.dirname(SCRIPT_DIR)
TEMP_DIR   = os.path.join(SKILL_DIR, 'temp')
CONFIG_FILE = os.path.join(SKILL_DIR, 'config', 'stocks.json')
os.makedirs(TEMP_DIR, exist_ok=True)

HEADERS = ['-H', 'Referer: https://finance.sina.com.cn',
           '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36']

def load_config():
    """从 config/stocks.json 加载配置，如果不存在则返回空配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if config.get('stocks') or config.get('indices'):
                return config
    return {
        "stocks": [],
        "indices": [
            {"code": "sh000001", "name": "上证指数"},
            {"code": "sz399001", "name": "深证成指"},
            {"code": "sz399006", "name": "创业板指"}
        ]
    }

def sina_get(url):
    r = subprocess.run(['curl', '-s', url] + HEADERS, capture_output=True)
    return r.stdout.decode('gbk', errors='replace')

def get_kline_raw(code, datalen=90):
    url = (f'https://money.finance.sina.com.cn/quotes_service/api/json_v2.php'
           f'/CN_MarketData.getKLineData?symbol={code}&scale=240&datalen={datalen}')
    try:
        return json.loads(sina_get(url))
    except:
        return []

def get_realtime_list(codes):
    url = f'https://hq.sinajs.cn/rn={int(time.time())}&list={codes}'
    raw = sina_get(url)
    res = {}
    for line in raw.strip().split('\n'):
        if '=' not in line: continue
        fields = line.split('"')[1].split(',')
        if len(fields) < 10: continue
        try:
            res[fields[0]] = {
                'open': float(fields[1]), 'prev': float(fields[2]),
                'price': float(fields[3]), 'high': float(fields[4]),
                'low': float(fields[5]), 'vol': int(float(fields[8])),
                'amt': float(fields[9]), 'date': fields[30],
            }
        except: pass
    return res

# ==================== 世界局势数据获取 ====================

def get_us_market_data():
    """
    获取隔夜美股数据（道琼斯、纳斯达克、标普500）
    """
    result = {}
    try:
        # 获取美股主要指数
        url = f'https://hq.sinajs.cn/rn={int(time.time())}&list=gb_ixic,gb_indu,gb_spi'
        raw = sina_get(url)
        
        for line in raw.strip().split('\n'):
            if '=' not in line: continue
            fields = line.split('"')[1].split(',')
            if len(fields) < 10: continue
            
            symbol = fields[0]
            price = float(fields[1]) if fields[1] else 0
            prev_close = float(fields[4]) if fields[4] else price
            change = price - prev_close
            change_pct = (change / prev_close * 100) if prev_close else 0
            
            if 'IXIC' in symbol:  # 纳斯达克
                result['nasdaq'] = {'price': price, 'change': change, 'pct': change_pct}
            elif 'INDU' in symbol:  # 道琼斯
                result['dow'] = {'price': price, 'change': change, 'pct': change_pct}
            elif 'SPI' in symbol:  # 标普500
                result['sp500'] = {'price': price, 'change': change, 'pct': change_pct}
    except Exception as e:
        pass
    return result

def get_vix_index():
    """
    获取VIX恐慌指数
    """
    try:
        url = 'https://hq.sinajs.cn/rn={}&list=hk_vix'.format(int(time.time()))
        raw = sina_get(url)
        for line in raw.strip().split('\n'):
            if '=' not in line: continue
            fields = line.split('"')[1].split(',')
            if len(fields) > 1:
                vix = float(fields[1]) if fields[1] else 0
                return vix
    except:
        pass
    return None

def get_a50_index():
    """
    获取富时A50夜盘数据
    """
    try:
        url = 'https://hq.sinajs.cn/rn={}&list=hf_CHA50'.format(int(time.time()))
        raw = sina_get(url)
        for line in raw.strip().split('\n'):
            if '=' not in line: continue
            fields = line.split('"')[1].split(',')
            if len(fields) > 1:
                price = float(fields[1]) if fields[1] else 0
                prev = float(fields[3]) if fields[3] else price
                pct = (price - prev) / prev * 100 if prev else 0
                return {'price': price, 'pct': pct}
    except:
        pass
    return None

def get_north_moneyflow():
    """
    获取北向资金数据（沪股通+深股通）
    """
    result = {'hgt': 0, 'sgt': 0, 'total': 0, 'total_amount': 0}
    try:
        # 东方财富北向资金接口
        url = 'https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get'
        params = {
            'lmt': '0', 'klt': '101', 'secid': '1.000001',
            'fields1': 'f1,f2,f3,f7',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65',
            'ut': 'b2884a393a59ad64002292a3e90d46a5',
            '_': str(int(time.time() * 1000)),
        }
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_str}"
        
        r = subprocess.run(
            ['curl', '-s', '-H', 'User-Agent: Mozilla/5.0', '-H', 'Referer: https://data.eastmoney.com/', full_url],
            capture_output=True, timeout=15
        )
        text = r.stdout.decode('utf-8', errors='replace')
        
        # 解析JSONP
        start = text.find('({"')
        if start == -1: start = text.find('({')
        end = text.rfind('})')
        if start != -1 and end != -1:
            json_str = text[start+1:end+1]
            data = json.loads(json_str)
            klines = data.get('data', {}).get('klines', [])
            if klines:
                last_day = klines[-1].split(',')
                if len(last_day) > 5:
                    result['hgt'] = float(last_day[5]) if last_day[5] else 0  # 沪股通
                    result['sgt'] = float(last_day[6]) if last_day[6] else 0  # 深股通
                    result['total'] = result['hgt'] + result['sgt']
    except:
        pass
    return result

# ==================== 主力资金数据 ====================

def get_moneyflow_from_eastmoney(code):
    """
    从东方财富获取个股主力资金流向数据（近10日）
    """
    if code.startswith('sh'):
        secid = f"1.{code[2:]}"
    elif code.startswith('sz'):
        secid = f"0.{code[2:]}"
    else:
        return []
    
    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "lmt": "0", "klt": "101", "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "cb": f"jQuery{int(time.time()*1000)}_{int(time.time()*1000)}",
        "_": str(int(time.time() * 1000)),
    }
    
    query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
    full_url = f"{url}?{query_str}"
    
    r = subprocess.run(
        ['curl', '-s', '-H', 'User-Agent: Mozilla/5.0', '-H', 'Referer: https://data.eastmoney.com/', full_url],
        capture_output=True, timeout=15
    )
    
    try:
        text = r.stdout.decode('utf-8', errors='replace')
        start = text.find('({"')
        if start == -1: start = text.find('({')
        end = text.rfind('})')
        if start == -1 or end == -1: return []
        
        json_str = text[start+1:end+1]
        data = json.loads(json_str)
        klines = data.get('data', {}).get('klines', [])
        
        result = []
        for kline in klines[-10:]:
            parts = kline.split(',')
            if len(parts) >= 15:
                result.append({
                    'date': parts[0],
                    'main_net_flow': float(parts[1]) if parts[1] else 0,
                    'small_net_flow': float(parts[2]) if parts[2] else 0,
                    'medium_net_flow': float(parts[3]) if parts[3] else 0,
                    'big_net_flow': float(parts[4]) if parts[4] else 0,
                    'super_big_net_flow': float(parts[5]) if parts[5] else 0,
                    'main_ratio': float(parts[6]) if parts[6] else 0,
                    'close': float(parts[11]) if parts[11] else 0,
                    'pct_change': float(parts[12]) if parts[12] else 0,
                })
        return result
    except:
        return []

def calc_moneyflow_summary(em_data):
    """
    计算3日/5日/10日主力资金汇总
    """
    summary = {'3d': 0, '5d': 0, '10d': 0}
    if not em_data:
        return summary
    
    # 3日汇总
    summary['3d'] = sum(d.get('main_net_flow', 0) for d in em_data[-3:])
    # 5日汇总
    summary['5d'] = sum(d.get('main_net_flow', 0) for d in em_data[-5:])
    # 10日汇总
    summary['10d'] = sum(d.get('main_net_flow', 0) for d in em_data)
    
    return summary

# ==================== 个股公告信息 ====================

def get_stock_announcements(code):
    """
    获取个股近期重要公告（模拟，实际需要东方财富公告接口）
    返回模拟数据，实际使用中需要接入真实公告API
    """
    # 股票代码转换
    if code.startswith('sh'):
        stock_code = code[2:]
        market = 'SH' if stock_code.startswith('6') else 'SZ'
    elif code.startswith('sz'):
        stock_code = code[2:]
        market = 'SZ'
    else:
        stock_code = code
        market = 'SH'
    
    announcements = []
    try:
        # 东方财富公告接口
        url = f'https://np-anotice-stock.eastmoney.com/api/security/ann'
        params = {
            'sr': '-1',
            'page_size': '5',
            'page_index': '1',
            'ann_type': 'A',
            'client_source': 'web',
            'stock_list': f'{market.upper()}{stock_code}'
        }
        query_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_str}"
        
        r = subprocess.run(
            ['curl', '-s', '-H', 'User-Agent: Mozilla/5.0', '-H', 'Referer: https://data.eastmoney.com/', full_url],
            capture_output=True, timeout=15
        )
        
        text = r.stdout.decode('utf-8', errors='replace')
        data = json.loads(text)
        
        notice_list = data.get('data', {}).get('list', [])
        for notice in notice_list[:3]:  # 只取前3条
            announcements.append({
                'title': notice.get('title', ''),
                'date': notice.get('notice_date', '')[:10] if notice.get('notice_date') else '',
                'summary': notice.get('summary', '')[:100] if notice.get('summary') else ''
            })
    except:
        pass
    
    return announcements

# ==================== 技术指标计算 ====================

def calc_ma(closes, n):
    return sum(closes[-n:]) / n if len(closes) >= n else 0

def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        if len(closes) < 3: return None
        diffs = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        avg_g = sum(d for d in diffs if d > 0) / max(len(diffs), 1)
        avg_l = sum(-d for d in diffs if d < 0) / max(len(diffs), 1)
        if avg_l == 0: return 100
        return round(100 - 100 / (1 + avg_g / avg_l), 1)
    gains = [max(closes[i]-closes[i-1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i-1]-closes[i], 0) for i in range(1, len(closes))]
    avg_g = sum(gains[-period:]) / period
    avg_l = sum(losses[-period:]) / period
    if avg_l == 0: return 100
    return round(100 - 100 / (1 + avg_g / avg_l), 1)

def calc_macd(closes, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(closes) < slow + signal:
        return None, None, None
    
    # 计算EMA
    def calc_ema(data, n):
        ema = [data[0]]
        k = 2 / (n + 1)
        for d in data[1:]:
            ema.append(d * k + ema[-1] * (1 - k))
        return ema
    
    ema_fast = calc_ema(closes, fast)
    ema_slow = calc_ema(closes, slow)
    dif = [ema_fast[i] - ema_slow[i] for i in range(len(closes))]
    
    # 计算DEA
    dea = calc_ema(dif, signal)
    
    macd = [(dif[i] - dea[i]) * 2 for i in range(len(dif))]
    
    return dif[-1], dea[-1], macd[-1]

def calc_kdj(closes, highs, lows, n=9):
    """计算KDJ指标"""
    if len(closes) < n:
        return None, None, None
    
    low_list = lows[-n:]
    high_list = highs[-n:]
    
    lowest_low = min(low_list)
    highest_high = max(high_list)
    
    if highest_high == lowest_low:
        return 50, 50, 50
    
    rsv = (closes[-1] - lowest_low) / (highest_high - lowest_low) * 100
    
    # KDJ计算
    k = 50
    d = 50
    for _ in range(3):
        k = 2/3 * k + 1/3 * rsv
        d = 2/3 * d + 1/3 * k
    j = 3 * k - 2 * d
    
    return k, d, j

def calc_volume_ma(volumes, n):
    return sum(volumes[-n:]) / n if len(volumes) >= n else 0

def fmt(v):
    return f"{v:.2f}" if v > 0 else "—"

def fmt_vol(v):
    if v >= 1e8: return f"{v/1e8:.2f}亿"
    if v >= 1e4: return f"{v/1e4:.2f}万"
    return f"{v:.0f}"

def format_amt(n):
    if n >= 1e8: return f"{n/1e8:.2f}亿"
    if n >= 1e4: return f"{n/1e4:.2f}万"
    return str(n)

def fmt_flow(v):
    """格式化资金流量"""
    v = v / 10000
    if abs(v) >= 10000:
        return f"{v/10000:.2f}亿"
    elif abs(v) >= 1:
        return f"{v:.2f}万"
    else:
        return f"{v*10000:.0f}元"

# ==================== 分析函数 ====================

def analyze_index_trend(rt, index_codes):
    """分析大盘指数趋势"""
    analysis = []
    total_pct = 0
    for code, name in index_codes:
        d = rt.get(code, {})
        pct = (d['price'] - d['prev']) / d['prev'] * 100 if d.get('prev', 0) else 0
        total_pct += pct
    
    avg_pct = total_pct / len(index_codes) if index_codes else 0
    
    if avg_pct > 1.5:
        analysis.append("📈 大盘强势上涨，市场做多情绪高涨")
    elif avg_pct > 0.5:
        analysis.append("📊 大盘温和上涨，震荡整理为主")
    elif avg_pct > -0.5:
        analysis.append("➡️ 大盘小幅波动，方向不明")
    elif avg_pct > -1.5:
        analysis.append("📉 大盘小幅回调，注意风险")
    else:
        analysis.append("⚠️ 大盘明显下跌，建议谨慎观望")
    
    return analysis

def analyze_volume_trend(raw):
    """分析量能趋势"""
    if len(raw) < 5:
        return "数据不足"
    volumes = [float(k.get('volume', 0)) for k in raw]
    ma5 = calc_volume_ma(volumes, 5)
    today_vol = volumes[-1]
    ratio = today_vol / ma5 if ma5 > 0 else 0
    
    if ratio > 1.5:
        return "🔴 今日明显放量——资金活跃，可能是大机构买入"
    elif ratio > 1.1:
        return "🟡 温和放量——有人买但不算疯狂"
    elif ratio < 0.7:
        return "🔵 缩量整理——市场观望情绪浓厚"
    else:
        return "⚪ 量能平稳——正常交易日"

def analyze_tech_signal(ma5, ma20, rsi, name=""):
    """分析技术信号"""
    signals = []
    if rsi:
        if rsi > 70:
            signals.append(f"RSI={rsi}超买区⚠️：涨太猛了，可能要回调")
        elif rsi < 30:
            signals.append(f"RSI={rsi}超卖区📈：跌太狠了，可能要反弹")
        else:
            signals.append(f"RSI={rsi}正常区")
    
    if ma5 > ma20:
        signals.append("MA5>MA20【金叉】✅：短期走势向上")
    elif ma5 < ma20:
        signals.append("MA5<MA20【死叉】❌：短期走势向下")
    
    return signals if signals else ["走势平稳"]

def analyze_moneyflow_signal(flow_summary, price_change):
    """分析主力资金信号"""
    signals = []
    
    # 3日信号
    if flow_summary['3d'] > 100000000:  # 超过1亿
        signals.append("🔵3日主力大幅净买入")
    elif flow_summary['3d'] > 30000000:
        signals.append("🟢3日主力温和流入")
    elif flow_summary['3d'] < -100000000:
        signals.append("🔴3日主力大幅净卖出")
    
    # 5日信号
    if flow_summary['5d'] > 100000000:
        signals.append("🔵5日主力持续买入")
    elif flow_summary['5d'] < -100000000:
        signals.append("🔴5日主力持续卖出")
    
    # 10日信号
    if flow_summary['10d'] > 100000000:
        signals.append("💎10日主力净流入")
    elif flow_summary['10d'] < -100000000:
        signals.append("⚠️10日主力净流出")
    
    return signals if signals else ["资金面平稳"]

def get_operation_suggestion(stock_data):
    """
    根据综合分析给出操作建议
    stock_data包含: name, code, price, pct, ma5, ma20, rsi, flow_summary, recent_high, recent_low
    """
    suggestions = []
    name = stock_data.get('name', '')
    price = stock_data.get('price', 0)
    pct = stock_data.get('pct', 0)
    ma5 = stock_data.get('ma5', 0)
    ma20 = stock_data.get('ma20', 0)
    ma60 = stock_data.get('ma60', 0)
    rsi = stock_data.get('rsi', 50)
    flow_summary = stock_data.get('flow_summary', {'3d': 0, '5d': 0, '10d': 0})
    recent_high = stock_data.get('recent_high', 0)
    recent_low = stock_data.get('recent_low', 0)
    
    # 基础信号判断
    trend_score = 0
    
    # 均线判断
    if ma5 > ma20:
        trend_score += 1
    else:
        trend_score -= 1
    
    # RSI判断
    if rsi > 65:
        trend_score -= 1  # 过热
    elif rsi < 35:
        trend_score += 1  # 超卖可能反弹
    
    # 主力资金判断
    if flow_summary['3d'] > 30000000:
        trend_score += 1
    elif flow_summary['3d'] < -30000000:
        trend_score -= 1
    
    # 生成建议
    if trend_score >= 2:
        action = "● 关注"
        desc = "技术面+资金面偏多"
    elif trend_score <= -2:
        action = "● 回避"
        desc = "技术面+资金面偏弱"
    else:
        action = "● 观望"
        desc = "多空因素交织，建议等待"
    
    # 支撑压力位
    support = recent_low if recent_low else price * 0.95
    resistance = recent_high if recent_high else price * 1.05
    
    return {
        'action': action,
        'description': desc,
        'support': support,
        'resistance': resistance,
        'trend_score': trend_score
    }

# ==================== 构建报告 ====================

def build_report(report_type='PM', config=None):
    """构建股票简报"""
    if config is None:
        config = load_config()
    
    stocks = config.get('stocks', [])
    indices = config.get('indices', [])
    
    stock_codes = [(s['code'], s['name']) for s in stocks]
    index_codes = [(i['code'], i['name']) for i in indices]
    code_name = dict(stock_codes + index_codes)
    
    emoji_map = {'AM': '📈', 'PM': '📊'}
    emoji = emoji_map.get(report_type, '📈')
    date_str = time.strftime('%Y-%m-%d')
    
    all_codes = ','.join(c for c, _ in stock_codes + index_codes)
    rt = get_realtime_list(all_codes)
    
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"{emoji} 股票简报 {date_str}")
    lines.append(f"{'='*60}")
    lines.append(f"\n*自选股共 {len(stocks)} 只，数据来源：新浪财经*")
    
    # ==================== 新手术语表 ====================
    lines.append("\n📚 **【新手必读】术语解释**")
    lines.append("├─ **MA5/MA20/MA60**：5日/20日/60日均线，简单说就是股票最近5/20/60天的「平均价格」")
    lines.append("├─ **金叉**：短期均线从下往上穿过长期均线，是买入信号之一")
    lines.append("├─ **死叉**：短期均线从上往下穿过长期均线，是卖出信号之一")
    lines.append("├─ **RSI**：相对强弱指数，0-100之间，>70超买（可能跌），<30超卖（可能涨）")
    lines.append("├─ **MACD**：指数平滑移动平均线，用于判断趋势方向和动能")
    lines.append("├─ **KDJ**：随机指标，用于判断超买超卖，J值>100超买，<0超卖")
    lines.append("├─ **放量/缩量**：成交量比平时多/少，表示市场活跃度变化")
    lines.append("├─ **主力净流入**：大资金买入多于卖出，主力可能是机构")
    lines.append("├─ **北向资金**：从香港流入A股的资金，外资看多做多的重要参考")
    lines.append("├─ **VIX恐慌指数**：衡量市场恐慌程度，>30表示市场恐慌，<20表示平静")
    lines.append("└─ **A50夜盘**：新加坡交易的A股指数期货，反映外围市场对A股的预期\n")

    # ===================== 一、大盘环境（含世界局势） =====================
    lines.append("\n" + "="*60)
    lines.append("**一、大盘环境**")
    lines.append("="*60)
    
    # A股指数
    if index_codes:
        lines.append("\n📊 **A股主要指数**")
        lines.append("┌───────────┬──────────┬──────────┐")
        lines.append("│ 指数      │ 收盘点位 │ 涨跌幅   │")
        lines.append("├───────────┼──────────┼──────────┤")
        
        for code, name in index_codes:
            d = rt.get(code_name[code], {})
            pct = (d['price'] - d['prev']) / d['prev'] * 100 if d.get('prev', 0) else 0
            arrow = "▲" if pct >= 0 else "▼"
            lines.append(f"│ {name:<9} │ {d.get('price', 0):>8.2f} │ {arrow}{abs(pct):>6.2f}% │")
        lines.append("└───────────┴──────────┴──────────┘")
        
        index_analysis = analyze_index_trend(rt, index_codes)
        lines.append(f"\n💡 **大盘分析**：{index_analysis[0]}")
    
    # 隔夜美股
    us_data = get_us_market_data()
    if us_data:
        lines.append("\n🌐 **隔夜美股**")
        lines.append("┌───────────┬──────────┬──────────┐")
        lines.append("│ 指数      │ 最新点位 │ 涨跌幅   │")
        lines.append("├───────────┼──────────┼──────────┤")
        
        if us_data.get('dow'):
            d = us_data['dow']
            arrow = "▲" if d['pct'] >= 0 else "▼"
            lines.append(f"│ 道琼斯    │ {d['price']:>8.2f} │ {arrow}{abs(d['pct']):>6.2f}% │")
        
        if us_data.get('nasdaq'):
            d = us_data['nasdaq']
            arrow = "▲" if d['pct'] >= 0 else "▼"
            lines.append(f"│ 纳斯达克  │ {d['price']:>8.2f} │ {arrow}{abs(d['pct']):>6.2f}% │")
        
        if us_data.get('sp500'):
            d = us_data['sp500']
            arrow = "▲" if d['pct'] >= 0 else "▼"
            lines.append(f"│ 标普500   │ {d['price']:>8.2f} │ {arrow}{abs(d['pct']):>6.2f}% │")
        
        lines.append("└───────────┴──────────┴──────────┘")
        
        # 美股影响分析
        if us_data.get('nasdaq'):
            nasdaq_pct = us_data['nasdaq']['pct']
            if nasdaq_pct < -1:
                lines.append("\n⚠️ 美股科技股下跌（纳指▼{:.2f}%），可能影响A股科技板块情绪".format(abs(nasdaq_pct)))
            elif nasdaq_pct > 1:
                lines.append("\n✅ 美股科技股上涨（纳指▲{:.2f}%），外围环境偏暖".format(nasdaq_pct))
    
    # VIX恐慌指数
    vix = get_vix_index()
    if vix:
        vix_level = "平静" if vix < 20 else ("谨慎" if vix < 30 else "恐慌")
        lines.append(f"\n😱 **VIX恐慌指数**：{vix:.2f}点（{vix_level}区）")
        if vix > 30:
            lines.append("   ⚠️ 市场恐慌情绪较重，注意控制风险")
        elif vix < 15:
            lines.append("   ✅ 市场情绪平静，风险偏好较高")
    
    # A50夜盘
    a50 = get_a50_index()
    if a50 and a50.get('price', 0) > 0:
        lines.append(f"\n📉 **富时A50夜盘**：{a50['price']:.0f}点（{'▲' if a50['pct'] >= 0 else '▼'}{abs(a50['pct']):.2f}%）")
        if a50['pct'] < -0.5:
            lines.append("   ⚠️ A50小幅承压，对A股开盘有一定负面影响")
        elif a50['pct'] > 0.5:
            lines.append("   ✅ A50表现较好，A股开盘有望高开")
    
    # 北向资金
    north_flow = get_north_moneyflow()
    if north_flow.get('total', 0) != 0:
        hgt = north_flow['hgt'] / 100000000
        sgt = north_flow['sgt'] / 100000000
        total = north_flow['total'] / 100000000
        arrow = "▲净买入" if total >= 0 else "▼净卖出"
        lines.append(f"\n🌊 **北向资金**：{arrow} {abs(total):.2f}亿元")
        lines.append(f"   • 沪股通：{hgt:+.2f}亿 | 深股通：{sgt:+.2f}亿")
        if total > 50:
            lines.append("   ✅ 外资大幅净买入，市场做多意愿强烈")
        elif total < -50:
            lines.append("   ⚠️ 外资净卖出，需警惕资金外流风险")
    
    # 开盘前综合研判
    lines.append("\n🔮 **开盘前综合研判**：")
    market_signals = []
    if us_data.get('nasdaq', {}).get('pct', 0) < -1:
        market_signals.append("美股科技股下跌")
    if vix and vix > 25:
        market_signals.append("VIX偏高")
    if a50 and a50.get('pct', 0) < -0.5:
        market_signals.append("A50承压")
    if north_flow.get('total', 0) > 50:
        market_signals.append("北向资金流入")
    
    if not market_signals:
        lines.append("   📊 外围市场无明显异动，预计今日A股震荡为主")
    else:
        lines.append(f"   关注点：{', '.join(market_signals)}")

    # ===================== 二、自选股行情 =====================
    if stock_codes:
        lines.append("\n" + "="*60)
        lines.append("**二、自选股行情**")
        lines.append("="*60)
        lines.append("\n┌──────────┬────────┬────────┬────────┬──────────┐")
        lines.append("│ 股票     │ 最新价 │ 昨收价 │ 涨跌幅 │ 成交额   │")
        lines.append("├──────────┼────────┼────────┼────────┼──────────┤")
        
        for code, name in stock_codes:
            d = rt.get(code_name[code], {})
            pct = (d['price'] - d['prev']) / d['prev'] * 100 if d.get('prev', 0) else 0
            arrow = "▲" if pct >= 0 else "▼"
            lines.append(f"│ {name:<8} │ {d.get('price', 0):>6.2f} │ {d.get('prev', 0):>6.2f}│ {arrow}{abs(pct):>5.2f}% │ {format_amt(d.get('amt', 0)):>8} │")
        lines.append("└──────────┴────────┴────────┴────────┴──────────┘")
        
        hot_stocks = []
        for code, name in stock_codes:
            d = rt.get(code_name[code], {})
            pct = (d['price'] - d['prev']) / d['prev'] * 100 if d.get('prev', 0) else 0
            if pct > 3:
                hot_stocks.append(f"{name}(+{pct:.1f}%)")
        
        if hot_stocks:
            lines.append(f"\n💡 **自选股分析**：{', '.join(hot_stocks)} 表现强势")
        else:
            lines.append(f"\n💡 **自选股分析**：今日整体平稳，关注量能变化")
    else:
        lines.append("\n" + "="*60)
        lines.append("**二、自选股行情**")
        lines.append("="*60)
        lines.append("\n⚠️ 尚未设置自选股！")
        lines.append("请通过以下方式添加自选股：")
        lines.append("   • 告诉我「添加XXX股票到自选股」")
        lines.append("   • 发送股票代码，如「sh601012」或「sz000963」")
        lines.append("   • 或直接告诉我股票名称，我会帮你查询代码")

    # ===================== 三、量能追踪 =====================
    if stock_codes:
        lines.append("\n" + "="*60)
        lines.append("**三、量能追踪**")
        lines.append("="*60)
        lines.append("\n┌──────────┬──────────┬──────────┬──────────┬──────────┐")
        lines.append("│ 股票     │ 5日均量  │ 10日均量 │ 30日均量 │  相对量  │")
        lines.append("├──────────┼──────────┼──────────┼──────────┼──────────┤")
        
        for code, name in stock_codes:
            raw = get_kline_raw(code, datalen=90)
            if not raw:
                lines.append(f"│ {name:<8} │    —    │    —    │    —    │    —    │")
                continue
            vol_today = float(raw[-1].get('volume', 0))
            ma_vol5  = float(raw[-1].get('ma_volume5',  0))
            ma_vol10 = float(raw[-1].get('ma_volume10', 0))
            ma_vol30 = float(raw[-1].get('ma_volume30', 0))
            ratio = vol_today / ma_vol5 if ma_vol5 > 0 else 0
            sig = "🔴放量" if ratio > 1.5 else ("🔵缩量" if ratio < 0.7 else "⚪正常")
            lines.append(f"│ {name:<8} │ {fmt_vol(ma_vol5):>8} │ {fmt_vol(ma_vol10):>8} │ {fmt_vol(ma_vol30):>8} │ {ratio:>7.2f}x │")
            lines.append(f"│           │ 信号: {sig:<31} │")
        
        lines.append("└──────────┴──────────┴──────────┴──────────┴──────────┘")
        
        for code, name in stock_codes:
            raw = get_kline_raw(code, datalen=30)
            if raw:
                vol_signal = analyze_volume_trend(raw[-10:])
                lines.append(f"   • {name}: {vol_signal}")

    # ===================== 四、技术指标 =====================
    if stock_codes:
        lines.append("\n" + "="*60)
        lines.append("**四、技术指标**")
        lines.append("="*60)
        lines.append("\n┌──────────┬────────┬────────┬────────┬────────┬────────┐")
        lines.append("│ 股票     │  MA5   │  MA20  │  MA60  │ RSI14  │  信号  │")
        lines.append("├──────────┼────────┼────────┼────────┼────────┼────────┤")
        
        for code, name in stock_codes:
            raw = get_kline_raw(code, datalen=90)
            closes = [float(k['close']) for k in raw] if raw else []
            ma5  = calc_ma(closes, 5)
            ma20 = calc_ma(closes, 20)
            ma60 = calc_ma(closes, 60)
            rsi  = calc_rsi(closes)
            
            sig = "✅金叉" if ma5 > ma20 else "❌死叉"
            if rsi:
                if rsi > 70: sig += "🔥"
                elif rsi < 30: sig += "🧊"
            
            rsi_s = f"{rsi}" if rsi else "—"
            lines.append(f"│ {name:<8} │ {fmt(ma5):>6} │ {fmt(ma20):>6} │ {fmt(ma60):>6} │ {rsi_s:>6} │ {sig} │")
        lines.append("└──────────┴────────┴────────┴────────┴────────┴────────┘")
        lines.append("  📖 RSI>70过买恐回调 | RSI<30过卖或有反弹 | ✅金叉=买入机会 | ❌死叉=卖出信号")
        
        # 技术信号分析
        lines.append("\n📊 **技术信号分析**：")
        for code, name in stock_codes:
            raw = get_kline_raw(code, datalen=90)
            closes = [float(k['close']) for k in raw] if raw else []
            ma5  = calc_ma(closes, 5)
            ma20 = calc_ma(closes, 20)
            rsi  = calc_rsi(closes)
            
            # MACD分析
            highs = [float(k.get('high', 0)) for k in raw] if raw else []
            lows = [float(k.get('low', 0)) for k in raw] if raw else []
            dif, dea, macd = calc_macd(closes)
            
            signals = analyze_tech_signal(ma5, ma20, rsi, name)
            
            # MACD解读
            macd_sig = ""
            if dif and dea:
                if dif > 0 and dif > dea:
                    macd_sig = "MACD零轴上方且金叉（上涨动能）"
                elif dif < 0 and dif < dea:
                    macd_sig = "MACD零轴下方且死叉（下跌动能）"
                elif dif > dea:
                    macd_sig = "MACD红柱收缩（上涨动力减弱）"
                else:
                    macd_sig = "MACD绿柱收缩（下跌压力减轻）"
            
            lines.append(f"   • **{name}**：{', '.join(signals)}")
            if macd_sig:
                lines.append(f"     → {macd_sig}")

    # ===================== 五、主力资金（3日/5日/10日） =====================
    if stock_codes:
        lines.append("\n" + "="*60)
        lines.append("**五、主力资金追踪（3日/5日/10日汇总）**")
        lines.append("="*60)
        lines.append("\n┌──────────┬────────────┬────────────┬────────────┬──────────┐")
        lines.append("│ 股票     │  3日净流入  │  5日净流入  │ 10日净流入  │ 信号评级 │")
        lines.append("├──────────┼────────────┼────────────┼────────────┼──────────┤")
        
        flow_summaries = {}
        for code, name in stock_codes:
            em_data = get_moneyflow_from_eastmoney(code)
            flow_summary = calc_moneyflow_summary(em_data)
            flow_summaries[code] = {'data': em_data, 'summary': flow_summary}
            
            # 评级
            if flow_summary['3d'] > 50000000 and flow_summary['10d'] > 0:
                rating = "✅积极建仓"
            elif flow_summary['3d'] > 20000000:
                rating = "🟢温和流入"
            elif flow_summary['3d'] < -50000000:
                rating = "❌主力出逃"
            elif flow_summary['3d'] < -20000000:
                rating = "🟠净流出"
            else:
                rating = "⚪中性"
            
            d3 = fmt_flow(flow_summary['3d'])
            d5 = fmt_flow(flow_summary['5d'])
            d10 = fmt_flow(flow_summary['10d'])
            lines.append(f"│ {name:<8} │ {d3:>10} │ {d5:>10} │ {d10:>10} │ {rating} │")
        
        lines.append("└──────────┴────────────┴────────────┴────────────┴──────────┘")
        
        # 主力资金解读
        lines.append("\n📊 **主力资金解读**：")
        for code, name in stock_codes:
            flow_data = flow_summaries.get(code, {})
            em_data = flow_data.get('data', [])
            flow_summary = flow_data.get('summary', {'3d': 0, '5d': 0, '10d': 0})
            
            if not em_data:
                lines.append(f"   • {name}: 数据获取中...")
                continue
            
            # 近10日每日明细
            lines.append(f"\n   **{name}** 近10日明细：")
            lines.append("   ┌──────────┬────────┬────────────┬────────────┐")
            lines.append("   │ 日期     │ 涨跌幅  │ 主力净流入  │  净占比    │")
            lines.append("   ├──────────┼────────┼────────────┼────────────┤")
            
            for day in em_data[-10:]:
                date = day.get('date', '')[:10]
                pct = day.get('pct_change', 0)
                arrow = "▲" if pct >= 0 else "▼"
                main_flow = day.get('main_net_flow', 0)
                main_ratio = day.get('main_ratio', 0)
                flow_str = fmt_flow(main_flow)
                lines.append(f"   │ {date} │ {arrow}{abs(pct):>5.2f}% │ {flow_str:>10} │ {main_ratio:>7.2f}% │")
            
            lines.append("   └──────────┴────────┴────────────┴────────────┘")
            
            # 综合解读
            signals = analyze_moneyflow_signal(flow_summary, 0)
            if flow_summary['3d'] > 50000000 and flow_summary['5d'] > 30000000:
                lines.append(f"   💡 **{name}** 综合判断：🔵主力连续净买入，短期资金面积极关注")
            elif flow_summary['3d'] < -50000000:
                lines.append(f"   💡 **{name}** 综合判断：🔴主力连续净卖出，短期回避")
            elif flow_summary['10d'] > 100000000:
                lines.append(f"   💡 **{name}** 综合判断：✅中期主力建仓，基本面或有机会")
            elif flow_summary['10d'] < -100000000:
                lines.append(f"   💡 **{name}** 综合判断：⚠️中期主力离场，短期难以企稳")
            else:
                lines.append(f"   💡 **{name}** 综合判断：⚪资金面平稳，暂无明显异动")

    # ===================== 六、重要公告 =====================
    if stock_codes:
        lines.append("\n" + "="*60)
        lines.append("**六、个股重要公告**")
        lines.append("="*60)
        
        has_announcements = False
        for code, name in stock_codes:
            announcements = get_stock_announcements(code)
            if announcements:
                has_announcements = True
                lines.append(f"\n📢 **{name}** ({code}) 近期公告：")
                for ann in announcements:
                    lines.append(f"   • [{ann['date']}] {ann['title']}")
                    if ann.get('summary'):
                        lines.append(f"     摘要：{ann['summary']}...")
        
        if not has_announcements:
            lines.append("\n   📭 近期无重大公告披露")
        
        lines.append("\n💡 **公告解读提示**：")
        lines.append("   • 年报/季报披露期重点关注业绩变化")
        lines.append("   • 股份回购计划通常被视为积极信号（公司认为股价被低估）")
        lines.append("   • 业绩预减/预亏公告需警惕下行风险")

    # ===================== 七、走势研判与操作建议 =====================
    if stock_codes:
        lines.append("\n" + "="*60)
        lines.append("**七、走势研判与操作建议**")
        lines.append("="*60)
        
        lines.append("\n┌──────────┬──────────┬───────────┬───────────┬────────────┐")
        lines.append("│ 股票     │ 操作建议  │  支撑位   │  压力位   │ 综合研判   │")
        lines.append("├──────────┼──────────┼───────────┼───────────┼────────────┤")
        
        operation_data = []
        for code, name in stock_codes:
            raw = get_kline_raw(code, datalen=90)
            closes = [float(k['close']) for k in raw] if raw else []
            highs = [float(k.get('high', 0)) for k in raw] if raw else []
            lows = [float(k.get('low', 0)) for k in raw] if raw else []
            
            d = rt.get(code_name[code], {})
            price = d.get('price', 0)
            pct = (d['price'] - d['prev']) / d['prev'] * 100 if d.get('prev', 0) else 0
            
            ma5 = calc_ma(closes, 5)
            ma20 = calc_ma(closes, 20)
            ma60 = calc_ma(closes, 60)
            rsi = calc_rsi(closes)
            
            flow_data = flow_summaries.get(code, {})
            flow_summary = flow_data.get('summary', {'3d': 0, '5d': 0, '10d': 0})
            
            # 计算近期高低点
            recent_high = max(highs[-20:]) if len(highs) >= 20 else (max(highs) if highs else price)
            recent_low = min(lows[-20:]) if len(lows) >= 20 else (min(lows) if lows else price * 0.9)
            
            stock_analysis = {
                'name': name,
                'code': code,
                'price': price,
                'pct': pct,
                'ma5': ma5,
                'ma20': ma20,
                'ma60': ma60,
                'rsi': rsi,
                'flow_summary': flow_summary,
                'recent_high': recent_high,
                'recent_low': recent_low
            }
            
            suggestion = get_operation_suggestion(stock_analysis)
            operation_data.append((name, suggestion, recent_low, recent_high))
            
            action = suggestion['action']
            support = suggestion['support']
            resistance = suggestion['resistance']
            desc = suggestion['description'][:8]
            
            lines.append(f"│ {name:<8} │ {action:<8} │ {support:>8.2f} │ {resistance:>8.2f} │ {desc:<10} │")
        
        lines.append("└──────────┴──────────┴───────────┴───────────┴────────────┘")
        
        # 详细操作建议
        lines.append("\n📋 **详细操作建议**：")
        for name, suggestion, recent_low, recent_high in operation_data:
            raw = get_kline_raw(code, datalen=90)
            closes = [float(k['close']) for k in raw] if raw else []
            
            flow_data = flow_summaries.get(code, {})
            flow_summary = flow_data.get('summary', {'3d': 0, '5d': 0, '10d': 0})
            
            rsi = calc_rsi(closes)
            ma5 = calc_ma(closes, 5)
            ma20 = calc_ma(closes, 20)
            
            action = suggestion['action']
            support = suggestion['support']
            resistance = suggestion['resistance']
            
            lines.append(f"\n   **{name}**：")
            
            # 技术面
            tech_analysis = []
            if ma5 > ma20:
                tech_analysis.append("均线呈多头排列，短期强势")
            elif ma5 < ma20:
                tech_analysis.append("均线呈空头排列，短期偏弱")
            else:
                tech_analysis.append("均线纠缠，方向不明")
            
            if rsi:
                if rsi > 65:
                    tech_analysis.append(f"RSI偏高({rsi:.0f})，注意回调风险")
                elif rsi < 35:
                    tech_analysis.append(f"RSI偏低({rsi:.0f})，存在反弹可能")
            
            lines.append(f"   技术面：{'; '.join(tech_analysis)}")
            
            # 资金面
            flow_analysis = []
            if flow_summary['3d'] > 30000000:
                flow_analysis.append(f"3日主力净流入{fmt_flow(flow_summary['3d'])}")
            elif flow_summary['3d'] < -30000000:
                flow_analysis.append(f"3日主力净流出{fmt_flow(abs(flow_summary['3d']))}")
            
            if flow_summary['5d'] > 0 and flow_summary['10d'] > 0:
                flow_analysis.append("中期资金持续建仓")
            elif flow_summary['5d'] < 0 and flow_summary['10d'] < 0:
                flow_analysis.append("中期资金持续离场")
            
            if flow_analysis:
                lines.append(f"   资金面：{'; '.join(flow_analysis)}")
            
            # 操作建议
            if action == "● 关注":
                lines.append(f"   操作建议：✅可逢低关注，支撑位{support:.2f}，突破{resistance:.2f}可加仓")
            elif action == "● 回避":
                lines.append(f"   操作建议：⚠️建议回避，资金持续流出，等待止跌信号")
            else:
                lines.append(f"   操作建议：➡️建议观望，等待趋势明朗后再操作")
        
        lines.append("\n⚠️ **风险提示**：以上建议仅供参考，不构成投资依据。股市有风险，投资需谨慎！")

    lines.append(f"\n{'='*60}")
    lines.append(f"*数据来源：新浪财经、东方财富、英为财情 | 生成时间 {time.strftime('%Y-%m-%d %H:%M:%S')} 北京时间*")
    return '\n'.join(lines)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'PM'
    report = build_report(mode)
    print(report)
    out_path = os.path.join(TEMP_DIR, 'briefing_latest.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 报告已保存 → {out_path}")
