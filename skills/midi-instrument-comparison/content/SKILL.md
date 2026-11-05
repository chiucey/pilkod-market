---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2995da2f44d25cc9569e8312ab423c43
    PropagateID: 2995da2f44d25cc9569e8312ab423c43
    ReservedCode1: 3045022056116ae2e733e35a8d824dff46345e32ad876388373a65aa0b7415ff06d92f2c022100bb173876cae334b78851469a51259df46f358f6cdd40e6e07a46459c8ec231cb
    ReservedCode2: 30460221008a739332599a429df1a771b2fc797184d991aa17953cbf6160e267c2252fc233022100f01137942d2729b6b747f0cc018b9feffd24f4bf269b9e940ab0f92d7af580b3
description: 多音轨长时间 MIDI 文件生成技能，基于 mido 库生成符合 GM 标准的 MIDI 文件。当用户要求生成 MIDI 文件、创建多音轨 MIDI、制作指定时长的 MIDI 音乐、导出 MIDI 音轨，或生成钢琴/吉他/鼓等特定乐器的 MIDI 时使用。支持 Studio One 7 和 Ableton Live 12 Suite 乐器库映射参考。
name: midi-instrument-comparison
---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6bbe165436ebbb8912b5650c7bc29094
    PropagateID: 6bbe165436ebbb8912b5650c7bc29094
    ReservedCode1: 3046022100a117556946cd32601f60064aceab80fcbfe071d0e9ea6cdc73c337cc94bd3455022100bb30eec92e050f5c871c7becb8ee72343bd781bb6f6b11c545960900acdc91c5
    ReservedCode2: 3045022100e79c72d6e0cdff3f595648edc15955c21656cf93d11a195518b7acf5f1560f060220350d6efeeab34d6f6855ddb1cc915fb3839de8bbfd06579a31066a72b3130eef
---

# MIDI 作曲助手

## 核心能力

基于 Python `mido` 库生成符合标准的 MIDI 文件，支持多音轨、长时间创作。

### 主要功能

1. **多音轨 MIDI 生成**
   - 支持 1-16 个独立音轨
   - 每个音轨可设置不同乐器音色（GM/GS/XG 标准）
   - 音轨级音量、声像、控制器配置

2. **长时间 MIDI 创作**
   - 无时长限制的 MIDI 文件生成
   - 支持完整歌曲结构（引子、主歌、副歌、桥段、尾声）
   - 智能文件分割（超过 30 分钟自动分段）

3. **DAW 乐器库参考**
   - Studio One 7 默认乐器映射
   - Ableton Live 12 Suite 默认乐器映射
   - 音色号（Program Change）与乐器名对应表

### 使用场景

当用户要求：
- "生成一段 MIDI 文件"
- "创建一个多轨 MIDI"
- "制作一个 5 分钟的 MIDI 音乐"
- "导出 MIDI 音轨"
- "生成钢琴/吉他/鼓 MIDI"

### 不适用场景

- 需要音频渲染（应使用 DAW 软件）
- 实时 MIDI 播放控制
- MIDI 编辑器操作（应使用专门的 MIDI 编辑器）

---

## 工作流程

### 阶段 1：需求分析

**必问信息**：
1. 音轨数量和每音轨的乐器类型
2. 音乐时长和结构
3. 节奏/速度（BPM）
4. 调性和调式

**可选信息**：
- 力度动态范围
- 特殊效果（延音、颤音、弯音）
- 是否需要鼓组轨道

### 阶段 2：MIDI 生成

使用 `mido` 库构建 MIDI 结构：

```python
import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack

def create_multitrack_midi(tracks_config, duration_minutes, tempo_bpm):
    mid = MidiFile(type=1)  # type=1 支持多轨

    # 设置速度
    track0 = MidiTrack()
    track0.append(MetaMessage('set_tempo', tempo=mido.tempo2bpm(tempo_bpm)))
    track0.append(MetaMessage('time_signature', numerator=4, denominator=4))
    mid.tracks.append(track0)

    # 为每个音轨添加音符
    for track_config in tracks_config:
        track = MidiTrack()
        # 添加 Program Change 设置音色
        track.append(Message('program_change', program=track_config['program'], time=0))
        # 添加音符事件...
        mid.tracks.append(track)

    return mid
```

### 阶段 3：文件输出

生成标准 .mid 文件，包含：
- 正确的 MIDI 头信息
- 所有音轨的元数据
- 完整的时间戳和增量时间

---

## 乐器库参考

### General MIDI 标准音色

