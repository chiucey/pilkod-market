#!/usr/bin/env python3
"""
林肯舆情日报生成器
根据Excel数据文件自动生成舆情日报文字版
"""

import pandas as pd
from collections import Counter
import sys
from datetime import datetime
from difflib import SequenceMatcher


def similar(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, a, b).ratio()


def remove_similar_titles(titles_dict, threshold=0.80):
    """去除相似标题，只保留第一个"""
    seen_titles = []
    filtered = {}

    for title, data in titles_dict.items():
        is_similar = False
        for seen_title in seen_titles:
            if similar(title, seen_title) >= threshold:
                is_similar = True
                break

        if not is_similar:
            seen_titles.append(title)
            filtered[title] = data

    return filtered


def extract_topic_tags(title, max_len=35):
    """提取话题标签和核心内容，精简标题"""
    if len(title) <= max_len:
        return title

    # 如果是话题标签类，提取林肯相关内容
    if '#' in title:
        # 提取包含林肯关键词的核心内容和话题标签
        lincoln_related = []
        parts = title.split('#')
        for part in parts:
            if '林肯' in part or '航海家' in part or '飞行家' in part or '冒险家' in part or 'Z' in part:
                lincoln_related.append('#' + part.strip())

        if lincoln_related:
            # 取前两个林肯相关标签 + 开头内容
            first_part = parts[0][:15] if parts[0] else ''
            tags = ' '.join(lincoln_related[:2])
            result = (first_part + ' ' + tags).strip()
            if len(result) > max_len:
                return result[:max_len] + '...'
            return result

    # 如果是长文本，取前35字
    if len(title) > max_len:
        return title[:max_len] + '...'
    return title


def merge_similar_topics(positive_top):
    """合并相似的正面话题"""
    merged = []
    seen_keywords = {}

    for title, data in positive_top:
        # 提取关键词判断是否重复
        platform_count = int(data['平台数'])
        repost = int(data['总转载量']) if pd.notna(data['总转载量']) else 0

        # 张雪机车类
        if '张雪' in title or '机车' in title:
            key = '张雪机车'
            if key in seen_keywords:
                seen_keywords[key]['平台数'] += platform_count
                seen_keywords[key]['总转载量'] += repost
            else:
                seen_keywords[key] = {'平台数': platform_count, '总转载量': repost, '标题': '#张雪机车 #林肯驾趣YYDS'}
            continue

        # 航海家安全感类
        if '安全感' in title or '放心' in title or '安全' in title:
            key = '航海家安全感'
            if key in seen_keywords:
                seen_keywords[key]['平台数'] += platform_count
                seen_keywords[key]['总转载量'] += repost
            else:
                seen_keywords[key] = {'平台数': platform_count, '总转载量': repost, '标题': '#安全还得看林肯'}
            continue

        # 春游拍照类
        if '拍花' in title or '春游' in title or '躺平' in title:
            key = '春游拍照'
            if key in seen_keywords:
                seen_keywords[key]['平台数'] += platform_count
                seen_keywords[key]['总转载量'] += repost
            else:
                seen_keywords[key] = {'平台数': platform_count, '总转载量': repost, '标题': '#花是春游出片关键词'}
            continue

        # 新江湾城类
        if '新江湾城' in title or '松弛' in title:
            key = '新江湾城'
            if key in seen_keywords:
                seen_keywords[key]['平台数'] += platform_count
                seen_keywords[key]['总转载量'] += repost
            else:
                seen_keywords[key] = {'平台数': platform_count, '总转载量': repost, '标题': '开着林肯航海家解锁新江湾城松弛感'}
            continue

        # 梦谷类
        if '梦谷' in title:
            key = '梦谷'
            if key in seen_keywords:
                seen_keywords[key]['平台数'] += platform_count
                seen_keywords[key]['总转载量'] += repost
            else:
                seen_keywords[key] = {'平台数': platform_count, '总转载量': repost, '标题': '周日放假开林肯航海家去梦谷体验'}
            continue

        # 山路类
        if '山路' in title or '跑山' in title or '重庆' in title:
            key = '山路'
            if key in seen_keywords:
                seen_keywords[key]['平台数'] += platform_count
                seen_keywords[key]['总转载量'] += repost
            else:
                seen_keywords[key] = {'平台数': platform_count, '总转载量': repost, '标题': '重庆崽儿开林肯山路驾驶体验分享'}
            continue

        # 其他话题保留原样
        merged.append((extract_topic_tags(title, 35), platform_count, repost))

    # 将合并的话题添加到结果
    for key, data in seen_keywords.items():
        title_prefix = {
            '张雪机车': '20年死磕技术张雪带梦想登顶',
            '航海家安全感': '论安全感航海家实力不必多说',
            '春游拍照': '出门哪有不拍花的',
            '新江湾城': '开着林肯航海家解锁新江湾城松弛感',
            '梦谷': '周日放假开林肯航海家去梦谷体验',
            '山路': '重庆崽儿开林肯山路驾驶体验分享'
        }
        full_title = f"{title_prefix.get(key, key)} {data['标题']}"
        merged.append((extract_topic_tags(full_title, 40), data['平台数'], data['总转载量']))

    # 按转载量排序，取TOP 8
    merged.sort(key=lambda x: x[2], reverse=True)
    return merged[:8]


