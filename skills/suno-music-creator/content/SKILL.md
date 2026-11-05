---
name: suno-music-creator
description: Create music with Suno AI (Chinese-first). Triggers on: "写歌"、"生成音乐"、"做个曲子"、"Suno"、"音乐创作" + any genre/scene/mood description. Handles full workflow: targeted song analysis → 作词人手法提取 → NA五元组 → GMIVE+T style prompt → 原创 lyrics → SI×W滑杆，全部参数化，防污染。
license: MIT
metadata:
  author: 小su
  version: "3.7.0"
  category: music
  tags: suno, music, chinese-lyrics, lyrics, music-creation, song-creation
---

# Suno 音乐创作助手 — 工作流指南

> **版本**: v3.7 防污染参数化版 | **语言**: 中文优先 | **Suno 模型**: V4.5（当前版本）

---

## ⚠️ 核心原则

```
❌ 禁止：
  收集 Suno 无法复刻的参数（精确BPM/和弦/曲谱/混音参数）
  歌词和风格提示词分开写再事后检查
  Style 和 Lyrics 的人声/情绪/能量不一致
  复制任何 .md 文件中的歌词正文或完整 Prompt 示例
  在 Style Prompt 中使用艺术家/歌手名称

✅ 必须：
  只收集 Suno 能复刻的参数
  歌词和 Style Prompt 基于同一 NA 五元组同步生成
  歌词正文 100% 原创，不含任何已有歌词片段
  用音色参数替代艺术家名称
  输出必须包含完整三件套（Style Prompt + Lyrics + SI×W）
  音频分析失败时，复制文件到 /workspace/ 无括号路径重试，再失败才用搜索数据

### ⚠️ 原曲歌词禁令（v3.7.1·核心防污染）

```
【禁令】原曲歌词永远不进入创作过程

触发条件：搜索词含"歌词"或"曲谱" → 直接污染
触发条件：歌词正文出现原曲歌词片段 ≥3字相同 → 污染

搜索阶段（禁用）：
  ❌ 搜"海阔天空歌词"
  ❌ 搜"水手歌词完整版"
  ❌ 搜"千千阙歌歌词"
  ✅ 搜"海阔天空网易云热评情感"
  ✅ 搜"水手创作背景分析"
  ✅ 搜"千千阙歌情感逻辑"

理解阶段（区分用户概念）：
  用户概念 ≠ 原曲歌词素材
  用户说"亲爱滴" → 判断：是用户给的方向，而非原曲歌词片段
  → 若无法判断，拒绝创作并要求澄清

提取阶段（禁用手法原文）：
  ❌ 方文山歌词原文（"窗外的麻雀"/"秋刀鱼"）
  ✅ 方文山手法：MTV蒙太奇 + 具体物件入诗 → 新意象
  ❌ 林夕歌词原文（"爱情万歳"）
  ✅ 林夕手法：用意象说情绪，不直说 → 新意象

输出前自检（8条·全过才算完成）：
□ 三件套完整（Style Prompt + Lyrics + SI×W，缺一 = 未完成）
□ 歌词正文无原曲歌词片段（≥3字相同）
□ 搜索记录不含"歌词/曲谱"关键词
□ Vocal 参数来自 data/vocal-tags.yaml（非自创词）
□ 音频文件路径无括号（否则工具读取失败）
□ Exclude 格式为 --no（不是 —no）
□ Style Prompt 无艺术家名称
□ NA 五元组从热评情感逻辑提取（非原曲歌词）
```
---

## 完整工作流（7步·默认调用）

```
Step 1  音频分析  → 音频文件 → 精准音乐参数（BPM/音色/节奏/混音/人声技术）
Step 1b 网上搜索  → 歌曲 + 热评 → 歌词内容/情感逻辑/创作背景
Step 2  判断     → 逐项判断每项参数能否复刻
Step 3  提取     → 能复刻的参数 → 写入GMIVE+T
Step 4  NA五元组 → 网易云热评情感逻辑 → 丢弃具体人名地名 → 保留行为模式
Step 5  同步创作 → Style Prompt（基于音频参数）+ Lyrics（基于热评情感）同步生成
Step 6  自检     → 防污染6条 + 可唱性5条
### Step 7  三件套   → 输出前必须同时完成两件事：
  ① 发给用户（展示）
  ② 写入 `/生成结果/YYYY-MM-DD/序号_歌名_风格_技术档案.md`（归档）

