#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""使用LibreOffice转换并读取工作总结文档"""

import subprocess
import os
from docx import Document

def convert_and_read(input_file):
    """转换.doc为.docx并读取内容

    Args:
        input_file: 输入的.doc文件路径

    Returns:
        str: 转换后的.docx文件路径
    """
    os.makedirs("tmp", exist_ok=True)
    output_file = f"tmp/{os.path.basename(input_file).replace('.doc', '.docx')}"

    # 转换.doc为.docx
    cmd = ["soffice", "--headless", "--convert-to", "docx", "--outdir", "tmp", input_file]
    subprocess.run(cmd, check=True, capture_output=True, timeout=30)

    return output_file

def read_docx_content(docx_file):
    """读取.docx文件内容

    Args:
        docx_file: .docx文件路径

    Returns:
        list: 所有非空段落文本列表
    """
    doc = Document(docx_file)
    contents = []
    for para in doc.paragraphs:
        if para.text.strip():
            contents.append(para.text)
    return contents

def read_all_docs(input_files):
    """批量转换和读取多个文档

    Args:
        input_files: .doc文件路径列表

    Returns:
        dict: {文件名: [段落列表]}
    """
    results = {}
    for f in input_files:
        try:
            converted = convert_and_read(f)
            results[f] = read_docx_content(converted)
            print(f"[成功] {f}")
        except Exception as e:
            print(f"[失败] {f}: {e}")
    return results

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        for f in files:
            converted = convert_and_read(f)
            contents = read_docx_content(converted)
            print(f"\n{'='*60}")
            print(f"文件: {f}")
            print('='*60)
            for line in contents:
                print(line)