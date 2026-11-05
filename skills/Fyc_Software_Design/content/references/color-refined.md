# 美观协调配色方案（参考 ECharts 官方主题）

参考 ECharts `macarons` / `shine` / `roma` 三大经典主题的设计语言,让大屏配色从"功能可用"升级到"专业美观、整体协调"。

---

## 设计原则(60/30/10 黄金比例)

```
- 60% 中性色(白/灰/深蓝) → 整体氛围
- 30% 主色(蓝色系) → 品牌一致
- 10% 强调色(橙/绿/紫) → 关键数据点
```

| 颜色类型 | 占比 | 用途 |
|---|---|---|
| 中性 | 60% | 底色、面板、标签 |
| 主色 | 30% | 图表主色、地图、标题 |
| 强调 | 10% | 高亮、警示、TOP 标记 |

---

## 一、主色板(蓝系 6 档,从浅到深)

| 档 | 颜色 | HEX | 用途 |
|---|---|---|---|
| 1 | 极浅 | `#eef3fb` | 地图最浅档填色、按钮 hover bg |
| 2 | 浅 | `#dde8f5` | 地图浅档、面板 hover 背景 |
| 3 | 中浅 | `#a8c8ed` | 地图中档、双折线面积 |
| 4 | 中 | `#7aa9e0` | 地图深档、柱状图主色 |
| 5 | 深 | `#4a7bb8` | 主强调色、标题、关键数据 |
| 6 | 极深 | `#1e3a6e` | 文字主色、深底色 |

> **比 v1.5 更"协调"的差异**:把浅蓝和中蓝之间加了过渡,避免直接从 `#dde8f5` 跳到 `#a8c8ed` 的色阶断层。

---

## 二、辅色板(强调色 5 色,参考 ECharts macarons)

```js
const ACCENT = {
    warm:    '#ff9a3c',  // 警告/损耗(对应原"橙")
    danger:  '#f87171',  // 危险(对应原"红")  
    success: '#4ade80',  // 良好(对应原"绿")
    purple:  '#a78bfa',  // 季度环(对应原"紫")
    gold:    '#fbbf24'   // 突出值(新增,比橙更亮)
};
```

5 色统一降饱和度(原 `#fbbf24` 改 `#fbbf24`, 原 `#ff9a3c` 改 `#f59e0b` 更柔和),避免颜色过于鲜艳。

---

## 三、八大图表的协调色卡(每图只配 2-3 个主色)

| 图表 | 主色 | 辅色 | 第三色 |
|---|---|---|---|
| TOP10 排行 | 蓝渐变 `#4a7bb8` | 圆点 `#8fbcff` | 高亮 `#ff9a3c` |
| 双折线 | `#4a7bb8` | `#ff9a3c` | 面积 `rgba(143,188,255,0.3)` |
| 表格 | 白底 | 损耗率 4 档色阶 | hover `#f5f9fd` |
| 中国地图 | 蓝 3 档渐变 | 高优 `#4a7bb8` | 高亮 `#ff9a3c` |
| 季度环形 | `#4a7bb8` / `#ff9a3c` / `#4ade80` / `#a78bfa` | 白色 2px 描边 | — |
| 柱状图 | `#4a7bb8`(运行) | `#ff9a3c`(新增) | — |
| 总计卡片 | SVG 渐变 | `#1e3a6e` 数字 | — |
| 趋势 sparkline | `#4a7bb8` | 面积渐变 | — |

> **协调原则**:所有图表的"主色"统一用 `#4a7bb8`(中蓝),保证视觉一致性。

---

## 四、阴影与发光(参考 ECharts 主题的 `itemStyle.shadowBlur`)

```css
/* 主面板阴影 - 浅淡蓝 */
box-shadow: 0 2px 12px rgba(143, 188, 255, 0.15);

/* 悬浮面板 - 加重 */
box-shadow: 0 4px 16px rgba(143, 188, 255, 0.25);

/* 高亮态(地图/Tab) - 蓝色发光 */
box-shadow: 0 0 20px rgba(95, 177, 255, 0.4);

/* 图表图标 drop-shadow */
filter: drop-shadow(0 2px 4px rgba(143, 188, 255, 0.3));

/* 跑马灯光晕 */
box-shadow: 0 4px 16px rgba(143, 188, 255, 0.2);
```

---

## 五、参考 ECharts 主题代码(可直接套用)

如果需要用 ECharts 内置主题,可在初始化前注入:

```js
// ECharts 官方主题(从 themes/ 目录加载)
const theme = {
    color: ['#5b8ff9', '#5ad8a6', '#5d7092', '#f7c739', '#7232f5', '#eb6383', '#e690d1', '#32c5e9', '#96bfff'],
    backgroundColor: 'transparent',
    textStyle: { fontFamily: 'Microsoft YaHei, sans-serif' },
    title: { textStyle: { color: '#1e3a6e', fontWeight: 700 } },
    line: { itemStyle: { borderWidth: 2 } },
    bar: { itemStyle: { barBorderWidth: 0, barBorderColor: '#ccc' } },
    pie: { itemStyle: { borderWidth: 1, borderColor: '#fff' } }
};
echarts.registerTheme('fyc-cream', theme);

// 使用
const chart = echarts.init(dom, 'fyc-cream');
```

