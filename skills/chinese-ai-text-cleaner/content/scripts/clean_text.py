#!/usr/bin/env python3
"""
中文AI文本排版清洗脚本
将AI生成的中文文本规范化中文排版格式
"""

import re
import sys

def clean_chinese_text(text: str) -> str:
    """清洗中文文本，规范化排版"""

    # 1. 标点符号规范化 - 半角转全角
    replacements = {
        ',': '，',
        ';': '；',
        ':': '：',
        '?': '？',
        '!': '！',
        '(': '（',
        ')': '）',
    }

    for half, full in replacements.items():
        text = text.replace(half, full)

    # 2. 引号处理 - 英文双引号 "" 转中文左右引号
    # 英文双引号在文本中成对出现：第一个是开引号，第二个是闭引号
    # 需要交替替换：第1、3、5...个 " 换成左引号，第2、4、6...个 " 换成右引号
    quote_count = 0
    result = []
    for char in text:
        if char == '"':
            if quote_count % 2 == 0:
                result.append('\u201c')  # 左引号
            else:
                result.append('\u201d')  # 右引号
            quote_count += 1
        else:
            result.append(char)
    text = ''.join(result)
    # 英文单引号转中文
    text = text.replace("'", '\u2018').replace("'", '\u2019')
    
    # 2.1 破折号处理 - 英文双破折号转中文，再删除所有破折号
    text = text.replace('--', '——')
    text = text.replace('---', '——')
    # 删除所有破折号（用户要求去掉所有破折号）
    text = text.replace('——', '')

    # 3. 句号处理（句末句号单独处理，避免误伤英文缩写）
    # 先处理独立成句的句号
    text = re.sub(r'\.([\s\n])', r'。\1', text)
    # 处理句末句号（后面是空格或结束）
    text = re.sub(r'\.([\s\n]|$)', r'。\1', text)

    # 4. 省略号处理
    text = re.sub(r'\.{5,}', '……', text)
    text = re.sub(r'…{2,}', '……', text)
    text = text.replace('…', '……')

    # 5. 连接符处理 - 删除多余的 em dash
    # 保留对话中的转折破折号，删除机械的连接
    text = re.sub(r'--+', '--', text)
    # 删除句中多余的 "--"（非对话转折）
    text = re.sub(r'([，。；：、])[\s]*--[\s]*', r'\1', text)
    text = re.sub(r'^--[\s]*', '', text, flags=re.MULTILINE)

    # 6. 空格清理
    # 删除英文词与中文之间的空格
    text = re.sub(r'([a-zA-Z0-9])[\s]+([\u4e00-\u9fff])', r'\1\2', text)
    text = re.sub(r'([\u4e00-\u9fff])[\s]+([a-zA-Z0-9])', r'\1\2', text)
    # 删除句首句尾空格
    text = re.sub(r'^[ \t]+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    # 合并多个空格为单个
    text = re.sub(r' {2,}', ' ', text)

    # 7. AI冗余表达清洗
    ai_phrases = [
        '首先，我需要说明的是',
        '需要注意的是',
        '值得注意的是',
        '一般来说',
        '通常情况下',
        '从某种意义上来说',
        '综上所述',
        '总之，',
    ]

    for phrase in ai_phrases:
        text = text.replace(phrase, '')

    # 8. 清理机械列表过渡
    mechanical_phrases = [
        (r'首先，', ''),
        (r'其次，', ''),
        (r'最后，', ''),
        (r'\n首先，', '\n'),
        (r'\n其次，', '\n'),
        (r'\n最后，', '\n'),
    ]

    for pattern, replacement in mechanical_phrases:
        text = re.sub(pattern, replacement, text)

    # 9. 连续标点清理
    text = re.sub(r'[，。！？]{3,}', '……', text)

    # 10. 段落空行规范化
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def main():
    if len(sys.argv) > 1:
        # 从文件读取
        input_file = sys.argv[1]
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # 从 stdin 读取
        content = sys.stdin.read()

    cleaned = clean_chinese_text(content)

    if len(sys.argv) > 2:
        output_file = sys.argv[2]
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print(f"已清洗并保存到: {output_file}")
    else:
        print(cleaned)


if __name__ == '__main__':
    main()
