#!/usr/bin/env python3
"""
Audio Typo Checker - 音频错别字检测工具
检测音频读音与文案不一致的问题：
1. 配音读错字（如"鳌鱼"读成"鲨鱼"）
2. 漏读、多读
3. 文案本身可能的错别字
4. 多音字读音提醒（如"堡"在镇北堡应读bǔ而非bǎo）
版本: v1.3.0
"""
import json
import sys
import re
import os
from difflib import SequenceMatcher

# 尝试导入拼音库
try:
    from pypinyin import pinyin, Style
    HAS_PYPINYIN = True
except ImportError:
    HAS_PYPINYIN = False
    print("提示: 安装 pypinyin 可获得更准确的拼音分析 (pip install pypinyin)")


def normalize_text(text):
    """标准化文本：去除标点、空格，统一格式"""
    # 标点符号正则 - 使用原始字符串避免转义警告
    punctuation_pattern = r'[，。、；：！？""''（）【】《》「」…—·,.:;!?\'\"()\[\]{}<>]'
    text = re.sub(punctuation_pattern, '', text)
    text = re.sub(r'\s+', '', text)
    return text


def get_pinyin(char):
    """获取字符的拼音"""
    if not HAS_PYPINYIN:
        return None
    try:
        py = pinyin(char, style=Style.NORMAL)
        return py[0][0] if py else None
    except:
        return None


def get_pinyin_similarity(char1, char2):
    """
    计算两个字符的拼音相似度
    返回：'same': 同音字, 'similar': 近音字, 'different': 不同音
    """
    if not HAS_PYPINYIN:
        return 'unknown'
    
    py1 = get_pinyin(char1)
    py2 = get_pinyin(char2)
    
    if not py1 or not py2:
        return 'unknown'
    
    if py1 == py2:
        return 'same'
    
    if py1[0] == py2[0]:
        return 'similar'
    
    return 'different'


def analyze_semantic_impact(script_word, audio_word):
    """
    分析语义影响
    返回：'high': 语义变化大, 'medium': 语义有变化, 'low': 语义相近
    """
    if len(script_word) >= 2 and len(audio_word) >= 2:
        common_chars = set(script_word) & set(audio_word)
        if len(common_chars) == 0:
            return 'high'
    
    if len(script_word) == 1 and len(audio_word) == 1:
        pinyin_sim = get_pinyin_similarity(script_word, audio_word)
        if pinyin_sim == 'same':
            return 'low'
        elif pinyin_sim == 'similar':
            return 'medium'
        else:
            return 'high'
    
    return 'medium'


def is_asr_misrecognition(script_word, audio_word):
    """判断是否可能是ASR误识别"""
    asr_patterns = {
        ('栖息', '欺欺'), ('骆驼', '落桶'), ('越野', '约也'),
        ('漂', '飘'), ('劈', '皮'), ('斩', '展'),
        ('牛', '扭'), ('筝', '争'), ('宠', '虫'),
        ('筝腾', '正疼'), ('风筝腾', '风正疼'),
    }
    
    key = (script_word, audio_word)
    if key in asr_patterns:
        return True
    
    if script_word.isdigit() or audio_word.isdigit():
        return True
    
    return False


def compare_texts(script_text, asr_text):
    """对比文案和语音识别结果，找出差异"""
    script_norm = normalize_text(script_text)
    asr_norm = normalize_text(asr_text)
    
    matcher = SequenceMatcher(None, script_norm, asr_norm)
    differences = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            script_part = script_norm[i1:i2]
            asr_part = asr_norm[j1:j2]
            differences.append({
                'type': 'replace', 'script': script_part, 'audio': asr_part,
                'script_pos': i1, 'audio_pos': j1
            })
        elif tag == 'delete':
            script_part = script_norm[i1:i2]
            differences.append({
                'type': 'delete', 'script': script_part, 'audio': '',
                'script_pos': i1, 'audio_pos': -1
            })
        elif tag == 'insert':
            asr_part = asr_norm[j1:j2]
            differences.append({
                'type': 'insert', 'script': '', 'audio': asr_part,
                'script_pos': -1, 'audio_pos': j1
            })
    
    return differences


