#!/usr/bin/env python3
"""
Word 公文智能格式化工具
自动识别文档类型并应用统一格式
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import re
import sys
import os


class DocumentFormatter:
    """文档格式化器"""
    
    def __init__(self):
        self.chinese_font = 'Microsoft YaHei'
        self.english_font = 'Arial'
        
    def format(self, input_file, output_file, doc_type=None):
        """格式化文档"""
        if not os.path.exists(input_file):
            print(f"错误: 文件不存在 - {input_file}")
            sys.exit(1)
        
        doc = Document(input_file)
        
        # 自动识别文档类型
        if not doc_type:
            doc_type = self._identify_doc_type(doc)
        
        print(f"文档类型: {doc_type}")
        
        # 根据类型格式化
        if doc_type == 'petition':
            self._format_petition(doc)
        elif doc_type == 'quotation':
            self._format_quotation(doc)
        elif doc_type == 'price_list':
            self._format_price_list(doc)
        else:
            self._format_general(doc)
        
        doc.save(output_file)
        print(f"✓ 已保存: {output_file}")
    
    def _identify_doc_type(self, doc):
        """识别文档类型"""
        text_all = ' '.join([p.text for p in doc.paragraphs])
        
        if any(kw in text_all for kw in ['请示', '批示', '妥否']):
            return 'petition'
        elif any(kw in text_all for kw in ['报价函', '询价', '控制价']):
            return 'quotation'
        elif any(kw in text_all for kw in ['报价单', '清单', '序号']):
            return 'price_list'
        else:
            return 'general'
    
    def _format_petition(self, doc):
        """格式化请示类文档"""
        paragraphs = list(doc.paragraphs)
        
        for i, para in enumerate(paragraphs):
            text = para.text.strip()
            if not text:
                continue
            
            # 标题
            if i == 0 or ('关于' in text and len(text) < 40):
                self._apply_style(para, 'heading1', align='center')
            
            # 收件单位
            elif re.match(r'^[\u4e00-\u9fa5]{2,10}：$', text):
                self._apply_style(para, 'heading2', align='left', indent=False)
            
            # 结尾语
            elif text in ['妥否，请批示。', '特此请示。']:
                self._apply_style(para, 'normal', indent=True)
            
            # 附件
            elif text.startswith('附件：'):
                self._apply_style(para, 'normal', align='left', indent=False)
            
            # 日期
            elif re.match(r'^\d{4}年\d{1,2}月\d{1,2}日$', text):
                self._apply_style(para, 'normal', align='right')
            
            # 经办人
            elif '经办人' in text or '联系方式' in text:
                self._apply_style(para, 'normal', align='right', font_size=10)
            
            # 正文
            else:
                self._apply_style(para, 'normal', indent=True)
    
    def _format_quotation(self, doc):
        """格式化报价函"""
        paragraphs = list(doc.paragraphs)
        
        for i, para in enumerate(paragraphs):
            text = para.text.strip()
            if not text:
                continue
            
            # 标题
            if i == 0 or ('报价函' in text and len(text) < 30):
                self._apply_style(para, 'heading1', align='center')
            
            # 章节标题
            elif re.match(r'^[一二三四五六七八九十]+、', text) or \
                 re.match(r'^\d+[、\.]\s*[\u4e00-\u9fa5]', text):
                self._apply_style(para, 'heading2', indent=True)
            
            # 落款单位
            elif '沈阳桃仙国际机场' in text or '信息技术中心' in text:
                self._apply_style(para, 'normal', align='right', bold=True)
            
            # 日期
            elif re.match(r'^\d{4}年', text):
                self._apply_style(para, 'normal', align='right')
            
            # 关键信息
            elif any(kw in text for kw in ['控制价', '联系电话', '联系人']):
                self._apply_style(para, 'normal', indent=True, bold=True, 
                                 color=RGBColor(0, 0, 128))
            
            # 正文
            else:
                self._apply_style(para, 'normal', indent=True)
    
    def _format_price_list(self, doc):
        """格式化报价清单（重点：重建表格）"""
        paragraphs = list(doc.paragraphs)
        
        # 简单处理：将文本转换为规范段落
        for i, para in enumerate(paragraphs):
            text = para.text.strip()
            if not text:
                continue
            
            # 标题
            if i == 0 or '报价单' in text:
                self._apply_style(para, 'heading1', align='center')
            
            # 表格内容（简化处理，实际应重建表格）
            elif re.match(r'^\d+$', text) or text in ['序号', 'A', 'B', 'C']:
                self._apply_style(para, 'table_content', align='center')
            
            # 备注
            elif text == '备注' or re.match(r'^\d+\.', text):
                self._apply_style(para, 'normal', indent=True)
            
            # 签名区
            elif any(kw in text for kw in ['供货商', '联系方式', '报价日期']):
                self._apply_style(para, 'normal', align='left')
            
            else:
                self._apply_style(para, 'normal', indent=True)
        
        # TODO: 高级功能 - 重建表格
        print("提示：复杂表格建议手动调整或使用高级脚本")
    
    def _format_general(self, doc):
        """通用格式化"""
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            
            # 简单标题检测
            if i == 0 or (len(text) < 30 and not text.endswith(('。', '！', '？'))):
                self._apply_style(para, 'heading2', indent=True)
            else:
                self._apply_style(para, 'normal', indent=True)
    
    def _apply_style(self, paragraph, style_type, align='justify', 
                     indent=False, bold=False, font_size=None, color=None):
        """应用样式"""
        # 字号映射
        size_map = {
            'heading1': 22,
            'heading2': 16,
            'normal': 12,
            'table_content': 10.5,
        }
        
        size = font_size or size_map.get(style_type, 12)
        
        # 设置字体
        for run in paragraph.runs:
            run.font.name = self.chinese_font
            run.font.size = Pt(size)
            run.font.bold = bold
            if color:
                run.font.color.rgb = color
            run._element.rPr.rFonts.set(qn('w:eastAsia'), self.chinese_font)
        
        # 对齐方式
        align_map = {
            'center': WD_ALIGN_PARAGRAPH.CENTER,
            'left': WD_ALIGN_PARAGRAPH.LEFT,
            'right': WD_ALIGN_PARAGRAPH.RIGHT,
            'justify': WD_ALIGN_PARAGRAPH.JUSTIFY,
        }
        paragraph.alignment = align_map.get(align, WD_ALIGN_PARAGRAPH.JUSTIFY)
        
        # 段落格式
        pf = paragraph.paragraph_format
        pf.line_spacing = 1.5
        
        if indent:
            pf.first_line_indent = Pt(24)
        
        # 段前段后间距
        if style_type == 'heading1':
            pf.space_before = Pt(18)
            pf.space_after = Pt(12)
        elif style_type == 'heading2':
            pf.space_before = Pt(12)
            pf.space_after = Pt(6)


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("=" * 60)
        print("Word 公文智能格式化工具")
        print("=" * 60)
        print("\n用法: python format_doc.py input.docx output.docx [doc_type]")
        print("\n文档类型:")
        print("  petition    - 请示/报告类文档")
        print("  quotation   - 报价函/询价函")
        print("  price_list  - 报价单/清单")
        print("  general     - 通用文档（默认，自动识别）")
        print("\n示例:")
        print("  python format_doc.py 原文档.docx 格式化后.docx")
        print("  python format_doc.py 原文档.docx 格式化后.docx petition")
        print("=" * 60)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    doc_type = sys.argv[3] if len(sys.argv) > 3 else None
    
    formatter = DocumentFormatter()
    formatter.format(input_file, output_file, doc_type)


if __name__ == '__main__':
    main()
