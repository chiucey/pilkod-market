#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件重命名处理器
将发票文件按规范格式重命名
"""
from typing import List, Dict, Any
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


class RenameProcessor:
    """文件重命名处理器"""

    # 文件名中的非法字符
    ILLEGAL_CHARS = r'[<>:"/\\|?*\x00-\x1f]'

    # 类型名称映射
    TYPE_NAMES = {
        'flight': '机票',
        'train': '高铁',
        'hotel': '住宿',
        'meal': '餐饮',
        'insurance': '保险',
        'taxi': '打车',
        'ctrip_order': '携程订单',
        'other': '其他'
    }

    def __init__(self):
        """初始化重命名处理器"""
        self.rename_history: List[Dict] = []

    def rename_files(self, invoices: List[Dict]) -> int:
        """
        重命名发票文件

        Args:
            invoices: 发票列表

        Returns:
            int: 成功重命名的文件数
        """
        success_count = 0

        for invoice in invoices:
            try:
                old_path = invoice.get('file_path')
                if not old_path:
                    continue

                old_path = Path(old_path)
                if not old_path.exists():
                    continue

                # 生成新文件名
                new_name = self._generate_filename(invoice)

                # 处理文件名冲突
                new_name = self._resolve_conflict(old_path.parent, new_name)

                # 执行重命名
                new_path = old_path.parent / new_name
                old_path.rename(new_path)

                # 记录历史
                self.rename_history.append({
                    'old_path': str(old_path),
                    'new_path': str(new_path),
                    'invoice_no': invoice.get('invoice_no'),
                    'status': 'success'
                })

                # 更新发票记录中的文件路径
                invoice['file_path'] = str(new_path)
                invoice['new_file_name'] = new_name

                success_count += 1
                logger.info(f"重命名: {old_path.name} -> {new_name}")

            except Exception as e:
                logger.warning(f"重命名失败: {invoice.get('file_path')}: {e}")
                self.rename_history.append({
                    'old_path': invoice.get('file_path'),
                    'new_path': None,
                    'invoice_no': invoice.get('invoice_no'),
                    'status': 'failed',
                    'error': str(e)
                })

        return success_count

    def _generate_filename(self, invoice: Dict) -> str:
        """
        生成规范化文件名

        格式: {类型}_{日期}_{描述}_{金额}.{扩展名}
        示例: 机票_2024-01-15_南京-北京_MU1234_560.00.pdf

        Args:
            invoice: 发票信息

        Returns:
            str: 生成的文件名
        """
        # 获取类型
        inv_type = invoice.get('type', 'other')
        type_name = self.TYPE_NAMES.get(inv_type, invoice.get('sub_type', '其他'))

        # 获取日期
        date = invoice.get('date', 'unknown')
        if date and date != 'unknown':
            # 标准化日期格式
            date = date[:10]  # 只取日期部分
        else:
            date = 'unknown'

        # 获取描述
        description = invoice.get('description', '')
        if description:
            # 清理描述中的特殊字符
            description = self._clean_filename(description)
            # 截取长度
            description = description[:20]
        else:
            description = invoice.get('sub_type', '')

        # 获取金额
        amount = invoice.get('amount', 0)
        if isinstance(amount, str):
            try:
                amount = float(amount)
            except ValueError:
                amount = 0
        amount_str = f"{amount:.2f}"

        # 特殊处理机票（添加航班号）
        if inv_type == 'flight' and invoice.get('flight_no'):
            flight_no = invoice.get('flight_no')
            filename = f"{type_name}_{date}_{flight_no}_{amount_str}"
        else:
            # 添加出发地和目的地
            departure = invoice.get('departure', '')
            arrival = invoice.get('arrival', '')
            if departure and arrival:
                route = f"{departure}-{arrival}"
            else:
                route = description

            filename = f"{type_name}_{date}_{route}_{amount_str}"

        # 添加扩展名
        old_path = invoice.get('file_path')
        if old_path:
            ext = Path(old_path).suffix.lower()
        else:
            ext = '.pdf'

        return f"{filename}{ext}"

    def _clean_filename(self, text: str) -> str:
        """
        清理文件名中的非法字符

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本
        """
        # 移除非法字符
        cleaned = re.sub(self.ILLEGAL_CHARS, '', text)

        # 移除多余空格
        cleaned = ' '.join(cleaned.split())

        return cleaned

    def _resolve_conflict(self, directory: Path, filename: str) -> str:
        """
        处理文件名冲突

        Args:
            directory: 文件目录
            filename: 原始文件名

        Returns:
            str: 不冲突的文件名
        """
        path = directory / filename

        if not path.exists():
            return filename

        # 分离文件名和扩展名
        stem = Path(filename).stem
        suffix = Path(filename).suffix

        # 添加序号
        counter = 1
        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            if not (directory / new_filename).exists():
                return new_filename
            counter += 1

            # 防止无限循环
            if counter > 1000:
                return f"{stem}_{timestamp()}{suffix}"

    def get_rename_report(self) -> Dict[str, Any]:
        """
        获取重命名报告

        Returns:
            Dict: 重命名统计信息
        """
        success = [h for h in self.rename_history if h['status'] == 'success']
        failed = [h for h in self.rename_history if h['status'] == 'failed']

        return {
            'total': len(self.rename_history),
            'success': len(success),
            'failed': len(failed),
            'details': self.rename_history
        }


def timestamp() -> str:
    """生成时间戳字符串"""
    from datetime import datetime
    return datetime.now().strftime('%H%M%S')
