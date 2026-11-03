#!/usr/bin/env python3
"""
运势分析器
根据八字分析运势和趋吉避凶建议
"""

# 五行属性表
WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
          '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
          '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
          '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
          '戌': '土', '亥': '水'}

# 十神对应表（以日干为基准）
SHISHEN = {
    '甲': {'甲': '比肩', '乙': '劫财', '丙': '食神', '丁': '伤官', '戊': '偏财',
           '己': '正财', '庚': '七杀', '辛': '正官', '壬': '偏印', '癸': '正印'},
    '乙': {'甲': '劫财', '乙': '比肩', '丙': '伤官', '丁': '食神', '戊': '正财',
           '己': '偏财', '庚': '正官', '辛': '七杀', '壬': '正印', '癸': '偏印'},
    '丙': {'甲': '偏印', '乙': '正印', '丙': '比肩', '丁': '劫财', '戊': '食神',
           '己': '伤官', '庚': '偏财', '辛': '正财', '壬': '七杀', '癸': '正官'},
    '丁': {'甲': '正印', '乙': '偏印', '丙': '劫财', '丁': '比肩', '戊': '伤官',
           '己': '食神', '庚': '正财', '辛': '偏财', '壬': '正官', '癸': '七杀'},
    '戊': {'甲': '七杀', '乙': '正官', '丙': '偏印', '丁': '正印', '戊': '比肩',
           '己': '劫财', '庚': '食神', '辛': '伤官', '壬': '偏财', '癸': '正财'},
    '己': {'甲': '正官', '乙': '七杀', '丙': '正印', '丁': '偏印', '戊': '劫财',
           '己': '比肩', '庚': '伤官', '辛': '食神', '壬': '正财', '癸': '偏财'},
    '庚': {'甲': '偏财', '乙': '正财', '丙': '七杀', '丁': '正官', '戊': '偏印',
           '己': '正印', '庚': '比肩', '辛': '劫财', '壬': '食神', '癸': '伤官'},
    '辛': {'甲': '正财', '乙': '偏财', '丙': '正官', '丁': '七杀', '戊': '正印',
           '己': '偏印', '庚': '劫财', '辛': '比肩', '壬': '伤官', '癸': '食神'},
    '壬': {'甲': '食神', '乙': '伤官', '丙': '偏财', '丁': '正财', '戊': '七杀',
           '己': '正官', '庚': '偏印', '辛': '正印', '壬': '比肩', '癸': '劫财'},
    '癸': {'甲': '伤官', '乙': '食神', '丙': '正财', '丁': '偏财', '戊': '正官',
           '己': '七杀', '庚': '正印', '辛': '偏印', '壬': '劫财', '癸': '比肩'}
}

# 五行对应特征
WUXING_FEATURES = {
    '木': {'性格': '仁慈、正直、有上进心', '事业': '教育、文化、木材相关',
           '健康': '肝胆、神经系统', '颜色': '青、绿色'},
    '火': {'性格': '热情、主动、有领导力', '事业': '能源、光电、餐饮',
           '健康': '心脏、血液循环', '颜色': '红、紫色'},
    '土': {'性格': '稳重、诚信、有耐心', '事业': '房地产、农业、建筑',
           '健康': '脾胃、消化系统', '颜色': '黄、棕色'},
    '金': {'性格': '刚毅、果断、有决断力', '事业': '金融、金属加工、法律',
           '健康': '肺、呼吸系统', '颜色': '白、金色'},
    '水': {'性格': '聪明、灵活、有智慧', '事业': '贸易、物流、科技",
           '健康': '肾、泌尿系统', '颜色': '黑、蓝色'}
}

