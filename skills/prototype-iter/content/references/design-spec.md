# ToB 工作台视觉规范（中国移动内勤系统）

> 此规范由用户提供 9 张参考图提取 + HTML 方案验证后沉淀，作为 `prototype-iter` skill 的"硬约束"。
> 所有基于此 skill 的原型生成必须严格遵守此规范。
> **重要**：本规范已根据最新用户反馈修正。设计 token 优先用 `:root` CSS 变量实现，保证改版一致性。

## 1. 色彩系统（CSS 变量）

```css
:root {
  --primary-blue: #3B7CFF;        /* 主色蓝：导航栏、主按钮、Tab 选中态、强调 */
  --primary-blue-dark: #1A5FE0;   /* 深蓝：区块标题左侧竖线、按钮 hover */
  --warning-orange: #FF8800;      /* 警告橙：告警文字、感叹号 */
  --warning-bg: #FFF8E1;          /* 警告底色：黄色提示框 */
  --danger-red: #E53935;          /* 警示红：必填星号、错误状态 */
  --danger-bg: #FFEBEE;           /* 警示底色 */
  --bg-page: #F5F7FA;             /* 页面浅灰：区块底色 */
  --bg-card: #FFFFFF;             /* 卡片白底 */
  --border-light: #ECECEC;        /* 字段间分割线 */
  --border-section: #D8DCE0;     /* 区块间分割线 */
  --border-default: #E8E8E8;      /* 通用边框 */
  --border-input: #D9D9D9;        /* 输入框边框（极少用） */
  --text-primary: #333333;        /* 主文字：标题、关键信息 */
  --text-secondary: #666666;      /* 次要说明 */
  --text-tertiary: #999999;       /* 提示 */
  --text-placeholder: #B5B5B5;    /* 占位符：纯文字、1px 灰线上方 */
  --text-on-primary: #FFFFFF;     /* 主按钮上的文字 */
  --stripes-red: #E53935;         /* 装饰条红色 */
  --stripes-blue: #3B7CFF;        /* 装饰条蓝色 */
  --table-row-alt: #F0F5FF;       /* 表格交替行浅蓝 */
  --select-bg: #E8E8E8;           /* mini-select 选择器底色 */
}
```

---

## 2. 字体系统

### 字体族（CSS font-family）
```css
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
             "Hiragino Sans GB", "Microsoft YaHei",
             "Helvetica Neue", Arial, sans-serif;
```

### 字号层级
| Token | 字号 | 字重 | 用途 |
|-------|------|------|------|
| `--font-statusbar` | 14px | 600 | 状态栏时间/电量 |
| `--font-nav-title` | 17px | 600 | 顶部导航标题 |
| `--font-section-title` | 16px | 600 | 区块标题（带蓝竖线） |
| `--font-label` | 14px | 400 | 字段标签 |
| `--font-body` | 14px | 400 | 占位符、表头 |
| `--font-button` | 14-15px | 500 | 按钮文字 |
| `--font-helper` | 13px | 400 | mini-select 文字 |
| `--font-tab` | 14-15px | 400 | Tab 文字 |

### 字重
- **400 (Regular)**: 默认正文、占位符、字段标签
- **500 (Medium)**: 按钮、Tab 选中
- **600 (Semi-Bold)**: 区块标题、导航标题、状态栏

---

## 3. 组件 HTML 实现（关键 - 沉淀自用户多轮反馈）

### 3.1 状态栏
```html
<div class="status-bar">
  <div>16:35</div>
  <div class="right">
    <span>4G</span>
    <span style="background:#FFD700;color:#000;padding:1px 4px;border-radius:3px;font-size:11px;font-weight:700;">91</span>
  </div>
</div>
```
- 高度 44px，背景 `--primary-blue`，白色文字
- 电量数字用金色背景小方块（这是这个 App 的特殊样式）

