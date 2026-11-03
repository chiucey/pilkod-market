#!/usr/bin/env python3
"""读取 docx 文件并返回纯文本段落列表"""
import sys
import zipfile
from xml.etree import ElementTree as ET

def read_docx(path):
    with zipfile.ZipFile(path) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    paragraphs = []
    for para in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = []
        for t in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if t.text:
                texts.append(t.text)
        line = ''.join(texts).strip()
        if line:
            paragraphs.append(line)
    return paragraphs

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 read_docx.py <docx文件路径>")
        sys.exit(1)
    paragraphs = read_docx(sys.argv[1])
    for p in paragraphs:
        print(p)
