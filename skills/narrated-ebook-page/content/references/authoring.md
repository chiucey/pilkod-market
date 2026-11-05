# 内容灌注手册

模板是骨架，这篇讲怎么把内容装进去。装完跑 `node scripts/check-page.mjs <文件>` 校验。

## 一、整体结构

```html
<body>
  <div class="progress"><i id="bar"></i></div>   <!-- 外壳，别动 -->
  <header class="mbar" id="mbar">…</header>        <!-- 移动端顶栏，别动 -->
  <aside class="rail" id="rail">…</aside>          <!-- 左侧目录，改条目 -->
  <div class="controls" id="controls">…</div>      <!-- 字号/打印，别动 -->
  <div class="ttsbar" id="ttsBar">…</div>          <!-- 朗读竖条，别动 -->
  <div class="tts" id="ttsPanel">…</div>           <!-- 朗读面板，别动 -->

  <main class="stage">
    <section class="cover" id="cover">…</section>  <!-- 封面卡：改内容 -->
    <div class="divider">◆ ◆ ◆</div>
    <section class="chapter" id="toc">…</section>  <!-- 序章（目录）：改条目 -->
    <section class="chapter" id="ch1">…</section>  <!-- 正文章：改内容 -->
    …
    <div class="colophon">…</div>
  </main>

  <script>…</script>                                <!-- 引擎，别动 -->
</body>
```

## 二、章节

一章一个 `section.chapter`，id 用 `ch1`、`ch2`……：

```html
<section class="chapter" id="ch1">
  <header class="chapter__head">
    <span class="chapter__no">第一章</span>
    <h2 class="chapter__title">章节标题</h2>
    <p class="chapter__lead">一句话导语：这一章要替读者解决的问题。</p>
  </header>
  …
</section>
```

左侧目录同步加一条：

```html
<a href="#ch1" data-ch="ch1"><small>第一章</small>章节标题</a>
```

`data-ch` 必须等于章节 id——目录高亮靠它。目录里列「序」和正文章节；
封面条目没有 `data-ch`，它只用来跳回首屏。

## 三、段落与朗读标记

每个要朗读的元素带两个属性：

- `data-tts-c`：章节 id，和所在 `section.chapter` 的 id 一致
- `data-tts-i`：章内序号，从 0 开始连续递增，不跳号

```html
<h3 class="h h--3" data-tts-c="ch1" data-tts-i="0">小标题</h3>
<p class="prose" data-tts-c="ch1" data-tts-i="1">正文段落。</p>
<p class="prose" data-tts-c="ch1" data-tts-i="2">下一段。</p>
<h3 class="h h--3" data-tts-c="ch1" data-tts-i="3">下一个小标题</h3>
```

要点卡把标记打在 `card__b` 上（朗读时读标题 + 描述）：

```html
<div class="card">
  <div class="card__n">01</div>
  <div class="card__b" data-tts-c="ch1" data-tts-i="4">
    <p class="card__t">要点标题</p>
    <p class="card__d">一句话说明。</p>
  </div>
</div>
```

**不要用 DOM 顺序代替序号**。章节重排、手动插段之后序号必然错位，
表现是「念 A 段高亮 B 段」。校验脚本会检查每章序号是否连续。

要朗读的段落文字取自元素文本。想让朗读念的内容与显示内容不同，
在该元素上加 `data-tts-text="要念的文本"`。

**章标题与导语不朗读**（它们是导航，不是正文）。

**目录章（`id="toc"`）的条目会被朗读**——模板里每个目录 `<li>` 都带着
`data-tts-c="toc"` 和连续的 `data-tts-i`，所以连续朗读时会把全书目录念一遍，
相当于有声书的「目录页」。要保留这个行为就照抄模板；不想要就**删掉目录 `<li>` 上的
`data-tts-c` 与 `data-tts-i`**——引擎的章间跳转只认「有朗读段的章」，
删掉后目录章会被自动跳过，不会出现「点了下一章没反应」。

两种做法都对，但**要挑一种并且知道自己在挑什么**：目录条目如果既有标记又缺 `data-tts-i`，
校验脚本会报序号不连续。