### 3.2 顶部导航栏
```html
<div class="nav-bar">
  <div class="nav-icon">✕</div>
  <div class="title">产品变更</div>
  <div class="nav-icon">
    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 2a8 8 0 0 0-8 8v6a4 4 0 0 0 4 4h1v-7H6v-3a6 6 0 0 1 12 0v3h-3v7h1a4 4 0 0 0 4-4v-6a8 8 0 0 0-8-8z"/>
    </svg>
  </div>
</div>
```
- 高度 44px，背景 `--primary-blue`
- 左侧 X 关闭按钮（白色），中间标题（17px Bold），右侧客服/操作图标

### 3.3 顶部 Tab 栏
```html
<div class="tabs-top">
  <div class="tab">短信验证码</div>
  <div class="tab active">服务密码</div>
  <div class="tab">读取证件</div>
  <div class="tab">证件输入</div>
</div>
```
- 4 个 Tab 等分
- 选中态：蓝色文字 + 下方 2px 蓝下划线（宽度约 50px，居中）
- 非选中：黑色 14px

### 3.4 搜索区（关键 - 不要用 input）
```html
<div class="search-area">
  <div class="input-line">
    <div class="placeholder">请输入服务号码或宽带账号</div>
    <div class="line"></div>
  </div>
  <div class="query-line">
    <div class="input-line">
      <div class="placeholder">请输入服务密码或宽带密码</div>
      <div class="line"></div>
    </div>
    <button class="query-btn">查询</button>
  </div>
</div>
```

```css
.input-line { padding: 12px 0 0; }
.input-line .placeholder {
  color: var(--text-placeholder);
  font-size: 14px;
  padding-bottom: 6px;
  display: block;
}
.input-line .line {
  height: 1px;
  background: #E8E8E8;
}
.query-btn {
  width: 90px;
  height: 32px;
  border: 1px solid var(--primary-blue);
  color: var(--primary-blue);
  background: var(--bg-card);
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
}
```

**关键**：搜索区**没有 input 边框**，只有 placeholder 文字 + 下方 1px 灰线。查询按钮是普通描边按钮。

### 3.5 选择用户区块
```html
<div class="section select-user">
  <div class="section-title">
    <div class="text">选择用户</div>
    <svg class="arrow"><polyline points="3 6 8 11 13 6"/></svg>
  </div>
  <div class="section-content">
    <div class="three-col-header">
      <div>主体服务类型</div>
      <div>接入类型</div>
      <div>服务号码</div>
    </div>
    <div class="stripes"></div>
    <div class="three-col-fields">
      <div>用户名：</div>
      <div>服务号码：</div>
      <div>用户状态：</div>
    </div>
  </div>
</div>
```

```css
.three-col-header {
  background: var(--table-row-alt);
  display: flex;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
}
.three-col-header > div { flex: 1; }

.stripes {
  height: 8px;
  background: repeating-linear-gradient(90deg,
    #E53935 0 8px, #FFFFFF 8px 16px,
    #3B7CFF 16px 24px, #FFFFFF 24px 32px);
}

.three-col-fields {
  background: var(--bg-card);
  display: flex;
  padding: 16px;
  font-size: 14px;
}
/* ★ 关键：所有 label 左对齐，给数值预留空间 ★ */
.three-col-fields > div {
  flex: 1;
  text-align: left;
}
```

**关键**：`three-col-fields` 三栏**全部左对齐**（不要居中/右对齐），因为这些字段后期要带数值。

### 3.6 中部 Tab 行
```html
<div class="tabs-middle">
  <div class="tab">主套餐变更</div>
  <div class="tab">流量专区</div>
  <div class="tab active">增值产品</div>
  <div class="tab">数据套餐</div>
</div>
```
- 浅灰背景
- 选中态：**蓝色实心背景 + 白字**（与顶部 Tab 不同，这里是块状选中）
- Tab 之间有 1px 分隔

### 3.7 区块（折叠/展开）—— 核心组件

