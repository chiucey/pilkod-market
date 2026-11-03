# Suno AI V5.5 提示词优化指南 v1.0

> 来源：Reddit SunoAI 社区验证 + medici.work + soundverse.ai + jackrighteous
> 版本：v1.0 | 更新：2026-04-19
> 用途：优化 GMIVE+T 参数，提升 Suno V5.5 复刻精度

---

## 一、V5.5 新特性与变化

### 1.1 V5.5 对提示词更敏感

> "v5 的超现实主义（Hyper-Realism）让人声、混音与结构都大幅提升，但要发挥它的极致潜力，提示工程（Prompt Engineering）变得更关键。v5 对提示更敏感、更精确。"

**核心变化：**
- 描述词冲突会被放大 → 更需要精确
- 模块化结构比"大段文字"效果好
- Genre 必须放第一位（注意力权重最高）

---

## 二、V5.5 推荐 Prompt 结构

### 2.1 最佳结构顺序

```
Genre + Tempo（第一位）
→ Mood + Energy（情绪）
→ Instruments + Timbre（乐器音色）
→ Vocal Chain（人声链）
→ Production Signature（声场）
→ Exclude（排除）
```

### 2.2 模块化写法规则

```
❌ V5.5 淘汰写法：
"a beautiful mandarin pop ballad song with piano and guitar,
sad emotional mood, female vocal, romantic feelings..."

✅ V5.5 正确写法（模块化）：
mandarin pop ballad, slow andante
nostalgic, bittersweet mood
warm piano(intimate), fingerpicked acoustic guitar(soft)
orchestral strings(soaring)
female vocal, breathy, emotional, close-miked
hall reverb, intimate, warm production
Exclude these styles:
--no auto-tune --no synth pop --no heavy drums
```

**关键区别：**
- 每行一个模块，不是混合长句
- 乐器音色单独成行
- Exclude 加引导语（"Exclude these styles:"）

---

## 三、V5.5 核心参数优化

### 3.1 Genre 优化

```
✅ 正确：
  mandarin pop rock
  cantonese ballad
  mandarin ballad

❌ 错误：
  Chinese pop ballad rock folk（太多genre混在一起）
  普通话流行歌曲（太模糊）
```

**中文歌曲 Genre 最佳写法：**
```
普通话歌曲：mandarin [sub-genre]
粤语歌曲：  cantonese [sub-genre]（必须标注 Cantonese，Suno 才能正确识别粤语发音）
台语歌曲：  taiwanese pop
```

### 3.2 描述词数量：4-7 个

> "4-7 descriptors is the sweet spot — too few gives generic output, too many creates conflicts."

| 数量 | 效果 |
|------|------|
| 1-3个 | 太泛，输出随机 |
| **4-7个** | **最优区间 ✅** |
| 8-10个 | 开始冲突，质量下降 |
| 11+个 | 严重冲突，可能崩溃 |

### 3.3 Mood 优化

```
❌ 错误：mood: happy, sad, romantic, melancholic（4个太多，且矛盾）
✅ 正确：nosta lgic, bittersweet（2个，选自不同象限）

❌ 错误：mood: sad, depressive（同一象限重叠）
✅ 正确：melancholic, wistful（Q3+Q4组合）
```

### 3.4 Vocal Chain 完整格式（V5.5）

```
格式：性别 + 音色 + 技术 + 制作效果

示例组合：
  male, rough, belted, hall reverb          # 摇滚呐喊
  female, breathy, emotional, close-miked    # 抒情亲密
  male, warm, spoken, intimate                # 叙述感
  female, ethereal, whispered, hall reverb     # 空灵飘渺
```

**Vocal Chain 各字段详解：**

| 字段 | 选项 | 说明 |
|------|------|------|
| 性别 | male / female / mixed | V5.5 必填 |
| 音色 | warm / rough / breathy / smooth / raspy | 声线质感 |
| 技术 | belted / whispered / spoken / falsetto | 唱法 |
| 制作 | close-miked / hall reverb / intimate / dynamic | 录音效果 |

---

