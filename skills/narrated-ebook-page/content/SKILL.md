---
name: narrated-ebook-page
description: |
  生成单文件 HTML 电子版阅读页：白底、正文近黑、大标题橙黄、小标题深色，
  自带章节目录、逐段朗读（跟随滚动 + 段落高亮）、内联 SVG 图表、宽表卡片化、
  响应式与打印导出 PDF。
  Load this skill whenever the user says 「做成电子版」「转成网页版」「做成能听的页面」
  「加朗读」「白底黑字橙黄标题」「把这份文档做成可读网页」"make an ebook page"
  "turn this document into a web page" "add read-aloud"，或要在已有电子版页面上
  加章节、换内容、沿用同一套版式。
  不要用于：扫描件书稿转静态阅读页（用 ebook-visual-html）、单页说明型或仪表盘页面
  （用 visual-page）、导出 PDF 文件本身（用 pdf）、给现有网站改配色（直接改 CSS）。
descriptions:
  zh-Hans: "生成电子版 HTML 阅读页：白底黑字正文、橙黄大标题、深色小标题，自带目录、逐段朗读、内联图表、响应式与打印导出。"
displayNames:
  zh-Hans: "电子版可视化"
---

# 电子版可视化页面

把一份内容做成能读、能听、能打印的单文件 HTML。版式是这个 skill 的固定资产：
**白底、黑字正文、橙黄大标题、深色小标题**。用户没提出配色要求前不要改 `:root`
里的 token；多份文档之间视觉必须一致，这是本 skill 存在的理由。

## Inputs to collect

先确认这四项，缺哪项就用中性占位继续推进，不要为一篇文档反问一串问题：

- 文档标题、作者（用于封面卡与版权页；没有就写「待定」并在交付时说明）
- 正文来源：纯文字 / Markdown / 结构化数据 / 已有 HTML
- 是否需要朗读（默认要，默认音色「电台男主播」；除非有「不下载外部文件」这类约束，
  或者用户明确说「能听就行」）
- 交付目录（默认 `<当前工作目录>/<标题简称>/`，用户指定了就用他指定的）

## Procedure

1. 先读 `references/design-system.md` 和 `references/template.html` 再动手。
   原因：类名与 token 是这个 skill 的契约；不读就手写 HTML，样式会和模板漂移，
   下一份文档就得重调一遍。

2. 把模板复制成工作文件：`references/template.html` → `<交付目录>/index.html`。
   原因：模板是已验证过的成品（配色、响应式、朗读、打印都跑通过），
   从零手写必然产生不一致。

3. 盘点素材：章节数、每章标题与导语、哪些块是正文 / 要点 / 数据 / 引文 / 插图。
   原因：结构判定错了，后面排版全跟着错；而这步的成本远低于返工。

4. 按 `references/authoring.md` 替换内容：封面卡、章节、小标题、段落、要点卡、图表、表格。
   保留模板里的外壳（进度条、左侧目录、朗读竖条、朗读面板、封面卡骨架）——
   它们是这套版式的一部分，不要重写。封面**只做文字卡片**：不引外部图片、
   不放图片占位框；需要图就用正文的 `.slot` 占位。

5. 给要朗读的段落加 `data-tts-c`（章 id）与 `data-tts-i`（章内序号，从 0 连续）。
   原因：音频与段落靠这两个属性对齐；靠 DOM 顺序猜会「念 A 段高亮 B 段」。

6. **配音频（默认要做这一步）**：
   `node scripts/make-audio.mjs <交付目录>/index.html`
   脚本会抽出所有带 `data-tts-*` 的段落、用**「电台男主播」**
   （`voice_id: Chinese (Mandarin)_Radio_Host`）合成 mp3、落到
   `assets/audio/Chinese_Mandarin__Radio_Host/`、把 `AUDIO_MANIFEST` 写回 HTML。
   先跑一次 `--dry-run` 看清楚要念的文本，确认无误再正式跑——合成要花钱也耗时间。
   上游限流时脚本会自动退避重试并缩批；中途断了就重跑同一条命令，
   已经生成好的文件不会重做。
   换音色、调整语速、手工兜底这些在 `references/reading-mode.md`。
   **只有这几种情况才跳过音频**：
   - 任务带「不引外部资源 / 不下载外部文件 / 离线自包含」这类约束
     → mp3 整条路作废，`AUDIO_MANIFEST` 留 `null` 走浏览器合成，
     并在交付说明里写明「朗读依赖读者系统的中文音色」
   - 段落多到合成耗时不可接受 → 同上
   原因：读者机器上没有中文音色时只有 mp3 一条能走通；
   浏览器合成出来的是系统彩蛋音（婷婷 / Eddy / Flo 之类），念长文非常难听。

