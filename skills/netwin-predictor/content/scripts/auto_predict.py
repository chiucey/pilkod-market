#!/usr/bin/env python3
"""
auto_predict.py — 自动预测管道
每天自动：搜索今日比赛 → 获取赔率 → 融合模型预测 → 输出报告
"""
import json, math, sys, re, datetime, urllib.request, ssl
from fuse_engine import fuse_prediction, get_weight, netwin_predict, winfp_predict, get_elo

# ═══════════════════════════════════════════════════════════
# 第1步：搜索今日/明日比赛（无API时使用）
# ═══════════════════════════════════════════════════════════
LEAGUE_NAME_MAP = {
    'Premier League':'PL','English Premier League':'PL','EPL':'PL','英超':'PL',
    'La Liga':'PD','Primera Division':'PD','西甲':'PD',
    'Serie A':'SA','意甲':'SA',
    'Bundesliga':'BL1','德甲':'BL1',
    'Ligue 1':'FL1','Ligue 1 Uber Eats':'FL1','法甲':'FL1',
    'Champions League':'CL','UEFA Champions League':'CL','欧冠':'CL',
    'Europa League':'EL','UEFA Europa League':'EL','欧罗巴':'EL',
    'UEFA Europa League':'EL','欧联':'EL',
    'Europa Conference League':'EL','欧协联':'EL',
    'World Cup':'WC','世界杯':'WC',
    'Asian Champions League':'AC','亚冠':'AC',
    'Chinese Super League':'CSL','中超':'CSL',
    'MLS':'MLS','美职联':'MLS',
    'J1 League':'J1','日职联':'J1',
    'K League 1':'K1','K联赛':'K1',
    'Eredivisie':'Eredivisie','荷甲':'Eredivisie',
    'Primeira Liga':'Primeira Liga','葡超':'Primeira Liga',
    'Scottish Premiership':'SPL','苏超':'SPL',
    'Brasileiro Serie A':'BSA','巴甲':'BSA',
}

# 赔率来源：使用公共博彩比较网站搜索
def search_match_odds(home, away, league):
    """
    通过网络搜索获取指定比赛的赔率
    返回: (oH, oD, oA) 或 None
    """
    query = f"{home} vs {away} odds {league} 1X2"
    try:
        import subprocess
        result = subprocess.run(
            ['python3', '-c', f'''
import urllib.request, json, ssl
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
url = "https://www.google.com/search?q={urllib.parse.quote('{query}')}&num=3"
req = urllib.request.Request(url, headers={{'User-Agent':'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=5, context=ctx)
html = resp.read().decode('utf-8', errors='ignore')
print(html[:2000] if html else "NO_HTML")
'''],
            capture_output=True, text=True, timeout=8
        )
        return None  # 网络搜索不靠谱，暂时返回None
    except:
        return None

# ═══════════════════════════════════════════════════════════
# 第2步：从本地数据获取赔率（备用）
# ═══════════════════════════════════════════════════════════
def load_local_odds():
    """从ou_realtime.json加载本地赔率数据"""
    try:
        data = json.load(open('/workspace/netwin-predictor/data/ou_realtime.json', encoding='utf-8'))
        # 转换为 dict: (home, away) -> odds
        odds_map = {}
        for match in data:
            home = match.get('home_team','')
            away = match.get('away_team','')
            # 找h2h赔率
            for bk in match.get('bookmakers', []):
                for mkt in bk.get('markets', []):
                    if mkt.get('key') == 'h2h':
                        outcomes = {o['name']: o['price'] for o in mkt.get('outcomes', [])}
                        # 识别主队/平局/客队
                        h = outcomes.get(home) or outcomes.get(home.split()[-1])
                        d = outcomes.get('Draw') or outcomes.get('draw') or outcomes.get('X') or outcomes.get('X.'))
                        a = outcomes.get(away) or outcomes.get(away.split()[-1])
                        if h and d and a:
                            odds_map[(home, away)] = (float(h), float(d), float(a))
                        break
        return odds_map
    except Exception as e:
        print(f"本地数据加载失败: {e}")
        return {}