## 四、中文歌曲专项优化

### 4.1 中文歌词与 Suno 的配合

```
中文歌曲提示词结构：
  mandarin [sub-genre], tempo
  [mood1], [mood2]
  [instruments]
  [vocal chain]
  Chinese lyrics  ← 明确标注语言

示例：
  mandarin pop ballad, slow andante
  nostalgic, bittersweet mood
  warm piano(intimate), orchestral strings(soaring)
  female vocal, breathy, emotional, close-miked
  Chinese lyrics
```

### 4.2 粤语歌曲提示词

```
cantonese pop ballad, slow andante
nostalgic, romantic mood
warm piano, orchestral strings
female vocal, warm, emotional, hall reverb
Cantonese lyrics  ← 必须标注 Cantonese
```

---

## 五、网易云热评提取方法论

### 5.1 提取层级

```
层级1：行为模式（做什么）
层级2：情感逻辑（为什么）
层级3：时间/空间代价（等待多久/在哪里等）
层级4：具体意象（物品/场景）
```

### 5.2 丢弃规则

```
❌ 丢弃：
  具体数字（3年/100次）
  具体地名（武汉/广州）
  具体人名
  热评完整句子

✅ 保留：
  行为模式（等待/思念/放弃）
  情感逻辑（明知不可为而为之）
  时间代价（等了多久不重要，重要的是"在等"这个状态）
  空间意象（用新的物品承载同一种等待）
```

### 5.3 从热评到 NA 五元组的转换示例

```
热评原文：
"听了这首歌，想起那年夏天的她，她说等我回来，可是等了三年她嫁给了别人，
我再也不相信承诺了，这首歌陪我度过最孤独的那段日子"

提取（丢弃数字/地名/原文）：
  agent:     等待归来的人
  action:    相信了承诺，选择了等待
  obstacle:  等到的不是归来，而是背叛
  attempt:   用这首歌陪伴孤独
  outcome:   学会了不相信，但也因此放下了
```

---

## 六、林夕歌词手法精解（粤韵研究）

> 来源：香港教育研究 + 学术论文

### 6.1 音韵特征

| 特征 | 具体表现 |
|------|---------|
| 头韵 | 偏好 [tʃ]/[ʃ]/[j] 声母（舌头音/半元音）|
| 押韵位置 | 句末押韵为主，偶尔句中韵 |
| 韵辙偏好 | eng韵/ang韵 为主 |

### 6.2 修辞手法

| 手法 | 说明 | 示例 |
|------|------|------|
| 排比 | 增强气势，制造节奏感 | 心跳/呼吸/眼泪 |
| 留白 | 用意象说情绪，不直说 | 用雨说眼泪 |
| 对比 | 落差制造张力 | 昨日vs今日 |
| 叠字 | 增强音韵美 | 渐渐/缓缓 |

### 6.3 防污染的林夕手法

```
❌ 错误：复制"林夕风"的意象组合
✅ 正确：用林夕的"留白+意象承载情绪"手法，写全新的意象
```

---

## 七、V5.5 失败模式与修复

### 7.1 常见失败模式

| 失败模式 | 原因 | 修复 |
|---------|------|------|
| 输出太泛 | Genre 不够具体 | 写 1 个具体 sub-genre |
| 情绪打架 | Mood 矛盾 | ≤2个，选自不同象限 |
| 人声不对 | Vocal 缺字段 | 必须含 4 个字段 |
| 乐器不对 | 只有乐器名，没有音色描述 | 加音色描述 |
| 描述冲突 | 8+ 个描述词 | 精简到 4-7 个 |
| 中文不地道 | 没有标注语言 | 加 Chinese / Cantonese |

### 7.2 V5.5 Character Limits

| 框 | 限制 | 建议 |
|---|------|------|
| Style Prompt | 200 字符（V4.5）→ 更宽松（V5.5）| 保留在 150 字符以内 |
| Lyrics | 3,000 字符 | 结构清晰即可 |

---

*suno-music-creator v3.7 | Suno V5.5 Prompt Optimization Guide v1.0*
