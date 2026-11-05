# 分镜提示词模板

每个镜头使用以下模板，严格按顺序填写。

---

## 单人镜头模板（无 SPATIAL SETUP）

```
【中文原剧本】（飞书文档一字未改）

【English Grok Prompt】

SUBJECT:    [人物外貌 + 服装简洁描述]
ACTION:     [核心动作，1-2句，精确描述]
EMOTION:    [情绪基调]
CAMERA:     [具体运镜，必须每1-3秒移动]
MOOD:       [氛围]

【必写约束】
FORMAT:     vertical 9:16 | 1080P | 25fps | H.265 | 10 seconds
CAMERA:    Must move every 1-3 seconds
PROHIBITED: No slow motion | No empty shots | No Asian features

VOICEOVER（如有台词）
Line: "[台词原文]"
Accent: American English
Emotion: [情绪]
Voice:   [角色名], [性别], [音色]
Platform: elevenlabs v3

【英文提示词 · 中文翻译】

【原文 → 提示词 · 核查】
[原句] → [提示词对应表达]
```

---

## 多人镜头模板（含 SPATIAL SETUP）

```
【中文原剧本】（飞书文档一字未改）

【English Grok Prompt】

SPATIAL SETUP
角色A: [LEFT/RIGHT/CENTER/TOP/BOTTOM] of frame → [方向]
角色B: [LEFT/RIGHT/CENTER/TOP/BOTTOM] of frame → [方向]
Direction: [谁] 从 [哪] 走向 [哪]
Scale: [所有角色身高比例必须一致；固定角色与移动角色同比例]
[承接：上一镜结尾状态]

SUBJECT:    [所有人物外貌 + 服装 + 比例说明]
ACTION:     [每个角色各自做什么，1-2句]
EMOTION:    [情绪基调]
CAMERA:     [具体运镜，必须每1-3秒移动]
MOOD:       [氛围]

【必写约束】
FORMAT:     vertical 9:16 | 1080P | 25fps | H.265 | 10 seconds
CAMERA:    Must move every 1-3 seconds
PROHIBITED: No slow motion | No empty shots | No Asian features

VOICEOVER（如有台词）
Line: "[台词原文]"
Accent: American English
Emotion: [情绪]
Voice:   [角色名], [性别], [音色]
Platform: elevenlabs v3

【英文提示词 · 中文翻译】

【原文 → 提示词 · 核查】
[原句] → [提示词对应表达]
```

---

## SPATIAL SETUP 方位速查

| 方位 | 含义 | 适用场景 |
|------|------|---------|
| TOP of frame | 画面上方/远端 | 王座、悬崖顶、神殿深处 |
| BOTTOM of frame | 画面下方/近端 | 群众、近端、悬崖底 |
| LEFT of frame | 画面左侧 | 群众方向 |
| RIGHT of frame | 画面右侧 | 侍卫/仆从方向 |
| CENTER | 画面中央 | 神殿核心、互动区域 |
| FOREGROUND | 前景 | 前景动作 |
| BACKGROUND | 背景 | 背景人物 |

---

## CAMERA 运镜速查

| 运镜类型 | 适用场景 |
|---------|---------|
| Wide tracking shot — [角色] walking [方向] | 走红毯、行进 |
| Extreme close-up ECU, slow push-in | 表情特写 |
| Low angle hero shot | MASON威严镜头 |
| Over-the-shoulder | 两人互动 |
| Aerial top-down | 悬崖场景、全景 |
| Chaotic handheld | 混乱场面 |
| Slow-motion aerial | 坠落/动作片段 |
| Circle shot — rapid push-in | 围攻场面 |
