"""
Local RAG Skill - 文档处理模块
支持将各种格式文档转换为Markdown
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
from datetime import datetime


@dataclass
class DocumentChunk:
    """文档块"""
    content: str
    chunk_id: str
    doc_id: str
    metadata: Dict
    index: int


@dataclass
class ProcessedDocument:
    """处理后的文档"""
    doc_id: str
    title: str
    content: str  # 完整Markdown内容
    chunks: List[DocumentChunk]
    metadata: Dict
    source_path: str


class DocumentProcessor:
    """文档处理器"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @staticmethod
    def generate_doc_id(file_path: str) -> str:
        """生成文档唯一ID"""
        timestamp = str(os.path.getmtime(file_path))
        content = f"{file_path}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    @staticmethod
    def generate_chunk_id(doc_id: str, index: int) -> str:
        """生成块ID"""
        return f"{doc_id}_{index:04d}"

    def process_file(self, file_path: str, metadata: Optional[Dict] = None) -> ProcessedDocument:
        """
        处理单个文件

        Args:
            file_path: 文件路径
            metadata: 额外元数据

        Returns:
            ProcessedDocument对象
        """
        path = Path(file_path)
        ext = path.suffix.lower()

        # 根据文件类型选择处理方法
        if ext == '.pdf':
            content = self._process_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            content = self._process_docx(file_path)
        elif ext == '.txt':
            content = self._process_txt(file_path)
        elif ext in ['.html', '.htm']:
            content = self._process_html(file_path)
        elif ext == '.md':
            content = self._process_markdown(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

        # 生成文档ID
        doc_id = self.generate_doc_id(file_path)

        # 分块处理
        chunks = self._chunk_text(content, doc_id)

        # 构建元数据
        doc_metadata = {
            'source': str(file_path),
            'title': path.stem,
            'extension': ext,
            'processed_at': datetime.now().isoformat(),
            'chunk_count': len(chunks),
            **(metadata or {})
        }

        return ProcessedDocument(
            doc_id=doc_id,
            title=path.stem,
            content=content,
            chunks=chunks,
            metadata=doc_metadata,
            source_path=str(file_path)
        )

    def _chunk_text(self, text: str, doc_id: str) -> List[DocumentChunk]:
        """
        将文本分块

        Args:
            text: 文本内容
            doc_id: 文档ID

        Returns:
            文档块列表
        """
        chunks = []
        start = 0
        index = 0

        # 预处理：规范化空白字符
        text = re.sub(r'\s+', ' ', text).strip()

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # 尝试在句子边界处分割
            if end < len(text):
                last_period = chunk_text.rfind('。')
                last_newline = chunk_text.rfind('\n')
                last_space = chunk_text.rfind(' ')

                split_point = max(last_period, last_newline, last_space)
                if split_point > start + self.chunk_size // 2:
                    chunk_text = chunk_text[:split_point + 1]
                    end = start + split_point + 1

            chunk = DocumentChunk(
                content=chunk_text.strip(),
                chunk_id=self.generate_chunk_id(doc_id, index),
                doc_id=doc_id,
                metadata={},
                index=index
            )
            chunks.append(chunk)

            # 移动到下一个块（包含重叠）
            start = end - self.chunk_overlap
            index += 1

        return chunks

    def _process_pdf(self, file_path: str) -> str:
        """处理PDF文件"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError("请安装 PyMuPDF: pip install pymupdf")

        doc = fitz.open(file_path)
        text_parts = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"## 第 {page_num + 1} 页\n\n{text}")

        doc.close()
        return '\n\n'.join(text_parts)

    def _process_docx(self, file_path: str) -> str:
        """处理Word文档"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

        doc = Document(file_path)
        parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                # 处理标题
                if para.style.name.startswith('Heading'):
                    level = para.style.name.replace('Heading ', '')
                    parts.append(f"{'#' * int(level)} {para.text}")
                else:
                    parts.append(para.text)

        # 处理表格
        for table in doc.tables:
            md_table = self._convert_table_to_markdown(table)
            if md_table:
                parts.append(md_table)

        return '\n\n'.join(parts)

    def _convert_table_to_markdown(self, table) -> str:
        """将表格转换为Markdown格式"""
        if not table.rows:
            return ""

        rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            rows.append('| ' + ' | '.join(cells) + ' |')

        # 添加分隔行
        if rows:
            col_count = len(table.columns)
            separator = '| ' + ' | '.join(['---'] * col_count) + ' |'
            rows.insert(1, separator)

        return '\n'.join(rows)

    def _process_txt(self, file_path: str) -> str:
        """处理纯文本文件"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        raise ValueError(f"无法解码文件: {file_path}")

    def _process_html(self, file_path: str) -> str:
        """处理HTML文件"""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            raise ImportError("请安装 beautifulsoup4: pip install beautifulsoup4")

        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 移除script和style标签
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()

        # 提取标题
        title = soup.find('title')
        parts = []
        if title:
            parts.append(f"# {title.text}\n")

        # 提取主要内容
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'table']):
                if element.name.startswith('h'):
                    level = element.name[1]
                    text = element.get_text().strip()
                    if text:
                        parts.append(f"{'#' * int(level)} {text}")
                elif element.name == 'p':
                    text = element.get_text().strip()
                    if text:
                        parts.append(text)
                elif element.name in ['ul', 'ol']:
                    for li in element.find_all('li', recursive=False):
                        text = li.get_text().strip()
                        if text:
                            prefix = '- ' if element.name == 'ul' else '1. '
                            parts.append(f"{prefix}{text}")
                elif element.name == 'table':
                    md_table = self._html_table_to_markdown(element)
                    if md_table:
                        parts.append(md_table)

        return '\n\n'.join(parts)

    def _html_table_to_markdown(self, table) -> str:
        """将HTML表格转换为Markdown"""
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for cell in tr.find_all(['th', 'td']):
                cells.append(cell.get_text().strip())
            if cells:
                rows.append('| ' + ' | '.join(cells) + ' |')

        if not rows:
            return ""

        # 添加分隔行
        col_count = len(rows[0].split('|')) - 2
        separator = '| ' + ' | '.join(['---'] * col_count) + ' |'
        rows.insert(1, separator)

        return '\n'.join(rows)

    def _process_markdown(self, file_path: str) -> str:
        """处理Markdown文件"""
        return self._process_txt(file_path)
