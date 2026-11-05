# Suno 技术参数速查 v3.7

> ⚠️ 防污染声明：本文档为参数数据，无可复制正文。

---

## 一、GMIVE+T 公式（v3.7确立）

```
G(Genre+Tempo) → M(Mood) → I(Instrument+Timbre) → T(Sound Signature) → V(Vocal) → E(Exclude)
```

| 槽位 | 来源 | 约束 |
|------|------|------|
| G | `data/genres.yaml` + `data/bpm-guide.yaml` | 只写1个， Tempo 用 term |
| M | `data/moods.yaml` | ≤ 2个，选自不同类别 |
| I | `data/instrument-timbre.yaml` | 2-4种，每种含 timbre 描述 |
| T | `data/production-tags.yaml` | 1-2个声场/制作词 |
| V | `data/vocal-tags.yaml` | **性别必填** + 音色 + 技术 + 制作 |
| E | 手动构造 | ≤ 6项，用 `--no xxx` 格式 |

---

## 二、BPM 规则

```
❌ 禁止：精确 BPM 数字（Suno 近似浮动±5，会误导）
✅ 正确：用 Tempo-Term 融合词

  slow andante（≈70-90 BPM）
  upbeat allegro（≈125-145 BPM）
  half-time（≈65-75 BPM）
```

---

## 三、Genre 规则

```
❌ 禁止：多个 genre 混写
✅ 正确：只写1个

  ❌ mandarin pop rock ballad
  ✅ mandarin pop rock
```

---

## 四、Mood 规则

```
❌ 禁止：超过2个情绪词
✅ 正确：≤ 2个独立情绪词

  ❌ melancholic, sad, nostalgic（3个）
  ✅ nostalgic, triumphant（2个）
```

---

## 五、Instrument Timbre 规则

```
❌ 禁止：只写乐器名称
✅ 正确：乐器名 + 音色描述

  ❌ piano, guitar, drums
  ✅ warm piano(intimate), clean electric guitar(bright), orchestral strings(soaring)
```

---

## 六、Vocal 规则（v3.7更新）

```
❌ 禁止：缺失性别字段
✅ 正确：4个字段全部给出

  ❌ rough, belted, hall reverb（缺性别）
  ✅ male, rough, belted, hall reverb
```

---

## 七、Exclude 规则（v3.7更新）

```
❌ 禁止：—no xxx（用了短横线）
✅ 正确：--no xxx（两个短横线）

  ❌ —no auto-tune —no synth pop
  ✅ --no auto-tune --no synth pop
```

---

## 八、SI×W 滑杆值（v3.7更新）

| 任务类型 | Style Influence | Weirdness |
|---------|---------------|-----------|
| 风格复刻（参考原歌曲）| 78–84 | 22–28 |
| 商业保守（安全生成）| 70–80 | 15–22 |
| 创意探索（全新方向）| 60–75 | 28–35 |

---

## 九、Style-Lyrics 协同规则

```
Style 设定音色基底
    ↓ 继承
Lyrics Meta Tags 在此底色上做段落级动态变化

❌ 矛盾：
  Style: warm, intimate
  Lyrics: male, rough, belted  ← 音色打架

✅ 协同：
  Style: warm, nostalgic
  Lyrics: male, warm, emotional, close-miked
  Lyrics: [Bridge]（sparse, whispered）← 同底色递进
```

---

## 十、描述词数量

```
4-7 个为最优
  太少 → 太泛，输出随机
  太多 → 互相冲突，质量下降
  11+  → 严重冲突
```

---

## 十一、复刻判断速查

| 参数 | 能否复刻 | 说明 |
|------|---------|------|
| Genre / Tempo Feel | ✅ | 用词描述 |
| Mood（Russell）| ✅ | 情绪词 |
| Instrument + Timbre | ✅ | 音色描述 |
| Vocal（含性别）| ✅ | 音色参数 |
| Sound Signature | ✅ | 声场/质感词 |
| 精确 BPM | ❌ | Suno 近似浮动 |
| 和弦进行 | ❌ | 无法精确控制 |
| 调性/转调 | ❌ | 无法精确控制 |
| 混音参数 | ❌ | 无法精确控制 |

---

*suno-music-creator v3.7 | 2026-04-18*
