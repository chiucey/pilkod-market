#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
发票信息提取模块
使用大模型从发票文本中提取结构化信息
"""
import json
import re
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InvoiceExtractor:
    """发票信息提取器"""

    # 发票类型关键词
    INVOICE_TYPE_KEYWORDS = {
        'flight': ['行程单', '电子客票', '航空', '机票', '航班'],
        'train': ['高铁', '火车', '铁路', '动车'],
        'hotel': ['住宿', '酒店', '宾馆', '旅馆'],
        'meal': ['餐饮', '餐费', '餐服务'],
        'insurance': ['保险', '意外险', '航意险'],
        'taxi': ['出租车', '打车', '滴滴'],
        'other': []
    }

    # 金额正则
    AMOUNT_PATTERN = r'(?:金额|总额|价税合计|实付)[：:\s]*[￥¥]?\s*(\d+\.?\d*)'

    # 日期正则
    DATE_PATTERNS = [
        r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?)',
        r'(\d{4}\d{2}\d{2})',
    ]

    def __init__(self, llm_client=None):
        """
        初始化提取器

        Args:
            llm_client: 大模型客户端
        """
        self.llm_client = llm_client

    def extract(self, text: str, file_type: str = 'pdf') -> Dict[str, Any]:
        """
        从发票文本中提取结构化信息

        Args:
            text: 发票文本内容
            file_type: 文件类型

        Returns:
            Dict[str, Any]: 提取的发票信息
        """
        # 优先使用规则提取
        result = self._rule_based_extract(text)

        # 如果规则提取不完整，尝试大模型增强
        if self.llm_client and self._needs_llm_enhancement(result):
            result = self._llm_enhance(text, result)

        # 确保所有必要字段都存在
        result = self._ensure_required_fields(result)

        return result

    def _rule_based_extract(self, text: str) -> Dict[str, Any]:
        """
        基于规则的信息提取

        Args:
            text: 发票文本

        Returns:
            Dict: 提取的信息
        """
        result = {
            'invoice_no': None,
            'date': None,
            'amount': 0.0,
            'type': 'other',
            'sub_type': None,
            'description': '',
            'departure': None,
            'arrival': None,
            'remarks': '',
            'status': 'pending',
            'file_path': None
        }

        # 提取发票号码
        result['invoice_no'] = self._extract_invoice_number(text)

        # 提取日期
        result['date'] = self._extract_date(text)

        # 提取金额
        result['amount'] = self._extract_amount(text)

        # 识别发票类型
        result['type'], result['sub_type'] = self._identify_invoice_type(text)

        # 提取描述
        result['description'] = self._extract_description(text)

        # 提取出发地和目的地（适用于交通票据）
        result['departure'], result['arrival'] = self._extract_route(text)

        # 提取备注信息
        result['remarks'] = self._extract_remarks(text)

        return result

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """提取发票号码"""
        patterns = [
            r'发票号码[：:]\s*([A-Z0-9]{8,20})',
            r'发票号[：:]\s*([A-Z0-9]{8,20})',
            r'NO[\.:：]\s*([A-Z0-9]{8,20})',
            r'编号[：:]\s*([A-Z0-9]{8,20})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """提取日期"""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(1)
                # 标准化日期格式
                date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                return date_str

        return None

    def _extract_amount(self, text: str) -> float:
        """提取金额"""
        # 尝试多个金额相关字段
        patterns = [
            r'(?:价税合计|实付金额|实付)[：:\s]*[￥¥]?\s*(\d+\.?\d*)',
            r'总额[：:\s]*[￥¥]?\s*(\d+\.?\d*)',
            r'金额[：:\s]*[￥¥]?\s*(\d+\.?\d*)',
            r'[￥¥]\s*(\d+\.?\d*)',
        ]

        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount = float(match)
                    if 0 < amount < 100000:  # 合理金额范围
                        amounts.append(amount)
                except ValueError:
                    continue

        # 返回最大金额（通常是总价）
        return max(amounts) if amounts else 0.0

    def _identify_invoice_type(self, text: str) -> tuple:
        """
        识别发票类型

        Returns:
            tuple: (type, sub_type)
        """
        text_lower = text.lower()

        for inv_type, keywords in self.INVOICE_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return inv_type, keyword

        return 'other', '其他'

    def _extract_description(self, text: str) -> str:
        """提取发票描述"""
        # 尝试提取服务名称、商品名称等
        patterns = [
            r'(?:服务名称|项目|商品)[：:]\s*([^\n]{2,30})',
            r'([^\n]{5,50})',  # 通用描述
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 3:
                    return desc

        return '未识别内容'

    def _extract_route(self, text: str) -> tuple:
        """
        提取出发地和目的地

        Returns:
            tuple: (departure, arrival)
        """
        departure = None
        arrival = None

        # 航空行程单格式
        if '行程单' in text or '出发' in text:
            dep_match = re.search(r'出发[：:]\s*([^\s,，]+)', text)
            arr_match = re.search(r'到达[：:]\s*([^\s,，]+)', text)
            if dep_match:
                departure = dep_match.group(1)
            if arr_match:
                arrival = arr_match.group(1)

        # 高铁格式
        if departure is None and arrival is None:
            route_match = re.search(r'([\u4e00-\u9fa5]+)\s*至\s*([\u4e00-\u9fa5]+)', text)
            if route_match:
                departure = route_match.group(1)
                arrival = route_match.group(2)

        return departure, arrival

    def _extract_remarks(self, text: str) -> str:
        """提取备注信息"""
        remarks_match = re.search(r'备注[：:]\s*([^\n]+)', text)
        if remarks_match:
            return remarks_match.group(1).strip()
        return ''

    def _needs_llm_enhancement(self, result: Dict) -> bool:
        """判断是否需要大模型增强"""
        # 如果关键字段缺失，需要大模型增强
        if not result.get('invoice_no'):
            return True
        if not result.get('date'):
            return True
        if result.get('amount', 0) == 0:
            return True
        if result.get('type') == 'other' and not result.get('description'):
            return True
        return False

    def _llm_enhance(self, text: str, result: Dict) -> Dict:
        """
        使用大模型增强信息提取

        Args:
            text: 原始文本
            result: 规则提取的结果

        Returns:
            Dict: 增强后的结果
        """
        try:
            prompt = f"""你是专业的发票信息提取助手。请从以下发票文本中提取关键信息。

