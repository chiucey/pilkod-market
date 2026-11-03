#!/usr/bin/env python3
"""
PDF文档校对脚本
支持100页以上大型报告的分片处理
"""

import re
import difflib
import hashlib
import json
from datetime import datetime
from typing import Tuple, List, Dict, Optional

# 默认分块大小（字符数）
DEFAULT_CHUNK_SIZE = 5000
# 重叠大小（用于保持上下文）
OVERLAP_SIZE = 200


def normalize_text(text: str) -> str:
    """
    规范化文本，移除格式差异
    """
    if not text:
        return ""

    # 替换多种空格为普通空格
    text = re.sub(r'[\u00A0\u2000-\u200A\u202F\u205F\u3000]', ' ', text)

    # 规范化换行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # 移除多余空格
    text = re.sub(r'[ \t]+', ' ', text)

    # 规范化标点符号
    # 中文引号
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    # 破折号
    text = text.replace('——', '—')

    # 移除常见的OCR错误
    text = text.replace('О', 'O')  # 西里尔字母O

    return text.strip()


def is_numeric_difference(text1: str, text2: str) -> bool:
    """
    检测是否是数字相关的差异
    """
    # 提取数字
    nums1 = re.findall(r'-?\d+\.?\d*', text1)
    nums2 = re.findall(r'-?\d+\.?\d*', text2)

    if nums1 != nums2:
        return True

    # 检查是否有数字但完全不同的值
    if re.search(r'\d', text1) and re.search(r'\d', text2):
        # 提取纯数字进行比较
        val1 = re.sub(r'[^\d.-]', '', text1)
        val2 = re.sub(r'[^\d.-]', '', text2)
        if val1 and val2 and val1 != val2:
            return True

    return False


def detect_digit_error(original: str, parsed: str) -> bool:
    """
    检测小数点位置错误等数字错误
    """
    # 提取所有数字
    orig_nums = re.findall(r'-?\d+\.?\d*', original)
    pars_nums = re.findall(r'-?\d+\.?\d*', parsed)

    if len(orig_nums) != len(pars_nums):
        return False

    for o, p in zip(orig_nums, pars_nums):
        try:
            if float(o) != float(p):
                return True
        except ValueError:
            if o != p:
                return True

    return False


class DocumentChunk:
    """文档分块"""
    def __init__(self, content: str, start_pos: int, chunk_index: int, page_hint: str = ""):
        self.content = content
        self.start_pos = start_pos
        self.chunk_index = chunk_index
        self.page_hint = page_hint
        self.content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]