| 音色号 | 类别 | 乐器名 |
|--------|------|--------|
| 0-7 | 钢琴 | Acoustic Grand, Bright Acoustic, Electric Grand, Honky-tonk, Electric Piano 1-4, Harpsichord, Clavinet |
| 8-15 | 色彩打击乐 | Celesta, Glockenspiel, Music Box, Vibraphone, Marimba, Xylophone, Tubular Bells, Dulcimer |
| 16-23 | 风琴 | Drawbar Organ, Percussive Organ, Rock Organ, Church Organ, Reed Organ, Accordion, Harmonica, Tango Accordion |
| 24-31 | 吉他 | Nylon Guitar, Steel Guitar, Jazz Guitar, Clean Guitar, Muted Guitar, Overdriven Guitar, Distortion Guitar, Guitar Harmonics |
| 32-39 | 贝斯 | Acoustic Bass, Electric Bass (Jazz), Electric Bass (Pick), Fretless Bass, Slap Bass 1, Slap Bass 2, Synth Bass 1, Synth Bass 2 |
| 40-47 | 弦乐 | Violin, Viola, Cello, Contrabass, Tremolo Strings, Pizzicato Strings, Orchestral Harp, Timpani |
| 48-55 | 合奏 | String Ensemble 1, String Ensemble 2, Synth Strings 1, Synth Strings 2, Choir Aahs, Voice Oohs, Synth Choir, Orchestra Hit |
| 56-63 | 铜管 | Trumpet, Trombone, Tuba, Muted Trumpet, French Horn, Brass Section, Synth Brass 1, Synth Brass 2 |
| 64-71 | 簧片 | Soprano Sax, Alto Sax, Tenor Sax, Baritone Sax, Oboe, English Horn, Bassoon, Clarinet |
| 72-79 | 笛 | Piccolo, Flute, Recorder, Pan Flute, Blown Bottle, Shakuhachi, Whistle, Ocarina |
| 80-87 | 合成音色 | Lead 1 (Square), Lead 2 (Sawtooth), Lead 3 (Calliope), Lead 4 (Chiff), Lead 5 (Charang), Lead 6 (Voice), Lead 7 (Fifths), Lead 8 (Bass+Lead) |
| 88-95 | 合成音色 | New Age, Warm, Polysynth, Choir, Bowed, Metallic, Halo, Sweep |
| 96-103 | 效果音 | Rain, Soundtrack, Crystal, Atmosphere, Brightness, Goblins, Echoes, Sci-Fi |
| 104-111 | 民族乐器 | Sitar, Banjo, Shamisen, Koto, Kalimba, Bagpipe, Fiddle, Shanai |
| 112-119 | 打击乐 | Tinkle Bell, Agogo, Steel Drums, Woodblock, Taiko Drum, Melodic Tom, Synth Drum, Reverse Cymbal |
| 120-127 | 声音效果 | Guitar Fret Noise, Breath Noise, Seashore, Bird Tweet, Telephone Ring, Helicopter, Applause, Gunshot |

### Studio One 7 / Ableton Live 12 Suite 乐器映射

> 详情见 `references/daw_instruments.md`

---

## 技术实现

### 依赖库

```python
# 核心库
mido>=1.2.0          # MIDI 文件读写
mido[midifiles]      # MIDI 文件后端支持

# 可选增强
numpy>=1.20.0        # 数学计算（和声、节奏）
```

### 文件格式

生成的 MIDI 文件：
- 格式：Standard MIDI File (SMF)
- 类型：`type=1`（多轨同步播放）
- 编码：二进制 .mid 文件
- 兼容性：所有 DAW 软件（Studio One, Ableton Live, FL Studio, Logic Pro 等）

### 性能考虑

| 时长范围 | 音轨数 | 建议 |
|----------|--------|------|
| < 5 分钟 | 1-8 | 单文件直接生成 |
| 5-30 分钟 | 4-16 | 单文件，优化控制器数量 |
| > 30 分钟 | 8-16 | 自动分段或优化量化精度 |

---

## 错误处理

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 文件无法打开 | 编码错误 | 使用 mido 默认编码，不指定 binary |
| 播放速度异常 | 未设置 tempo | 确保包含 `set_tempo` MetaMessage |
| 音色不对 | 未发送 Program Change | 每个音轨开头添加 program_change 消息 |
| 音轨缺失 | track 添加顺序 | 主 tempo 轨道在 index=0 |

---

## 输出规范

生成的 MIDI 文件必须满足：
1. ✅ 有效的 MIDI 头标识符（MThd）
2. ✅ 正确的 ticks_per_beat（默认 480）
3. ✅ 所有音轨包含 end_of_track
4. ✅ 无重叠的 Note On/Off 事件
5. ✅ 正确的增量时间计算

---

## 快速命令模板

```
用户输入：创建一个 4 音轨的 MIDI 文件，包括钢琴、贝斯、鼓、弦乐，时长 3 分钟，120 BPM

执行步骤：
1. 解析需求 → tracks_config = [
    {"name": "Piano", "program": 0, "volume": 100},
    {"name": "Bass", "program": 32, "volume": 90},
    {"name": "Drums", "program": 0, "channel": 9},
    {"name": "Strings", "program": 48, "volume": 80}
   ]
2. 生成 MIDI 结构
3. 输出文件
```

---

## 交付物

当技能完成时，输出：
- `.mid` 格式的 MIDI 文件
- 文件名格式：`composition_[timestamp].mid`
- 包含完整的元数据和所有音轨信息