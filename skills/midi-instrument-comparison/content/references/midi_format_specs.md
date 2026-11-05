# MIDI 文件格式规范参考

本文档详细说明 Standard MIDI File (SMF) 格式规范，确保生成的 MIDI 文件与所有 DAW 软件兼容。

---

## 文件结构

### MIDI 文件组成

```
┌─────────────────────────────────────┐
│           Header Chunk (MThd)        │
│  - Format Type                      │
│  - Number of Tracks                 │
│  - Time Division                    │
├─────────────────────────────────────┤
│           Track Chunk 1 (MTrk)       │
│  - Track Events                     │
│  - Delta Times                      │
├─────────────────────────────────────┤
│           Track Chunk 2 (MTrk)       │
│  - Track Events                     │
│  - Delta Times                      │
├─────────────────────────────────────┤
│                ...                   │
└─────────────────────────────────────┘
```

### 头标识符

| 标识 | 名称 | 长度 | 说明 |
|------|------|------|------|
| `MThd` | MIDI Header | 6 bytes | 文件头部 |
| `MTrk` | MIDI Track | 变长 | 音轨数据 |

---

## Header Chunk 详解

### MThd 结构

```
Offset | Length | Description
-------|--------|-------------
0      | 4      | "MThd" (0x4D546864)
4      | 4      | Chunk length (always 6)
8      | 2      | Format type (0, 1, or 2)
10     | 2      | Number of tracks
12     | 2      | Division (ticks per quarter note)
```

### Format 类型

| Type | Name | Description | Use Case |
|-------|------|-------------|----------|
| 0 | Single Track | 单音轨格式 | 单乐器文件 |
| 1 | Multi-Track | 多音轨同步 | 多乐器音乐作品 |
| 2 | Multi-Track | 多音轨异步 | 多段独立音乐 |

### Division (时间分辨率)

```
标准格式: 480 ticks per quarter note (PPQ)
常用值:
  - 96 PPQ (低精度)
  - 192 PPQ (中等精度)
  - 384 PPQ (高精度)
  - 480 PPQ (推荐，高精度)
  - 960 PPQ (超高精度)
```

---

## Track Chunk 详解

### MTrk 结构

```
Offset | Length | Description
-------|--------|-------------
0      | 4      | "MTrk" (0x4D54726B)
4      | 4      | Chunk length (N)
8      | N      | Track events
```

### 事件类型

#### 1. 通道消息 (Channel Voice Messages)

| Status | Message | Data Bytes | Description |
|--------|---------|------------|-------------|
| 0x80-0x8F | Note Off | 2 | 音符释放 (note, velocity) |
| 0x90-0x9F | Note On | 2 | 音符按下 (note, velocity) |
| 0xA0-0xAF | Polyphonic Aftertouch | 2 | 复音触后 |
| 0xB0-0xBF | Control Change | 2 | 控制器改变 |
| 0xC0-0xCF | Program Change | 1 | 音色改变 (program) |
| 0xD0-0xDF | Channel Aftertouch | 1 | 通道触后 |
| 0xE0-0xEF | Pitch Bend | 2 | 弯音轮 |

#### 2. 元消息 (Meta Events)

| Status | Type | Description |
|--------|------|-------------|
| 0xFF 0x00 | Sequence Number | 音轨序号 |
| 0xFF 0x01 | Text Event | 文本 |
| 0xFF 0x02 | Copyright Notice | 版权信息 |
| 0xFF 0x03 | Track Name | 音轨名称 |
| 0xFF 0x04 | Instrument Name | 乐器名称 |
| 0xFF 0x05 | Lyric | 歌词 |
| 0xFF 0x06 | Marker | 标记 |
| 0xFF 0x07 | Cue Point | 提示点 |
| 0xFF 0x2F | End of Track | 音轨结束 (必填) |
| 0xFF 0x51 | Set Tempo | 速度设置 |
| 0xFF 0x54 | SMPTE Offset | SMPTE 时间码 |
| 0xFF 0x58 | Time Signature | 拍号 |
| 0xFF 0x59 | Key Signature | 调号 |
| 0xFF 0x7F | Sequencer Specific | 厂商特定 |

#### 3. 系统消息 (System Messages)

| Status | Description |
|--------|-------------|
| 0xF0 | SysEx Start |
| 0xF7 | SysEx End |
| 0xF8-0xFE | 系统实时消息 |

---

## 重要规范

### 1. Delta Time (增量时间)

```
MIDI 使用变长格式存储时间戳：
  - 每个字节 7 位有效数据
  - 最高位表示是否有后续字节
  - 格式: 0xxxxxxx 或 1xxxxxxx 0xxxxxxx ...

示例:
  0 (0 ticks)      → 0x00
  127 (127 ticks)  → 0x7F
  128 (128 ticks)  → 0x81 0x00
  1000 (1000 ticks)→ 0x87 0x68
```

### 2. Running Status (运行状态)

