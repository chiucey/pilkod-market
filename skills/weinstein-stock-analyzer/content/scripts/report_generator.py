#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel报告生成器
用于MaxClaw技能输出
"""

import os
import sys
from datetime import datetime
from typing import Dict, List

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ReportGenerator:
    """Excel报告生成器"""

    COLORS = {
        'stage1': 'FFFFFF',
        'stage2': 'FF6464',
        'stage3': 'FFFF64',
        'stage4': '64FF64',
        'rs_strong': 'FF6464',
        'rs_mild': 'FFFF64',
        'rs_weak': '64FF64',
        'good': 'FF6464',
        'neutral': 'FFFF64',
        'bad': '64FF64',
        'header_bg': 'D3D3D3',
        'label_bg': 'B8CCE4',
        'white': 'FFFFFF',
    }

    def __init__(self):
        self.workbook = None
        self.worksheet = None

    def _apply_style(self, cell, value=None, font_size=10, bold=False,
                     bg_color=None, text_color='000000', align='center'):
        """应用单元格样式"""
        if value is not None:
            cell.value = value
        cell.font = Font(size=font_size, bold=bold, color=text_color)
        cell.alignment = Alignment(horizontal=align, vertical='center', wrap_text=True)
        if bg_color:
            cell.fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type='solid')
        thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        cell.border = thin_border

    def _get_stage_color(self, stage: int) -> str:
        """获取阶段颜色"""
        return self.COLORS.get(f'stage{stage}', self.COLORS['white'])

    def _get_rs_color(self, rs_level: str) -> str:
        """获取相对强度颜色"""
        if rs_level == '强':
            return self.COLORS['rs_strong']
        elif rs_level in ['小强', '小弱']:
            return self.COLORS['rs_mild']
        elif rs_level == '弱':
            return self.COLORS['rs_weak']
        return self.COLORS['neutral']

    def create_report(self, analysis_results: List[Dict],
                      title: str = "笑傲牛熊股票分析报告") -> str:
        """创建Excel报告"""
        if not OPENPYXL_AVAILABLE:
            return None

        self.workbook = Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = "股票分析"

        # 设置列宽
        self.worksheet.column_dimensions['A'].width = 12
        for i in range(2, len(analysis_results) + 2):
            self.worksheet.column_dimensions[get_column_letter(i)].width = 12

        # 标题行
        self.worksheet.row_dimensions[1].height = 30
        end_col = get_column_letter(1 + len(analysis_results))
        title_cell = self.worksheet.cell(row=1, column=1)
        self._apply_style(title_cell, title, font_size=14, bold=True,
                         bg_color=self.COLORS['header_bg'])
        self.worksheet.merge_cells(f'A1:{end_col}1')

        # 表头行
        row = 2
        self.worksheet.row_dimensions[row].height = 25
        label_cell = self.worksheet.cell(row=row, column=1)
        self._apply_style(label_cell, "指标/股票", bold=True, bg_color=self.COLORS['label_bg'])
        for i, result in enumerate(analysis_results):
            col = i + 2
            cell = self.worksheet.cell(row=row, column=col)
            self._apply_style(cell, result.get('stock_name', result.get('stock_code', f'股票{i+1}')),
                            bold=True, bg_color=self.COLORS['label_bg'])

        # 数据行
        indicators = [
            ('市场', lambda r: r.get('market_stage', {}).get('stage_name', '未知'),
             lambda r: self._get_stage_color(r.get('market_stage', {}).get('stage', 1))),
            ('行业', lambda r: r.get('industry_stage', {}).get('stage_name', '未知'),
             lambda r: self._get_stage_color(r.get('industry_stage', {}).get('stage', 1))),
            ('股票阶段', lambda r: r.get('stock_stage', {}).get('stage_name', '未知'),
             lambda r: self._get_stage_color(r.get('stock_stage', {}).get('stage', 1))),
            ('相对强度', lambda r: r.get('relative_strength', '未知'), self._get_rs_color),
            ('30周以上', lambda r: "高于30周" if r.get('above_30_week') else "低于30周",
             lambda r: 'FF6464' if r.get('above_30_week') else '64FF64'),
            ('成交量', lambda r: r.get('volume_level', '未知'), lambda r: r.get('volume_color', 'FFFF64')),
            ('幅度%', lambda r: f"{r.get('price_change_pct', 0):+.2f}%",
             lambda r: 'FF6464' if r.get('price_change_pct', 0) > 0 else '64FF64'),
            ('现价', lambda r: f"{r.get('current_price', 0):.2f}", lambda r: 'FFFFFF'),
            ('止损点', lambda r: f"{r.get('stop_loss_daily', 0):.2f}" if r.get('stop_loss_daily', 0) > 0 else "-",
             lambda r: 'FFCCCC'),
            ('长期止损', lambda r: f"{r.get('stop_loss_weekly', 0):.2f}" if r.get('stop_loss_weekly', 0) > 0 else "-",
             lambda r: 'FFCCCC'),
            ('操作建议', lambda r: r.get('recommendation', '观望'),
             lambda r: {'买入': 'FF6464', '持有': 'FF6464', '观望': 'FFFF64', '减仓': 'FFFF64', '卖出': '64FF64'}.get(
                 r.get('recommendation', '观望'), 'FFFFFF')),
        ]

        for i, (name, value_func, color_func) in enumerate(indicators):
            row = i + 3
            self.worksheet.row_dimensions[row].height = 22

            label_cell = self.worksheet.cell(row=row, column=1)
            self._apply_style(label_cell, name, bg_color=self.COLORS['label_bg'])

            for j, result in enumerate(analysis_results):
                col = j + 2
                cell = self.worksheet.cell(row=row, column=col)
                value = value_func(result)
                color = color_func(result) if callable(color_func) else color_func
                self._apply_style(cell, value, bg_color=color)

        # 备注区域
        row += 2
        notes_title = self.worksheet.cell(row=row, column=1)
        self._apply_style(notes_title, "备注", bold=True, bg_color=self.COLORS['label_bg'])
        self.worksheet.merge_cells(f'A{row}:{end_col}{row}')

        notes = [
            "阶段颜色: 阶段1(无色)=底部, 阶段2(红色)=拉升, 阶段3(黄色)=顶部, 阶段4(绿色)=下跌",
            "相对强度: 强(红色)=个股强于大盘20%+, 小强/小弱(黄色)=5%-20%, 弱(绿色)=<-5%",
            "操作建议: 买入/持有=积极关注, 观望=谨慎, 减仓/卖出=风险警示",
        ]

        for note in notes:
            row += 1
            cell = self.worksheet.cell(row=row, column=1)
            self._apply_style(cell, note)
            self.worksheet.merge_cells(f'A{row}:{end_col}{row}')

        # 保存
        os.makedirs("output", exist_ok=True)
        output_path = f"output/weinstein_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.workbook.save(output_path)
        return output_path


def generate_report(analysis_results: List[Dict], title: str = "笑傲牛熊股票分析报告") -> str:
    """生成报告的便捷函数"""
    generator = ReportGenerator()
    return generator.create_report(analysis_results, title)


# 导出
__all__ = ['ReportGenerator', 'generate_report']