## 四、封面（首屏）

封面是读者打开页面后第一眼看到的东西。模板默认给一张**文字封面卡**：
题目 + 副题 + 关键数字 + 两个明确入口 + 一句能力说明 + 一段导语。

```html
<section class="cover" id="cover">
  <div class="cover__card">
    <div class="cover__top">
      <span class="cover__kicker">分类标签</span>
      <span class="cover__badge">版本或状态</span>
    </div>
    <h1 class="cover__title">书名</h1>
    <p class="cover__sub">副标题</p>
    <p class="cover__by">著 <b>作者</b>　·　文档类型</p>
    <dl class="cover__nums">
      <div class="cover__num"><dt>关键数字一</dt><dd>12<small>章</small></dd></div>
      <div class="cover__num"><dt>关键数字二</dt><dd>1.2<small>万字</small></dd></div>
      …
    </dl>
    <div class="cover__cta">
      <a class="btn btn--primary" id="btnStartRead" href="#ch1">开始阅读</a>
      <a class="btn" href="#toc">全书目录</a>
    </div>
    <ul class="cover__hint">
      <li><b>▶</b> 点「开始阅读」即从第一章开始朗读</li>
      <li><b>⇩</b> 可导出 PDF</li>
      <li><b>12</b> 章 · 约 1.2 万字</li>
    </ul>
  </div>
  <div class="wrap"><p class="cover__intro">导语……</p></div>
</section>
```

**封面只做文字卡片，不做封面图**：不引外部图片、不放图片占位框、不依赖任何图文件。
封面图会毁掉这个模板的两个前提——单文件自包含（离线可读、不下载外部文件）与
打印不失真。需要图的地方用正文里的 `.slot` 占位，素材到位了再换成内联 SVG。

`.cover__nums` 是「结论前置」：四个读者扫一眼就要拿走的数字。标签写具体的维度
（「种子轮融资」「出让股权」），不要写「指标一」「指标二」。

`id="btnStartRead"` 必须保留：它绑定了「跳转第一章 + 立刻起播」。
去掉这个 id，按钮就只剩普通锚点跳转，不会开始朗读。

`href="#ch1"` 保留：禁用 JS 时它仍然是可用的目录入口。

不要把封面退回成「虚线占位框 + 重复一遍标题」：读者打开页面要立刻知道
这是什么文档、能干什么、结论是什么。

左侧目录里的「封面」条目保留（它没有 `data-ch`，不参与朗读与章节跳转）。

## 五、图表

内联 SVG，不要用 `<img>` 引外部图片（离线不可用、打印会糊）：

```html
<figure class="figure figure--svg">
  <div class="svgfig" data-svgfig="fig1" data-motion="reveal">
    <svg id="fig1" viewBox="0 0 960 300" xmlns="http://www.w3.org/2000/svg"
         class="svgfig__svg" role="img" aria-label="一句话说清这张图在讲什么">
      <g aria-hidden="true">
        <style>
          #fig1 text{ font-family:"PingFang SC",…; }
          #fig1 .hd{ font-size:17px; font-weight:700; fill:#0E1826; }
        </style>
        …
      </g>
    </svg>
  </div>
  <figcaption><b>图 1　图名</b>　图注说明这张图在讲什么，不是重复图里的文字。</figcaption>
</figure>
```

规则：

- `id` 必须唯一（图内样式按 id 选，重复会串）
- `viewBox` 必给，尺寸按内容定，一般宽 900–1200px
- `role="img"` + `aria-label` 必给；图内装饰性元素放 `aria-hidden="true"`
- `data-motion="reveal"` 进场淡入；`none` 不动（打印时用 `none`）
- SVG 里的配色用 token 的字面值：描边 `#E4E1DA`、底 `#FFFFFF`/`#FBFAF8`、
  强调底 `#FFF4DE`、强调线 `#F2A100`、文字 `#0E1826`/`#8A8F98`/`#C87C02`