> ⚠️ **归档优先于一切对话**：文件写进去才算完成。只发给用户不算完成。
```

### 信息来源分工（双轨制·禁止区）

| 信息类型 | 来源 | 精度 | 允许 |
|---------|------|------|------|
| 精确BPM | 音频分析 | ✅ 精确 | ✅ |
| 乐器音色/演奏方式 | 音频分析 | ✅ 精确 | ✅ |
| 人声技术（气声/真假声/懒散处理）| 音频分析 | ✅ 精确 | ✅ |
| 混音技术（Reverb/EQ/声场）| 音频分析 | ✅ 精确 | ✅ |
| 情感逻辑 | 网易云热评（**非原曲歌词**）| ✅ 可提取 | ✅ |
| 创作背景/主题 | 网上搜索（**非原曲歌词**）| ✅ 可提取 | ✅ |
| 歌词正文内容 | **禁止** | — | ❌ |
| 原曲歌词片段 | **禁止搜索** | — | ❌ |
| 作词人手法的歌词原文 | **禁止复制** | — | ❌ |
| 创作背景/主题 | 网上搜索 | ✅ 可获取 |
| 作词人手法人格 | 网上搜索 + 分析 | ✅ 可提取 |

> **注意**：有音频文件时，优先音频分析 → 音频给参数精度，搜索给歌词灵魂，两者缺一不可。

---

## Step 1：定向歌曲分析

### ✅ 只收集这些（Suno可复刻）

| 参数 | 具体内容 | 来源 |
|------|---------|------|
| Genre / Subgenre | 曲风大类+子风格 | `data/genres.yaml` |
| Tempo Feel | slow/fast/mid快慢感，不用数字 | `data/bpm-guide.yaml` |
| Mood | 核心情绪词，1-2个 | `data/moods.yaml`（Russell象限）|
| Instruments（含音色）| 2-4种，含音色描述 | `data/instrument-timbre.yaml` |
| Vocal | 性别+音色+技术+制作效果 | `data/vocal-tags.yaml` |
| Sound Signature | 声场+制作质感 | `data/production-tags.yaml` |
| Exclude | 排除项 | 手动构造 |

### ❌ 这些不收集

| 参数 | 原因 |
|------|------|
| 精确 BPM 值 | Suno 近似，收集了反而误导 |
| 具体和弦进行 | Suno 无法精确控制 |
| 混音参数 | Suno 无法精确控制 |
| 录音棚信息 | 无法复现 |

---

## Step 2：复刻判断

> 搜索完成后，逐项判断每一项参数能否被 Suno 复刻。搜到了才能判断，判断后才能提取。

### 判断矩阵

| 参数 | 能复刻 | 不可复刻 |
|------|--------|---------|
| Genre + Tempo Feel | ✅ 曲风大类 + 速度感描述词 | ❌ 精确 BPM 数字 |
| Mood | ✅ Russell情绪词1-2个 | ❌ 过度具体的情绪描述 |
| Instrument + Timbre | ✅ 乐器名 + 音色描述词 | ❌ 具体话筒型号 |
| Vocal | ✅ 性别+音色+技术+制作 | ❌ 歌手名字、录音棚名 |
| Sound Signature | ✅ 声场/质感描述词 | ❌ 精确混音参数（EQ/压缩）|
| 和弦进行 | ❌ 无法精确复刻 | — |
| 调性 / 转调 | ❌ 无法精确复刻 | — |
| 录音棚信息 | ❌ 无法复刻 | — |

### 判断后动作

```
搜索拿到完整分析
    ↓
逐项判断能否复刻
    ↓
能复刻 → 写入 GMIVE+T 对应槽位
不能复刻 → 丢弃，注明原因（不入 Style Prompt）
```

---

## Step 3：GMIVE+T 参数提取

### DNA 六维参数（`author-dna.md`）

```
分析目标歌曲时，提取六个维度：
□ 反复出现的主题（≥3次）
□ 高频意象（具体物品/场景词频）
□ 标志性句式结构（短句型/场景型/直白型）
□ 核心哲学/价值观（一句话）
□ 押韵习惯（常用韵辙）
□ 情绪走向（悲伤→释然？压抑→爆发？）
```

### 三要素绑定（SYNTAX_pattern 决定形式）

```
林夕式（短句型）：
  结构："主语" + "行为"（两句分开，不写结果）
  三要素：留白，让听众自己补结果

方文山式（场景型）：
  结构："主语+行为+场景细节"（一句内完成）
  三要素：画面感强，结果融在场景里

李宗盛式（直白型）：
  结构："因为X，所以我Y"（一句说清因果）
  三要素：真实感强，结果直接给出
```

---

## Step 4：热评情感提取 → NA五元组

> ⚠️ **硬规则：原曲歌词永远不进入创作过程**
> 搜索只搜热评/创作背景/风格分析，**绝对不能搜索原曲歌词**

```
Step 4a：搜索热评情感（网易云/豆瓣/知乎评论）
          → 提取"行为模式/情感逻辑/时间代价/空间等待"