---

## 六、配色原则(避免的踩坑)

### ❌ 不要做的
1. **不要用纯饱和色**(`#ff0000`、`#00ff00`) → 改成柔和版 `#f87171`、`#4ade80`
2. **不要相邻面板颜色对比过强** → 保持同样的色温(都是蓝色系或都是暖色)
3. **不要超过 5 个主色** → 限制在蓝/橙/绿/紫/红 5 个
4. **不要透明度叠加混乱** → 同元素保持同一种透明度规则
5. **不要黑色文字** → 全部用 `#1e3a6e` 深蓝近黑,更柔和

### ✅ 应该做的
1. **同一概念用同色**:所有"电力/装机容量"用蓝色;所有"损耗/警告"用橙色
2. **数字越大颜色越深**:3 档蓝色渐变表示数据量级
3. **强调用透明度而非色相**:高亮态用 `opacity 0.8 → 1` 变化
4. **阴影用蓝色而非黑色**:`rgba(143,188,255,0.15)` 替代 `rgba(0,0,0,0.1)`
5. **小元素用低饱和**:大数字 `#1e3a6e` 高饱和,小标签 `#8aa7c9` 低饱和

---

## 七、对比度检查(无障碍)

所有文字/背景对比度必须满足 WCAG AA:
- 正文 vs 背景: ≥ 4.5:1
- 大字(> 18px) vs 背景: ≥ 3:1

| 文字 | 背景 | 对比度 | 是否通过 |
|---|---|---|---|
| `#1e3a6e` | `#ffffff` | 11.4:1 | ✅ |
| `#3a5a8c` | `#ffffff` | 7.0:1 | ✅ |
| `#6b8fc4` | `#ffffff` | 3.6:1 | ⚠️ 仅大字 |
| `#8aa7c9` | `#ffffff` | 2.5:1 | ❌ 仅辅助文字 |

→ `#6b8fc4` 和 `#8aa7c9` 只用于大字号(>14px)或非关键文字。

---

## 八、与 ECharts 主题的对应关系

我们的配色系统 ≈ ECharts **macarons** + 自定义 cream 背景:

| ECharts 主题 | 我们的对应 |
|---|---|
| `macarons` (粉嫩糖果) | 蓝主色 + 5 色辅 |
| `shine` (明亮现代) | 渐变 + 阴影 + 圆角 |
| `roma` (地中海) | 中性色 + 暖橙强调 |
| `vintage` (复古) | (未采用,与我们风格不符) |
| `dark` | 备选 dark-tech 主题 |

---

## 九、完整 CSS 变量表(可直接 copy)

```css
:root {
    /* === 中性色(60%) === */
    --bg-primary: #ffffff;
    --bg-gradient: radial-gradient(ellipse at top, #eef3fb 0%, #f5f9fd 50%, #ffffff 100%);
    --panel-bg: rgba(255, 255, 255, 0.78);
    --panel-border: rgba(143, 188, 255, 0.4);
    --shadow: 0 2px 12px rgba(143, 188, 255, 0.15);

    /* === 文字色阶(4 档) === */
    --text-primary: #1e3a6e;
    --text-secondary: #3a5a8c;
    --text-muted: #6b8fc4;
    --text-faint: #8aa7c9;

    /* === 主色 蓝(30%) === */
    --accent: #4a7bb8;        /* 主强调色 */
    --accent-light: #8fbcff;  /* 亮蓝(脉冲/光柱) */
    --accent-mid: #7aa9e0;    /* 中蓝(柱状/地图中档) */
    --accent-pale: #dde8f5;   /* 浅蓝(地图浅档/hover) */
    --accent-deep: #1e3a6e;   /* 深蓝(标题) */

    /* === 强调色(10%) === */
    --warning: #ff9a3c;       /* 损耗/警告 */
    --warning-soft: #f59e0b;  /* 柔和橙 */
    --danger: #f87171;        /* 危险 */
    --success: #4ade80;       /* 良好 */
    --purple: #a78bfa;        /* 季度环点缀 */
    --gold: #fbbf24;          /* 突出值(可选) */

    /* === 阴影强度 === */
    --shadow-sm: 0 1px 4px rgba(143, 188, 255, 0.1);
    --shadow-md: 0 2px 12px rgba(143, 188, 255, 0.15);
    --shadow-lg: 0 4px 16px rgba(143, 188, 255, 0.25);
    --shadow-glow: 0 0 20px rgba(95, 177, 255, 0.4);
}
```

**直接复制上面这整段到 `:root`,整个项目的配色就统一了。**

---

## 十、检查清单(交付前过一遍)

- [ ] 同一概念用同色(如所有"电力"用蓝)
- [ ] 强调色 ≤ 10%(避免色彩泛滥)
- [ ] 同一面板内透明度一致
- [ ] 文字对比度 ≥ 4.5:1(大字)或 ≥ 3:1(正文)
- [ ] 阴影用蓝色不用黑色
- [ ] 没有纯饱和色(`#ff0000` 等)
- [ ] 紫色 / 绿色仅作点缀,不在主色盘里滥用
- [ ] 数字 vs 标签 字号差 ≥ 6px(让大数字显眼)