```html
<!-- 折叠状态：只显示标题区，不要 section-content -->
<div class="section collapsed">
  <div class="section-title">
    <div class="text">我的附加套餐</div>
    <svg class="arrow" viewBox="0 0 16 16" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="3 6 8 11 13 6"/>
    </svg>
  </div>
</div>

<!-- 展开状态 -->
<div class="section expanded">
  <div class="section-title">
    <div class="text">代办人信息</div>
    <svg class="arrow">...</svg>
  </div>
  <div class="section-content">
    <!-- 字段行 -->
  </div>
</div>
```

```css
.section {
  background: var(--bg-page);
  border-bottom: 1px solid var(--border-section);  /* ★ 区块间 1px 分割线 ★ */
}
.section:last-child { border-bottom: none; }

.section-title {
  height: 44px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  background: var(--bg-page);
  position: relative;
  user-select: none;
}
.section-title::before {
  content: "";
  width: 3px;
  height: 18px;
  background: var(--primary-blue-dark);
  margin-right: 12px;
}
.section-title .text {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}
.section-title .arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  transition: transform 0.2s;
}
/* 折叠时箭头旋转 180°（向上 = 展开态） */
.section.collapsed .section-title .arrow {
  transform: translateY(-50%) rotate(180deg);
}
.section.collapsed .section-content { display: none; }
```

**关键约定**：
- **所有 6 个区块的标题箭头都是向上（∧）**，无论折叠/展开状态
- 折叠状态通过箭头旋转 180° 表达
- 区块之间**必须有 1px 浅灰分割线**（`border-bottom`）

### 3.8 字段行（关键 - 很多字段无 input）

```html
<!-- 类型 A：带 input（用于"证件类型"下拉、"促销员/推荐人"输入） -->
<div class="field-row">
  <div class="label"><span class="required">*</span>证件类型：</div>
  <div class="value-wrap">
    <div class="mini-select">
      <span>请选择</span>
      <span class="arrow-down">⌄</span>
    </div>
  </div>
</div>

<!-- 类型 B：纯文字（用于"证件号码"、"姓名"等） -->
<div class="field-row">
  <div class="label"><span class="required">*</span>证件号码：</div>
  <div class="value-wrap"></div>
</div>

<!-- 类型 C：占位文字 + 搜索图标（用于"促销员"、"推荐人"） -->
<div class="field-row">
  <div class="label">促销员：</div>
  <div class="value-wrap">
    <span class="placeholder-text">请点击右侧图片进行查询</span>
    <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="#3B7CFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="10" cy="10" r="6"/>
      <line x1="20" y1="20" x2="14.5" y2="14.5"/>
    </svg>
  </div>
</div>
```

```css
.field-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-card);
  min-height: 48px;
  border-bottom: 1px solid var(--border-light);  /* ★ 字段间 1px 分割线 ★ */
}
.field-row:last-child { border-bottom: none; }
.field-row .label {
  width: 100px;
  font-size: 14px;
  color: var(--text-primary);
}
.field-row .label .required {
  color: var(--danger-red);
  margin-right: 3px;
}
.field-row .value-wrap {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* mini-select 选择器（圆角椭圆） */
.mini-select {
  display: inline-flex;
  align-items: center;
  gap: 24px;
  padding: 6px 14px;
  background: var(--select-bg);
  border-radius: 16px;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
}

/* 搜索图标 */
.search-icon {
  width: 22px;
  height: 22px;
  color: var(--primary-blue);
  cursor: pointer;
  flex-shrink: 0;
}
```

**关键规则**：
- **大多数字段（证件号码、姓名）value-wrap 为空**，不渲染 input
- **只有"证件类型"用 mini-select 圆角椭圆**（不要用全宽大下拉框）
- **"促销员"、"推荐人"用纯 placeholder 文字 + 右侧 SVG 搜索图标**
- 字段之间**必须有 1px 浅灰分割线**

### 3.9 按钮
```html
<!-- 主按钮：蓝色实心 -->
<button class="btn-primary">提交</button>

<!-- 次按钮：白色 + 蓝色描边 -->
<button class="btn-secondary">取消</button>
```

