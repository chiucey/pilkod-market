#!/usr/bin/env python3
"""
b2b-sales-case-infographic: Case Information Extractor
Reads case document (docx/md/txt) and outputs structured content.
"""

import sys
import re
from pathlib import Path

def extract_from_md(text: str) -> dict:
    """从Markdown文本中提取案例结构化信息"""
    result = {
        "客户类型": [],
        "客户特点": [],
        "用户痛点": [],
        "产品价值": [],
        "可复制经验": [],
        "原始文本": text
    }

    current_section = None
    lines = text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            # 检测章节标题
            lower = stripped.lower()
            if "客户类型" in lower or "customer type" in lower:
                current_section = "客户类型"
            elif "客户特点" in lower or "customer characteristics" in lower:
                current_section = "客户特点"
            elif "用户痛点" in lower or "pain point" in lower or "pain_points" in lower:
                current_section = "用户痛点"
            elif "产品价值" in lower or "product value" in lower:
                current_section = "产品价值"
            elif "可复制" in lower or "经验" in lower or "replicable" in lower:
                current_section = "可复制经验"
            continue

        if current_section and stripped:
            result[current_section].append(stripped)

    return result

def extract_from_docx(path: str) -> str:
    """从docx文件读取文本"""
    try:
        from docx import Document
        doc = Document(path)
        return "\n".join([p.text for p in doc.paragraphs])
    except ImportError:
        print("python-docx not installed, falling back to text extraction")
        return open(path, "r", encoding="utf-8", errors="ignore").read()

def main():
    if len(sys.argv) < 2:
        print("Usage: extract_case_info.py <file.md|file.docx|file.txt>")
        sys.exit(1)

    path = Path(sys.argv[1])
    suffix = path.suffix.lower()

    if suffix == ".docx":
        text = extract_from_docx(str(path))
    elif suffix in [".md", ".txt"]:
        text = path.read_text(encoding="utf-8", errors="ignore")
    else:
        print(f"Unsupported file type: {suffix}")
        sys.exit(1)

    result = extract_from_md(text)

    print("=== 提取结果 ===")
    for key, items in result.items():
        if key != "原始文本":
            print(f"\n## {key}")
            if items:
                for item in items:
                    print(f"  - {item}")
            else:
                print("  [未找到相关内容，请手动填写]")

if __name__ == "__main__":
    main()
