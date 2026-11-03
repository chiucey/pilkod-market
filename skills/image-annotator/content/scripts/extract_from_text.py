#!/usr/bin/env python3
"""
extract_from_text.py — 从用户提供的文字内容中提取附图标记对应关系
支持格式：
  - 部件名称[编号]  →  编号:部件名称
  - 部件名称（编号）  →  编号:部件名称
  - 编号：部件名称   →  编号:部件名称
"""
import re, sys, json

# 常见前缀词（与部件名连写时会被误识别），遇到这些认为名称结束
PREFIX_WORDS = ['包括', '具有', '设有', '设置', '安装', '连接', '配合', '抵接',
                '封堵', '盖合', '螺纹', '固定', '活动', '可拆卸', '两端', '顶部',
                '底部', '侧壁', '内壁', '外壁', '槽底', '远离', '靠近', '贯穿',
                '固设', '旋合', '滑动', '滑移', '相向', '相背', '贯穿']

CN_PUNCT = '，。、；：""''（）【】《》'

def clean_name(s):
    """清理名字：移除首尾标点、常见前缀词、截断超长内容"""
    s = s.strip()
    while s and s[0] in CN_PUNCT:
        s = s[1:]
    for pw in PREFIX_WORDS:
        if s.startswith(pw):
            s = s[len(pw):]
            break
    while s and s[-1] in CN_PUNCT:
        s = s[:-1]
    s = s.strip()
    # 部件名通常不超过10字
    return s[:10] if len(s) > 10 else s

def extract_from_text(text: str) -> dict:
    """从技术文字中提取附图标记对应关系"""
    mapping = {}

    # 模式1：部件名称[编号]  例如：离心管[100]
    pattern1 = re.compile(
        r'([^\[\]\n，。、；：""''（）【】《》\s]{2,10})\s*\[\s*(\d{2,3})\s*\]')
    for raw_name, num in pattern1.findall(text):
        name = clean_name(raw_name)
        if name and num:
            mapping[num] = name

    # 模式2：编号：部件名称  例如：100：离心管
    pattern2 = re.compile(
        r'\b(\d{2,3})\s*[:：\-–—]\s*([^\n\[\]，。、；：""''（）【】《》\s]{1,15})')
    for num, raw_name in pattern2.findall(text):
        name = clean_name(raw_name)
        if name and num and num not in mapping:
            mapping[num] = name

    # 模式3：部件名称（编号）  例如：离心管（100）
    pattern3 = re.compile(
        r'([^\n\[\]，。、；：""''（）【】《》\s]{1,10})\s*（\s*(\d{2,3})\s*）')
    for raw_name, num in pattern3.findall(text):
        name = clean_name(raw_name)
        if name and num and num not in mapping:
            mapping[num] = name

    return mapping

def format_mapping_table(mapping: dict) -> str:
    """格式化输出对应表"""
    if not mapping:
        return "未找到任何附图标记对应关系"
    lines = ["## 附图标记对应表\n",
             "| 编号 | 部件名称 |",
             "|------|----------|"]
    for num, name in sorted(mapping.items(), key=lambda x: int(x[0])):
        lines.append(f"| {num} | {name} |")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 extract_from_text.py <文字文件路径>")
        print("      或通过管道输入: cat text.txt | python3 extract_from_text.py")
        sys.exit(1)

    filepath = sys.argv[1]
    if filepath == "-":
        text = sys.stdin.read()
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

    mapping = extract_from_text(text)
    print(f"\n共提取到 {len(mapping)} 个附图标记：\n")
    print(format_mapping_table(mapping))
    print("\n[DEBUG]", json.dumps(mapping, ensure_ascii=False))
