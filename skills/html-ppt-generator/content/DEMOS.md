---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100c7cfab36ce0c8e6a9dc147d2ee5a157d1627247b16d057cd40dd103d5fb0276e022050e7a0e5bef391bf97239edf94ab48a426e03d6f8ac8d4a0fa69090e5f1c018c
    ReservedCode2: 3046022100bad8664d987fd9f3dbf6b9b1b4604821b2d3bb6cd39065992bd84a6a15094c5e022100def381c29a5dd396efff8a080ff01d1f5f64e2e0b0c49636f682694ebc956125
---

# HTML PPT Generator - 完整案例演示

> 本文档提供7大场景类型的完整PPT示例，可直接复制使用或作为参考模板。

## 目录

1. [需求收集示例](#0-需求收集示例)
2. [政务信息化汇报完整示例](#1-政务信息化汇报完整示例)
3. [商务业绩汇报完整示例](#2-商务业绩汇报完整示例)
4. [产品发布会完整示例](#3-产品发布会完整示例)
5. [教育培训课程完整示例](#4-教育培训课程完整示例)
6. [数据分析报告完整示例](#5-数据分析报告完整示例)
7. [个人简历展示完整示例](#6-个人简历展示完整示例)
8. [评审汇报完整示例](#7-评审汇报完整示例)

---

## 0. 需求收集示例

> 以下展示AI在实际应用时如何收集需求、确认关键信息。

### 场景：用户提出初步需求

```
用户：请帮我做一个关于"企业数据中台建设"的PPT
```

### AI的确认流程

```
【第一步：确认关键信息】

AI：好的，我来帮您制作这个PPT。为了确保生成结果符合实际需求，请提供以下关键信息：

📋 汇报场景
  • 目标：揭示问题 / 展示方案 / 申请预算 / 汇报进度？
  • 时长：约几分钟？

👥 听众分析
  • 受众：一把手 / 分管领导 / 执行层 / 外部客户？
  • 他们最关心什么问题？

📝 内容核心
  • 核心主题：数据中台建设的什么方面？（方案/现状/规划）
  • 关键数据：有哪些数据可以支撑？（如：当前数据孤岛率、预期整合效率）
  • 素材情况：有没有现成的需求文档、架构图、数据报表？

🎨 设计偏好
  • 风格：商务麦肯锡 / 科技前沿 / 政务庄重？
  • 页数限制：有没有具体页数要求？

请提供以上信息，我将为您生成专业的PPT。
```

### 确认后的回复示例

```
用户回复：
- 目标：申请数据中台建设预算
- 时长：15分钟
- 受众：CTO和财务总监
- 核心主题：数据中台建设可行性分析
- 关键数据：当前数据孤岛率68%，预期整合后效率提升40%
- 风格：商务麦肯锡风格
- 页数：约12页

AI：收到！根据您的需求，我将制作一个商务麦肯锡风格的可行性分析PPT：
- 受众：CTO + CFO（关注ROI和实施路径）
- 页数：约12页
- 叙事结构：问题-解决方案（痛点→方案→ROI→行动）

现在开始为您生成...
```

### 麦肯锡风格专项确认

当用户选择麦肯锡风格时，AI应额外追问：

```
【麦肯锡风格专项确认】

1. 核心结论
   "您希望听众听完汇报后，记住哪3个核心观点？"
   例如：① 数据孤岛制约业务发展 ② 数据中台是最佳解决方案 ③ 投资回报可观

2. 数据来源
   "关键数据是否有权威来源？"
   例如：内部IT调研报告 / 第三方咨询报告 / 行业benchmark

3. 决策人
   "汇报结束后，听众需要做出什么决定？"
   例如：批准预算 / 立项 / 继续调研

4. 风险敏感度
   "听众对风险的接受程度如何？"
   例如：激进型（愿意冒险） / 稳健型（需要充分论证） / 保守型（需要详细风险对策）
```

### 需求确认检查点

生成前，AI必须确认：

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 受众已明确 | ✅/❓ | 知道是谁、关心什么 |
| 时长已确认 | ✅/❓ | 决定页数（5分钟≈5页，15分钟≈15页） |
| 核心信息已收集 | ✅/❓ | 主题、数据、素材 |
| 风格已选定 | ✅/❓ | 7套主题色选1套 |
| 硬约束已记录 | ✅/❓ | 页数限制、必须包含/排除 |

> **重要**：如果某项为❓，AI应主动追问后再开始生成。

### 需求不完整时的追问示例

#### 场景一：用户只说"做PPT"

```
用户：请帮我做一个关于数据中台建设的PPT

AI：请提供以下关键信息，以便生成符合需求的PPT：

必须确认：
  1. 汇报场景
     • 目标：揭示问题 / 展示方案 / 申请预算 / 汇报进度？
     • 时长：约几分钟？

  2. 听众分析
     • 受众：一把手 / 分管领导 / 执行层 / 外部客户？
     • 他们最关心什么问题？

可选确认：
  3. 风格：商务麦肯锡 / 科技前沿 / 政务庄重？
  4. 数据：有哪些具体数据可以支撑？

请提供以上信息，我将为您生成专业的PPT。
```

#### 场景二：用户说"做一个20分钟的汇报"

```
用户：我要做一个20分钟的汇报

AI：好的，20分钟约需15-18页。

还需确认：

  ✓ 时长：20分钟（已确认）
  ❓ 受众：主要是给谁看的？（一把手/分管领导/执行层）
  ❓ 主题：汇报什么内容？（工作进展/项目方案/业绩总结）
  ❓ 风格：倾向哪种视觉风格？

请补充以上信息。
```

#### 场景三：用户只说"做麦肯锡风格的PPT"

```
用户：请做一个麦肯锡风格的汇报

AI：好的，麦肯锡风格已确认。

还需确认：

  ✓ 风格：麦肯锡商务（已确认）
  ❓ 受众：主要是给谁看的？
  ❓ 时长：约多长时间？
  ❓ 主题：汇报什么核心内容？

请补充关键信息，我将开始生成。
```

#### 场景四：用户提供的信息完整

```
用户：我要做一个15分钟的汇报，向CTO展示数据中台建设方案，
      目的是申请预算，有系统集成率35%等数据，风格用麦肯锡。

AI：收到！已确认：
  ✓ 受众：CTO（技术决策层，关注ROI和可行性）
  ✓ 时长：15分钟（约12-15页）
  ✓ 主题：数据中台建设方案（申请预算）
  ✓ 数据：系统集成率35%等
  ✓ 风格：麦肯锡商务

开始为您生成PPT...
```

---

### 分步追问流程图

```
用户请求
    │
    ├── 信息完整？ ──是──→ 开始生成
    │
    └── 信息不完整？
            │
            ├── 缺少受众 ──追问1──→ 用户回复？
            │                     │
            ├── 缺少时长 ──追问2──→ 用户回复？
            │                     │
            └── 缺少主题 ──追问3──→ 用户回复？
                                      │
                                      ↓
                              3项核心信息已齐？
                                    │
                           ┌────────┴────────┐
                           ↓                 ↓
                         是                否
                           ↓                 ↓
                       开始生成          继续追问
                                        (最多3轮)
```

---

### 追问底线检查

> AI必须在收到以下3项信息后才能开始生成：
> 1. ✅ 受众（至少知道是一把手/分管领导/执行层）
> 2. ✅ 时长（至少知道是5分钟/15分钟/30分钟）
> 3. ✅ 核心主题（至少知道要做什么主题）
>
> **缺少任意一项，必须追问，不得跳过。**

---

## 1. 政务信息化汇报完整示例

### 场景设定

```
主题：智慧城市建设成果汇报
受众：市领导、评审专家
时长：15分钟，约12页
主题色：政务科技
架构图：五横三纵总体架构
```

### 页面清单

| 页码 | 布局类型 | 内容 |
|------|----------|------|
| 01 | Hero全屏封面 | 项目名称、口号、汇报人信息 |
| 02 | 目录 | 六大章节导航 |
| 03 | 章节幕封 | 第一章：建设背景与目标 |
| 04 | 左文右图 | 政策背景 + 架构示意图 |
| 05 | 章节幕封 | 第二章：总体架构 |
| 06 | 架构图 | 五横三纵总体架构图 |
| 07 | 章节幕封 | 第三章：建设成果 |
| 08 | Stat数字大字报 | 核心成效数据（4-6个指标） |
| 09 | 图表组件 | 柱状图/环形图展示详情数据 |
| 10 | 章节幕封 | 第四章：问题与计划 |
| 11 | 问题与建议 | 挑战 + 对策 |
| 12 | 结束致谢 | 联系方式、致谢 |

### 关键代码片段

**封面页（Page 01）**：
```html
<section class="slide hero" data-theme="dark" data-animate="hero">
  <div class="chrome">
    <div class="left">智慧城市建设项目</div>
    <div class="center"></div>
    <div class="right">01</div>
  </div>
  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;text-align:center;">
    <div class="kicker" data-anim>2024年度成果汇报</div>
    <h1 class="display-zh" data-anim style="margin:2vh 0;">
      智慧城市建设<br>成果汇报
    </h1>
    <p class="lead" data-anim style="color:var(--gray-3);max-width:60vw;">
      数字化转型引领城市治理现代化
    </p>
    <div class="meta" data-anim style="margin-top:4vh;">
      汇报人：张三 ｜ 汇报日期：2024年12月
    </div>
  </div>
  <div class="foot">
    <div class="left">01 / 12</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">Cover</div>
  </div>
</section>
```

**数据成效页（Page 08）**：
```html
<section class="slide" data-theme="dark">
  <div class="chrome">
    <div class="left">第三章 · 建设成果</div>
    <div class="center"></div>
    <div class="right">08</div>
  </div>
  <div class="content" style="display:flex;flex-direction:column;justify-content:center;height:100%;">
    <div class="kicker" data-anim style="margin-bottom:2vh;">KEY ACHIEVEMENTS</div>
    <h2 class="h2-zh" data-anim style="margin-bottom:4vh;">核心建设成果</h2>
    <div class="grid" style="grid-template-columns:repeat(4,1fr);gap:2vw;">
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">平台接入量</div>
        <div class="n">2,847 <small>万</small></div>
        <div class="l">同比提升 156%</div>
      </div>
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">办件效率提升</div>
        <div class="n">68<span style="font-size:0.4em;">%</span></div>
        <div class="l">平均办理时限缩短</div>
      </div>
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">用户满意度</div>
        <div class="n">96.8<span style="font-size:0.4em;">%</span></div>
        <div class="l">服务好评率</div>
      </div>
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">数据共享率</div>
        <div class="n">92<span style="font-size:0.4em;">%</span></div>
        <div class="l">部门数据互通</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div class="left">08 / 12</div>
    <div class="center">智慧城市建设项目组</div>
    <div class="right">03 · Results</div>
  </div>
</section>
```

---

## 2. 商务业绩汇报完整示例

### 场景设定

```
主题：2024年度销售业绩汇报
受众：销售总监、公司管理层
时长：20分钟，约15页
主题色：墨水经典
```

### 页面清单

| 页码 | 布局类型 | 内容 |
|------|----------|------|
| 01 | Hero全屏封面 | 年度、销售、部门名称 |
| 02 | 目录 | 五大章节导航 |
| 03 | Stat数字大字报 | 年度核心业绩指标 |
| 04 | 图表组件 | 季度业绩柱状图 |
| 05 | Grid网格 | 区域业绩排名 |
| 06 | 章节幕封 | 区域表现分析 |
| 07 | Before/After对比 | 区域A：转型前后对比 |
| 08 | 左文右图 | 区域B：成功案例 |
| 09 | 章节幕封 | 重点客户分析 |
| 10 | Rowline表格行 | Top5客户详情 |
| 11 | 章节幕封 | 问题与对策 |
| 12 | 问题与建议 | 三大挑战 + 解决方案 |
| 13 | Pipeline流程 | 下季度目标分解 |
| 14 | 章节幕封 | 总结与展望 |
| 15 | 结束致谢 | 联系方式 |

### 关键代码片段

**年度业绩总览（Page 03）**：
```html
<section class="slide" data-theme="dark">
  <div class="chrome">
    <div class="left">2024年度业绩总览</div>
    <div class="center"></div>
    <div class="right">03</div>
  </div>
  <div class="content" style="display:flex;flex-direction:column;justify-content:center;height:100%;">
    <div class="kicker" data-anim>ANNUAL PERFORMANCE OVERVIEW</div>
    <h2 class="h2-zh" data-anim style="margin:1vh 0 4vh;">年度核心业绩指标</h2>
    <div class="grid" style="grid-template-columns:repeat(3,1fr);gap:3vw;">
      <div class="stat-card" data-anim style="text-align:center;border:2px solid var(--accent);padding:2vh;">
        <div class="m">全年销售额</div>
        <div class="n" style="color:var(--accent);">8,520 <small>万</small></div>
        <div class="l">目标完成率 106.5%</div>
      </div>
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">新增客户数</div>
        <div class="n">1,286 <small>家</small></div>
        <div class="l">同比增长 23.8%</div>
      </div>
      <div class="stat-card" data-anim style="text-align:center;">
        <div class="m">客户续约率</div>
        <div class="n">94.2<span style="font-size:0.4em;">%</span></div>
        <div class="l">历史最佳水平</div>
      </div>
    </div>
    <div class="mini-chart-grid" data-anim style="margin-top:4vh;">
      <div class="mini-chart-card">
        <div class="mini-chart-label">毛利润</div>
        <div class="mini-chart-value">3,180万</div>
        <div class="mini-chart-trend up">↑ 18.5%</div>
      </div>
      <div class="mini-chart-card">
        <div class="mini-chart-label">净利润</div>
        <div class="mini-chart-value">2,560万</div>
        <div class="mini-chart-trend up">↑ 21.2%</div>
      </div>
      <div class="mini-chart-card">
        <div class="mini-chart-label">回款率</div>
        <div class="mini-chart-value">97.3%</div>
        <div class="mini-chart-trend up">↑ 3.1%</div>
      </div>
    </div>
  </div>
  <div class="foot">
    <div class="left">03 / 15</div>
    <div class="center">2024年度销售业绩汇报</div>
    <div class="right">Overview</div>
  </div>
</section>
```

---

## 3. 产品发布会完整示例

### 场景设定

```
主题：智慧城市AI平台产品发布
受众：政府客户、企业客户、合作伙伴
时长：30分钟，约20页
主题色：科技未来
```

### 页面清单

| 页码 | 布局类型 | 内容 |
|------|----------|------|
| 01 | Hero全屏封面 | 产品名称、Slogan |
| 02 | 目录 | 六大章节 |
| 03 | 章节幕封 | 产品理念 |
| 04 | 大引用金句 | 核心价值主张 |
| 05 | 章节幕封 | 核心功能 |
| 06 | 三栏支柱 | 三大核心能力 |
| 07 | Grid网格 | 功能模块概览 |
| 08 | 左文右图 | 功能详解（示例） |
| 09 | 章节幕封 | 技术架构 |
| 10 | 架构图 | 整体技术架构 |
| 11 | 图表组件 | 性能指标数据 |
| 12 | 章节幕封 | 应用场景 |
| 13 | 图片网格 | 场景案例 |
| 14 | 时间轴 | 场景扩展路线 |
| 15 | 章节幕封 | 竞争优势 |
| 16 | 对比表格 | vs 竞品对比 |
| 17 | 章节幕封 | 成功案例 |
| 18 | 引用+数据 | 客户证言 |
| 19 | 章节幕封 | 合作方式 |
| 20 | 结束致谢 | 联系方式、演示预约 |

---

## 4. 教育培训课程完整示例

### 场景设定

```
主题：数据分析实战技能培训
受众：新入职员工、业务骨干
时长：45分钟，约25页
主题色：教育清新
```

### 页面清单

| 页码 | 布局类型 | 内容 |
|------|----------|------|
| 01 | Hero全屏封面 | 课程名称、讲师 |
| 02 | 章节幕封 | 课程介绍 |
| 03 | 三栏支柱 | 学习目标 |
| 04 | Grid网格 | 课程大纲 |
| 05 | 章节幕封 | 模块一：数据思维 |
| 06 | 左文右图 | 数据思维核心概念 |
| 07 | Pipeline流程 | 数据分析五步法 |
| 08 | 章节幕封 | 模块二：工具实战 |
| 09 | 三栏支柱 | Excel/Python/SQL三大工具 |
| 10 | Rowline表格行 | 工具对比表 |
| 11 | 左文右图 | Excel高级技巧 |
| 12 | 左文右图 | Python数据处理 |
| 13 | 章节幕封 | 模块三：可视化 |
| 14 | Grid网格 | 图表类型选择 |
| 15 | 图表组件 | 实战案例演示 |
| 16 | 章节幕封 | 模块四：实战演练 |
| 17 | Pipeline流程 | 练习步骤 |
| 18 | 问题与建议 | 常见问题避坑 |
| 19 | 章节幕封 | 总结与资源 |
| 20 | Rowline表格行 | 知识点回顾 |
| 21 | Grid网格 | 学习资源推荐 |
| 22 | 结束致谢 | 联系方式、Q&A |

---

## 5. 数据分析报告完整示例

### 场景设定

```
主题：2024年Q3用户行为分析报告
受众：产品团队、运营团队、管理层
时长：30分钟，约20页
主题色：数据专业
```

### 页面清单

| 页码 | 布局类型 | 内容 |
|------|----------|------|
| 01 | Hero全屏封面 | 报告名称、分析周期 |
| 02 | 目录 | 分析框架 |
| 03 | 章节幕封 | 分析背景 |
| 04 | Stat数字大字报 | 关键数据概览 |
| 05 | 章节幕封 | 数据来源 |
| 06 | Rowline表格行 | 数据字典 |
| 07 | 章节幕封 | 核心发现 |
| 08 | 大引用金句 | 核心洞察 |
| 09 | Stat数字大字报 | 三大发现 |
| 10 | 章节幕封 | 用户画像 |
| 11 | Grid网格 | 用户群体分布 |
| 12 | 图表组件 | 行为数据详情 |
| 13 | 章节幕封 | 趋势分析 |
| 14 | 时间轴 | 季度趋势变化 |
| 15 | 图表组件 | 预测模型 |
| 16 | 章节幕封 | 建议行动 |
| 17 | Pipeline流程 | 行动计划 |
| 18 | 问题与建议 | 风险提示 |
| 19 | 附录 | 数据说明 |
| 20 | 结束致谢 | 联系方式 |

---

## 6. 个人简历展示完整示例

### 场景设定

```
主题：产品经理简历展示
受众：HR、面试官
时长：5分钟，约10页
主题色：创意艺术
```

### 页面清单

| 页码 | 布局类型 | 内容 |
|------|----------|------|
| 01 | Hero全屏封面 | 姓名、职位目标 |
| 02 | 章节幕封 | 关于我 |
| 03 | Stat数字大字报 | 工作成就数据 |
| 04 | 章节幕封 | 核心能力 |
| 05 | 三栏支柱 | 专业技能 |
| 06 | 章节幕封 | 工作经历 |
| 07 | 时间轴 | 职业历程 |
| 08 | 章节幕封 | 项目案例 |
| 09 | 图片网格 | 代表作品 |
| 10 | 结束致谢 | 联系方式 |

---

## 7. 评审汇报完整示例

### 场景设定

```
主题：城市大脑二期项目立项评审
受众：评审专家、领导
时长：30分钟，约25页
主题色：政务科技
架构图：五横三纵 + 数据架构
```

### 页面清单

| 页码 | 布局类型 | 内容 |
|------|----------|------|
| 01 | Hero全屏封面 | 项目名称、评审类型 |
| 02 | 目录 | 汇报提纲 |
| 03 | 章节幕封 | 项目概述 |
| 04 | Stat数字大字报 | 建设必要性数据 |
| 05 | 章节幕封 | 建设方案 |
| 06 | 架构图 | 五横三纵总体架构 |
| 07 | 架构图 | 数据架构 |
| 08 | Grid网格 | 技术选型 |
| 09 | 章节幕封 | 建设内容 |
| 10 | 左文右图 | 应用系统建设 |
| 11 | Pipeline流程 | 分阶段实施计划 |
| 12 | 时间轴 | 里程碑节点 |
| 13 | 章节幕封 | 投资预算 |
| 14 | Stat数字大字报 | 投资估算 |
| 15 | 表格行 | 预算明细 |
| 16 | 章节幕封 | 建设成效 |
| 17 | 图表组件 | 预期效果 |
| 18 | 图表组件 | 效益分析 |
| 19 | 章节幕封 | 风险与对策 |
| 20 | 问题与建议 | 风险识别+应对 |
| 21 | 章节幕封 | 结论与建议 |
| 22 | 大引用金句 | 核心结论 |
| 23 | 章节幕封 | 专家问答 |
| 24 | 结束致谢 | 致谢 |

---

## 8. 麦肯锡风格咨询汇报完整示例

### 场景设定

```
主题：企业数字化转型战略咨询汇报
受众：一把手/高管决策层
时长：20分钟，约15页
主题色：墨水经典（商务专业）
叙事结构：问题-解决方案
方法论：金字塔原理 + MECE
```

### 核心特征

麦肯锡风格PPT的核心特点：
- **结论先行**：每页标题即核心观点
- **数据驱动**：所有论点都有数据支撑
- **图表优先**：能用图表就不用文字
- **简洁克制**：删到不能再删
- **受众导向**：内容因受众而异

### 麦肯锡PPT页面结构

```
第1页：封面（项目名称 + 核心价值主张）
第2页：执行摘要（3-4个核心结论，1页概览）
第3页：问题诊断（3个核心问题，每个1页）
  ├─ 问题1：根因 → 证据 → 影响
  ├─ 问题2：根因 → 证据 → 影响
  └─ 问题3：根因 → 证据 → 影响
第9页：解决方案（整体方案概述）
第10-12页：实施路径（3个阶段）
第13页：投资回报（ROI分析）
第14页：行动计划（下一步）
第15页：结束/致谢
```

### 页面清单

| 页码 | 布局类型 | 麦肯锡要素 |
|------|----------|-----------|
| 01 | Hero全屏封面 | 核心价值主张（动宾短语） |
| 02 | Stat大字报 | 执行摘要（3-4个关键结论） |
| 03 | 章节幕封 | 问题诊断 |
| 04 | 左文右图 | 问题1：系统孤岛 → 集成率35% |
| 05 | 数据图表 | 问题2：决策滞后 → 报表周期14天 |
| 06 | 对比布局 | 问题3：效率低下 → 人工操作占比60% |
| 07 | 章节幕封 | 解决方案 |
| 08 | 全图标题 | 方案核心思路（一句话） |
| 09 | 架构图 | 目标架构蓝图 |
| 10 | 章节幕封 | 实施路径 |
| 11 | Pipeline流程 | 三阶段实施计划 |
| 12 | 时间轴 | 关键里程碑 |
| 13 | Stat大字报 | ROI分析（投入产出比） |
| 14 | 行动清单 | 下一步行动计划（5项） |
| 15 | 结束致谢 | 联系方式 |

### 关键代码片段

**执行摘要页（Page 02）**：
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

    <!-- 结论1 -->
    <div class="rowline" data-anim style="border-left:4px solid var(--accent);padding-left:2vw;margin-bottom:3vh;">
      <div class="k" style="color:var(--accent);font-size:3vw;">01</div>
      <div class="v" style="font-size:1.8vw;font-weight:600;">
        系统孤岛制约数字化转型，系统集成率仅35%
      </div>
    </div>

    <!-- 结论2 -->
    <div class="rowline" data-anim style="border-left:4px solid var(--info);padding-left:2vw;margin-bottom:3vh;">
      <div class="k" style="color:var(--info);font-size:3vw;">02</div>
      <div class="v" style="font-size:1.8vw;font-weight:600;">
        数据决策能力不足，报表生成周期长达14天
      </div>
    </div>

    <!-- 结论3 -->
    <div class="rowline" data-anim style="border-left:4px solid var(--success);padding-left:2vw;margin-bottom:3vh;">
      <div class="k" style="color:var(--success);font-size:3vw;">03</div>
      <div class="v" style="font-size:1.8vw;font-weight:600;">
        建议投入1200万进行数据中台建设，预期ROI 280%
      </div>
    </div>
  </div>
</section>
```

**问题诊断页（Page 04）- 标题即结论**：
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

      <p class="body-zh" style="font-size:1.4vw;color:var(--gray-2);margin:2vh 0;">
        当前系统集成率仅<span style="color:var(--accent);font-weight:700;">35%</span>，
        导致跨部门业务协同效率低下。
      </p>

      <div style="margin-top:3vh;padding:2vh;background:var(--accent-light);border-radius:8px;">
        <div style="font-family:var(--font-mono);color:var(--accent);margin-bottom:1vh;">影响分析</div>
        <ul style="list-style:none;">
          <li style="margin-bottom:1vh;">✗ 数据录入重复率 68%</li>
          <li style="margin-bottom:1vh;">✗ 跨部门审批平均耗时 3.5天</li>
          <li>✗ 年均人力浪费约 200人天</li>
        </ul>
      </div>
    </div>

    <div data-anim="right">
      <!-- 数据图表支撑 -->
      <div class="chart-container">
        <div class="chart-title">各系统集成现状</div>
        <div class="chart-bar" style="display:flex;align-items:flex-end;height:20vh;gap:2vw;padding-top:2vh;">
          <div style="flex:1;text-align:center;">
            <div style="height:35%;background:var(--accent);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.8vw;margin-top:0.5vh;">ERP</div>
            <div style="font-size:0.7vw;color:var(--gray-4);">35%</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:60%;background:var(--info);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.8vw;margin-top:0.5vh;">CRM</div>
            <div style="font-size:0.7vw;color:var(--gray-4);">60%</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:45%;background:var(--success);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.8vw;margin-top:0.5vh;">SCM</div>
            <div style="font-size:0.7vw;color:var(--gray-4);">45%</div>
          </div>
        </div>
        <div style="font-size:0.7vw;color:var(--gray-4);text-align:right;margin-top:1vh;">
          数据来源：IT部门调研 2024.12
        </div>
      </div>
    </div>
  </div>
</section>
```

**解决方案概述页（Page 08）- 一句话方案**：
```html
<section class="slide" data-theme="dark">
  <div class="chrome">
    <div class="left">解决方案</div>
    <div class="center"></div>
    <div class="right">08</div>
  </div>
  <div class="content" style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:100%;text-align:center;">
    <div class="kicker" data-anim>OUR RECOMMENDATION</div>

    <!-- 一句话核心方案 -->
    <h1 class="display-zh" data-anim style="max-width:70vw;margin:3vh 0;">
      构建统一数据中台<br>打通系统壁垒，实现数据贯通
    </h1>

    <!-- 三大价值 -->
    <div class="grid" data-anim style="grid-template-columns:repeat(3,1fr);gap:4vw;max-width:80vw;margin-top:4vh;">
      <div style="text-align:center;">
        <div style="font-size:3vw;color:var(--accent);font-weight:700;">85%</div>
        <div style="font-size:1.2vw;color:var(--gray-3);margin-top:1vh;">系统集成率提升</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:3vw;color:var(--info);font-weight:700;">3天→4小时</div>
        <div style="font-size:1.2vw;color:var(--gray-3);margin-top:1vh;">数据获取效率</div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:3vw;color:var(--success);font-weight:700;">280%</div>
        <div style="font-size:1.2vw;color:var(--gray-3);margin-top:1vh;">预期ROI</div>
      </div>
    </div>
  </div>
</section>
```

**ROI分析页（Page 13）**：
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

      <!-- 核心数据 -->
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
            <div style="font-size:0.8vw;color:var(--gray-4);">投资回报率</div>
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
      <!-- 收益分解图表 -->
      <div class="chart-container">
        <div class="chart-title">年度收益预测（万元）</div>
        <div style="height:25vh;display:flex;align-items:flex-end;gap:3vw;padding:2vh 0;">
          <div style="flex:1;text-align:center;">
            <div style="height:30%;background:var(--info);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.8vw;margin-top:0.5vh;">第一年</div>
            <div style="font-size:0.7vw;color:var(--gray-4);">960</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:70%;background:var(--info);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.8vw;margin-top:0.5vh;">第二年</div>
            <div style="font-size:0.7vw;color:var(--gray-4);">1,200</div>
          </div>
          <div style="flex:1;text-align:center;">
            <div style="height:100%;background:var(--info);border-radius:4px 4px 0 0;"></div>
            <div style="font-size:0.8vw;margin-top:0.5vh;">第三年</div>
            <div style="font-size:0.7vw;color:var(--gray-4);">1,200</div>
          </div>
        </div>
        <div style="font-size:0.7vw;color:var(--gray-4);text-align:right;">
          数据来源：财务部测算 2024.12
        </div>
      </div>
    </div>
  </div>
</section>
```

### 麦肯锡PPT设计要点

| 要点 | 具体要求 |
|------|----------|
| **标题即结论** | 标题用动宾短语，直接表明核心观点 |
| **数据必须标注** | 所有数据都要有来源和时间 |
| **删到极致** | 每页只讲一件事，删除所有冗余 |
| **图表说话** | 文字能换成图表的就不写文字 |
| **留白充足** | 内容不要挤在一起，保持呼吸感 |

### 受众差异化示例

**给一把手（5分钟版）**：
- 只讲3个核心结论
- 每个结论配1个关键数据
- 结尾直接问"是否同意推进"

**给分管领导（15分钟版）**：
- 详细问题分析
- 实施方案路径
- 资源需求清单

**给执行层（30分钟版）**：
- 完整根因分析
- 详细技术方案
- 任务分解表

---

## 复用指南

### 如何复用示例

1. **复制模板**：选择符合你场景的示例，复制完整HTML代码
2. **替换内容**：修改文字、数字、图片路径
3. **调整页数**：增删页面，调整页码
4. **定制样式**：根据需要调整颜色、字号

### 快速修改技巧

**替换主题色**：
```html
<!-- 在<head>中添加 -->
<style>
  :root {
    /* 替换为你选择的主题色变量 */
    --accent: #0369A1; /* 政务科技主色 */
  }
</style>
```

**调整数据展示**：
```html
<!-- 修改数字和标签 -->
<div class="stat-card">
  <div class="m">新标签名称</div>
  <div class="n">新数字 <small>单位</small></div>
  <div class="l">新说明文字</div>
</div>
```

**替换图片**：
```html
<!-- 修改src路径 -->
<div class="frame-img h-22">
  <img src="your-image-path.png" alt="图片说明">
</div>
```

---

## 下一步

- 查看 [references/layouts.md](./references/layouts.md) 了解12种布局代码
- 查看 [references/components.md](./references/components.md) 了解所有组件用法
- 查看 [references/themes.md](./references/themes.md) 了解主题色切换方法
- 使用 [QUICKSTART.md](./QUICKSTART.md) 快速上手

**开始制作你的专业PPT吧！**