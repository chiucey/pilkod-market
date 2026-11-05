# 必写约束清单

每个镜头必须包含以下约束，不得遗漏。

---

## 基础规格约束（每镜必写）

| 约束项 | 标准值 | 说明 |
|--------|--------|------|
| 画幅 | `vertical 9:16` | 竖屏必须写 |
| 分辨率 | `1080P` | 高清必须写 |
| 帧率 | `25fps` | 标准帧率 |
| 编码 | `H.265` | 必写 |
| 时长 | `10 seconds` | 每卡10秒 |

---

## 镜头约束（每镜必写）

| 约束项 | 标准值 |
|--------|--------|
| 运镜 | `Must move camera every 1-3 seconds — no static shots` |
| 禁止慢镜头 | `No slow motion`（开篇3秒除外）|
| 禁止空镜 | `No empty establishing shots` |
| 禁止纯场景 | `No scenery-only shots` |
| 每镜有内容 | `Every shot must contain character action or interaction` |

---

## 人物约束（必须标注）

```
SUBJECT RULE: Western Caucasian actors only — NO Asian features
```

---

## 慢镜头例外规则

以下场景允许慢镜头：
- 开篇3秒（Golden Hook）
- 已批准的动作片段（坠落、打斗、爆发）
- 镜头末尾淡出（End fade）

写法：
```
NOTE: Slow motion ALLOWED — opening 3 seconds exempt
```
或：
```
NOTE: Slow motion ALLOWED — approved action sequence
```

---

## 配音约束

| 约束项 | 标准值 |
|--------|--------|
| 口音 | `American English only` |
| 风格 | `Emotional, natural, conversational` |
| 模型 | `elevenlabs v3` |
| 禁止 | `No dubbed content, no robotic TTS` |

---

## 音乐约束

| 约束项 | 标准值 |
|--------|--------|
| 版权 | `NO UMG / Sony / Warner` |
| BPM | `above 120` |
| 风格 | `epic orchestral` |
| 来源 | `Epidemic Sound / Artlist / YouTube Audio Library` |

---

## 成片格式

```
MP4 | 1080P | 25fps | H.265
English subtitles required
```

---

## 标注格式模板

```
【必写约束】
FORMAT:     vertical 9:16 | 1080P | 25fps | H.265 | 10 seconds
CAMERA:    Must move every 1-3 seconds
PROHIBITED: No slow motion | No empty shots | No Asian features
```

---

## 人物比例约束（多人镜头必须标注）

```
SCALE: All characters in same frame must maintain consistent height ratio
       — same scale throughout, no size changes between cuts
       Fixed character and moving character: SAME proportion ratio
       DO NOT use "taller than / smaller than" → use "same scale"
```

**比例标注示例：**
```
Scale: MASON and LILY same height ratio — both full body in frame,
       MASON slightly ahead in composition; LILY at same scale
Scale: SELENE and LILY same scale — both visible head to feet,
       SELENE in foreground left, LILY in background right, same proportion
```

**比例禁止词：**
```
❌ "MASON taller than LILY"
❌ "LILY smaller than SELENE"
❌ "background character smaller"
✅ "same height ratio"
✅ "same scale throughout"
✅ "all characters same proportion"
```

---

## 多人镜头额外约束

```
All characters must appear in SAME FRAME throughout the shot
All characters must maintain consistent SCALE throughout the shot
Fixed character and moving character: SAME proportion ratio
```

同框要求必须写入 SPATIAL SETUP，比例标注用 Scale 字段。
