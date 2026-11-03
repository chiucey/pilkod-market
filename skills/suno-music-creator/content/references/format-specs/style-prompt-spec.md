# Style Prompt 格式规范 v3.7

> ⚠️ 防污染：本文档为格式规范/参数数据，无可复制正文。

---

## 一、GMIVE+T 公式

```
G(Genre+Tempo) → M(Mood) → I(Instrument+Timbre) → T(Sound Signature) → V(Vocal) → E(Exclude)
```

| 优先级 | 槽位 | 来源 | 核心约束 |
|--------|------|------|---------|
| 1 | G | `data/genres.yaml` + `data/bpm-guide.yaml` | Genre 只写1个；Tempo 用 term |
| 2 | M | `data/moods.yaml` | ≤ 2个独立情绪词 |
| 3 | I | `data/instrument-timbre.yaml` | 2-4种，每种须含 timbre 描述 |
| 4 | T | `data/production-tags.yaml` | 声场/制作质感，1-2个 |
| 5 | V | `data/vocal-tags.yaml` | **性别必填** + 音色 + 技术 + 制作，共4字段 |
| 6 | E | 手动构造 | ≤ 6项，用 `--no xxx` 格式，末尾 |

---

## 二、核心规则（v3.7更新）

```
规则1：Genre 必须放第一位，只写1个
规则2：Tempo 用 term（slow andante / upbeat allegro 等），禁止写精确 BPM 数字
规则3：Mood ≤ 2 个，选自不同类别，genre 自带的不重复计入
规则4：Instrument 每种须含音色描述（sparse/warm/bright 等），不只写乐器名
规则5：Vocal 性别必填（male/female/mixed）
规则6：Exclude 用 --no 格式，≤ 6项，末尾
规则7：禁止艺术家/歌手名称，用音色参数替代
规则8：描述词总量 4-7 个为最优
```

---

## 三、Tempo-Term 融合写法

> Suno 官方："Combine tempo terms with genres"

```
✅ 正确：
  slow andante ballad
  upbeat allegro pop
  mid-tempo andante
  slow andante cantonese classic
  half-time

❌ 错误：
  ballad, 72 BPM
  pop, 65 BPM
  ballad, slow, emotional
```

---

## 四、I 槽位写法

```
来源：data/instrument-timbre.yaml，每行 prompt 字段直接用

❌ 只写名称：
  piano
  electric guitar

✅ 须含音色描述：
  warm piano(intimate)
  clean electric guitar(bright)
  orchestral strings(soaring)
  punchy drums(epic)
```

---

## 五、V 槽位写法（v3.7更新）

```
来源：data/vocal-tags.yaml，4个字段全部给出

格式：male/female/mixed, 音色, 技术, 制作

❌ 缺失性别：
  breathy, emotional, close-miked

✅ 完整格式：
  male, rough, belted, hall reverb
  female, breathy, belted, close-miked
  male, warm, emotional, dynamic
```

---

## 六、Exclude 写法（v3.7更新）

```
格式：--no xxx（不是 —no）
数量：≤ 6 项
位置：Prompt 最末尾

✅ 正确：
  --no auto-tune --no synth pop --no minor key --no ballad --no acoustic only --no hip-hop rhythm

❌ 错误：
  —no auto-tune（用了 — 而不是 --）
```

---

## 七、三件套格式（输出模板）

```
Style Prompt（纯提示词，无标签前缀）：
  mandarin pop rock, slow andante,
  warm, nostalgic mood,
  warm piano(intimate), orchestral strings(soaring), punchy drums(epic),
  hall reverb, dynamic
  male vocal, rough, belted, hall reverb
  --no auto-tune --no synth pop --no minor key

Lyrics（含 Meta Tags）：
  [Intro]（intimate, piano alone）
  ...

Generation Settings：
  Style Influence: 80
  Weirdness: 24
```

---

## 八、合规自检（出门前必过）

```
□ Genre 在 Prompt 第一位，只写1个
□ Tempo 用 term 而非 BPM 数字
□ Mood ≤ 2 个（选自不同类别）
□ Instrument 每种含音色描述（非仅名称）
□ Sound Signature 有声场/制作词
□ Vocal 含性别（male/female/mixed）+ 音色 + 技术 + 制作
□ Exclude 用 --no 格式，≤ 6项
□ 总描述词 4-7 个
□ 没有人名/艺术家名
□ SI × W 滑杆值已给出
□ Style 和 Lyrics 基于同一 NA 五元组
□ 中文歌词经 chinese-singability.md 可唱性检查
□ 同段落相邻行音节差 ≤ 2
```

---

*suno-music-creator v3.7 | 2026-04-18*