# 十神性格特征
SHISHEN_FEATURES = {
    '比肩': {'优点': '自信、独立、有毅力', '缺点': '固执、主观、不善变通'},
    '劫财': {'优点': '豪爽、义气、敢于冒险', '缺点': '冲动、鲁莽、易破财'},
    '食神': {'优点': '温和、善良、有才华', '缺点': '懒散、缺乏上进心'},
    '伤官': {'优点': '聪明、创新、口才好', '缺点': '叛逆、任性、易得罪人'},
    '偏财': {'优点': '慷慨、大方、善于交际', '缺点': '挥霍、缺乏耐心'},
    '正财': {'优点': '务实、稳重、守财', '缺点': '保守、不善投资'},
    '偏印': {'优点': '聪明、独立、善于分析', '缺点': '冷漠、孤僻、不善表达'},
    '正印': {'优点': '善良、包容、有耐心', '缺点': '依赖心强、不够果断'},
    '七杀': {'优点': '果断、勇敢、有魄力', '缺点': '冲动、暴躁、容易树敌'},
    '正官': {'优点': '正直、有责任心、守法', '缺点': '保守、缺乏魄力'}
}

def analyze_wuxing(wuxing_count):
    """分析五行强弱"""
    total = sum(wuxing_count.values())
    percentages = {k: round(v/total*100, 1) if total > 0 else 0 for k, v in wuxing_count.items()}

    max_wuxing = max(wuxing_count, key=wuxing_count.get)
    min_wuxing = min(wuxing_count, key=wuxing_count.get)

    return {
        'percentages': percentages,
        'strongest': max_wuxing,
        'weakest': min_wuxing,
        'imbalance': '过强' if wuxing_count[max_wuxing] >= 4 else ('过弱' if wuxing_count[min_wuxing] == 0 else '平衡')
    }

def get_yongshen(rizhu_gan, wuxing_analysis):
    """确定用神"""
    weakest = wuxing_analysis['weakest']
    # 用神是命主最需要的五行
    yongshen_map = {'木': '木', '火': '火', '土': '土', '金': '金', '水': '水'}
    return yongshen_map.get(weakest, '水')

def analyze_personality(bazi, wuxing_analysis, rizhu_gan):
    """分析性格特点"""
    features = []

    # 五行特征
    rizhu_wuxing = WUXING.get(rizhu_gan, '水')
    if rizhu_wuxing in WUXING_FEATURES:
        features.append(f"日主属{rizhu_wuxing}：{WUXING_FEATURES[rizhu_wuxing]['性格']}")

    # 八字整体五行分析
    if wuxing_analysis['imbalance'] == '过强':
        features.append(f"八字{wuxing_analysis['strongest']}气过旺，需注意{wuxing_analysis['weakest']}的补充")
    elif wuxing_analysis['imbalance'] == '过弱':
        features.append(f"八字{wuxing_analysis['weakest']}气不足，需要重点补{wuxing_analysis['weakest']}")

    return features

def generate_jiyu_advice(wuxing_analysis, rizhu_gan, yongshen):
    """生成趋吉避凶建议"""
    advice = {'favorable': [], 'avoid': []}

    # 吉方建议
    fangwei = {'木': '东方', '火': '南方', '土': '中央/东北', '金': '西方', '水': '北方'}
    yongshen_fangwei = fangwei.get(yongshen, '东方')
    advice['favorable'].append(f"本月吉方：{yongshen_fangwei}（补充{yongshen}气）")

    # 吉时建议
    advice['favorable'].append("吉时：辰时（7-9点）、午时（11-13点）")

    # 颜色建议
    colors = {'木': '青色、绿色', '火': '红色、紫色', '土': '黄色、棕色',
              '金': '白色、金色', '水': '黑色、蓝色'}
    advice['favorable'].append(f"幸运颜色：{colors.get(yongshen, '青色')}")

    # 数字建议
    numbers = {'木': '3、8', '火': '2、7', '土': '5、10', '金': '4、9', '水': '1、6'}
    advice['favorable'].append(f"幸运数字：{numbers.get(yongshen, '3')}")

    # 需要注意
    if wuxing_analysis['imbalance'] == '过强':
        avoid_wuxing = wuxing_analysis['strongest']
        advice['avoid'].append(f"避免过多接触{avoid_wuxing}属性的事物")

    return advice

