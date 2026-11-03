# 法考错题分析技能 - 完整代码实现

本文件包含法考错题分析技能的完整Python代码实现。

## 依赖安装

```bash
pip install pdfplumber python-docx matplotlib numpy pytesseract Pillow pdf2image
```

**OCR额外依赖（需安装Tesseract OCR引擎）：**
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim`
- macOS: `brew install tesseract tesseract-lang`
- Windows: 下载安装包并配置环境变量

**中文字体支持（Ubuntu）：**
```bash
sudo apt-get install fonts-noto-cjk
```

## 主程序文件：law_exam_analyzer.py

```python
import os
import sys
import re
import json
import pdfplumber
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional

# ============ OCR模块 ============

try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: OCR dependencies not installed. Run: pip install pytesseract Pillow pdf2image")


def ocr_pdf_to_text(pdf_path: str, dpi: int = 300, lang: str = 'chi_sim+eng') -> List[Dict[str, Any]]:
    """
    使用OCR从PDF中提取文本（适用于扫描版PDF）

    参数:
        pdf_path: PDF文件路径
        dpi: OCR图像分辨率，默认300
        lang: Tesseract语言代码，'chi_sim+eng'表示中文简体+英文

    返回:
        包含页面号和OCR提取文本的字典列表
    """
    if not OCR_AVAILABLE:
        print("Error: OCR库未安装，请运行: pip install pytesseract Pillow pdf2image")
        return []

    try:
        # 将PDF转换为图像
        print(f"正在将PDF转换为图像（DPI: {dpi}）...")
        images = pdf2image.convert_from_path(pdf_path, dpi=dpi)

        results = []
        for page_num, image in enumerate(images, 1):
            print(f"正在OCR识别第 {page_num}/{len(images)} 页...")

            # 可选：图像预处理以提高识别率
            processed_image = preprocess_image(image)

            # 执行OCR
            text = pytesseract.image_to_string(
                processed_image,
                lang=lang,
                config='--psm 6'  # 假设统一文本块
            )

            results.append({
                'page': page_num,
                'text': text,
                'image_path': None  # 可选：保存处理后的图像
            })

        return results

    except Exception as e:
        print(f"OCR处理失败: {e}")
        return []


def preprocess_image(image: Image.Image, denoise: bool = True) -> Image.Image:
    """
    预处理图像以提高OCR识别率

    参数:
        image: PIL图像对象
        denoise: 是否进行降噪处理

    返回:
        处理后的PIL图像对象
    """
    from PIL import ImageFilter, ImageEnhance

    # 转换为灰度图
    gray_image = image.convert('L')

    # 提高对比度
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(1.5)

    # 可选：应用锐化滤镜
    if denoise:
        sharpened = enhanced_image.filter(ImageFilter.SHARPEN)
        return sharpened

    return enhanced_image


def ocr_single_image(image_path: str, lang: str = 'chi_sim+eng') -> str:
    """
    对单个图像文件执行OCR

    参数:
        image_path: 图像文件路径
        lang: Tesseract语言代码

    返回:
        识别的文本内容
    """
    if not OCR_AVAILABLE:
        return ""

    try:
        image = Image.open(image_path)
        processed = preprocess_image(image)
        text = pytesseract.image_to_string(processed, lang=lang, config='--psm 6')
        return text
    except Exception as e:
        print(f"图像OCR失败: {e}")
        return ""


