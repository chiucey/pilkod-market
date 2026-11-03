#!/usr/bin/env python3
"""
根据关键词规则，将播客文案智能切分成场景段落
每个场景输出一行：序号|场景描述|对应文案摘要
"""
import sys
import re

# 场景切分关键词规则（用于识别段落主题切换）
SCENE_RULES = [
    # 关键词, 场景编号前缀, 场景标题
    (r'欢迎收听|开场|欢迎|大家好', '开场', '开场白'),
    (r'三位食材|食材|搭配|主角', '食材', '三大食材亮相'),
    (r'牛大力|补腰|强筋骨|久坐|腰肾', '功效', '牛大力功效'),
    (r'枸杞|养肝|明目|眼睛|眼干', '枸杞', '枸杞功效'),
    (r'猪尾|胶原蛋白|猪蹄|胶质', '猪尾', '猪尾功效'),
    (r'核心|总结|三大功效|补腰.*养肝|养肝.*补腰', '总结', '功效总结'),
    (r'做法|烹饪|炖|焯水|制作|步骤', '做法', '烹饪方法'),
    (r'多久|每周|一次|坚持|建议|食用', '建议', '食用建议'),
    (r'拜拜|下期|再见|照顾|结尾|结束', '结尾', '温馨结尾'),
]

def split_scenes(paragraphs):
    """
    将段落列表切分为场景
    返回: list[dict] 每个元素含 scene_id, title, description, full_text
    """
    full_text = '\n'.join(paragraphs)
    scenes = []
    current_scene = None
    current_lines = []

    # 尝试按句子断点切分（对话形式的播客文案）
    # 合并所有文字后，按主题关键词切分
    lines = full_text.split('。')

    scene_map = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        matched = None
        for keyword, scene_key, scene_title in SCENE_RULES:
            if re.search(keyword, line):
                matched = (scene_key, scene_title, line)
                break
        if matched:
            scene_key, scene_title, line = matched
            if scene_key not in scene_map:
                scene_map[scene_key] = {'title': scene_title, 'lines': []}
            if line:
                scene_map[scene_key]['lines'].append(line + '。')

    # 按预定顺序排列，补充缺失的场景
    ordered = []
    for keyword, scene_key, scene_title in SCENE_RULES:
        if scene_key in scene_map:
            full = ''.join(scene_map[scene_key]['lines'])
            # 限制描述长度
            desc = full[:80] + ('...' if len(full) > 80 else '')
            ordered.append({
                'scene_id': len(ordered) + 1,
                'scene_key': scene_key,
                'title': scene_title,
                'description': desc,
                'full_text': full
            })

    return ordered

if __name__ == '__main__':
    paragraphs = [line.strip() for line in sys.stdin if line.strip()]
    scenes = split_scenes(paragraphs)
    for s in scenes:
        print(f"---SCENE---")
        print(f"id:{s['scene_id']}")
        print(f"title:{s['title']}")
        print(f"desc:{s['description']}")
        print(f"text:{s['full_text']}")
