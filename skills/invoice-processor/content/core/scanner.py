#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件扫描器模块
扫描指定文件夹，按文件类型分类发票文件
"""
import os
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class FileInfo:
    """文件信息"""
    path: Path
    name: str
    suffix: str
    size: int
    category: str


class FileScanner:
    """发票文件扫描器"""

    # 支持的文件类型及分类
    SUPPORTED_TYPES = {
        '.pdf': 'pdf',
        '.ofd': 'ofd',
        '.xml': 'xml',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.bmp': 'image',
        '.gif': 'image'
    }

    # 分类显示名称
    CATEGORY_NAMES = {
        'pdf': 'PDF文件',
        'ofd': 'OFD文件',
        'xml': 'XML文件',
        'image': '图片文件'
    }

    def __init__(self, folder_path: str):
        """
        初始化扫描器

        Args:
            folder_path: 要扫描的文件夹路径
        """
        self.folder_path = Path(folder_path)
        self.files_by_type: Dict[str, List[Path]] = {}
        self.all_files: List[FileInfo] = []

    def scan(self) -> Dict[str, List[Path]]:
        """
        扫描文件夹，返回按类型分类的文件列表

        Returns:
            Dict[str, List[Path]]: 按类型分类的文件路径字典
        """
        # 初始化分类字典
        self.files_by_type = {category: [] for category in set(self.SUPPORTED_TYPES.values())}
        self.all_files = []

        if not self.folder_path.exists():
            raise FileNotFoundError(f"文件夹不存在: {self.folder_path}")

        if not self.folder_path.is_dir():
            raise NotADirectoryError(f"路径不是文件夹: {self.folder_path}")

        # 遍历文件夹
        for file_path in self.folder_path.iterdir():
            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()
            if suffix not in self.SUPPORTED_TYPES:
                continue

            category = self.SUPPORTED_TYPES[suffix]
            self.files_by_type[category].append(file_path)

            # 记录文件信息
            file_info = FileInfo(
                path=file_path,
                name=file_path.name,
                suffix=suffix,
                size=file_path.stat().st_size,
                category=category
            )
            self.all_files.append(file_info)

        return self.files_by_type

    def get_summary(self) -> Dict[str, int]:
        """
        获取扫描结果摘要

        Returns:
            Dict[str, int]: 各类文件的数量统计
        """
        summary = {}
        for category, files in self.files_by_type.items():
            summary[self.CATEGORY_NAMES.get(category, category)] = len(files)
        summary['总计'] = len(self.all_files)
        return summary

    def get_all_files_list(self) -> List[Path]:
        """获取所有文件的路径列表"""
        all_files = []
        for files in self.files_by_type.values():
            all_files.extend(files)
        return all_files
