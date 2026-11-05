---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3044022033180f0aa39473e84d4e64403c977603713e294983af871addc68901049f05f002206c4f80908bca8121bf16f645ea1d7fd0cb405ce2105824a3d2b4b4d79304f9a6
    ReservedCode2: 3045022050c8f9dac10d16e3fdbe1132d84ddba2ec420138f780d8e6fbfd9ee12490985b022100c64dbd2f7fae32226e204ab7cf195c48372ef494b392cb6c902a8be8182dce8a
---

# 页面布局库 · Layouts

> 本文档收录12种最常用的页面布局骨架。每个布局都是一个完整可粘贴的HTML代码块，直接替换文案/图片即可使用。

## ⚠️ 重要说明

### A. 类名必须来自template.html

layouts.md使用的所有类名（如`h-hero`、`h-xl`、`stat-card`、`grid-6`等）都必须在`assets/template.html`中已定义。在使用布局前，必须先确保template.html已被复制到项目目录。

### B. 主题变量必须存在

布局中的颜色引用（如`var(--accent)`、`var(--bg)`）必须在`:root`中定义。确保在切换主题后布局正常工作。

### C. 动画属性可选

`data-anim`和`data-animate`属性用于控制动画效果。如果不需要动画，可以移除这些属性。

### D. 图片高度固定

所有图片网格必须使用`height:Nvh`固定高度，禁止使用`aspect-ratio`。这确保网格布局的稳定性。

---

## 布局1：Hero全屏封面

适用场景：开场封面、章节过渡、结尾致谢

特点：视觉冲击力强，大标题居中，常配合WebGL背景效果

```html
<section class="slide hero" data-theme="dark" data-animate="hero">
  <div class="chrome">
    <div class="left">项目名称</div>
    <div class="center"></div>
    <div class="right">01</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;text-align:center;">
    <div class="kicker" data-anim>2024年度汇报</div>
    <h1 class="display-zh" data-anim style="margin:2vh 0;">
      智慧城市建设<br>成果汇报
    </h1>
    <p class="lead" data-anim style="color:var(--gray-3);max-width:60vw;">
      数字化转型引领城市治理现代化
    </p>
    <div class="meta" data-anim style="margin-top:4vh;">
      汇报人：XXX ｜ 汇报日期：2024年12月
    </div>
  </div>

  <div class="foot">
    <div class="left">01 / 15</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">Hero</div>
  </div>
</section>
```

---

## 布局2：章节幕封

适用场景：章节过渡页、章节开始页

特点：简洁有力，章节编号醒目，用于分隔内容的节奏感

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第一章</div>
    <div class="center"></div>
    <div class="right">03</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;height:100%;">
    <div class="big-num" data-anim style="color:var(--accent);opacity:0.15;font-size:20vw;position:absolute;right:-5vw;top:-5vh;z-index:0;">
      01
    </div>
    <div style="position:relative;z-index:1;">
      <div class="kicker" data-anim>CHAPTER ONE</div>
      <h1 class="h1-zh" data-anim>建设背景与目标</h1>
      <p class="body-zh" data-anim style="max-width:50vw;color:var(--gray-4);margin-top:2vh;">
        阐述项目政策背景、建设意义和总体目标
      </p>
    </div>
  </div>

  <div class="foot">
    <div class="left">03 / 15</div>
    <div class="center"></div>
    <div class="right">Chapter 01</div>
  </div>
</section>
```

---

## 布局3：左文右图（标准内容页）

适用场景：概念说明、功能介绍、案例展示

特点：左右分栏，内容和图片各占一半，视觉平衡

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第一章 · 建设背景</div>
    <div class="center"></div>
    <div class="right">04</div>
  </div>

  <div class="content" style="display:grid;grid-template-columns:1fr 1fr;gap:4vw;height:100%;align-items:center;">
    <!-- 左侧文字内容 -->
    <div>
      <div class="kicker" data-anim>政策背景</div>
      <h2 class="h2-zh" data-anim style="margin:1vh 0;">
        国家数字化战略部署
      </h2>
      <p class="body-zh" data-anim style="color:var(--gray-3);line-height:1.8;">
        根据《"十四五"数字经济发展规划》和《智慧城市建设指导意见》，推进城市数字化转型是提升治理效能的关键举措。
      </p>
      <ul data-anim style="margin-top:2vh;padding-left:1.5vw;">
        <li class="body-zh" style="margin-bottom:1vh;">✓ 政策支持：多项国家政策明确支持</li>
        <li class="body-zh" style="margin-bottom:1vh;">✓ 资金保障：专项财政资金支持</li>
        <li class="body-zh">✓ 技术成熟：5G、AI、物联网技术支撑</li>
      </ul>
    </div>

    <!-- 右侧图片 -->
    <div class="frame-img h-28" data-anim>
      <img src="/assets/policy-architecture.png" alt="政策架构图" loading="lazy" style="object-fit:contain;">
    </div>
  </div>

  <div class="foot">
    <div class="left">04 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">01 · Background</div>
  </div>
</section>
```

---

## 布局4：Stat数字大字报

适用场景：数据展示页、成果展示页、核心指标页

特点：大数字醒目，配合简短说明，数据冲击力强

```html
<section class="slide" data-theme="dark">
  <div class="chrome">
    <div class="left">第三章 · 建设成效</div>
    <div class="center"></div>
    <div class="right">08</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;height:100%;">
    <div class="kicker" data-anim style="margin-bottom:2vh;">KEY METRICS</div>
    <h2 class="h2-zh" data-anim style="margin-bottom:4vh;">核心建设成果</h2>

    <div class="grid" style="grid-template-columns:repeat(3,1fr);gap:3vw;">
      <!-- 数据卡片1 -->
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">平台接入量</div>
        <div class="n">2,847 <small>万</small></div>
        <div class="l">同比提升 156%</div>
      </div>

      <!-- 数据卡片2 -->
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">办件效率提升</div>
        <div class="n">68<span style="font-size:0.4em;">%</span></div>
        <div class="l">平均办理时限缩短</div>
      </div>

      <!-- 数据卡片3 -->
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">用户满意度</div>
        <div class="n">96.8<span style="font-size:0.4em;">%</span></div>
        <div class="l">服务好评率</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">08 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">03 · Results</div>
  </div>
</section>
```

---

## 布局5：Pipeline流程步骤

适用场景：实施路径、流程说明、分步讲解

