#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
出差行程处理器
自动识别和关联出差相关的发票票据
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class TravelProcessor:
    """出差行程处理器"""

    def __init__(self, base_city: str = "南京"):
        """
        初始化处理器

        Args:
            base_city: 基准城市（出差出发地和返回目的地）
        """
        self.base_city = base_city
        self.trips: List[Dict] = []

    def process(self, invoices: List[Dict]) -> List[Dict]:
        """
        处理发票，识别出差行程

        Args:
            invoices: 发票列表

        Returns:
            List[Dict]: 识别出的出差行程列表
        """
        self.trips = []

        # 筛选交通票据（机票、高铁）
        transport_invoices = [
            inv for inv in invoices
            if inv.get('type') in ['flight', 'train'] and inv.get('date')
        ]

        # 按日期排序
        transport_invoices.sort(key=lambda x: x.get('date', ''))

        # 识别出差行程
        current_trip = None

        for invoice in transport_invoices:
            departure = invoice.get('departure', '')
            arrival = invoice.get('arrival', '')
            date = invoice.get('date', '')
            inv_type = invoice.get('type', '')

            # 检查是否是从基准城市出发的去程
            is_outbound = (departure == self.base_city and
                          arrival != self.base_city and
                          not current_trip)

            # 检查是否是返回基准城市的返程
            is_return = (arrival == self.base_city and
                        departure != self.base_city and
                        current_trip)

            if is_outbound:
                # 开始新行程
                current_trip = {
                    'trip_id': len(self.trips) + 1,
                    'start_date': date,
                    'end_date': None,
                    'departure_city': departure,
                    'arrival_city': arrival,
                    'outbound': [invoice],
                    'return': [],
                    'accommodations': [],
                    'insurance': [],
                    'meals': [],
                    'other': [],
                    'total_amount': 0.0,
                    'missing_items': []
                }
                logger.info(f"识别新行程 #{current_trip['trip_id']}: {date} {departure} -> {arrival}")

            elif is_return and current_trip:
                # 完成当前行程
                current_trip['return'].append(invoice)
                current_trip['end_date'] = date
                current_trip['arrival_city'] = arrival

                # 计算行程天数
                days = self._calculate_days(
                    current_trip['start_date'],
                    current_trip['end_date']
                )
                current_trip['days'] = days

                # 收集行程中的其他票据
                self._collect_trip_invoices(current_trip, invoices)

                # 计算总金额
                self._calculate_trip_total(current_trip)

                # 检查缺失票据
                self._check_missing_items(current_trip)

                self.trips.append(current_trip)
                logger.info(f"行程 #{current_trip['trip_id']} 完成: "
                           f"{current_trip['start_date']} - {current_trip['end_date']}, "
                           f"总金额: {current_trip['total_amount']:.2f}")

                current_trip = None

            elif current_trip:
                # 行程中的票据（可能是同城市交通）
                pass

        # 处理未完成的行程（只有去程没有返程）
        if current_trip:
            current_trip['days'] = 1
            current_trip['end_date'] = current_trip['start_date']
            self._collect_trip_invoices(current_trip, invoices)
            self._calculate_trip_total(current_trip)
            self._check_missing_items(current_trip)
            current_trip['missing_items'].append("缺少返程票据")
            self.trips.append(current_trip)

        # 关联非交通票据（住宿、餐饮等）到行程
        self._associate_invoices_to_trips()

        return self.trips

    def _collect_trip_invoices(self, trip: Dict, all_invoices: List[Dict]):
        """
        收集行程中的其他票据

        Args:
            trip: 行程信息
            all_invoices: 所有发票
        """
        if not trip.get('start_date') or not trip.get('end_date'):
            return

        start = datetime.strptime(trip['start_date'][:10], '%Y-%m-%d')
        end = datetime.strptime(trip['end_date'][:10], '%Y-%m-%d')

        for invoice in all_invoices:
            if invoice.get('type') in ['flight', 'train']:
                continue

            inv_date_str = invoice.get('date', '')
            if not inv_date_str:
                continue

            try:
                inv_date = datetime.strptime(inv_date_str[:10], '%Y-%m-%d')

                # 检查日期是否在行程范围内
                if start <= inv_date <= end + timedelta(days=1):
                    inv_type = invoice.get('type', '')

                    if inv_type == 'hotel':
                        trip['accommodations'].append(invoice)
                    elif inv_type == 'insurance':
                        trip['insurance'].append(invoice)
                    elif inv_type == 'meal':
                        trip['meals'].append(invoice)
                    else:
                        trip['other'].append(invoice)
            except ValueError:
                continue

    def _calculate_trip_total(self, trip: Dict):
        """计算行程总金额"""
        total = 0.0

        # 去程交通
        for inv in trip.get('outbound', []):
            total += float(inv.get('amount', 0))

        # 返程交通
        for inv in trip.get('return', []):
            total += float(inv.get('amount', 0))

        # 住宿
        for inv in trip.get('accommodations', []):
            total += float(inv.get('amount', 0))

        # 保险
        for inv in trip.get('insurance', []):
            total += float(inv.get('amount', 0))

        # 餐饮
        for inv in trip.get('meals', []):
            total += float(inv.get('amount', 0))

        # 其他
        for inv in trip.get('other', []):
            total += float(inv.get('amount', 0))

        trip['total_amount'] = total

    def _check_missing_items(self, trip: Dict):
        """检查缺失的票据"""
        missing = []

        # 检查去程
        if not trip.get('outbound'):
            missing.append("缺少去程交通票据")

        # 检查返程
        if not trip.get('return'):
            missing.append("缺少返程交通票据")

        # 检查住宿（如果行程超过1天）
        days = trip.get('days', 1)
        if days > 1 and not trip.get('accommodations'):
            missing.append(f"缺少住宿发票（出差{days}天）")

        trip['missing_items'] = missing

    def _calculate_days(self, start_date: str, end_date: str) -> int:
        """计算天数"""
        try:
            start = datetime.strptime(start_date[:10], '%Y-%m-%d')
            end = datetime.strptime(end_date[:10], '%Y-%m-%d')
            return (end - start).days + 1
        except ValueError:
            return 1

    def _associate_invoices_to_trips(self):
        """将未关联的发票关联到相应行程"""
        pass

    def get_travel_summary(self) -> Dict[str, Any]:
        """
        获取出差统计摘要

        Returns:
            Dict: 统计信息
        """
        summary = {
            'total_trips': len(self.trips),
            'total_amount': sum(trip.get('total_amount', 0) for trip in self.trips),
            'total_days': sum(trip.get('days', 0) for trip in self.trips),
            'trips_with_missing': sum(1 for trip in self.trips if trip.get('missing_items')),
            'missing_count': sum(len(trip.get('missing_items', [])) for trip in self.trips)
        }
        return summary
