#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
携程订单XML解析器
解析携程等OTA订单导出的XML格式文件
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import xml.etree.ElementTree as ET
import logging
import re

logger = logging.getLogger(__name__)


class CtripXMLParser:
    """携程订单XML解析器"""

    def __init__(self):
        """初始化携程XML解析器"""
        pass

    def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        解析携程订单XML文件

        Args:
            file_path: XML文件路径

        Returns:
            Optional[Dict]: 解析结果
        """
        try:
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return None

            # 解析XML
            tree = ET.parse(file_path)
            root = tree.getroot()

            # 检测XML命名空间
            ns = self._detect_namespace(root)

            # 提取订单信息
            result = {
                'invoice_no': None,
                'date': None,
                'amount': 0.0,
                'type': 'ctrip_order',
                'sub_type': '携程订单',
                'description': '携程订单',
                'departure': None,
                'arrival': None,
                'order_no': None,
                'items': [],
                'remarks': '',
                'status': 'extracted',
                'file_path': str(file_path),
                'file_name': file_path.name
            }

            # 提取订单号
            result['order_no'] = self._find_text(root, './/OrderNo', ns) or \
                                 self._find_text(root, './/OrderID', ns) or \
                                 self._find_text(root, './/订单号', ns)
            result['invoice_no'] = result['order_no']

            # 提取订单日期
            result['date'] = self._format_date(
                self._find_text(root, './/OrderDate', ns) or
                self._find_text(root, './/下单时间', ns) or
                self._find_text(root, './/CreateTime', ns)
            )

            # 提取总金额
            amount_str = self._find_text(root, './/TotalAmount', ns) or \
                         self._find_text(root, './/OrderAmount', ns) or \
                         self._find_text(root, './/TotalPrice', ns) or \
                         self._find_text(root, './/总金额', ns)
            if amount_str:
                result['amount'] = self._parse_amount(amount_str)

            # 提取订单项目
            items = self._extract_order_items(root, ns)
            result['items'] = items

            # 根据项目类型确定主类型
            if items:
                item_types = [item.get('type', '') for item in items]
                if any('flight' in t.lower() or '机票' in t for t in item_types):
                    result['type'] = 'flight'
                    result['sub_type'] = '机票'
                elif any('hotel' in t.lower() or '酒店' in t or '住宿' in t for t in item_types):
                    result['type'] = 'hotel'
                    result['sub_type'] = '住宿'

            # 提取出发地和目的地（适用于机票订单）
            result['departure'] = self._find_text(root, './/DepartureCity', ns) or \
                                   self._find_text(root, './/Departure', ns) or \
                                   self._find_text(root, './/出发地', ns)
            result['arrival'] = self._find_text(root, './/ArrivalCity', ns) or \
                                self._find_text(root, './/Arrival', ns) or \
                                self._find_text(root, './/目的地', ns)

            # 提取备注
            result['remarks'] = self._find_text(root, './/Remarks', ns) or \
                               self._find_text(root, './/备注', ns) or ''

            return result

        except ET.ParseError as e:
            logger.error(f"XML解析错误 {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"携程XML解析失败 {file_path}: {e}")
            return None

    def _detect_namespace(self, root: ET.Element) -> Dict[str, str]:
        """
        检测XML命名空间

        Args:
            root: XML根元素

        Returns:
            Dict: 命名空间字典
        """
        ns = {}
        match = re.match(r'\{(.+)\}', root.tag)
        if match:
            ns_prefix = 'ns'
            ns[ns_prefix] = match.group(1)
        return ns

    def _find_text(self, element: ET.Element, xpath: str, ns: Dict = None) -> Optional[str]:
        """
        安全查找元素文本

        Args:
            element: XML元素
            xpath: XPath表达式
            ns: 命名空间字典

        Returns:
            Optional[str]: 元素文本
        """
        found = element.find(xpath, ns)
        return found.text.strip() if found is not None and found.text else None

    def _extract_order_items(self, root: ET.Element, ns: Dict) -> List[Dict[str, Any]]:
        """
        提取订单项目

        Args:
            root: XML根元素
            ns: 命名空间字典

        Returns:
            List[Dict]: 订单项目列表
        """
        items = []

        # 尝试多种订单项目XPath
        item_paths = [
            './/OrderItem',
            './/Item',
            './/OrderDetail',
            './/Detail',
            './/订单项',
            './/项目'
        ]

        item_elements = None
        for path in item_paths:
            item_elements = root.findall(path, ns)
            if item_elements:
                break

        if not item_elements:
            return items

        for item_elem in item_elements:
            item = {
                'type': None,
                'description': None,
                'amount': 0.0,
                'date': None
            }

            # 提取项目类型
            item['type'] = self._find_text(item_elem, './/ItemType', ns) or \
                          self._find_text(item_elem, './/Type', ns) or \
                          self._find_text(item_elem, './/类型', ns)

            # 提取项目描述
            item['description'] = self._find_text(item_elem, './/Description', ns) or \
                                 self._find_text(item_elem, './/Name', ns) or \
                                 self._find_text(item_elem, './/名称', ns)

            # 提取金额
            amount_str = self._find_text(item_elem, './/Amount', ns) or \
                        self._find_text(item_elem, './/Price', ns) or \
                        self._find_text(item_elem, './/金额', ns) or \
                        self._find_text(item_elem, './/价格', ns)
            if amount_str:
                item['amount'] = self._parse_amount(amount_str)

            # 提取日期
            item['date'] = self._format_date(
                self._find_text(item_elem, './/ServiceDate', ns) or
                self._find_text(item_elem, './/Date', ns) or
                self._find_text(item_elem, './/日期', ns)
            )

            if item['type'] or item['description']:
                items.append(item)

        return items

    def _parse_amount(self, amount_str: str) -> float:
        """
        解析金额字符串

        Args:
            amount_str: 金额字符串

        Returns:
            float: 解析后的金额
        """
        if not amount_str:
            return 0.0

        # 移除非数字字符（保留小数点）
        cleaned = re.sub(r'[^\d.]', '', amount_str)
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    def _format_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        格式化日期

        Args:
            date_str: 日期字符串

        Returns:
            Optional[str]: 格式化的日期
        """
        if not date_str:
            return None

        # 移除时间部分，只保留日期
        date_str = date_str.split('T')[0] if 'T' in date_str else date_str
        date_str = date_str.split(' ')[0]

        # 尝试标准化格式
        date_str = date_str.replace('/', '-')

        # 验证是否为有效日期
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            return date_str