def analyze_difference(diff, script_text, asr_text):
    """分析差异，判断是配音错误还是ASR误识别"""
    analysis = {
        'type': diff['type'], 'script_part': diff['script'], 'audio_part': diff['audio'],
        'severity': 'medium', 'issue_type': 'unknown', 'suggestion': '',
        'pinyin_similarity': 'unknown', 'semantic_impact': 'unknown', 'is_asr_error': False
    }
    
    if diff['type'] == 'replace':
        script_word = diff['script']
        audio_word = diff['audio']
        
        if is_asr_misrecognition(script_word, audio_word):
            analysis['is_asr_error'] = True
            analysis['issue_type'] = 'asr_error'
            analysis['severity'] = 'low'
            analysis['suggestion'] = f'可能是ASR误识别："{script_word}" → "{audio_word}"（音频可能读对了）'
        else:
            if len(script_word) == 1 and len(audio_word) == 1:
                analysis['pinyin_similarity'] = get_pinyin_similarity(script_word, audio_word)
            
            analysis['semantic_impact'] = analyze_semantic_impact(script_word, audio_word)
            
            if analysis['semantic_impact'] == 'high':
                analysis['issue_type'] = 'dubbing_error'
                analysis['severity'] = 'high'
                analysis['suggestion'] = f'❌ 配音错误："{script_word}" 读成了 "{audio_word}"（语义变化大）'
            elif analysis['semantic_impact'] == 'medium':
                analysis['issue_type'] = 'dubbing_error'
                analysis['severity'] = 'medium'
                analysis['suggestion'] = f'⚠️ 配音差异："{script_word}" 读成了 "{audio_word}"（语义有变化）'
            else:
                analysis['issue_type'] = 'pronunciation_diff'
                analysis['severity'] = 'low'
                analysis['suggestion'] = f'ℹ️ 发音差异："{script_word}" 读成了 "{audio_word}"（同音字，语义相近）'
        
    elif diff['type'] == 'delete':
        analysis['issue_type'] = 'audio_missing'
        analysis['severity'] = 'high'
        analysis['suggestion'] = f'配音漏读了 "{diff["script"]}"'
        
    elif diff['type'] == 'insert':
        analysis['issue_type'] = 'audio_extra'
        analysis['severity'] = 'medium'
        analysis['suggestion'] = f'配音多读了 "{diff["audio"]}"'
    
    return analysis


def check_script_typos(text):
    """检测文案本身可能的错别字"""
    common_typos = {'必需': '必须', '己经': '已经', '帐号': '账号', '登陆': '登录'}
    issues = []
    for wrong, correct in common_typos.items():
        if wrong in text:
            issues.append({
                'type': 'script_typo', 'wrong': wrong, 'correct': correct,
                'severity': 'low', 'suggestion': f'"{wrong}"是否应为"{correct}"？'
            })
    return issues


