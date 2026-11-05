---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100e76de4cf8d961244149aca4a5a92633c14475e9e8296e5aca45ba1d0e50020fc0220465dde7251a3575432615e4210e0fab7d44f9ea9139be2334277eabe2262f7d2
    ReservedCode2: 304502202c33ab4564b985a4a3baecce53e3fe6be7735f1253197b90eb9c5196e14d3e62022100dba19305fc0f887f9987fb6f4e05a6f29f94769f3e9f93847b7b4d8df66769d5
---

# 主题色系统 · Themes

> 本Skill采用7套预设主题色方案。选择预设而非自定义颜色，确保视觉风格的专业性和一致性。

## 选择原则

- 通用默认场景选择「墨水经典」
- 政务传统场合选择「政务庄重」
- 政务科技场景选择「政务科技」
- 科技产品场景选择「科技未来」
- 教育培训场景选择「教育清新」
- 数据分析场景选择「数据专业」
- 创意展示场景选择「创意艺术」

## 切换方法

在`template.html`中，修改`:root`选择器下的CSS变量值，替换为对应主题的变量定义。

---

## 🖋 墨水经典（Ink Classic）

适合场景：通用默认、商业发布、年度汇报、方案提案、竞聘演讲

风格定位：专业稳重、优雅大气、信息密度适中

```css
/* 墨水经典 - 浅色主题 */
:root {
  /* 背景与前景 */
  --bg: #FAFAF9;
  --fg: #1A1A1A;
  --bg-secondary: #F5F5F4;

  /* 强调色 */
  --accent: #2563EB;
  --accent-light: #DBEAFE;
  --accent-dark: #1D4ED8;

  /* 功能色 */
  --success: #059669;
  --warning: #D97706;
  --error: #DC2626;

  /* 灰度阶梯 */
  --gray-1: #171717;
  --gray-2: #262626;
  --gray-3: #404040;
  --gray-4: #737373;
  --gray-5: #A3A3A3;
  --gray-6: #D4D4D4;
  --gray-7: #E5E5E5;

  /* 透明度变量 */
  --overlay: rgba(250, 250, 249, 0.85);
  --shadow: rgba(0, 0, 0, 0.08);
}
```

```css
/* 墨水经典 - 深色主题 */
[data-theme="dark"] {
  --bg: #0F0F0F;
  --fg: #FAFAF9;
  --bg-secondary: #1A1A1A;
  --overlay: rgba(15, 15, 15, 0.85);
  --shadow: rgba(0, 0, 0, 0.3);
}
```

---

## 🔴 政务庄重（Government Formal）

适合场景：政务汇报、智慧城市建设、数字化改革、信息化项目评审、官方会议

风格定位：庄重大气、权威专业、政治正确、层次分明

```css
/* 政务庄重 - 浅色主题 */
:root {
  /* 背景与前景 */
  --bg: #FFFFFF;
  --fg: #1F2937;
  --bg-secondary: #F3F4F6;

  /* 强调色 - 中国红 */
  --accent: #C41E3A;
  --accent-light: #FEE2E2;
  --accent-dark: #9B1C1C;

  /* 辅助强调 - 国旗黄 */
  --accent-secondary: #FFD700;

  /* 功能色 */
  --success: #059669;
  --warning: #D97706;
  --error: #DC2626;

  /* 灰度阶梯 */
  --gray-1: #111827;
  --gray-2: #1F2937;
  --gray-3: #374151;
  --gray-4: #6B7280;
  --gray-5: #9CA3AF;
  --gray-6: #D1D5DB;
  --gray-7: #E5E7EB;

  /* 透明度变量 */
  --overlay: rgba(255, 255, 255, 0.9);
  --shadow: rgba(0, 0, 0, 0.1);
}
```

```css
/* 政务庄重 - 深色主题 */
[data-theme="dark"] {
  --bg: #1F2937;
  --fg: #F9FAFB;
  --bg-secondary: #111827;
  --accent: #EF4444;
  --accent-secondary: #FCD34D;
  --overlay: rgba(31, 41, 55, 0.9);
  --shadow: rgba(0, 0, 0, 0.4);
}
```

**政务场景配色特点**：

- 主色调使用中国红（#C41E3A），体现政治属性
- 金色作为辅助强调色，用于重要数据和标题
- 白色背景为主，保证内容清晰可读
- 深蓝色用于正文，增强专业感