特点：步骤清晰，进度可控，适合需要引导观众理解的流程说明

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第四章 · 实施路径</div>
    <div class="center"></div>
    <div class="right">10</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;height:100%;">
    <div class="kicker" data-anim>IMPLEMENTATION ROADMAP</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">四阶段实施计划</h2>

    <div class="pipeline">
      <!-- 步骤1 -->
      <div class="step" data-anim="step">
        <div class="step-nb">01</div>
        <div class="step-title">基础夯实</div>
        <div class="step-desc">完成基础设施建设和数据归集</div>
        <div class="step-meta">2024.Q1-Q2</div>
      </div>

      <!-- 步骤2 -->
      <div class="step" data-anim="step">
        <div class="step-nb">02</div>
        <div class="step-title">平台搭建</div>
        <div class="step-desc">构建统一数据中台和应用支撑</div>
        <div class="step-meta">2024.Q2-Q3</div>
      </div>

      <!-- 步骤3 -->
      <div class="step" data-anim="step">
        <div class="step-nb">03</div>
        <div class="step-title">应用推广</div>
        <div class="step-desc">部署核心业务系统并推广应用</div>
        <div class="step-meta">2024.Q3-Q4</div>
      </div>

      <!-- 步骤4 -->
      <div class="step" data-anim="step">
        <div class="step-nb">04</div>
        <div class="step-title">优化迭代</div>
        <div class="step-desc">持续优化提升和功能迭代</div>
        <div class="step-meta">2025.Q1+</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">10 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">04 · Roadmap</div>
  </div>
</section>
```

---

## 布局6：大引用金句

适用场景：核心观点、领导讲话、重要结论

特点：引用醒目，配合引言来源，增强说服力

```html
<section class="slide hero" data-theme="dark">
  <div class="chrome">
    <div class="left"></div>
    <div class="center"></div>
    <div class="right">12</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;text-align:center;position:relative;z-index:2;">
    <blockquote class="callout" data-anim style="max-width:70vw;border-left:4px solid var(--accent);padding-left:3vw;">
      <p style="font-family:var(--font-serif);font-size:3vw;line-height:1.5;color:var(--fg);">
        "数字化转型不是选择题，而是生存题。<br>谁先完成转型，谁就赢得未来。"
      </p>
    </blockquote>
    <cite class="meta" data-anim style="margin-top:3vh;color:var(--gray-4);">
      — 某市数字化改革工作领导小组
    </cite>
  </div>

  <div class="foot">
    <div class="left">12 / 15</div>
    <div class="center"></div>
    <div class="right">Quote</div>
  </div>
</section>
```

---

## 布局7：Before/After对比

适用场景：效果对比、问题与方案、过去与现在

特点：左右对比，直观展示差异和进步

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第三章 · 建设成效</div>
    <div class="center"></div>
    <div class="right">09</div>
  </div>

  <div class="content" style="display:grid;grid-template-columns:1fr 1fr;gap:4vw;height:100%;align-items:center;">
    <!-- 左侧：Before -->
    <div data-anim="left">
      <div class="kicker" style="color:var(--gray-4);">BEFORE</div>
      <h3 class="h3-zh" style="color:var(--gray-3);margin:1vh 0 2vh;">传统模式痛点</h3>
      <div class="pillar" style="background:var(--bg-secondary);padding:2vh;border-radius:8px;">
        <div class="ic" style="color:var(--gray-4);">✗</div>
        <div class="ti" style="color:var(--gray-4);">信息孤岛</div>
        <div class="desc" style="color:var(--gray-4);">各部门系统独立，数据无法共享</div>
      </div>
      <div class="pillar" style="background:var(--bg-secondary);padding:2vh;border-radius:8px;margin-top:2vh;">
        <div class="ic" style="color:var(--gray-4);">✗</div>
        <div class="ti" style="color:var(--gray-4);">办事繁琐</div>
        <div class="desc" style="color:var(--gray-4);">群众需要跑多个部门，耗时长</div>
      </div>
      <div class="pillar" style="background:var(--bg-secondary);padding:2vh;border-radius:8px;margin-top:2vh;">
        <div class="ic" style="color:var(--gray-4);">✗</div>
        <div class="ti" style="color:var(--gray-4);">决策困难</div>
        <div class="desc" style="color:var(--gray-4);">缺乏数据支撑，决策凭经验</div>
      </div>
    </div>

    <!-- 右侧：After -->
    <div data-anim="right">
      <div class="kicker" style="color:var(--accent);">AFTER</div>
      <h3 class="h3-zh" style="color:var(--fg);margin:1vh 0 2vh;">数字化转型成效</h3>
      <div class="pillar" style="background:var(--accent-light);padding:2vh;border-radius:8px;border-left:4px solid var(--accent);">
        <div class="ic" style="color:var(--accent);">✓</div>
        <div class="ti" style="color:var(--fg);">数据贯通</div>
        <div class="desc" style="color:var(--gray-2);">统一数据中台，全量数据共享</div>
      </div>
      <div class="pillar" style="background:var(--accent-light);padding:2vh;border-radius:8px;border-left:4px solid var(--accent);margin-top:2vh;">
        <div class="ic" style="color:var(--accent);">✓</div>
        <div class="ti" style="color:var(--fg);">一网通办</div>
        <div class="desc" style="color:var(--gray-2);">线上全程办理，最多跑一次</div>
      </div>
      <div class="pillar" style="background:var(--accent-light);padding:2vh;border-radius:8px;border-left:4px solid var(--accent);margin-top:2vh;">
        <div class="ic" style="color:var(--accent);">✓</div>
        <div class="ti" style="color:var(--fg);">智能决策</div>
        <div class="desc" style="color:var(--gray-2);">大数据分析，精准决策支撑</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">09 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">03 · Comparison</div>
  </div>
</section>
```

---

## 布局8：图片网格

适用场景：案例展示、功能展示、作品集

特点：多图并列展示，视觉丰富

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第三章 · 应用案例</div>
    <div class="center"></div>
    <div class="right">11</div>
  </div>

  <div class="content" style="padding-top:4vh;">
    <div class="kicker" data-anim>APPLICATION CASES</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 3vh;">典型应用场景</h2>

    <div class="grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5vw;">
      <!-- 图片卡片1 -->
      <figure class="figure" data-anim>
        <div class="frame-img h-22">
          <img src="/assets/case-1.png" alt="智慧交通" loading="lazy">
        </div>
        <figcaption>
          <div class="title">智慧交通</div>
          <div class="stat">实时路况优化</div>
        </figcaption>
      </figure>

      <!-- 图片卡片2 -->
      <figure class="figure" data-anim>
        <div class="frame-img h-22">
          <img src="/assets/case-2.png" alt="智慧政务" loading="lazy">
        </div>
        <figcaption>
          <div class="title">智慧政务</div>
          <div class="stat">一网通办平台</div>
        </figcaption>
      </figure>

      <!-- 图片卡片3 -->
      <figure class="figure" data-anim>
        <div class="frame-img h-22">
          <img src="/assets/case-3.png" alt="智慧医疗" loading="lazy">
        </div>
        <figcaption>
          <div class="title">智慧医疗</div>
          <div class="stat">电子健康档案</div>
        </figcaption>
      </figure>
    </div>
  </div>

  <div class="foot">
    <div class="left">11 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">03 · Cases</div>
  </div>
