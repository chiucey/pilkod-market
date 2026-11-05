# Style Prompt 参数组合指南：按流派分类

> ⚠️ **防污染声明**：本文件只含参数槽位组合，**无任何可直接复制的 Style Prompt 正文**
> 生成时：从 data/genres.yaml 取 genre，从 data/moods.yaml 选 mood，从 data/instrument-timbre.yaml 选乐器
> 按 GMIVE+T 公式自主组合，不复制本文件的任何字符串

---

## 使用方法

```
1. 找到目标流派对应的参数槽位
2. genre → data/genres.yaml 确认
3. mood → data/moods.yaml 选 1-2 个
4. instruments → data/instrument-timbre.yaml 选 2-4 种（须含音色描述）
5. production → data/production-tags.yaml 选 1-2 个
6. vocal → data/vocal-tags.yaml 选完整4字段
7. 按公式组合，写入 Style Prompt
8. 对照 format-specs/style-prompt-spec.md 做合规检查
```

---

## 华语

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| 普通话抒情 | mandarin pop / mandarin ballad | melancholic / bittersweet / romantic | slow andante | warm piano(intimate) |
| 古风/中国风 | chinese-traditional | melancholic / ethereal | slow adagio | guzheng + erhu + bamboo-flute |
| C-pop 现代 | mandarin pop | upbeat / romantic / energetic | andante | synth + electric-guitar |
| 复古港风 | cantonese pop / retro-cantonese | nostalgic / romantic | andante | synth + bass + saxophone |
| 粤语抒情 | cantonese ballad | nostalgic / bittersweet | slow andante | warm piano(intimate) + strings |

---

## 主流流行

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| 情感 ballad | ballad | emotional / melancholic / romantic | slow andante | warm piano(intimate) + orchestral strings(soaring) |
| 舞曲流行 | dance-pop | energetic / euphoric | upbeat allegro | synth-pad + electronic drums |
| Electropop | synth-pop | modern / dreamy | moderate | synth-lead + electronic drums |
| K-pop 风格 | kpop | energetic / glossy | upbeat allegro | synth + 808 + vocal-harmonies |
| 成人抒情 | pop ballad | warm / intimate / romantic | andante | warm piano + light guitar |
| 复古 Synthwave | synthwave | retro / nostalgic | moderate | synthesizer + electronic drums |

---

## 摇滚

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| 经典摇滚 | classic-rock | anthemic / driving | upbeat allegro | distorted electric guitar(powerful) + bass + drums |
| 硬摇滚 | hard-rock | aggressive / powerful | allegro | distorted guitar(powerful) + bass + punchy drums(epic) |
| 另类/独立摇滚 | indie-rock | gritty / introspective / dreamy | andante | clean electric guitar(bright) + bass + understated drums |
| 后摇（纯器乐）| cinematic / post-rock | cinematic / ethereal | varies | clean guitar + drums |
| 流行朋克 | pop-rock | energetic / rebellious | allegro | electric guitar + bass + drums |
| 盯鞋梦幻 | dream-pop | dreamy / hazy | andante | clean guitar + reverb + strings |

---

## 电子

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| Progressive House | edm | euphoric / building | upbeat allegro | synth-pad + four-on-floor kick |
| Techno | techno | industrial / tense | upbeat allegro | synth bass + electronic drums |
| Ambient | ambient | ethereal / calm | slow adagio | synth-pads（+1件）|
| Lo-fi Hip Hop | lofi | nostalgic / chill | andante | rhodes + vinyl-crackle + lazy drums |
| Synthwave | synthwave | retro / nostalgic | moderate | synthesizer + electronic drums |
| Drum & Bass | edm | energetic / uplifting | presto | synth-pad + drums |

---

## 嘻哈

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| Boom Bap | boom-bap | nostalgic / gritty | andante | dusty samples + tight kick + vinyl-crackle |
| Trap | trap | dark / aggressive | allegro | 808 + rapid hihats |
| 陷阱情歌 | trap-ballad | melancholic / emotional | andante | warm piano(intimate) + 808 |
| Lo-fi Hip Hop | lofi | nostalgic / mellow | andante | rhodes + vinyl-crackle + drums |

---

## 爵士与蓝调

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| Smooth Jazz | smooth-jazz | late-night / sophisticated | andante | saxophone + rhodes + brushed drums |
| Bossa Nova | bossa-nova | smooth / romantic | andante | nylon guitar + soft percussion |
| 标准蓝调 | blues | soulful / gritty | andante | electric guitar + harmonica + drums |
| Jazz Lo-Fi | lofi | nostalgic / chill | andante | saxophone + rhodes + brushed drums |

---

## 民谣与乡村

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| 原声民谣 | acoustic-folk | intimate / storytelling | andante | fingerpicked acoustic guitar(soft) |
| 凯尔特民谣 | celtic-folk | mystical / adventurous | andante | tin-whistle + harp + fiddle |
| 独立民谣 | indie-folk | introspective / delicate | andante | fingerpicked guitar + cello |
| Country | country | heartfelt / warm | andante | acoustic guitar + telecaster |

---

## 影视配乐

| 流派 | genre 参数 | mood 选项 | tempo term | instrument 示例 |
|------|-----------|---------|-----------|---------------|
| 史诗电影配乐 | epic-cinematic | triumphant / epic | andante | orchestral strings(soaring) + epic drums + choir |
| 悬疑配乐 | tension-underscore | tense / dark | andante | low strings + warm piano(intimate) + sub-bass |
| 暗黑管弦 | cinematic | dark / epic | andante | orchestral strings + taiko + distorted brass |
| 喜剧配乐 | cinematic | playful / whimsical | upbeat allegro | strings + glockenspiel |

---

## 融合风格

```
融合规则：主流派放前面，副流派加 influence

示例：
  rock + electronic → genre=rock, instruments 从两边各取
  jazz + hiphop     → genre=boom-bap, mood/instruments 从两边各取
  chinese-traditional + electronic → genre=chinese-traditional, production=[electronic, ethereal]
```

---

*参数组合指南 | 防污染版 | suno-music-creator v3.7 | 2026-04-19*
