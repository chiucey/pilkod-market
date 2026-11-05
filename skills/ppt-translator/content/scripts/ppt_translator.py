#!/usr/bin/env python3
"""
PPT Translator - 翻译PowerPoint文件并保持原有格式和主题

功能：
- 读取PPT文件的所有幻灯片
- 翻译文本内容到目标语言
- 智能调整字体大小
- 保持原有背景主题和设计元素
"""

import os
import sys
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

try:
    from pptx import Presentation
    from pptx.util import Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
except ImportError:
    print("错误：需要安装 python-pptx 库")
    print("请运行: pip install python-pptx")
    sys.exit(1)


@dataclass
class TextStyle:
    """文本样式数据类"""
    font_name: str = "Arial"
    font_size: float = 18.0
    bold: bool = False
    italic: bool = False
    color: Optional[Tuple[int, int, int]] = None
    alignment: str = "LEFT"


@dataclass
class TextElement:
    """文本元素数据类"""
    text: str
    style: TextStyle
    left: float
    top: float
    width: float
    height: float


class PptTranslator:
    """PPT翻译器类"""

    def __init__(self, file_path: str, target_lang: str = "en", source_lang: str = "zh-cn"):
        """
        初始化翻译器

        Args:
            file_path: PPT文件路径
            target_lang: 目标语言代码 (如 'en', 'zh-cn', 'ja', 'ko', 'es', 'fr', 'de')
            source_lang: 源语言代码
        """
        self.file_path = file_path
        self.target_lang = target_lang
        self.source_lang = source_lang
        self.prs = None
        self._language_names = {
            'zh-cn': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'en': 'English',
            'ja': 'Japanese',
            'ko': 'Korean',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ar': 'Arabic'
        }
        # 语言后缀映射（用于生成输出文件名）
        self._lang_suffixes = {
            'zh-cn': '中文',
            'zh-tw': '繁体中文',
            'en': '英文',
            'ja': '日文',
            'ko': '韩文',
            'es': '西班牙文',
            'fr': '法文',
            'de': '德文',
            'it': '意大利文',
            'pt': '葡萄牙文',
            'ru': '俄文',
            'ar': '阿拉伯文'
        }

    def load_presentation(self) -> bool:
        """加载PPT文件"""
        try:
            self.prs = Presentation(self.file_path)
            return True
        except Exception as e:
            print(f"加载PPT文件失败: {e}")
            return False

    def translate_text(self, text: str) -> str:
        """
        翻译文本（需要集成翻译API）

        当前为占位实现，实际使用时需要接入：
        - Google Translate API
        - Azure Translator
        - DeepL API
        - 或使用开源库如 googletrans, deep-translator

        Args:
            text: 待翻译文本

        Returns:
            翻译后的文本
        """
        # 尝试使用 googletrans 库
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src=self.source_lang, dest=self._get_lang_code(self.target_lang))
            return result.text
        except ImportError:
            print("提示: 请安装 googletrans 库进行实际翻译")
            print(f"运行: pip install googletrans==4.0.0-rc1")
            return f"[翻译内容] {text}"
        except Exception as e:
            print(f"翻译API调用失败: {e}")
            return f"[翻译内容] {text}"

    def _get_lang_code(self, lang: str) -> str:
        """获取Google Translate语言代码"""
        lang_map = {
            'zh-cn': 'zh-cn',
            'zh-tw': 'zh-tw',
            'zh': 'zh-cn',
            'ja': 'ja',
            'ko': 'ko',
            'es': 'es',
            'fr': 'fr',
            'de': 'de',
            'it': 'it',
            'pt': 'pt',
            'ru': 'ru',
            'ar': 'ar',
            'en': 'en'
        }
        return lang_map.get(lang.lower(), 'en')

    def _calculate_font_size(self, original_text: str, translated_text: str,
                            original_size: float, max_size: float = 72.0,
                            min_size: float = 8.0) -> float:
        """
        智能计算调整后的字体大小

        Args:
            original_text: 原始文本
            translated_text: 翻译后文本
            original_size: 原始字体大小
            max_size: 最大字体限制
            min_size: 最小字体限制

        Returns:
            调整后的字体大小
        """
        if not original_text or not translated_text:
            return original_size

        # 计算长度比例（中文通常比英文短，翻译后可能变长）
        original_len = len(original_text)
        translated_len = len(translated_text)

        if original_len == 0:
            return original_size

        # 根据字符数比例调整
        length_ratio = translated_len / original_len

        # 中文/日文/韩文每个字符约等于2个英文字符的宽度
        is_cjk_target = any('\u4e00' <= c <= '\u9fff' or '\u3040' <= c <= '\u309f'
                           or '\u30a0' <= c <= '\u30ff' or '\uac00' <= c <= '\ud7af'
                           for c in translated_text)

        if is_cjk_target:
            # 目标语言是CJK语言，根据长度比调整
            if length_ratio > 1.5:
                new_size = original_size / (length_ratio * 0.8)
            elif length_ratio < 0.7:
                new_size = original_size * 1.2
            else:
                new_size = original_size
        else:
            # 目标语言是拉丁语系，保持原大小
            new_size = original_size

        # 确保在合理范围内
        return max(min_size, min(max_size, new_size))

    def _get_output_filename(self) -> str:
        """
        生成输出文件名（与原文件位置保持一致）

        文件命名规则：原文件名 + 目标语言名称
        输出位置：与原文件相同目录
        例如：
        - /path/to/上海复动医疗公司介绍.pptx → /path/to/上海复动医疗公司介绍英文.pptx
        - /path/to/产品手册.pptx → /path/to/产品手册日文.pptx

        Returns:
            输出文件完整路径
        """
        # 获取文件所在目录
        file_dir = os.path.dirname(self.file_path)
        if not file_dir:
            file_dir = '.'

        # 获取文件名（不含扩展名）
        base_name = os.path.basename(self.file_path)
        base_name_no_ext = os.path.splitext(base_name)[0]
        ext = os.path.splitext(base_name)[1]

        # 获取目标语言后缀
        lang_suffix = self._lang_suffixes.get(self.target_lang, self.target_lang)

        # 组合新文件名（保持与原文件相同目录）
        new_filename = f"{base_name_no_ext}{lang_suffix}{ext}"

        return os.path.join(file_dir, new_filename)

    def translate_presentation(self, output_path: str = None) -> bool:
        """
        翻译整个演示文稿

        Args:
            output_path: 输出文件路径，如果为None则自动生成

        Returns:
            是否成功
        """
        if not self.prs:
            if not self.load_presentation():
                return False

        if output_path is None:
            # 自动生成输出文件名：原文件名 + 目标语言名称
            output_path = self._get_output_filename()

        total_slides = len(self.prs.slides)

        for slide_idx, slide in enumerate(self.prs.slides, 1):
            print(f"正在处理幻灯片 {slide_idx}/{total_slides}...")

            for shape in slide.shapes:
                if shape.has_text_frame:
                    self._translate_shape_text(shape)

        # 保存翻译后的文件
        try:
            self.prs.save(output_path)
            print(f"\n翻译完成！文件已保存至: {output_path}")
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False

    def _translate_shape_text(self, shape):
        """翻译单个形状的文本内容"""
        text_frame = shape.text_frame

        for paragraph in text_frame.paragraphs:
            # 获取段落样式
            if paragraph.runs:
                # 使用第一个run的样式作为参考
                first_run = paragraph.runs[0]
                ref_font = first_run.font
                ref_size = ref_font.size
                original_size = ref_size.pt if ref_size else 18.0
            else:
                original_size = 18.0

            # 翻译整个段落
            full_text = paragraph.text

            if full_text.strip():
                translated = self.translate_text(full_text)

                # 清除所有run，重新设置
                if paragraph.runs:
                    first_run.text = translated
                    # 调整字体大小
                    new_size = self._calculate_font_size(
                        full_text, translated, original_size
                    )
                    first_run.font.size = Pt(new_size)

                    # 复制其他run的样式到第一个run
                    for run in paragraph.runs[1:]:
                        if run.font.bold:
                            first_run.font.bold = True
                        if run.font.italic:
                            first_run.font.italic = True
                        if run.font.color and run.font.color.rgb:
                            first_run.font.color.rgb = run.font.color.rgb
                        run.text = ""

    def get_presentation_info(self) -> Dict:
        """获取演示文稿信息"""
        if not self.prs:
            if not self.load_presentation():
                return {}

        return {
            'slide_count': len(self.prs.slides),
            'title': self.prs.core_properties.title if self.prs.core_properties else '',
            'author': self.prs.core_properties.author if self.prs.core_properties else '',
            'file_path': self.file_path
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PPT Translator - 翻译PowerPoint文件并保持原有格式和主题'
    )
    parser.add_argument('input_file', help='输入PPT文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（默认：原文件名+目标语言名称）')
    parser.add_argument('-t', '--target', default='en',
                       help='目标语言代码 (默认: en)')
    parser.add_argument('-s', '--source', default='zh-cn',
                       help='源语言代码 (默认: zh-cn)')
    parser.add_argument('-i', '--info', action='store_true',
                       help='仅显示PPT信息，不进行翻译')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"错误: 文件不存在 - {args.input_file}")
        sys.exit(1)

    translator = PptTranslator(args.input_file, args.target, args.source)

    if args.info:
        info = translator.get_presentation_info()
        print("\n=== PPT文件信息 ===")
        for key, value in info.items():
            print(f"{key}: {value}")
    else:
        print(f"开始翻译PPT文件...")
        print(f"源语言: {args.source}")
        print(f"目标语言: {args.target}")
        print(f"输出文件名: 原文件名 + {translator._lang_suffixes.get(args.target, args.target)}")
        print()

        translator.translate_presentation(args.output)


if __name__ == '__main__':
    main()
