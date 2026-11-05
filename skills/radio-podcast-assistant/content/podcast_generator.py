#!/usr/bin/env python3
"""
播客生成器 - 将文字内容转换为播客音频

功能：
- 单人/双人播客模式
- 可控时长
- 智能脚本生成
"""

import re
import json
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VoiceConfig:
    """声音配置"""
    voice_id: str
    name: str
    gender: str  # 'male' or 'female'
    style: str  # 'professional', 'friendly', 'energetic', etc.


@dataclass
class PodcastScript:
    """播客脚本"""
    mode: str  # 'single' or 'dual'
    segments: List[Dict]  # [{'speaker': 'A'/'B', 'text': '...', 'emotion': '...'}]
    estimated_duration: int  # seconds
    theme: str


class PodcastGenerator:
    """播客生成器主类"""

    # 内置开场白和结束语
    OPENINGS_SINGLE = [
        "大家好，欢迎收听今天的播客。",
        "亲爱的听众朋友们，大家好！",
        "欢迎来到今天的播客时间。",
        "各位好，很高兴又和大家见面了。",
    ]

    OPENINGS_DUAL_HOST = [
        "A：各位听众朋友大家好，欢迎收听今天的节目。",
        "A：大家好，欢迎来到我们的播客。",
    ]

    CLOSINGS = [
        "以上就是今天的内容，感谢大家的聆听。",
        "好了，今天的分享就到这里，我们下期再见。",
        "感谢大家的收听，如果喜欢我们的节目，记得订阅哦。",
        "这就是今天的所有内容，祝大家有美好的一天。",
    ]

    TRANSITIONS = [
        "接下来让我们看看",
        "然后我们来说说",
        "除此之外，还有一个重要的问题是",
        "说到这个，不得不提",
    ]

    def __init__(self):
        self.theme = ""
        self.mode = "single"

    def analyze_content(self, text: str) -> Dict:
        """分析文本内容"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text).strip()

        # 统计信息
        char_count = len(text)
        word_count = len(text.split())

        # 尝试提取主题（取前50字符或第一个句号前的内容）
        theme = text[:50].split('。')[0] if '。' in text else text[:50]

        # 尝试识别段落结构
        paragraphs = [p.strip() for p in re.split(r'[\n\r]+', text) if p.strip()]

        return {
            'text': text,
            'char_count': char_count,
            'word_count': word_count,
            'theme': theme,
            'paragraphs': paragraphs,
            'estimated_read_time': char_count / 400  # 按每分钟400字估算
        }

    def estimate_duration(self, text: str, target_minutes: int) -> int:
        """估算目标时长所需的内容量"""
        # 基础字数：每分钟约300字（考虑对话节奏和停顿）
        base_chars_per_minute = 300

        # 双人模式因为有对话间隙，可以容纳更多内容
        if self.mode == "dual":
            base_chars_per_minute = 350

        target_chars = target_minutes * base_chars_per_minute
        return target_chars

    def compress_content(self, text: str, target_chars: int) -> str:
        """压缩内容到目标字数"""
        current_chars = len(text)

        if current_chars <= target_chars:
            return text

        # 按句子分割
        sentences = re.split(r'[。！？\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 智能选择句子
        if len(sentences) <= 3:
            return text

        # 选择最能代表主题的句子
        # 保留首句、尾句和中间随机采样
        selected = [sentences[0]]  # 开头
        end_idx = len(sentences) - 1 if len(sentences) > 1 else 0
        selected.append(sentences[end_idx])  # 结尾

        # 中间部分按比例采样
        middle = sentences[1:-1] if len(sentences) > 2 else []
        if middle:
            ratio = (target_chars - len(sentences[0]) - len(sentences[-1])) / max(1, sum(len(s) for s in middle))
            num_select = max(1, int(len(middle) * min(1, ratio)))
            selected.extend(random.sample(middle, min(num_select, len(middle))))

        result = '。'.join(selected)
        if not result.endswith('。'):
            result += '。'

        # 递归压缩直到达标
        if len(result) > target_chars:
            return self.compress_content(result, target_chars)

        return result

    def expand_content(self, text: str, target_chars: int) -> str:
        """扩展内容到目标字数"""
        current_chars = len(text)

        if current_chars >= target_chars:
            return text

        # 分析文本获取关键信息
        analysis = self.analyze_content(text)

        # 生成扩展内容
        additions = []

        # 添加背景介绍
        if len(text) < target_chars * 0.3:
            additions.append(f"今天我们要聊的话题是关于{analysis['theme']}的。")
            additions.append(f"这个问题在当前社会受到了广泛的关注。")

        # 添加细节扩展
        if len(text) < target_chars * 0.6 and analysis['paragraphs']:
            # 找最长的段落进行拆分扩展
            longest = max(analysis['paragraphs'], key=len)
            if len(longest) > 30:
                additions.append(f"特别值得注意的是，{longest[:50]}...")

        # 添加总结性内容
        if len(text) < target_chars * 0.8:
            additions.append(f"总的来说，{analysis['theme']}是一个值得我们深入思考的话题。")

        # 合并扩展
        expanded = text + '。'.join(additions)
        if not expanded.endswith('。'):
            expanded += '。'

        if len(expanded) < target_chars:
            return self.expand_content(expanded, target_chars)

        return expanded

    def generate_script_single(self, text: str, theme: str, target_minutes: int) -> PodcastScript:
        """生成单人播客脚本"""
        # 计算目标字数
        target_chars = self.estimate_duration(text, target_minutes)

        # 调整内容长度
        if len(text) > target_chars:
            processed_text = self.compress_content(text, target_chars)
        else:
            processed_text = self.expand_content(text, target_chars)

        # 构建脚本
        segments = []

        # 开场
        opening = random.choice(self.OPENINGS_SINGLE)
        segments.append({
            'speaker': 'A',
            'text': opening,
            'type': 'opening',
            'emotion': 'friendly'
        })

        # 主题引入
        segments.append({
            'speaker': 'A',
            'text': f"今天我们要聊的是：{theme}",
            'type': 'intro',
            'emotion': 'professional'
        })

        # 正文分段
        sentences = re.split(r'[。！？]+', processed_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        current_paragraph = []
        for i, sentence in enumerate(sentences):
            if len(sentence) < 5:
                continue

            current_paragraph.append(sentence)

            # 每3-5个句子组成一个段落
            if len(current_paragraph) >= 3 or i == len(sentences) - 1:
                # 添加过渡语
                if random.random() > 0.5 and len(current_paragraph) > 2:
                    transition = random.choice(self.TRANSITIONS)
                    segments.append({
                        'speaker': 'A',
                        'text': transition,
                        'type': 'transition',
                        'emotion': 'engaging'
                    })

                # 添加内容段落
                paragraph_text = '。'.join(current_paragraph)
                if not paragraph_text.endswith('。'):
                    paragraph_text += '。'

                segments.append({
                    'speaker': 'A',
                    'text': paragraph_text,
                    'type': 'content',
                    'emotion': random.choice(['professional', 'friendly', 'engaging'])
                })

                current_paragraph = []

        # 结束语
        closing = random.choice(self.CLOSINGS)
        segments.append({
            'speaker': 'A',
            'text': closing,
            'type': 'closing',
            'emotion': 'friendly'
        })

        return PodcastScript(
            mode='single',
            segments=segments,
            estimated_duration=target_minutes * 60,
            theme=theme
        )

    def generate_script_dual(self, text: str, theme: str, target_minutes: int) -> PodcastScript:
        """生成双人播客脚本"""
        # 计算目标字数
        target_chars = self.estimate_duration(text, target_minutes)

        # 调整内容长度
        if len(text) > target_chars:
            processed_text = self.compress_content(text, target_chars)
        else:
            processed_text = self.expand_content(text, target_chars)

        # 构建脚本
        segments = []

        # 开场
        opening_idx = random.randint(0, len(self.OPENINGS_DUAL_HOST) - 1)
        segments.append({
            'speaker': 'A',
            'text': self.OPENINGS_DUAL_HOST[opening_idx].replace('A：', ''),
            'type': 'opening',
            'emotion': 'friendly'
        })

        segments.append({
            'speaker': 'B',
            'text': '大家好，很高兴能参与今天的节目。',
            'type': 'opening',
            'emotion': 'friendly'
        })

        # 主题讨论
        sentences = re.split(r'[。！？]+', processed_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 分配对话角色
        for i, sentence in enumerate(sentences):
            if len(sentence) < 5:
                continue

            # 轮流提问和回答
            if i % 4 == 0:
                # 提问
                segments.append({
                    'speaker': 'A',
                    'text': f"关于{theme}，你怎么看？",
                    'type': 'question',
                    'emotion': 'curious'
                })
            else:
                # 回答
                if not sentence.endswith('。'):
                    sentence += '。'
                segments.append({
                    'speaker': 'B',
                    'text': sentence,
                    'type': 'answer',
                    'emotion': random.choice(['professional', 'friendly', 'thoughtful'])
                })

        # 互动讨论
        if len(segments) > 5:
            # 添加一些互动
            interactions = [
                ('A', '这确实很有见地。', 'agreeing'),
                ('B', '没错，这也是我想强调的。', 'emphasizing'),
                ('A', '听众朋友们，你们觉得呢？', 'engaging'),
                ('B', '让我们再来深入聊聊这个话题。', 'deepening'),
            ]
            for speaker, text, emotion in interactions[:2]:
                segments.append({
                    'speaker': speaker,
                    'text': text,
                    'type': emotion,
                    'emotion': emotion
                })

        # 结束语
        segments.append({
            'speaker': 'A',
            'text': random.choice(self.CLOSINGS),
            'type': 'closing',
            'emotion': 'friendly'
        })

        segments.append({
            'speaker': 'B',
            'text': '感谢大家的收听，下次节目再见！',
            'type': 'closing',
            'emotion': 'friendly'
        })

        return PodcastScript(
            mode='dual',
            segments=segments,
            estimated_duration=target_minutes * 60,
            theme=theme
        )

    def generate_script(self, text: str, mode: str = 'single',
                       target_minutes: int = 3) -> PodcastScript:
        """生成播客脚本"""
        self.mode = mode

        # 分析内容
        analysis = self.analyze_content(text)

        # 根据模式生成脚本
        if mode == 'single':
            return self.generate_script_single(
                text,
                analysis['theme'],
                target_minutes
            )
        else:
            return self.generate_script_dual(
                text,
                analysis['theme'],
                target_minutes
            )

    def script_to_text(self, script: PodcastScript) -> str:
        """将脚本转换为可读文本"""
        output = []
        output.append(f"【播客脚本 - {'单' if script.mode == 'single' else '双'}人模式】")
        output.append(f"预计时长：约 {script.estimated_duration // 60} 分 {script.estimated_duration % 60} 秒")
        output.append(f"主题：{script.theme}")
        output.append("")
        output.append("-" * 40)

        speaker_names = {'A': '主播', 'B': '嘉宾'}
        if script.mode == 'dual':
            speaker_names = {'A': '主持人A', 'B': '嘉宾B'}

        for segment in script.segments:
            speaker = speaker_names.get(segment['speaker'], segment['speaker'])
            output.append(f"[{speaker}] {segment['text']}")

        output.append("-" * 40)
        output.append("")

        return '\n'.join(output)

    def get_audio_segments(self, script: PodcastScript) -> List[Tuple[str, str]]:
        """获取用于TTS的音频片段"""
        segments = []
        for i, segment in enumerate(script.segments):
            segments.append((segment['speaker'], segment['text']))
        return segments


def demo():
    """演示函数"""
    generator = PodcastGenerator()

    # 示例文本
    sample_text = """
    人工智能技术正在快速发展，它正在改变我们生活和工作的方式。
    机器学习让计算机能够从数据中学习，深度学习则推动了计算机视觉和自然语言处理的进步。
    在医疗领域，AI可以帮助医生诊断疾病；在金融领域，它可以检测欺诈行为；在教育领域，智能辅导系统能够个性化教学。
    当然，AI也带来了挑战，比如隐私问题和就业影响。
    我们需要在发展技术的同时，认真思考如何应对这些挑战。
    总的来说，人工智能是一把双刃剑，关键在于我们如何使用它。
    """

    # 生成单人播客
    print("=" * 50)
    print("单人播客示例")
    print("=" * 50)
    script_single = generator.generate_script(sample_text, mode='single', target_minutes=2)
    print(generator.script_to_text(script_single))

    # 生成双人播客
    print("\n" + "=" * 50)
    print("双人播客示例")
    print("=" * 50)
    script_dual = generator.generate_script(sample_text, mode='dual', target_minutes=3)
    print(generator.script_to_text(script_dual))


if __name__ == "__main__":
    demo()