提取字段：
1. invoice_no - 发票号码
2. date - 开票日期（格式：YYYY-MM-DD）
3. amount - 金额（数字）
4. type - 发票类型（flight/train/hotel/meal/insurance/taxi/other）
5. description - 内容描述
6. departure - 出发地（如适用）
7. arrival - 目的地（如适用）
8. remarks - 备注信息

文本内容：
{text[:2000]}

请以JSON格式返回结果。"""

            response = self.llm_client.chat_completion(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": "你是一个专业的发票信息提取助手"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            llm_result = json.loads(response.choices[0].message.content)

            # 合并结果，优先使用大模型结果
            for key, value in llm_result.items():
                if value and (not result.get(key) or result.get(key) == 'pending'):
                    result[key] = value

            result['status'] = 'extracted_with_llm'

        except Exception as e:
            logger.warning(f"大模型增强失败: {e}")
            result['status'] = 'extracted_rule_only'

        return result

    def _ensure_required_fields(self, result: Dict) -> Dict:
        """确保所有必要字段都存在"""
        required_fields = {
            'invoice_no': 'UNKNOWN',
            'date': '1970-01-01',
            'amount': 0.0,
            'type': 'other',
            'sub_type': '其他',
            'description': '未识别内容',
            'departure': None,
            'arrival': None,
            'remarks': '',
            'status': 'extracted'
        }

        for field, default_value in required_fields.items():
            if field not in result or result[field] is None:
                result[field] = default_value

        return result
