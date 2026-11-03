"""
文件夹自动整理工具 - 工具函数模块
提供文件分析、内容提取、格式化等辅助功能
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 文件类型定义
FILE_TYPE_MAP = {
    # 文档类型
    'pdf': ('Documents', '📄 PDF'),
    'doc': ('Documents', '📄 Word'),
    'docx': ('Documents', '📄 Word'),
    'txt': ('Documents', '📄 Text'),
    'md': ('Documents', '📄 Markdown'),
    'rtf': ('Documents', '📄 RTF'),
    'odt': ('Documents', '📄 ODT'),

    # 表格类型
    'xls': ('Spreadsheets', '📊 Excel'),
    'xlsx': ('Spreadsheets', '📊 Excel'),
    'csv': ('Spreadsheets', '📊 CSV'),
    'ods': ('Spreadsheets', '📊 ODS'),

    # 演示类型
    'ppt': ('Presentations', '📽️ PowerPoint'),
    'pptx': ('Presentations', '📽️ PowerPoint'),
    'odp': ('Presentations', '📽️ ODP'),

    # 图片类型
    'jpg': ('Images', '🖼️ JPG'),
    'jpeg': ('Images', '🖼️ JPG'),
    'png': ('Images', '🖼️ PNG'),
    'gif': ('Images', '🖼️ GIF'),
    'bmp': ('Images', '🖼️ BMP'),
    'svg': ('Images', '🖼️ SVG'),
    'webp': ('Images', '🖼️ WebP'),
    'ico': ('Images', '🖼️ Icon'),

    # 音频类型
    'mp3': ('Audio', '🎵 MP3'),
    'wav': ('Audio', '🎵 WAV'),
    'aac': ('Audio', '🎵 AAC'),
    'flac': ('Audio', '🎵 FLAC'),
    'ogg': ('Audio', '🎵 OGG'),
    'm4a': ('Audio', '🎵 M4A'),

    # 视频类型
    'mp4': ('Videos', '🎬 MP4'),
    'avi': ('Videos', '🎬 AVI'),
    'mov': ('Videos', '🎬 MOV'),
    'mkv': ('Videos', '🎬 MKV'),
    'wmv': ('Videos', '🎬 WMV'),
    'flv': ('Videos', '🎬 FLV'),

    # 代码类型
    'py': ('Code', '💻 Python'),
    'js': ('Code', '💻 JavaScript'),
    'java': ('Code', '💻 Java'),
    'cpp': ('Code', '💻 C++'),
    'c': ('Code', '💻 C'),
    'h': ('Code', '💻 Header'),
    'html': ('Code', '💻 HTML'),
    'css': ('Code', '💻 CSS'),
    'json': ('Code', '💻 JSON'),
    'xml': ('Code', '💻 XML'),
    'yaml': ('Code', '💻 YAML'),
    'yml': ('Code', '💻 YAML'),
    'sh': ('Code', '💻 Shell'),
    'bat': ('Code', '💻 Batch'),
    'sql': ('Code', '💻 SQL'),
    'go': ('Code', '💻 Go'),
    'rs': ('Code', '💻 Rust'),
    'ts': ('Code', '💻 TypeScript'),
    'php': ('Code', '💻 PHP'),
    'rb': ('Code', '💻 Ruby'),

    # 压缩类型
    'zip': ('Archives', '📦 ZIP'),
    'rar': ('Archives', '📦 RAR'),
    '7z': ('Archives', '📦 7Z'),
    'tar': ('Archives', '📦 TAR'),
    'gz': ('Archives', '📦 GZ'),
    'bz2': ('Archives', '📦 BZ2'),

    # 字体类型
    'ttf': ('Fonts', '🔤 TTF'),
    'otf': ('Fonts', '🔤 OTF'),
    'woff': ('Fonts', '🔤 WOFF'),
    'woff2': ('Fonts', '🔤 WOFF2'),

    # 电子书类型
    'epub': ('Ebooks', '📚 EPUB'),
    'mobi': ('Ebooks', '📚 MOBI'),
    'azw': ('Ebooks', '📚 AZW'),
    'azw3': ('Ebooks', '📚 AZW3'),
}

# 主题关键词映射
TOPIC_KEYWORDS = {
    '合同': ['合同', '协议', 'contract', 'agreement'],
    '报告': ['报告', '总结', 'report', 'summary', '年报', '季报'],
    '方案': ['方案', '计划', 'proposal', 'plan'],
    '简历': ['简历', 'CV', 'resume', '个人履历'],
    '发票': ['发票', '收据', 'invoice', 'receipt', '账单'],
    '证书': ['证书', '认证', 'certificate', '资质'],
    '培训': ['培训', '教程', '教程', 'training', 'tutorial'],
    '会议': ['会议', '议程', 'meeting', 'minutes'],
    '项目': ['项目', 'project'],
    '数据': ['数据', 'data', '数据库', 'database'],
    '图纸': ['图纸', '设计', 'design', 'blueprint'],
    '照片': ['照片', '图片', 'photo', 'picture'],
    '视频': ['视频', '录像', 'video'],
    '备份': ['备份', 'backup', 'bak'],
}

# 敏感文件模式
SENSITIVE_PATTERNS = [
    r'password', r'passwd', r'secret', r'private',
    r'api[_-]?key', r'api[_-]?token', r'access[_-]?token',
    r'\.env', r'\.git[\\/]config', r'id_rsa', r'id_dsa',
    r'credentials', r'auth', r'oauth',
]


def get_file_type(file_path: str) -> Tuple[str, str]:
    """
    获取文件类型信息

    Returns:
        Tuple[str, str]: (分类文件夹名, 文件类型描述)
    """
    ext = Path(file_path).suffix.lower().lstrip('.')
    if ext in FILE_TYPE_MAP:
        return FILE_TYPE_MAP[ext]
    return ('Others', '📁 Other')


def extract_topic(file_path: str, content_hint: str = "") -> Optional[str]:
    """
    根据文件名和内容提示识别文件主题

    Args:
        file_path: 文件路径
        content_hint: 内容提示文本

    Returns:
        str: 识别的主题名称，无匹配返回 None
    """
    # 组合文件名和内容提示进行匹配
    search_text = (Path(file_path).stem + ' ' + content_hint).lower()

    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in search_text:
                return topic
    return None


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读格式
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def calculate_folder_size(folder_path: str) -> int:
    """
    计算文件夹总大小
    """
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    continue
    except Exception:
        pass
    return total_size


def is_sensitive_file(file_path: str) -> bool:
    """
    检查文件是否为敏感文件
    """
    filename = Path(file_path).name.lower()
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False


def extract_text_preview(file_path: str, max_length: int = 200) -> str:
    """
    提取文本文件的预览内容
    """
    ext = Path(file_path).suffix.lower().lstrip('.')

    try:
        if ext in ['txt', 'md', 'json', 'xml', 'yaml', 'yml', 'html', 'css', 'js']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_length * 3)
                # 清理空白字符
                content = re.sub(r'\s+', ' ', content).strip()
                return content[:max_length]
        elif ext in ['py', 'java', 'cpp', 'c', 'h', 'sh', 'sql', 'go', 'rs']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_length * 3)
                content = re.sub(r'\s+', ' ', content).strip()
                return content[:max_length]
    except Exception:
        pass

    return "[二进制文件，内容无法预览]"


def scan_directory_structure(root_path: str) -> Dict:
    """
    扫描目录结构，返回树形信息
    """
    structure = {
        'path': root_path,
        'name': Path(root_path).name,
        'type': 'directory',
        'children': [],
        'files': []
    }

    try:
        entries = sorted(os.listdir(root_path))
        for entry in entries:
            # 跳过隐藏文件
            if entry.startswith('.'):
                continue

            full_path = os.path.join(root_path, entry)
            if os.path.isdir(full_path):
                structure['children'].append(scan_directory_structure(full_path))
            else:
                try:
                    stat = os.stat(full_path)
                    structure['files'].append({
                        'name': entry,
                        'path': full_path,
                        'size': stat.st_size,
                        'size_formatted': format_file_size(stat.st_size),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                    })
                except (OSError, FileNotFoundError):
                    continue
    except PermissionError:
        pass

    return structure


def generate_summary_content(folder_path: str, structure: Dict, level: int = 0) -> str:
    """
    生成目录总结内容
    """
    folder_name = Path(folder_path).name
    files = structure.get('files', [])
    children = structure.get('children', [])

    # 计算文件夹大小
    total_size = sum(f['size'] for f in files)
    for child in children:
        total_size += calculate_folder_size(child['path'])

    # 构建总结
    lines = [
        f"# {folder_name} 目录总结",
        "",
        f"**整理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**文件总数**: {len(files)} 个",
        f"**子文件夹**: {len(children)} 个",
        f"**总大小**: {format_file_size(total_size)}",
        "",
        "## 内容概览",
        "",
        "[简要描述此文件夹的主要内容和用途]",
        "",
    ]

    # 文件清单
    if files:
        lines.extend([
            "## 文件清单",
            "",
            "| 文件名 | 类型 | 大小 | 修改时间 |",
            "|--------|------|------|----------|",
        ])

        for f in sorted(files, key=lambda x: x['name']):
            file_type = get_file_type(f['path'])
            lines.append(f"| {f['name']} | {file_type[1]} | {f['size_formatted']} | {f['modified']} |")

        lines.append("")

    # 子文件夹列表
    if children:
        lines.extend([
            "## 子文件夹",
            "",
        ])

        for child in sorted(children, key=lambda x: x['name']):
            child_files = len(child.get('files', []))
            lines.append(f"- 📁 `{child['name']}` - 包含 {child_files} 个文件")

        lines.append("")

    return '\n'.join(lines)


def generate_root_summary(target_path: str, structures: List[Dict]) -> str:
    """
    生成根目录总览报告
    """
    # 收集所有文件
    all_files = []

    def collect_files(struct):
        all_files.extend(struct.get('files', []))
        for child in struct.get('children', []):
            collect_files(child)

    for s in structures:
        collect_files(s)

    # 统计各类文件
    type_stats = {}
    for f in all_files:
        file_type = get_file_type(f['path'])[0]
        type_stats[file_type] = type_stats.get(file_type, 0) + 1

    total_size = sum(f['size'] for f in all_files)

    lines = [
        "# 文件夹整理总报告",
        "",
        f"**整理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**目标路径**: {target_path}",
        f"**文件总数**: {len(all_files)} 个",
        f"**总大小**: {format_file_size(total_size)}",
        "",
        "## 分类统计",
        "",
    ]

    for category, count in sorted(type_stats.items(), key=lambda x: -x[1]):
        lines.append(f"- {category}: {count} 个文件")

    lines.extend([
        "",
        "## 目录结构",
        "",
        "```",
        Path(target_path).name + "/",
    ])

    def print_tree(struct, prefix="", is_last=True):
        name = struct['name']
        connector = "└── " if is_last else "├── "

        if struct.get('files'):
            for i, f in enumerate(struct['files']):
                is_last_file = (i == len(struct['files']) - 1) and not struct['children']
                file_conn = "└── " if is_last_file else "├── "
                lines.append(f"{prefix}{file_conn}{f['name']}")

        children = struct.get('children', [])
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1) and not struct['files']
            new_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(f"{prefix}{connector}{child['name']}/")
            print_tree(child, new_prefix, is_child_last)

    for i, s in enumerate(structures):
        print_tree(s, "", i == len(structures) - 1)

    lines.append("```")

    return '\n'.join(lines)


def sanitize_filename(filename: str) -> str:
    """
    清理文件名中的非法字符
    """
    # Windows 非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    filename = re.sub(illegal_chars, '_', filename)
    # 去除首尾空格和点
    filename = filename.strip('. ')
    # 限制长度
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    return filename


def get_unique_path(target_path: str) -> str:
    """
    如果路径已存在，生成唯一的路径名
    """
    if not os.path.exists(target_path):
        return target_path

    base, ext = os.path.splitext(target_path)
    counter = 1
    while os.path.exists(target_path):
        target_path = f"{base}_{counter}{ext}"
        counter += 1
    return target_path
