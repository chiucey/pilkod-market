#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF发票解析器
支持PDF格式发票、行程单、酒店发票等的解析
"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PDFParser:
    """PDF发票解析器"""

    def __init__(self, extractor=None):
        """
        初始化PDF解析器

        Args:
            extractor: 信息提取器（可选）
        """
        self.extractor = extractor
        self._pdfplumber_available = False

        # 尝试导入pdfplumber
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
            self._pdfplumber_available = True
        except ImportError:
            logger.warning("pdfplumber未安装，部分PDF解析功能可能受限")

    def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        解析PDF文件

        Args:
            file_path: PDF文件路径

        Returns:
            Optional[Dict]: 解析结果，失败返回None
        """
        try:
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return None

            # 提取文本内容
            text = self._extract_text(file_path)
            if not text:
                logger.warning(f"无法从PDF提取文本: {file_path}")
                text = ""

            # 识别发票类型
            invoice_type = self._identify_invoice_type(text)

            # 根据类型解析
            if invoice_type == 'flight':
                return self._parse_flight_ticket(text, file_path)
            elif invoice_type == 'hotel':
                return self._parse_hotel_invoice(text, file_path)
            elif invoice_type == 'e_invoice':
                return self._parse_e_invoice(text, file_path)
            else:
                return self._parse_general_invoice(text, file_path)

        except Exception as e:
            logger.error(f"PDF解析失败 {file_path}: {e}")
            return None

    def _extract_text(self, file_path: Path) -> str:
        """
        从PDF提取文本

        Args:
            file_path: PDF文件路径

        Returns:
            str: 提取的文本内容
        """
        if not self._pdfplumber_available:
            return ""

        text = ""
        try:
            with self.pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                    # 尝试提取表格
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"

        except Exception as e:
            logger.warning(f"PDF文本提取失败: {e}")

        return text

    def _identify_invoice_type(self, text: str) -> str:
        """
        识别发票类型

        Args:
            text: 发票文本

        Returns:
            str: 发票类型
        """
        text_lower = text.lower()

        # 航空行程单
        if any(keyword in text for keyword in ['行程单', '电子客票', '航空', '航班', '机票']):
            return 'flight'

        # 酒店住宿
        if any(keyword in text for keyword in ['住宿', '酒店', '宾馆', '房费', '房晚']):
            return 'hotel'

        # 增值税电子发票
        if '电子发票' in text or '增值税' in text:
            return 'e_invoice'

        # 携程订单
        if '携程' in text:
            return 'ctrip'

        # 火车票
        if any(keyword in text for keyword in ['高铁', '火车', '动车', '铁路']):
            return 'train'

        # 保险
        if '保险' in text and ('航空' in text or '意外' in text):
            return 'insurance'

        return 'other'

    def _parse_flight_ticket(self, text: str, file_path: Path) -> Dict[str, Any]:
        """
        解析机票行程单

        Args:
            text: 发票文本
            file_path: 文件路径

        Returns:
            Dict: 解析结果
        """
        result = {
            'invoice_no': None,
            'date': None,
            'amount': 0.0,
            'type': 'flight',
            'sub_type': '机票',
            'description': '航空运输',
            'departure': None,
            'arrival': None,
            'flight_no': None,
            'flight_date': None,
            'insurance': 0.0,
            'remarks': '',
            'status': 'extracted',
            'file_path': str(file_path),
            'file_name': file_path.name
        }

        # 提取航班号
        import re
        flight_match = re.search(r'(?:航班号|航班|No)[：:\s]*([A-Z]{2}\d{3,4})', text, re.IGNORECASE)
        if flight_match:
            result['flight_no'] = flight_match.group(1).upper()

        # 提取出发地和目的地
        dep_match = re.search(r'(?:出发|始发|出发地|始发地)[：:\s]*([^\s,，]+)', text)
        arr_match = re.search(r'(?:到达|目的|目的地)[：:\s]*([^\s,，]+)', text)
        if dep_match:
            result['departure'] = dep_match.group(1)
        if arr_match:
            result['arrival'] = arr_match.group(1)

        # 提取日期
        date_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', text)
        if date_match:
            result['date'] = date_match.group(1).replace('年', '-').replace('月', '-').replace('日', '')
            result['flight_date'] = result['date']

        # 提取金额
        amount_patterns = [
            r'(?:票价|机票价|实付)[：:\s]*[￥¥]?\s*(\d+\.?\d*)',
            r'(?:合计|总额)[：:\s]*[￥¥]?\s*(\d+\.?\d*)',
            r'[￥¥]\s*(\d+\.?\d*)',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    result['amount'] = float(match.group(1))
                    break
                except ValueError:
                    continue

        # 提取保险金额
        insurance_match = re.search(r'(?:保险|航意险)[：:\s]*[￥¥]?\s*(\d+\.?\d*)', text)
        if insurance_match:
            try:
                result['insurance'] = float(insurance_match.group(1))
            except ValueError:
                pass

        # 提取备注（通常包含航班信息）
        remarks_match = re.search(r'备注[：:]\s*([^\n]+)', text)
        if remarks_match:
            result['remarks'] = remarks_match.group(1)

        # 如果有航班号，加入描述
        if result.get('flight_no'):
            result['description'] = f"航班{result['flight_no']}"

        return result

    def _parse_hotel_invoice(self, text: str, file_path: Path) -> Dict[str, Any]:
        """
        解析酒店住宿发票

        Args:
            text: 发票文本
            file_path: 文件路径

        Returns:
            Dict: 解析结果
        """
        result = {
            'invoice_no': None,
            'date': None,
            'amount': 0.0,
            'type': 'hotel',
            'sub_type': '住宿',
            'description': '酒店住宿',
            'departure': None,
            'arrival': None,
            'nights': None,
            'remarks': '',
            'status': 'extracted',
            'file_path': str(file_path),
            'file_name': file_path.name
        }

        import re

        # 提取发票号码
        invoice_match = re.search(r'(?:发票号(?:码)?)[：:\s]*([A-Z0-9]{8,20})', text, re.IGNORECASE)
        if invoice_match:
            result['invoice_no'] = invoice_match.group(1).upper()

        # 提取日期
        date_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', text)
        if date_match:
            result['date'] = date_match.group(1).replace('年', '-').replace('月', '-').replace('日', '')

        # 提取金额
        amount_match = re.search(r'(?:金额|总额|价税合计|实付)[：:\s]*[￥¥]?\s*(\d+\.?\d*)', text)
        if amount_match:
            try:
                result['amount'] = float(amount_match.group(1))
            except ValueError:
                pass

        # 提取住宿天数
        nights_match = re.search(r'(\d+)\s*(?:晚|天|间)', text)
        if nights_match:
            result['nights'] = int(nights_match.group(1))

        # 提取酒店名称
        hotel_match = re.search(r'([\u4e00-\u9fa5]{2,20})(?:酒店|宾馆|旅馆)', text)
        if hotel_match:
            result['description'] = f"{hotel_match.group(1)}住宿"

        return result

    def _parse_e_invoice(self, text: str, file_path: Path) -> Dict[str, Any]:
        """
        解析增值税电子发票

        Args:
            text: 发票文本
            file_path: 文件路径

        Returns:
            Dict: 解析结果
        """
        result = {
            'invoice_no': None,
            'date': None,
            'amount': 0.0,
            'type': 'other',
            'sub_type': '增值税发票',
            'description': '',
            'departure': None,
            'arrival': None,
            'tax_amount': 0.0,
            'remarks': '',
            'status': 'extracted',
            'file_path': str(file_path),
            'file_name': file_path.name
        }

        import re

        # 提取发票号码
        patterns = [
            r'发票号码[：:]\s*([A-Z0-9]{8,20})',
            r'发票号[：:]\s*([A-Z0-9]{8,20})',
            r'NO[：:\s]*([A-Z0-9]{8,20})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['invoice_no'] = match.group(1).upper()
                break

        # 提取日期
        date_match = re.search(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)', text)
        if date_match:
            result['date'] = date_match.group(1).replace('年', '-').replace('月', '-').replace('日', '')

        # 提取金额
        amount_match = re.search(r'(?:价税合计|实付金额|实付)[：:\s]*[￥¥]?\s*(\d+\.?\d*)', text)
        if amount_match:
            try:
                result['amount'] = float(amount_match.group(1))
            except ValueError:
                pass

        # 提取税额
        tax_match = re.search(r'税额[：:\s]*[￥¥]?\s*(\d+\.?\d*)', text)
        if tax_match:
            try:
                result['tax_amount'] = float(tax_match.group(1))
            except ValueError:
                pass

        # 提取商品/服务描述
        desc_match = re.search(r'(?:商品|服务|项目)[：:]\s*([^\n]{5,50})', text)
        if desc_match:
            result['description'] = desc_match.group(1).strip()

        return result

    def _parse_general_invoice(self, text: str, file_path: Path) -> Dict[str, Any]:
        """
        解析通用发票

        Args:
            text: 发票文本
            file_path: 文件路径

        Returns:
            Dict: 解析结果
        """
        result = {
            'invoice_no': None,
            'date': None,
            'amount': 0.0,
            'type': 'other',
            'sub_type': '其他',
            'description': '',
            'departure': None,
            'arrival': None,
            'remarks': '',
            'status': 'extracted',
            'file_path': str(file_path),
            'file_name': file_path.name
        }

        # 如果有提取器，使用提取器
        if self.extractor:
            return self.extractor.extract(text, 'pdf')

        return result