---

## 🔵 政务科技（Government Tech）

适合场景：智慧城市建设、数字化改革、科技政务、数据治理、人工智能政务、信息化项目评审

风格定位：科技感与政务庄重融合、现代化治理、数字化转型、权威专业

```css
/* 政务科技 - 浅色主题 */
:root {
  /* 背景与前景 */
  --bg: #F0F9FF;
  --fg: #0F172A;
  --bg-secondary: #E0F2FE;

  /* 强调色 - 科技蓝 */
  --accent: #0369A1;
  --accent-light: #BAE6FD;
  --accent-dark: #0284C7;

  /* 辅助强调 - 深邃蓝 */
  --accent-secondary: #1E40AF;

  /* 渐变色 */
  --gradient-start: #0284C7;
  --gradient-end: #6366F1;

  /* 功能色 */
  --success: #059669;
  --warning: #D97706;
  --error: #DC2626;
  --info: #0284C7;

  /* 灰度阶梯 */
  --gray-1: #0F172A;
  --gray-2: #1E293B;
  --gray-3: #334155;
  --gray-4: #64748B;
  --gray-5: #94A3B8;
  --gray-6: #CBD5E1;
  --gray-7: #E2E8F0;

  /* 透明度变量 */
  --overlay: rgba(240, 249, 255, 0.9);
  --shadow: rgba(2, 132, 199, 0.15);
  --glow: rgba(2, 132, 199, 0.3);
}
```

```css
/* 政务科技 - 深色主题 */
[data-theme="dark"] {
  --bg: #0C4A6E;
  --fg: #F0F9FF;
  --bg-secondary: #0C4A6E;
  --accent: #38BDF8;
  --accent-light: #0284C7;
  --accent-dark: #7DD3FC;
  --accent-secondary: #818CF8;
  --overlay: rgba(12, 74, 110, 0.9);
  --shadow: rgba(56, 189, 248, 0.2);
  --glow: rgba(56, 189, 248, 0.4);
}
```

**政务科技场景配色特点**：

- 主色调采用深邃科技蓝（#0369A1），体现数字化治理的专业形象
- 蓝色渐变营造科技感和现代感，同时保持政务的庄重气质
- 浅蓝背景（#F0F9FF）传达清新、信任、透明的政务服务理念
- 辅助紫色（#6366F1）增添数字化转型的前沿感
- 发光效果用于强调关键数据和交互元素

**与"政务庄重"的区别**：

| 维度 | 政务庄重 | 政务科技 |
|------|----------|----------|
| 主色调 | 中国红 #C41E3A | 科技蓝 #0369A1 |
| 风格 | 传统政务 | 数字化政务 |
| 背景 | 白色为主 | 浅蓝为主 |
| 适用场景 | 传统汇报、正式会议 | 智慧城市、科技评审 |
| 科技感 | 弱 | 强 |

---

## 🌊 科技未来（Tech Future）

适合场景：科技产品发布、AI技术展示、互联网产品、创业项目、创新大赛

风格定位：科技感、未来感、现代简约、视觉冲击强

```css
/* 科技未来 - 浅色主题 */
:root {
  /* 背景与前景 */
  --bg: #030712;
  --fg: #F9FAFB;
  --bg-secondary: #111827;

  /* 强调色 - 电光蓝 */
  --accent: #06B6D4;
  --accent-light: #0891B2;
  --accent-dark: #22D3EE;

  /* 渐变色 */
  --gradient-start: #06B6D4;
  --gradient-end: #8B5CF6;

  /* 功能色 */
  --success: #10B981;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;

  /* 灰度阶梯 */
  --gray-1: #F9FAFB;
  --gray-2: #E5E7EB;
  --gray-3: #9CA3AF;
  --gray-4: #6B7280;
  --gray-5: #4B5563;
  --gray-6: #374151;
  --gray-7: #1F2937;

  /* 透明度变量 */
  --overlay: rgba(3, 7, 18, 0.85);
  --shadow: rgba(6, 182, 212, 0.2);
  --glow: rgba(6, 182, 212, 0.4);
}
```

```css
/* 科技未来 - 浅色变体 */
[data-theme="light"] {
  --bg: #F8FAFC;
  --fg: #0F172A;
  --bg-secondary: #E2E8F0;
  --accent: #0891B2;
  --shadow: rgba(8, 145, 178, 0.15);
  --glow: rgba(8, 145, 178, 0.3);
}
```

