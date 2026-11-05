#!/usr/bin/env python3
"""
detect_markers.py — 从工程图片中提取附图标记
使用 images_understand MCP 工具分析图片中的数字标记
"""
import re, json, sys

def analyze_markers(image_path: str) -> dict:
    """
    使用 images_understand 分析图片中的附图标记
    返回格式：{"markers": [{"number": "100", "x": 361, "y": 111, "area": "顶部"}, ...]}
    """
    # 此函数由 Agent 通过 images_understand 工具调用
    # 以下为提示词模板，供 Agent 直接使用
    PROMPT_TEMPLATE = """这是一张工程示意图。请详细列出图中所有数字附图标记（如100、40、10等）：
1. 每个标记的数字编号
2. 每个标记在图中的位置区域（左/右/上/下/中间）
3. 标记引导线指向的部位描述

请用列表格式输出每个标记的：编号、位置、指向部位"""

    # 注：实际调用通过 Agent 的 images_understand 工具完成
    print("[detect_markers] 请使用 images_understand 工具分析图片")
    print(f"[detect_markers] 图片路径: {image_path}")
    return {}

def parse_marker_response(response_text: str) -> list:
    """
    解析 images_understand 返回的文本，提取标记列表
    """
    markers = []
    # 匹配形如 "100：离心管（顶部）" 或 "100 - 离心管" 的模式
    patterns = [
        r'[*\s]?(\d{2,3})\s*[:：]\s*([^（\n]+?)(?:（|$)',
        r'[*\s]?(\d{2,3})\s*[-–—]\s*([^\n]+?)(?:\n|$)',
    ]
    for pat in patterns:
        matches = re.findall(pat, response_text)
        for num, name in matches:
            name = name.strip()
            if name and len(name) > 0:
                markers.append({"number": num, "name": name})
    return markers

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 detect_markers.py <图片路径>")
        sys.exit(1)
    result = analyze_markers(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
