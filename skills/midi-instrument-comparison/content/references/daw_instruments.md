# DAW 软件默认 MIDI 乐器库参考

本文档汇总 **Studio One 7** 和 **Ableton Live 12 Suite** 的默认虚拟乐器和音色映射。

---

## Studio One 7 默认乐器

### 原生虚拟乐器

| 类别 | 乐器名称 | MIDI Program | 说明 |
|------|----------|--------------|------|
| **合成器** | | | |
| | Mai Tai | 80-87 | 多音色模拟合成器 |
| | Mojito | 80-87 | 单音模拟合成器 |
| | Presence XT | 0-127 | 采样播放器和工作站 |
| | Sample One XT | 0-127 | 采样器 |
| | **Easy Limiter** | - | 母带限制器（无MIDI）|
| | **Fat Channel** | - | 通道条处理器 |
| **鼓机/采样** | | | |
| | Impact | 118 | 16 pads 采样鼓机 |
| | Impact XT | 118 | 增强版鼓机 |
| **钢琴/键盘** | | | |
| | Presence | 0 | 钢琴采样器 |
| | **Legacy** | - | 经典虚拟乐器集合 |
| **效果器** | | | |
| | Pro EQ3 | - | 3段参量均衡器 |
| | Rotor | - | 旋转扬声器模拟 |

### Studio One 7 音色库映射

```
GM 兼容音色号 → Studio One 乐器映射：

Program 0-7 (钢琴类):
  Studio One: Presence (钢琴采样)
  Control: 可通过 Key Switch 切换变体

Program 24-31 (吉他类):
  Studio One: Presence (吉他采样)
  支持电吉他原声/失真变体

Program 40-47 (弦乐类):
  Studio One: Presence (管弦乐采样)
  支持弓弦/拨弦技法切换

Program 48-55 (合奏类):
  Studio One: Presence (合奏采样)
  String Ensemble 1 → Studio One Strings
```

---

## Ableton Live 12 Suite 默认乐器

### 内置虚拟乐器

| 类别 | 乐器名称 | MIDI Program | 说明 |
|------|----------|--------------|------|
| **合成器** | | | |
| | Wavetable | 80-87 | 波表合成器 |
| | Operator | 80-87 | FM 合成器 |
| | Analog | 80-87 | 模拟合成器 |
| | Collision | - | 物理建模合成器 |
| | Drift | 80-87 | 减法合成器 |
| | Tension | - | 物理弦乐合成器 |
| | Electric | - | 电钢琴物理建模 |
| **采样器** | | | |
| | Sampler | 0-127 | 完整采样工作站 |
| | Simpler | 0-127 | 简化采样器 |
| | Impulse | 118 | 鼓采样器 |
| **打击乐** | | | |
| | Drum Rack | 118 | 16/64 pads 鼓机 |
| | Drum Machines | - | 经典鼓机模拟 (LM7, TT78等) |
| **其他** | | | |
| | Grand | 0 | 三角钢琴采样 |
| | Electric | 4 | 电钢琴 (Rhodes/Wurlitzer) |
| | Collision | - | 打击膜/共鸣器合成器 |

### Ableton Live 12 Suite 音色包

Live 12 Suite 包含以下音色包（需在 Content Browser 中查看）：

```
Core Library 内置音色包：
├── Instruments/
│   ├── Analog/
│   │   └── Analog Raw.kmmat (预设)
│   ├── Collision/
│   ├── Drift/
│   ├── Drums/
│   │   ├── 707 Kit.clp
│   │   ├── 808 Kit.clp
│   │   ├── 909 Kit.clp
│   │   └── Acoustic Kit.clp
│   ├── Electric/
│   ├── Grand/
│   ├── Latigo/
│   ├── Operator/
│   ├── Sampler/
│   ├── Simple/
│   ├── Tension/
│   └── Wavetable/
└── Packs/
    └── Core Library Packs/
        ├── Ambient Textures
        ├── Brass & Reeds
        ├── Guitars & Bass
        ├── Keys & Bells
        ├── Orchestral Strings
        ├── Orchestral Percussion
        ├── Orchestral Winds
        ├── Synth Lead
        ├── Synth Pad
        └── World Instruments
```

---

## 音色号对照表 (GM Standard → DAW)

