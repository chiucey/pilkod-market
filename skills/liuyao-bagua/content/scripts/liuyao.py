#!/usr/bin/env python3
"""
六爻八卦命理计算器
基于用户出生时间排出八字，并起六爻卦象进行解读
"""

import sys
from datetime import datetime, timedelta

# 天干
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 五行
WU_XING = ["木", "火", "土", "金", "水"]
WU_XING_GAN = ["甲乙木", "丙丁火", "戊己土", "庚辛金", "壬癸水"]
WU_XING_ZHI = ["寅卯木", "巳午火", "申酉金", "亥子水", "丑辰未戌土"]

# 八卦
BA_GUA = {
    0: ("☰", "乾", "天", "父亲", "金", "健"),
    1: ("☱", "兑", "泽", "少女", "金", "悦"),
    2: ("☲", "离", "火", "中女", "火", "丽"),
    3: ("☳", "震", "雷", "长男", "木", "动"),
    4: ("☴", "巽", "风", "长女", "木", "入"),
    5: ("☵", "坎", "水", "中男", "水", "陷"),
    6: ("☶", "艮", "山", "少男", "土", "止"),
    7: ("☷", "坤", "地", "母亲", "土", "顺"),
}

# 八卦对应数字（先天数）
BA_GUA_NUM = {
    "乾": 1, "兑": 2, "离": 3, "震": 4,
    "巽": 5, "坎": 6, "艮": 7, "坤": 8
}

# 六十四卦表（卦名，上卦，下卦）
HEXAGRAMS = [
    ("乾为天","乾","乾"), ("天泽履","乾","兑"), ("天火同人","乾","离"), ("天雷无妄","乾","震"),
    ("天风姤","乾","巽"), ("天水讼","乾","坎"), ("天山遯","乾","艮"), ("天地否","乾","坤"),
    ("泽天夬","兑","乾"), ("兑为泽","兑","兑"), ("泽火革","兑","离"), ("泽雷随","兑","震"),
    ("泽风大过","兑","巽"), ("泽水困","兑","坎"), ("泽山咸","兑","艮"), ("地泽临","兑","坤"),
    ("火天大有","离","乾"), ("火泽睽","离","兑"), ("离为火","离","离"), ("火雷噬嗑","离","震"),
    ("火风鼎","离","巽"), ("火水未济","离","坎"), ("火山旅","离","艮"), ("火地晋","离","坤"),
    ("雷天大壮","震","乾"), ("雷泽归妹","震","兑"), ("雷火丰","震","离"), ("震为雷","震","震"),
    ("雷风恒","震","巽"), ("雷水解","震","坎"), ("雷山小过","震","艮"), ("雷地豫","震","坤"),
    ("风天大畜","巽","乾"), ("风泽中孚","巽","兑"), ("风火家人","巽","离"), ("风雷益","巽","震"),
    ("巽为风","巽","巽"), ("风水涣","巽","坎"), ("风山渐","巽","艮"), ("风地观","巽","坤"),
    ("水天需","坎","乾"), ("水泽节","坎","兑"), ("水火既济","坎","离"), ("水雷屯","坎","震"),
    ("水风井","坎","巽"), ("坎为水","坎","坎"), ("水山蹇","坎","艮"), ("水地比","坎","坤"),
    ("山天大畜","艮","乾"), ("山泽损","艮","兑"), ("山火贲","艮","离"), ("山雷颐","艮","震"),
    ("山风蛊","艮","巽"), ("山水蒙","艮","坎"), ("艮为山","艮","艮"), ("山地剥","艮","坤"),
    ("地天泰","坤","乾"), ("地泽谦","坤","兑"), ("地火明夷","坤","离"), ("地雷复","坤","震"),
    ("地风升","坤","巽"), ("地水师","坤","坎"), ("地山谦","坤","艮"), ("坤为地","坤","坤"),
]

def lunar_year_gans(year):
    """计算年份天干"""
    return TIAN_GAN[(year - 4) % 10]

def lunar_year_zhi(year):
    """计算年份地支"""
    return DI_ZHI[(year - 4) % 12]

def lunar_month_gans(day_gan):
    """根据日干计算月干"""
    idx = TIAN_GAN.index(day_gan)
    return TIAN_GAN[(idx * 2 + 1) % 10]

def lunar_hour_gans(day_gan):
    """根据日干计算时干"""
    idx = TIAN_GAN.index(day_gan)
    return TIAN_GAN[(idx * 2) % 10]

def get_zhi_index(zhi):
    """地支索引"""
    return DI_ZHI.index(zhi)

def get_wu_xing(zhi):
    """根据地支判断五行"""
    if zhi in ["寅", "卯"]:
        return "木"
    elif zhi in ["巳", "午"]:
        return "火"
    elif zhi in ["申", "酉"]:
        return "金"
    elif zhi in ["亥", "子"]:
        return "水"
    else:
        return "土"

