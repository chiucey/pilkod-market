#!/usr/bin/env python3
"""
read_doc.py — 通用文档读取脚本
支持: .docx .xlsx .pdf
依赖: 纯标准库 (zipfile, xml.etree.ElementTree, json, re)
"""
import sys
import zipfile
import xml.etree.ElementTree as ET
import re
import os
import csv
import io
import json

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'xlsx': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
}

def read_docx(path):
    """读取 DOCX 文件，返回纯文本"""
    texts = []
    with zipfile.ZipFile(path, 'r') as z:
        # 读取主体内容
        xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            line = ''
            for run in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if run.text:
                    line += run.text
            if line.strip():
                texts.append(line)
    return '\n'.join(texts)

def read_xlsx(path):
    """读取 XLSX 文件，返回所有 sheet 的表格文本"""
    sheets = {}
    with zipfile.ZipFile(path, 'r') as z:
        # 读取共享字符串
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_root = ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in ss_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                text = ''.join(t.text or '' for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'))
                shared_strings.append(text)
        
        # 读取工作表列表
        wb_root = ET.fromstring(z.read('xl/workbook.xml'))
        sheet_entries = []
        for sh in wb_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet'):
            sheet_entries.append((sh.get('name', ''), sh.get('{http://schemas.openxmlformats.org/relationships}id', '')))
        
        # 建立 rId -> sheetFile 映射
        rels_root = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        rid_to_file = {r.get('Id'): r.get('Target') for r in rels_root}
        
        for name, rid in sheet_entries:
            target = rid_to_file.get(rid, '')
            if not target.startswith('worksheets/'):
                target = 'xl/' + target
            else:
                target = 'xl/' + target
            
            sheet_texts = []
            try:
                ws_root = ET.fromstring(z.read(target))
                for row in ws_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                    row_cells = []
                    for cell in row.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
                        t = cell.get('t', '')
                        v_el = cell.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        val = ''
                        if v_el is not None and v_el.text:
                            if t == 's':
                                val = shared_strings[int(v_el.text)]
                            else:
                                val = v_el.text
                        row_cells.append(val)
                    if any(c.strip() for c in row_cells):
                        sheets.setdefault(name, []).append('\t'.join(row_cells))
            except Exception as e:
                sheets.setdefault(name, []).append(f'[读取错误: {e}]')
    
    # 输出
    output = []
    for sheet_name, rows in sheets.items():
        output.append(f'=== Sheet: {sheet_name} ===')
        output.extend(rows)
        output.append('')
    return '\n'.join(output)

def read_pdf_basic(path):
    """读取 PDF 文件（基础文本抽取，依赖 pdfminer.six）"""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(path)
        return text.strip() if text.strip() else '[PDF 内容为空或为扫描件（无文字图层）]'
    except ImportError:
        return '[错误: 未安装 pdfminer.six，无法读取 PDF]\n可执行: pip install pdfminer.six'
    except Exception as e:
        return f'[PDF 读取错误: {e}]'

def detect_and_read(path):
    ext = os.path.splitext(path)[1].lower()
    fname = os.path.basename(path)
    
    if ext == '.docx':
        content = read_docx(path)
        return '【DOCX 文件: {}】\n{}'.format(fname, content)
    elif ext == '.xlsx':
        content = read_xlsx(path)
        return '【XLSX 文件: {}】\n{}'.format(fname, content)
    elif ext == '.pdf':
        content = read_pdf_basic(path)
        return '【PDF 文件: {}】\n{}'.format(fname, content)
    else:
        return '[错误: 不支持的格式 "{}", 仅支持 .docx .xlsx .pdf]'.format(ext)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 read_doc.py <file_path>')
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f'[错误: 文件不存在: {file_path}]')
        sys.exit(1)
    
    result = detect_and_read(file_path)
    print(result)