```
规则:
  - 在同一音轨内，如果连续消息类型相同
  - 可以省略状态字节，只传输数据
  - 系统独占消息后运行状态清除

示例:
  Note On, C4, 64 → 0x90 0x3C 0x40
  (下一行运行状态仍为 0x90)
  Note On, D4, 64 → 0x3C 0x40  (省略 0x90)
```

### 3. Note On/Off 事件

```python
# Note On (状态 0x90-0x9F, channel=0-15)
message = [0x90 + channel, note, velocity]
# note: 0-127 (C-1=0, C0=12, C1=24, C2=36, C3=48, C4=60, C5=72, C6=84, C7=96, C8=108, C9=120)
# velocity: 0-127

# Note Off (状态 0x80-0x8F 或 Note On with velocity=0)
message = [0x80 + channel, note, 0]
# 或
message = [0x90 + channel, note, 0]
```

### 4. Control Change 常用控制器

| CC# | Name | Range | Description |
|-----|------|-------|-------------|
| 0 | Bank Select MSB | 0-127 | 音色库高位 |
| 1 | Modulation Wheel | 0-127 | 调制轮 |
| 7 | Volume | 0-127 | 音量 |
| 10 | Pan | 0-127 | 声像 (0=左, 64=中, 127=右) |
| 11 | Expression | 0-127 | 表情 |
| 32 | Bank Select LSB | 0-127 | 音色库低位 |
| 64 | Sustain Pedal | 0-63=Off, 64-127=On | 延音踏板 |
| 65 | Portamento | 0-63=Off, 64-127=On | 滑音开关 |
| 66 | Sostenuto | 0-63=Off, 64-127=On | 持音踏板 |
| 67 | Soft Pedal | 0-63=Off, 64-127=On | 柔音踏板 |
| 91 | Effect 1 (Reverb) | 0-127 | 混响 |
| 93 | Effect 3 (Chorus) | 0-127 | 合唱 |

---

## 时长计算公式

### 拍数计算

```python
def ticks_to_seconds(ticks: int, tempo_bpm: int, ticks_per_beat: int) -> float:
    """将 ticks 转换为秒"""
    seconds_per_beat = 60.0 / tempo_bpm
    beats = ticks / ticks_per_beat
    return beats * seconds_per_beat

def seconds_to_ticks(seconds: float, tempo_bpm: int, ticks_per_beat: int) -> int:
    """将秒转换为 ticks"""
    beats_per_second = tempo_bpm / 60.0
    beats = seconds * beats_per_second
    return int(beats * ticks_per_beat)
```

### 文件大小估算

```
估算公式:
  估计大小 = (音符数 × 12) + (控制器数 × 12) + 元数据大小 + 头部开销

示例 (3分钟, 120 BPM, 4音轨):
  - 音符数 ≈ 5000
  - 控制器数 ≈ 200
  - 文件大小 ≈ 65 KB
```

---

## mido 库使用示例

```python
import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack

# 创建 MIDI 文件
mid = MidiFile(type=1, ticks_per_beat=480)

# 添加速度轨 (必须是第一个轨道)
tempo_track = MidiTrack()
tempo_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
tempo_track.append(MetaMessage('time_signature', numerator=4, denominator=4))
tempo_track.append(MetaMessage('track_name', name='Tempo'))
mid.tracks.append(tempo_track)

# 添加音轨
track = MidiTrack()
track.name = 'Piano'
track.append(Message('program_change', program=0, time=0))
track.append(Message('control_change', controller=7, value=100, time=0))
track.append(Message('note_on', note=60, velocity=80, time=0))
track.append(Message('note_off', note=60, velocity=0, time=480))
track.append(MetaMessage('end_of_track', time=0))
mid.tracks.append(track)

# 保存
mid.save('example.mid')
```

---

## 兼容性检查清单

生成 MIDI 文件前确保：

- [ ] 文件以 `MThd` 开头
- [ ] 每个 MTrk 以 `MTrk` 开头
- [ ] 每个音轨以 `end_of_track` 结束
- [ ] tempo 轨道在第一个音轨
- [ ] 所有 delta time 使用变长格式
- [ ] Note Off 事件正确发送
- [ ] Program Change 在音轨开头
- [ ] 音量/声像控制器在音轨开头

---

## 常见问题

### 1. 文件无法播放
- 检查是否包含 `set_tempo` 元消息
- 确认 `ticks_per_beat` 不为 0

### 2. 音色不正确
- 确保发送 `program_change` 消息
- 验证 Program Number 在 0-127 范围内

### 3. 音符全部同时发声
- 检查增量时间是否正确累加
- 确保 Note Off 有正确的 delta time

### 4. 文件在某些 DAW 打开异常
- 使用 type=1 格式
- 避免使用厂商特定的 SysEx 消息
- 确保所有字符串使用 UTF-8 编码

---

*文档版本: 1.0*
*参考标准: MMA RP-038 (Standard MIDI File 1.0)*