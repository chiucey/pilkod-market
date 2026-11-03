---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: dfdf86a3035bfee0f98ff73467413508
    PropagateID: dfdf86a3035bfee0f98ff73467413508
    ReservedCode1: 304402203962e3fcf37fce6c817518608f1df6efbfa3e8047f8ac9f051514cae6278d0940220399b30976f963290a768c19893f880c41d9b6e6d47228095070e158496eb1c34
    ReservedCode2: 304502203af315250e958f241ee4470fa16cd1016079f832eb5f1727f41b3043f64feefd0221009fc7ceebc3c4b48e79f9d9b7a4cc64b09112f5a6316fe48f581d5c7c211502f4
---

# MOBI GARDEN 双语网页生成 — Prompts 参考库

> 本文档记录每个板块的生成逻辑、prompt 示例和关键技巧。可在 `skill-creator` 或直接复制到对话中使用。

---

## 整体结构（4大板块）

```
一、独立站进度     → 独立站 / DTC Store Progress
二、品牌侧确认     → Brand Confirmation
三、社媒板块       → Social Media & North America Trails
四、其他进度       → Other Progress & Open Items
```

---

## 板块一：独立站进度

### 包含内容
- 1.1 上线进度（Launch Progress）
- 1.2 下阶段优化（Next Phase Optimizations）
- 1.3 第二批上新产品（Phase 2）
- 1.4 东南亚站点（SEA Launch）

### 核心字段模板
```markdown
## 1.1 Launch Progress
- us.mobigarden.com 上线时间：[DATE]
- [已完成项] ✅
- [进行中项] 🔄 → 预计[X日内/Y月X日]完成
- [待确认项] ⏳
- Shipping & Return Policy：[状态]
- 商详页：[状态]
- 品牌故事 + About Us：[状态]

## 1.2 下阶段优化
卖点 Icon：[列出所有 Icon 名称]
视频素材：[安装 / 搭建]
站内链路：[热力图 + G4]

## 1.3 Phase 2 产品
[产品名] — [品类]
[产品名] — [品类]

## 1.4 SEA 东南亚
启动时间：[TBD / 具体日期]
定位：[描述]
```

### 生成Prompt示例
```
请将以下独立站进度数据生成为HTML卡片结构，中文为主，英文副标题：

[粘贴数据]

要求：
- 状态用彩色圆点表示：绿色=已完成，黄色=进行中，红色=待处理
- 时间节点明确标注
- Phase 2产品用红色标签高亮
- 布局：2列grid，1.1+1.2并排，1.3+1.4各独占一行
```

---

## 板块二：品牌侧确认

### 包含内容（按顺序）
- 2.1 品牌故事（中英双语 × 3段）
- 2.2 TOV · Voice Pillars · 语调四柱
- 2.3 DO & DON'T 词汇表
- 2.4 目标受众 TA × Anti-Persona
- 2.5 定位 & 定价（价格对比表）
- 2.6 产品设计·起源故事（新增）

### 品牌故事三段式结构
```markdown
### 起源 Origin
英文：[5-8句，Hengduan山脉地理背景，团队被困山野发现问题]
中文：[对应段落]

### 冷山传奇 The Original / HENGDUAN
英文：[5-8句，第一顶帐篷的工程思考，一百万行者背书]
中文：[对应段落]

### 品牌使命 OUR MISSION
英文：[5-8句，山野召唤，我们确保装备就绪]
中文：[对应段落]
```

### 产品设计故事结构（每款产品）
```markdown
### [产品英文名] · [产品中文名]
英文故事：[地点/背景事件] → [观察到的自然元素] → [灵感转化为产品设计] → [核心技术/规格]
中文故事：[对应翻译，保持叙事流畅]
```

### TOV Voice Pillars 结构
```markdown
P1 Evolutionary · 创新驱动
- 描述：[Biomimicry + altitude]
- 例句：[英文原句]

P2 Understated Mastery · 内敛精湛
- 描述：[Calm authority, explain engineering]
- 例句：[英文原句]

P3 Data-Driven Precision · 数据驱动
- 描述：[Exact metrics, measured not estimated]
- 例句：[英文原句]

P4 Earned Wit · 克制的幽默
- 描述：[Occasionally say something true]
- 已批准例句：[英文原句]
```

### 价格对比表格式
```markdown
| 产品 | MOBI GARDEN | 竞品 | 竞品价格 |
|------|-------------|------|---------|
| GENNYE PRO R6 (L) | $139.99 | NEMO Tensor All-Season long wide | $239.95 |
| Mountain Wing Pro | $89.99 | Helinox Chair Zero L | $169.95 |
| KONGAR EXO-FLEX UL | $349 | MSR Hubba NX | $499 |
```

### 生成Prompt示例
```
请将以下品牌材料生成为HTML结构，**中英双语同框展示**：

[粘贴品牌故事 × 3段]
[粘贴 Voice Pillars × 4条]
[粘贴 DO/DON'T 词汇表]
[粘贴 TA × Anti-Persona]
[粘贴定价信息]

要求：
- 品牌故事用 qt 引用块，英文在上、中文在下
- Voice Pillar 用 pll 卡片，按颜色区分 P1/P2/P3(蓝) vs P4(黄)
- DO/DON'T 用表格，红色删除线 vs 绿色批准词
- TA受众用 g3 三列grid，每个TA含Anti-Persona红色区块
- 定价表用 tbl 表格，MOBI GARDEN价格加粗
```

