## 格式规范（format-specs/）

| 文件 | 版本 | 内容 |
|------|------|------|
| `style-prompt-spec.md` | v3.7 | GMIVE+T 公式 + V5.5模块化格式 + 合规自检 |
| `lyrics-meta-spec.md` | v3.5 | 两层Meta Tags + 行内标签 + 合规自检 |
| **`Cantonese_Song_Guide.md`** | **v1.0** | **粤语歌曲生成专项：粤拼标注 + Style增强 + 避坑指南** |

## 数据文件（data/）

| 文件 | 版本 | 内容 |
|------|------|------|
| `genres.yaml` | — | 10大类 × 120+子流派 |
| `bpm-guide.yaml` | — | Tempo-Term融合 + BPM×字数对照 |
| `moods.yaml` | — | Russell 16情绪坐标 + BPM匹配 |
| `instrument-timbre.yaml` | — | 8乐器家族 × 48音色变体 |
| `production-tags.yaml` | — | 6维度 × 45质感标签 |
| `vocal-tags.yaml` | — | 21音色 + 9技术 + 7能量 |

## 核心参考文档

| 文件 | 版本 | 内容 | 污染状态 |
|------|------|------|---------|
| `author-dna.md` | v3.7 | DNA六维 + 四步复刻 + 防污染规则 | ✅ 干净 |
| `lyrics-parametric.md` | v3.7 | 热评→NA→新意象工作流 | ✅ 干净 |
| `Suno_V55_Prompt_Guide.md` | v1.0 | V5.5专项 + 中文处理 + 林夕粤韵 | ✅ 干净 |
| `quick-ref.md` | v3.7 | 7步+GMIVE+T V5.5格式 | ✅ 干净 |
| `technical-params.md` | v3.7 | GMIVE+T规则+判断矩阵 | ✅ 干净 |

## 风格参数库

| 文件 | 版本 | 内容 | 污染状态 |
|------|------|------|---------|
| `style-by-genre.md` | **v3.7** | **genre×mood×tempo×instrument 参数组合**（无正文）| ✅ 已净化 |
| `style-by-scene.md` | **v3.7** | **场景×情绪 参数库**（无正文）| ✅ 已净化 |
| `lyrics-chinese.md` | — | 十三辙押韵 + 作词人手法 | ✅ 干净 |
| `lyrics-structure.md` | — | 段落结构 + Meta Tags | ✅ 干净 |
| `chinese-singability.md` | — | 多音字 + 开口音规则 | ✅ 干净 |
| `syllable-guide.md` | — | ±2音节规则 + 密度曲线 | ✅ 干净 |

## 风格档案

| 文件 | 内容 |
|------|------|
| `Beyond_海阔天空_风格档案.md` | DNA六维 + GMIVE+T参数 + NA五元组 + 能量曲线 |

---

## v3.7 核心更新

### 信息双轨制（音频 + 搜索）

```
音频分析（MCP audios_understand）
  → 精准BPM/乐器音色/节奏感/演奏方式/混音/人声技术

网上搜索（batch_web_search）
  → 歌词内容/网易云热评/创作背景/情感逻辑

两者叠加 = 最完整复刻
```

### 防污染三原则

```
原则1：热评情感 → NA五元组 → 新意象（不是原曲意象）
原则2：作词人手法 → 用于润色（不是复制原文）
原则3：污染排查 → 逐行对比，超过5字相同 → 重写
```

### 7步工作流

```
Step 1  搜索     → 歌曲分析 + 网易云热评
Step 2  判断     → 逐项判断能否复刻
Step 3  提取     → 能复刻的参数写入GMIVE+T
Step 4  NA五元组 → 热评情感逻辑（不是热评原文）
Step 5  同步创作 → Style + Lyrics（新意象，非原曲意象）
Step 6  自检     → 防污染6条 + 可唱性5条
Step 7  三件套   → 输出交付
```

---

## 核心规则速记

| 规则 | 内容 |
|------|------|
| Genre | 只写1个，放第一位 |
| Tempo | 用 term（slow andante 等），禁止 BPM 数字 |
| Mood | ≤ 2个，选自不同类别 |
| Instrument | 2-4种，每种含 timbre 描述 |
| Vocal | **性别必填** + 音色 + 技术 + 制作 |
| Exclude | 用 `--no` 格式，≤ 6项 |
| 防污染 | 热评情感→NA→新意象，不用原曲意象 |
| 作词手法 | 用于润色生成，不用于复制原文 |

