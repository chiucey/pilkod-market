# 歌词 Meta Tags 格式规范 v3.5

> ⚠️ 防污染声明：本文档为格式规范，无可复制正文。
> 用途：约束 agent 如何在歌词中嵌入 Meta Tags，控制 Suno 人声演绎

---

## 一、两层结构

```
段落层：控制整段的人声音色/能量/乐器
行内标签：控制单句的演唱方式/动态/情绪
```

---

## 二、段落层标签

```
[结构标签]（energy, vocal-timbre）
歌词正文...
```

标签来源：只从 lyrics-structure.md 合规段落类型选取，不自创。

---

## 三、行内标签

### 音量/动态

| 标签 | 含义 | 用法 |
|------|------|------|
| `（soft）` | 轻柔 | Verse |
| `（intimate）` | 亲密，近耳 | Intro/Verse |
| `（building）` | 渐强 | Pre-Chorus |
| `（sustained）` | 延音，拉长 | Chorus |
| `（full）` | 全音量 | Chorus |
| `（fade）` | 渐弱消散 | Outro |
| `（whispered）` | 耳语/气声 | Bridge |
| `（spoken）` | 口语念白 | Intro/Bridge |

### 人声音色

| 标签 | 含义 |
|------|------|
| `（breathy）` | 气声，亲密感 |
| `（emotional）` | 情感充沛 |
| `（emotional belting）` | 情感爆发+真声 |
| `（intimate）` | 亲密，近距离 |
| `（smooth）` | 流畅，滑顺 |
| `（raw）` | 未打磨，原始 |

### 段落专属组合

```
[Intro]（intimate, guitar alone）
[Verse]（soft, intimate, slow delivery）
[Pre-Chorus]（building, breathing）
[Chorus]（sustained, emotional belting, full voice）
[Bridge]（sparse, whispered）
[Outro]（fade, acoustic only）
```

---

## 四、合规自检

```
□ 段落层标签来源：lyrics-structure.md
□ 行内标签来源：本文件第三章
□ 中文歌词经 chinese-singability.md 可唱性检查
□ Chorus 每行有开口音韵母（a/o/e/ai/ou/eng/ang 结尾）
□ 同段落相邻行音节差 ≤ 2
□ 歌词正文是原创，不复制任何 .md 示例
□ Style 和 Lyrics 基于同一 NA 五元组
```

---

*格式规范 | suno-music-creator v3.5 | 2026-04-18*
