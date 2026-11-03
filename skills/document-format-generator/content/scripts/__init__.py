"""
公文格式生成器脚本模块
"""

from .generator import (
    generate_gongwen,
    generate_gongwen_from_text,
    create_gongwen_document,
    parse_content_sections,
    GONGWEN_CONFIG
)

__version__ = '1.0.0'
__all__ = [
    'generate_gongwen',
    'generate_gongwen_from_text',
    'create_gongwen_document',
    'parse_content_sections',
    'GONGWEN_CONFIG'
]
