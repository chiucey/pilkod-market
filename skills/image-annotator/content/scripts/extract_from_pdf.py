#!/usr/bin/env python3
"""
extract_from_pdf.py — 从 PDF 文件中提取附图标记说明
使用 images_understand 工具读取 PDF 内容
"""
import sys, json, re, os

def extract_from_pdf(pdf_path: str) -> dict:
    """
    从 PDF 中提取附图标记说明
    返回格式：{"100": "离心管", "40": "管盖", ...}
    """
    print(f"[extract_from_pdf] 分析 PDF 文件: {pdf_path}")

    # PDF 提示词模板（供 Agent 使用 images_understand 时使用）
    PROMPT = """请提取这份专利文档中所有"附图标记说明"的内容：
列出所有"数字-部件名称"的对应关系，格式例如：
100：离心管
40：管盖
10：上管体

如果没有"附图标记说明"章节，请告知。"""

    # 注：实际通过 Agent 的 images_understand 工具调用 PDF 内容
    # 此函数仅供 Agent 参考提示词格式
    return {}

def parse_pdf_text_response(response_text: str) -> dict:
    """
    解析 images_understand 返回的文本，提取附图标记
    """
    mapping = {}

    # 匹配多种格式：100：离心管、100-离心管、100. 离心管
    patterns = [
        r'\b(\d{2,3})\s*[:：.]\s*([^\n\d]{1,30})',
        r'\b(\d{2,3})\s*[-–—]\s*([^\n\d]{1,30})',
    ]

    for pat in patterns:
        for num, name in re.findall(pat, response_text):
            name = name.strip()
            num = num.strip()
            if name and len(name) > 0 and not name.startswith("http"):
                mapping[num] = name

    return mapping

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 extract_from_pdf.py <PDF文件路径>")
        sys.exit(1)
    result = extract_from_pdf(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
