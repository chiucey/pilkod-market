#!/usr/bin/env python3
"""
八字排盘计算器
用于计算八字四柱的天干地支
"""

# 天干表
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
# 地支表
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
# 属相表
SHUXIANG = ['猴', '鸡', '狗', '猪', '鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊']

# 节气与月支对应表（以节为界）
JIEQI_MONTH = {
    (2, 4): '寅', (3, 6): '卯', (4, 5): '辰',
    (5, 6): '巳', (6, 6): '午', (7, 7): '未',
    (8, 8): '申', (9, 8): '酉', (10, 8): '戌',
    (11, 8): '亥', (12, 8): '子', (1, 6): '丑'
}

def get_nianzhu(year):
    """计算年柱"""
    gan_index = (year - 3) % 10
    zhi_index = (year - 3) % 12
    return TIANGAN[gan_index] + DIZHI[zhi_index], SHUXIANG[zhi_index]

def get_yuezhu(year, month, day):
    """计算月柱（简化版，以节气估算）"""
    # 简化计算：使用月份估算月支
    if month == 1:
        if day < 20:
            return '癸丑'
        else:
            return '甲寅'
    elif month == 2:
        if day < 19:
            return '甲寅'
        else:
            return '乙卯'
    elif month == 3:
        if day < 21:
            return '乙卯'
        else:
            return '丙辰'
    elif month == 4:
        if day < 20:
            return '丙辰'
        else:
            return '丁巳'
    elif month == 5:
        if day < 21:
            return '丁巳'
        else:
            return '戊午'
    elif month == 6:
        if day < 22:
            return '戊午'
        else:
            return '己未'
    elif month == 7:
        if day < 23:
            return '己未'
        else:
            return '庚申'
    elif month == 8:
        if day < 23:
            return '庚申'
        else:
            return '辛酉'
    elif month == 9:
        if day < 23:
            return '辛酉'
        else:
            return '壬戌'
    elif month == 10:
        if day < 24:
            return '壬戌'
        else:
            return '癸亥'
    elif month == 11:
        if day < 23:
            return '癸亥'
        else:
            return '甲子'
    else:  # month == 12
        if day < 22:
            return '甲子'
        else:
            return '乙丑'

def get_yuezhu_gan(year, month, day):
    """根据年干计算月干"""
    yuezhu_zhi = get_yuezhu(year, month, day)[1]
    # 月干口诀：甲己之年丙作首，乙庚之年戊为头
    # 丙辛必定寻庚起，丁壬壬位顺行流
    # 戊癸之年何方发，甲寅之上好追求
    if year % 10 in [0, 5]:  # 甲、己年
        start_gan = 2  # 丙
    elif year % 10 in [1, 6]:  # 乙、庚年
        start_gan = 4  # 戊
    elif year % 10 in [2, 7]:  # 丙、辛年
        start_gan = 6  # 庚
    elif year % 10 in [3, 8]:  # 丁、壬年
        start_gan = 8  # 壬
    else:  # 戊、癸年
        start_gan = 0  # 甲

    # 计算月支索引(0=寅,1=卯,...,11=丑)
    zhi_to_index = {'寅': 0, '卯': 1, '辰': 2, '巳': 3, '午': 4, '未': 5,
                    '申': 6, '酉': 7, '戌': 8, '亥': 9, '子': 10, '丑': 11}
    gan_index = (start_gan + zhi_to_index[yuezhu_zhi]) % 10
    return TIANGAN[gan_index]

def get_rizhu(year, month, day):
    """计算日柱（简化版，需查询万年历）"""
    # 这是简化版，实际需要万年历查询
    # 基数为1900年1月1日是甲子日
    from datetime import date
    base_date = date(1900, 1, 1)
    current_date = date(year, month, day)
    days_diff = (current_date - base_date).days

    gan_index = days_diff % 10
    zhi_index = days_diff % 12
    return TIANGAN[gan_index] + DIZHI[zhi_index]

def get_shizhu(hour):
    """计算时柱"""
    # 时支: 23-1子, 1-3丑, 3-5寅, 5-7卯, 7-9辰, 9-11巳, 11-13午, 13-15未, 15-17申, 17-19酉, 19-21戌, 21-23亥
    if 23 <= hour or hour < 1:
        zhi = '子'
    elif 1 <= hour < 3:
        zhi = '丑'
    elif 3 <= hour < 5:
        zhi = '寅'
    elif 5 <= hour < 7:
        zhi = '卯'
    elif 7 <= hour < 9:
        zhi = '辰'
    elif 9 <= hour < 11:
        zhi = '巳'
    elif 11 <= hour < 13:
        zhi = '午'
    elif 13 <= hour < 15:
        zhi = '未'
    elif 15 <= hour < 17:
        zhi = '申'
    elif 17 <= hour < 19:
        zhi = '酉'
    elif 19 <= hour < 21:
        zhi = '戌'
    else:
        zhi = '亥'

    # 时干计算: 甲己还生甲，乙庚丙作初
    # 丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
    if hour < 1 or 23 <= hour:
        start_gan = 0  # 甲
    elif 1 <= hour < 3:
        start_gan = 1  # 乙
    elif 3 <= hour < 5:
        start_gan = 2  # 丙
    elif 5 <= hour < 7:
        start_gan = 3  # 丁
    elif 7 <= hour < 9:
        start_gan = 4  # 戊
    elif 9 <= hour < 11:
        start_gan = 5  # 己
    elif 11 <= hour < 13:
        start_gan = 6  # 庚
    elif 13 <= hour < 15:
        start_gan = 7  # 辛
    elif 15 <= hour < 17:
        start_gan = 8  # 壬
    elif 17 <= hour < 19:
        start_gan = 9  # 癸
    elif 19 <= hour < 21:
        start_gan = 0  # 甲
    else:
        start_gan = 1  # 乙

    return TIANGAN[start_gan] + zhi

def calculate_bazi(year, month, day, hour, gender):
    """计算完整八字"""
    nianzhu, shuxiang = get_nianzhu(year)
    yuezhu_zhi = get_yuezhu(year, month, day)
    yuezhu_gan = get_yuezhu_gan(year, month, day)
    yuezhu = yuezhu_gan + yuezhu_zhi
    rizhu = get_rizhu(year, month, day)
    shizhu = get_shizhu(hour)

    return {
        'year': nianzhu,
        'month': yuezhu,
        'day': rizhu,
        'hour': shizhu,
        'shuxiang': shuxiang,
        'gender': gender,
        'birth_date': f'{year}年{month}月{day}日{hour}时'
    }

def get_wuxing(bazi):
    """分析八字五行"""
    wuxing_map = {
        '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
        '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
        '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
        '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
        '戌': '土', '亥': '水'
    }

    all_chars = bazi['year'] + bazi['month'] + bazi['day'] + bazi['hour']
    wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}

    for char in all_chars:
        if char in wuxing_map:
            wuxing_count[wuxing_map[char]] += 1

    return wuxing_count

def get_rizhu_gan(bazi):
    """获取日干（用于十神分析）"""
    return bazi['day'][0]

if __name__ == '__main__':
    # 测试
    result = calculate_bazi(1990, 5, 15, 10, '男')
    print('八字:', result)
    print('五行:', get_wuxing(result))