</section>
```

---

## 布局9：问题与建议

适用场景：挑战分析、问题讨论、建议提出

特点：清晰列出问题，配合对策说明

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第五章 · 问题与建议</div>
    <div class="center"></div>
    <div class="right">13</div>
  </div>

  <div class="content" style="display:grid;grid-template-columns:1fr 1fr;gap:3vw;height:100%;align-items:start;padding-top:6vh;">
    <!-- 左侧：问题 -->
    <div>
      <div class="kicker" data-anim style="color:var(--error);">CHALLENGES</div>
      <h3 class="h3-zh" data-anim style="margin:1vh 0 2vh;">面临的主要挑战</h3>

      <div class="rowline" data-anim>
        <div class="k" style="color:var(--fg);">数据安全</div>
        <div class="v" style="color:var(--gray-3);">跨部门数据共享存在安全风险</div>
        <div class="m" style="color:var(--gray-4);">HIGH</div>
      </div>

      <div class="rowline" data-anim>
        <div class="k" style="color:var(--fg);">人才短缺</div>
        <div class="v" style="color:var(--gray-3);">复合型数字化人才不足</div>
        <div class="m" style="color:var(--gray-4);">MEDIUM</div>
      </div>

      <div class="rowline" data-anim>
        <div class="k" style="color:var(--fg);">资金压力</div>
        <div class="v" style="color:var(--gray-3);">后续运维资金持续投入需求</div>
        <div class="m" style="color:var(--gray-4);">MEDIUM</div>
      </div>
    </div>

    <!-- 右侧：对策 -->
    <div>
      <div class="kicker" data-anim style="color:var(--success);">SOLUTIONS</div>
      <h3 class="h3-zh" data-anim style="margin:1vh 0 2vh;">对策与建议</h3>

      <div class="pillar" data-anim style="border-left:3px solid var(--accent);padding-left:1.5vw;margin-bottom:2vh;">
        <div class="ti" style="font-size:1.4vw;">完善安全体系</div>
        <div class="desc" style="color:var(--gray-3);">建立数据分级分类管理制度</div>
      </div>

      <div class="pillar" data-anim style="border-left:3px solid var(--accent);padding-left:1.5vw;margin-bottom:2vh;">
        <div class="ti" style="font-size:1.4vw;">加强人才培养</div>
        <div class="desc" style="color:var(--gray-3);">与高校合作，培养复合型人才</div>
      </div>

      <div class="pillar" data-anim style="border-left:3px solid var(--accent);padding-left:1.5vw;">
        <div class="ti" style="font-size:1.4vw;">拓宽资金渠道</div>
        <div class="desc" style="color:var(--gray-3);">争取上级资金和社会资本支持</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">13 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">05 · Challenges</div>
  </div>
</section>
```

---

## 布局10：时间轴/里程碑

适用场景：发展历程、时间规划、路线图

特点：时间线清晰，展示时间维度的进展

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">附录 · 里程碑</div>
    <div class="center"></div>
    <div class="right">14</div>
  </div>

  <div class="content" style="padding-top:4vh;">
    <div class="kicker" data-anim>MILESTONES</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">项目发展历程</h2>

    <div class="timeline" style="position:relative;padding-left:3vw;">
      <!-- 时间线主轴 -->
      <div style="position:absolute;left:1vw;top:0;bottom:0;width:2px;background:var(--gray-6);"></div>

      <!-- 里程碑1 -->
      <div class="timeline-item" data-anim style="position:relative;padding-left:3vw;margin-bottom:4vh;">
        <div style="position:absolute;left:-0.6vw;top:0.5vh;width:1.2vw;height:1.2vw;border-radius:50%;background:var(--accent);"></div>
        <div class="meta" style="color:var(--accent);">2023年6月</div>
        <h4 class="h4-zh" style="margin:0.5vh 0;">项目启动</h4>
        <p class="body-zh" style="color:var(--gray-3);">完成项目立项和总体方案设计</p>
      </div>

      <!-- 里程碑2 -->
      <div class="timeline-item" data-anim style="position:relative;padding-left:3vw;margin-bottom:4vh;">
        <div style="position:absolute;left:-0.6vw;top:0.5vh;width:1.2vw;height:1.2vw;border-radius:50%;background:var(--accent);"></div>
        <div class="meta" style="color:var(--accent);">2023年12月</div>
        <h4 class="h4-zh" style="margin:0.5vh 0;">一期上线</h4>
        <p class="body-zh" style="color:var(--gray-3);">数据中台和首批应用系统上线</p>
      </div>

      <!-- 里程碑3 -->
      <div class="timeline-item" data-anim style="position:relative;padding-left:3vw;margin-bottom:4vh;">
        <div style="position:absolute;left:-0.6vw;top:0.5vh;width:1.2vw;height:1.2vw;border-radius:50%;background:var(--success);"></div>
        <div class="meta" style="color:var(--success);">2024年6月</div>
        <h4 class="h4-zh" style="margin:0.5vh 0;">二期完成</h4>
        <p class="body-zh" style="color:var(--gray-3);">核心业务系统全覆盖</p>
      </div>

      <!-- 里程碑4 -->
      <div class="timeline-item" data-anim style="position:relative;padding-left:3vw;">
        <div style="position:absolute;left:-0.6vw;top:0.5vh;width:1.2vw;height:1.2vw;border-radius:50%;background:var(--gray-4);border:2px solid var(--gray-4);"></div>
        <div class="meta" style="color:var(--gray-4);">2024年12月（计划）</div>
        <h4 class="h4-zh" style="margin:0.5vh 0;">全面验收</h4>
        <p class="body-zh" style="color:var(--gray-3);">完成项目整体验收和移交</p>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">14 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">Appendix · Timeline</div>
  </div>
