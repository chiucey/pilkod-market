# 字体对参考表（font-pairs.md）

> 用途：第 2 步用。按 style-dna 的 `type_feel` 找到匹配的一档，作为标题 + 正文的字体对。
> 全部走 Google Fonts（免费、可 CDN 引），无需本地安装。
>
> 硬禁忌：不用 Inter / Roboto / Arial / 系统默认当**主**字体（AI 均值脸）。
> 需要衬线时，不用 Times New Roman / Georgia / Garamond，用下面的现代衬线。
> 中文标题若需要，用 `Noto Sans SC` / `Noto Serif SC` 兜底。

## 按 type_feel 选

### 几何无衬线（geometric sans）— 现代、干净、科技
- 标题 **Space Grotesk** / 正文 **Inter Tight** 或 **IBM Plex Sans**
- 或 标题 **Sora** / 正文 **Manrope**
- 适配：SaaS、科技、产品站

### 人文无衬线（humanist sans）— 温和、易读、亲和
- 标题 **Bricolage Grotesque** / 正文 **Figtree**
- 或 标题 **Outfit** / 正文 **Public Sans**
- 适配：消费级、健康、教育、品牌

### 超粗展示 + 无衬线（bold display）— 大胆、活泼、高辨识
- 标题 **Clash Display**（若不可得用 **Archivo Black** / **Anton**）/ 正文 **Space Grotesk**
- 适配：孟菲斯、潮玩、活动、创意机构

### 现代衬线（modern serif）— 编辑部、高级、时尚
- 标题 **Fraunces**（可调光学尺寸）/ 正文 **Inter Tight** 或 **Source Serif 4**
- 或 标题 **Instrument Serif** / 正文 **Geist**
- 适配：杂志、时尚、奢侈品、作品集

### 复古 / 优雅衬线（elegant serif）— 温暖、经典、品牌
- 标题 **Playfair Display** / 正文 **Nunito Sans**
- 或 标题 **DM Serif Display** / 正文 **DM Sans**
- 适配：餐饮、婚礼、生活方式、精品

### 圆体（rounded）— 友好、软萌、儿童/消费
- 标题 **Baloo 2** 或 **Quicksand（粗）** / 正文 **Nunito**
- 适配：儿童、社交、轻应用

### 等宽 / 科技感（mono）— 极客、终端、数据
- 标题 **Space Mono** 或 **JetBrains Mono** / 正文 **IBM Plex Sans**
- 高密度数据表：数字统一用 **JetBrains Mono** 的等宽数字
- 适配：开发者工具、暗色科技、数据看板

### 编辑部黑白强排版（swiss / editorial）
- 标题 **Archivo（Expanded 粗）** / 正文 **Archivo**
- 或 标题 **Syne** / 正文 **Inter Tight**
- 适配：Swiss、杂志、作品集、强排版

## 通用规则
- 一个页面**最多两套字体家族**（标题 + 正文），多了显乱。
- 标题字重拉开与正文的反差（如标题 700+，正文 400）。
- 正文行高 1.5–1.7，正文每行 60–75 字符（中文更短）。
- 标题用 `clamp()` 做响应式缩放，正文移动端不小于 16px。