```css
.btn-primary {
  height: 40px;
  padding: 0 24px;
  background: var(--primary-blue);
  color: var(--text-on-primary);
  font-size: 15px;
  font-weight: 500;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-secondary {
  height: 40px;
  padding: 0 24px;
  background: var(--bg-card);
  color: var(--primary-blue);
  font-size: 15px;
  font-weight: 500;
  border: 1px solid var(--primary-blue);
  border-radius: 4px;
  cursor: pointer;
}
```

### 3.10 提示框
```html
<!-- 警告（黄色） -->
<div class="alert-warning">
  <span class="icon">⚠</span>
  <span>该用户未订购过分期返还活动</span>
</div>

<!-- 错误（红色） -->
<div class="alert-danger">
  <span class="icon">⚠</span>
  <span>操作失败</span>
</div>
```

```css
.alert-warning {
  background: var(--warning-bg);
  color: var(--warning-orange);
  padding: 12px;
  font-size: 14px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
.alert-danger {
  background: var(--danger-bg);
  color: var(--danger-red);
  padding: 12px;
  font-size: 14px;
}
```

---

## 4. 布局规范

### 容器宽度
- 移动端模拟：`.phone { width: 390px; }`（iPhone 14）
- 页面左右边距：16px

### 区块间距
- 区块之间：通过 `border-bottom` 1px 浅灰线分割（**不是用 margin**）
- 字段之间：通过 `border-bottom` 1px 浅灰线分割
- 区块内部 padding：12-16px

### 表单布局
- 左右结构：标签左（width: 100px）+ 输入右
- 标签宽度：固定 100px
- value-wrap flex: 1 占满剩余

---

## 5. 图标 SVG 规范

### 搜索图标（圆 + 斜把手）
```svg
<svg viewBox="0 0 24 24" fill="none" stroke="#3B7CFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="10" cy="10" r="6"/>
  <line x1="20" y1="20" x2="14.5" y2="14.5"/>
</svg>
```
- 描边色：主色蓝
- 描边宽度：2px
- 圆头线帽

### 折叠箭头（向上 ∨ 形状）
```svg
<svg viewBox="0 0 16 16" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="3 6 8 11 13 6"/>
</svg>
```
- 描边色：主文字 #333333
- 形状：向上箭头（"∧"）
- 折叠状态：通过 `transform: rotate(180deg)` 翻转

### 客服头像（iOS 风格）
```svg
<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2a8 8 0 0 0-8 8v6a4 4 0 0 0 4 4h1v-7H6v-3a6 6 0 0 1 12 0v3h-3v7h1a4 4 0 0 0 4-4v-6a8 8 0 0 0-8-8z"/>
</svg>
```

### 关闭按钮
- 用 `✕` 字符即可（22px 字号，weight 300）

---

### 3.11 信息提示 banner（蓝色 info）

```html
<div class="info-banner">该用户暂无活动订购信息！</div>
```

```css
.info-banner {
  background: #E8F0FF;   /* 浅蓝底 */
  color: #3B7CFF;        /* 蓝色文字 */
  padding: 14px 16px;
  text-align: center;
  font-size: 14px;
}
```

**注意**：与警告框（黄色 `#FFF8E1`）和错误框（红色 `#FFEBEE`）不同，info banner 是**浅蓝底 + 主色蓝字**。

### 3.12 主按钮 vs 次按钮（关键 - 容易用错）

| 类型 | 用途 | 样式 |
|------|------|------|
| **主按钮（实心）** | 重要操作（提交、确定） | 蓝底 + 白字 |
| **次按钮（描边）** | 普通操作（去办理、取消） | **白底 + 蓝边 + 蓝字** |

```css
/* 主按钮 - 实心 */
.btn-primary {
  background: var(--primary-blue);
  color: var(--text-on-primary);
  border: none;
}

/* 次按钮 - 描边，"去办理"用这个 */
.btn-secondary {
  background: var(--bg-card);
  color: var(--primary-blue);
  border: 1px solid var(--primary-blue);
}
```

### 3.13 5 个图标按钮行