def analyze_fortune(bazi, month=None):
    """综合运势分析"""
    wuxing_count = bazi.get('wuxing', {'木': 2, '火': 2, '土': 2, '金': 1, '水': 1})
    rizhu_gan = bazi.get('day', '甲')[0]

    wuxing_analysis = analyze_wuxing(wuxing_count)
    yongshen = get_yongshen(rizhu_gan, wuxing_analysis)
    personality = analyze_personality(bazi, wuxing_analysis, rizhu_gan)

    # 月度运势（模拟）
    monthly_score = 75 + (hash(str(month)) % 20) if month else 80

    fortune = {
        'summary': f'本月综合运势指数：{monthly_score}分',
        'score': monthly_score,
        'wuxing': wuxing_analysis,
        'yongshen': yongshen,
        'personality': personality,
        'lucky_direction': {'木': '东', '火': '南', '土': '东北', '金': '西', '水': '北'}.get(yongshen, '东'),
        'advice': generate_jiyu_advice(wuxing_analysis, rizhu_gan, yongshen)
    }

    return fortune

def format_fortune_report(bazi, fortune):
    """格式化运势报告"""
    report = f"""
╔══════════════════════════════════════════╗
║         八字命盘分析报告                 ║
╠══════════════════════════════════════════╣
║ 年柱：{bazi.get('year', 'XX')}（{bazi.get('shuxiang', 'XX')}年）         ║
║ 月柱：{bazi.get('month', 'XX')}                         ║
║ 日柱：{bazi.get('day', 'XX')}                         ║
║ 时柱：{bazi.get('hour', 'XX')}                         ║
╠══════════════════════════════════════════╣
║ 五行分布：                               ║
║ 木:{fortune['wuxing']['percentages'].get('木', 0)}% 火:{fortune['wuxing']['percentages'].get('火', 0)}% 土:{fortune['wuxing']['percentages'].get('土', 0)}%    ║
║ 金:{fortune['wuxing']['percentages'].get('金', 0)}% 水:{fortune['wuxing']['percentages'].get('水', 0)}%              ║
╠══════════════════════════════════════════╣
║ 日主：{fortune.get('rizhu_gan', bazi.get('day', 'XX')[0])} 五行属{fortune.get('rizhu_wuxing', '木')}       ║
║ 用神：{fortune['yongshen']}                               ║
║ 命格：{fortune['wuxing']['imbalance']}                       ║
╚══════════════════════════════════════════╝

🌟 【运势分析】

{fortune['summary']}

💼 【事业财运】
本月事业运势{'较好' if fortune['score'] > 75 else '一般'}，适合在{fortune['lucky_direction']}方发展。创业或投资需谨慎，建议保守策略。

❤️ 【感情姻缘】
本月感情运势平稳，已有伴侣者关系和睦。

🏥 【健康提醒】
注意休息，避免过度劳累。

🧭 【趋吉避凶指南】

✅ 吉利事项：
"""
    for item in fortune['advice']['favorable']:
        report += f"   • {item}\n"

    report += "\n⚠️ 注意事项：\n"
    for item in fortune['advice']['avoid']:
        report += f"   • {item}\n"

    colors = {'木': '青色', '火': '红色', '土': '黄色', '金': '白色', '水': '黑色'}
    report += "\n📌 开运建议：\n"
    report += f"   1. 多往{fortune['lucky_direction']}方走动\n"
    report += f"   2. 佩戴{colors.get(fortune['yongshen'], '青色')}系饰品\n"
    report += f"   3. 保持心情愉悦，避免争执\n"

    return report

if __name__ == '__main__':
    # 测试
    from bazi_calculator import calculate_bazi, get_wuxing

    test_bazi = calculate_bazi(1990, 5, 15, 10, '男')
    test_bazi['wuxing'] = get_wuxing(test_bazi)
    fortune = analyze_fortune(test_bazi, month=3)
    print(format_fortune_report(test_bazi, fortune))
