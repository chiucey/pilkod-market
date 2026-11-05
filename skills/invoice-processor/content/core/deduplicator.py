#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
发票去重模块
基于发票号码进行智能去重，相同发票保留PDF格式
"""
import re
from typing import Dict, List, Set, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InvoiceDeduplicator:
    """发票去重器"""

    # 发票号码正则模式
    INVOICE_NUMBER_PATTERNS = [
        r'发票号码[：:]\s*([A-Z0-9]{8,20})',
        r'发票号[：:]\s*([A-Z0-9]{8,20})',
        r'NO[\.:：]\s*([A-Z0-9]{8,20})',
        r'编号[：:]\s*([A-Z0-9]{8,20})',
        r'[A-Z]{2}\d{10,18}',  # 通用发票号码格式
    ]

    def __init__(self, llm_client=None):
        """
        初始化去重器

        Args:
            llm_client: 大模型客户端（可选，用于复杂发票号码提取）
        """
        self.llm_client = llm_client
        self.invoice_groups: Dict[str, List[Path]] = {}
        self.duplicates_removed: int = 0

    def extract_invoice_number(self, content: str) -> Optional[str]:
        """
        从文本内容中提取发票号码

        Args:
            content: 文件文本内容

        Returns:
            Optional[str]: 发票号码，未找到返回None
        """
        # 尝试正则匹配
        for pattern in self.INVOICE_NUMBER_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0).upper()

        # 如果没找到，尝试调用大模型
        if self.llm_client:
            return self._llm_extract_invoice_number(content)

        return None

    def _llm_extract_invoice_number(self, content: str) -> Optional[str]:
        """
        使用大模型提取发票号码

        Args:
            content: 文件文本内容

        Returns:
            Optional[str]: 发票号码
        """
        try:
            prompt = f"""从以下发票文本中提取发票号码。发票号码通常是一串数字或字母组合。

文本内容：
{content[:1000]}

请只返回发票号码，不要其他内容。如果没有找到发票号码，返回"未找到"。"""

            response = self.llm_client.chat_completion(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个专业的发票信息提取助手"},
                    {"role": "user", "content": prompt}
                ]
            )

            result = response.choices[0].message.content.strip()
            if result and result != "未找到":
                return result

        except Exception as e:
            logger.warning(f"大模型提取发票号码失败: {e}")

        return None

    def deduplicate(self, files: List[Path], read_func=None) -> List[Path]:
        """
        对文件列表进行去重

        Args:
            files: 文件路径列表
            read_func: 读取文件内容的函数，签名为 read_func(path: Path) -> str

        Returns:
            List[Path]: 去重后的文件列表
        """
        self.invoice_groups = {}
        self.duplicates_removed = 0

        # 分组：按发票号码分组
        for file_path in files:
            invoice_number = None

            # 尝试从文件名提取发票号码
            invoice_number = self._extract_from_filename(file_path.name)

            # 如果没找到，尝试读取文件内容
            if not invoice_number and read_func:
                try:
                    content = read_func(file_path)
                    if content:
                        invoice_number = self.extract_invoice_number(content)
                except Exception as e:
                    logger.warning(f"读取文件失败 {file_path}: {e}")

            # 使用文件路径作为唯一标识
            if not invoice_number:
                invoice_number = f"__UNIQUE__{file_path.as_posix()}"

            if invoice_number not in self.invoice_groups:
                self.invoice_groups[invoice_number] = []
            self.invoice_groups[invoice_number].append(file_path)

        # 选择保留的文件
        keep_files = []
        for invoice_number, file_list in self.invoice_groups.items():
            if invoice_number.startswith("__UNIQUE__"):
                # 唯一文件直接保留
                keep_files.append(file_list[0])
            else:
                # 有发票号码的，优先保留PDF
                pdf_files = [f for f in file_list if f.suffix.lower() == '.pdf']
                if pdf_files:
                    keep_files.append(pdf_files[0])
                    # 记录被删除的重复文件
                    self.duplicates_removed += len(file_list) - 1
                else:
                    keep_files.append(file_list[0])
                    self.duplicates_removed += len(file_list) - 1

        logger.info(f"去重完成：保留 {len(keep_files)} 个文件，删除 {self.duplicates_removed} 个重复文件")
        return keep_files

    def _extract_from_filename(self, filename: str) -> Optional[str]:
        """
        从文件名中提取发票号码

        Args:
            filename: 文件名

        Returns:
            Optional[str]: 发票号码
        """
        # 常见发票号码模式
        patterns = [
            r'([A-Z]{2}\d{10,12})',  # 如：FP1234567890
            r'(\d{12,16})',          # 纯数字长号码
            r'([A-Z0-9]{10,20})'     # 混合字母数字
        ]

        name_without_ext = Path(filename).stem
        for pattern in patterns:
            match = re.search(pattern, name_without_ext, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        return None

    def get_duplicate_report(self) -> Dict[str, any]:
        """
        获取去重报告

        Returns:
            Dict: 去重统计信息
        """
        report = {
            'total_groups': len(self.invoice_groups),
            'duplicate_groups': sum(1 for files in self.invoice_groups.values() if len(files) > 1),
            'files_removed': self.duplicates_removed,
            'groups_detail': {}
        }

        for invoice_num, files in self.invoice_groups.items():
            if len(files) > 1:
                report['groups_detail'][invoice_num] = [f.name for f in files]

        return report
