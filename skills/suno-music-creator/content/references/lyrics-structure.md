# 歌词结构与 Meta Tags 完整指南

> 来源：Suno 官方文档 × 社区验证 | 适合：Custom Mode 用户，需要精确控制歌曲结构 | 优先级：**中**
> **⚠️ 防污染声明**：本文档含示例内容（歌词/Prompt），仅供 agent 参考格式和结构。
> **歌词正文严禁直接复制输出**。正文必须是围绕用户需求的原创内容。

---

## 一、Suno 的两种创作模式

| 模式 | 界面 | 适合场景 | 控制精度 |
|------|------|---------|---------|
| **Simple Mode** | 单框输入自然语言描述 | 快速探索，灵感激发 | 低（AI 全权决定结构） |
| **Custom Mode** | Style 框 + Lyrics 框（分开） | 精细控制，专业创作 | **高（你控制一切）** |

**切换方式**：在 Suno 页面点击 `Custom Mode` 按钮。

---

## 二、双框填写规则

### Style 框（风格蓝图书写区）

- **字符限制**：1,000 字符（V4.5+）
- **内容类型**：流派、情绪、BPM、乐器、制作质感、人声特征
- **禁止混入**：歌词内容（会干扰音乐特征解析）
- **可以混入**：结构描述（如 `with verse-chorus-bridge structure`）

### Lyrics 框（歌词与结构控制区）

- **字符限制**：3,000 字符（V4.5+）
- **内容类型**：歌词文本 + Meta Tags（结构标签、人声标签、乐器标签）
- **核心功能**：Meta Tags 精确控制每个段落的风格

---

## 三、Meta Tags 分类速查

### 3.1 结构标签（最常用）

| 标签 | 含义 | 典型时长 |
|------|------|---------|
| `[Intro]` | 器乐开场/前奏 | 8–16 小节 |
| `[Verse]` / `[Verse 1]` | 主歌，叙事主体 | 4–8 行 |
| `[Verse 2]` | 第二段主歌 | 同上 |
| `[Pre-Chorus]` | 导歌，张力累积 | 2–4 行 |
| `[Chorus]` | 副歌，Hook，情感高潮 | 4–8 行 |
| `[Post-Chorus]` | 副歌后能量维持 | 2–4 行 |
| `[Bridge]` | 桥段，对比与转折 | 4–8 行 |
| `[Interlude]` | 器乐间奏 | 器乐段落 |
| `[Solo]` / `[Guitar Solo]` | 乐器独奏 | 器乐段落 |
| `[Break]` | 节奏中断/留白 | 1–4 小节 |
| `[Hook]` | 记忆点片段 | 1–2 行 |
| `[Outro]` | 尾奏收束 | 4–8 小节 |
| `[End]` | 明确终止 | 终止标记 |
| `[Fade Out]` | 渐弱至无声 | 指定渐弱 |

### 3.2 能量标签

| 标签 | 含义 | 适用位置 |
|------|------|---------|
| `[Energy: Low]` | 低能量，安静内敛 | Verse, Intro |
| `[Energy: Medium]` | 中等能量 | Verse 2, Post-Chorus |
| `[Energy: Rising]` | 逐步上升 | Pre-Chorus |
| `[Energy: High]` | 高能量，情感爆发 | Chorus |
| `[Energy: Maximum]` | 极限能量 | Final Chorus, Drop |
| `[Energy: Medium→High]` | 渐进过渡 | Bridge |
| `[Energy: Variable]` | 变化不定 | Bridge |

### 3.3 人声标签

#### 性别与组合

| 标签 | 含义 |
|------|------|
| `[Male Vocal]` / `[Male]` | 男声 |
| `[Female Vocal]` / `[Female]` | 女声 |
| `[Duet]` | 男女二重唱 |
| `[Group Vocals]` / `[Choir]` | 合唱/多人声 |
| `[Children's Vocal]` | 童声 |

#### 音色标签

| 标签 | 含义 | 效果 |
|------|------|------|
| `[Raspy]` | 沙哑 | 力量，沧桑 |
| `[Bright]` | 明亮 | 活泼，清透 |
| `[Breathless]` | 气声 | 空灵，亲密 |
| `[Soulful]` | 灵魂 | 深情，厚实 |
| `[Melodic]` | 旋律性 | 流畅，可唱 |
| `[Ethereal]` | 空灵 | 梦幻，超脱 |
| `[Gravelly]` | 粗哑 | 男人味，故事感 |

#### 唱法标签