Step 4b：丢弃：
  ❌ 原曲歌词片段（≥3字相同）
  ❌ 具体数字/具体地名/人名
  ❌ 热评原文完整句子
  ✅ 保留：情感逻辑、行为模式、时间代价
Step 4c：用保留内容 + 作词人手法参数 → 生成全新意象
```

**禁止行为：**
```
❌ 搜索原曲歌词（曲谱网/歌词网）
❌ 把"搜索歌词"当作工作流步骤
❌ 把原曲意象换几个字当新词
❌ 把歌名当情感逻辑用
❌ 把用户概念混用为原曲歌词片段
```

---

## Step 5：同步创作

### GMIVE+T 公式

```
G(Genre+Tempo) → M(Mood) → I(Instrument+Timbre)
→ T(Sound Signature) → V(Vocal) → E(Exclude)
```

**参数来源（必须对照数据文件选取）：**
| 槽位 | 来源 | 规则 |
|------|------|------|
| G | `data/genres.yaml` + `data/bpm-guide.yaml` | **Genre 只写1个**，Tempo 用 term；中文歌曲加 `mandarin` / `cantonese` 前缀；**禁止写精确BPM数字** |
| M | `data/moods.yaml`（Russell象限）| **≤ 2个独立情绪词**，选自不同类别；genre 自带的 mood 不重复计入 |
| I | `data/instrument-timbre.yaml` | **2-4种**，每种须含音色描述（sparse/warm/bright 等），不只写乐器名 |
| T | `data/production-tags.yaml` | 声场/制作质感，1-2个 |
| V | `data/vocal-tags.yaml` | **性别（male/female/mixed）+ 音色（warm/breathy 等）+ 技术（belted/whispered 等）+ 制作（close-miked 等）**，共4个字段，性别必填 |
| E | 手动构造 | ≤ 6项，用 `--no xxx` 格式，**加引导语"Exclude these styles:"**，置于 Style Prompt 末尾 |

**V5.5 描述词数量：4-7 个为最优（太少→太泛，太多→冲突）**

### Lyrics 格式（`lyrics-meta-spec.md` + `lyrics-chinese.md`）

```
段落标签（lyrics-structure.md）：
  [Intro] / [Verse] / [Pre-Chorus] / [Chorus]
  [Verse 2] / [Bridge] / [Final Chorus] / [Outro]

行内标签（lyrics-meta-spec.md）：
  Verse → （soft, intimate, tired breathy）
  Pre → （building, breathing）
  Chorus → （sustained, emotional belting, full voice）
  Bridge → （sparse, whispered）
  Outro → （fade, acoustic only）

韵辙（lyrics-chinese.md 十三辙）：
  Chorus 优先：eng/ang/ou/ai 韵（可唱性最高）
  高风险韵（i/u）：仅 Bridge/Outro 使用
```

### 粤语歌词写法（`Cantonese_Song_Guide.md`）

> **注意**：Suno 默认按普通话音系唱歌，粤语歌曲需加粤拼（Jyutping）标注才能正确发音。

```
格式：歌词正文[粤拼拼音]

示例：
人群中間 我在找自己[jam4 kwan4 zung1 gaan3 ngo5 zai6 zaau6 zi6 gei2]
霓虹燈下 一切變得模糊[nei4 hung4 dang1 haa6 jat1 cai3 bin3 dak1 mo4 fu1]

步骤：
1. 歌词正文用繁体中文
2. 每行末尾加 [粤拼拼音标注]
3. Style Prompt 加 cantonese song + cantonese vocal articulation
4. Exclude 加 --no mandarin pronunciation
详细说明见：Cantonese_Song_Guide.md
```
```

### 音节密度（`syllable-guide.md`）

```
±2规则：同段落相邻行音节差 ≤ 2

密度曲线：
  0 → 低 → 中低 → 高 → 低 → 中低 → 高 → 极低 → 最高 → 低
  I  V  Pre C  V2 Pre C2  Bridge Final  Outro
```

---

## Step 6：防污染 + 可唱性检查

### 防污染三原则（v3.7核心·更新）

```
原则1：意象从热评情感逻辑 + NA五元组生发，不借用原曲意象
原则2：作词人手法用于润色，不用于复制原文
原则3：逐行排查，超过5字与原曲歌词相同 → 必须重写
原则4：【新增】原曲歌词永远不进入创作过程（Step 4硬规则）
```

### 防污染自检（每首歌必过·8条全检）