</section>
```

---

## 布局11：三栏支柱

适用场景：核心优势、并列概念、三大要点

特点：三个并列模块，强调平衡和均等

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">第二章 · 建设内容</div>
    <div class="center"></div>
    <div class="right">05</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;height:100%;">
    <div class="kicker" data-anim>CORE ARCHITECTURE</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">整体技术架构</h2>

    <div class="grid-3" style="display:grid;grid-template-columns:repeat(3,1fr);gap:3vw;">
      <!-- 支柱1 -->
      <div class="pillar" data-anim style="text-align:center;padding:3vh 2vw;background:var(--bg-secondary);border-radius:12px;">
        <div class="ic" style="font-size:3vw;color:var(--accent);margin-bottom:2vh;">01</div>
        <h4 class="h4-zh" style="margin-bottom:1.5vh;">基础设施层</h4>
        <p class="body-zh" style="color:var(--gray-3);font-size:1vw;">
          云计算中心<br>
          5G网络覆盖<br>
          物联网感知设备
        </p>
      </div>

      <!-- 支柱2 -->
      <div class="pillar" data-anim style="text-align:center;padding:3vh 2vw;background:var(--bg-secondary);border-radius:12px;">
        <div class="ic" style="font-size:3vw;color:var(--accent);margin-bottom:2vh;">02</div>
        <h4 class="h4-zh" style="margin-bottom:1.5vh;">数据中台层</h4>
        <p class="body-zh" style="color:var(--gray-3);font-size:1vw;">
          数据归集治理<br>
          数据共享交换<br>
          数据分析服务
        </p>
      </div>

      <!-- 支柱3 -->
      <div class="pillar" data-anim style="text-align:center;padding:3vh 2vw;background:var(--bg-secondary);border-radius:12px;">
        <div class="ic" style="font-size:3vw;color:var(--accent);margin-bottom:2vh;">03</div>
        <h4 class="h4-zh" style="margin-bottom:1.5vh;">应用支撑层</h4>
        <p class="body-zh" style="color:var(--gray-3);font-size:1vw;">
          统一身份认证<br>
          统一支付平台<br>
          统一消息中心
        </p>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">05 / 15</div>
    <div class="center">智慧城市建设成果汇报</div>
    <div class="right">02 · Architecture</div>
  </div>
</section>
```

---

## 布局12：结束致谢

适用场景：结尾页、感谢页、联系方式

特点：简洁收尾，配合联系方式

```html
<section class="slide hero" data-theme="dark">
  <div class="chrome">
    <div class="left"></div>
    <div class="center"></div>
    <div class="right">15</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;text-align:center;position:relative;z-index:2;">
    <div class="kicker" data-anim>THANK YOU</div>
    <h1 class="display-zh" data-anim style="margin:2vh 0;">
      感谢聆听
    </h1>
    <p class="lead" data-anim style="color:var(--gray-3);max-width:50vw;margin-bottom:4vh;">
      智慧城市建设是一项长期工程，我们将持续优化完善
    </p>

    <div class="meta" data-anim style="line-height:2;">
      汇报人：XXX<br>
      单　位：XXXXXX<br>
      电　话：XXX-XXXX-XXXX<br>
      邮　箱：example@domain.com
    </div>
  </div>

  <div class="foot">
    <div class="left">15 / 15</div>
    <div class="center"></div>
    <div class="right">End</div>
  </div>
</section>
```

---

## 布局选择决策树

```
开始选择布局
│
├── 这是封面页吗？
│   └── 是 → 布局1：Hero全屏封面
│
├── 这是章节过渡吗？
│   └── 是 → 布局2：章节幕封
│
├── 这是核心观点引用页吗？
│   └── 是 → 布局6：大引用金句
│
├── 这是对比展示吗？
│   └── 是 → 布局7：Before/After对比
│
├── 这是结尾致谢吗？
│   └── 是 → 布局12：结束致谢
│
├── 主要展示数据吗？
│   ├── 单一关键数据 → 布局4：Stat数字大字报
│   └── 多个并列数据 → 布局4 + 网格布局
│
├── 主要展示流程/步骤吗？
│   └── 是 → 布局5：Pipeline流程步骤
│
├── 主要展示时间线吗？
│   └── 是 → 布局10：时间轴/里程碑
│
├── 主要展示问题与对策吗？
│   └── 是 → 布局9：问题与建议
│
├── 主要展示图片吗？
│   └── 是 → 布局8：图片网格
│
├── 主要展示并列概念吗？
│   └── 是 → 布局11：三栏支柱
│
└── 一般内容说明页
    └── 布局3：左文右图（标准内容页）
```

---

## 布局变体13-18

### 布局13：代码展示

适用场景：技术分享、API文档、功能演示

特点：代码片段清晰展示，配合语法高亮

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">技术实现</div>
    <div class="center"></div>
    <div class="right">06</div>
  </div>

  <div class="content" style="display:grid;grid-template-columns:1fr 1fr;gap:3vw;height:100%;align-items:center;">
    <!-- 左侧：说明文字 -->
    <div>
      <div class="kicker" data-anim>TECHNICAL IMPLEMENTATION</div>
      <h2 class="h2-zh" data-anim style="margin:1vh 0 2vh;">API调用示例</h2>
      <p class="body-zh" data-anim style="color:var(--gray-3);line-height:1.8;">
        通过RESTful API获取数据，支持GET/POST请求，返回JSON格式数据。
      </p>
      <ul data-anim style="margin-top:2vh;padding-left:1.5vw;">
        <li class="body-zh" style="margin-bottom:1vh;">✓ 支持 HTTPS 加密传输</li>
        <li class="body-zh" style="margin-bottom:1vh;">✓ 返回标准化 JSON 格式</li>
        <li class="body-zh">✓ 完善的错误码说明</li>
      </ul>
    </div>

    <!-- 右侧：代码块 -->
    <div data-anim style="background:var(--gray-7);border-radius:8px;padding:2vh;overflow:auto;max-height:60vh;">
      <pre style="font-family:var(--font-mono);font-size:0.9vw;line-height:1.6;white-space:pre-wrap;"><code><span style="color:var(--accent);">fetch</span>(<span style="color:var(--success);">'/api/data'</span>)
  .then(res => res.<span style="color:var(--accent);">json</span>())
  .then(data => {
    console.<span style="color:var(--accent);">log</span>(data);
  })
  .catch(err => {
    console.<span style="color:var(--error);">error</span>(err);
  });</code></pre>
    </div>
  </div>

  <div class="foot">
    <div class="left">06 / 15</div>
    <div class="center">技术方案分享</div>
    <div class="right">Code</div>
  </div>
