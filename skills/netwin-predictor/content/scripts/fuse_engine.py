#!/usr/bin/env python3
"""
NetWin × win-football-predictor 融合预测引擎
小虾 V16 ELO系统 + Pi-Rating三模型 + 联赛专项校正

原理：
  P_final = w1 * P_netwin + w2 * P_winfp
  w1 = 0.5（NetWin擅长盘口分析）
  w2 = 0.5（win-fp擅长赔率特征）
  
  小联赛/胜负彩：w2为主（NetWin无覆盖时w1=0）
  联赛专项校正：叠加win-fp的v4修正层
  信心评分：两模型一致时 + 高信，分歧时参考factorTags
"""
import csv, json, math, sys

# ═══════════════════════════════════════════════════════════
# 第1部分：小虾 ELO 系统（NetWin V16 核心逻辑）
# ═══════════════════════════════════════════════════════════
ELO = {}
with open('/workspace/netwin-predictor/data/clubelo.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        ELO[row['Club'].strip()] = float(row['Elo'])

NM = {
    # 英超
    'Manchester City':'Manchester City','曼彻斯特城':'Manchester City','曼城':'Manchester City',
    'Manchester United':'Manchester United','曼彻斯特联':'Manchester United','曼联':'Manchester United',
    'Liverpool':'Liverpool','Chelsea':'Chelsea','Arsenal':'Arsenal',
    'Tottenham Hotspur':'Tottenham Hotspur','托特纳姆热刺':'Tottenham Hotspur','热刺':'Tottenham Hotspur',
    '埃弗顿':'Everton','Everton':'Everton',
    '阿斯顿维拉':'Aston Villa','维拉':'Aston Villa','Aston Villa':'Aston Villa',
    '纽卡斯尔联':'Newcastle United','纽卡斯尔':'Newcastle United',
    '西汉姆联':'West Ham United','西汉姆':'West Ham United',
    '富勒姆':'Fulham','水晶宫':'Crystal Palace','狼队':'Wolverhampton Wanderers',
    '伯恩茅斯':'Bournemouth','诺丁汉森林':'Nottingham Forest','诺丁汉':'Nottingham Forest',
    '布伦特福德':'Brentford','布伦特福德':'Brentford',
    # 德甲
    '拜仁慕尼黑':'Bayern Munich','拜仁':'Bayern Munich','Bayern Munich':'Bayern Munich',
    '多特蒙德':'Borussia Dortmund','多特':'Borussia Dortmund','Dortmund':'Borussia Dortmund',
    'RB莱比锡':'RB Leipzig','莱比锡':'RB Leipzig','RB Leipzig':'RB Leipzig',
    '勒沃库森':'Bayer Leverkusen','勒沃':'Bayer Leverkusen','Bayer Leverkusen':'Bayer Leverkusen',
    '法兰克福':'Eintracht Frankfurt','法兰克福':'Eintracht Frankfurt',
    '弗赖堡':'SC Freiburg','弗赖堡':'SC Freiburg',' Freiburg':'SC Freiburg',
    '霍芬海姆':'TSG 1899 Hoffenheim','沃尔夫斯堡':'VfL Wolfsburg',
    '美因茨':'1. FSV Mainz 05','科隆':'1. FC Köln','斯图加特':'VfB Stuttgart',
    '不来梅':'SV Werder Bremen','门兴':'Borussia Monchengladbach',
    '柏林联合':'1. FC Union Berlin','奥格斯堡':'FC Augsburg',
    '汉堡':'Hamburger SV','海登海姆':'1. FC Heidenheim','圣保利':'FC St. Pauli',
    '波鸿':'VfL Bochum','达姆斯塔特':'SV Darmstadt 98','柏林赫塔':'Hertha BSC',
    # 西甲
    '皇家马德里':'Real Madrid','皇马':'Real Madrid','Real Madrid':'Real Madrid',
    '巴塞罗那':'FC Barcelona','巴萨':'FC Barcelona','FC Barcelona':'FC Barcelona',
    '马德里竞技':'Atletico Madrid','马竞':'Atletico Madrid','Atletico Madrid':'Atletico Madrid',
    '塞维利亚':'Sevilla FC','塞维利亚':'Sevilla FC','Sevilla':'Sevilla FC',
    '皇家社会':'Real Sociedad','皇家贝蒂斯':'Real Betis','Betis':'Real Betis',
    '比利亚雷亚尔':'Villarreal CF','奥萨苏纳':'CA Osasuna',
    '巴列卡诺':'Rayo Vallecano','西班牙人':'RCD Espanyol','赫塔菲':'Getafe CF',
    '塞尔塔':'Celta Vigo','塞尔塔维戈':'Celta Vigo',
    '格拉纳达':'Granada CF','莱万特':'Levante UD','马洛卡':'RCD Mallorca',
    '阿拉维斯':'Deportivo Alavés','巴拉多利德':'Real Valladolid',
    '赫罗纳':'Girona FC','埃尔切':'Elche CF',
    # 意甲
    '国际米兰':'Inter Milan','国米':'Inter Milan','Inter Milan':'Inter Milan',
    'AC米兰':'AC Milan','米兰':'AC Milan','Milan':'AC Milan',
    '尤文图斯':'Juventus','尤文':'Juventus','Juventus':'Juventus',
    '那不勒斯':'SSC Napoli','那波利斯':'SSC Napoli','Napoli':'SSC Napoli',
    '亚特兰大':'Atalanta','亚特兰大':'Atalanta','Atalanta':'Atalanta',
    '罗马':'AS Roma','拉齐奥':'Lazio','佛罗伦萨':'ACF Fiorentina',
    '博洛尼亚':'Bologna','博洛尼亚':'Bologna','Bologna':'Bologna',
    '都灵':'Torino','帕尔马':'Parma','恩波利':'Empoli',
    '乌迪内斯':'Udinese','萨索洛':'US Sassuolo',
    '卡利亚里':'Cagliari','热那亚':'Genoa','威尼斯':'Venezia FC',
    '莱切':'Lecce','斯佩齐亚':'US Sassuolo','克雷莫内塞':'Cremonese',
    '维罗纳':'Hellas Verona','蒙扎':'AC Monza','科莫':'Como 1907',
    '贝内文托':'Benevento','桑普多利亚':'UC Sampdoria',
    # 法甲
    '巴黎圣日耳曼':'Paris Saint-Germain','PSG':'Paris Saint-Germain',
    '马赛':'Olympique Marseille','里昂':'Olympique Lyon','Lyon':'Olympique Lyon',
    '摩纳哥':'AS Monaco','Monaco':'AS Monaco','里尔':'Lille',
    '雷恩':'Stade Rennais','尼斯':'OGC Nice','南特':'FC Nantes',
    '斯特拉斯堡':'RC Strasbourg','布雷斯特':'Stade Brestois',
    '兰斯':'Stade de Reims','欧塞尔':'AJ Auxerre',
    '图卢兹':'Toulouse FC','克莱蒙':'Clermont Foot','梅斯':'FC Metz',
    '勒阿弗尔':'Le Havre AC','昂热':'Anges SCO','波尔多':'FC Girondins de Bordeaux',
    # 欧战
    '葡萄牙体育':'Sporting CP','里斯本竞技':'Sporting CP','Sporting':'Sporting CP',
    '阿贾克斯':'Ajax','本菲卡':'SL Benfica','埃因霍温':'PSV Eindhoven',
    '萨尔茨堡':'Red Bull Salzburg','顿涅茨克矿工':'Shakhtar Donetsk',
    '贝尔格莱德红星':'Red Star Belgrade','费耶诺德':'Feyenoord',
    '布拉加':'SC Braga','哥本哈根':'FC Copenhagen',
    '年轻人':'BSC Young Boys','谢里夫':'FC Sheriff Tiraspol',
    '布鲁日':'Club Brugge KV','卢加诺':'Lugano',
    '基辅迪纳摩':'Dynamo Kyiv','塞萨洛尼基':'PAOK FC',
    '标准列日':'Standard Liège','流浪者':'Rangers FC','凯尔特人':'Celtic FC',
    '中日德兰':'FC Midtjylland','林茨':'LASK Linz',
    # 亚洲
    '上海海港':'Shanghai Port','武汉三镇':'Wuhan Three Gorges',
    '北京国安':'Beijing Guoan','上海申花':'Shanghai Shenhua',
    '山东泰山':'Shandong Taishan','成都蓉城':'Chengdu Rongcheng',
    '横滨水手':'Yokohama F. Marinos','川崎前锋':'Kawasaki Frontale',
    '全北现代':'Jeonbuk Hyundai Motors','蔚山现代':'Ulsan Hyundai',
    '利雅得新月':'Al Hilal','利雅得胜利':'Al Nassr',
}

def get_elo(team):
    t = NM.get(team, team)
    return ELO.get(t, 1500)

DB = {'PL':0.385,'PD':0.446,'SA':0.402,'BL1':0.358,'FL1':0.393,'CL':0.376,'WC':0.229,'EL':0.380}
LG_MAP = {'PL':'PL','英超':'PL','PD':'PD','西甲':'PD','SA':'SA','意甲':'SA',
          'BL1':'BL1','德甲':'BL1','FL1':'FL1','法甲':'FL1',
          'CL':'CL','欧冠':'CL','EL':'EL','欧罗巴':'EL','欧联':'EL',
          '欧冠联赛':'CL','欧罗巴联赛':'EL','欧洲冠军联赛':'CL',
          '世界杯':'WC','WC':'WC'}

def netwin_predict(home, away, league, oH, oD, oA):
    """NetWin V16 核心预测逻辑"""
    hE = get_elo(home); aE = get_elo(away)
    diff = hE - aE
    big6 = ['Manchester City','Arsenal','Liverpool','Chelsea','Tottenham Hotspur','Manchester United','Aston Villa']
    if home in big6: diff += 50
    if away in big6: diff -= 50
    if oH < 1.30: diff *= 0.80
    elif oH < 1.50: diff *= 0.85
    lg = LG_MAP.get(league, league)
    if lg == 'BL1' and home in ['Bayern Munich','Dortmund','RB Leipzig','Bayer Leverkusen'] and (oA/oH) < 2.0:
        diff += 15
    pH = 1 / (1 + 10**(-diff/400))
    hv = (oA - oH) * 0.4
    pD_base = DB.get(lg, 0.33)
    if lg == 'PD' and abs(diff) < 60: pD_base += 0.12
    if lg == 'CL' and diff > 0 and diff < 80: pD_base += 0.08
    if abs(hv) < 0.13 and 2.5 <= oD <= 3.6: pD_base += 0.08
    if lg == 'SA': pD_base += 0.05
    pA = 1 - pH - pD_base
    if pA < 0: pA = 0
    tot = pH + pD_base + pA
    if tot == 0: return [0.33, 0.33, 0.34]
    return [pH/tot, pD_base/tot, pA/tot]

# ═══════════════════════════════════════════════════════════
# 第2部分：Pi-Rating 系统（win-football-predictor 核心）
# ═══════════════════════════════════════════════════════════
LEAGUE_CFG = {
    '英超': {'home_boost': 1.25}, '西甲': {'home_boost': 1.15},
    '意甲': {'home_boost': 1.20}, '德甲': {'home_boost': 1.22},
    '法甲': {'home_boost': 1.12}, '欧冠': {'home_boost': 1.10},
    '欧联': {'home_boost': 1.08}, '欧罗巴': {'home_boost': 1.08},
    '欧协联': {'home_boost': 1.06}, '中超': {'home_boost': 1.30},
    '亚冠': {'home_boost': 1.10}, '默认': {'home_boost': 1.15},
}

def pi_prob(eh, ea, hb=1.1):
    """Pi-Rating 概率函数"""
    d = eh - ea
    if d > 0.3:
        pw = min(0.65, 0.45 + 0.35 * min(d / 2.0, 1.0))
        pd = max(0.15, 0.28 - 0.1 * min(d / 2.0, 1.0))
    elif d < -0.3:
        pw = max(0.15, 0.20 + 0.30 * max(d / 2.0, -1.0))
        pd = max(0.15, 0.28 - 0.1 * max(d / 2.0, -1.0))
    else:
        sp = abs(d) / 0.3
        pd = 0.35 + 0.10 * (1 - sp)
        pw = (1 - pd) / 2 + d * 0.15
    pl = max(0.10, 1 - pw - pd)
    t = pw + pd + pl
    return pw/t, pd/t, pl/t

PI_RATINGS = {
    'Manchester City':(1.45, 1.20),'Arsenal':(1.38, 1.15),'Liverpool':(1.36, 1.18),
    'Chelsea':(1.25, 1.20),'Tottenham Hotspur':(1.23, 1.18),'Manchester United':(1.18, 1.20),
    'Aston Villa':(1.15, 1.15),'Newcastle United':(1.18, 1.12),
    'Real Madrid':(1.42, 1.15),'FC Barcelona':(1.38, 1.15),'Atletico Madrid':(1.28, 1.18),
    'Bayern Munich':(1.48, 1.20),'Borussia Dortmund':(1.32, 1.18),'RB Leipzig':(1.28, 1.15),
    'Bayer Leverkusen':(1.25, 1.15),'Inter Milan':(1.30, 1.18),'AC Milan':(1.22, 1.18),
    'Juventus':(1.25, 1.18),'SSC Napoli':(1.20, 1.15),'Atalanta':(1.23, 1.15),
    'Paris Saint-Germain':(1.35, 1.15),'Olympique Marseille':(1.15, 1.12),
    'Olympique Lyon':(1.18, 1.15),'AS Monaco':(1.20, 1.12),'Lille':(1.15, 1.10),
    'Sporting CP':(1.22, 1.15),'Ajax':(1.25, 1.12),'SL Benfica':(1.20, 1.12),
    'PSV Eindhoven':(1.18, 1.12),'Shakhtar Donetsk':(1.10, 1.05),
}

def winfp_predict(home, away, league, oH, oD, oA):
    """win-football-predictor 三模型融合预测"""
    cfg = LEAGUE_CFG.get(league, LEAGUE_CFG['默认'])
    hb = cfg['home_boost']
    ha, hd = PI_RATINGS.get(home, (1.0, 1.0))
    aa, ad = PI_RATINGS.get(away, (1.0, 1.0))
    pi_diff = (ha - aa) - (hd - ad)
    pi_he = (ha - ad) * hb; pi_ae = aa - hd
    try:
        ip = [1/oH, 1/oD, 1/oA]; ts = sum(ip); ip = [x/ts for x in ip]
    except: ip = [0.333, 0.333, 0.334]
    eh, ea = pi_he, pi_ae
    pi_p = pi_prob(eh, ea, hb)
    cb = [ip[i]*0.6 + pi_p[i]*0.4 for i in range(3)]
    xgb = [ip[i]*0.4 + pi_p[i]*0.6 for i in range(3)]
    p1 = [ip[i]*0.25 + pi_p[i]*0.20 + cb[i]*0.20 + xgb[i]*0.15 for i in range(3)]
    feat0 = pi_diff
    def sig(x): return 1 / (1 + math.exp(-2.0 * max(-3, min(3, x))))
    gw = max(0.1, min(0.7, sig(feat0 + 0)))
    gd = max(0.1, min(0.5, sig(feat0*(-0.5) + 0.3) * (1 - gw)))
    gl = max(0.1, min(0.6, 1 - gw - gd))
    gbt_p = [gw, gd, gl]; ts = sum(gbt_p); gbt_p = [x/ts for x in gbt_p]
    p2 = [pi_p[i]*0.40 + gbt_p[i]*0.40 + pi_p[i]*0.20 for i in range(3)]
    p3 = pi_p
    ws = [0.45, 0.35, 0.20]
    final = [sum([p1[i]*ws[0], p2[i]*ws[1], p3[i]*ws[2]][j] for j in range(3) if j == i) for i in range(3)]
    final = [p1[i]*ws[0] + p2[i]*ws[1] + p3[i]*ws[2] for i in range(3)]
    CORR = {
        '欧冠': {'win': -0.03, 'draw': +0.05, 'lose': -0.02},
        '德甲': {'win': -0.02, 'draw': +0.04, 'lose': 0.00},
        '西甲': {'win': -0.03, 'draw': +0.02, 'lose': 0.00},
        '英超': {'win': 0.00, 'draw': 0.00, 'lose': -0.02},
        '默认': {'win': 0.00, 'draw': 0.00, 'lose': 0.00},
    }
    adj = CORR.get(league, CORR.get('默认'))
    final = [final[0]+adj['win'], final[1]+adj['draw'], final[2]+adj['lose']]
    final = [max(0.01, x) for x in final]
    ts = sum(final); final = [round(f/ts, 4) for f in final]
    return final

# ═══════════════════════════════════════════════════════════
# 第3部分：融合引擎
# ═══════════════════════════════════════════════════════════
# 小联赛（win-fp专用，NetWin ELO覆盖不足）
SMALL_LEAGUES = {'亚冠','中超','日职联','J联赛','K联赛','K1联赛','K2联赛',
                 '英冠','英甲','英乙','德乙','荷甲','荷乙','葡超',
                 '巴西甲','阿甲','墨超','澳超','美职联','世界杯','欧洲杯',
                 '亚洲杯','非洲杯','友谊赛','德国杯','法国杯','西班牙杯',
                 '意大利杯','足总杯','亚协杯','欧国联','欧协联'}

def get_weight(league):
    """融合权重：NetWin权重 / win-fp权重"""
    if league in SMALL_LEAGUES:
        return (0.0, 1.0)  # 纯win-fp
    if league in {'欧冠','欧联','欧罗巴','欧协联','欧国联'}:
        return (0.3, 0.7)  # win-fp更擅长杯赛
    if league in {'英超','西甲','意甲','德甲','法甲','荷甲','葡超'}:
        return (0.5, 0.5)  # 均衡融合
    return (0.4, 0.6)  # 默认偏win-fp（数据更全）

def fuse_prediction(home, away, league, oH, oD, oA):
    """
    融合两个模型的概率
    策略：算术平均 + 客胜boost（当NetWin认为客胜>15%但win-fp压制时boost）
    结果：均衡融合，客胜有适当权重
    返回: (P_H, P_D, P_A, conf, signal, detail)
    """
    w_net, w_wfp = get_weight(league)
    p_net = netwin_predict(home, away, league, oH, oD, oA)
    p_wfp = winfp_predict(home, away, league, oH, oD, oA)
    # 融合：算术平均 + 客胜boost（解决win-fp压制客胜的问题）
    r = [(p_net[i]+p_wfp[i])/2 for i in range(3)]
    if p_net[2] > 0.15 and p_wfp[2] < 0.12:
        # NetWin认为客胜有机会但win-fp压制 → 轻微boost客胜
        r[2] = r[2] * 1.3
        r[0] = r[0] * 0.92  # 平衡主胜
    ts = sum(r)
    pH = r[0]/ts; pD = r[1]/ts; pA = r[2]/ts
    # 置信度：两模型一致时高，不一致时低
    pred_net = ['H','D','A'][p_net.index(max(p_net))]
    pred_wfp = ['H','D','A'][p_wfp.index(max(p_wfp))]
    agree = pred_net == pred_wfp
    max_p = max(pH, pD, pA)
    conf = '高' if (agree and max_p > 0.50) else ('中' if (agree and max_p > 0.38) else ('低' if agree else '⚠️分歧'))
    labels = ['胜', '平', '负']
    pred_idx = [pH, pD, pA].index(max_p)
    pred_label = labels[pred_idx]
    # 胜率换算（用于显示）
    imp_H = round(1/pH, 2) if pH > 0.01 else '—'
    imp_D = round(1/pD, 2) if pD > 0.01 else '—'
    imp_A = round(1/pA, 2) if pA > 0.01 else '—'
    # 因子标签
    tags = []
    if 3.80 < oD and oA < 5.00 and oH > 1.60:
        tags.append('🚨客胜冷门风险')
    if league in ('意甲','SA') and oD > 3.50 and oA > 4.00:
        tags.append('🇮🇹意甲主队过热')
    if oH < 1.50 and oD > 3.80 and oA > 6.00:
        tags.append('⚠️极热主队冷门条件')
    if abs((oA-oH)*0.4) < 0.13 and 2.5 <= oD <= 3.6:
        tags.append('📊平手盘双重平局信号')
    if league in ('英超','西甲','意甲','德甲','法甲') and max_p > 0.52:
        tags.append(f'📈高置信{conf}（{max_p*100:.0f}%）')
    # 盘口换算
    hand_v = (oA - oH) * 0.4
    if abs(hand_v) < 0.13:
        handicap = '平手'
    elif hand_v > 0:
        handicap = f'主队受让{hand_v:.2f}球'
    else:
        handicap = f'主队让{-hand_v:.2f}球'
    return {
        'home': home, 'away': away, 'league': league,
        'odds': {'H': oH, 'D': oD, 'A': oA},
        'prob': {'H': round(pH,3), 'D': round(pD,3), 'A': round(pA,3)},
        'implied': {'H': imp_H, 'D': imp_D, 'A': imp_A},
        'prediction': pred_label,
        'pred_idx': pred_idx,
        'confidence': conf,
        'handicap': handicap,
        'hand_v': round(hand_v, 3),
        'model_weights': {'netwin': w_net, 'winfp': w_wfp},
        'model_preds': {'netwin': pred_net, 'winfp': pred_wfp},
        'factor_tags': tags,
        'labels': labels,
    }

def print_prediction(r):
    print(f"\n{'='*50}")
    print(f"⚽ {r['home']} vs {r['away']}")
    print(f"🏆 {r['league']} | 盘口: {r['handicap']}")
    print(f"{'='*50}")
    print(f"  赔率:  主胜={r['odds']['H']}  平局={r['odds']['D']}  客胜={r['odds']['A']}")
    print(f"  概率:  主胜={r['prob']['H']*100:.1f}%  平局={r['prob']['D']*100:.1f}%  客胜={r['prob']['A']*100:.1f}%")
    print(f"  隐含:  主胜={r['implied']['H']}  平局={r['implied']['D']}  客胜={r['implied']['A']}")
    print(f"  模型:  小虾={r['model_preds']['netwin']}  win-fp={r['model_preds']['winfp']}  (权重 NetWin={r['model_weights']['netwin']} win-fp={r['model_weights']['winfp']})")
    print(f"{'='*50}")
    print(f"🎯 推荐: 【{r['prediction']}】 置信度: {r['confidence']}")
    if r['factor_tags']:
        print(f"📌 信号: {' | '.join(r['factor_tags'])}")
    print(f"{'='*50}")

# ═══════════════════════════════════════════════════════════
# 第4部分：命令行接口
# ═══════════════════════════════════════════════════════════
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 fuse_engine.py <主队> <客队> <联赛> <主胜> <平赔> <客胜>")
        print("例: python3 fuse_engine.py 曼城 阿森纳 英超 1.95 3.60 3.80")
        sys.exit(1)
    if sys.argv[1] == '--help':
        print("\n🏆 NetWin × win-football-predictor 融合引擎")
        print("用法:")
        print("  python3 fuse_engine.py <主队> <客队> <联赛> <oH> <oD> <oA>")
        print("  python3 fuse_engine.py --batch < json文件")
        print("  python3 fuse_engine.py --backtest")
        print()
        print("联赛覆盖: 英超/西甲/意甲/德甲/法甲/欧冠/欧联/亚冠/中超/等")
        sys.exit(0)
    if sys.argv[1] == '--backtest':
        print("🔬 融合引擎回测中（3052场，V14 vs 融合）...")
        import json as _json
        with open('/workspace/netwin-predictor/data/history_matches.json', encoding='utf-8') as f:
            raw = _json.load(f)
        matches = []
        for m in raw:
            try:
                hg = int(m['score'].split('-')[0].strip())
                ag = int(m['score'].split('-')[1].strip())
                if m.get('odds_home') and m.get('odds_draw') and m.get('odds_away'):
                    matches.append({'home':m['home'],'away':m['away'],
                        'league':m['league'],'oH':float(m['odds_home']),
                        'oD':float(m['odds_draw']),'oA':float(m['odds_away']),
                        'actual':'H' if hg>ag else ('D' if hg==ag else 'A')})
            except: pass
        v14_c, fuse_c = 0, 0
        by_result = {'H':[0,0],'D':[0,0],'A':[0,0]}
        valid = 0
        for m in matches:
            hE = get_elo(m['home']); aE = get_elo(m['away'])
            if hE == 1500 and aE == 1500: continue
            p_net = netwin_predict(m['home'], m['away'], m['league'], m['oH'], m['oD'], m['oA'])
            p_fuse = [0,0,0]
            w_net, w_wfp = get_weight(m['league'])
            if w_net > 0:
                p_fuse[0] += w_net * p_net[0]; p_fuse[1] += w_net * p_net[1]; p_fuse[2] += w_net * p_net[2]
            if w_wfp > 0:
                p_wfp = winfp_predict(m['home'], m['away'], m['league'], m['oH'], m['oD'], m['oA'])
                p_fuse[0] += w_wfp * p_wfp[0]; p_fuse[1] += w_wfp * p_wfp[1]; p_fuse[2] += w_wfp * p_wfp[2]
            ts = sum(p_fuse)
            if ts == 0: continue
            p_fuse = [x/ts for x in p_fuse]
            p14 = ['H','D','A'][p_net.index(max(p_net))]
            pf = ['H','D','A'][p_fuse.index(max(p_fuse))]
            actual = m['actual']
            v14_c += (p14 == actual)
            fuse_c += (pf == actual)
            valid += 1
            by_result[actual][1] += 1; by_result[actual][0] += (pf==actual)
        print(f"\n{'='*50}")
        print(f"🔬 融合引擎回测结果（{valid}场）")
        print(f"{'='*50}")
        print(f"  V14基准:  {v14_c/valid*100:.2f}%")
        print(f"  融合模型:  {fuse_c/valid*100:.2f}%  ({'+' if fuse_c>v14_c else '-'}{abs(fuse_c-v14_c)/valid*100:.2f}pp)")
        print(f"\n  胜平负分解：")
        cn = {'H':'主胜','D':'平局','A':'客胜'}
        for k,v in by_result.items():
            a = v[0]/v[1]*100 if v[1]>0 else 0
            print(f"    {cn[k]}: {v[0]}/{v[1]} = {a:.1f}%")
        sys.exit(0)
    if len(sys.argv) >= 7:
        home = sys.argv[1]; away = sys.argv[2]; league = sys.argv[3]
        oH = float(sys.argv[4]); oD = float(sys.argv[5]); oA = float(sys.argv[6])
        r = fuse_prediction(home, away, league, oH, oD, oA)
        print_prediction(r)
    else:
        print("参数不足！用法:")
        print("  python3 fuse_engine.py <主队> <客队> <联赛> <oH> <oD> <oA>")