def calc_ba_gua_number(gua_str):
    """计算卦数"""
    return BA_GUA_NUM.get(gua_str, 1)

def generate_hexagram_index(year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi, hour_gan, hour_zhi):
    """起卦：上卦加下卦，再加动爻"""

    # 上卦数 = 年+月+日，取8余数
    upper_num = (TIAN_GAN.index(year_gan) + DI_ZHI.index(month_zhi) + TIAN_GAN.index(day_gan)) % 8
    # 下卦数 = 日+时，取8余数
    lower_num = (TIAN_GAN.index(day_gan) + DI_ZHI.index(hour_zhi)) % 8

    # 动爻：年+月+日+时，取6余数（1-6）
    total = TIAN_GAN.index(year_gan) + DI_ZHI.index(year_zhi) + \
            TIAN_GAN.index(month_gan) + DI_ZHI.index(month_zhi) + \
            TIAN_GAN.index(day_gan) + DI_ZHI.index(day_zhi) + \
            TIAN_GAN.index(hour_gan) + DI_ZHI.index(hour_zhi)
    dong_yao = (total % 6) + 1  # 1-6爻

    # 卦象索引
    gua_idx = upper_num * 8 + lower_num
    gua_idx = min(gua_idx, len(HEXAGRAMS) - 1)

    return gua_idx, upper_num, lower_num, dong_yao

def get_bazi(year, month, day, hour=12, minute=0):
    """排出八字"""
    try:
        dt = datetime(year, month, day, hour, minute)
    except:
        dt = datetime(year, month, day, 12, 0)

    # 年柱
    year_gan = lunar_year_gans(dt.year)
    year_zhi = lunar_year_zhi(dt.year)

    # 日柱（基准：1900年1月1日 0点 = 甲子）
    base = datetime(1900, 1, 1, 0, 0)
    days_passed = (dt - base).days

    day_gan = TIAN_GAN[days_passed % 10]
    day_zhi = DI_ZHI[days_passed % 12]

    # 时柱
    hour_zhi_idx = (dt.hour + 1) // 2 % 12
    hour_zhi = DI_ZHI[hour_zhi_idx]
    hour_gan = lunar_hour_gans(day_gan)

    # 月柱
    month_zhi_idx = (dt.month + 1) % 12
    month_zhi = DI_ZHI[month_zhi_idx]
    month_gan = lunar_month_gans(day_gan)

    return {
        "year": f"{year_gan}{year_zhi}",
        "month": f"{month_gan}{month_zhi}",
        "day": f"{day_gan}{day_zhi}",
        "hour": f"{hour_gan}{hour_zhi}",
        "year_gan": year_gan, "year_zhi": year_zhi,
        "month_gan": month_gan, "month_zhi": month_zhi,
        "day_gan": day_gan, "day_zhi": day_zhi,
        "hour_gan": hour_gan, "hour_zhi": hour_zhi,
    }

def generate_bagua_display(upper_idx, lower_idx, dong_yao, bazi):
    """生成六爻卦象显示"""

    # 获取卦的符号
    def get_gua_symbol(idx):
        return BA_GUA[idx % 8][0]

    def get_gua_name(idx):
        return BA_GUA[idx % 8][1]

    upper_gua = get_gua_name(upper_idx)
    lower_gua = get_gua_name(lower_idx)

    # 卦象（从下往上，6爻）
    # 每个卦由3爻组成，上卦3爻+下卦3爻
    upper_symbols = BA_GUA[upper_idx][0]
    lower_symbols = BA_GUA[lower_idx][0]

    gua_info = HEXAGRAMS[upper_idx * 8 + lower_idx]

    return {
        "upper_gua": upper_gua,
        "lower_gua": lower_gua,
        "upper_symbol": upper_symbols,
        "lower_symbol": lower_symbols,
        "hexagram_name": gua_info[0],
        "dong_yao": dong_yao,
        "bazi": bazi,
    }

def interpret_wu_xing(bazi):
    """解读五行"""
    year_wx = get_wu_xing(bazi["year_zhi"])
    month_wx = get_wu_xing(bazi["month_zhi"])
    day_wx = get_wu_xing(bazi["day_zhi"])
    hour_wx = get_wu_xing(bazi["hour_zhi"])

    wx_map = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    wx_map[year_wx] += 1
    wx_map[month_wx] += 1
    wx_map[day_wx] += 1
    wx_map[hour_wx] += 1

    return wx_map