| 标签 | 含义 | 适用场景 |
|------|------|---------|
| `[Whispered]` | 耳语 | 亲密开头，桥段 |
| `[Spoken Word]` | 口语念白 | 说唱，Intro |
| `[Belted]` | 强声爆发 | 副歌高潮 |
| `[Rapped]` | 说唱 | Rap Verse |
| `[Harmonized]` | 和声 | 副歌，桥段 |
| `[Harmony]` | 多声部和声 | 增强厚度 |
| `[Screamed]` | 嘶吼 | 金属，硬核 |
| `[Falsetto]` | 假声 | 过渡，高音点缀 |
| `[Chanted]` | 吟诵 | 仪式感，Hook |

#### 人声效果标签

| 标签 | 含义 |
|------|------|
| `[Auto-Tune]` | 电子音高修正 |
| `[Vocoder]` | 机器人声 |
| `[Telephone]` | 电话频段滤波 |
| `[Radio]` | AM 广播失真 |
| `[Distant]` | 远距离混响 |
| `[Intimate]` | 近距离拾音 |

### 3.4 乐器标签

#### 弦乐器

| 标签 | 乐器 | 备注 |
|------|------|------|
| `[Acoustic Guitar]` | 原声吉他 | 温暖，木质 |
| `[Electric Guitar]` | 电吉他 | 多种音色变化 |
| `[Distorted Guitar]` | 失真吉他 | 摇滚，金属 |
| `[Clean Guitar]` | 清音吉他 | 抒情，干净 |
| `[Nylon Guitar]` | 尼龙弦吉他 | 古典/西班牙/Bossa |
| `[Fingerpicked Guitar]` | 指弹吉他 | 民谣，细腻 |
| `[Piano]` | 钢琴 | 通用 |
| `[Electric Piano]` | 电钢琴 | Jazz, Soul |
| `[Rhodes]` |  Rhodes 电钢琴 | Lo-fi, Jazz |
| `[Strings]` | 弦乐（整体） | 通用铺底 |
| `[Violin]` | 小提琴 | 旋律高音 |
| `[Cello]` | 大提琴 | 低音弦乐，厚重 |
| `[Harp]` | 竖琴 | 空灵，梦幻 |

#### 管乐器

| 标签 | 乐器 |
|------|------|
| `[Saxophone]` | 萨克斯（爵士/灵魂） |
| `[Trumpet]` | 小号（爵士/拉丁） |
| `[Flute]` | 长笛（民谣/凯尔特） |
| `[Harmonica]` | 口琴（蓝调/民谣） |
| `[French Horn]` | 圆号 |

#### 打击乐器

| 标签 | 乐器/音色 |
|------|---------|
| `[Drums]` | 标准鼓组 |
| `[Electronic Drums]` | 电子鼓 |
| `[Live Drums]` | 现场鼓组感 |
| `[808]` | 808 鼓机低音 |
| `[909]` | 909 鼓机 |
| `[Percussion]` | 打击乐（康加/邦哥鼓） |
| `[Taiko]` | 太鼓（史诗） |

#### 合成器与电子

| 标签 | 音色/功能 |
|------|---------|
| `[Synth Pad]` | 合成器垫音（氛围） |
| `[Synth Lead]` | 主音合成器 |
| `[Synth Bass]` | 合成贝斯 |
| `[Arpeggiator]` | 琶音器 |
| `[Vinyl Crackle]` | 黑胶噪音（复古） |
| `[Tape Hiss]` | 磁带嘶声（复古） |

### 3.5 制作质感标签

| 标签 | 效果 | 适用风格 |
|------|------|---------|
| `[Lo-fi]` | 低保真，复古温暖 | Lo-fi, 怀旧 |
| `[Hi-fi]` | 高保真，干净清晰 | 商业，主流 |
| `[Cinematic]` | 电影感，动态大 | 影视配乐 |
| `[Raw]` | 原始粗粝 | 摇滚，民谣 |
| `[Polished]` | 精致专业 | 商业流行 |
| `[Intimate]` | 亲密感 | Ballad，抒情 |
| `[Hall Reverb]` | 大厅混响（宏大） | 史诗 |
| `[Room Reverb]` | 房间混响（亲密） | Ballad |
| `[Plate Reverb]` | 金属板混响（复古） | 复古，Soul |

### 3.6 调性与节奏标签

| 标签 | 含义 | 备注 |
|------|------|------|
| `[Major Key]` | 大调 | 明亮，积极 |
| `[Minor Key]` | 小调 | 忧郁，悲伤 |
| `[4/4]` | 四拍子 | 默认 |
| `[3/4]` | 三拍子 | 圆舞曲 |
| `[6/8]` | 六拍子 | 史诗，抒情 |
| `[Swing]` | 摇摆节奏 | Jazz, Blues |
| `[Shuffle]` | 洗牌节奏 | Blues, Rock |
| `[Accelerando]` | 渐快 | 戏剧性增长 |
| `[Ritardando]` | 渐慢 | 收束 |