def analyze_lincoln_report(excel_path: str) -> str:
    """
    分析林肯舆情Excel数据并生成日报文字版

    Args:
        excel_path: Excel文件路径

    Returns:
        生成的日报文字内容
    """
    # 读取Excel文件，自动检测sheet名和header位置
    xl = pd.ExcelFile(excel_path)
    sheet_name = xl.sheet_names[0]  # 使用第一个sheet

    # 尝试检测header位置
    try:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=1)
        if '情感' not in df.columns:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)
    except:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=0)

    total_count = len(df)

    # 情感分布
    emotion_counts = df['情感'].value_counts()
    positive_count = emotion_counts.get('正面', 0)
    neutral_count = emotion_counts.get('中性', 0)
    negative_count = emotion_counts.get('负面', 0)

    positive_pct = round(positive_count / total_count * 100)
    neutral_pct = round(neutral_count / total_count * 100)
    negative_pct = round(negative_count / total_count * 100)

    # TOP 5 传播平台（具体媒体）
    platform_counts = df['媒体名称'].value_counts().head(5)
    top_platforms = []
    for platform, count in platform_counts.items():
        top_platforms.append(f"{platform}{count}条")

    # 正面话题（按标题分组统计）
    positive_df = df[df['情感'] == '正面'].copy()
    positive_grouped = positive_df.groupby('标题').agg({
        '媒体名称': 'count',
        '转载数量': 'sum'
    }).rename(columns={'媒体名称': '平台数', '转载数量': '总转载量'})

    positive_dict = positive_grouped.to_dict('index')
    positive_filtered = remove_similar_titles(positive_dict, threshold=0.80)
    positive_top = sorted(positive_filtered.items(), key=lambda x: x[1]['总转载量'], reverse=True)[:10]
    positive_merged = merge_similar_topics(positive_top)

    # 敏感话题（按标题分组统计）
    negative_df = df[df['情感'] == '负面'].copy()
    negative_grouped = negative_df.groupby('标题').agg({
        '媒体名称': lambda x: ', '.join(sorted(set(x))),
        '转载数量': 'sum'
    }).rename(columns={'媒体名称': '平台', '转载数量': '总转载量'})

    negative_dict = negative_grouped.to_dict('index')
    negative_filtered = remove_similar_titles(negative_dict, threshold=0.75)
    negative_top = sorted(negative_filtered.items(), key=lambda x: x[1]['总转载量'], reverse=True)[:8]

    # 敏感话题平台分布TOP 5
    negative_platform_counts = df[df['情感'] == '负面']['媒体名称'].value_counts().head(5)
    negative_platforms = []
    for platform, count in negative_platform_counts.items():
        negative_platforms.append(f"{platform}{count}条")

    # 生成日报
    report = f"""林肯舆情日报-0403（2026年4月2日16:00-2026年4月3日16:00）

1. 声量
   截至4月3日16点，相关信息共计传播{total_count}条。其中：正面信息{positive_count}条，占比{positive_pct}%；中性信息{neutral_count}条，占比{neutral_pct}%；敏感信息{negative_count}条，占比{negative_pct}%

2. 今日正面传播话题
   2.1 主要围绕"产品种草""品牌传播""用户体验""行业资讯"等内容方向展开
"""

    # 添加正面话题
    for idx, (title, platforms, repost) in enumerate(positive_merged, 1):
        report += f"     2.1.{idx} {title}（{platforms}个平台，总转载{repost}次）\n"

    report += f"   2.2 TOP 5传播平台：{', '.join(top_platforms)}\n"

    report += """
3. 今日敏感话题
   3.1 主要围绕"品牌评价""市场讨论""二线豪华品牌危机"等内容方向展开
"""

    # 添加敏感话题
    for idx, (title, data) in enumerate(negative_top, 1):
        short_title = extract_topic_tags(title, 35)
        platforms = data['平台']
        repost = int(data['总转载量']) if pd.notna(data['总转载量']) else 0
        report += f"     3.1.{idx} {short_title}（{platforms}，总转载{repost}次）\n"

    report += f"   3.2 TOP 5传播平台：{', '.join(negative_platforms)}\n"

    report += """
---"""

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python lincoln_report.py <excel_file_path>")
        print("Example: python lincoln_report.py /path/to/林肯-舆情监测-4月2日16时-4月3日16时.xlsx")
        sys.exit(1)

    excel_path = sys.argv[1]
    report = analyze_lincoln_report(excel_path)
    print(report)


if __name__ == "__main__":
    main()
