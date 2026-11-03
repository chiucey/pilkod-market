#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Pro 核心处理模块
支持 PDF、DOCX、PPT、TXT、Markdown 等多格式文档处理
纯本地实现，无 OpenClaw 依赖
"""

import json
import re
import sys
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


def clean_text(text: str) -> str:
    """清理文本空白与多余换行"""
    text = re.sub(r'\s+', ' ', text.strip())
    return text


def split_paragraphs(text: str, min_length: int = 100) -> List[str]:
    """智能分段"""
    if not text:
        return []
    raw = re.split(r'[\n\r]+', text.strip())
    paragraphs = []
    current = ''
    for line in raw:
        line = line.strip()
        if not line:
            continue
        if len(current) + len(line) < min_length:
            current += ' ' + line
        else:
            if current:
                paragraphs.append(current.strip())
            current = line
    if current:
        paragraphs.append(current.strip())
    return paragraphs


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """关键词提取（支持中英文）"""
    stop_words = {
        '的', '了', '和', '是', '在', '我', '有', '就', '都', '而', '及', '与',
        '不', '人', '也', '很', '到', '说', '去', '要', '会', '着', '没有',
        '看', '好', '自己', '这', '那', '个', '们', '为', '被', '与', '由',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
        'and', 'or', 'but', 'if', 'because', 'as', 'until', 'while', 'of',
        'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
        'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
        'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'just', 'this', 'that', 'these', 'those', 'it', 'its'
    }

    # 中英文分词
    chinese_words = re.findall(r'[\u4e00-\u9fa5]+', text)
    english_words = re.findall(r'[a-zA-Z]+', text)

    freq = {}

    # 统计中文词频
    for word in chinese_words:
        if len(word) < 2 or word in stop_words:
            continue
        freq[word] = freq.get(word, 0) + 1

    # 统计英文词频（转小写）
    for word in english_words:
        word_lower = word.lower()
        if len(word) < 3 or word_lower in stop_words:
            continue
        freq[word_lower] = freq.get(word_lower, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, c in sorted_words[:top_n]]


def extract_title(text: str) -> str:
    """提取文档标题（通常为第一行或第一个大标题）"""
    lines = text.strip().split('\n')
    for line in lines[:5]:  # 检查前5行
        line = line.strip()
        # 跳过空行和太短的行
        if len(line) < 5 or len(line) > 200:
            continue
        # 跳过可能是页眉的短行
        if re.match(r'^[\d\-\.]+\s*$', line):
            continue
        return line
    # 返回第一个非空行，或者默认标题
    for line in lines:
        if line.strip():
            return line.strip()
    return "未识别标题"


def generate_summary(paragraphs: List[str], max_length: int = 1000) -> str:
    """生成文档摘要"""
    if not paragraphs:
        return ""

    summary_parts = []
    current_length = 0

    for para in paragraphs:
        if current_length + len(para) <= max_length:
            summary_parts.append(para)
            current_length += len(para)
        else:
            remaining = max_length - current_length
            if remaining > 50:
                summary_parts.append(para[:remaining] + '...')
            break

    return ' '.join(summary_parts) if summary_parts else paragraphs[0][:max_length]


def detect_document_type(file_path: str) -> str:
    """检测文档类型"""
    ext = Path(file_path).suffix.lower()
    type_map = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.pptx': 'pptx',
        '.ppt': 'ppt',
        '.txt': 'txt',
        '.md': 'markdown',
        '.markdown': 'markdown'
    }
    return type_map.get(ext, 'unknown')


def parse_pdf(file_path: str) -> Dict[str, Any]:
    """解析 PDF 文档"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text_parts = []
            metadata = {}

            # 提取元数据
            if reader.metadata:
                metadata = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', '')
                }

            # 提取每页文本
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"[第{i+1}页]\n{page_text}")

            full_text = '\n\n'.join(text_parts)
            return {
                'success': True,
                'text': full_text,
                'metadata': metadata,
                'page_count': len(reader.pages)
            }
    except ImportError:
        return {'success': False, 'error': '请安装 PyPDF2: pip install PyPDF2'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_docx(file_path: str) -> Dict[str, Any]:
    """解析 DOCX 文档"""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = []
        tables = []

        # 提取段落
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)

        # 提取表格
        for i, table in enumerate(doc.tables):
            table_data = []
            for row in table.rows:
                row_data = [cell.text for cell in row.cells]
                table_data.append(row_data)
            tables.append({'index': i, 'data': table_data})

        full_text = '\n'.join(paragraphs)

        # 尝试提取标题（第一个大号字体段落）
        title = paragraphs[0] if paragraphs and len(paragraphs[0]) < 200 else "未识别标题"

        return {
            'success': True,
            'text': full_text,
            'title': title,
            'paragraph_count': len(paragraphs),
            'table_count': len(tables),
            'tables': tables
        }
    except ImportError:
        return {'success': False, 'error': '请安装 python-docx: pip install python-docx'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_pptx(file_path: str) -> Dict[str, Any]:
    """解析 PPTX 文档"""
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt

        prs = Presentation(file_path)
        slides = []

        for i, slide in enumerate(prs.slides):
            slide_texts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_texts.append(shape.text.strip())

            if slide_texts:
                slides.append({
                    'index': i + 1,
                    'content': '\n'.join(slide_texts)
                })

        full_text = '\n\n'.join([s['content'] for s in slides])

        return {
            'success': True,
            'text': full_text,
            'slide_count': len(slides),
            'slides': slides
        }
    except ImportError:
        return {'success': False, 'error': '请安装 python-pptx: pip install python-pptx'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_txt(file_path: str) -> Dict[str, Any]:
    """解析纯文本文件"""
    try:
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        content = None

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                break
            except (UnicodeDecodeError, LookupError):
                continue

        if content is None:
            # 最后尝试二进制读取后忽略错误
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        return {
            'success': True,
            'text': content,
            'encoding': encoding if content else 'unknown'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_markdown(file_path: str) -> Dict[str, Any]:
    """解析 Markdown 文件"""
    result = parse_txt(file_path)
    if result['success']:
        result['format'] = 'markdown'
        # 提取标题
        lines = result['text'].split('\n')
        for line in lines:
            if line.startswith('# '):
                result['title'] = line[2:].strip()
                break
    return result


def process_document(file_path: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    处理文档的主函数
    支持文件路径或直接文本输入
    """
    options = options or {}
    mode = options.get('mode', 'full')
    language = options.get('language', 'zh-CN')
    max_summary_length = options.get('max_summary_length', 1000)
    keyword_count = options.get('keyword_count', 10)
    min_paragraph_length = options.get('min_paragraph_length', 100)

    # 如果提供了直接内容
    if 'content' in options:
        content = options['content']
        doc_type = 'text'
        parse_result = {'success': True, 'text': content}
    else:
        # 检测文档类型并解析
        if not file_path or not os.path.exists(file_path):
            return {
                "status": "error",
                "data": None,
                "message_for_user": f"文件不存在或路径无效: {file_path}"
            }

        doc_type = detect_document_type(file_path)

        if doc_type == 'unknown':
            return {
                "status": "error",
                "data": None,
                "message_for_user": f"不支持的文档格式: {Path(file_path).suffix}"
            }

        # 根据类型解析
        parsers = {
            'pdf': parse_pdf,
            'docx': parse_docx,
            'pptx': parse_pptx,
            'txt': parse_txt,
            'markdown': parse_markdown
        }

        parser = parsers.get(doc_type)
        if not parser:
            return {
                "status": "error",
                "data": None,
                "message_for_user": f"暂不支持此格式: {doc_type}"
            }

        parse_result = parser(file_path)

    if not parse_result.get('success'):
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"文档解析失败: {parse_result.get('error', '未知错误')}"
        }

    # 处理文本内容
    raw_text = parse_result.get('text', '')
    if not raw_text:
        return {
            "status": "error",
            "data": None,
            "message_for_user": "文档内容为空或无法提取文本"
        }

    # 清洗文本
    cleaned_text = clean_text(raw_text)

    # 分段
    paragraphs = split_paragraphs(cleaned_text, min_length=min_paragraph_length)

    # 提取标题
    title = parse_result.get('title') or extract_title(raw_text)

    # 提取关键词
    keywords = extract_keywords(cleaned_text, top_n=keyword_count)

    # 生成摘要
    summary = generate_summary(paragraphs, max_length=max_summary_length)

    # 构建结果
    base_result = {
        "document_type": doc_type,
        "original_length": len(raw_text),
        "cleaned_length": len(cleaned_text),
        "title": title,
        "keywords": keywords,
        "paragraph_count": len(paragraphs),
        "summary": summary,
        "paragraphs": paragraphs
    }

    # 添加格式特有信息
    if 'metadata' in parse_result:
        base_result['metadata'] = parse_result['metadata']
    if 'page_count' in parse_result:
        base_result['page_count'] = parse_result['page_count']
    if 'slide_count' in parse_result:
        base_result['slide_count'] = parse_result['slide_count']
    if 'table_count' in parse_result:
        base_result['table_count'] = parse_result['table_count']
        base_result['tables'] = parse_result.get('tables', [])
    if 'slides' in parse_result:
        base_result['slides'] = parse_result['slides']

    # 根据模式过滤输出
    if mode == 'summary':
        output = {
            "summary": summary,
            "keywords": keywords,
            "title": title
        }
    elif mode == 'extract':
        output = {
            "keywords": keywords,
            "paragraphs": paragraphs,
            "tables": base_result.get('tables', [])
        }
    elif mode == 'structure':
        output = {"structure": base_result}
    else:
        output = base_result

    return {
        "status": "success",
        "data": output,
        "message_for_user": f"文档处理完成，已成功解析 {doc_type.upper()} 格式文档，生成结构化结果。"
    }


def run(input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Skill 主入口
    input_data 支持字段：
    - content: 文本内容（可选）
    - file_path: 文件路径（可选）
    - mode: summary / extract / structure / full
    - language: zh-CN / en
    """
    input_data = input_data or {}
    file_path = input_data.get('file_path')
    options = {
        'mode': input_data.get('mode', 'full'),
        'language': input_data.get('language', 'zh-CN'),
        'max_summary_length': input_data.get('max_summary_length', 1000),
        'keyword_count': input_data.get('keyword_count', 10),
        'min_paragraph_length': input_data.get('min_paragraph_length', 100)
    }

    # 如果没有内容也没有文件路径
    if not input_data.get('content') and not file_path:
        return {
            "status": "error",
            "data": None,
            "message_for_user": "请提供文档内容（content）或文件路径（file_path）。"
        }

    # 如果有内容但没有文件
    if input_data.get('content') and not file_path:
        options['content'] = input_data['content']
        return process_document(None, options)

    # 处理文件
    return process_document(file_path, options)


if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            input_json = sys.stdin.read().strip()
            input_data = json.loads(input_json) if input_json else {}
        else:
            input_data = {}
    except json.JSONDecodeError:
        input_data = {}

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