---

## 四、段落级精细控制（V5 参数语法）

在 V5 版本中，可以用冒号语法为单个段落附加局部指令：

```
[Verse: whispered vocals, acoustic guitar only]
[Verse 2: building energy, full band enters]
[Chorus: full vocals, powerful belting, hall reverb]
[Bridge: a cappella, emotional, intimate]
```

---

## 五、标准结构模板

### 通用流行结构（ABABCB）

```
[Intro | low energy | atmospheric synth]
      ↓
[Verse 1 | low energy | intimate vocal, piano]
      ↓
[Chorus | high energy | full band, powerful vocal]
      ↓
[Verse 2 | medium energy | vocal, drums enter]
      ↓
[Chorus | high energy | same as above]
      ↓
[Bridge | medium→high energy | building, strings enter]
      ↓
[Final Chorus | maximum energy | full band, choir]
      ↓
[Outro | fading | energy decreasing]
```

### Lyrics Meta Tags 格式示例（参数级）

> ⚠️ 以下仅展示格式，不含任何歌词正文

```
[结构标签]（能量, 人声音色）
[Energy: 能量级别]
[Instrument: 乐器A, 乐器B]
[Vocal: 性别, 音色, 技术]
歌词正文（自主创作，不复制任何示例）

参数值来源：
  能量级别：0-10量表
  人声音色：data/vocal-tags.yaml
  乐器配置：data/instrument-timbre.yaml
```


## 六、特殊技巧

### Callback 指令（Extend 时维持一致性）

当你用 Extend 续接歌曲时，在歌词开头使用：

```
[Callback: continue with the same vibe as the chorus, maintain the emotional intensity]
```

### 人声段落指定

```
[Solo Vocal | Female, Soulful, Belted]
```

### 多语言段落

在对应段落的歌词框中直接写对应语言歌词：

```
[Chorus]
[Vocal: Female, English]
Love is a melody...

[Bridge]
[Vocal: Female, Mandarin]
就算世界都改变...
```

### 纯器乐段落

使用 `[Instrumental]` 标签，Suno 会生成纯器乐：

```
[Instrumental]
[Energy: Rising]
[Instrument: Full orchestra, building]
[Duration: 8 bars]
```

---



## 八、Style-Lyrics 协同规则（核心）

> **最常见失败模式**：Style 和 Lyrics 各自为政，互相冲突
> **正确模式**：Style 设定音色基底，Lyrics Meta Tags 在此底色上做段落级动态变化

### 协同原则

```
Style（音色基底）：定义整首歌的音色方向
    ↓ 继承
Lyrics Meta Tags（段落动态）：在 Style 底色上做乐器/能量的增减
```

### 音色梯度设计模板

| 段落 | 乐器变化 | 能量变化 |
|------|---------|---------|
| Verse 1 | Piano + 1件核心（稀疏） | Low |
| Pre-Chorus | +Drums enter gradually | Rising |
| Chorus | Full band（全编制） | High |
| Verse 2 | Piano + 核心 + 1件新乐器 | Medium |
| Bridge | Piano Solo 或回归2件核心 | Medium |
| Final Chorus | Full band + 加强 | Maximum |
| Outro | 全撤，只留1件 | Low → Fade |

### 人声标签协同规则

| 段落 | 标签写法 |
|------|---------|
| Verse | female, breathy / intimate |
| Pre-Chorus | female, breathy, building |
| Chorus | female, emotional / full |
| Bridge | female, intimate, whispered |
| Final | female, emotional, full, harmonized |
| Outro | female, whispered |

### 禁止：Style-Lyrics 打架

```
❌ Style: intimate, breathy
   Lyrics: [Vocal: Female, Belted]        ← 音色矛盾

✅ Style: intimate, breathy
   Lyrics: [Vocal: Female, Emotional]       ← 同底色，强度递进

❌ Style: melancholic, intimate
   Lyrics: [Instrument: distorted guitar, heavy drums] ← 能量矛盾

✅ Style: melancholic, intimate
   Lyrics: [Instrument: Piano, Cello → Full Band] ← 递进式动态
```

### 乐器描述精确化

```
❌ 模糊：strings, drums
✅ 精确：[Soft Strings] / [Cello] / [Piano Solo] / [Drums Enter Gradually]
✅ 动态：Verse用稀疏 → Chorus用全编制 → Bridge回归核心
```


*来源：Suno 官方文档 × 社区验证 | suno-music-creator v3.0 | 2026-04-18*