---

## 板块三：社媒板块 & 北美徒步路线

### 包含内容
- 3.1 达人合作（专业化 + 情绪化两路）
- 3.2 账号布局（Instagram / TikTok / YouTube / Reddit）
- 3.3 GEO 搜索词策略（SEM + SEO + AB Test）
- 3.4 北美徒步路线总览 + 产品×路线矩阵图（含Toggle开关）

### 路线表格结构
```markdown
| 路线 | 距离 | 最高海拔 | 气候 | 热度星级 | 主力产品 |
|------|------|---------|------|---------|---------|
| Colorado 14ers | 9.75 mi | 14,440 ft | Dry | ★★★★ | KONGAR P0 |
```

### Toggle开关HTML模板
```html
<!-- Toggle 开关 -->
<div class="toggle-row">
  <div class="toggle-label">显示产品匹配层 / Show Product Fit Overlay</div>
  <label class="switch">
    <input type="checkbox" id="matrixToggle" checked onclick="toggleMatrix()">
    <span class="slider"></span>
  </label>
</div>

<!-- 图片显示区 -->
<div class="matrix-wrap" id="matrixWrap">
  <img id="matrixImg" src="[产品匹配叠加图URL]" alt="...">
  <div class="caption" id="matrixCaption">产品×路线×气候三维匹配矩阵（开）</div>
</div>

<script>
function toggleMatrix() {
  var isOn = document.getElementById('matrixToggle').checked;
  var img = document.getElementById('matrixImg');
  var cap = document.getElementById('matrixCaption');
  if (isOn) {
    img.src = '[产品叠加图URL]';
    cap.innerHTML = '产品×路线×气候三维匹配矩阵（开）';
  } else {
    img.src = '[原始象限图URL]';
    cap.innerHTML = '原始象限图（关）';
  }
}
</script>
```

### 生成Prompt示例
```
请将以下达人策略和路线数据生成为HTML：

[粘贴达人合作策略]
[粘贴账号布局]
[粘贴GEO策略]

同时生成北美路线表格（8条路线，含：路线名/距离/最高海拔/气候/热度星级/主力产品）
嵌入产品×路线矩阵图（已有图片CDN：[URL]），并加入Toggle开关：
- 开=产品叠加图层
- 关=原始象限图
```

---

## 板块四：其他进度 & 待讨论事项

### Wayfair专题块模板
```html
<div class="wf-block">
  <div class="wf-grid">
    <div class="wf-stat"><div class="num">$12B+</div><div class="desc">2024年营收</div></div>
    <div class="wf-stat"><div class="num">21.3M+</div><div class="desc">活跃用户</div></div>
    <div class="wf-stat"><div class="num">80.7%</div><div class="desc">复购率</div></div>
    <div class="wf-stat"><div class="num">$150K+</div><div class="desc">用户年均收入</div></div>
  </div>
  <div class="wf-opp">
    <div class="label">我们的机会 / Our Opportunity</div>
    <ul>
      <li><strong>户外产品：</strong>...</li>
      <li><strong>庭院/Outdoor Living：</strong>...</li>
    </ul>
  </div>
</div>
```

---

## HTML样式常量（可直接复制）

### 颜色变量
```css
--red: #dc2626;        /* 主色，左侧边线 */
--green: #16a34a;      /* 完成状态 */
--yellow: #d97706;     /* 进行中 */
--blue: #2563eb;       /* TA/Pillar 蓝 */
--bg: #f5f5f5;         /* 页面背景 */
--card: #fff;          /* 卡片背景 */
--border: #e5e5e5;     /* 边框 */
```

### 布局网格
```css
.g2 { grid-template-columns: 1fr 1fr; gap: 10px; }
.g3 { grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
@media(max-width: 680px) { .g2, .g3 { grid-template-columns: 1fr; } }
```

### 状态指示灯
```html
<div class="sr">
  <div class="dot d-g"></div>  <!-- 绿色/完成 -->
  <div>内容</div>
</div>
<div class="sr">
  <div class="dot d-y"></div>  <!-- 黄色/进行中 -->
  <div>内容</div>
</div>
<div class="sr">
  <div class="dot d-r"></div>  <!-- 红色/待处理 -->
  <div>内容</div>
</div>
```

---

## 已知CDN链接（固化URL，供直接引用）

| 内容 | CDN URL |
|------|---------|
| 原始象限图 | `https://cdn.hailuoai.com/mcp/cdn_upload/489636598254198787/384727503606579/1776521303_0aec26e5.png` |
| 产品×路线矩阵叠加图 | `https://cdn.hailuoai.com/mcp/cdn_upload/489636598254198787/384727503606579/1776527885_54823726.png` |
| 北美路线象限图（另一版本） | `https://cdn.hailuoai.com/mcp/cdn_upload/489636598254198787/384727503606579/1776522226_c306d6b9.png` |

---

## 文件版本记录

| 版本 | 日期 | 主要变化 |
|------|------|---------|
| v1 | 2026-04-21 | 框架版，4大板块结构 |
| v2 | 2026-04-21 | 填入所有用户提供内容 |
| v3 | 2026-04-21 | 增加产品矩阵Toggle + Wayfair专题 |
| v4 | 2026-04-21 | 增加 2.6 产品设计·起源故事（GENNYE/KONGAR/KAWA/TALO）|
| v4.1 | 2026-04-22 | 生成 Skill 文件 mobi-meeting-deck + Prompts 参考库 |