class DocumentComparator:
    """文档比对器"""

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE):
        self.chunk_size = chunk_size
        self.differences = []
        self.identical_sections = []

    def chunk_text(self, text: str) -> List[DocumentChunk]:
        """
        将文本分块，支持大文档处理
        """
        chunks = []
        text = text.strip()

        if not text:
            return chunks

        # 首先尝试按段落分割
        paragraphs = re.split(r'\n\s*\n', text)

        current_chunk = ""
        current_pos = 0
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 如果单个段落就超过分块大小，需要进一步分割
            if len(para) > self.chunk_size:
                # 先保存当前chunk
                if current_chunk:
                    chunks.append(DocumentChunk(
                        current_chunk,
                        current_pos,
                        chunk_index
                    ))
                    chunk_index += 1
                    current_pos += len(current_chunk)
                    current_chunk = ""

                # 分割大段落
                sub_chunks = self._split_large_paragraph(para, current_pos, chunk_index)
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
                current_pos += len(para)
                current_chunk = ""
            elif len(current_chunk) + len(para) + 1 > self.chunk_size:
                # 当前chunk已满，保存并开始新chunk
                chunks.append(DocumentChunk(
                    current_chunk,
                    current_pos,
                    chunk_index
                ))
                chunk_index += 1
                current_pos += len(current_chunk)
                current_chunk = para
            else:
                # 添加到当前chunk
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # 保存最后一个chunk
        if current_chunk:
            chunks.append(DocumentChunk(
                current_chunk,
                current_pos,
                chunk_index
            ))

        return chunks

    def _split_large_paragraph(self, text: str, start_pos: int, start_index: int) -> List[DocumentChunk]:
        """分割过大的段落"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - OVERLAP_SIZE):
            chunk_text = text[i:i + self.chunk_size]
            if i > 0:
                # 添加前一个块的部分内容作为上下文
                chunk_text = text[max(0, i - OVERLAP_SIZE):i + self.chunk_size]
            chunks.append(DocumentChunk(
                chunk_text,
                start_pos + i,
                start_index + len(chunks)
            ))
        return chunks

    def compare_texts(self, original: str, parsed: str) -> Tuple[List[Dict], List[str]]:
        """
        比对两份文本内容
        返回：(差异列表, 无差异段落列表)
        """
        # 规范化
        orig_norm = normalize_text(original)
        parsed_norm = normalize_text(parsed)

        # 如果完全相同
        if orig_norm == parsed_norm:
            return [], [original]

        # 分块处理
        orig_chunks = self.chunk_text(orig_norm)
        parsed_chunks = self.chunk_text(parsed_norm)

        print(f"原文分块数: {len(orig_chunks)}")
        print(f"解析文分块数: {len(parsed_chunks)}")

        # 使用滑动窗口进行比对
        self._compare_chunks(orig_chunks, parsed_chunks)

        return self.differences, self.identical_sections

    def _compare_chunks(self, orig_chunks: List[DocumentChunk],
                        parsed_chunks: List[DocumentChunk]):
        """比对分块"""

        for o_chunk in orig_chunks:
            best_match = None
            best_ratio = 0

            # 在解析文分块中寻找最佳匹配
            for p_idx, p_chunk in enumerate(parsed_chunks):
                ratio = difflib.SequenceMatcher(
                    None, o_chunk.content, p_chunk.content
                ).ratio()

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = (p_idx, p_chunk)

            if best_match:
                p_idx, p_chunk = best_match

                if best_ratio >= 0.95:
                    # 几乎完全匹配，视为无差异
                    self.identical_sections.append(o_chunk.content[:500])
                elif best_ratio >= 0.7:
                    # 部分匹配，进行详细比对
                    self._detailed_compare(o_chunk, p_chunk)
                else:
                    # 匹配度低，可能是遗漏或多余
                    self.differences.append({
                        'type': '可能的遗漏或多余',
                        'position': f'原文块 {o_chunk.chunk_index}',
                        'original': o_chunk.content[:500],
                        'parsed': p_chunk.content[:500] if p_chunk else '（无匹配）',
                        'confidence': best_ratio
                    })

    def _detailed_compare(self, orig_chunk: DocumentChunk,
                          parsed_chunk: DocumentChunk):
        """详细比对两个块"""

        orig_lines = orig_chunk.content.split('\n')
        parsed_lines = parsed_chunk.content.split('\n')

        matcher = difflib.SequenceMatcher(None, orig_lines, parsed_lines)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # 相同内容
                self.identical_sections.extend(orig_lines[i1:i2])
            elif tag == 'replace':
                # 替换
                for i in range(i1, i2):
                    orig_line = orig_lines[i]
                    if i - i1 < j2 - j1 and i - i1 < len(parsed_lines):
                        parsed_line = parsed_lines[i - i1]
                        self._analyze_line_diff(orig_line, parsed_line,
                                                orig_chunk.chunk_index, i)
                    else:
                        # 原文多出的行
                        self.differences.append({
                            'type': '遗漏内容',
                            'position': f'原文块 {orig_chunk.chunk_index}, 第{i+1}行',
                            'original': orig_line,
                            'parsed': '（缺失）',
                            'description': '原文中存在的内容在解析结果中未找到'
                        })

            elif tag == 'delete':
                # 删除（原文有，解析无）
                for i in range(i1, i2):
                    self.differences.append({
                        'type': '遗漏内容',
                        'position': f'原文块 {orig_chunk.chunk_index}, 第{i+1}行',
                        'original': orig_lines[i],
                        'parsed': '（缺失）',
                        'description': '原文中存在的内容在解析结果中未找到'
                    })

            elif tag == 'insert':
                # 插入（解析有，原文无）
                for j in range(j1, j2):
                    self.differences.append({
                        'type': '多余内容',
                        'position': f'解析块 {parsed_chunk.chunk_index}, 第{j+1}行',
                        'original': '（缺失）',
                        'parsed': parsed_lines[j],
                        'description': '解析结果中多出的内容，原文中未找到'
                    })

    def _analyze_line_diff(self, orig_line: str, parsed_line: str,
                           chunk_idx: int, line_num: int):
        """分析单行差异"""

        if not orig_line.strip() or not parsed_line.strip():
            return

        # 检测数字错误
        if is_numeric_difference(orig_line, parsed_line):
            self.differences.append({
                'type': '数字错误',
                'position': f'块 {chunk_idx}, 第{line_num+1}行',
                'original': orig_line,
                'parsed': parsed_line,
                'description': self._get_numeric_description(orig_line, parsed_line)
            })
            return

        # 检测文字错误（逐字符比对）
        if orig_line != parsed_line:
            self.differences.append({
                'type': '文字错误',
                'position': f'块 {chunk_idx}, 第{line_num+1}行',
                'original': orig_line,
                'parsed': parsed_line,
                'description': self._get_text_diff_description(orig_line, parsed_line)
            })

    def _get_numeric_description(self, orig: str, parsed: str) -> str:
        """获取数字差异描述"""
        orig_nums = re.findall(r'-?\d+\.?\d*', orig)
        pars_nums = re.findall(r'-?\d+\.?\d*', parsed)

        desc_parts = []
        for o, p in zip(orig_nums, pars_nums):
            if o != p:
                try:
                    diff = abs(float(o) - float(p))
                    desc_parts.append(f"数值 {o} → {p}，差异 {diff}")
                except:
                    desc_parts.append(f"数值 {o} → {p}")

        return "; ".join(desc_parts) if desc_parts else "检测到数字差异"

    def _get_text_diff_description(self, orig: str, parsed: str) -> str:
        """获取文字差异描述"""
        # 找出具体不同的字符
        orig_chars = list(orig)
        pars_chars = list(parsed)

        matcher = difflib.SequenceMatcher(None, orig_chars, pars_chars)

        changes = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                removed = ''.join(orig_chars[i1:i2])
                added = ''.join(pars_chars[j1:j2])
                changes.append(f"'{removed}' → '{added}'")

        if len(changes) <= 3:
            return "字符差异: " + ", ".join(changes)
        else:
            return f"存在 {len(changes)} 处字符差异"


def generate_markdown_report(
    differences: List[Dict],
    identical_sections: List[str],
    original_file: str = "",
    parsed_file: str = ""
) -> str:
    """生成Markdown格式的校对报告"""

    report = f"""# 文档校对报告