</section>
```

---

### 布局14：数据仪表盘

适用场景：运营报告、数据看板、实时监控

特点：多指标聚合展示，数据一目了然

```html
<section class="slide" data-theme="dark">
  <div class="chrome">
    <div class="left">运营数据看板</div>
    <div class="center"></div>
    <div class="right">07</div>
  </div>

  <div class="content" style="padding-top:4vh;">
    <div class="kicker" data-anim>REAL-TIME DASHBOARD</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 3vh;">今日运营数据</h2>

    <!-- 第一行：4个关键指标 -->
    <div class="mini-chart-grid" data-anim style="gap:2vw;">
      <div class="mini-chart-card" style="background:var(--bg-secondary);padding:2vh;border-radius:8px;">
        <div class="mini-chart-label">实时在线用户</div>
        <div class="mini-chart-value" style="color:var(--accent);font-size:2.5vw;">12,847</div>
        <div class="mini-chart-trend up">↑ 8.2%</div>
      </div>
      <div class="mini-chart-card" style="background:var(--bg-secondary);padding:2vh;border-radius:8px;">
        <div class="mini-chart-label">今日订单量</div>
        <div class="mini-chart-value" style="color:var(--success);font-size:2.5vw;">3,592</div>
        <div class="mini-chart-trend up">↑ 15.3%</div>
      </div>
      <div class="mini-chart-card" style="background:var(--bg-secondary);padding:2vh;border-radius:8px;">
        <div class="mini-chart-label">系统响应时间</div>
        <div class="mini-chart-value" style="color:var(--warning);font-size:2.5vw;">45ms</div>
        <div class="mini-chart-trend down">↓ 12.5%</div>
      </div>
      <div class="mini-chart-card" style="background:var(--bg-secondary);padding:2vh;border-radius:8px;">
        <div class="mini-chart-label">异常告警数</div>
        <div class="mini-chart-value" style="color:var(--error);font-size:2.5vw;">3</div>
        <div class="mini-chart-trend down">↓ 70%</div>
      </div>
    </div>

    <!-- 第二行：进度条 -->
    <div class="progress-container" data-anim style="margin-top:3vh;">
      <div class="progress-item">
        <div class="progress-header">
          <div class="progress-label">API 调用成功率</div>
          <div class="progress-value" style="color:var(--success);">99.8%</div>
        </div>
        <div class="progress-track" style="height:8px;"><div class="progress-fill" style="width:99.8%;background:var(--success);"></div></div>
      </div>
      <div class="progress-item">
        <div class="progress-header">
          <div class="progress-label">数据库同步率</div>
          <div class="progress-value" style="color:var(--accent);">98.5%</div>
        </div>
        <div class="progress-track" style="height:8px;"><div class="progress-fill" style="width:98.5%;background:var(--accent);"></div></div>
      </div>
      <div class="progress-item">
        <div class="progress-header">
          <div class="progress-label">缓存命中率</div>
          <div class="progress-value" style="color:var(--info);">95.2%</div>
        </div>
        <div class="progress-track" style="height:8px;"><div class="progress-fill" style="width:95.2%;background:var(--info);"></div></div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">07 / 15</div>
    <div class="center">运营数据看板</div>
    <div class="right">Dashboard</div>
  </div>
</section>
```

---

### 布局15：FAQ问答

适用场景：问题解答、培训课程、知识分享

特点：问答形式清晰展示，便于观众理解

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">常见问题</div>
    <div class="center"></div>
    <div class="right">10</div>
  </div>

  <div class="content" style="padding-top:4vh;">
    <div class="kicker" data-anim>FREQUENTLY ASKED QUESTIONS</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">常见问题解答</h2>

    <div style="display:flex;flex-direction:column;gap:2vh;">
      <!-- 问题1 -->
      <div class="pillar" data-anim style="border-left:3px solid var(--accent);padding-left:1.5vw;padding:2vh;background:var(--bg-secondary);border-radius:0 8px 8px 0;">
        <div class="h4-zh" style="color:var(--accent);margin-bottom:1vh;">Q: 如何申请开通服务？</div>
        <p class="body-zh" style="color:var(--gray-3);">A: 登录控制台，进入「服务管理」→「开通申请」，填写基本信息后提交审核，1-3个工作日内完成审核。</p>
      </div>

      <!-- 问题2 -->
      <div class="pillar" data-anim style="border-left:3px solid var(--accent);padding-left:1.5vw;padding:2vh;background:var(--bg-secondary);border-radius:0 8px 8px 0;">
        <div class="h4-zh" style="color:var(--accent);margin-bottom:1vh;">Q: 收费标准是怎样的？</div>
        <p class="body-zh" style="color:var(--gray-3);">A: 采用按量计费模式，根据API调用次数和数据存储量收费，详细价格请参考官网定价页。</p>
      </div>

      <!-- 问题3 -->
      <div class="pillar" data-anim style="border-left:3px solid var(--accent);padding-left:1.5vw;padding:2vh;background:var(--bg-secondary);border-radius:0 8px 8px 0;">
        <div class="h4-zh" style="color:var(--accent);margin-bottom:1vh;">Q: 数据安全性如何保障？</div>
        <p class="body-zh" style="color:var(--gray-3);">A: 采用银行级加密传输，数据存储多重备份，支持私有化部署，满足等保三级要求。</p>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">10 / 15</div>
    <div class="center">培训课程</div>
    <div class="right">FAQ</div>
  </div>
</section>
```

---

### 布局16：团队介绍

适用场景：团队展示、项目成员、公司架构

特点：成员信息清晰展示，配合照片和职位

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">关于我们</div>
    <div class="center"></div>
    <div class="right">02</div>
  </div>

  <div class="content" style="padding-top:4vh;">
    <div class="kicker" data-anim>OUR TEAM</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">核心团队成员</h2>

    <div class="grid" style="grid-template-columns:repeat(4,1fr);gap:2vw;">
      <!-- 成员1 -->
      <div class="pillar" data-anim style="text-align:center;padding:2vh;background:var(--bg-secondary);border-radius:12px;">
        <div class="frame-img h-18" style="border-radius:50%;overflow:hidden;margin:0 auto 2vh;width:8vw;">
          <img src="/assets/avatar-1.png" alt="张明" style="object-fit:cover;">
        </div>
        <h4 class="h4-zh">张明</h4>
        <p class="meta" style="color:var(--accent);margin:0.5vh 0;">首席执行官</p>
        <p class="body-zh" style="color:var(--gray-4);font-size:0.9vw;">15年行业经验</p>
      </div>

      <!-- 成员2 -->
      <div class="pillar" data-anim style="text-align:center;padding:2vh;background:var(--bg-secondary);border-radius:12px;">
        <div class="frame-img h-18" style="border-radius:50%;overflow:hidden;margin:0 auto 2vh;width:8vw;">
          <img src="/assets/avatar-2.png" alt="李华" style="object-fit:cover;">
        </div>
        <h4 class="h4-zh">李华</h4>
        <p class="meta" style="color:var(--accent);margin:0.5vh 0;">技术总监</p>
        <p class="body-zh" style="color:var(--gray-4);font-size:0.9vw;">前BAT技术专家</p>
      </div>

      <!-- 成员3 -->
      <div class="pillar" data-anim style="text-align:center;padding:2vh;background:var(--bg-secondary);border-radius:12px;">
        <div class="frame-img h-18" style="border-radius:50%;overflow:hidden;margin:0 auto 2vh;width:8vw;">
          <img src="/assets/avatar-3.png" alt="王芳" style="object-fit:cover;">
        </div>
        <h4 class="h4-zh">王芳</h4>
        <p class="meta" style="color:var(--accent);margin:0.5vh 0;">产品总监</p>
        <p class="body-zh" style="color:var(--gray-4);font-size:0.9vw;">资深产品专家</p>
      </div>

      <!-- 成员4 -->
      <div class="pillar" data-anim style="text-align:center;padding:2vh;background:var(--bg-secondary);border-radius:12px;">
        <div class="frame-img h-18" style="border-radius:50%;overflow:hidden;margin:0 auto 2vh;width:8vw;">
          <img src="/assets/avatar-4.png" alt="刘强" style="object-fit:cover;">
        </div>
        <h4 class="h4-zh">刘强</h4>
        <p class="meta" style="color:var(--accent);margin:0.5vh 0;">运营总监</p>
        <p class="body-zh" style="color:var(--gray-4);font-size:0.9vw;">连续创业者</p>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">02 / 15</div>
    <div class="center">关于我们</div>
    <div class="right">Team</div>
  </div>