**科技场景配色特点**：

- 以深色背景为主（#030712），突出科技质感
- 电光蓝和紫色渐变营造未来感
- 青色发光效果用于强调和装饰
- 大量使用深灰和黑色增加层次

---

## 🌿 教育清新（Education Fresh）

适合场景：教育培训、知识分享、在线课程、技能培训、学术交流

风格定位：清新自然、轻松明快、层次清晰、便于阅读

```css
/* 教育清新 - 浅色主题 */
:root {
  /* 背景与前景 */
  --bg: #F0FDF4;
  --fg: #14532D;
  --bg-secondary: #DCFCE7;

  /* 强调色 - 清新绿 */
  --accent: #16A34A;
  --accent-light: #BBF7D0;
  --accent-dark: #15803D;

  /* 辅助色 */
  --accent-secondary: #3B82F6;

  /* 功能色 */
  --success: #16A34A;
  --warning: #F59E0B;
  --error: #EF4444;
  --info: #3B82F6;

  /* 灰度阶梯 */
  --gray-1: #14532D;
  --gray-2: #166534;
  --gray-3: #15803D;
  --gray-4: #16A34A;
  --gray-5: #22C55E;
  --gray-6: #86EFAC;
  --gray-7: #DCFCE7;

  /* 透明度变量 */
  --overlay: rgba(240, 253, 244, 0.9);
  --shadow: rgba(22, 163, 74, 0.1);
}
```

```css
/* 教育清新 - 深色主题 */
[data-theme="dark"] {
  --bg: #052E16;
  --fg: #F0FDF4;
  --bg-secondary: #14532D;
  --accent: #22C55E;
  --accent-secondary: #60A5FA;
  --overlay: rgba(5, 46, 22, 0.9);
  --shadow: rgba(34, 197, 94, 0.2);
}
```

**教育场景配色特点**：

- 以绿色系为主，营造自然舒适的学习氛围
- 深绿色用于标题，增强可读性
- 浅绿色用于背景，舒缓眼睛疲劳
- 蓝色作为辅助色，用于交互元素

---

## 📊 数据专业（Data Professional）

适合场景：数据分析报告、市场研究报告、运营报告、财务报告、行业分析

风格定位：专业严谨、数据密集、图表突出、洞察清晰

```css
/* 数据专业 - 深色主题 */
:root {
  /* 背景与前景 */
  --bg: #0D1117;
  --fg: #E6EDF3;
  --bg-secondary: #161B22;

  /* 强调色 - 数据蓝 */
  --accent: #58A6FF;
  --accent-light: #388BFD;
  --accent-dark: #79C0FF;

  /* 图表色板 */
  --chart-1: #58A6FF;
  --chart-2: #3FB950;
  --chart-3: #F78166;
  --chart-4: #D29922;
  --chart-5: #A371F7;
  --chart-6: #DB61A2;

  /* 功能色 */
  --success: #3FB950;
  --warning: #D29922;
  --error: #F85149;
  --info: #58A6FF;

  /* 灰度阶梯 */
  --gray-1: #E6EDF3;
  --gray-2: #C9D1D9;
  --gray-3: #8B949E;
  --gray-4: #6E7681;
  --gray-5: #484F58;
  --gray-6: #30363D;
  --gray-7: #21262D;

  /* 透明度变量 */
  --overlay: rgba(13, 17, 23, 0.9);
  --shadow: rgba(88, 166, 255, 0.15);
}
```

```css
/* 数据专业 - 浅色主题 */
[data-theme="light"] {
  --bg: #FFFFFF;
  --fg: #1F2328;
  --bg-secondary: #F6F8FA;
  --accent: #0969DA;
  --chart-1: #0969DA;
  --chart-2: #1A7F37;
  --chart-3: #CF222E;
  --chart-4: #9A6700;
  --chart-5: #8250DF;
  --chart-6: #BF3989;
  --overlay: rgba(255, 255, 255, 0.9);
  --shadow: rgba(9, 105, 218, 0.1);
}
```

**数据场景配色特点**：

- 深色背景为主，减少视觉疲劳，方便长时间阅读数据
- 提供6色图表色板，确保多数据系列的可区分性
- 蓝色为主色调，突出专业感
- 绿/红/黄分别表示增长/下降/警告状态

---

## 🎨 创意艺术（Creative Art）