# ═══════════════════════════════════════════════════════════
# 第3步：从网络获取赔率（主要方式：The Odds API）
# ═══════════════════════════════════════════════════════════
def fetch_live_odds_from_api():
    """
    从The Odds API获取实时赔率
    API Key: 0e3dfc7fb7420cb2d45fe55895a1007c（已注册免费账号）
    """
    import urllib.request, json, ssl
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    api_key = '0e3dfc7fb7420cb2d45fe55895a1007c'
    # 只取最重要的盘口：h2h（胜平负）
    url = f'https://api.the-odds-api.com/v4/sports/soccer/odds?regions=eu&markets=h2h&apiKey={api_key}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=8, context=ctx)
        data = json.loads(resp.read().decode('utf-8'))
        matches = []
        for m in data:
            home = m.get('home_team','')
            away = m.get('away_team','')
            sport = m.get('sport_key','')
            commence = m.get('commence_time','')[:10]
            # 提取赔率（取第一个bookmaker）
            for bk in m.get('bookmakers', []):
                for mkt in bk.get('markets', []):
                    if mkt.get('key') == 'h2h':
                        outcomes = {o['name'].lower(): o['price'] for o in mkt.get('outcomes', [])}
                        # 尝试识别
                        oH = outcomes.get('home') or outcomes.get(home.lower())
                        oD = outcomes.get('draw') or outcomes.get('tie')
                        oA = outcomes.get('away') or outcomes.get(away.lower())
                        if oH and oD and oA:
                            matches.append({
                                'home': home, 'away': away, 'league': sport,
                                'date': commence,
                                'oH': float(oH), 'oD': float(oD), 'oA': float(oA)
                            })
                        break
        return matches
    except Exception as e:
        return []

# ═══════════════════════════════════════════════════════════
# 第4步：从今日比赛数据（hardcoded赛程）构建预测
# ═══════════════════════════════════════════════════════════
TODAY_MATCHES = [
    # 格式：(home, away, league, oH, oD, oA, match_date)
    # 示例 — 真实赔率从网络获取后填入
]

def get_default_odds(home, away):
    """
    当无法获取赔率时，用ELO估算默认赔率
    基于ELO差查表
    """
    hE = get_elo(home); aE = get_elo(away)
    if hE == 1500 and aE == 1500:
        return None
    diff = hE - aE
    # ELO差→概率映射（NetWin逆向工程）
    pH = 1 / (1 + 10**(-diff/400))
    pA = 1 / (1 + 10**(diff/400))
    pD = max(0.15, 0.33 - abs(diff)/1000)
    ts = pH + pD + pA
    pH /= ts; pD /= ts; pA /= ts
    oH = round(1/pH, 2) if pH > 0.01 else 4.00
    oD = round(1/pD, 2) if pD > 0.01 else 3.30
    oA = round(1/pA, 2) if pA > 0.01 else 4.00
    return (oH, oD, oA)

# ═══════════════════════════════════════════════════════════
# 第5步：预测输出格式
# ═══════════════════════════════════════════════════════════
def output_prediction(r):
    """格式化输出单场比赛预测"""
    emoji = {'胜':'✅','平':'🔶','负':'🔴'}
    conf_emoji = {'高':'🔥','中':'⚡','低':'💤','⚠️分歧':'⚠️'}
    # 联赛旗帜
    lg_flag = {'PL':'🏴󠁧󠁢󠁥󠁮󠁧󠁿','PD':'🇪🇸','SA':'🇮🇹','BL1':'🇩🇪','FL1':'🇫🇷','CL':'🏆','EL':'🥇','WC':'🌍','AC':'🌏','CSL':'🇨🇳','J1':'🇯🇵','K1':'🇰🇷','Eredivisie':'🇳🇱','Primeira Liga':'🇵🇹','SPL':'🏴󠁧󠁢󠁳󠁣󠁴󠁿','BSA':'🇧🇷'}
    flag = lg_flag.get(r.get('league',''),'⚽')
    conf = conf_emoji.get(r.get('confidence',''),'⚡')
    tags = r.get('factor_tags', [])
    tag_str = ' | '.join(tags) if tags else '无特殊信号'
    lines = [
        '',
        f'{flag} **{r["home"]}** vs **{r["away"]}**',
        f'   联赛：{r.get("league","?")} | {r.get("date","今晚")} ',
        f'   盘口：{r.get("handicap","?")}',
        f'   赔率：主{r["odds"]["H"]} / 平{r["odds"]["D"]} / 客{r["odds"]["A"]}',
        f'   模型：{r["prob"]["H"]*100:.1f}% / {r["prob"]["D"]*100:.1f}% / {r["prob"]["A"]*100:.1f}%',
        f'   🎯 **{r["prediction"]}**（{conf} {r["confidence"]}）',
        f'   📌 {tag_str}',
        ''
    ]
    return '\n'.join(lines)