</section>
```

---

### 布局17：价格方案

适用场景：产品定价、套餐选择、合作方案

特点：三方案并列，便于对比选择

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">合作方案</div>
    <div class="center"></div>
    <div class="right">08</div>
  </div>

  <div class="content" style="padding-top:4vh;">
    <div class="kicker" data-anim>PRICING PLANS</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">选择适合您的方案</h2>

    <div class="grid-3" style="grid-template-columns:repeat(3,1fr);gap:2vw;">
      <!-- 基础版 -->
      <div class="pillar" data-anim style="padding:3vh 2vw;background:var(--bg-secondary);border-radius:12px;text-align:center;">
        <div class="kicker" style="color:var(--gray-4);">基础版</div>
        <h3 class="h3-zh" style="margin:1vh 0;">¥9,800<span style="font-size:1vw;color:var(--gray-4);">/年</span></h3>
        <p class="body-zh" style="color:var(--gray-4);margin-bottom:2vh;">适合初创企业</p>
        <div style="border-top:1px solid var(--gray-6);padding-top:2vh;">
          <p class="body-zh" style="margin-bottom:1vh;">✓ 5个API调用权限</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 100GB存储空间</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 基础技术支持</p>
          <p class="body-zh" style="color:var(--gray-5);">✗ 高级分析功能</p>
        </div>
      </div>

      <!-- 专业版（推荐） -->
      <div class="pillar" data-anim style="padding:3vh 2vw;background:var(--accent);border-radius:12px;text-align:center;color:var(--bg);">
        <div class="kicker" style="color:var(--accent-light);">推荐方案</div>
        <h3 class="h3-zh" style="margin:1vh 0;color:var(--bg);">¥29,800<span style="font-size:1vw;">/年</span></h3>
        <p class="body-zh" style="color:var(--accent-light);margin-bottom:2vh;">适合成长型企业</p>
        <div style="border-top:1px solid var(--accent-light);padding-top:2vh;">
          <p class="body-zh" style="margin-bottom:1vh;">✓ 无限API调用</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 1TB存储空间</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 7×24技术支持</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 高级分析功能</p>
        </div>
      </div>

      <!-- 企业版 -->
      <div class="pillar" data-anim style="padding:3vh 2vw;background:var(--bg-secondary);border-radius:12px;text-align:center;">
        <div class="kicker" style="color:var(--gray-4);">企业版</div>
        <h3 class="h3-zh" style="margin:1vh 0;">¥99,800<span style="font-size:1vw;color:var(--gray-4);">/年</span></h3>
        <p class="body-zh" style="color:var(--gray-4);margin-bottom:2vh;">适合大型企业</p>
        <div style="border-top:1px solid var(--gray-6);padding-top:2vh;">
          <p class="body-zh" style="margin-bottom:1vh;">✓ 无限API调用</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 无限存储空间</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 专属客户经理</p>
          <p class="body-zh" style="margin-bottom:1vh;">✓ 私有化部署</p>
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">08 / 15</div>
    <div class="center">合作方案</div>
    <div class="right">Pricing</div>
  </div>
</section>
```

---

### 布局18：全屏图片背景

适用场景：产品展示、场景展示、视觉冲击

特点：全屏图片作为背景，文字叠加其上

```html
<section class="slide hero" data-theme="dark" style="position:relative;overflow:hidden;">
  <!-- 全屏背景图片 -->
  <div style="position:absolute;top:0;left:0;right:0;bottom:0;z-index:0;">
    <img src="/assets/hero-bg.jpg" alt="" style="width:100%;height:100%;object-fit:cover;opacity:0.6;">
  </div>

  <div class="chrome" style="position:relative;z-index:2;">
    <div class="left"></div>
    <div class="center"></div>
    <div class="right">01</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;text-align:center;position:relative;z-index:2;">
    <div class="kicker" data-anim style="color:var(--accent-light);">VISION 2025</div>
    <h1 class="display-zh" data-anim style="margin:2vh 0;color:var(--bg);">
      用科技连接<br>美好生活
    </h1>
    <p class="lead" data-anim style="max-width:50vw;color:var(--gray-2);">
      专注于人工智能与大数据技术创新，为企业数字化转型提供领先解决方案
    </p>
    <div class="meta" data-anim style="margin-top:4vh;">
      公司愿景 ｜ 使命宣言
    </div>
  </div>

  <div class="foot" style="position:relative;z-index:2;">
    <div class="left">01 / 10</div>
    <div class="center"></div>
    <div class="right">Vision</div>
  </div>
</section>
```

---

## 布局使用注意事项

### 1. 布局可以组合使用

复杂的页面可以组合多个布局。例如，左侧文字说明 + 右侧多个数据卡片，可以结合布局3和布局4。

### 2. 布局可以灵活调整

所有布局只是骨架，可以根据内容调整：

- 增加或减少元素
- 调整列数和比例
- 修改文字大小和颜色
- 增删边框和背景

### 3. 注意页面节奏

连续使用同类型布局会显得单调。建议：

- 数据页后接文字说明页
- 流程页后接案例展示页
- 大引用页作为观点转折点

### 4. 响应式考虑

布局默认针对PC端优化。如需移动端适配，需要：

- 将2列布局改为单列
- 缩小字号和间距
- 调整图片尺寸

### 5. 新布局使用场景

| 布局编号 | 布局名称 | 新增场景 |
|----------|----------|----------|
| 布局13 | 代码展示 | 技术分享、API文档 |
| 布局14 | 数据仪表盘 | 运营报告、实时监控 |
| 布局15 | FAQ问答 | 问题解答、知识培训 |
| 布局16 | 团队介绍 | 公司介绍、项目团队 |
| 布局17 | 价格方案 | 产品定价、合作方案 |
| 布局18 | 全屏图片 | 产品展示、品牌形象 |

---

## 麦肯锡风格专用布局

以下布局专门为麦肯锡风格的咨询汇报设计，强调**结论先行、数据驱动、简洁克制**。

### 布局M1：执行摘要（结论并列）

适用场景：执行摘要页、核心发现页、关键建议页

