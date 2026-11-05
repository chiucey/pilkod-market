# 粤语歌曲 Suno 生成专项指南 v1.0

> 来源：Suno 社区验证 + Twitter/Suno4.cn 实践教程
> 版本：v1.0 | 更新：2026-04-20
> 用途：解决 Suno 生成粤语歌曲时发音不准的问题

---

## 一、问题：Suno 唱普通话不唱粤语

**现象：**
- Style 里写了 `cantonese`，但 Suno 还是唱普通话发音
- 歌词是粤语字，但唱出来是普通话调

**根本原因：**
Suno 的 TTS（文字转语音）默认基于普通话音系，没有粤语的声调信息。
粤语有6个声调（vs 普通话4个），声调决定词义，Suno 无法自动识别。

---

## 二、解决方案：粤拼（Jyutping）标注

> "把歌词扔给语言模型，让他给出粤语拼音标注，然后贴到Suno歌词框里，在style写上 cantonese song" — Suno4.cn 实践验证

**核心原理：**
粤拼标注 = 把每个字的音调标出来 → Suno 识别后按粤拼发音唱歌

---

## 三、歌词格式（粤拼标注版）

### 标准格式

```
[Intro] [vocal:male, language:Cantonese]
歌词正文[粤拼拼音]
```

### 标注规则

```
歌词正文[粤拼拼音]

示例：
人群中間 我在找自己[jan4 kwan4 zung1 gaan3 ngo5 zai6 zaau6 zi6 gei2]
霓虹燈下 一切變得模糊[nei4 hung4 dang1 haa6 jat1 cai3 bin3 dak1 mo4 fu1]
```

### 粤拼标注位置

```
每行歌词末尾
[拼音]紧跟在歌词后面，中间无空格
```

---

## 四、粤拼速查要点

### 声调标注

| 声调 | 粤拼标注 | 示例字 |
|------|---------|-------|
| 高平（阴平）| 1 | 詩[si1] |
| 高降（阴上）| 2 | 史[si2] |
| 低升（阳平）| 3 | 時[si3] |
| 低降（阳上）| 4 | 市[si4] |
| 高平（阴去）| 5 | 試[si5] |
| 低降（阳去）| 6 | 是[si6] |

### 标注原则

```
逐字标注，不要整句标注
每行歌词末尾加 [粤拼]
中文正文保持繁体（粤拼更准确）
```

---

## 五、Style Prompt 粤语增强写法

### 标准格式

```
cantonese pop/cantonese ballad/cantonese rnb,
[tempo term],
[mood1], [mood2] mood,
[instruments],
male/female vocal, [timbre], [technique], hall reverb,
cantonese song, cantonese vocal articulation,
[production signature]
Exclude these styles:
--no mandarin pronunciation --no auto-tune --no [genre]
```

### 示例（带感粤语舞曲）

```
cantonese pop dance, moderate, 118 BPM,
nostalgic, energetic, bittersweet mood,
electric guitar(punchy), synth-pad(bright),
four-on-floor kick(dynamic), bass(gritty),
male vocal, rough, emotional, belted, hall reverb,
cantonese song, cantonese vocal articulation,
loud, club, energetic production
Exclude these styles:
--no mandarin pronunciation --no ballad --no acoustic
```

### 示例（抒情粤语 ballad）

```
cantonese ballad, slow andante,
nostalgic, romantic mood,
warm piano(intimate), orchestral strings(soaring),
soft drums(gentle), fretless bass(warm),
female vocal, breathy, emotional, close-miked,
cantonese song, cantonese vocal articulation,
warm, intimate, nostalgic production
Exclude these styles:
--no mandarin pronunciation --no synth pop --no heavy drums
```

---

## 六、Lyrics Meta Tags 粤语写法

### 结构标签

```
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Pre-Chorus]
[Chorus]
[Bridge]
[Final Chorus]
[Outro]
```

### 行内标签（粤语适用）

```
[Intro]（intimate, piano solo）
[Verse]（soft, breathy, intimate）
[Pre-Chorus]（building, breathing）
[Chorus]（sustained, emotional belting, full voice）
[Bridge]（sparse, whispered）
[Outro]（fade, acoustic only）
```

### 段落标签中的语言标注

```
[Intro] [vocal:male, language:Cantonese]
[Verse 1] [vocal:female, language:Cantonese]
```

---

## 七、避坑指南

### ❌ 错误做法

| 错误 | 后果 |
|------|------|
| 只写 `cantonese` 不加粤拼标注 | Suno 仍唱普通话发音 |
| 用简体字标注粤拼 | 粤拼基于繁体，声调不准确 |
| 粤拼标在整句前 | Suno 无法正确识别每个字音调 |

### ✅ 正确做法

| 正确 | 原因 |
|------|------|
| 歌词末尾逐字加 [粤拼] | 每个字对应正确声调 |
| 中文正文用繁体 | 粤拼基于繁体字 |
| Style 加 `cantonese song` | 双重保障 |

---

## 八、生成流程

```
Step 1：创作粤语歌词（繁体中文）
Step 2：为每行歌词添加粤拼标注
Step 3：填写 Style Prompt（含 cantonese song）
Step 4：在 Lyrics 框贴入带粤拼的歌词
Step 5：设置 SI×W 滑杆
Step 6：生成
```

---

## 九、AI 辅助标注提示词

如果需要 AI 帮助标注粤拼，可用以下提示词：

```
请为以下歌词添加粤拼（Jyutping）拼音标注，
格式：[字]拼音，逐字标注，标在每行歌词末尾。
保持繁体中文歌词正文，只添加拼音标注。

歌词：
（此处粘贴歌词）
```

---

*suno-music-creator v3.7 | Cantonese Song Guide v1.0 | 2026-04-20*
