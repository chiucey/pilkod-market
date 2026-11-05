---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3cae14c1fd3cc949110fb662aaaa9272
    PropagateID: 3cae14c1fd3cc949110fb662aaaa9272
    ReservedCode1: 3045022100c860cf0e9848c9c81bebffbbf949f3acdeb6a93f558d6ea15994f8c1e2c87bc00220467f290749f93aa6218a97cfe4343768155cdcd6fda1e99ce91bc84c57a38148
    ReservedCode2: 304502204e384382faab468bd0fb4687e0cf87b09b25023590b9d1c207e3a4719bb44aff0221009655c9aa1322f30d5cbbc082c856f0cecd1eab57a6c491cbb4c19c04b99e99fa
description: 品牌营销项目双语汇报网页生成器。当用户需要「生成会议网页」「双语汇报」「项目协同页面」「进度汇报链接」时触发。支持品牌出海、全案合作、跨部门对齐等场景的标准化汇报输出。
name: report-deck
trigger:
    - 生成会议网页
    - 双语汇报
    - 项目协同页面
    - 进度汇报链接
    - 领聚牧高笛
    - 项目对接表
    - Collaboration Brief
    - 项目追踪表
---

# SKILL.md — Report Deck · 品牌营销项目双语汇报网页生成器

## 版本
v1.0 | 2026-05-19 | 稳定可复用

---

## 一、设计语言（Design Tokens）

所有报表网页必须严格遵循以下视觉规范，不可随意更改。

### 色彩系统
| Token | 色值 | 用途 |
|---|---|---|
| 品牌红（主色） | `#dc2626` | 标题栏、Section 头部、强调元素 |
| 深黑 | `#1a1a1a` | 表头背景、重要信息条 |
| 背景灰 | `#f5f5f5` | 页面背景 |
| 卡片白 | `#fff` | 区块背景 |
| 完成绿 | `#16a34a` | 状态：已完成 |
| 进行黄 | `#d97706` | 状态：进行中 |
| 危险红 | `#dc2626` | 状态：待启动 / 高优先级 |
| 链接蓝 | `#2563eb` | 日期 Badge 背景 |

### 字体
- 主字体：`-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- 字号体系：
  - 页面背景：13px / line-height: 1.6
  - 标题栏：17px bold
  - Section 小标题：14px bold
  - 正文：12px
  - 注释/小字：10-11px

### 间距系统
- 页面横向内边距：`margin: 14px 20px`
- Section 内边距：`padding: 16px 18px`
- 区块间距（gap）：`gap: 20px`（双栏）/ `gap: 14px`（三栏）

### 圆角
- 卡片/区块：`border-radius: 8px`
- 小标签（Badge）：`border-radius: 4px` / 20px（胶囊）
- 状态圆点：`border-radius: 50%`

---

## 二、通用模板结构

每个网页必须包含以下固定板块，按顺序排列：

```
[Doc Header]          品牌标题栏（红色块 + 白色 Meta 区）
[Sec 00]              项目总览（双方Banner + 状态概览）
[Sec 01]              服务范围 / 职责划分
[Sec 02]              核心问题（问题 → 期望 → 磨合合作形式）
[Sec 03]              协同管理表（可编辑表格）
[Sec 04]              下一步待办（进度条）
[Doc Footer]          品牌签名档
```

### Section 结构（三层）
```html
<div class="mobi-section">
  <div class="sec-head">
    <span class="sec-num">00</span>
    <span class="sec-label">中文标题</span>
    <span class="sec-en">English Subtitle</span>
  </div>
  <div class="sec-body">
    <!-- 内容区 -->
  </div>
</div>
```

---

## 三、核心组件库

### 3.1 Doc Header
```html
<div class="doc-header">
  <div class="brand-block">
    <div class="brand">品牌名称</div>
    <div class="ver">Internal Document</div>
  </div>
  <div class="meta">
    <h1>页面主标题</h1>
    <div class="sub">副标题 · 日期</div>
    <div class="tags">
      <span class="tag r">标签1</span>
      <span class="tag g">标签2</span>
    </div>
  </div>
</div>
```

### 3.2 Party Banner（双方角色卡）
```html
<div class="party-banner">
  <div class="party lj">
    <div class="party-tag">A 方 服务方</div>
    <div class="party-name">机构名</div>
    <div class="party-desc">一句话描述</div>
    <div class="party-role">牵头：模块A / 模块B</div>
  </div>
  <div class="party mg">
    <div class="party-tag">B 方 品牌方</div>
    <div class="party-name">品牌名</div>
    <div class="party-desc">一句话描述</div>
    <div class="party-role">牵头：模块A / 模块B</div>
  </div>
</div>
```

### 3.3 状态概览行
```html
<div class="st-row">
  <div class="st-item"><div class="dot d-g"></div><strong>Q2 2026</strong></div>
  <div class="st-item"><div class="dot d-g"></div><strong>Shopify</strong></div>
  ...
</div>
```

### 3.4 已完成 / 进行中 列表
```html
<div class="grid-2">
  <div>
    <div class="s-title"><span class="zh">已完成</span></div>
    <div class="st-row" style="flex-direction:column;gap:4px">
      <div class="st-item"><div class="dot d-g"></div>事项1</div>
      <div class="st-item"><div class="dot d-r"></div>事项2</div>
    </div>
  </div>
  <div>
    <div class="s-title"><span class="zh">进行中 / 待推进</span></div>
    ...
  </div>