特点：3-4个核心结论并列展示，每个结论配编号和左侧色条标识

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">执行摘要</div>
    <div class="center"></div>
    <div class="right">02</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;height:100%;padding:0 10vw;">
    <div class="kicker" data-anim>EXECUTIVE SUMMARY</div>
    <h2 class="h2-zh" data-anim style="margin:2vh 0 4vh;">核心发现与建议</h2>

    <!-- 结论1 - 使用accent色 -->
    <div class="rowline" data-anim style="border-left:4px solid var(--accent);padding-left:2vw;margin-bottom:3vh;">
      <div class="k" style="color:var(--accent);font-size:3vw;">01</div>
      <div class="v" style="font-size:1.6vw;font-weight:600;">
        系统孤岛制约数字化转型，系统集成率仅35%
      </div>
    </div>

    <!-- 结论2 - 使用info色 -->
    <div class="rowline" data-anim style="border-left:4px solid var(--info);padding-left:2vw;margin-bottom:3vh;">
      <div class="k" style="color:var(--info);font-size:3vw;">02</div>
      <div class="v" style="font-size:1.6vw;font-weight:600;">
        数据决策能力不足，报表生成周期长达14天
      </div>
    </div>

    <!-- 结论3 - 使用success色 -->
    <div class="rowline" data-anim style="border-left:4px solid var(--success);padding-left:2vw;margin-bottom:3vh;">
      <div class="k" style="color:var(--success);font-size:3vw;">03</div>
      <div class="v" style="font-size:1.6vw;font-weight:600;">
        建议投入1200万进行数据中台建设，预期ROI 280%
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">02 / 15</div>
    <div class="center">企业数字化转型咨询</div>
    <div class="right">Summary</div>
  </div>
</section>
```

**麦肯锡要点**：
- 结论用动宾短语，直接表明观点
- 编号用大号数字，视觉醒目
- 左侧色条区分不同结论
- 不需要解释性文字，结论本身就是内容

---

### 布局M2：问题诊断（标题即结论）

适用场景：问题分析、根因诊断、痛点揭示

特点：**标题就是核心结论**，下方用数据和证据支撑

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">问题诊断 · 问题一</div>
    <div class="center"></div>
    <div class="right">04</div>
  </div>

  <div class="content" style="display:grid;grid-template-columns:1fr 1fr;gap:4vw;height:100%;align-items:center;">
    <div data-anim="left">
      <!-- 核心观点（标题即结论） -->
      <div class="kicker" style="color:var(--accent);">KEY FINDING</div>
      <h2 class="h2-zh" style="color:var(--accent);">系统孤岛制约业务协同</h2>

      <!-- 关键数据（一眼看到） -->
      <div style="margin:3vh 0;padding:2vh;background:var(--accent-light);border-radius:12px;">
        <div style="font-size:4vw;font-weight:700;color:var(--accent);">35%</div>
        <div style="font-size:1vw;color:var(--gray-3);">系统集成率（目标85%）</div>
      </div>

      <!-- 影响分析 -->
      <div style="padding:2vh;background:var(--bg-secondary);border-radius:8px;">
        <div style="font-family:var(--font-mono);color:var(--accent);margin-bottom:1vh;font-size:0.8vw;">IMPACT</div>
        <ul style="list-style:none;padding:0;">
          <li style="margin-bottom:1vh;font-size:1vw;">✗ 数据录入重复率 <strong>68%</strong></li>
          <li style="margin-bottom:1vh;font-size:1vw;">✗ 跨部门审批平均耗时 <strong>3.5天</strong></li>
          <li style="font-size:1vw;">✗ 年均人力浪费约 <strong>200人天</strong></li>
        </ul>
      </div>
    </div>

    <div data-anim="right">
      <!-- 数据图表支撑 -->
      <div class="chart-container">
        <div style="font-size:0.9vw;color:var(--gray-4);margin-bottom:2vh;">各系统集成现状</div>
        <div style="display:flex;align-items:flex-end;height:20vh;gap:2vw;">
          <div style="flex:1;text-align:center;">
            <div style="height:35%;background:var(--accent);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.85vw;margin-top:0.5vh;">ERP</div>
            <div style="font-size:0.75vw;color:var(--gray-4);">35%</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:60%;background:var(--info);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.85vw;margin-top:0.5vh;">CRM</div>
            <div style="font-size:0.75vw;color:var(--gray-4);">60%</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:45%;background:var(--success);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.85vw;margin-top:0.5vh;">SCM</div>
            <div style="font-size:0.75vw;color:var(--gray-4);">45%</div>
          </div>
        </div>
        <div style="font-size:0.65vw;color:var(--gray-4);text-align:right;margin-top:1vh;">
          数据来源：IT部门调研 2024.12
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">04 / 15</div>
    <div class="center">问题诊断</div>
    <div class="right">Finding 01</div>
  </div>
</section>
```

**麦肯锡要点**：
- 标题必须是完整的结论句子
- 关键数据用大字号突出显示
- 影响分析用"✗"符号强调负面
- 数据来源必须标注

---

### 布局M3：解决方案（一句话方案）

适用场景：方案概述、核心建议、核心思路

特点：**全页聚焦一个核心观点**，用一句话说明方案精髓

```html
<section class="slide hero" data-theme="dark">
  <div class="chrome">
    <div class="left">解决方案</div>
    <div class="center"></div>
    <div class="right">08</div>
  </div>

  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;text-align:center;">
    <div class="kicker" data-anim>OUR RECOMMENDATION</div>

    <!-- 一句话核心方案（大字） -->
    <h1 class="display-zh" data-anim style="max-width:75vw;margin:3vh 0;line-height:1.3;">
      构建统一数据中台<br>打通系统壁垒，实现数据贯通
    </h1>

    <!-- 三大价值指标 -->
    <div data-anim style="display:flex;gap:6vw;max-width:80vw;margin-top:5vh;">
      <div style="text-align:center;">
        <div style="font-size:3.5vw;font-weight:700;color:var(--accent);">85%</div>
        <div style="font-size:1.1vw;color:var(--gray-3);margin-top:1vh;">系统集成率</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:3.5vw;font-weight:700;color:var(--info);">3天→4小时</div>
        <div style="font-size:1.1vw;color:var(--gray-3);margin-top:1vh;">数据获取效率</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:3.5vw;font-weight:700;color:var(--success);">280%</div>
        <div style="font-size:1.1vw;color:var(--gray-3);margin-top:1vh;">预期ROI</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">08 / 15</div>
    <div class="center">解决方案</div>
    <div class="right">Solution</div>
  </div>
</section>
```

**麦肯锡要点**：
- 核心方案用最大字号，视觉冲击力强
- 3个关键指标支撑方案价值
- 不要在方案页堆砌细节
- 简洁到极致

---

### 布局M4：ROI分析（投资回报）

适用场景：投资分析、预算汇报、成本效益

