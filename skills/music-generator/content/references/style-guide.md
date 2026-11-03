# 音乐生成技能 - 参考文档

## 支持的音乐风格详细说明

### 1. 流行 Pop
- **特点**：旋律朗朗上口，节奏明快
- **提示词**：Pop music, upbeat, catchy melody, suitable for celebration
- **适用场景**：派对、健身、轻松氛围

### 2. 爵士 Jazz
- **特点**：即兴演奏丰富，和弦复杂
- **提示词**：Jazz music, smooth, soulful, relaxing atmosphere
- **适用场景**：咖啡厅、放松、夜晚氛围

### 3. 电子 Electronic
- **特点**：合成器音效，动感节拍
- **提示词**：Electronic music, energetic beats, modern synth
- **适用场景**：舞曲、科技感、未来感

### 4. 古典 Classical
- **特点**：交响乐编配，优雅庄重
- **提示词**：Classical music, elegant, orchestral arrangement
- **适用场景**：正式场合、艺术展示

### 5. 摇滚 Rock
- **特点**：电吉他riff，有力节奏
- **提示词**：Rock music, powerful, energetic guitar riffs
- **适用场景**：运动、释放能量

### 6. 嘻哈 Hip-Hop
- **特点**：说唱节奏，Urban 风格
- **提示词**：Hip-hop, rhythmic beats, urban vibe
- **适用场景**：街舞、说唱表演

### 7. 乡村 Country
- **特点**：原声乐器，叙事性强
- **提示词**：Country music, acoustic, heartfelt storytelling
- **适用场景**：乡村、回忆、故事

### 8. 蓝调 Blues
- **特点**：情感丰富，吉他蓝调音阶
- **提示词**：Blues music, emotional, soulful guitar
- **适用场景**：沉思、怀旧

## 歌词结构标签

支持以下结构标签用于分隔歌词段落：

| 标签 | 说明 | 典型长度 |
|------|------|----------|
| `[Intro]` | 前奏 | 4-8 行 |
| `[Verse]` | 主歌 | 4-8 行 |
| `[Pre-Chorus]` | 预副歌 | 2-4 行 |
| `[Chorus]` | 副歌 | 4-8 行 |
| `[Bridge]` | 桥段 | 4-8 行 |
| `[Outro]` | 结尾 | 2-4 行 |
| `[Hook]` | 钩子/记忆点 | 1-2 行 |

## 歌词示例

### 流行风格示例
```
[Verse]
阳光洒在海面上
微风轻轻吹拂
夏天的味道在空气中弥漫

[Chorus]
这就是夏天
快乐的夏天
让我们一起歌唱
这美好时光

[Outro]
永远记得这个夏天
```

### 嘻哈风格示例
```
[Intro]
Yo, let me take you higher

[Verse]
每天都在追逐梦想
不停脚步向前闯
不管多少困难阻挡

[Hook]
我们一起嗨
```

### 爵士风格示例
```
[Verse]
月光洒落在窗台
咖啡香气弥漫开来
回忆在脑海里徘徊

[Chorus]
今夜如此温柔
让音乐带你远走
```

## 技术参数推荐

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| sample_rate | 32000 | 采样率（Hz） |
| bitrate | 128000 | 比特率（bps） |
| format | mp3 | 音频格式 |
| duration | 1分钟 | 最大时长 |

## 常见问题

### Q: 歌词太长怎么办？
A: 建议控制在 600 字符以内。如果歌词较长，可以分段生成多首歌曲。

### Q: 可以生成纯音乐吗？
A: 可以，只需在歌词框中填写 "[Instrumental]" 或留空，并指定想要的氛围。

### Q: 生成的音乐可以商用吗？
A: 请查看具体服务条款，通常仅供个人使用。

### Q: 如何提高生成质量？
A:
- 使用清晰的歌词结构标签
- 选择与歌词内容匹配的风格
- 指定具体的心情/场景描述
- 避免过于抽象或矛盾的描述
