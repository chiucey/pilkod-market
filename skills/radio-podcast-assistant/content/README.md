# 播客生成器 (Podcast Generator)

将文字或文档内容转换为专业的播客音频，支持单人和双人对话模式。

## 功能特点

- **多模式支持**：单人独白、双人对话
- **时长可控**：1分钟到10+分钟自由调节
- **智能脚本**：自动重组内容为流畅的播客形式
- **自然语音**：使用高质量文本转语音技术

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from podcast_generator import PodcastGenerator

# 初始化生成器
generator = PodcastGenerator()

# 准备内容
text = """
你的文字内容...
"""

# 生成单人播客（2分钟）
script = generator.generate_script(text, mode='single', target_minutes=2)
print(generator.script_to_text(script))

# 生成双人播客（3分钟）
script = generator.generate_script(text, mode='dual', target_minutes=3)
print(generator.script_to_text(script))
```

### 生成音频

```python
# 获取音频片段
segments = generator.get_audio_segments(script)

# 使用TTS工具生成音频
# 参考 gen_audios 工具的使用方式
```

## 命令行使用

```bash
python podcast_generator.py
```

## 模式说明

### 单人模式
- 适合：个人分享、知识讲解、故事叙述
- 特点：连贯性强，节奏稳定

### 双人模式
- 适合：访谈、讨论、问答
- 特点：互动感强，趣味性高

## 时长控制

| 目标时长 | 适用场景 |
|---------|---------|
| 1-2分钟 | 精华摘要、快速概览 |
| 3-5分钟 | 完整概述、日常内容 |
| 5-10分钟 | 详细讲解、深度分析 |
| 10+分钟 | 完整报告、专题讨论 |

## 注意事项

1. 输入内容越清晰、结构化，生成质量越高
2. 实际时长可能因语速、停顿等因素有±10%误差
3. 建议根据内容主题选择合适的播客模式
