---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 37e96dfbf8ec7099594743f8dac31772
    PropagateID: 37e96dfbf8ec7099594743f8dac31772
    ReservedCode1: 30450220504d61362417568939f285f8492595e5868283e1b14fc3f16f9fcc473bb2f0990221008c55bb129b0937b5285a7f507754056d835f2218c6c35e3060c1d2933b498b88
    ReservedCode2: 3045022038476a885a038cca14b536fba252dc6a6fd62572e3e8f2527f36b526f14f6507022100f25d543cfc3022af8bc5b869d2d8bf413be95f5ed2b4360d4aeffbeab48f658c
description: |-
    把书稿转成可直接阅读、可导出 PDF 的单文件 HTML 电子版：纸书扫描页图片 / PDF / 纯文字稿，
    提取文字并判定结构（章、小标题、正文、引文、表格、要点、配图），生成带章节目录、阅读进度条与
    打印分页样式的网页。视觉系统固定为白底、黑字正文、橙黄大标题、深色小标题。
    Load this skill whenever the user says 「电子版」「书稿转网页」「扫描件做成 HTML」「把这本书做成可读页面」
    「可视化生成电子版」"make an ebook page" / "turn this book into an HTML reading page"，
    或要求在已有电子版页面上继续加章节、换一本书、沿用同一套版式。
    不要用于：单页说明型 / 演示型网页（用 visual-page）、导出 PDF 文件本身（用 pdf）、
    只做一张封面海报或营销落地页（用 visual-page / frontend-design）、给现有网页改配色（直接改 CSS 即可）。
name: ebook-visual-html
---

# 电子版可视化 HTML 生成

把一本书变成能读、能翻、能导 PDF 的网页。版式是这个 skill 的固定资产：**白底、黑字正文、
橙黄大标题、深色小标题**。用户没提出配色要求前，不要凭个人审美改 `:root` 里的 token；
多本书之间视觉必须一致，这是本 skill 存在的理由。

## Inputs to collect

从对话和素材里先确认这四项。缺哪项就用中性占位继续推进，不要为了一本书反问一串问题：
- 书名、作者（用于封面区；没有就写「书名待定」并在交付时说明）
- 封面图文件（没有则用纯色封面占位，提示用户后续替换）
- 正文来源：扫描页图 / PDF / 纯文字稿
- 交付目录：默认 `<当前工作目录>/<书名简称>/`，用户指定了就用他指定的

## Procedure

1. 先读 `references/components.md` 和 `references/template.html` 再动手。
   原因：组件类名与版式 token 是这个 skill 的契约；不读就手写 HTML，样式会和模板漂移，
   下一本书就得重调一遍。

2. 盘点素材：确定页序、书籍信息（书名/作者/出版社/章节数）、哪些页是配图页。
   原因：页序错一次，后面每张图、每段正文都会错位，返工成本高于核对成本。

3. 逐页提取文字并做结构判定。用 read 看图（PDF 先用 pdf skill 取文），把内容判成：
   章 / 小标题（h3、h4）/ 正文段 / 引文 / 并列要点 / 表格 / 对比数据 / 时间线 / 编者补充 / 配图。
   判定规则见 `references/components.md`。两条最容易出错的：
   **保留原文的段落切分**，不要把同一段里的话并进上一个 `<p>`——一本书的呼吸感就在段与段之间；
   **副标题、简介、类别只用素材里已有的信息**，素材没写就留空，不要替作者编。
   **配图默认只当图片使用，不去 OCR 图上的文字**，除非用户明确要提取图中文字——
   书页配图与正文混排时，OCR 配图文字是这类任务最常见的错误来源。
   原因：把扫描页顺序铺成连续段落，读起来像 Word 导出的网页，不是书。

4. 按 `references/content-schema.md` 写成 `content.json`。
   原因：结构化中间产物让"改一章不用重写整页"，也让 build 脚本保证每本书用同一套类名。

