# Suno 快速参考卡 v3.7

> 出门前背一句，回来核对合规。完整流程：SKILL.md

---

## 7步工作流

```
Step 1  音频分析  → 音频文件 → 精准BPM/音色/节奏/混音/人声
Step 1b 网上搜索  → 歌曲+热评 → 歌词/情感逻辑/创作背景
Step 2  判断     → 逐项判断每项参数能否复刻
Step 3  提取     → 能复刻的参数写入GMIVE+T
Step 4  NA五元组 → 热评情感逻辑（丢弃原文，保留行为模式）
Step 5  同步创作 → Style（音频参数）+ Lyrics（热评情感）
Step 6  自检     → 防污染6条 + 可唱性5条
Step 7  三件套   → Style + Lyrics + SI×W 输出
```

---

## 合规检查清单（出门前必过）

```
□ Genre 在 Prompt 第一位，只写1个
□ Tempo 用 term（slow andante / upbeat allegro），不用 BPM 数字
□ Mood ≤ 2 个（选自 moods.yaml Russell 象限）
□ Instrument 每种含音色描述（非仅名称，选自 instrument-timbre.yaml）
□ Vocal 含性别（male/female/mixed）+ 音色 + 技术 + 制作
□ Exclude 用 --no 格式，≤ 6 项
□ Style 和 Lyrics 基于同一 NA 五元组
□ 中文歌词经 chinese-singability.md 可唱性检查
□ 同段落相邻行音节差 ≤ 2
□ 歌词正文是原创，不复制任何 .md 示例
□ SI × W 滑杆值已给出
```

---

## GMIVE+T 公式（V5.5模块化格式）

```
Genre, tempo term
mood1, mood2
instrument1(timbre), instrument2(timbre)...
sound-signature
vocal: gender, timbre, technique, production
Exclude these styles:
--no xxx --no xxx
```

> V5.5：每行一个模块，4-7个描述词，禁止混合长句

---

## 多音字强制替换

| 原字 | 替换 | 场景 |
|------|------|------|
| 还(hái/huán) | 仍 | 还在/还有 |
| 了(le/liǎo) | 啦/过 | 句末 |
| 着(zhe/zhao) | 在 | 看着/等着 |
| 地(de/dì) | 得 | 修饰副词 |
| 得(dé/děi) | 到 | 得到 |
| 长(cháng/zhǎng) | 成长 | 长大 |
| 行(xíng/háng) | 走/路 | 行走 |

---

## Chorus 开口音规则

```
优先韵母（eng/ang/ou/ai/ao）→ 可唱性最高
闭口音（i/u/ü）→ 单行 ≤ 3次
三声字 → Chorus 行 ≤ 2个/行
```

---

## BPM 速查

| 情绪 | BPM | Tempo词 |
|------|-----|---------|
| 非常慢 | 40-60 | slow adagio |
| 慢 ballad | 55-80 | slow |
| 华语抒情 | 70-85 | slow andante |
| 叙事抒情 | 80-100 | andante |
| 流行 | 100-120 | moderate |
| 快流行 | 120-140 | upbeat allegro |
| 摇滚 | 120-160 | allegro |
| 嘻哈 Trap | 130-170 | allegro |
| 金属/硬核 | 155+ | presto |

---

## Instrument Timbre 选取

```
来源：data/instrument-timbre.yaml（prompt字段直接用）

❌ 只写名称：piano / electric guitar / drums
✅ 须含描述：warm piano(intimate) / clean electric guitar(bright)
✅ 数量：2-4种，不要超过4种
```

---

## Vocal 参数选取

```
来源：data/vocal-tags.yaml

格式：male/female/mixed, 音色, 技术, 制作

❌ 缺性别：breathy, emotional, close-miked
✅ 有性别：male, rough, belted, hall reverb
```

---

## SI×W 滑杆值

| 任务类型 | SI | W |
|---------|-----|-----|
| 风格复刻（参考原歌曲）| 78–84 | 22–28 |
| 商业保守（安全生成）| 70–80 | 15–22 |
| 创意探索（全新方向）| 60–75 | 28–35 |

---

## Exclude 格式

```
❌ 错误：—no auto-tune
✅ 正确：--no auto-tune
数量：≤ 6 项，末尾
```

---

## 复刻判断矩阵

| 参数 | 能/不能 |
|------|---------|
| Genre + Tempo Feel | ✅ 能 |
| 精确 BPM 数字 | ❌ 不能 |
| Mood（Russell词）| ✅ 能 |
| Instrument + Timbre | ✅ 能 |
| Vocal（性别+音色）| ✅ 能 |
| 和弦进行 | ❌ 不能 |
| 调性/转调 | ❌ 不能 |
| 混音参数 | ❌ 不能 |

---

## 粤语歌曲快速指南

```
问题：Suno 唱普通话不唱粤语
解决：歌词末尾加粤拼标注 + style 加 cantonese song

格式：
歌词正文[粤拼拼音]

示例：
带我走 带到最高的地方[dai6 ngo5 zau2 dai6 dou3 zeoi3 gou1]

Style 加：
cantonese song, cantonese vocal articulation

Exclude 加：
--no mandarin pronunciation

详见：Cantonese_Song_Guide.md
```

---

*v3.7 | 2026-04-20*
