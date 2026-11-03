#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
图片发票解析器
支持JPG、PNG等图片格式的高铁票、发票等的OCR识别
"""
from typing import Dict, Any, Optional
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class ImageParser:
    """图片发票解析器"""

    def __init__(self, extractor=None):
        """
        初始化图片解析器

        Args:
            extractor: 信息提取器（可选）
        """
        self.extractor = extractor
        self._paddleocr_available = False
        self._easyocr_available = False

        # 尝试导入OCR库
        try:
            from paddleocr import PaddleOCR
            self.paddleocr = PaddleOCR
            self._paddleocr_available = True
            logger.info("PaddleOCR 已启用")
        except ImportError:
            logger.warning("PaddleOCR未安装，图片解析功能受限")

        try:
            import easyocr
            self.easyocr = easyocr
            self._easyocr_available = True
            logger.info("EasyOCR 已启用")
        except ImportError:
            logger.warning("EasyOCR未安装，图片解析功能受限")

    def parse(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        解析图片文件

        Args:
            file_path: 图片文件路径

        Returns:
            Optional[Dict]: 解析结果
        """
        try:
            if not file_path.exists():
                logger.error(f"文件不存在: {file_path}")
                return None

            # 提取文本内容
            text = self._extract_text(file_path)
            if not text:
                logger.warning(f"无法从图片提取文本: {file_path}")
                return None

            # 识别发票类型
            invoice_type = self._identify_invoice_type(text)

            # 根据类型解析
            if invoice_type == 'train':
                return self._parse_train_ticket(text, file_path)
            else:
                return self._parse_general_image(text, file_path)

        except Exception as e:
            logger.error(f"图片解析失败 {file_path}: {e}")
            return None

    def _extract_text(self, file_path: Path) -> str:
        """
        从图片提取文本（OCR）

        Args:
            file_path: 图片文件路径

        Returns:
            str: 提取的文本内容
        """
        # 优先使用PaddleOCR
        if self._paddleocr_available:
            return self._extract_with_paddleocr(file_path)

        # 备选使用EasyOCR
        if self._easyocr_available:
            return self._extract_with_easyocr(file_path)

        logger.warning("没有可用的OCR库，无法解析图片")
        return ""

    def _extract_with_paddleocr(self, file_path: Path) -> str:
        """
        使用PaddleOCR提取文本

        Args:
            file_path: 图片文件路径

        Returns:
            str: 提取的文本
        """
        try:
            from paddleocr import PaddleOCR

            ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            result = ocr.ocr(str(file_path), cls=True)

            text_lines = []
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text_lines.append(line[1][0])

            return '\n'.join(text_lines)

        except Exception as e:
            logger.warning(f"PaddleOCR提取失败: {e}")
            return ""

    def _extract_with_easyocr(self, file_path: Path) -> str:
        """
        使用EasyOCR提取文本

        Args:
            file_path: 图片文件路径

        Returns:
            str: 提取的文本
        """
        try:
            reader = self.easyocr.Reader(['ch_sim', 'en'])
            result = reader.readtext(str(file_path))

            text_lines = []
            for item in result:
                if len(item) >= 2:
                    text_lines.append(item[1])

            return '\n'.join(text_lines)

        except Exception as e:
            logger.warning(f"EasyOCR提取失败: {e}")
            return ""

    def _identify_invoice_type(self, text: str) -> str:
        """
        识别发票类型

        Args:
            text: 图片OCR文本

        Returns:
            str: 发票类型
        """
        text_lower = text.lower()

        # 高铁票
        if any(keyword in text for keyword in ['高铁', '动车', '火车', '铁路', 'G字', 'D字', 'T字', 'K字']):
            return 'train'

        # 行程单
        if '行程单' in text or '电子客票' in text:
            return 'flight'

        # 出租车
        if any(keyword in text for keyword in ['出租车', '滴滴', '打车']):
            return 'taxi'

        return 'other'

    def _parse_train_ticket(self, text: str, file_path: Path) -> Dict[str, Any]:
        """
        解析高铁票

        Args:
            text: OCR文本
            file_path: 文件路径

        Returns:
            Dict: 解析结果
        """
        result = {
            'invoice_no': None,
            'date': None,
            'amount': 0.0,
            'type': 'train',
            'sub_type': '高铁',
            'description': '铁路运输',
            'departure': None,
            'arrival': None,
            'train_no': None,
            'seat_type': None,
            'passenger': None,
            'remarks': '',
            'status': 'extracted',
            'file_path': str(file_path),
            'file_name': file_path.name
        }

        # 提取车次号
        train_match = re.search(r'([GDTKZ]\d{1,4})', text)
        if train_match:
            result['train_no'] = train_match.group(1)

        # 提取出发地和目的地
        route_match = re.search(r'([\u4e00-\u9fa5]+)\s*(?:至|→)\s*([\u4e00-\u9fa5]+)', text)
        if route_match:
            result['departure'] = route_match.group(1)
            result['arrival'] = route_match.group(2)

        # 提取日期时间
        datetime_match = re.search(r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})[日]?\s*(\d{1,2}:\d{2})?', text)
        if datetime_match:
            year, month, day = datetime_match.group(1, 2, 3)
            time_part = datetime_match.group(4) or ''
            result['date'] = f"{year}-{int(month):02d}-{int(day):02d}"
            if time_part:
                result['date'] += f" {time_part}"

        # 提取金额
        amount_match = re.search(r'(?:票价|金额|合计)[：:\s]*[￥¥]?\s*(\d+\.?\d*)', text)
        if amount_match:
            try:
                result['amount'] = float(amount_match.group(1))
            except ValueError:
                pass

        # 提取座位类型
        seat_patterns = ['二等座', '一等座', '商务座', '特等座', '硬座', '软座', '硬卧', '软卧']
        for seat in seat_patterns:
            if seat in text:
                result['seat_type'] = seat
                break

        # 提取乘客姓名
        passenger_match = re.search(r'乘客[：:]\s*([\u4e00-\u9fa5]+)', text)
        if passenger_match:
            result['passenger'] = passenger_match.group(1)

        # 更新描述
        if result.get('train_no'):
            desc = result['train_no']
            if result.get('seat_type'):
                desc += result['seat_type']
            result['description'] = desc

        return result

    def _parse_general_image(self, text: str, file_path: Path) -> Dict[str, Any]:
        """
        解析通用图片发票

        Args:
            text: OCR文本
            file_path: 文件路径

        Returns:
            Dict: 解析结果
        """
        result = {
            'invoice_no': None,
            'date': None,
            'amount': 0.0,
            'type': 'other',
            'sub_type': '图片发票',
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
            return self.extractor.extract(text, 'image')

        return result