- 窄屏正文窗口只有 350px，图有 880–1200px 宽 → 模板已内置「可横拖」提示
  与「全屏看」按钮（`figzoom` 层），不用自己加
- 素材还没到位时用 `<div class="slot"><b>插图待补</b>说明</div>`，别硬编一张图

### 图文联动（可选）

想让「读到某段时图里对应部件亮起来」：

```html
<!-- 图里：部件带 data-fig="键" -->
<rect class="box2" data-fig="rm-1">…</rect>

<!-- 正文：段落带 data-figkey="键"，多个键用空格分隔 -->
<p class="prose" data-tts-c="ch1" data-tts-i="5" data-figkey="rm-1 rm-2">这一段讲到图里的这两个部件。</p>
```

两侧键名一致才联动。朗读走到那段时，图里对应部件点亮、其余淡出；
反过来点图上的部件，会跳回正文对应段落并短暂高亮。

**这是可选增强**：不用它图也正常显示（没有 `data-figkey` 的段落一律不点亮，
图保持常态）。一页里只有一两个图时才值得加；每段都标会让图一直处于聚焦态。

## 六、表格

```html
<div class="tablewrap">
  <table>
    <thead><tr><th>列名 A</th><th>列名 B</th></tr></thead>
    <tbody>
      <tr><td data-l="列名 A">值</td><td data-l="列名 B">值</td></tr>
    </tbody>
  </table>
</div>
```

**每个 `td` 必须带 `data-l`**：手机档宽表会摊成卡片，`data-l` 用来把列名
显示成行内小标签。漏了就只剩一列值，读者不知道是什么。

列数超过 4 列时正文会显得拥挤——先想能不能用要点卡或数据条代替。

## 七、数据条与时间轴

```html
<div class="bars">
  <div class="bar__row"><span class="bar__label">标签</span>
    <span class="bar__track"><span class="bar__fill" style="--w:50"></span></span>
    <span class="bar__val">50%</span></div>
</div>
```

`--w` 是 0–100 的比例（不是原始数值）；`bar__val` 里放给人看的值。

```html
<ol class="timeline">
  <li><time>2026-01</time><b>事件标题</b><p>说明。</p></li>
</ol>
```

## 八、标签与待补占位

少量并列属性用标签，别用要点卡（卡片是给「有标题 + 有说明」的内容用的，
标签只标属性本身）：

```html
<div class="tags">
  <span class="tag">文档类型</span>
  <span class="tag tag--amber">重点章节</span>
</div>
```

`.tags` 是自动换行的弹性行，`.tag` 是描边胶囊，`.tag--amber` 是琥珀底变体
（琥珀底上的字用 `--amber-deep`，模板已配好）。

素材还没到位时用占位块，别硬编一张图，也别留空：

```html
<div class="slot"><b>插图待补</b>这里说明将要放什么图</div>
```

`.slot` 里的 `<b>` 是标签文字，模板已给它上了琥珀色。

## 九、交付前自查

- [ ] 封面标题、章数字数与实际一致（封面里的数字错了读者会当场发现）
- [ ] 封面里没有图片、没有外链图（封面只做文字卡片）
- [ ] `<title>`、`<meta name="description">`、版权页（书名 / 作者 / 版本）都换成本文档的
- [ ] 左侧目录条目数 = 章节数 + 1（序）
- [ ] 每章 `data-tts-i` 从 0 连续，无跳号
- [ ] 目录章要么照模板带着朗读标记，要么整条删干净（校验输出会列出「哪几章会被朗读」）
- [ ] 表格每个 `td` 有 `data-l`
- [ ] 每张 SVG 有 `role="img"` 和 `aria-label`
- [ ] 跑过 `node scripts/make-audio.mjs index.html`（音频清单与段落一一对应，
      音色是「电台男主播」）
- [ ] 作者、版本等「待定」字段已补齐，或已明确写进交付说明
- [ ] `id="btnStartRead"` 还在，`href="#ch1"` 指向真实第一章
- [ ] `node scripts/check-page.mjs index.html` 零错误
- [ ] 390 / 834 / 1280 三档视口没有横向滚动、没有压字
