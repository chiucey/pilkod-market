---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b1fb83bfddd6c5a801d18d5225a5b87c
    PropagateID: b1fb83bfddd6c5a801d18d5225a5b87c
    ReservedCode1: 304602210090eeaf008183ae2bc6180b3e9209c1fa0d6e014fba36be48ffb016ff1b078318022100994864eab0fd2874ab6ccfad64bf78d4a4bef95e194c7bb5f0c53c99bad5d301
    ReservedCode2: 304502204053411eabef96474f174da9734b8e7622575aaa649c678212d199adb5f017b802210090c9a014f6ff3f2a9247797e34aaa7afe5373aec65a7e8769e5cdfbca9e00b57
description: 短剧AI分镜提示词生成流水线。自动将中文分镜剧本转换为Grok视频提示词，支持空间定位、人物比例约束、镜头衔接、情绪连贯性检查。当用户需要根据中文剧本生成Grok分镜提示词、生成AI短剧提示词、生成短剧分镜、按照剧本生成提示词时触发此技能。
name: grok-drama-pipeline
---

# Grok Drama Pipeline · 短剧AI分镜提示词生成流水线

将中文分镜剧本 → 生成符合Grok规范的视频提示词，包含完整三层对照格式。

---

## 核心原则

1. **原文优先** — 英文提示词必须完整覆盖原剧本所有核心要素，不得遗漏
2. **空间定位** — 2人以上同框镜头，必须写 SPATIAL SETUP；单人镜头跳过
3. **人物比例约束** — 多人同框场景，必须标注 Scale 比例，禁止"taller/smaller"
4. **承上启下** — 每个镜头开头标注 `[承接上一镜：...]`，保证角色位置和情绪连贯
5. **情绪链条** — 情绪变化必须平滑过渡，不能跳跃（震惊→恐慌→绝望→崩溃）
6. **格式统一** — 每镜头三层结构：中文原文 / English Grok Prompt / 中文翻译

---

## 输出格式（三层结构）

每个镜头输出顺序：

```
【中文原剧本】（飞书文档一字未改）

【English Grok Prompt】

【英文提示词 · 中文翻译】

【原文 → 提示词 · 核查】（每个镜头必做）
```

---

## 镜头分类判断

```
Q1：几个角色？
  1个 → 跳过 SPATIAL SETUP，直接写 SUBJECT + ACTION + CAMERA
  2个以上 → 必须写 SPATIAL SETUP

Q2：是否承接上一镜？
  是 → 在 SPATIAL SETUP 前加 [承接：...]
  否 → 正常写

Q3：情绪是否在变化？
  是 → 检查情绪是否平滑过渡，不跳跃
  否 → 保持当前情绪
```

---

## SPATIAL SETUP 写法（四层）

```
SPATIAL SETUP
角色A: [LEFT/RIGHT/CENTER/TOP/BOTTOM] of frame → [方向]
角色B: [LEFT/RIGHT/CENTER/TOP/BOTTOM] of frame → [方向]
Direction: [谁] 从 [哪] 走向 [哪]
Scale: [所有角色身高比例必须一致；固定角色与移动角色同比例]
[承接：上一镜结尾状态]
```

**比例标注规则（核心！）：**

```
Scale: MASON and LILY must be same height ratio throughout —
       both full body in same frame, same proportion
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

**比例标准（多人场景必须标注）：**
| 场景类型 | 固定角色 | 移动角色 | 比例规则 |
|---------|---------|---------|---------|
| 双人中景 | 主体与镜头等距 | 与固定者同距 | 两人身高相同比例 |
| 双人特写 | 主体脸部特写 | 与主体同框 | 两人脸部比例一致 |
| 三人场景 | MASON居中 | 左右配角 | MASON略高或同等 |
| 前景+背景 | 背景人物 | 前景人物 | 背景人物略小 |

**方位标准：**
- `TOP` = 王座端/远端/上方
- `BOTTOM` = 群众端/近端/下方
- `LEFT / RIGHT` = 画面左右侧
- `CENTER` = 画面中央

---

## Grok 提示词结构（每个镜头必须包含）

```
SUBJECT:    人物外貌 + 服装（简洁）
ACTION:     核心动作，1-2句，精确描述每个人在做什么
EMOTION:    情绪基调
CAMERA:     具体运镜（必须每1-3秒移动）
MOOD:       氛围

【必写约束】
FORMAT:     vertical 9:16 | 1080P | 25fps | H.265 | 10 seconds
CAMERA:    Must move every 1-3 seconds
PROHIBITED: No slow motion | No empty shots | No Asian features
SCALE:     All characters same height ratio — no size changes
```

---

## 情绪连贯性原则

| 情绪层级 | 程度 | 适用场景 |
|---------|------|---------|
| shock | 震惊 | 初次面对打击，呆住 |
| panic | 恐慌 | 意识到严重性，开始崩溃 |
| despair | 绝望 | 完全无力，情绪谷底 |
| collapse | 崩溃 | 彻底失控，爆发或麻木 |

**演变规则：**情绪只能逐级演变，不能跳级（如：震惊→崩溃 是错误的）

---

## 承上启下处理

每个镜头检查：
1. 上个镜头结尾时，角色在哪个位置？
2. 这个镜头开头，角色还在那个位置吗？
3. 情绪是否平滑衔接？

**接不上时，在 ACTION 开头加承接句：**
```
[承接上一镜：MASON已在王座就位，SELENE站在MASON身旁]
```

---

## 角色定位原则

- **MASON**：固定王座（TOP），走向王座或王座上
- **SELENE**：MASON右侧，始终伴随
- **LILY**：红毯近端（BOTTOM)，群众前方
- **GUARDS**：左右两侧前景
- **空间约定**：先建坐标系，全集通用，不乱改
- **比例约定**：同框所有角色身高比例必须一致，不随位置变化

---

## 参考文件

详细模板和示例请阅读：
- [references/scene_coords_template.md](references/scene_coords_template.md) — 场景坐标系模板
- [references/shot_prompt_template.md](references/shot_prompt_template.md) — 分镜提示词模板（含比例字段说明）
- [references/mandatory_constraints.md](references/mandatory_constraints.md) — 必写约束清单（含人物比例约束）
- [references/emotion_chain.md](references/emotion_chain.md) — 情绪链条设计指南