def interpret_personality(bazi):
    """性格解读"""
    day_gan = bazi["day_gan"]
    day_zhi = bazi["day_zhi"]

    gan_interpret = {
        "甲": "仁慈、有领导力、积极进取、喜欢开创",
        "乙": "温柔、敏感、有韧性、善于变通",
        "丙": "热情、开朗、直接、有执行力",
        "丁": "细腻、有耐心、善于沟通、内心热忱",
        "戊": "稳重、踏实、诚实、注重积累",
        "己": "务实、包容、忠厚、善于策划",
        "庚": "果断、坚毅、刚强、有正义感",
        "辛": "细腻、精致、追求完美、善于表达",
        "壬": "聪明、灵活、胸襟宽广、善于谋略",
        "癸": "智慧、含蓄、深思熟虑、有直觉力",
    }

    zhi_interpret = {
        "子": "机智、灵活、善变、适应力强",
        "丑": "诚实、勤勉、保守、有耐力",
        "寅": "热情、有活力、有野心、积极",
        "卯": "柔和、善良、敏感、有艺术气质",
        "辰": "稳重、包容、有智慧、善于交际",
        "巳": "聪明、热情、有创造力、善于表达",
        "午": "热情、豪爽、正义感强、领导力强",
        "未": "温和、善良、有爱心、重感情",
        "申": "果断、机敏、有魄力、爱钻研",
        "酉": "细腻、有品位、追求完美、善于精打细算",
        "戌": "忠诚、可靠、有责任感、善于理财",
        "亥": "聪明、善良、有同情心、直觉力强",
    }

    return {
        "gan": gan_interpret.get(day_gan, "特质未明"),
        "zhi": zhi_interpret.get(day_zhi, "特质未明"),
    }

def main():
    if len(sys.argv) < 4:
        print("用法: python liuyao.py <年> <月> <日> [时] [分]")
        print("例: python liuyao.py 1990 5 15 14 30")
        sys.exit(1)

    year = int(sys.argv[1])
    month = int(sys.argv[2])
    day = int(sys.argv[3])
    hour = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    minute = int(sys.argv[5]) if len(sys.argv) > 5 else 0

    # 排八字
    bazi = get_bazi(year, month, day, hour, minute)

    # 起卦
    gua_idx, upper_idx, lower_idx, dong_yao = generate_hexagram_index(
        bazi["year_gan"], bazi["year_zhi"],
        bazi["month_gan"], bazi["month_zhi"],
        bazi["day_gan"], bazi["day_zhi"],
        bazi["hour_gan"], bazi["hour_zhi"],
    )

    # 卦象信息
    gua_info = generate_bagua_display(upper_idx, lower_idx, dong_yao, bazi)

    # 五行
    wx = interpret_wu_xing(bazi)

    # 性格
    personality = interpret_personality(bazi)

    # ====== 输出结果 ======
    print()
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃           六 爻 八 卦 · 命 理 详 解              ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print()
    print(f"  出生时间：{year}年{month}月{day}日 {hour:02d}:{minute:02d}")
    print()

    # 八字
    print("  【八字·四柱】")
    print(f"   年柱：{bazi['year']}  |  月柱：{bazi['month']}  |  日柱：{bazi['day']}  |  时柱：{bazi['hour']}")
    print()

    # 五行
    print("  【五行·力量分布】")
    wx_bar = ""
    for wx_name, wx_count in wx.items():
        wx_bar += f"  {wx_name} {'●' * wx_count}{'○' * (3 - wx_count)}"
    print(wx_bar)
    print()

    # 卦象
    upper_sym = gua_info["upper_symbol"]
    lower_sym = gua_info["lower_symbol"]
    print("  【六爻·卦象】")
    print(f"   上卦：{upper_sym} {gua_info['upper_gua']}  |  下卦：{lower_sym} {gua_info['lower_gua']}")
    print(f"   卦名：{gua_info['hexagram_name']}")
    print(f"   动爻：第{dong_yao}爻（{['初爻','二爻','三爻','四爻','五爻','上爻'][dong_yao-1]}）")
    print()

    # 性格
    print("  【性格·日主特质】")
    print(f"   日主：{bazi['day_gan']}（{personality['gan']}）")
    print(f"   日支：{bazi['day_zhi']}（{personality['zhi']}）")
    print()

    # 流年
    print("  【大运·走势】")
    year_element = get_wu_xing(bazi["year_zhi"])
    print(f"   年柱五行属：{year_element}，命盘以{bazi['day_zhi']}为日主")
    print(f"   喜用五行参考：木、火（命理喜忌需综合判断）")
    print()
    print("  【六爻简析】")
    print(f"   {gua_info['hexagram_name']}卦，上☰下☷相应，体用相生，")
    print(f"   运势平稳有进财之机，宜守正道，把握时机。")
    print()

    print("─" * 55)
    print("  ⚠️ 命理分析仅供娱乐参考，不能作为人生重大决策的唯一依据。")
    print("─" * 55)

if __name__ == "__main__":
    main()
