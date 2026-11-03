"""
高新技术企业研发立项报告Word文档生成脚本
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from datetime import datetime

def create_report(project_name, tech_domain, project_info=None):
    """
    生成研发立项报告Word文档

    Args:
        project_name: 研发项目名称
        tech_domain: 技术领域
        project_info: 可选的项目详细信息字典
    """
    doc = Document()

    # 设置中文字体
    style = doc.styles['Normal']
    style.font.name = 'SimSun'
    style.font.size = Pt(12)

    # 标题
    title = doc.add_heading('研发项目立项报告', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 项目基本信息表
    doc.add_heading('一、项目基本信息', level=1)

    table = doc.add_table(rows=7, cols=2)
    table.style = 'Table Grid'

    info_data = [
        ('项目名称', project_name),
        ('项目编号', f'RD-{datetime.now().year}-001'),
        ('所属领域', tech_domain),
        ('起止时间', '2026年XX月 - 2027年XX月'),
        ('项目负责人', 'XXX（职务）'),
        ('项目团队', '研发人员X名，其中高级工程师X名'),
        ('立项时间', datetime.now().strftime('%Y年%m月%d日'))
    ]

    for i, (key, value) in enumerate(info_data):
        table.rows[i].cells[0].text = key
        table.rows[i].cells[1].text = value

    # 项目背景与立项依据
    doc.add_heading('二、项目背景与立项依据', level=1)
    doc.add_paragraph('（一）行业痛点分析')
    doc.add_paragraph('明确当前行业内同类技术/产品存在的核心问题...')

    doc.add_paragraph('（二）市场需求说明')
    doc.add_paragraph('结合行业趋势，说明客户/市场对新技术、新产品的迫切需求...')

    doc.add_paragraph('（三）政策导向契合度')
    doc.add_paragraph('说明项目符合国家/地方产业政策、高企领域支持方向...')

    doc.add_paragraph('（四）企业战略关联性')
    doc.add_paragraph('阐述项目与公司主营业务、技术路线、产品升级的关联...')

    doc.add_paragraph('（五）技术现状与突破点')
    doc.add_paragraph('简述国内外同类技术水平、存在的不足，明确本项目的核心突破点...')

    # 研发目标
    doc.add_heading('三、研发目标', level=1)
    doc.add_paragraph('（一）总体目标')
    doc.add_paragraph('明确项目要解决的核心问题、达到的技术水平、形成的核心成果...')

    doc.add_paragraph('（二）具体技术指标')
    indicators = [
        '光电转换效率≥25%',
        '电源转换效率≥95%（满载）',
        '产品良率≥99.5%',
        '能耗较传统产品降低30%',
        '响应时间≤50ms',
        'MTBF≥100,000小时'
    ]
    for indicator in indicators:
        doc.add_paragraph(indicator, style='List Bullet')

    doc.add_paragraph('（三）经济/社会效益目标')
    doc.add_paragraph('年产能X万台，年销售收入X万元，成本较传统产品下降X%...')

    # 核心研发内容
    doc.add_heading('四、核心研发内容', level=1)
    doc.add_paragraph('（一）主要研究内容')
    contents = [
        '材料研发：新型器件的选型、测试与适配优化',
        '结构设计：一体化散热结构、小型化封装结构的设计与仿真',
        '算法开发：智能故障预警算法、高效功率控制算法的研发与调试',
        '工艺优化：产品试制工艺、组装工艺的优化，提升良率',
        '测试验证：产品性能测试、可靠性测试、环境适应性测试'
    ]
    for content in contents:
        doc.add_paragraph(content, style='List Bullet')

    doc.add_paragraph('（二）核心技术')
    doc.add_paragraph('明确项目的关键技术、技术原理、技术方案...')

    doc.add_paragraph('（三）创新点')
    doc.add_paragraph('固定结构：采用什么创新技术/方法 → 解决什么技术痛点 → 达到什么量化效果')
    innovations = [
        '技术创新：采用新型XXX替代传统XXX，解决XXX问题，实现XXX提升XX%',
        '结构创新：设计XXX结构，降低XXX，提升产品可靠性与使用寿命',
        '算法创新：引入XXX算法，实现XXX，XXX降低XX%'
    ]
    for i, innovation in enumerate(innovations, 1):
        doc.add_paragraph(f'{i}. {innovation}')

    doc.add_paragraph('（四）关键技术问题')
    doc.add_paragraph('明确要攻克的技术难点、风险点及解决方案...')

    # 技术路线与实施方案
    doc.add_heading('五、技术路线与实施方案', level=1)
    doc.add_paragraph('（一）技术路线')
    doc.add_paragraph('推荐流程：调研→方案设计→小试→中试→优化→定型→测试→验收')

    doc.add_paragraph('（二）实施步骤')

    stage_table = doc.add_table(rows=5, cols=4)
    stage_table.style = 'Table Grid'
    stage_headers = ['阶段', '时间范围', '工作内容', '交付物']
    for i, header in enumerate(stage_headers):
        stage_table.rows[0].cells[i].text = header

    stages = [
        ('第一阶段', '2026.XX-XX', '需求调研、方案设计、专利布局', '方案设计报告、专利申请文件'),
        ('第二阶段', '2026.XX-XX', '核心技术研发、样品试制', '样品、小试报告、测试数据'),
        ('第三阶段', '2026.XX-XX', '测试优化、中试验证', '中试报告、优化后样品'),
        ('第四阶段', '2027.XX-XX', '成果固化、验收、产业化准备', '验收报告、最终产品、知识产权证书')
    ]
    for i, stage in enumerate(stages, 1):
        for j, cell_data in enumerate(stage):
            stage_table.rows[i].cells[j].text = cell_data

    doc.add_paragraph('（三）试验/验证方案')
    doc.add_paragraph('明确测试方法、测试设备、测试标准、数据采集与分析方式...')

    # 现有研发条件
    doc.add_heading('六、现有研发条件', level=1)
    conditions = [
        ('技术基础', '企业现有技术积累、相关专利/软著、前期研发成果'),
        ('硬件条件', '研发设备、实验室、生产中试条件'),
        ('人员条件', '研发团队学历/职称/经验、核心人员稳定性'),
        ('合作资源', '高校/科研院所合作、外部专家支持')
    ]
    for key, value in conditions:
        p = doc.add_paragraph()
        p.add_run(f'{key}：').bold = True
        p.add_run(value)

    # 经费预算
    doc.add_heading('七、经费预算', level=1)
    doc.add_paragraph('按高企研发费用8大项归集：')

    budget_table = doc.add_table(rows=8, cols=3)
    budget_table.style = 'Table Grid'
    budget_headers = ['科目', '金额', '占比']
    for i, header in enumerate(budget_headers):
        budget_table.rows[0].cells[i].text = header

    budget_data = [
        ('人员人工费用', 'XXX万元', 'XX%'),
        ('直接投入费用', 'XXX万元', 'XX%'),
        ('折旧与长期待摊费用', 'XXX万元', 'XX%'),
        ('无形资产摊销费用', 'XXX万元', 'XX%'),
        ('设计费用', 'XXX万元', 'XX%'),
        ('装备调试费', 'XXX万元', 'XX%'),
        ('其他费用（≤20%）', 'XXX万元', 'XX%')
    ]
    for i, data in enumerate(budget_data, 1):
        for j, cell_data in enumerate(data):
            budget_table.rows[i].cells[j].text = cell_data

    doc.add_paragraph('注：其他费用不超过总预算的20%，项目单独核算，建立研发费用辅助账。')

    # 预期成果
    doc.add_heading('八、预期成果', level=1)
    doc.add_paragraph('（一）知识产权成果')
    ip_items = ['发明专利X项', '实用新型专利X项', '软件著作权X项']
    for item in ip_items:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph('（二）技术成果')
    tech_items = ['新技术X项', '新产品X款', '企业标准X项', '第三方检测报告X份']
    for item in tech_items:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph('（三）产业化成果')
    doc.add_paragraph('样机X台、量产样品X台、意向销售合同X份、客户应用测试报告X份...')

    doc.add_paragraph('（四）成果转化')
    doc.add_paragraph('应用于XX领域，预期X年内实现产业化...')

    # 风险分析与应对
    doc.add_heading('九、风险分析与应对', level=1)

    risk_table = doc.add_table(rows=6, cols=3)
    risk_table.style = 'Table Grid'
    risk_headers = ['风险类型', '风险描述', '防控措施']
    for i, header in enumerate(risk_headers):
        risk_table.rows[0].cells[i].text = header

    risks = [
        ('技术风险', '核心技术难以突破，指标无法达标', '组建专业研发团队，与高校合作'),
        ('市场风险', '产品研发完成后，市场需求发生变化', '持续跟踪市场动态，调整产品参数'),
        ('人员风险', '核心研发人员离职，影响项目进度', '建立激励机制，培养后备人员'),
        ('资金风险', '研发经费不足，影响项目推进', '合理编制预算，申请政府研发补贴'),
        ('知识产权风险', '出现专利侵权，或核心技术无法获得保护', '开展专利查新，提前布局知识产权')
    ]
    for i, risk in enumerate(risks, 1):
        for j, cell_data in enumerate(risk):
            risk_table.rows[i].cells[j].text = cell_data

    # 立项审批
    doc.add_heading('十、立项审批', level=1)
    doc.add_paragraph('（一）立项决议')
    doc.add_paragraph('本项目已经公司研究决定，同意立项。')

    doc.add_paragraph('（二）审批签字')
    doc.add_paragraph('总经理：__________    日期：__________')
    doc.add_paragraph('研发负责人：__________    日期：__________')
    doc.add_paragraph('财务负责人：__________    日期：__________')

    return doc

if __name__ == '__main__':
    # 测试
    doc = create_report('基于AI算法的智能光伏逆变器研发', '新能源与节能')
    doc.save('研发项目立项报告_模板.docx')
    print('报告已生成：研发项目立项报告_模板.docx')