</div>
```

### 3.5 问题卡片（三栏布局）
```html
<div class="prob-row">
  <div class="prob-card">
    <div class="prob-header"><span class="prob-num">01</span><span class="prob-title">问题标题</span></div>
    <div class="prob-body">
      <strong>问题</strong><p>问题描述...</p>
      <div class="expect-block">
        <div class="block-label">牧高笛期望</div><p>期望内容...</p>
      </div>
      <div class="coop-block">
        <div class="block-label">磨合合作形式</div><p>磨合形式...</p>
      </div>
    </div>
  </div>
</div>
```

### 3.6 协同管理表（核心表格）
```html
<!-- 说明区 -->
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px;font-size:11px;color:#555">
  <span><span style="display:inline-block;width:9px;height:9px;background:#2563eb;border-radius:50%;margin-right:4px;vertical-align:middle"></span><span class="col-badge col-date">需求时间</span> 含义</span>
  <span><span class="custom-checkbox checked" style="margin-right:4px">OK</span>牵头负责方</span>
  <span><span class="col-badge col-ddl">DDL</span> 交付截止时间</span>
</div>

<table class="coop-tbl">
  <thead>
    <tr>
      <th style="width:30px">#</th>
      <th>项目 / 描述</th>
      <th style="width:55px">优先级</th>
      <th style="width:82px"><span class="col-badge col-date">需求时间</span></th>
      <th style="width:82px">预计完成时间</th>
      <th style="width:78px">审核周期</th>
      <th style="width:82px"><span class="col-badge col-ddl">DDL</span></th>
      <th style="width:58px" class="center">OK 机构</th>
      <th style="width:58px" class="center">OK 品牌</th>
      <th style="width:88px">备注</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="num-badge">1</span></td>
      <td>
        <div class="item-name">项目名称</div>
        <div class="item-sub">英文描述 · 补充说明</div>
      </td>
      <td><span class="priority-tag priority-hi">高</span></td>
      <td><input class="date-input" type="text" value="2026/05/25"></td>
      <td><input class="date-input" type="text" value="2026/06/05"></td>
      <td><input class="date-input" type="text" value="5 工作日"></td>
      <td><input class="date-input" type="text" value="2026/06/12"></td>
      <td class="checkbox-cell"><span class="custom-checkbox checked">OK</span></td>
      <td class="checkbox-cell"><span class="custom-checkbox">o</span></td>
      <td><input class="date-input" type="text" value="待启动" style="color:#dc2626;font-weight:600"></td>
    </tr>
  </tbody>
</table>
```

### 3.7 下一步待办（进度条）
```html
<div class="grid-2">
  <div>
    <div class="s-title"><span class="zh" style="color:#dc2626">待启动</span></div>
    <div class="tl-row">
      <div class="tl-dot" style="background:#dc2626"></div>
      <div class="tl-label">任务名称</div>
      <div class="tl-bar"><div class="tl-fill" style="width:0%;background:#dc2626"></div></div>
      <div class="tl-pct">0%</div>
    </div>
  </div>
</div>
```

### 3.8 双周会对齐条
```html
<div class="biweek-strip">
  <div class="biweek-main">
    <div class="biweek-title">双周会对齐机制 Bi-Weekly Sync</div>
    <div class="biweek-desc">每两周一次快速对齐会（建议15分钟），保持双周沟通节奏不中断。</div>
  </div>
  <div class="biweek-tag">双周会</div>
</div>
```

### 3.9 Doc Footer
```html
<div class="doc-footer">
  品牌名 Engineered in the Hengduan Built for your trailhead<br>
  助手名 · 协作方 · Internal Document · YYYY-MM-DD
</div>
```

---

## 四、执行流程

### Step 1 — 确认需求
- 确定项目名称（如牧高笛 x 领聚）
- 确定双方名称、角色定位（A方服务方 / B方品牌方）
- 确定要展示哪些 Section（00-04 默认全部，可选）

### Step 2 — 替换关键变量
将以下占位符替换为实际内容：
- `{品牌名}` → MOBI GARDEN
- `{项目标题}` → 项目协同对接表
- `{A方机构名}` → 领聚
- `{B方品牌名}` → 牧高笛
- `{日期}` → YYYY-MM-DD
- `{助手名}` → Max Claw Second

### Step 3 — 生成 HTML
使用本 SKILL.md 的 CSS + HTML 模板，将内容填充进去。

**重点规则：**
- 所有 CSS 必须内联在 `<style>` 中，不得使用外部文件
- CSS 变量不得随意修改，色值必须使用 Design Tokens 表格中的定义
- HTML 标签结构必须遵循组件库的三层结构

### Step 4 — 验证与发布
1. 确认文件保存为 `index.html`（含 index.html）
2. `deploy` 到 `workspace/report-deck/` 或 `workspace/{项目名}/`
3. 返回链接给用户

---

## 五、稳定输出检查清单

每次输出前核对：
- [ ] Doc Header 红色块 + 白 Meta 区结构正确
- [ ] Section 编号连续（00 / 01 / 02…）
- [ ] 表头为深黑色 `#1a1a1a`，白字，UPPERCASE
- [ ] 日期 Badge：蓝色 `#2563eb` / DDL Badge：红色 `#dc2626`
- [ ] 优先级 Badge：红（高）/ 黄（中）/ 绿（低）
- [ ] 进度条 0% 为红色，任意进度为黄色
- [ ] 可编辑表格中，领聚打勾（OK 红色填充），牧高笛留空（o 灰色）
- [ ] Doc Footer 有品牌签名档
- [ ] deploy 目录包含 `index.html`，不是只有 `meeting-deck.html`