# 多音字词库
POLYPHONIC_WORDS = {
    '镇北堡': {'char': '堡', 'correct': 'bǔ', 'wrong': 'bǎo', 'note': '地名读bǔ'},
    '瓦窑堡': {'char': '堡', 'correct': 'bǔ', 'wrong': 'bǎo', 'note': '地名读bǔ'},
    '吴堡': {'char': '堡', 'correct': 'bǔ', 'wrong': 'bǎo', 'note': '地名读bǔ'},
    '堡垒': {'char': '堡', 'correct': 'bǎo', 'wrong': 'bǔ', 'note': '军事设施读bǎo'},
    '城堡': {'char': '堡', 'correct': 'bǎo', 'wrong': 'bǔ', 'note': '读bǎo'},
    '更正': {'char': '更', 'correct': 'gēng', 'wrong': 'gèng', 'note': '改正读gēng'},
    '更改': {'char': '更', 'correct': 'gēng', 'wrong': 'gèng', 'note': '改变读gēng'},
    '更新': {'char': '更', 'correct': 'gēng', 'wrong': 'gèng', 'note': '更新读gēng'},
    '更加': {'char': '更', 'correct': 'gèng', 'wrong': 'gēng', 'note': '程度读gèng'},
    '更好': {'char': '更', 'correct': 'gèng', 'wrong': 'gēng', 'note': '程度读gèng'},
    '流血': {'char': '血', 'correct': 'xuè', 'wrong': 'xiě', 'note': '书面语读xuè'},
    '鲜血': {'char': '血', 'correct': 'xuè', 'wrong': 'xiě', 'note': '书面语读xuè'},
    '贫血': {'char': '血', 'correct': 'xuè', 'wrong': 'xiě', 'note': '书面语读xuè'},
    '削弱': {'char': '削', 'correct': 'xuē', 'wrong': 'xiāo', 'note': '书面语读xuē'},
    '剥削': {'char': '削', 'correct': 'xuē', 'wrong': 'xiāo', 'note': '书面语读xuē'},
    '贝壳': {'char': '壳', 'correct': 'ké', 'wrong': 'qiào', 'note': '口语读ké'},
    '蛋壳': {'char': '壳', 'correct': 'ké', 'wrong': 'qiào', 'note': '口语读ké'},
    '地壳': {'char': '壳', 'correct': 'qiào', 'wrong': 'ké', 'note': '地质学读qiào'},
    '薄弱': {'char': '薄', 'correct': 'bó', 'wrong': 'báo', 'note': '书面语读bó'},
    '单薄': {'char': '薄', 'correct': 'bó', 'wrong': 'báo', 'note': '书面语读bó'},
    '薄荷': {'char': '薄', 'correct': 'bò', 'wrong': 'báo', 'note': '植物读bò'},
    '角色': {'char': '角', 'correct': 'jué', 'wrong': 'jiǎo', 'note': '演员读jué'},
    '主角': {'char': '角', 'correct': 'jué', 'wrong': 'jiǎo', 'note': '演员读jué'},
    '给予': {'char': '给', 'correct': 'jǐ', 'wrong': 'gěi', 'note': '书面语读jǐ'},
    '记载': {'char': '载', 'correct': 'zǎi', 'wrong': 'zài', 'note': '记录读zǎi'},
    '转载': {'char': '载', 'correct': 'zǎi', 'wrong': 'zài', 'note': '记录读zǎi'},
    '载体': {'char': '载', 'correct': 'zài', 'wrong': 'zǎi', 'note': '承载读zài'},
    '模型': {'char': '模', 'correct': 'mó', 'wrong': 'mú', 'note': '规范读mó'},
    '模式': {'char': '模', 'correct': 'mó', 'wrong': 'mú', 'note': '规范读mó'},
    '模样': {'char': '模', 'correct': 'mú', 'wrong': 'mó', 'note': '样子读mú'},
    '处理': {'char': '处', 'correct': 'chǔ', 'wrong': 'chù', 'note': '动词读chǔ'},
    '强迫': {'char': '强', 'correct': 'qiǎng', 'wrong': 'qiáng', 'note': '勉强读qiǎng'},
    '厦门': {'char': '厦', 'correct': 'xià', 'wrong': 'shà', 'note': '地名读xià'},
    '参加': {'char': '参', 'correct': 'cān', 'wrong': 'shēn', 'note': '动词读cān'},
    '人参': {'char': '参', 'correct': 'shēn', 'wrong': 'cān', 'note': '植物读shēn'},
    '关系': {'char': '系', 'correct': 'xì', 'wrong': 'jì', 'note': '名词读xì'},
    '系鞋带': {'char': '系', 'correct': 'jì', 'wrong': 'xì', 'note': '动词读jì'},
    '省份': {'char': '省', 'correct': 'shěng', 'wrong': 'xǐng', 'note': '行政读shěng'},
    '反省': {'char': '省', 'correct': 'xǐng', 'wrong': 'shěng', 'note': '检查读xǐng'},
    '快乐': {'char': '乐', 'correct': 'lè', 'wrong': 'yuè', 'note': '情绪读lè'},
    '音乐': {'char': '乐', 'correct': 'yuè', 'wrong': 'lè', 'note': '艺术读yuè'},
}