特点：左右分栏，左侧核心数据，右侧图表

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">投资回报分析</div>
    <div class="center"></div>
    <div class="right">13</div>
  </div>

  <div class="content" style="display:grid;grid-template-columns:1fr 1.2fr;gap:4vw;height:100%;align-items:center;">
    <div data-anim="left">
      <div class="kicker">RETURN ON INVESTMENT</div>
      <h2 class="h2-zh" style="margin:2vh 0;">投资回报分析</h2>

      <!-- 核心数据卡片 -->
      <div style="background:var(--accent-light);padding:3vh;border-radius:12px;margin-top:3vh;">
        <div style="display:flex;justify-content:space-between;margin-bottom:2vh;">
          <div>
            <div style="font-size:0.8vw;color:var(--gray-4);">总投资额</div>
            <div style="font-size:2vw;font-weight:700;">1,200万</div>
          </div>
          <div>
            <div style="font-size:0.8vw;color:var(--gray-4);">预期收益</div>
            <div style="font-size:2vw;font-weight:700;color:var(--success);">3,360万</div>
          </div>
          <div>
            <div style="font-size:0.8vw;color:var(--gray-4);">ROI</div>
            <div style="font-size:2vw;font-weight:700;color:var(--accent);">280%</div>
          </div>
        </div>
        <div style="font-size:0.9vw;color:var(--gray-3);">
          投资回收期：<strong>14个月</strong><br>
          3年累计净收益：<strong>2,160万</strong>
        </div>
      </div>
    </div>

    <div data-anim="right">
      <!-- 柱状图 -->
      <div class="chart-container">
        <div style="font-size:0.9vw;color:var(--gray-4);margin-bottom:2vh;">年度收益预测（万元）</div>
        <div style="display:flex;align-items:flex-end;height:22vh;gap:3vw;padding-top:2vh;">
          <div style="flex:1;text-align:center;">
            <div style="height:30%;background:var(--accent);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.85vw;margin-top:0.5vh;">第一年</div>
            <div style="font-size:0.75vw;color:var(--gray-4);">960</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:70%;background:var(--accent);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.85vw;margin-top:0.5vh;">第二年</div>
            <div style="font-size:0.75vw;color:var(--gray-4);">1,200</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:100%;background:var(--accent);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.85vw;margin-top:0.5vh;">第三年</div>
            <div style="font-size:0.75vw;color:var(--gray-4);">1,200</div>
          </div>
        </div>
        <div style="font-size:0.65vw;color:var(--gray-4);text-align:right;">
          数据来源：财务部测算 2024.12
        </div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">13 / 15</div>
    <div class="center">投资回报分析</div>
    <div class="right">ROI</div>
  </div>
</section>
```

**麦肯锡要点**：
- 关键数字要醒目（大字号、加粗、强调色）
- 图表必须标注数据来源
- 一图一结论，不要混合信息
- ROI页是决策的关键，数据必须准确

---

### 布局M5：行动计划（任务清单）

适用场景：下一步计划、行动方案、任务分解

特点：清晰的行动项列表，配合责任和时间

```html
<section class="slide" data-theme="light">
  <div class="chrome">
    <div class="left">行动计划</div>
    <div class="center"></div>
    <div class="right">14</div>
  </div>

  <div class="content" style="padding-top:4vh;">
    <div class="kicker" data-anim>NEXT STEPS</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">建议下一步行动</h2>

    <div style="display:flex;flex-direction:column;gap:2vh;">
      <!-- 行动项1 -->
      <div class="pillar" data-anim style="display:flex;align-items:center;padding:2vh 2vw;background:var(--accent-light);border-left:4px solid var(--accent);border-radius:0 8px 8px 0;">
        <div style="width:3vw;height:3vw;background:var(--accent);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;margin-right:2vw;">1</div>
        <div style="flex:1;">
          <div style="font-size:1.3vw;font-weight:600;color:var(--fg);">组建项目筹备小组</div>
          <div style="font-size:0.9vw;color:var(--gray-4);">明确负责人及核心成员</div>
        </div>
        <div style="font-family:var(--font-mono);font-size:0.8vw;color:var(--gray-4);">1月内</div>
      </div>

      <!-- 行动项2 -->
      <div class="pillar" data-anim style="display:flex;align-items:center;padding:2vh 2vw;background:var(--bg-secondary);border-left:4px solid var(--info);border-radius:0 8px 8px 0;">
        <div style="width:3vw;height:3vw;background:var(--info);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;margin-right:2vw;">2</div>
        <div style="flex:1;">
          <div style="font-size:1.3vw;font-weight:600;color:var(--fg);">完成技术方案细化</div>
          <div style="font-size:0.9vw;color:var(--gray-4);">IT部门主导，3周内提交</div>
        </div>
        <div style="font-family:var(--font-mono);font-size:0.8vw;color:var(--gray-4);">2月内</div>
      </div>

      <!-- 行动项3 -->
      <div class="pillar" data-anim style="display:flex;align-items:center;padding:2vh 2vw;background:var(--bg-secondary);border-left:4px solid var(--success);border-radius:0 8px 8px 0;">
        <div style="width:3vw;height:3vw;background:var(--success);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;margin-right:2vw;">3</div>
        <div style="flex:1;">
          <div style="font-size:1.3vw;font-weight:600;color:var(--fg);">启动供应商入围</div>
          <div style="font-size:0.9vw;color:var(--gray-4);">采购部门组织技术评审</div>
        </div>
        <div style="font-family:var(--font-mono);font-size:0.8vw;color:var(--gray-4);">3月内</div>
      </div>

      <!-- 行动项4 -->
      <div class="pillar" data-anim style="display:flex;align-items:center;padding:2vh 2vw;background:var(--bg-secondary);border-left:4px solid var(--warning);border-radius:0 8px 8px 0;">
        <div style="width:3vw;height:3vw;background:var(--warning);border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;margin-right:2vw;">4</div>
        <div style="flex:1;">
          <div style="font-size:1.3vw;font-weight:600;color:var(--fg);">项目立项审批</div>
          <div style="font-size:0.9vw;color:var(--gray-4);">提交管理层审批</div>
        </div>
        <div style="font-family:var(--font-mono);font-size:0.8vw;color:var(--gray-4);">4月内</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="left">14 / 15</div>
    <div class="center">行动计划</div>
    <div class="right">Action</div>
  </div>
</section>
```

**麦肯锡要点**：
- 每项行动清晰、具体、可执行
- 配合时间节点，增加紧迫感
- 编号用圆形色块，视觉统一
- 第一个行动项用强调色突出

---

## 麦肯锡布局使用指南

| 麦肯锡场景 | 推荐布局 | 关键要点 |
|-----------|----------|----------|
| 执行摘要 | 布局M1 | 3-4个核心结论并列 |
| 问题诊断 | 布局M2 | 标题即结论，数据支撑 |
| 方案概述 | 布局M3 | 一句话方案，简洁有力 |
| 投资回报 | 布局M4 | 数据醒目，图表清晰 |
| 行动计划 | 布局M5 | 任务具体，时间明确 |