横向排列 5 个图标 + 文字，常用于"套餐余量查询"等快捷入口。

```html
<div class="icon-row">
  <div class="item active">
    <div class="icon-box">
      <svg>...</svg>
    </div>
    <div class="label">语音通话</div>
  </div>
  <!-- 4 more items -->
</div>
```

```css
.icon-row { display: flex; background: var(--bg-card); padding: 16px 8px; }
.icon-row .item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; }
.icon-row .icon-box {
  width: 44px; height: 44px;
  background: #F0F5FF;       /* 浅蓝底（激活态） */
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: var(--primary-blue);
}
.icon-row .item .label { font-size: 13px; color: var(--primary-blue); }

/* 未激活：灰底 + 灰图标 + 灰字 */
.icon-row .item:not(.active) .icon-box { background: #F0F0F0; color: var(--text-tertiary); }
.icon-row .item:not(.active) .label { color: var(--text-tertiary); }
```

### 3.14 个人套餐/群套餐切换（下划线样式）

```html
<div class="pkg-switch">
  <div class="item active">个人套餐</div>
  <div class="item">群套餐</div>
</div>
```

```css
.pkg-switch { display: flex; background: var(--bg-page); }
.pkg-switch .item { flex: 1; padding: 14px 0; text-align: center; font-size: 14px; color: var(--text-secondary); cursor: pointer; }
.pkg-switch .item.active { color: var(--primary-blue); font-weight: 500; }
.pkg-switch .item.active::after {
  content: ""; display: block;
  width: 40px; height: 2px;
  background: var(--primary-blue);
  margin: 6px auto 0;
}
```

### 3.15 数据卡（左侧圆形 + 右侧带外框字段）

```html
<div class="data-card">
  <div class="donut">
    <div>
      <div class="top">套餐</div>
      <div class="bottom">总量</div>
    </div>
  </div>
  <div class="fields">
    <div class="field">
      <div class="name">套餐外主叫</div>
      <div class="val">0分钟</div>
    </div>
    <div class="field">
      <div class="name">套餐外被叫</div>
      <div class="val">0分钟</div>
    </div>
  </div>
</div>
```

```css
.data-card { display: flex; align-items: center; background: var(--bg-card); padding: 20px 16px; gap: 16px; }

/* 左侧蓝色圆 */
.data-card .donut {
  width: 88px; height: 88px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A8BFF, #6FA0FF);
  display: flex; align-items: center; justify-content: center;
  color: var(--bg-card);
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(74, 139, 255, 0.35);
}
/* 圆内文字：上下两行层次 */
.data-card .donut .top { font-size: 11px; opacity: 0.95; line-height: 1.2; }
.data-card .donut .bottom { font-size: 17px; font-weight: 600; line-height: 1.2; margin-top: 2px; }

/* 右侧两个字段：每个有 1px 浅灰圆角外框 */
.data-card .fields { flex: 1; display: flex; gap: 12px; }
.data-card .field {
  flex: 1;
  border: 1px solid #E0E0E0;
  border-radius: 6px;
  padding: 10px 8px;
  text-align: center;
  background: var(--bg-card);
}
.data-card .field .name { font-size: 12px; color: var(--text-secondary); }
.data-card .field .val { font-size: 14px; color: var(--text-primary); margin-top: 4px; font-weight: 500; }
```

### 3.16 表格（带表头/斑马纹/新增列处理）

```html
<table class="table">
  <thead>
    <tr>
      <th class="col-name">套餐名称</th>
      <th class="col-type">优惠类型</th>
      <th class="col-total">套餐总量</th>
      <th class="col-used">已使用量</th>
      <th class="col-left">剩余量</th>
      <th class="col-done">是否用完</th>
      <th class="col-share">是否共享</th>   <!-- 新增列 -->
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>...</td>
      <!-- 每行 cell 数量 = 表头 th 数量 -->
    </tr>
  </tbody>
</table>
```