7. 校验：`node scripts/check-page.mjs <交付目录>/index.html`，修到零错误。
   它查配色 token、朗读标记与引擎挂钩、外链、图片 alt、打印块、响应式断点、
   段落序号连续性。 原因：这几项错起来都不会报错，只会安静地坏掉。
   「待定」这类占位会报 WARN——那是提醒你交付时补上，不是错误，改文案或如实说明即可。

8. 视觉自检：起本地静态服务（`python3 -m http.server <任选空闲端口>`），
   在 390 / 834 / 1280 三档视口各看一遍首屏，外加一张含图表或宽表的页。
   原因：栏宽、行高、卡片塌陷、宽表溢出这类问题，静态检查看不出来。
   **若本机起不来任何浏览器**（沙箱拦截、缺二进制、无头浏览器装不上），
   退化做法：按 CSS 级联顺序算出各断点下的实际栏宽与字号、逐项核对内容不变量、
   仿一遍朗读引擎的队列推进逻辑，并在交付说明里**如实声明未做像素级复核**。
   不要因为看不到页面就跳过这一步，也不要假装看过。

9. 交付：给出 `index.html` 绝对路径 + `<deliver-assets>` 包裹的 `<media>`，并说明四件事：
   怎么本地打开、配色 token 在哪、怎么导出 PDF（⌘P，已分页）、想改内容改哪几处。

## Output contract

- `<交付目录>/index.html` — 单文件，CSS/JS 内联，不引 CDN、不引外链字体
- `<交付目录>/assets/audio/Chinese_Mandarin__Radio_Host/*.mp3` — 配了音频就有，
  段数与 `data-tts-*` 段落一一对应
- `check-page.mjs` 零错误
- 交付说明：路径 + 打开方式 + token 位置 + PDF 导出方式

## Failure handling

- 音频没生成或文件缺失：不要留一个点了没反应的按钮。退回浏览器合成，
  或保留缺失段并在交付说明里列出待补段落。
- 播放中按钮没有换成暂停键：引擎的 `setState` 里少了 `barToggle` 的 `is-on` 切换。
  按钮永远长一个样，不报错但读者看不出还能不能暂停。照 `references/reading-mode.md`
  第六节补回去。
- 校验报「朗读段序号不连续」：重新按章核对 `data-tts-i`——序号错位会让
  朗读跳段或重复念同一段。
- 宽表在手机档挤成一团：确认每个 `td` 都带 `data-l`（行内小标签），没有就补上。
- 插图在窄屏看不全：模板已内置横拖提示与「全屏看」按钮，不用自己加。
- 想加组件但模板没有：先查 `references/design-system.md` 有没有等价类；
  确实没有才改模板，并把新类名补进设计系统文档，让下一份文档能用上。
- 文档超过 20 章：目录、章节跳转、朗读队列都会变长。在交付说明里写清章数，
  并确认目录在手机抽屉里能滚到底。

## Examples

- Input：「把这份方案做成电子版网页，要能听」
  → 复制模板 → 替换章节与段落 → 加 `data-tts-*` → `AUDIO_MANIFEST` 留空走合成
  → 校验 → 三档视口自检 → 交付
- Input：「这个页面再补两章」
  → 只在 `main.stage` 里追加两个 `section.chapter`，左侧目录同步加两条，
  `data-tts-i` 从新章各自从 0 开始编

## Windows (win32) platform notes

- `check-page.mjs` 是 Node 脚本，跨平台一致：`node scripts\check-page.mjs index.html`。
- 本地预览在 Windows 上用 `npx serve <目录>` 或 `python -m http.server <端口>`，
  不要照抄 bash 里的 `python3 -m http.server` 写法。端口要挑一个当前没被占用的，
  被占用就换一个——写死的端口迟早会撞车。
- 路径交给 Node 处理，不要在提示里让用户手拼 `assets\audio\…`。
