#!/usr/bin/env python3
"""
Quiz Generator Script
自动从文本内容生成交互式测验 HTML 文件
"""

import json
import re
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional


class QuizGenerator:
    """交互式测验生成器"""

    def __init__(self):
        self.templates = {}
        self.load_templates()

    def load_templates(self):
        """加载 HTML 模板"""
        template_dir = Path(__file__).parent.parent / "templates"
        for template_file in template_dir.glob("*.html"):
            self.templates[template_file.stem] = template_file.read_text(encoding='utf-8')

    def extract_questions_from_text(
        self,
        text: str,
        count: int = 10,
        question_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        从文本内容智能提取测验题目

        Args:
            text: 原始文本内容
            count: 生成的题目数量
            question_types: 题型列表 ['single', 'multiple', 'boolean']

        Returns:
            题目列表
        """
        if question_types is None:
            question_types = ['single', 'multiple', 'boolean']

        # 简单的关键词提取和题目生成逻辑
        # 在实际使用中，这里可以接入 AI API 进行智能题目生成

        questions = []
        sentences = self._split_sentences(text)

        for i, sentence in enumerate(sentences[:count]):
            q_type = question_types[i % len(question_types)]
            question = self._generate_question(sentence, q_type, i)
            if question:
                questions.append(question)

        return questions

    def _split_sentences(self, text: str) -> List[str]:
        """将文本分割为句子"""
        # 按常见分隔符分割
        sentences = re.split(r'[。！？\n]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]

    def _generate_question(
        self,
        sentence: str,
        q_type: str,
        index: int
    ) -> Optional[Dict[str, Any]]:
        """根据句子生成一道题目"""
        # 简单示例 - 实际应用中需要更智能的处理

        # 提取可能的关键词
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', sentence)
        words = [w for w in words if len(w) > 1][:5]

        if len(words) < 2:
            return None

        # 生成选项
        correct = words[0]
        distractors = words[1:min(4, len(words))]
        while len(distractors) < 3:
            distractors.append(f"选项{len(distractors) + 1}")

        options = [correct] + distractors[:3]
        import random
        random.shuffle(options)
        correct_index = options.index(correct)

        # 构建题目
        if q_type == 'single':
            question_text = f"以下关于"{correct}"的说法正确的是？"
        elif q_type == 'multiple':
            question_text = f"以下哪些是正确的？（多选）"
        else:
            question_text = f"以下说法是否正确：{sentence[:50]}..."

        return {
            "question": question_text,
            "type": q_type,
            "options": options,
            "correct": correct_index,
            "points": 10,
            "explanation": f"正确答案：{correct}"
        }

    def generate_from_json(
        self,
        questions: List[Dict[str, Any]],
        title: str,
        style: str = 'elegant'
    ) -> str:
        """
        从题目数据生成 HTML

        Args:
            questions: 题目列表
            title: 测验标题
            style: 模板风格 ('study', 'elegant', 'game')

        Returns:
            生成的 HTML 内容
        """
        if style not in self.templates:
            raise ValueError(f"Unknown style: {style}. Available: {list(self.templates.keys())}")

        template = self.templates[style]

        # 替换模板变量
        template = template.replace('{{QUIZ_TITLE}}', title)
        template = template.replace('{{QUESTION_COUNT}}', str(len(questions)))
        template = template.replace(
            '{{QUIZ_DATA}}',
            json.dumps(questions, ensure_ascii=False, indent=2)
        )

        return template

    def generate_from_file(
        self,
        content: str,
        title: str,
        style: str = 'elegant',
        question_count: int = 10
    ) -> str:
        """从内容自动生成测验"""
        questions = self.extract_questions_from_text(content, question_count)
        return self.generate_from_json(questions, title, style)

    def save_html(self, html_content: str, output_path: str) -> None:
        """保存 HTML 文件"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(html_content, encoding='utf-8')
        print(f"✓ HTML 文件已保存: {output_path}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='交互式测验生成器')
    parser.add_argument('--title', '-t', default='知识测验', help='测验标题')
    parser.add_argument('--content', '-c', help='测验内容文本')
    parser.add_argument('--file', '-f', help='内容文件路径')
    parser.add_argument('--questions', '-q', type=int, default=10, help='题目数量')
    parser.add_argument('--style', '-s', choices=['study', 'elegant', 'game'],
                        default='elegant', help='模板风格')
    parser.add_argument('--output', '-o', default='quiz_output.html', help='输出文件路径')

    args = parser.parse_args()

    # 获取内容
    if args.file:
        content = Path(args.file).read_text(encoding='utf-8')
    elif args.content:
        content = args.content
    else:
        print("错误: 请提供 --content 或 --file 参数")
        return

    # 生成测验
    generator = QuizGenerator()
    html = generator.generate_from_file(
        content=content,
        title=args.title,
        style=args.style,
        question_count=args.questions
    )

    # 保存
    generator.save_html(html, args.output)


if __name__ == '__main__':
    main()
