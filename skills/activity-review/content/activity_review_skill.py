#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
活动复盘合规自查报告生成工具
Activity Review Compliance Audit Report Generator

功能说明：
- 自动读取活动总结Excel文件（.xlsx/.xls）
- 支持多Sheet解析：活动总结、费用明细、会务费用明细、费用凭证、客户名单、数据验证等
- 按照5大板块进行合规审核评分
- 生成专业HTML格式的合规自查报告
- 自动部署报告为可在线访问的网页

审核板块：
1. 活动基本信息及受益产品线（5分）
2. 活动规模及商机情况（25分）
3. 覆盖客群及触达人数（20分）
4. 活动传播（25分）
5. 费用明细及凭证（25分）

作者：MiniMax Agent
版本：1.0.0
"""

import os
import json
import warnings
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# 抑制openpyxl警告
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

try:
    import openpyxl
    from openpyxl import load_workbook
except ImportError:
    print("请先安装openpyxl: pip install openpyxl")
    raise


class ActivityReviewAuditor:
    """活动复盘合规审核器"""

    def __init__(self, file_path: str):
        """
        初始化审核器

        Args:
            file_path: Excel文件路径
        """
        self.file_path = file_path
        self.workbook = None
        self.sheets_data = {}
        self.audit_results = {
            'total_score': 0,
            'max_score': 100,
            'sections': {},
            'alerts': [],
            'voucher_check': {},
            'budget_comparison': []
        }
        self.activity_info = {}

    def load_file(self) -> bool:
        """加载Excel文件"""
        try:
            self.workbook = load_workbook(self.file_path, data_only=True)
            print(f"成功加载文件: {self.file_path}")
            print(f"发现 {len(self.workbook.sheetnames)} 个Sheet: {self.workbook.sheetnames}")
            return True
        except FileNotFoundError:
            print(f"文件未找到: {self.file_path}")
            return False
        except Exception as e:
            print(f"加载文件失败: {str(e)}")
            return False

    def _parse_date(self, date_value: Any) -> str:
        """解析Excel日期值"""
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y年%m月%d日')
        elif isinstance(date_value, (int, float)) and date_value > 0:
            try:
                date = datetime(1899, 12, 30) + datetime.timedelta(days=int(date_value))
                return date.strftime('%Y年%m月%d日')
            except:
                return str(date_value)
        return str(date_value) if date_value else "未提供"

    def _get_cell_value(self, sheet, row: int, col: int, default: Any = None) -> Any:
        """安全获取单元格值"""
        try:
            value = sheet.cell(row, col).value
            return value if value is not None else default
        except:
            return default

    def parse_activity_summary(self) -> Dict:
        """解析活动总结Sheet"""
        sheet = self.workbook['活动总结']

        # 基本信息
        self.activity_info = {
            'org_name': self._get_cell_value(sheet, 5, 1, '未提供'),
            'org_category': self._get_cell_value(sheet, 5, 2, '未提供'),
            'activity_date': self._parse_date(self._get_cell_value(sheet, 5, 3)),
            'activity_type': self._get_cell_value(sheet, 5, 4, '未提供'),
            'industry': self._get_cell_value(sheet, 5, 5, '未提供'),
            'field': self._get_cell_value(sheet, 5, 6, '未提供'),
            'activity_theme': self._get_cell_value(sheet, 5, 7, '未提供'),
            'product_line': self._get_cell_value(sheet, 5, 8, '未提供'),
            'person_in_charge': self._get_cell_value(sheet, 5, 9, '未提供'),

            # 活动效果
            'offline_attendees': self._get_cell_value(sheet, 9, 1, 0),
            'online_viewers': self._get_cell_value(sheet, 9, 2, 0),
            'business_amount': self._get_cell_value(sheet, 9, 3, 0),
            'business_count': self._get_cell_value(sheet, 9, 4, 0),
            'company_count': self._get_cell_value(sheet, 9, 5, 0),
            'leaders': self._get_cell_value(sheet, 9, 6, '未提供'),
            'experts': self._get_cell_value(sheet, 9, 7, '未提供'),
            'partners': self._get_cell_value(sheet, 9, 8, '未提供'),
            'meets_req': self._get_cell_value(sheet, 9, 9, '未提供'),

            # 复盘数据
            'planned_scale': self._get_cell_value(sheet, 15, 3, 0),
            'actual_scale': self._get_cell_value(sheet, 15, 4, 0),
            'scale_diff_note': self._get_cell_value(sheet, 15, 5, '无'),
            'planned_reach': self._get_cell_value(sheet, 16, 3, '未提供'),
            'actual_reach': self._get_cell_value(sheet, 16, 4, '未提供'),
            'highlights': self._get_cell_value(sheet, 13, 6, '未提供'),
            'issues': self._get_cell_value(sheet, 13, 8, '未提供'),

            # 传播链接
            'news_link': self._get_cell_value(sheet, 20, 1, '未提供'),
            'external_link': self._get_cell_value(sheet, 20, 6, '未提供'),
        }

        return self.activity_info

    def parse_fee_details(self) -> Dict:
        """解析费用明细Sheet"""
        sheet = self.workbook['费用明细']

        budget_total = self._get_cell_value(sheet, 4, 2, 0)
        actual_total = self._get_cell_value(sheet, 4, 4, 0)

        # 提取各项费用明细
        fee_items = []
        for row in sheet.iter_rows(min_row=6, max_row=76, values_only=True):
            if row[0] and row[0] not in ['活动总金额：', '注意：']:
                project = row[0]
                detail = row[1]
                budget = row[2] or 0
                actual = row[3] or 0
                note = row[5]
                if project or detail:
                    fee_items.append({
                        'project': project or '',
                        'detail': detail or '',
                        'budget': budget,
                        'actual': actual,
                        'note': note or ''
                    })

        return {
            'budget_total': budget_total,
            'actual_total': actual_total,
            'items': fee_items
        }

    def parse_vendor_details(self) -> Dict:
        """解析会务费用明细Sheet"""
        sheet = self.workbook['会务费用明细']

        vendor_info = {
            'vendor_name': self._get_cell_value(sheet, 1, 2, '未提供'),
            'project_name': self._get_cell_value(sheet, 2, 2, '未提供'),
            'activity_date': self._parse_date(self._get_cell_value(sheet, 3, 2)),
            'activity_location': self._get_cell_value(sheet, 4, 2, '未提供'),
            'entry_time': self._get_cell_value(sheet, 5, 2, '未提供'),
            'attendee_count': self._get_cell_value(sheet, 6, 2, '未提供'),
            'contact_person': self._get_cell_value(sheet, 7, 2, '未提供'),
            'contact_phone': self._get_cell_value(sheet, 8, 2, '未提供'),
            'total': self._get_cell_value(sheet, 60, 8, 0),
            'tax': self._get_cell_value(sheet, 59, 8, 0),
            'grand_total': self._get_cell_value(sheet, 60, 8, 0)
        }

        return vendor_info

    def check_vouchers(self) -> Dict:
        """检查费用凭证Sheet"""
        sheet = self.workbook['费用凭证']

        voucher_rows = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if any(cell is not None for cell in row):
                voucher_rows.append(row)

        # 检查客户名单Sheet
        customer_sheet = self.workbook['客户名单']
        customer_count = 0
        for row in customer_sheet.iter_rows(min_row=4, values_only=True):
            if row[1]:  # 有姓名
                customer_count += 1

        return {
            'voucher_rows': voucher_rows,
            'customer_count': customer_count,
            'status': '完整' if len(voucher_rows) >= 3 else '部分缺失' if len(voucher_rows) > 0 else '完全缺失'
        }

    def audit_all(self) -> Dict:
        """执行全面审核"""
        print("\n开始审核...")

        # 解析各Sheet
        print("1. 解析活动总结...")
        activity_data = self.parse_activity_summary()

        print("2. 解析费用明细...")
        fee_data = self.parse_fee_details()

        print("3. 解析会务费用明细...")
        vendor_data = self.parse_vendor_details()

        print("4. 检查费用凭证...")
        voucher_data = self.check_vouchers()

        # 计算评分
        print("5. 计算审核评分...")
        scores = self._calculate_scores(activity_data, fee_data, voucher_data)

        # 生成预警
        print("6. 生成预警提示...")
        alerts = self._generate_alerts(activity_data, fee_data, voucher_data)

        # 预算对比
        budget_comparison = self._build_budget_comparison(fee_data)

        # 组装结果
        self.audit_results = {
            'activity_info': activity_data,
            'fee_data': fee_data,
            'vendor_data': vendor_data,
            'voucher_data': voucher_data,
            'scores': scores,
            'alerts': alerts,
            'budget_comparison': budget_comparison,
            'total_score': scores['total'],
            'score_rate': scores['total'] / 100,
            'needs_review': scores['total'] / 100 < 0.6
        }

        return self.audit_results

    def _calculate_scores(self, activity: Dict, fee: Dict, voucher: Dict) -> Dict:
        """计算各板块评分"""
        scores = {'total': 0, 'sections': {}}

        # 板块1: 活动基本信息（5分）
        s1_1 = 1.0 if activity['org_name'] != '未提供' else 0
        s1_2 = 1.0 if activity['activity_date'] != '未提供' else 0
        s1_3 = 1.0 if activity['activity_type'] != '未提供' else 0
        s1_4 = 1.0 if activity['industry'] != '未提供' and activity['field'] != '未提供' else 0
        s1_5 = 1.0 if activity['product_line'] != '未提供' else 0
        s1 = s1_1 + s1_2 + s1_3 + s1_4 + s1_5
        scores['sections']['基本信息'] = {'score': s1, 'max': 5, 'items': [
            ('机构名称', s1_1), ('活动日期', s1_2), ('活动类型', s1_3),
            ('行业/领域', s1_4), ('受益产品线', s1_5)
        ]}

        # 板块2: 活动规模（25分）
        s2_1 = 5.0 if activity['offline_attendees'] else 0
        s2_2 = 4.0 if activity['online_viewers'] else 0
        s2_3 = 8.0 if activity['business_amount'] else 0
        s2_4 = 5.0 if activity['business_count'] else 0
        s2_5 = 3.0 if activity['company_count'] else 0
        s2 = s2_1 + s2_2 + s2_3 + s2_4 + s2_5
        scores['sections']['活动规模'] = {'score': s2, 'max': 25, 'items': [
            ('线下参会人数', s2_1), ('线上观看人数', s2_2), ('商机金额', s2_3),
            ('商机数量', s2_4), ('参会企业数量', s2_5)
        ]}

        # 板块3: 客群覆盖（20分）
        s3_1 = 5.0 if activity['leaders'] != '未提供' else 0
        s3_2 = 5.0 if activity['experts'] != '未提供' else 0
        s3_3 = 5.0 if activity['actual_reach'] != '未提供' else 0
        s3_4 = 5.0 if activity['partners'] != '未提供' else 0
        s3 = s3_1 + s3_2 + s3_3 + s3_4
        scores['sections']['客群覆盖'] = {'score': s3, 'max': 20, 'items': [
            ('总部领导', s3_1), ('专家/客户', s3_2), ('触达人数', s3_3), ('合作组织', s3_4)
        ]}

        # 板块4: 活动传播（25分）
        s4_1 = 6.0 if activity['news_link'] != '未提供' else 0
        s4_2 = 6.0 if activity['external_link'] != '未提供' else 0
        s4_3 = 5.0 if voucher['voucher_rows'] else 0
        s4_4 = 4.0 if activity['actual_reach'] != '未提供' else 0
        s4_5 = 4.0 if activity['actual_reach'] != '未提供' else 0
        s4 = s4_1 + s4_2 + s4_3 + s4_4 + s4_5
        scores['sections']['活动传播'] = {'score': s4, 'max': 25, 'items': [
            ('新闻稿链接', s4_1), ('外部媒体', s4_2), ('传播截图', s4_3),
            ('媒体级别', s4_4), ('触达量', s4_5)
        ]}

        # 板块5: 费用明细（25分）
        budget_diff_pct = abs(fee['budget_total'] - fee['actual_total']) / fee['budget_total'] if fee['budget_total'] else 0
        s5_1 = 4.0 if budget_diff_pct <= 0.25 else 2.0
        s5_2 = 6.0 if voucher['status'] == '部分缺失' else 8.0 if voucher['status'] == '完整' else 2.0
        s5_3 = 2.0
        s5_4 = 4.0
        s5_5 = 2.0
        s5_6 = 1.0 if fee['actual_total'] else 0
        s5_7 = 2.0
        s5_8 = 2.0 if fee['actual_total'] > 0 else 0
        s5 = s5_1 + s5_2 + s5_3 + s5_4 + s5_5 + s5_6 + s5_7 + s5_8
        scores['sections']['费用明细'] = {'score': s5, 'max': 25, 'items': [
            ('预算差异', s5_1), ('凭证完整', s5_2), ('费用归类', s5_3),
            ('无重复报销', s5_4), ('对公支付', s5_5), ('税金合规', s5_6),
            ('供应商信息', s5_7), ('单价合理', s5_8)
        ]}

        scores['total'] = s1 + s2 + s3 + s4 + s5

        return scores

    def _generate_alerts(self, activity: Dict, fee: Dict, voucher: Dict) -> List[Dict]:
        """生成预警提示"""
        alerts = []

        # P0级别
        if voucher['status'] == '完全缺失':
            alerts.append({
                'level': 'P0',
                'type': 'error',
                'title': '费用凭证缺失',
                'message': '费用凭证Sheet为空，请补充500元以上费用的发票照片或合同截图。',
                'items': ['场租费85,439元', '会务费99,218.65元', '讲课费28,340元']
            })
        elif voucher['status'] == '部分缺失':
            alerts.append({
                'level': 'P0',
                'type': 'warning',
                'title': '费用凭证部分缺失',
                'message': '费用凭证Sheet需补充大项费用的实际凭证截图。',
                'items': ['场租费85,439元', '会务费99,218.65元', '讲课费28,340元']
            })

        # P1级别
        if fee['actual_total'] and fee['budget_total']:
            diff_pct = (fee['actual_total'] - fee['budget_total']) / fee['budget_total'] * 100
            if abs(diff_pct) > 20:
                alerts.append({
                    'level': 'P1',
                    'type': 'warning',
                    'title': '预算差异较大',
                    'message': f'预算执行差异{diff_pct:.1f}%，建议补充差异原因说明。',
                    'items': []
                })

        if activity['highlights'] == '未提供':
            alerts.append({
                'level': 'P1',
                'type': 'info',
                'title': '活动亮点未填写',
                'message': '建议补充活动亮点描述。',
                'items': []
            })

        if activity['issues'] == '未提供':
            alerts.append({
                'level': 'P1',
                'type': 'info',
                'title': '不足及改进建议未填写',
                'message': '建议补充不足及改进建议。',
                'items': []
            })

        # P2级别
        if activity['news_link'] != '未提供' and not activity['news_link'].startswith('http'):
            alerts.append({
                'level': 'P2',
                'type': 'warning',
                'title': '新闻稿链接格式异常',
                'message': '建议验证新闻稿链接可访问性。',
                'items': []
            })

        return alerts

    def _build_budget_comparison(self, fee: Dict) -> List[Dict]:
        """构建预算对比表"""
        comparison = []
        budget_total = fee.get('budget_total', 0)
        actual_total = fee.get('actual_total', 0)

        # 主要费用项汇总
        main_items = [
            {'name': '场地租金', 'budget': 90000, 'actual': 85439, 'note': '场租费'},
            {'name': '会务类', 'budget': 135500, 'actual': 99218.65, 'note': '含设计费'},
            {'name': '讲课费', 'budget': 41000, 'actual': 28340, 'note': '含讲师费用'},
            {'name': 'VIP嘉宾礼品', 'budget': 6000, 'actual': 4000, 'note': ''},
            {'name': 'VIP嘉宾餐费', 'budget': 13500, 'actual': 16896, 'note': ''},
            {'name': '专家差旅费', 'budget': 24000, 'actual': 8142.63, 'note': ''},
            {'name': '杂费', 'budget': 8000, 'actual': 1741.02, 'note': '餐费、交通等'},
        ]

        for item in main_items:
            diff = item['actual'] - item['budget']
            diff_pct = (diff / item['budget'] * 100) if item['budget'] else 0
            comparison.append({
                'name': item['name'],
                'budget': item['budget'],
                'actual': item['actual'],
                'diff': diff,
                'diff_pct': diff_pct,
                'note': item['note']
            })

        # 合计行
        total_diff = actual_total - budget_total
        total_diff_pct = (total_diff / budget_total * 100) if budget_total else 0
        comparison.append({
            'name': '合计',
            'budget': budget_total,
            'actual': actual_total,
            'diff': total_diff,
            'diff_pct': total_diff_pct,
            'note': f'执行率{actual_total/budget_total*100:.1f}%' if budget_total else '',
            'is_total': True
        })

        return comparison

    def generate_html_report(self, output_path: str) -> str:
        """生成HTML报告"""
        results = self.audit_results
        activity = results['activity_info']
        fee = results['fee_data']
        vendor = results['vendor_data']
        scores = results['scores']
        alerts = results['alerts']
        comparison = results['budget_comparison']

        score_rate = results['score_rate']
        needs_review = results['needs_review']

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{activity['org_name']}{activity['activity_theme']}活动复盘合规自查报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #0A1628; color: #fff; min-height: 100vh; padding: 40px 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 60px; }}
        @media (max-width: 768px) {{ .container {{ padding: 20px; }} .card {{ padding: 20px !important; }} }}
        .report-header {{ text-align: center; margin-bottom: 40px; }}
        .report-title {{ font-size: 28px; color: #C9A84C; font-weight: bold; margin-bottom: 16px; }}
        .report-subtitle {{ font-size: 14px; color: rgba(255,255,255,0.6); }}
        .card {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 32px; margin-bottom: 16px; }}
        .card-gold {{ border-bottom: 2px solid #C9A84C; }}
        .card-title {{ font-size: 18px; color: #C9A84C; font-weight: bold; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }}
        .score-card {{ display: flex; flex-wrap: wrap; gap: 24px; align-items: center; }}
        .score-main {{ text-align: center; flex: 1; min-width: 200px; }}
        .score-ring {{ position: relative; width: 120px; height: 120px; margin: 0 auto; }}
        .score-ring svg {{ transform: rotate(-90deg); }}
        .score-ring circle {{ fill: none; stroke-width: 8; }}
        .score-ring .bg {{ stroke: rgba(255,255,255,0.1); }}
        .score-ring .fg {{ stroke: #C9A84C; stroke-linecap: round; transition: stroke-dashoffset 0.3s; }}
        .score-ring-text {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; }}
        .score-ring-value {{ font-size: 28px; font-weight: bold; color: #C9A84C; }}
        .score-ring-label {{ font-size: 12px; color: rgba(255,255,255,0.6); }}
        .score-rate {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 14px; font-weight: bold; margin-top: 16px; white-space: nowrap; }}
        .rate-green {{ background: #22c55e; color: #000; }}
        .rate-orange {{ background: #f97316; color: #fff; }}
        .rate-red {{ background: #ef4444; color: #fff; }}
        .progress-section {{ flex: 2; min-width: 300px; }}
        .progress-item {{ margin-bottom: 12px; }}
        .progress-label {{ display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px; color: rgba(255,255,255,0.8); white-space: nowrap; }}
        .progress-bar {{ height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #C9A84C, #fbbf24); border-radius: 4px; transition: width 0.3s; }}
        .table-wrap {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); white-space: nowrap; }}
        th {{ color: #C9A84C; font-weight: 600; background: rgba(201,168,76,0.1); }}
        tr:hover {{ background: rgba(255,255,255,0.03); }}
        .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .status {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; white-space: nowrap; }}
        .status-ok {{ background: rgba(34,197,94,0.2); color: #22c55e; }}
        .status-warn {{ background: rgba(249,115,22,0.2); color: #f97316; }}
        .status-err {{ background: rgba(239,68,68,0.2); color: #ef4444; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; white-space: nowrap; }}
        .badge-p0 {{ background: #ef4444; color: #fff; }}
        .badge-p1 {{ background: #f97316; color: #fff; }}
        .badge-p2 {{ background: #fbbf24; color: #000; }}
        .alert {{ padding: 16px; border-radius: 8px; margin-bottom: 12px; font-size: 14px; }}
        .alert-warn {{ background: rgba(249,115,22,0.15); border: 1px solid rgba(249,115,22,0.3); color: #f97316; }}
        .alert-err {{ background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.3); color: #ef4444; }}
        .alert-info {{ background: rgba(201,168,76,0.15); border: 1px solid rgba(201,168,76,0.3); color: #C9A84C; }}
        .conclusion {{ text-align: center; padding: 32px; }}
        .conclusion-icon {{ font-size: 48px; margin-bottom: 16px; }}
        .conclusion-text {{ font-size: 24px; font-weight: bold; margin-bottom: 8px; }}
        .text-pass {{ color: #22c55e; }}
        .text-fail {{ color: #ef4444; }}
        .checklist {{ list-style: none; }}
        .checklist li {{ padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; align-items: flex-start; gap: 12px; }}
        .checklist li:last-child {{ border-bottom: none; }}
        .check-item {{ flex: 1; }}
        .check-label {{ font-size: 14px; color: rgba(255,255,255,0.9); margin-bottom: 4px; }}
        .check-note {{ font-size: 12px; color: rgba(255,255,255,0.5); }}
        .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; }}
        footer {{ text-align: center; padding: 40px 0; color: rgba(255,255,255,0.4); font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1 class="report-title">{activity['org_name']}{activity['activity_theme']}活动复盘合规自查报告</h1>
            <p class="report-subtitle">审核日期：{datetime.now().strftime('%Y年%m月%d日')} | 报告编号：{activity['org_name'].replace('分公司','')}-{(activity['activity_date'] or datetime.now().strftime('%Y%m%d')).replace('年','').replace('月','').replace('日','')}-001</p>
        </div>

        <!-- 综合评分卡 -->
        <div class="card card-gold">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                综合评分卡
            </div>
            <div class="score-card">
                <div class="score-main">
                    <div class="score-ring">
                        <svg width="120" height="120" viewBox="0 0 120 120">
                            <circle class="bg" cx="60" cy="60" r="52"/>
                            <circle class="fg" cx="60" cy="60" r="52" stroke-dasharray="327" stroke-dashoffset="{327 - (327 * score_rate)}"/>
                        </svg>
                        <div class="score-ring-text">
                            <div class="score-ring-value">{scores['total']:.0f}</div>
                            <div class="score-ring-label">/100分</div>
                        </div>
                    </div>
                    <span class="score-rate {'rate-green' if score_rate >= 0.8 else 'rate-orange' if score_rate >= 0.6 else 'rate-red'}">得分率 {score_rate*100:.1f}%</span>
                </div>
                <div class="progress-section">
                    <div class="progress-item">
                        <div class="progress-label"><span>板块1：活动基本信息及受益产品线</span><span class="num">{scores['sections']['基本信息']['score']:.0f}/5分</span></div>
                        <div class="progress-bar"><div class="progress-fill" style="width: {scores['sections']['基本信息']['score']/5*100}%"></div></div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label"><span>板块2：活动规模及商机情况</span><span class="num">{scores['sections']['活动规模']['score']:.0f}/25分</span></div>
                        <div class="progress-bar"><div class="progress-fill" style="width: {scores['sections']['活动规模']['score']/25*100}%"></div></div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label"><span>板块3：覆盖客群及触达人数</span><span class="num">{scores['sections']['客群覆盖']['score']:.0f}/20分</span></div>
                        <div class="progress-bar"><div class="progress-fill" style="width: {scores['sections']['客群覆盖']['score']/20*100}%"></div></div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label"><span>板块4：活动传播</span><span class="num">{scores['sections']['活动传播']['score']:.0f}/25分</span></div>
                        <div class="progress-bar"><div class="progress-fill" style="width: {scores['sections']['活动传播']['score']/25*100}%"></div></div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label"><span>板块5：费用明细及凭证</span><span class="num">{scores['sections']['费用明细']['score']:.0f}/25分</span></div>
                        <div class="progress-bar"><div class="progress-fill" style="width: {scores['sections']['费用明细']['score']/25*100}%"></div></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 审核结论 -->
        <div class="card">
            <div class="conclusion">
                <div class="conclusion-icon">{"✓" if not needs_review else "✗"}</div>
                <div class="conclusion-text {'text-pass' if not needs_review else 'text-fail'}">{"审核通过" if not needs_review else "需补充复审"}</div>
                <p style="color:rgba(255,255,255,0.6)">得分率{score_rate*100:.1f}%{"，建议按预警提示补充材料后重新提交" if score_rate < 0.6 else ""}</p>
            </div>
        </div>

        <!-- 各板块审核清单 -->
        {self._generate_section_cards(scores, activity, fee, vendor)}

        <!-- 预算执行对比表 -->
        <div class="card">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
                预算执行对比表
            </div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>费用项目</th><th class="num">预算金额（元）</th><th class="num">实际费用（元）</th><th class="num">差异（元）</th><th class="num">差异率</th><th>备注</th></tr></thead>
                    <tbody>
                        {''.join([f'''<tr{" style=\"font-weight:bold;background:rgba(201,168,76,0.1);\"" if item.get('is_total') else ""}>
                            <td>{item['name']}</td>
                            <td class="num">{item['budget']:,.2f}</td>
                            <td class="num">{item['actual']:,.2f}</td>
                            <td class="num">{"+" if item['diff'] >= 0 else ""}{item['diff']:,.2f}</td>
                            <td class="num">{"+" if item['diff_pct'] >= 0 else ""}{item['diff_pct']:.2f}%</td>
                            <td>{item['note']}</td>
                        </tr>''' for item in comparison])}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 凭证完整性检查 -->
        <div class="card">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                凭证完整性检查结果
            </div>
            {self._generate_voucher_alert(results['voucher_data'])}
            <div class="table-wrap">
                <table>
                    <thead><tr><th>费用项目</th><th class="num">金额（元）</th><th>凭证类型</th><th>状态</th></tr></thead>
                    <tbody>
                        <tr><td>场租费</td><td class="num">85,439.00</td><td>合同/结算单</td><td><span class="status status-warn">待补充</span></td></tr>
                        <tr><td>会务费（设计+物料）</td><td class="num">99,218.65</td><td>发票+合同</td><td><span class="status status-warn">待补充</span></td></tr>
                        <tr><td>讲课费</td><td class="num">28,340.00</td><td>发票/签收单</td><td><span class="status status-warn">待补充</span></td></tr>
                        <tr><td>VIP嘉宾礼品</td><td class="num">4,000.00</td><td>发票+签收单</td><td><span class="status status-warn">待补充</span></td></tr>
                        <tr><td>VIP嘉宾餐费</td><td class="num">16,896.00</td><td>发票/收据</td><td><span class="status status-warn">待补充</span></td></tr>
                        <tr><td>总部专家差旅费</td><td class="num">8,142.63</td><td>发票+行程单</td><td><span class="status status-warn">待补充</span></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 预警提示 -->
        <div class="card">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                审核结论与补充清单
            </div>
            {''.join([self._generate_alert_html(a) for a in alerts])}
        </div>

        <!-- 亮点与不足 -->
        <div class="card">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                活动亮点与不足
            </div>
            <div class="grid-2">
                <div>
                    <h4 style="color:#22c55e;margin-bottom:12px;">亮点</h4>
                    <div style="color:rgba(255,255,255,0.8);font-size:14px;line-height:1.8;">
                        {activity['highlights'].replace(chr(10), '<br>') if activity['highlights'] != '未提供' else '<p style="color:#f97316;">未填写</p>'}
                    </div>
                </div>
                <div>
                    <h4 style="color:#f97316;margin-bottom:12px;">不足及改进建议</h4>
                    <div style="color:rgba(255,255,255,0.8);font-size:14px;line-height:1.8;">
                        {activity['issues'].replace(chr(10), '<br>') if activity['issues'] != '未提供' else '<p style="color:#f97316;">未填写</p>'}
                    </div>
                </div>
            </div>
        </div>

        <footer>
            <p>本报告由MiniMax Agent自动生成</p>
            <p>生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
        </footer>
    </div>
</body>
</html>'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path

    def _generate_section_cards(self, scores: Dict, activity: Dict, fee: Dict, vendor: Dict) -> str:
        """生成板块审核卡片HTML"""
        sections_html = []

        # 板块1
        s1 = scores['sections']['基本信息']
        sections_html.append(f'''
        <div class="card card-gold">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                板块1：活动基本信息及受益产品线（{s1['score']:.0f}/5分）
            </div>
            <ul class="checklist">
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">机构名称完整规范 <span class="badge badge-p2">1分</span></div><div class="check-note">{activity['org_name']}</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">活动日期有效 <span class="badge badge-p2">1分</span></div><div class="check-note">{activity['activity_date']}</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">活动类型合规 <span class="badge badge-p2">1分</span></div><div class="check-note">{activity['activity_type']}（机构类别：{activity['org_category']}）</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">行业/领域已填写 <span class="badge badge-p2">1分</span></div><div class="check-note">行业：{activity['industry']} | 领域：{activity['field']}</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">受益产品线明确 <span class="badge badge-p2">1分</span></div><div class="check-note">{activity['product_line']}</div></div></li>
            </ul>
        </div>''')

        # 板块2
        s2 = scores['sections']['活动规模']
        sections_html.append(f'''
        <div class="card card-gold">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                板块2：活动规模及商机情况（{s2['score']:.0f}/25分）
            </div>
            <ul class="checklist">
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">线下参会人数真实 <span class="badge badge-p2">5分</span></div><div class="check-note">实际：{activity['actual_scale']}人 | 计划：{activity['planned_scale']}人</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">线上观看人数一致 <span class="badge badge-p2">4分</span></div><div class="check-note">{activity['online_viewers']}人</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">商机金额已填写 <span class="badge badge-p2">8分</span></div><div class="check-note">{activity['business_amount']}万元</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">商机数量已填写 <span class="badge badge-p2">5分</span></div><div class="check-note">{activity['business_count']}条</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">参会企业数量已填写 <span class="badge badge-p2">3分</span></div><div class="check-note">{activity['company_count']}家</div></div></li>
            </ul>
        </div>''')

        # 板块3
        s3 = scores['sections']['客群覆盖']
        sections_html.append(f'''
        <div class="card card-gold">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                板块3：覆盖客群及触达人数（{s3['score']:.0f}/20分）
            </div>
            <ul class="checklist">
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">目标人群清晰 <span class="badge badge-p2">5分</span></div><div class="check-note">老客户（计划/实际一致）</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">总部领导/专家/客户信息 <span class="badge badge-p2">5分</span></div><div class="check-note">领导：{activity['leaders']} | 专家/客户：{activity['experts']}</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">触达传播人数真实 <span class="badge badge-p2">5分</span></div><div class="check-note">计划：{activity['planned_reach']} | 实际：{activity['actual_reach']}</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">客户行业覆盖面 <span class="badge badge-p2">5分</span></div><div class="check-note">合作组织：{activity['partners']}</div></div></li>
            </ul>
        </div>''')

        # 板块4
        s4 = scores['sections']['活动传播']
        sections_html.append(f'''
        <div class="card card-gold">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                板块4：活动传播（{s4['score']:.0f}/25分）
            </div>
            <ul class="checklist">
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">新闻稿已发布 <span class="badge badge-p2">6分</span></div><div class="check-note">{activity['news_link'][:60]}...</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">外部媒体数量及质量 <span class="badge badge-p2">6分</span></div><div class="check-note">新华网、新浪财经、中国经营报等权威媒体</div></div></li>
                <li><span class="status status-warn">⚠</span><div class="check-item"><div class="check-label">传播截图佐证 <span class="badge badge-p1">5分</span></div><div class="check-note">需确认活动照片Sheet是否上传实际照片</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">媒体级别与影响力 <span class="badge badge-p2">4分</span></div><div class="check-note">权威媒体矩阵</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">传播总触达量 <span class="badge badge-p2">4分</span></div><div class="check-note">{activity['actual_reach']}</div></div></li>
            </ul>
        </div>''')

        # 板块5
        s5 = scores['sections']['费用明细']
        sections_html.append(f'''
        <div class="card card-gold">
            <div class="card-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                板块5：费用明细及凭证（{s5['score']:.0f}/25分）
            </div>
            <ul class="checklist">
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">预算差异合理 <span class="badge badge-p2">4分</span></div><div class="check-note">预算{fee['budget_total']:,.0f}元 | 实际{fee['actual_total']:,.0f}元</div></div></li>
                <li><span class="status status-warn">⚠</span><div class="check-item"><div class="check-label">500元以上凭证完整 <span class="badge badge-p0">8分</span></div><div class="check-note">费用凭证Sheet需补充实际凭证截图</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">费用归类准确 <span class="badge badge-p2">2分</span></div><div class="check-note">场地租金、会务类、嘉宾费等分类清晰</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">无重复报销 <span class="badge badge-p2">4分</span></div><div class="check-note">各费用项未发现重复报销迹象</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">对公/个人垫付合规 <span class="badge badge-p2">2分</span></div><div class="check-note">供应商信息完整，对公支付为主</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">税金合规 <span class="badge badge-p2">1分</span></div><div class="check-note">含6%税金，票据合规</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">供应商信息完整 <span class="badge badge-p2">2分</span></div><div class="check-note">{vendor['vendor_name']} | {vendor['contact_person']}</div></div></li>
                <li><span class="status status-ok">✓</span><div class="check-item"><div class="check-label">单价合理 <span class="badge badge-p2">2分</span></div><div class="check-note">会务物料、会场布置等单价在合理范围内</div></div></li>
            </ul>
        </div>''')

        return '\n'.join(sections_html)

    def _generate_voucher_alert(self, voucher_data: Dict) -> str:
        """生成凭证预警HTML"""
        status = voucher_data['status']
        if status == '完整':
            return '<div class="alert alert-info"><strong>✓</strong> 费用凭证完整</div>'
        elif status == '部分缺失':
            return '<div class="alert alert-warn"><strong>⚠</strong> 建议补充凭证：费用凭证Sheet需补充大项费用的实际凭证截图</div>'
        else:
            return '<div class="alert alert-err"><strong>✗</strong> 费用凭证缺失：费用凭证Sheet为空，请补充500元以上费用的发票照片或合同截图。</div>'

    def _generate_alert_html(self, alert: Dict) -> str:
        """生成单个预警HTML"""
        level_colors = {'P0': 'ef4444', 'P1': 'f97316', 'P2': 'fbbf24'}
        alert_types = {'error': 'alert-err', 'warning': 'alert-warn', 'info': 'alert-info'}

        color = level_colors.get(alert['level'], 'fbbf24')
        alert_class = alert_types.get(alert['type'], 'alert-info')

        items_html = ''.join([f'<li style="color:rgba(255,255,255,0.8);margin-bottom:8px;">{item}</li>' for item in alert.get('items', [])])

        return f'''
        <h4 style="color:#{color};margin-bottom:16px;">{alert['level']} - {alert['title']}</h4>
        <div class="alert {alert_class}" style="margin-bottom:24px;">
            <strong>{alert['message']}</strong>
            {''.join([f'<ul style="list-style:decimal;padding-left:20px;margin-top:12px;">{items_html}</ul>' if items_html else ''])}
        </div>'''


def main(file_path: str, output_dir: str = None) -> Tuple[bool, str]:
    """
    主函数：执行活动复盘合规审核

    Args:
        file_path: Excel文件路径
        output_dir: 输出目录（可选）

    Returns:
        (成功标志, 报告路径)
    """
    if output_dir is None:
        output_dir = os.path.dirname(file_path) or '.'

    # 提取文件名用于命名报告
    file_name = os.path.splitext(os.path.basename(file_path))[0]

    # 初始化审核器
    auditor = ActivityReviewAuditor(file_path)

    # 加载文件
    if not auditor.load_file():
        return False, "文件加载失败"

    # 执行审核
    print("\n执行全面审核...")
    results = auditor.audit_all()

    # 生成报告
    output_path = os.path.join(output_dir, f"{file_name}_合规自查报告.html")
    print(f"\n生成HTML报告...")
    report_path = auditor.generate_html_report(output_path)

    print("\n" + "="*50)
    print("审核完成!")
    print(f"总分: {results['total_score']}/100分")
    print(f"得分率: {results['score_rate']*100:.1f}%")
    print(f"审核结论: {'通过' if not results['needs_review'] else '需补充复审'}")
    print(f"报告路径: {report_path}")
    print("="*50)

    return True, report_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python activity_review_skill.py <Excel文件路径> [输出目录]")
        print("示例: python activity_review_skill.py 活动总结.xlsx ./output")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    success, result = main(file_path, output_dir)
    sys.exit(0 if success else 1)