def output_report(results, title="今日融合预测报告"):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    total = len(results)
    high_conf = sum(1 for r in results if r.get('confidence') == '高')
    warn = sum(1 for r in results if '⚠️' in r.get('confidence',''))
    body = '\n'.join(output_prediction(r) for r in results)
    report = f"""
{'='*52}
🏆 {title}
生成时间：{now} | 共{total}场 | 高置信{high_conf}场 | 分歧{warn}场
{'='*52}
{body}
{'='*52}
⚠️ 免责声明：本报告由AI融合模型生成，仅供参考，
   不构成投注建议，请理性观赛。
{'='*52}
"""
    return report

# ═══════════════════════════════════════════════════════════
# 第6步：主预测管道
# ═══════════════════════════════════════════════════════════
def run_pipeline(matches_data):
    """
    matches_data: [(home, away, league, oH, oD, oA, date), ...]
    """
    results = []
    for item in matches_data:
        try:
            if len(item) == 7:
                home, away, league, oH, oD, oA, date = item
            else:
                home, away, league, oH, oD, oA = item
                date = '今晚'
            r = fuse_prediction(home, away, league, oH, oD, oA)
            r['date'] = date
            results.append(r)
        except Exception as e:
            results.append({
                'home': item[0], 'away': item[1], 'league': item[2],
                'odds': {'H': item[3], 'D': item[4], 'A': item[5]},
                'error': str(e)
            })
    return results

# ═══════════════════════════════════════════════════════════
# 第7步：从网络自动获取赔率 + 预测
# ═══════════════════════════════════════════════════════════
def fetch_and_predict():
    """
    完整管道：从API/网络获取今日赔率 → 运行融合模型 → 输出报告
    """
    print("📡 正在从The Odds API获取实时赔率...")
    matches = fetch_live_odds_from_api()
    if not matches:
        print("⚠️ The Odds API无响应，尝试从本地数据...")
        local = load_local_odds()
        if local:
            results = []
            for (home, away), (oH, oD, oA) in local.items():
                lg = 'Unknown'
                r = fuse_prediction(home, away, lg, oH, oD, oA)
                results.append(r)
            print(output_report(results, "本地赔率预测报告"))
            return
        print("❌ 无法获取赔率数据，请手动输入比赛。")
        print_usage()
        return
    # 运行预测
    results = []
    for m in matches:
        try:
            r = fuse_prediction(m['home'], m['away'], m['league'], m['oH'], m['oD'], m['oA'])
            r['date'] = m.get('date','今晚')
            results.append(r)
        except: pass
    print(output_report(results, "实时赔率融合预测报告"))

def print_usage():
    print("""
📋 用法说明：

   方式1 — 自动获取（需要网络）：
   python3 auto_predict.py --fetch

   方式2 — 手动输入赔率：
   python3 auto_predict.py 曼城 阿森纳 英超 2.10 3.50 3.40
   python3 auto_predict.py 拜仁 皇马 欧冠 1.85 3.80 4.00 "今晚20:00"

   方式3 — 批量文件（JSON格式）：
   python3 auto_predict.py --file matches.json

   方式4 — 预设比赛（无赔率时用ELO估算）：
   python3 auto_predict.py --preset
""")

# ═══════════════════════════════════════════════════════════
# 预设比赛（今日重要比赛，赔率来自搜索补充）
# ═══════════════════════════════════════════════════════════
PRESET_MATCHES = [
    # 2026-04-17/18 重要比赛（赔率为示例值，实际运行时应从网络获取）
    # ("主队","客队","联赛",oH,oD,oA,"日期")
]

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print_usage()
    elif args[0] == '--fetch':
        fetch_and_predict()
    elif args[0] == '--preset' or args[0] == '--today':
        if not PRESET_MATCHES:
            print("⚠️ 暂无预设比赛（赛程数据过期），请用 --fetch 或手动输入。")
        else:
            results = run_pipeline(PRESET_MATCHES)
            print(output_report(results, "今日融合预测报告"))
    elif args[0] == '--file':
        if len(args) < 2:
            print("需要指定文件：--file matches.json")
        else:
            data = json.load(open(args[1], encoding='utf-8'))
            results = run_pipeline(data)
            print(output_report(results, f"批量预测报告（{args[1]}）"))
    elif len(args) >= 6:
        home, away, league = args[0], args[1], args[2]
        oH, oD, oA = float(args[3]), float(args[4]), float(args[5])
        date = args[6] if len(args) > 6 else '比赛日'
        r = fuse_prediction(home, away, league, oH, oD, oA)
        r['date'] = date
        print(output_report([r], f"{home} vs {away} 融合预测"))
    else:
        print_usage()