def extract_questions_with_ocr(pdf_path: str, dpi: int = 300) -> List[Dict[str, Any]]:
    """
    使用OCR从PDF提取错题（自动检测文本型或扫描型PDF）

    参数:
        pdf_path: PDF文件路径
        dpi: OCR图像分辨率

    返回:
        包含题目信息的字典列表
    """
    # 首先尝试普通文本提取
    questions = extract_questions_from_pdf(pdf_path)

    # 如果普通提取失败或结果为空，尝试OCR
    if not questions:
        print("普通文本提取未获取到内容，尝试OCR识别...")
        ocr_results = ocr_pdf_to_text(pdf_path, dpi=dpi)

        for ocr_result in ocr_results:
            text = ocr_result['text']
            page_num = ocr_result['page']

            # 按题目分割
            question_blocks = re.split(r'\n\s*\d+[.、]', text)

            for block in question_blocks:
                if len(block.strip()) > 20:
                    question = parse_question_block(block)
                    if question:
                        question['page'] = page_num
                        question['ocr_source'] = True  # 标记为OCR来源
                        questions.append(question)

    return questions


# ============ PDF解析模块 ============

def extract_questions_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    从PDF中提取法考错题

    参数:
        pdf_path: PDF文件路径

    返回:
        包含题目信息的字典列表
    """
    questions = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if not text:
                continue

            # 按题目分割（通常题目以序号开头）
            question_blocks = re.split(r'\n\s*\d+[.、]', text)

            for block in question_blocks:
                if len(block.strip()) > 20:
                    question = parse_question_block(block)
                    if question:
                        question['page'] = page_num
                        questions.append(question)

    return questions


def parse_question_block(block: str) -> Dict[str, Any]:
    """解析单个题目块"""
    lines = block.strip().split('\n')
    question_text = lines[0] if lines else ""

    # 提取选项
    options = {}
    current_option = None
    current_text = []

    for line in lines[1:]:
        option_match = re.match(r'^([A-D])[.、]\s*(.*)$', line)
        if option_match:
            if current_option:
                options[current_option] = ' '.join(current_text)
            current_option = option_match.group(1)
            current_text = [option_match.group(2)]
        elif current_option:
            current_text.append(line.strip())

    if current_option:
        options[current_option] = ' '.join(current_text)

    # 提取答案
    answer_match = re.search(r'答案[：:]\s*([A-D])', block)
    answer = answer_match.group(1) if answer_match else None

    # 提取解析
    analysis_match = re.search(r'解析[：:]\s*(.*?)(?=【|$)', block, re.DOTALL)
    analysis = analysis_match.group(1).strip() if analysis_match else None

    return {
        'question': question_text,
        'options': options,
        'answer': answer,
        'analysis': analysis,
        'raw_text': block
    }


# ============ 知识点提取与分析模块 ============

# 法律科目分类映射
LEGAL_SUBJECTS = {
    '民法': ['民事法律关系', '物权', '债权', '合同', '侵权', '婚姻', '继承', '人格权'],
    '刑法': ['犯罪', '刑罚', '正当防卫', '紧急避险', '犯罪构成', '共同犯罪', '罪数', '量刑'],
    '行政法': ['行政行为', '行政许可', '行政处罚', '行政强制', '行政复议', '行政诉讼', '国家赔偿'],
    '商法': ['公司法', '合伙企业', '证券', '破产', '票据', '保险', '信托'],
    '经济法': ['反垄断', '反不正当竞争', '消费者保护', '产品质量', '价格法', '宏观调控'],
    '民事诉讼法': ['管辖', '当事人', '证据', '诉讼程序', '一审', '二审', '再审', '执行'],
    '刑事诉讼法': ['立案', '侦查', '起诉', '审判', '辩护', '证据', '程序'],
    '行政诉讼法': ['受案范围', '管辖', '诉讼参与人', '证据', '审判程序'],
    '法理学': ['法的本体', '法的运行', '法与社会', '法治', '法系'],
    '宪法': ['公民权利', '国家机构', '选举制度', '违宪审查', '宪法修改'],
    '中国法律史': ['夏商周', '秦汉', '唐宋', '明清', '近代法律变革'],
    '国际法': ['国际法基本原则', '国际法主体', '国际法律责任', '国际争端解决'],
    '国际私法': ['冲突规范', '准据法', '外国人的民事法律地位', '国际民事诉讼'],
    '国际经济法': ['国际贸易法', '国际投资法', '国际金融法', '知识产权国际保护'],
    '知识产权法': ['著作权', '专利权', '商标权', '反不正当竞争'],
    '劳动与社会保障法': ['劳动合同', '社会保险', '劳动争议', '职工福利'],
    '环境资源法': ['环境保护', '自然资源', '污染防治', '生态保护']
}

# 错误原因分类
ERROR_CAUSES = {
    '概念混淆': ['混淆', '搞混', '分不清', '错误理解'],
    '重点遗漏': ['没注意到', '遗漏', '忽视', '忘记了', '没看到'],
    '粗心失误': ['看错了', '选错了', '粗心', '疏忽'],
    '理解偏差': ['理解错误', '理解偏差', '理解不当'],
    '记忆模糊': ['记不清', '记忆模糊', '不确定', '印象不深'],
    '综合理解不足': ['综合分析', '复杂', '关联', '综合']
}


def classify_subject(question_text: str, analysis: str = None) -> str:
    """根据题目内容识别法律科目"""
    full_text = question_text + ' ' + (analysis or "")
    subject_scores = {}

    for subject, keywords in LEGAL_SUBJECTS.items():
        score = sum(1 for keyword in keywords if keyword in full_text)
        if score > 0:
            subject_scores[subject] = score

    if subject_scores:
        return max(subject_scores, key=subject_scores.get)
    return '其他'


def classify_error_cause(question_text: str, options: Dict,
                         answer: str, user_answer: str = None) -> str:
    """判断错误原因"""
    text = question_text + ' ' + ' '.join(options.values())
    cause_scores = defaultdict(int)

    for cause, indicators in ERROR_CAUSES.items():
        for indicator in indicators:
            if indicator in text:
                cause_scores[cause] += 1

    if cause_scores:
        return max(cause_scores, key=cause_scores.get)

    if len(options) > 2 and answer in options:
        if len(options[answer]) > 50:
            return '概念混淆'

    return '综合理解不足'


def extract_knowledge_points(questions: List[Dict]) -> Dict[str, Any]:
    """提取并归纳知识点"""
    subject_questions = defaultdict(list)

    for q in questions:
        subject = classify_subject(q['question'], q.get('analysis'))
        error_cause = classify_error_cause(
            q['question'],
            q.get('options', {}),
            q.get('answer')
        )

        subject_questions[subject].append({
            'question': q['question'],
            'answer': q.get('answer'),
            'error_cause': error_cause,
            'analysis': q.get('analysis'),
            'options': q.get('options')
        })

    subject_stats = {subject: len(q_list) for subject, q_list in subject_questions.items()}

    error_cause_stats = defaultdict(int)
    for q_list in subject_questions.values():
        for q in q_list:
            error_cause_stats[q['error_cause']] += 1

    mastery_stats = {'薄弱': 0, '一般': 0, '需加强': 0}
    for count in subject_stats.values():
        if count >= 3:
            mastery_stats['薄弱'] += count
        elif count == 2:
            mastery_stats['一般'] += count
        else:
            mastery_stats['需加强'] += count

    return {
        'subject_distribution': dict(subject_stats),
        'error_cause_distribution': dict(error_cause_stats),
        'mastery_level_distribution': mastery_stats,
        'subject_questions': dict(subject_questions)
    }


# ============ Word文档生成模块 ============

from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn


def create_summary_document(knowledge_data: Dict[str, Any],
                            output_path: str) -> bool:
    """生成法考错题知识点总结Word文档"""
    doc = Document()

    # 设置默认字体为宋体
    style = doc.styles['Normal']
    style.font.name = '宋体'
    style.font.size = Pt(14)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

    # 添加标题
    title = doc.add_heading('法考错题知识点总结', level=0)

    # 添加统计概览
    doc.add_heading('一、错题统计概览', level=1)
    total = sum(knowledge_data['subject_distribution'].values())
    stats_para = doc.add_paragraph()
    stats_para.add_run(f'本次分析共涉及 {total} 道错题，分布在 {len(knowledge_data["subject_distribution"])} 个法律科目中。')

    # 添加科目分布表
    doc.add_heading('二、各科目错题分布', level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'

    header_cells = table.rows[0].cells
    header_cells[0].text = '法律科目'
    header_cells[1].text = '错题数量'
    header_cells[2].text = '占比'

    for subject, count in sorted(knowledge_data['subject_distribution'].items(), key=lambda x: x[1], reverse=True):
        row_cells = table.add_row().cells
        row_cells[0].text = subject
        row_cells[1].text = str(count)
        row_cells[2].text = f'{count/total*100:.1f}%'

    # 添加错误原因分析
    doc.add_heading('三、错误原因分析', level=1)
    for cause, count in sorted(knowledge_data['error_cause_distribution'].items(), key=lambda x: x[1], reverse=True):
        p = doc.add_paragraph()
        p.add_run(f'• {cause}：{count}题（{count/total*100:.1f}%）')

    # 添加各科目详细知识点
    doc.add_heading('四、各科目知识点归纳', level=1)
    for subject in sorted(knowledge_data['subject_distribution'].keys(), key=lambda x: knowledge_data['subject_distribution'][x], reverse=True):
        doc.add_heading(subject, level=2)
        questions = knowledge_data['subject_questions'][subject]

        for i, q in enumerate(questions, 1):
            p = doc.add_paragraph()
            p.add_run(f'{i}. {q["question"]}').bold = True

            if q.get('options'):
                for opt_key, opt_val in q['options'].items():
                    p = doc.add_paragraph()
                    p.add_run(f'{opt_key}. {opt_val}')

            p = doc.add_paragraph()
            p.add_run(f'正确答案：{q["answer"]}').bold = True

            p = doc.add_paragraph()
            p.add_run(f'错误原因：{q["error_cause"]}')

            if q.get('analysis'):
                p = doc.add_paragraph()
                p.add_run(f'解析：{q["analysis"]}')

            doc.add_paragraph()

    # 添加掌握程度评估
    doc.add_heading('五、知识点掌握程度评估', level=1)
    mastery = knowledge_data['mastery_level_distribution']
    p = doc.add_paragraph()
    p.add_run(f'• 掌握薄弱（高频错题）：{mastery["薄弱"]}题\n')
    p.add_run(f'• 掌握一般（中频错题）：{mastery["一般"]}题\n')
    p.add_run(f'• 需加强（低频错题）：{mastery["需加强"]}题')

    doc.save(output_path)
    return True


# ============ 思维导图生成模块 ============

def generate_mindmap_markdown(knowledge_data: Dict[str, Any]) -> str:
    """生成Markdown格式的思维导图"""
    lines = ['# 法考错题知识点思维导图\n']

    total = sum(knowledge_data['subject_distribution'].values())
    lines.append('## 概览\n')
    lines.append(f'- 总错题数：{total}')
    lines.append(f'- 涉及科目：{len(knowledge_data["subject_distribution"])}个\n')

    sorted_subjects = sorted(knowledge_data['subject_distribution'].items(), key=lambda x: x[1], reverse=True)
    lines.append('## 法律科目分类\n')

    for subject, count in sorted_subjects:
        percentage = count / total * 100
        lines.append(f'### {subject} ({count}题, {percentage:.1f}%)\n')

        questions = knowledge_data['subject_questions'][subject]
        cause_groups = defaultdict(list)
        for q in questions:
            cause_groups[q['error_cause']].append(q)

        for cause, cause_questions in sorted(cause_groups.items(), key=lambda x: len(x[1]), reverse=True):
            lines.append(f'#### {cause} ({len(cause_questions)}题)\n')
            for q in cause_questions:
                text = re.sub(r'^\d+[.、]\s*', '', q['question'])
                if len(text) > 50:
                    text = text[:50] + '...'
                lines.append(f'- {text}')
            lines.append('')

    lines.append('## 错误原因分布\n')
    for cause, count in sorted(knowledge_data['error_cause_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = count / total * 100
        lines.append(f'- {cause}：{count}题（{percentage:.1f}%）')

    lines.append('\n## 掌握程度评估\n')
    mastery = knowledge_data['mastery_level_distribution']
    total_mastery = sum(mastery.values())
    for level, count in mastery.items():
        percentage = count / total_mastery * 100 if total_mastery > 0 else 0
        lines.append(f'- {level}：{count}题（{percentage:.1f}%）')

    return '\n'.join(lines)


# ============ 饼状图生成模块 ============

import matplotlib.pyplot as plt
import numpy as np


def generate_pie_charts(knowledge_data: Dict[str, Any], output_dir: str) -> List[str]:
    """生成三个饼状图"""
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    output_files = []
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']

    subject_file = generate_subject_pie_chart(knowledge_data['subject_distribution'], output_dir, colors)
    if subject_file:
        output_files.append(subject_file)

    cause_file = generate_cause_pie_chart(knowledge_data['error_cause_distribution'], output_dir, colors)
    if cause_file:
        output_files.append(cause_file)

    mastery_file = generate_mastery_pie_chart(knowledge_data['mastery_level_distribution'], output_dir)
    if mastery_file:
        output_files.append(mastery_file)

    return output_files


def generate_subject_pie_chart(data, output_dir, colors):
    if not data:
        return None

    fig, ax = plt.subplots(figsize=(12, 8))
    labels = list(data.keys())
    sizes = list(data.values())
    total = sum(sizes)

    percentages = [f'{s/total*100:.1f}%' for s in sizes]
    legend_labels = [f'{l} ({p})' for l, p in zip(labels, percentages)]

    wedges, texts = ax.pie(sizes, colors=colors[:len(labels)], startangle=90)
    ax.legend(wedges, legend_labels, title='法律科目', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title('法律科目错题分布', fontsize=16, fontweight='bold', pad=20)

    output_path = os.path.join(output_dir, '图1-法律科目错题分布.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return output_path


def generate_cause_pie_chart(data, output_dir, colors):
    if not data:
        return None

    fig, ax = plt.subplots(figsize=(10, 8))
    labels = list(data.keys())
    sizes = list(data.values())
    total = sum(sizes)

    legend_labels = [f'{l}：{s}题' for l, s in zip(labels, sizes)]

    wedges, texts, autotexts = ax.pie(sizes, colors=colors[:len(labels)], startangle=90, wedgeprops=dict(width=0.5))
    ax.text(0, 0, f'总题数\n{total}', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.legend(wedges, legend_labels, title='错误原因', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title('错误原因分布', fontsize=16, fontweight='bold', pad=20)

    output_path = os.path.join(output_dir, '图2-错误原因分布.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return output_path


def generate_mastery_pie_chart(data, output_dir):
    if not data:
        return None

    fig, ax = plt.subplots(figsize=(10, 8))
    mastery_colors = {'薄弱': '#FF4444', '一般': '#FFA500', '需加强': '#44AA44'}
    labels = list(data.keys())
    sizes = list(data.values())
    total = sum(sizes)

    pie_colors = [mastery_colors.get(l, '#888888') for l in labels]
    legend_labels = [f'{l}：{s}题' for l, s in zip(labels, sizes)]

    wedges, texts = ax.pie(sizes, colors=pie_colors, startangle=90, wedgeprops=dict(width=0.5))
    ax.text(0, 0, '掌握\n程度', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.legend(wedges, legend_labels, title='掌握程度', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title('知识点掌握程度分布', fontsize=16, fontweight='bold', pad=20)

    output_path = os.path.join(output_dir, '图3-知识点掌握程度分布.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    return output_path


# ============ 主程序整合模块 ============

def main(pdf_path: str, output_dir: str = './output', use_ocr: bool = False, dpi: int = 300) -> Dict[str, Any]:
    """
    法考错题分析主程序

    参数:
        pdf_path: PDF文件路径
        output_dir: 输出目录路径
        use_ocr: 是否强制使用OCR识别（即使普通提取成功也会使用OCR）
        dpi: OCR图像分辨率（仅当use_ocr=True时有效）
    """
    print(f'开始分析法考错题集：{pdf_path}')
    print(f'时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('-' * 50)

    os.makedirs(output_dir, exist_ok=True)

    print('【步骤1/4】正在解析PDF文件...')

    # 选择提取方法
    if use_ocr:
        print('使用OCR模式进行文本提取...')
        questions = extract_questions_with_ocr(pdf_path, dpi=dpi)
    else:
        # 首先尝试普通文本提取
        questions = extract_questions_from_pdf(pdf_path)

        # 如果普通提取失败，自动尝试OCR
        if not questions:
            print('普通文本提取未获取到内容，自动切换到OCR模式...')
            questions = extract_questions_with_ocr(pdf_path, dpi=dpi)

    print(f'成功提取 {len(questions)} 道错题')

    # 统计OCR来源的题目数量
    ocr_count = sum(1 for q in questions if q.get('ocr_source'))
    if ocr_count > 0:
        print(f'  （其中 {ocr_count} 道通过OCR识别）')

    print('\n【步骤2/4】正在分析知识点...')
    knowledge_data = extract_knowledge_points(questions)
    print(f'涉及 {len(knowledge_data["subject_distribution"])} 个法律科目')

    print('\n【步骤3/4】正在生成Word文档...')
    docx_path = os.path.join(output_dir, '法考错题知识点总结.docx')
    create_summary_document(knowledge_data, docx_path)
    print(f'Word文档已生成：{docx_path}')

    print('\n【步骤4/4】正在生成思维导图和饼状图...')
    mindmap_path = os.path.join(output_dir, '法考错题知识点思维导图.md')
    mindmap_content = generate_mindmap_markdown(knowledge_data)
    with open(mindmap_path, 'w', encoding='utf-8') as f:
        f.write(mindmap_content)
    print(f'思维导图已生成：{mindmap_path}')

    pie_charts = generate_pie_charts(knowledge_data, output_dir)
    print(f'已生成 {len(pie_charts)} 个饼状图')

    print('\n' + '=' * 50)
    print('分析完成！')
    print('=' * 50)

    return {
        'docx': docx_path,
        'mindmap': mindmap_path,
        'pie_charts': pie_charts
    }


if __name__ == '__main__':
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else './output'

        # 检查是否启用OCR
        use_ocr = '--ocr' in sys.argv
        dpi = 300

        # 解析DPI参数
        for arg in sys.argv:
            if arg.startswith('--dpi='):
                try:
                    dpi = int(arg.split('=')[1])
                except ValueError:
                    pass

        results = main(pdf_path, output_dir, use_ocr=use_ocr, dpi=dpi)
    else:
        print('请提供PDF文件路径作为参数')
        print('用法：python law_exam_analyzer.py <pdf_path> [output_dir] [--ocr] [--dpi=300]')
        print('')
        print('参数说明：')
        print('  pdf_path      - PDF文件路径（必填）')
        print('  output_dir    - 输出目录（可选，默认为 ./output）')
        print('  --ocr         - 强制使用OCR识别（可选）')
        print('  --dpi=N       - OCR图像分辨率（可选，默认300）')
        print('')
        print('示例：')
        print('  python law_exam_analyzer.py ./错题集.pdf')
        print('  python law_exam_analyzer.py ./错题集.pdf ./output')
        print('  python law_exam_analyzer.py ./扫描版错题集.pdf --ocr')
        print('  python law_exam_analyzer.py ./扫描版错题集.pdf --ocr --dpi=400')
```
