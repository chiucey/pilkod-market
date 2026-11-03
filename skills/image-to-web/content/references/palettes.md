# 配色参考表（palettes.md）

> 用途：第 2 步用。拿 style-dna 的 `mood` / `theme` / `saturation` 找到最贴的一档，
> 再把里面的 hex **微调**到图片实际取色上。这张表是"避免 AI 均值坑 + 提供成熟起点"，
> 不覆盖图片 DNA——图片取的 hex 优先。
>
> 通用禁忌（所有档位都守）：不用纯黑 #000000 当大面积背景（用 #0A0A0B / #18181B）；
> 强调色饱和度别拉满到刺眼；一套页面只用一套中性灰，不混暖灰冷灰。

## 1. 极简克制（minimal / calm / editorial / Linear 风）
- bg `#FFFFFF` / surface `#FAFAFA` / ink `#18181B` / muted `#71717A` / border `#E4E4E7`
- accent 二选一：靛蓝 `#4F46E5` 或 墨绿 `#047857`（只用一个）
- 适配 mood：干净 / 高级 / 冷静 / 专业

## 2. 深色科技（dark tech / SaaS / 未来感）
- bg `#0A0A0B` / surface `#161618` / ink `#FAFAFA` / muted `#A1A1AA` / border `#27272A`
- accent：青 `#22D3EE` 或 电蓝 `#3B82F6`（点缀，别铺）
- 适配 mood：冷峻 / 未来感 / 极客 / 高级暗色

## 3. 暖调高级（premium / luxury / Apple-y / 温暖）
- bg `#FBF9F6`(米白) / surface `#FFFFFF` / ink `#1C1917` / muted `#78716C` / border `#E7E2DA`
- accent：赤陶 `#C2410C` 或 深金 `#B45309`
- 适配 mood：温暖 / 精致 / 品牌感 / 编辑部

## 4. 活泼高饱和（playful / vibrant / 消费级 / 儿童）
- bg `#FFFDF7` / surface `#FFFFFF` / ink `#1A1A1A` / muted `#6B7280` / border `#1A1A1A`
- accent 轮换：橙 `#FF6B35` / 黄 `#FFD84D` / 薄荷 `#3DD6A0` / 粉 `#FF6FA5`
- 适配 mood：活泼 / 大胆 / 年轻 / 趣味

## 5. 新孟菲斯 / 硬阴影野兽派（Memphis / neo-brutalist）
- bg `#F8F6F6` / surface `#FFFFFF` / ink `#1A1A1A` / **border 一律 `#000000`（粗描边）**
- accent 马卡龙轮换：橙 `#FF6B35` / 黄 `#FFD84D` / 薄荷 `#B8E4D0` / 粉 `#FFB4C6` / 蓝 `#A5C9FF`
- 招牌：3px 黑描边 + 硬阴影 `4px 4px 0 #000` + 16px 圆角
- 适配 mood：Memphis / 复古大胆 / 高辨识 / 潮玩

## 6. 自然有机（organic / wellness / 环保 / 温和）
- bg `#F7F5F0` / surface `#FFFFFF` / ink `#2D2A26` / muted `#8A857C` / border `#E5E0D6`
- accent：橄榄绿 `#6B8E4E` 或 陶土 `#B5734F`
- 适配 mood：自然 / 平静 / 治愈 / 手作感

## 7. 编辑部 / 杂志（editorial / magazine / 时尚）
- bg `#FBFBF9` / surface `#FFFFFF` / ink `#111111` / muted `#666666` / border `#111111`
- accent：正红 `#E4002B`（少量、克制、当强调）
- 适配 mood：编辑部 / 时尚 / 强排版 / 黑白 + 一点红

## 8. 玻璃拟态（glassmorphism，配深色/渐变背景用）
- 背景：深色或彩色渐变打底；面板：`rgba(255,255,255,0.08)` + `backdrop-filter: blur(16px)`
  + `1px solid rgba(255,255,255,0.18)`
- ink `#FFFFFF` / muted `rgba(255,255,255,0.7)`
- 必给 `prefers-reduced-transparency` 的实色回退
- 适配 mood：轻盈 / 通透 / 高级科技