def check_polyphonic_words(text):
    """检测文案中的多音字"""
    warnings = []
    for word, info in POLYPHONIC_WORDS.items():
        if word in text:
            warnings.append({
                'type': 'polyphonic_warning', 'word': word, 'char': info['char'],
                'correct': info['correct'], 'wrong': info['wrong'], 'note': info['note'],
                'severity': 'info',
                'suggestion': f'"{word}"中的"{info["char"]}"应读{info["correct"]}，易误读为{info["wrong"]}。{info["note"]}'
            })
    return warnings


def generate_report(script_text, asr_text, differences, script_issues, polyphonic_warnings=None):
    """生成检测报告"""
    report_lines = []
    report_lines.append("📝 错别字检测报告")
    report_lines.append("=" * 60)
    report_lines.append(f"\n文案字数：{len(normalize_text(script_text))}")
    report_lines.append(f"识别字数：{len(normalize_text(asr_text))}")
    
    dubbing_errors = [d for d in differences if d.get('issue_type') == 'dubbing_error']
    pronunciation_diffs = [d for d in differences if d.get('issue_type') == 'pronunciation_diff']
    asr_errors = [d for d in differences if d.get('is_asr_error')]
    
    report_lines.append(f"\n检测结果：")
    report_lines.append(f"  配音错误：{len(dubbing_errors)} 处")
    report_lines.append(f"  发音差异：{len(pronunciation_diffs)} 处")
    report_lines.append(f"  ASR误识别：{len(asr_errors)} 处（可忽略）")
    if polyphonic_warnings:
        report_lines.append(f"  多音字提醒：{len(polyphonic_warnings)} 处")
    report_lines.append("")
    
    if dubbing_errors:
        report_lines.append("【配音错误 - 需要重新配音】")
        report_lines.append("━" * 60)
        for err in dubbing_errors:
            report_lines.append(f"\n{err['suggestion']}")
            if err['script_part']:
                report_lines.append(f"   文案：{err['script_part']}")
            if err['audio_part']:
                report_lines.append(f"   音频：{err['audio_part']}")
    
    if pronunciation_diffs:
        report_lines.append("\n【发音差异 - 需人工确认】")
        report_lines.append("━" * 60)
        for err in pronunciation_diffs:
            report_lines.append(f"\n{err['suggestion']}")
    
    if asr_errors:
        report_lines.append("\n【ASR误识别 - 可忽略】")
        report_lines.append("━" * 60)
        for err in asr_errors:
            report_lines.append(f"\n{err['suggestion']}")
    
    if script_issues:
        report_lines.append("\n【文案疑似错别字】")
        report_lines.append("━" * 60)
        for issue in script_issues:
            report_lines.append(f"\n⚠️ {issue['suggestion']}")
    
    if polyphonic_warnings:
        report_lines.append("\n【多音字读音提醒 - 请注意正确读音】")
        report_lines.append("━" * 60)
        for warning in polyphonic_warnings:
            report_lines.append(f"\n🔔 {warning['suggestion']}")
    
    report_lines.append("\n" + "=" * 60)
    return '\n'.join(report_lines)