```
□ 未复制任何 .md 参考文件的歌词正文或完整 Prompt 示例
□ 歌词正文 100% 原创，无任何已有歌词片段
□ Style Prompt 不含艺术家/歌手名称（用音色参数替代）
□ NA 五元组从热评情感逻辑提取，未直接复制热评原文
□ 作词人手法参数用于润色生成，非复制原文
□ 搜索范围：热评情感/创作背景/风格分析，不含原曲歌词
□ 逐行排查：与原曲歌词超过5字相同 → 必须重写
□ 【新增检查】歌词正文不出现原曲歌词片段（"原谅我这一生"/"舵盘"/"来日纵有"等）
```

### 可唱性检查（必过·5条）

```
□ 多音字已处理：还/着/了/地/得/长/行
□ Chorus 每行至少一个开口音韵母（eng/ang/ai/ao/ou）
□ 同段落相邻行音节差 ≤ 2（±2规则）
□ Vocal 含性别字段（male/female/mixed）
□ Genre 只写1个，Tempo 用 term 而非精确 BPM 数字
```

### 污染判定标准

```
以下情况视为污染：
  □ 原曲歌词完整短语超过5字相同
  □ 热评原文完整句子
  □ 原曲核心意象直接使用（特定意象词）

以下情况不算污染：
  □ 共用常见意象（风/雨/海/路）—— 常见词人人用
  □ 共用情感逻辑（离别/追梦/遗憾）—— 情感共通
  □ 共用押韵韵脚（ang/eng/ai）—— 韵辙共用
```
□ 韵辙和意象均为重新生成，非原文保留
```

---

## Step 7：三件套输出

### 三件套结构

```
┌──────────────────────────────────────────────┐
│  Style Prompt（风格框·纯提示词）               │
│  Genre, tempo term                           │
│  mood1, mood2                                │
│  instrument1(timbre), instrument2(timbre)... │
│  sound-signature                              │
│  vocal: gender, timbre, technique, production│
│  --no exclude1 --no exclude2 ...             │
├──────────────────────────────────────────────┤
│  Lyrics（歌词框·含 Meta Tags）                 │
│  [Intro]（energy, vocal）                    │
│  [Verse]（energy, vocal）                    │
│  原创歌词正文（不复制任何示例）                 │
├──────────────────────────────────────────────┤
│  Generation Settings（生成界面滑杆）            │
│  Style Influence: 数值                       │
│  Weirdness: 数值                              │
└──────────────────────────────────────────────┘
```

### SI×W 滑杆值（参考范围）

| 任务类型 | Style Influence | Weirdness |
|---------|---------------|-----------|
| 风格复刻（参考原歌曲）| 78–84 | 22–28 |
| 商业保守（安全生成）| 70–80 | 15–22 |
| 创意探索（全新方向）| 60–75 | 28–35 |

---

## Reference 文件速查

### 数据文件（`data/`）
| 文件 | 内容 | 必须读取 |
|------|------|---------|
| `genres.yaml` | 10大类 × 120+子流派 | ✅ |
| `bpm-guide.yaml` | Tempo-Term融合 + BPM×字数对照 | ✅ |
| `moods.yaml` | Russell 16情绪坐标 + BPM匹配 | ✅ |
| `instrument-timbre.yaml` | 8乐器家族 × 48音色变体 | ✅ |
| `production-tags.yaml` | 6维度 × 45质感标签 | ✅ |
| `vocal-tags.yaml` | 21音色 + 9技术 + 7能量 | ✅ |

### 参考文件（`references/`）
| 文件 | 内容 |
|------|------|
| `style-prompt-spec.md` | GMIVE+T 公式 + 合规检查 |
| `lyrics-meta-spec.md` | 两层 Meta Tags + 行内标签 |
| `lyrics-structure.md` | 段落结构 + Style-Lyrics 协同 |
| `lyrics-chinese.md` | 十三辙押韵 + 作词人手法 + 三要素绑定 |
| `lyrics-parametric.md` | NA五元组 + BPM×字数公式 + 可唱性规则 |
| `chinese-singability.md` | 多音字替换表 + Chorus开口音规则 |
| `syllable-guide.md` | ±2音节规则 + 密度层次曲线 |
| `author-dna.md` | DNA六维提取 + 四步复刻技术 |
| `quick-ref.md` | 出门前速查（合规检查+SI×W）|

### 场景速查
| 需要什么 | 文件 |
|---------|------|
| 不知道什么风格 | `style-by-scene.md` |
| 有风格方向 | `style-by-genre.md` |

---

*本技能专注于 Prompt 构造和歌词创作指导，不涉及音频文件处理或账号管理。*