```css
.table { width: 100%; border-collapse: collapse; background: var(--bg-card); font-size: 13px; }
.table thead th {
  background: var(--primary-blue);   /* 表头蓝底白字 */
  color: var(--bg-card);
  padding: 12px 8px;
  font-weight: 500;
  text-align: center;
  font-size: 13px;
}
.table tbody td {
  padding: 14px 8px;
  text-align: center;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-light);
}
/* 斑马纹：偶数行浅蓝底 */
.table tbody tr:nth-child(even) td { background: #F0F5FF; }
.table tbody tr:last-child td { border-bottom: none; }

/* 列宽自定义 */
.col-name { width: 18%; }
.col-type { width: 14%; }
.col-total { width: 14%; }
.col-used { width: 14%; }
.col-left { width: 14%; }
.col-done { width: 13%; }
.col-share { width: 13%; }
```

**关键：新增列的列宽分配**
- 不要给新列 100% 宽度然后让其他列被挤爆
- 原则：每列等比例缩减约 2-3%，让总宽度保持 100%
- 例：原 6 列各 ~16%，新增第 7 列后各列重新分到 ~13-14%


---

## 6. 易错点（用户多次反馈过的问题）

| 错误做法 | 正确做法 |
|---------|---------|
| 搜索区用 `<input type="text">` | 搜索区用 `<div class="placeholder">` + `<div class="line">` |
| "证件号码"/"姓名"用 input 框 | value-wrap 留空 |
| "证件类型"用全宽大下拉框 | 用 mini-select 圆角椭圆选择器 |
| "促销员/推荐人"用 input 框 | 用占位文字 + 右侧 SVG 搜索图标 |
| 区块之间用 margin 分隔 | 用 `border-bottom: 1px solid` 分割线 |
| 字段之间没有分割线 | 加 `border-bottom: 1px solid var(--border-light)` |
| "用户名/服务号码/用户状态" 三栏分别左/中/右对齐 | **全部左对齐**，给数值预留空间 |
| 折叠区块有"暂无附加套餐"等占位文字 | 折叠区块只显示 section-title，**不显示 section-content** |
| 区块右侧箭头使用向下 "∨" | **所有箭头都是向上 "∧"**，折叠态用 CSS 旋转 180° |
| 搜索图标用 emoji 🔍 | 用 SVG 圆 + 斜把手 |
| "去办理"按钮做成实心蓝底白字（主按钮） | **白底 + 蓝边 + 蓝字**（次按钮样式） |
| 数据卡左侧"套餐总量"用单行 | **上下两行层次**：上"套餐"11px + 下"总量"17px Bold |
| "套餐外主叫/被叫"无外框 | 每个字段 1px 浅灰圆角外框（`#E0E0E0` + 6px 圆角） |
| 表格新增列给 100% 宽度 | 每列等比例缩减 2-3%，保持总宽 100% |
| 信息提示用黄色警告框 | **info 用浅蓝底**（`#E8F0FF` + 蓝字 `#3B7CFF`），区别于警告（黄）和错误（红） |
| 5 个图标按钮用 emoji | 用 SVG 线性图标 + 浅蓝/浅灰圆角方形底 |

---

## 7. 参考图清单

用户提供 9 张参考图，覆盖：
1. 加解密黑历史记录页（表单+折叠）
2. 产品变更页（Tab+折叠+分组）
3. 单宽带开户页（图片占位+表单+折叠）
4. 当期跟踪页（数据卡+表格）
5. 客户视图页（告警+Tab+信息卡）
6. 宽带移机信息收集页（折叠+输入卡）
7. 新融合专区成员管理页（步骤条+Tab+表单）
8. 费用合计页（折叠+表单+双按钮）
9. 新版违约金减免页（多选+单选+卡片列表）

**改版基线**：以"产品变更页"（`cc0cc048`）为标准实现，已在 HTML 方案中完整还原。

---

## 8. HTML 模板路径

完整 HTML 实现位于：`/workspace/prototype-iter/html-output/index.html`

可直接复制该文件作为新页面的起点，然后修改区块内容。