5. 按 `references/image-prep.md` 处理图片：正文配图 ≤1600px、`assets/img/p001.jpg` 顺序命名，
   封面单独放 `assets/cover.jpg`。
   原因：扫描件原图动辄几 MB，整本直塞会让页面卡到读不下去；缩到阅读尺寸是这一步的主要目的。

6. 生成页面：`node <skill>/scripts/build.mjs <work>/content.json`。
   脚本读 `references/template.html` 注入内容，产出 `<work>/index.html`。
   原因：每本书手写七百行 HTML 必然产生不一致，脚本渲染是确定性的。
   模板确实缺某种布局时，改 `references/template.html` 与 build 的 block 分支，
   不要在生成结果里手改 HTML——下次重建会全部丢掉。

7. 校验：`node <skill>/scripts/verify.mjs <work>/index.html`，修到零错误。
   它查资源路径、alt、目录锚点、章节数、残留占位符、标签闭合、版式 token。
   原因：这几项错起来都不会报错，只会安静地坏掉（图片裂开、目录点不动）。

8. 视觉自检：打开页面确认首屏（封面 + 第一章开头），以及一张含表格或卡片的长内容页。
   原因：栏宽、行高、卡片塌陷这类问题静态检查看不出来，只有渲染后才暴露。

9. 交付：给出 `index.html` 绝对路径 + `<deliver-assets>` 包裹的 `<media>`，并说明四件事：
   怎么本地打开、配色 token 在哪（`references/template.html` 的 `:root`）、怎么导出 PDF（⌘P，已分页）、
   想改内容改 `content.json` 再 rebuild。

## Output contract

- `<work>/index.html` — 单文件，CSS/JS 内联，只依赖 `<work>/assets/` 下的本地图片；不引 CDN、不引外链字体
- `<work>/assets/cover.jpg` + `<work>/assets/img/pNNN.jpg` — 网页尺寸（≤1600px）的图
- `<work>/content.json` — 结构化正文，改内容只改它再 rebuild
- `<work>/content.md` — 同一份内容的纯文字稿，方便逐字校对
- 交付说明：路径 + 打开方式 + token 位置 + PDF 导出方式

## Failure handling

- 图片工具（sips / ffmpeg / ImageMagick / Pillow）都不可用时，不要把原图直链了事。
  保留原图，但必须在交付说明里写清「图片未压缩，页面偏重」，让用户决定是装工具还是接受。
  原因：安静地降级会让用户后面在低端设备上才发现页面卡。
- `prepare-images.mjs` 报"成功但没有产物"时（受限沙箱里 sips 常见），先确认目标文件是否存在，
  存在即忽略该报错，不存在就换下一个工具重试，不要重复跑同一个失败命令。
- 某页扫描质量差、看不清时不要猜：保留 `.slot` 占位，并在交付说明里列出待补页码。
  原因：编造出来的正文比空白危害大得多。
- 用户要的组件模板里没有时，先查 `components.md` 有没有等价类；确实没有才加
  `template.html` + `build.mjs`，并把新类名补进 `components.md`，让下一本书能用上。

## Examples

- Input：「《XXX》扫描件放在 scans/ 了，做成电子版网页」
  → 图片缩放排序 → 逐页提取定结构 → `content.json` → build → verify → 交付 `index.html`
- Input：「这个页面再补两章」
  → 只往 `chapters` 里追加两块并 rebuild，目录与阅读进度自动更新，不重写 HTML

## Windows (win32) platform notes

- `build.mjs` / `verify.mjs` 是 Node 脚本，跨平台一致：`node scripts\build.mjs content.json`。
- `prepare-images.mjs` 按 sips → magick → ffmpeg → Pillow 顺序探测工具。Windows 上通常命中
  ImageMagick（`magick`）或 Python + Pillow，命令差异见 `references/image-prep.md`。
- 路径分隔符交给 Node 处理，不要在提示里让用户手拼 `assets\img\p001.jpg`。