适合场景：艺术展示、创意演讲、个人分享、设计作品集、摄影作品

风格定位：个性鲜明、艺术感强、打破常规、视觉冲击力

```css
/* 创意艺术 - 多彩主题 */
:root {
  /* 背景与前景 */
  --bg: #0C0A09;
  --fg: #FAFAF9;
  --bg-secondary: #1C1917;

  /* 强调色 - 多彩渐变 */
  --accent: #F97316;
  --accent-secondary: #EC4899;

  /* 渐变背景 */
  --gradient-primary: linear-gradient(135deg, #F97316 0%, #EC4899 50%, #8B5CF6 100%);
  --gradient-secondary: linear-gradient(135deg, #06B6D4 0%, #3B82F6 50%, #8B5CF6 100%);

  /* 功能色 */
  --success: #22C55E;
  --warning: #EAB308;
  --error: #EF4444;
  --info: #06B6D4;

  /* 灰度阶梯 */
  --gray-1: #FAFAF9;
  --gray-2: #F5F5F4;
  --gray-3: #D6D3D1;
  --gray-4: #A8A29E;
  --gray-5: #78716C;
  --gray-6: #57534E;
  --gray-7: #44403C;

  /* 透明度变量 */
  --overlay: rgba(12, 10, 9, 0.85);
  --shadow: rgba(249, 115, 22, 0.2);
  --glow: rgba(236, 72, 153, 0.3);
}
```

```css
/* 创意艺术 - 浅色变体 */
[data-theme="light"] {
  --bg: #FAFAF9;
  --fg: #1C1917;
  --bg-secondary: #F5F5F4;
  --overlay: rgba(250, 250, 249, 0.9);
  --shadow: rgba(249, 115, 22, 0.15);
  --glow: rgba(236, 72, 153, 0.2);
}
```

**创意场景配色特点**：

- 使用多彩渐变背景，增加视觉冲击力
- 橙色和粉色作为主强调色，活泼有创意
- 紫色作为辅助色，增添神秘艺术感
- 可根据具体作品风格调整强调色

---

## 主题色快速对照表

| 主题名称 | 主色 | 辅色 | 适合场景 | 背景风格 |
|----------|------|------|----------|----------|
| 墨水经典 | #2563EB（蓝） | #1D4ED8（深蓝） | 商务通用 | 浅/深 |
| 政务庄重 | #C41E3A（中国红） | #FFD700（金） | 传统政务汇报 | 浅色为主 |
| 政务科技 | #0369A1（科技蓝） | #6366F1（紫） | 智慧城市、科技政务 | 浅蓝为主 |
| 科技未来 | #06B6D4（青） | #8B5CF6（紫） | 科技产品 | 深色为主 |
| 教育清新 | #16A34A（绿） | #3B82F6（蓝） | 教育培训 | 浅色为主 |
| 数据专业 | #58A6FF（蓝） | #3FB950（绿） | 数据分析 | 深色为主 |
| 创意艺术 | #F97316（橙） | #EC4899（粉） | 艺术展示 | 深色为主 |

---

## 使用注意事项

### 1. 主题色不可自定义

本Skill采用预设主题色方案，**不允许用户自定义hex值**。这是为了保护视觉风格的一致性和专业性。

如果用户有特殊需求，请在预设主题中选择最接近的方案，然后通过调整透明度、明度等方式进行微调。

### 2. 浅色/深色主题交替使用

每2-3页应切换一次主题（浅色/深色），避免连续超过3页使用相同主题。切换时WebGL背景会在两个颜色之间渐变过渡。

### 3. 强调色的谨慎使用

强调色（--accent）应该只用于：

- 重要数据数字
- 核心观点标题
- CTA按钮和链接
- 图表中的关键数据点

避免在页面大面积使用强调色，以免喧宾夺主。

### 4. 功能色的语义一致性

无论选择哪个主题，功能色的语义应该保持一致：

- 绿色（--success）：表示正面增长、完成状态
- 红色（--error）：表示负面下降、错误状态
- 黄色（--warning）：表示警告、注意状态
- 蓝色（--info）：表示信息、提示状态

### 5. 透明度的合理使用

透明度变量（--overlay、--shadow）用于：

- --overlay：遮罩层、模态框背景
- --shadow：元素阴影、卡片边框
- --glow（科技/创意主题）：发光效果

合理使用透明度可以增加层次感，但过度使用会显得杂乱。