#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
威胁研判分析报告生成器
Professional Threat Assessment Report Generator

This script generates comprehensive threat assessment reports in DOCX format
with professional table styling, risk matrices, and multi-level recommendations.
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement
from datetime import datetime
from typing import List, Dict, Tuple, Any
import os

def set_cell_shading(cell, fill: str) -> None:
    """
    设置单元格背景色
    Set cell background color for table headers
    """
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), fill)
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_border(cell, **kwargs) -> None:
    """
    设置单元格边框
    Set cell borders
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ['top', 'left', 'bottom', 'right']:
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = OxmlElement(tag)
            element.set(qn('w:val'), edge_data.get('val', 'single'))
            element.set(qn('w:sz'), str(edge_data.get('sz', 4)))
            element.set(qn('w:color'), edge_data.get('color', 'auto'))
            tcBorders.append(element)
    tcPr.append(tcBorders)

def create_header_row(table, headers: List[str], bg_color: str = 'E7E6E6') -> None:
    """
    创建表格表头行
    Create table header row with styling
    """
    row = table.rows[0]
    for idx, header in enumerate(headers):
        cell = row.cells[idx]
        cell.text = header
        set_cell_shading(cell, bg_color)
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10.5)
                run.font.name = 'SimSun'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

def add_data_row(table, row_idx: int, data: List[str]) -> None:
    """
    添加数据行
    Add data row to table
    """
    row = table.rows[row_idx]
    for idx, cell_text in enumerate(data):
        cell = row.cells[idx]
        cell.text = cell_text
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(10.5)
                run.font.name = 'SimSun'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')

def create_threat_report(
    threat_name: str,
    report_number: str,
    organization: str,
    classification: str,
    executive_summary: Dict[str, Any],
    infrastructure_data: Dict[str, Any],
    technical_analysis: Dict[str, Any],
    impact_assessment: Dict[str, Any],
    risk_matrix: List[Dict[str, str]],
    recommendations: Dict[str, List[str]],
    references: List[Dict[str, str]],
    output_path: str
) -> str:
    """
    生成威胁研判分析报告
    Generate comprehensive threat assessment report

    Args:
        threat_name: 威胁名称
        report_number: 报告编号
        organization: 编制单位
        classification: 密级
        executive_summary: 执行摘要数据
        infrastructure_data: 基础设施数据
        technical_analysis: 技术分析数据
        impact_assessment: 影响评估数据
        risk_matrix: 风险矩阵
        recommendations: 建议
        references: 参考来源
        output_path: 输出路径

    Returns:
        生成的文件路径
    """
    doc = Document()

    # 设置默认字体
    style = doc.styles['Normal']
    style.font.name = 'SimSun'
    style._element.rPr.rFonts.set(qn('w:eastAsia'), 'SimSun')
    style.font.size = Pt(12)

    # 设置页面边距
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    # ============ 封面 ============
    for _ in range(8):
        doc.add_paragraph()

    # 标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(f'{threat_name}威胁研判分析报告')
    run.bold = True
    run.font.size = Pt(28)
    run.font.name = 'Microsoft YaHei'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    # 副标题
    if 'subtitle' in executive_summary:
        subtitle = doc.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = subtitle.add_run(executive_summary['subtitle'])
        run.font.size = Pt(16)
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    for _ in range(6):
        doc.add_paragraph()

    # 文档信息
    info_items = [
        ('报告编号', report_number),
        ('编制单位', organization),
        ('编制日期', datetime.now().strftime('%Y年%m月%d日')),
        ('密级', classification)
    ]

    for label, value in info_items:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(f'{label}：{value}')
        run.font.size = Pt(12)

    doc.add_page_break()

    # ============ 目录 ============
    toc_title = doc.add_paragraph()
    toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = toc_title.add_run('目  录')
    run.bold = True
    run.font.size = Pt(18)
    run.font.name = 'Microsoft YaHei'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    toc_items = [
        '一、执行摘要',
        '二、威胁实体概述',
        '三、域名基础设施分析',
        '四、技术架构分析',
        '五、境内影响评估',
        '六、风险等级划分',
        '七、防范建议与措施',
        '八、结论与总结',
        '参考来源'
    ]

    for item in toc_items:
        p = doc.add_paragraph()
        run = p.add_run(item)
        run.font.size = Pt(12)

    doc.add_page_break()

    # ============ 一、执行摘要 ============
    h1 = doc.add_heading('一、执行摘要', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'intro' in executive_summary:
        p = doc.add_paragraph()
        p.add_run(executive_summary['intro'])

    if 'key_findings' in executive_summary:
        for finding in executive_summary['key_findings']:
            p = doc.add_paragraph()
            if isinstance(finding, tuple):
                run = p.add_run(finding[0])
                run.bold = True
                p.add_run(finding[1])
            else:
                p.add_run(finding)

    # ============ 二、威胁实体概述 ============
    if 'entity_overview' in infrastructure_data:
        h1 = doc.add_heading('二、威胁实体概述', level=1)
        for run in h1.runs:
            run.font.name = 'Microsoft YaHei'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

        overview = infrastructure_data['entity_overview']
        if 'company_history' in overview:
            h2 = doc.add_heading('2.1 公司历史与发展', level=2)
            for run in h2.runs:
                run.font.name = 'Microsoft YaHei'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
            p = doc.add_paragraph()
            p.add_run(overview['company_history'])

        if 'product_portfolio' in overview:
            h2 = doc.add_heading('2.2 产品线概述', level=2)
            for run in h2.runs:
                run.font.name = 'Microsoft YaHei'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
            p = doc.add_paragraph()
            p.add_run(overview.get('product_intro', ''))
            for product in overview['product_portfolio']:
                p = doc.add_paragraph()
                run = p.add_run(f"{product['name']}：")
                run.bold = True
                p.add_run(product['description'])

    # ============ 三、域名基础设施分析 ============
    h1 = doc.add_heading('三、域名基础设施分析', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    # 3.1 域名体系分布
    h2 = doc.add_heading('3.1 域名体系分布', level=2)
    for run in h2.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'domain_systems' in infrastructure_data:
        p = doc.add_paragraph()
        p.add_run(infrastructure_data.get('domain_intro', '本次分析的域名清单涵盖主要域名体系，具体分布如下：'))

        # 域名体系分布表格
        table1 = doc.add_table(rows=len(infrastructure_data['domain_systems']) + 1, cols=4)
        table1.style = 'Table Grid'
        create_header_row(table1, ['域名体系', '主要功能标识', '服务器数量估算', '主要用途'])

        for idx, domain in enumerate(infrastructure_data['domain_systems']):
            add_data_row(table1, idx + 1, [
                domain['system'],
                domain['function_id'],
                domain['count'],
                domain['primary_use']
            ])

    # 3.2 服务器地域分布
    h2 = doc.add_heading('3.2 服务器地域分布', level=2)
    for run in h2.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'geo_distribution' in infrastructure_data:
        p = doc.add_paragraph()
        p.add_run(infrastructure_data.get('geo_intro', '服务器地理分布如下：'))

        # 地域分布表格
        table2 = doc.add_table(rows=len(infrastructure_data['geo_distribution']) + 1, cols=4)
        table2.style = 'Table Grid'
        create_header_row(table2, ['地区/国家', '服务器数量', '战略地位', '主要功能'])

        for idx, geo in enumerate(infrastructure_data['geo_distribution']):
            add_data_row(table2, idx + 1, [
                geo['region'],
                geo['count'],
                geo['position'],
                geo['function']
            ])

    # 3.3 节点功能分析
    h2 = doc.add_heading('3.3 节点功能分析', level=2)
    for run in h2.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'node_functions' in infrastructure_data:
        p = doc.add_paragraph()
        p.add_run('通过对域名命名规则的分析，可以推断出系统的功能架构：')

        table3 = doc.add_table(rows=len(infrastructure_data['node_functions']) + 1, cols=3)
        table3.style = 'Table Grid'
        create_header_row(table3, ['功能标识', '推测功能', '典型域名示例'])

        for idx, node in enumerate(infrastructure_data['node_functions']):
            add_data_row(table3, idx + 1, [
                node['function_id'],
                node['inferred_function'],
                node['examples']
            ])

    # ============ 四、技术架构分析 ============
    h1 = doc.add_heading('四、技术架构分析', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'technical_elements' in technical_analysis:
        h2 = doc.add_heading('4.1 核心技术要素', level=2)
        for run in h2.runs:
            run.font.name = 'Microsoft YaHei'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

        if 'intro' in technical_analysis:
            p = doc.add_paragraph()
            p.add_run(technical_analysis['intro'])

        # 技术要素表格
        table4 = doc.add_table(rows=len(technical_analysis['technical_elements']) + 1, cols=3)
        table4.style = 'Table Grid'
        create_header_row(table4, ['技术要素', '详细说明', '威胁等级'])

        for idx, element in enumerate(technical_analysis['technical_elements']):
            add_data_row(table4, idx + 1, [
                element['element'],
                element['description'],
                element['threat_level']
            ])

    if 'capabilities' in technical_analysis:
        h2 = doc.add_heading('4.2 核心功能分析', level=2)
        for run in h2.runs:
            run.font.name = 'Microsoft YaHei'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

        for capability in technical_analysis['capabilities']:
            if 'heading' in capability:
                h3 = doc.add_heading(capability['heading'], level=3)
                for run in h3.runs:
                    run.font.name = 'Microsoft YaHei'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
            if 'description' in capability:
                p = doc.add_paragraph()
                p.add_run(capability['description'])

    # ============ 五、境内影响评估 ============
    h1 = doc.add_heading('五、境内影响评估', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'impact_sections' in impact_assessment:
        for section in impact_assessment['impact_sections']:
            if 'heading' in section:
                level = section.get('level', 2)
                h = doc.add_heading(section['heading'], level=level)
                for run in h.runs:
                    run.font.name = 'Microsoft YaHei'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

            if 'content' in section:
                p = doc.add_paragraph()
                p.add_run(section['content'])

            if 'subsections' in section:
                for subsection in section['subsections']:
                    if 'heading' in subsection:
                        h_sub = doc.add_heading(subsection['heading'], level=3)
                        for run in h_sub.runs:
                            run.font.name = 'Microsoft YaHei'
                            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
                    if 'content' in subsection:
                        p = doc.add_paragraph()
                        p.add_run(subsection['content'])

    # ============ 六、风险等级划分 ============
    h1 = doc.add_heading('六、风险等级划分', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'intro' in impact_assessment:
        p = doc.add_paragraph()
        p.add_run(impact_assessment['intro'])

    if risk_matrix:
        table5 = doc.add_table(rows=len(risk_matrix) + 1, cols=4)
        table5.style = 'Table Grid'
        create_header_row(table5, ['风险类别', '风险等级', '具体描述', '影响范围'])

        for idx, risk in enumerate(risk_matrix):
            add_data_row(table5, idx + 1, [
                risk['category'],
                risk['level'],
                risk['description'],
                risk['scope']
            ])

    # ============ 七、防范建议与措施 ============
    h1 = doc.add_heading('七、防范建议与措施', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'individual' in recommendations:
        h2 = doc.add_heading('7.1 个人层面防范建议', level=2)
        for run in h2.runs:
            run.font.name = 'Microsoft YaHei'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

        for tip in recommendations['individual']:
            p = doc.add_paragraph()
            p.add_run(tip)

    if 'enterprise' in recommendations:
        h2 = doc.add_heading('7.2 企业层面防范建议', level=2)
        for run in h2.runs:
            run.font.name = 'Microsoft YaHei'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

        for tip in recommendations['enterprise']:
            p = doc.add_paragraph()
            p.add_run(tip)

    if 'national' in recommendations:
        h2 = doc.add_heading('7.3 国家层面应对措施', level=2)
        for run in h2.runs:
            run.font.name = 'Microsoft YaHei'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

        for tip in recommendations['national']:
            p = doc.add_paragraph()
            p.add_run(tip)

    # ============ 八、结论与总结 ============
    h1 = doc.add_heading('八、结论与总结', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    if 'conclusions' in executive_summary:
        for conclusion in executive_summary['conclusions']:
            p = doc.add_paragraph()
            if isinstance(conclusion, tuple):
                run = p.add_run(conclusion[0])
                run.bold = True
                p.add_run(conclusion[1])
            else:
                p.add_run(conclusion)

    if 'summary' in executive_summary:
        p = doc.add_paragraph()
        p.add_run(executive_summary['summary'])

    # ============ 参考来源 ============
    h1 = doc.add_heading('参考来源', level=1)
    for run in h1.runs:
        run.font.name = 'Microsoft YaHei'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')

    for idx, ref in enumerate(references):
        p = doc.add_paragraph()
        p.add_run(f"[{idx + 1}] {ref['name']} - {ref['reliability']} - {ref['description']}")
        if 'url' in ref:
            p = doc.add_paragraph()
            p.add_run(f"    URL: {ref['url']}")
        p.paragraph_format.space_after = Pt(6)

    # 保存文档
    doc.save(output_path)
    return output_path


# 示例数据生成函数
def generate_sample_data(threat_name: str = "Cobweb/Webloc") -> Dict[str, Any]:
    """
    生成示例数据
    Generate sample data for demonstration
    """
    return {
        'threat_name': threat_name,
        'report_number': f'THREAT-{datetime.now().strftime("%Y%m%d")}-001',
        'organization': '技术分析中心',
        'classification': '内部研判',
        'executive_summary': {
            'subtitle': '——基于域名分布的深度技术分析与境内影响评估',
            'intro': f'本报告针对{threat_name}系统进行系统性技术分析，主要发现如下：',
            'key_findings': [
                ('1. 系统性质确认：', '该系统是由以色列公司开发的商业化广告定位监控工具。'),
                ('2. 域名分布特征：', '涵盖三大域名体系，共涉及约430个二级域名服务器节点。'),
                ('3. 境内影响评估：', '香港部署的服务器对中国境内用户构成直接威胁。'),
                ('4. 执法应用情况：', '已被多国执法机构正式采用。'),
                ('5. 制裁记录：', '被主要社交平台认定为"网络雇佣军"并封禁。')
            ],
            'conclusions': [
                ('技术先进性：', '利用广告数据生态系统实现精准定位。'),
                ('全球覆盖：', '服务器基础设施遍布25个国家。'),
                ('隐私侵犯：', '可追溯三年的历史数据。')
            ],
            'summary': '建议相关部门持续关注该系统的发展动态，加强数据跨境流动监管。'
        },
        'infrastructure_data': {
            'entity_overview': {
                'company_history': 'Cobwebs Technologies是一家成立于2015年的以色列网络情报公司...',
                'product_intro': '提供三款主要监控软件：',
                'product_portfolio': [
                    {'name': 'Tangles', 'description': '用于追踪和监控人们的社交关系。'},
                    {'name': 'Webloc', 'description': '基于Web的监控软件，能够追踪人们的言论和行动轨迹。'},
                    {'name': 'Lynx', 'description': '可用于根据手机、网络和社交媒体活动追踪和监控人员。'}
                ]
            },
            'domain_intro': '本次分析的域名清单涵盖三大域名体系，共约430个二级域名服务器节点。',
            'domain_systems': [
                {'system': 'cobwebsapp.com', 'function_id': 'tg/wr/td/wl前缀', 'count': '约120+个节点', 'primary_use': '主控服务器集群'},
                {'system': 'cwsystem.com', 'function_id': 'p前缀 + 数字编号', 'count': '约90+个节点', 'primary_use': '备用系统节点'},
                {'system': 'cwtapp.com', 'function_id': 's前缀 + 数字编号', 'count': '约220+个节点', 'primary_use': '分布式服务节点'}
            ],
            'geo_intro': '服务器地理分布如下：',
            'geo_distribution': [
                {'region': '美国', 'count': '126台', 'position': '核心枢纽', 'function': '主要数据处理中心'},
                {'region': '荷兰', 'count': '32台', 'position': '欧洲枢纽', 'function': '欧洲数据中转站'},
                {'region': '新加坡', 'count': '17台', 'position': '亚太枢纽', 'function': '亚太数据覆盖'},
                {'region': '香港', 'count': '8台', 'position': '重要节点', 'function': '中国及亚太覆盖'}
            ],
            'node_functions': [
                {'function_id': 'tg-*', 'inferred_function': '目标追踪服务器', 'examples': 'tg-101、tg-102'},
                {'function_id': 'wr-*', 'inferred_function': '网关路由服务器', 'examples': 'wr-s361'},
                {'function_id': 'td-*', 'inferred_function': '目标数据服务器', 'examples': 'td-rtn'},
                {'function_id': 'wl-*', 'inferred_function': '网络定位服务器', 'examples': 'wl-angel6'}
            ]
        },
        'technical_analysis': {
            'intro': '核心技术要素如下：',
            'technical_elements': [
                {'element': '数据来源', 'description': '实时竞价（RTB）广告拍卖和基于SDK的应用追踪器', 'threat_level': '高'},
                {'element': '追踪方式', 'description': '链接到GPS、Wi-Fi和行为数据的移动广告ID', 'threat_level': '高'},
                {'element': '历史数据', 'description': '最多可追溯三年的过往记录', 'threat_level': '极高'},
                {'element': '地理围栏', 'description': '支持地理围栏功能', 'threat_level': '高'}
            ],
            'capabilities': [
                {'heading': '4.2.1 设备追踪能力', 'description': '自动并持续监控独特的移动广告ID；基于位置的IP地址分析。'},
                {'heading': '4.2.2 历史追溯能力', 'description': '该系统可以监控个人最多三年的过往位置、行动轨迹和个人特征。'},
                {'heading': '4.2.3 身份推断功能', 'description': '系统可以从广告定位细分中推断出用户的兴趣、行为特征等。'}
            ]
        },
        'impact_assessment': {
            'intro': '基于对系统的技术分析和境内影响评估，将相关风险划分为以下等级：',
            'impact_sections': [
                {
                    'heading': '5.1 香港服务器的特殊意义',
                    'content': '香港部署的服务器对中国境内用户具有以下潜在影响：',
                    'subsections': [
                        {'heading': '数据覆盖范围', 'content': '可能用于收集访港中国公民的数据、监控跨境网络流量。'},
                        {'heading': '"一国两制"下的监控漏洞', 'content': '香港的特殊地位可能使其成为监控中国目标的一个跳板。'}
                    ]
                },
                {
                    'heading': '5.2 亚太地区影响分析',
                    'content': '新加坡部署的服务器是亚太地区的重要节点，可能被用于监控东南亚地区的中国公民和实体。'
                },
                {
                    'heading': '5.3 监管关注点',
                    'content': '该系统可能引发以下监管关注：',
                    'subsections': [
                        {'heading': '数据跨境流动', 'content': '可能涉及数据跨境传输问题。'},
                        {'heading': '个人信息保护', 'content': '根据中国《个人信息保护法》，大规模数据收集可能违反相关法规。'}
                    ]
                }
            ]
        },
        'risk_matrix': [
            {'category': '数据主权风险', 'level': '极高', 'description': '境外服务器存储中国公民数据', 'scope': '所有在港/海外中国公民'},
            {'category': '隐私泄露风险', 'level': '高', 'description': '三年历史数据可追溯分析', 'scope': '使用广告追踪应用的用户'},
            {'category': '跨境执法风险', 'level': '高', 'description': '美执法机构追踪中国目标', 'scope': '涉美案件相关人员'},
            {'category': '商业情报风险', 'level': '中', 'description': '亚太节点收集商业数据', 'scope': '在东南亚运营的中资企业'},
            {'category': '个人追踪风险', 'level': '高', 'description': '精准定位特定个人', 'scope': '高价值目标人员'}
        ],
        'recommendations': {
            'individual': [
                '限制移动应用的位置权限：仅在必要时授权位置访问，定期审查已授权应用列表；',
                '使用广告拦截和隐私保护工具：安装可信的广告拦截插件，减少广告追踪；',
                '关注应用的隐私政策：仔细阅读应用权限请求，避免安装来源不明的应用。'
            ],
            'enterprise': [
                '对员工进行安全意识培训：提高员工对隐私保护和设备安全的认识；',
                '在敏感地区使用安全通信工具：部署企业级加密通信解决方案；',
                '定期审计企业设备的安全状态：检查是否存在异常的数据传输行为。'
            ],
            'national': [
                '关注境外监控工具的情报活动：建立针对商业监控工具的监测机制；',
                '加强数据跨境传输的监管：完善数据出境安全评估制度；',
                '推动建立国际监控规范：在多边框架下倡导负责任使用监控技术。'
            ]
        },
        'references': [
            {'name': 'Citizen Lab. Uncovering Webloc', 'reliability': '高可信度', 'description': '权威安全研究机构', 'url': 'https://citizenlab.ca'},
            {'name': 'The Hacker News. Citizen Lab Reports', 'reliability': '高可信度', 'description': '网络安全权威媒体', 'url': 'https://thehackernews.com'},
            {'name': 'Meta Threat Report', 'reliability': '高可信度', 'description': '平台官方威胁报告', 'url': 'https://about.fb.com'}
        ]
    }


if __name__ == '__main__':
    # 生成示例报告
    sample_data = generate_sample_data()
    output = create_threat_report(**sample_data, output_path='/workspace/docs/sample_threat_report.docx')
    print(f'Sample report generated: {output}')