def check_audio_typo(script_text, asr_text, output_format='markdown'):
    """主函数：检测音频错别字"""
    differences = compare_texts(script_text, asr_text)
    
    analyzed_diffs = []
    for diff in differences:
        analysis = analyze_difference(diff, script_text, asr_text)
        analyzed_diffs.append(analysis)
    
    script_issues = check_script_typos(script_text)
    polyphonic_warnings = check_polyphonic_words(script_text)
    
    if output_format == 'json':
        result = {
            'script_text': script_text, 'asr_text': asr_text,
            'script_norm': normalize_text(script_text), 'asr_norm': normalize_text(asr_text),
            'differences': analyzed_diffs, 'script_issues': script_issues,
            'polyphonic_warnings': polyphonic_warnings,
            'summary': {
                'dubbing_errors': len([d for d in analyzed_diffs if d.get('issue_type') == 'dubbing_error']),
                'pronunciation_diffs': len([d for d in analyzed_diffs if d.get('issue_type') == 'pronunciation_diff']),
                'asr_errors': len([d for d in analyzed_diffs if d.get('is_asr_error')]),
                'script_errors': len(script_issues),
            }
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return generate_report(script_text, asr_text, analyzed_diffs, script_issues, polyphonic_warnings)


def generate_marked_document(script_text, dubbing_errors, output_path, original_filename=None, 
                             script_paragraphs=None, polyphonic_warnings=None):
    """生成标注红色的Word文档（保留原文标点和段落格式）"""
    try:
        from docx import Document
        from docx.shared import RGBColor
        from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
    except ImportError:
        print("错误: 需要安装 python-docx 库 (pip install python-docx)")
        return None
    
    doc = Document()
    
    # 标题
    title = doc.add_heading('配音文案校对结果', level=1)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    doc.add_paragraph(f'检测到 {len(dubbing_errors)} 处配音错误，已用红色加粗标注')
    doc.add_paragraph('建议重新配音红色标注的部分')
    doc.add_paragraph()
    
    doc.add_paragraph().add_run('配音文案：').bold = True
    
    def mark_text_with_context(text, errors):
        """将文本中需要标红的部分标记出来"""
        marks = []
        for err in errors:
            context = err.get('context', '')
            err_text = err['text']
            
            if not context:
                idx = 0
                while True:
                    pos = text.find(err_text, idx)
                    if pos < 0:
                        break
                    marks.append({'start': pos, 'end': pos + len(err_text), 'text': err_text})
                    idx = pos + 1
            else:
                idx = 0
                while True:
                    pos = text.find(context, idx)
                    if pos < 0:
                        break
                    char_pos = context.find(err_text)
                    if char_pos >= 0:
                        marks.append({'start': pos + char_pos, 'end': pos + char_pos + 1, 'text': err_text})
                    idx = pos + 1
        
        marks.sort(key=lambda x: x['start'])
        
        result = []
        last_end = 0
        for mark in marks:
            if mark['start'] >= last_end:
                if mark['start'] > last_end:
                    result.append((text[last_end:mark['start']], False))
                result.append((mark['text'], True))
                last_end = mark['end']
        
        if last_end < len(text):
            result.append((text[last_end:], False))
        
        return result
    
    # 标注文案
    if script_paragraphs:
        for para_lines in script_paragraphs:
            para = doc.add_paragraph()
            for line_idx, line in enumerate(para_lines):
                if line_idx > 0:
                    para.add_run('\n')
                parts = mark_text_with_context(line, dubbing_errors)
                for text, is_red in parts:
                    if is_red:
                        red_run = para.add_run(text)
                        red_run.font.color.rgb = RGBColor(255, 0, 0)
                        red_run.font.bold = True
                    else:
                        para.add_run(text)
    else:
        para = doc.add_paragraph()
        parts = mark_text_with_context(script_text, dubbing_errors)
        for text, is_red in parts:
            if is_red:
                red_run = para.add_run(text)
                red_run.font.color.rgb = RGBColor(255, 0, 0)
                red_run.font.bold = True
            else:
                para.add_run(text)
    
    # 错误列表
    doc.add_paragraph()
    doc.add_heading('配音错误详情', level=2)
    for i, err in enumerate(dubbing_errors, 1):
        p = doc.add_paragraph()
        p.add_run(f'{i}. ')
        red_run = p.add_run(f'"{err["text"]}"')
        red_run.font.color.rgb = RGBColor(255, 0, 0)
        red_run.font.bold = True
        p.add_run(f' 读成了 ')
        p.add_run(f'"{err["audio"]}"')
        if err.get('pinyin'):
            p.add_run(f'（拼音：{err["pinyin"]}）')
    
    # 多音字提醒
    if polyphonic_warnings:
        doc.add_paragraph()
        doc.add_heading('多音字读音提醒', level=2)
        for i, warning in enumerate(polyphonic_warnings, 1):
            p = doc.add_paragraph()
            p.add_run(f'{i}. ')
            p.add_run(f'"{warning["word"]}"')
            p.add_run(f' 中的 "')
            blue_run = p.add_run(warning['char'])
            blue_run.font.color.rgb = RGBColor(0, 102, 204)
            blue_run.font.bold = True
            p.add_run(f'" 应读 ')
            correct_run = p.add_run(warning['correct'])
            correct_run.font.bold = True
            p.add_run(f'（易误读为 {warning["wrong"]}）')
            p.add_run(f'\n   📌 {warning["note"]}')
    
    doc.save(output_path)
    return output_path


def check_and_generate_marked_doc(script_text, asr_text, output_dir='.', original_filename=None, script_paragraphs=None):
    """检测配音错误并生成标注红色的Word文档"""
    script_norm = normalize_text(script_text)
    asr_norm = normalize_text(asr_text)
    
    differences = compare_texts(script_text, asr_text)
    
    dubbing_errors = []
    for diff in differences:
        analysis = analyze_difference(diff, script_text, asr_text)
        if analysis.get('issue_type') == 'dubbing_error':
            py_str = None
            if HAS_PYPINYIN:
                try:
                    py_script = pinyin(diff['script'], style=Style.TONE)
                    py_audio = pinyin(diff['audio'], style=Style.TONE)
                    py_str = f"{''.join([p[0] for p in py_script])} → {''.join([p[0] for p in py_audio])}"
                except:
                    pass
            
            context = None
            err_text = diff['script']
            norm_pos = diff.get('script_pos', 0)
            
            if norm_pos >= 0 and norm_pos < len(script_norm):
                start = max(0, norm_pos - 2)
                end = min(len(script_norm), norm_pos + len(err_text) + 2)
                context_norm = script_norm[start:end]
                context = find_context_in_original(script_text, script_norm, context_norm, err_text)
            
            dubbing_errors.append({
                'text': diff['script'], 'audio': diff['audio'], 'pinyin': py_str, 'context': context
            })
    
    polyphonic_warnings = check_polyphonic_words(script_text)
    report = check_audio_typo(script_text, asr_text)
    
    output_path = None
    if dubbing_errors or polyphonic_warnings:
        if original_filename:
            base = os.path.splitext(original_filename)[0]
            output_name = base + '（有读错需修改，已标红）.docx'
        else:
            output_name = '配音文案（有读错需修改，已标红）.docx'
        
        output_path = os.path.join(output_dir, output_name)
        generate_marked_document(script_text, dubbing_errors, output_path, original_filename, 
                                 script_paragraphs, polyphonic_warnings)
    
    return report, output_path


def find_context_in_original(original_text, norm_text, context_norm, err_text):
    """在原文中找到上下文"""
    norm_pos = norm_text.find(context_norm)
    if norm_pos < 0:
        return None
    
    err_pos_in_context = context_norm.find(err_text)
    if err_pos_in_context < 0:
        return None
    
    norm_to_orig = {}
    norm_idx = 0
    
    for i, char in enumerate(original_text):
        if char in '，。、；：！？""''（）【】《》「」…—·,.:;!?\'\"()\\[\\]{}<> \n\t':
            continue
        else:
            norm_to_orig[norm_idx] = i
            norm_idx += 1
    
    start_norm = norm_pos
    end_norm = norm_pos + len(context_norm)
    
    if start_norm in norm_to_orig and end_norm - 1 in norm_to_orig:
        start_orig = norm_to_orig[start_norm]
        end_orig = norm_to_orig[end_norm - 1] + 1
        return original_text[start_orig:end_orig]
    
    return None


def extract_paragraphs_from_docx(docx_path, voice_prefix='配音：'):
    """从DOCX文件中提取配音段落"""
    try:
        from docx import Document
    except ImportError:
        return None
    
    doc = Document(docx_path)
    voice_paragraphs = []
    current_para = []
    
    for para in doc.paragraphs:
        text = para.text
        if text.startswith(voice_prefix):
            if current_para:
                voice_paragraphs.append(current_para)
            current_para = [text.replace(voice_prefix, '')]
        elif current_para and text.strip():
            if not any(text.startswith(prefix) for prefix in ['【', '时间码', '画面', '镜头', '---', '===']):
                current_para.append(text)
    
    if current_para:
        voice_paragraphs.append(current_para)
    
    return voice_paragraphs


def check_and_generate_marked_doc_from_files(script_file, asr_file, output_dir='.', use_paragraphs=True):
    """从文件检测配音错误并生成标注红色的Word文档"""
    import os
    
    script_paragraphs = None
    if script_file.endswith('.docx'):
        from docx import Document
        doc = Document(script_file)
        
        if use_paragraphs:
            script_paragraphs = extract_paragraphs_from_docx(script_file)
        
        script_lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text.startswith('配音：'):
                script_lines.append(text.replace('配音：', ''))
            elif script_lines and text and not text.startswith('【') and not text.startswith('时间码') and not text.startswith('画面') and not text.startswith('镜头'):
                script_lines.append(text)
        script_text = ''.join(script_lines)
    else:
        with open(script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()
    
    with open(asr_file, 'r', encoding='utf-8') as f:
        asr_lines = f.readlines()
    asr_text = ''.join([line.split(']')[1].strip() if ']' in line else line.strip() for line in asr_lines])
    
    original_filename = os.path.basename(script_file)
    
    return check_and_generate_marked_doc(
        script_text=script_text, asr_text=asr_text,
        output_dir=output_dir, original_filename=original_filename,
        script_paragraphs=script_paragraphs
    )


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python check_typo.py <文案文件> <ASR结果文件> [输出目录]")
        sys.exit(1)
    
    script_file = sys.argv[1]
    asr_file = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else '.'
    
    with open(script_file, 'r', encoding='utf-8') as f:
        script_text = f.read()
    
    with open(asr_file, 'r', encoding='utf-8') as f:
        asr_text = f.read()
    
    report = check_audio_typo(script_text, asr_text)
    print(report)
    
    try:
        from docx import Document
        from docx.shared import RGBColor
        
        differences = compare_texts(script_text, asr_text)
        dubbing_errors = []
        for diff in differences:
            analysis = analyze_difference(diff, script_text, asr_text)
            if analysis.get('issue_type') == 'dubbing_error':
                dubbing_errors.append({
                    'text': diff['script'], 'audio': diff['audio'], 'start_pos': diff.get('script_pos', 0)
                })
        
        if dubbing_errors:
            doc = Document()
            doc.add_heading('配音文案校对结果', level=1)
            doc.add_paragraph(f'检测到 {len(dubbing_errors)} 处配音错误，已用红色标注')
            doc.add_paragraph()
            
            script_norm = normalize_text(script_text)
            para = doc.add_paragraph()
            
            last_pos = 0
            for err in sorted(dubbing_errors, key=lambda x: x.get('start_pos', 0)):
                err_text = err['text']
                pos = script_norm.find(err_text, last_pos)
                if pos >= 0:
                    if pos > last_pos:
                        para.add_run(script_norm[last_pos:pos])
                    red_run = para.add_run(err_text)
                    red_run.font.color.rgb = RGBColor(255, 0, 0)
                    red_run.font.bold = True
                    last_pos = pos + len(err_text)
            
            if last_pos < len(script_norm):
                para.add_run(script_norm[last_pos:])
            
            doc.add_paragraph()
            doc.add_heading('配音错误列表', level=2)
            for i, err in enumerate(dubbing_errors, 1):
                p = doc.add_paragraph()
                red_run = p.add_run(f'{i}. "{err["text"]}"')
                red_run.font.color.rgb = RGBColor(255, 0, 0)
                p.add_run(f' 读成了 "{err["audio"]}"')
            
            import os
            script_basename = os.path.basename(script_file)
            if script_basename.endswith('.txt'):
                output_name = script_basename[:-4] + '（有读错需修改，已标红）.docx'
            elif script_basename.endswith('.docx'):
                output_name = script_basename[:-5] + '（有读错需修改，已标红）.docx'
            else:
                output_name = script_basename + '（有读错需修改，已标红）.docx'
            
            output_path = os.path.join(output_dir, output_name)
            doc.save(output_path)
            print(f"\n✓ 已生成标注文档: {output_path}")
        else:
            print("\n✓ 未检测到配音错误，无需生成标注文档")
            
    except ImportError:
        print("\n提示: 安装 python-docx 可生成标注红色的Word文档 (pip install python-docx)")