| GM Program | GM 乐器名 | Studio One 7 | Ableton Live 12 |
|-------------|-----------|--------------|-----------------|
| 0 | Acoustic Grand Piano | Presence (Piano) | Grand |
| 1 | Bright Acoustic Piano | Presence (Piano Bright) | Grand (Bright) |
| 4 | Electric Piano 1 | Presence (E-Piano) | Electric |
| 6 | Harpsichord | Presence (Harpsichord) | - |
| 24 | Nylon Guitar | Presence (Nylon) | Sampler (Guitar) |
| 25 | Steel Guitar | Presence (Steel) | Sampler (Steel) |
| 27 | Clean Guitar | Presence (Clean) | Sampler (Clean) |
| 29 | Overdriven Guitar | Presence (Overdrive) | Sampler (Overdrive) |
| 30 | Distortion Guitar | Presence (Distortion) | Sampler (Distortion) |
| 32 | Acoustic Bass | Presence (Bass) | Sampler (Acoustic Bass) |
| 33 | Electric Bass (Jazz) | Presence (Jazz Bass) | Sampler (Jazz Bass) |
| 35 | Fretless Bass | Presence (Fretless) | Sampler (Fretless) |
| 40 | Violin | Presence (Violin) | Sampler (Violin) |
| 41 | Viola | Presence (Viola) | Sampler (Viola) |
| 42 | Cello | Presence (Cello) | Sampler (Cello) |
| 48 | String Ensemble 1 | Presence (Strings) | Sampler (Strings) |
| 56 | Trumpet | Presence (Trumpet) | Sampler (Trumpet) |
| 57 | Trombone | Presence (Trombone) | Sampler (Trombone) |
| 60 | French Horn | Presence (Horn) | Sampler (French Horn) |
| 65 | Alto Sax | Presence (Alto Sax) | Sampler (Sax) |
| 73 | Flute | Presence (Flute) | Sampler (Flute) |
| 80 | Lead 1 (Square) | Mai Tai (Square) | Wavetable (Square) |
| 81 | Lead 2 (Sawtooth) | Mai Tai (Saw) | Wavetable (Saw) |
| 88 | Pad 1 (New Age) | Mai Tai (Pad) | Wavetable (Pad) |
| 118 | Synth Drum | Impact XT | Impulse |
| 120 | Guitar Fret Noise | Presence | Sampler |
| 126 | Applause | Presence | Sampler |

---

## MIDI CC 控制器映射

### 标准 GM 控制器

| CC# | 名称 | 用途 | Studio One | Ableton Live |
|-----|------|------|------------|--------------|
| 0 | Bank Select MSB | 音色库选择 | 支持 | 支持 |
| 1 | Modulation | 调制轮 | Mai Tai/Sdepth | Wavetable/Operator |
| 7 | Volume | 音量 | Track Volume | Track Volume |
| 10 | Pan | 声像 | Track Pan | Track Pan |
| 11 | Expression | 表情 | 支持 | 支持 |
| 64 | Sustain Pedal | 延音踏板 | 支持 | 支持 |
| 66 | Sostenuto | 持音 | 支持 | 支持 |
| 67 | Soft Pedal | 柔音踏板 | 支持 | 支持 |
| 68 | Legato | 连奏 | 支持 | 支持 |
| 91 | Reverb | 混响发送 | 返回轨道 | 返回轨道 |
| 93 | Chorus | 合唱发送 | 返回轨道 | 返回轨道 |

### DAW 特定控制器

| CC# | Studio One 7 | Ableton Live 12 |
|-----|--------------|-----------------|
| 102-119 | 内部保留 | Key/Scaled Playing |
| 120-127 | 通道模式消息 | 通道模式消息 |

---

## 鼓组映射 (GM Drum Map)

两个 DAW 都遵循标准 GM 鼓组映射：

```
Channel 10 (Index 9) - Drum Channel:

Note  | GM Name           | Studio One | Ableton Live
------|-------------------|------------|--------------
35    | Acoustic Bass Drum | Impact    | Drum Rack
36    | Bass Drum 1        | Impact    | Drum Rack
37    | Side Stick         | Impact    | Drum Rack
38    | Acoustic Snare     | Impact    | Drum Rack
39    | Hand Clap          | Impact    | Drum Rack
40    | Electric Snare     | Impact    | Drum Rack
41    | Low Floor Tom      | Impact    | Drum Rack
42    | Closed Hi-Hat      | Impact    | Drum Rack
43    | High Floor Tom     | Impact    | Drum Rack
44    | Pedal Hi-Hat       | Impact    | Drum Rack
45    | Low Tom            | Impact    | Drum Rack
46    | Open Hi-Hat        | Impact    | Drum Rack
47    | Low-Mid Tom        | Impact    | Drum Rack
48    | Hi-Mid Tom         | Impact    | Drum Rack
49    | Crash Cymbal 1     | Impact    | Drum Rack
50    | High Tom           | Impact    | Drum Rack
51    | Ride Cymbal 1      | Impact    | Drum Rack
52    | Chinese Cymbal     | Impact    | Drum Rack
53    | Ride Bell          | Impact    | Drum Rack
54    | Tambourine         | Impact    | Drum Rack
55    | Splash Cymbal      | Impact    | Drum Rack
56    | Cowbell            | Impact    | Drum Rack
57    | Crash Cymbal 2     | Impact    | Drum Rack
59    | Ride Cymbal 2      | Impact    | Drum Rack
```

---

## 导入/导出注意事项

### Studio One 7
- 使用 `.song` 格式保存完整项目
- MIDI 导出为 `.mid` 或 `.std` (Studio One 专用)
- 支持 Drag & Drop 到外部 DAW
- Program Change 信息完整保留

### Ableton Live 12
- 使用 `.als` 格式保存完整项目
- MIDI 导出为 `.mid`
- Live 的 MIDI Clip 包含表情/弯音数据
- 需要手动设置 Program Change

---

## 附录：音色库路径

### Studio One 7
```
Windows: C:\Users\[用户名]\Documents\Presonus\Studio One 7\Soundter\
macOS: ~/Documents/Studio One 7/Soundter/

音色格式: .sus (原生采样格式)
```

### Ableton Live 12 Suite
```
Windows: C:\Users\[用户名]\Documents\Ableton\Live Library\
macOS: ~/Documents/Ableton/Live Library/

音色格式: .adg (Device Group), .adv (Device Preset)
```

---

*文档更新日期: 2024年*
*参考版本: Studio One 7.0, Ableton Live 12.0 Suite*