## 文档信息
- 源文件：{original_file if original_file else '未指定'}
- 解析文件：{parsed_file if parsed_file else '未指定'}
- 比对时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 差异详情
"""

    if not differences:
        report += "\n**无差异**\n\n所有比对内容完全一致。"
    else:
        # 分类统计
        type_counts = {}
        for diff in differences:
            diff_type = diff.get('type', '未知')
            type_counts[diff_type] = type_counts.get(diff_type, 0) + 1

        report += "\n### 差异类型统计\n"
        for diff_type, count in type_counts.items():
            report += f"- {diff_type}：{count}处\n"

        report += "\n---\n\n### 详细差异\n"

        for idx, diff in enumerate(differences, 1):
            report += f"""### 第{idx}处差异

**位置**：{diff.get('position', '未知位置')}
**类型**：{diff.get('type', '未知类型')}

| | 内容 |
|---|---|
| **原文** | {diff.get('original', '')} |
| **解析后** | {diff.get('parsed', '')} |

**描述**：{diff.get('description', '无详细描述')}

---
"""

    report += """

## 无差异区域

以下是已确认一致的内容片段：

"""

    if identical_sections:
        for idx, section in enumerate(identical_sections[:20], 1):
            # 截取前200字符
            preview = section[:200] + "..." if len(section) > 200 else section
            report += f"{idx}. {preview}\n\n"

        if len(identical_sections) > 20:
            report += f"\n*（共 {len(identical_sections)} 个无差异段落，此处展示前20个）*\n"
    else:
        report += "无完全一致的段落\n"

    report += f"""

---

**校对完成**

- 差异总数：{len(differences)}处
- 无差异段落：{len(identical_sections)}段
"""

    return report


def compare_files(original_path: str, parsed_path: str,
                  output_path: str = "comparison_report.md",
                  chunk_size: int = DEFAULT_CHUNK_SIZE) -> str:
    """
    比较两个文件并生成报告

    Args:
        original_path: 源文件路径
        parsed_path: 解析后文件路径
        output_path: 输出报告路径
        chunk_size: 分块大小

    Returns:
        报告内容
    """
    print(f"正在读取文件...")
    print(f"  源文件: {original_path}")
    print(f"  解析文件: {parsed_path}")

    # 读取文件
    with open(original_path, 'r', encoding='utf-8', errors='ignore') as f:
        original_text = f.read()

    with open(parsed_path, 'r', encoding='utf-8', errors='ignore') as f:
        parsed_text = f.read()

    print(f"源文件长度: {len(original_text)} 字符")
    print(f"解析文件长度: {len(parsed_text)} 字符")

    # 执行比对
    comparator = DocumentComparator(chunk_size=chunk_size)
    differences, identical_sections = comparator.compare_texts(original_text, parsed_text)

    # 生成报告
    report = generate_markdown_report(
        differences,
        identical_sections,
        original_path,
        parsed_path
    )

    # 保存报告
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存到: {output_path}")
    print(f"发现差异: {len(differences)}处")
    print(f"无差异段落: {len(identical_sections)}段")

    return report


# 主函数（用于命令行执行）
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='PDF文档校对工具')
    parser.add_argument('original', help='源文件路径')
    parser.add_argument('parsed', help='解析后文件路径')
    parser.add_argument('-o', '--output', default='comparison_report.md',
                        help='输出报告路径')
    parser.add_argument('-c', '--chunk-size', type=int, default=DEFAULT_CHUNK_SIZE,
                        help=f'分块大小（默认{DEFAULT_CHUNK_SIZE}字符）')

    args = parser.parse_args()

    report = compare_files(
        args.original,
        args.parsed,
        args.output,
        args.chunk_size
    )

    print("\n" + "="*50)
    print("报告预览：")
    print("="*50)
    print(report[:2000])
