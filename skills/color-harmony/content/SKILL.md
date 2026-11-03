---
name: color-harmony
description: 科学色彩搭配技能。当用户要求配色方案、颜色搭配、色彩组合、设计配色或输入颜色代码（如 HEX、RGB）并希望获得和谐的色彩搭配方案时使用。支持1-5种颜色的搭配生成。
---

# 科学色彩搭配技能

## 核心能力

基于色彩理论（色轮关系），从用户输入的主颜色自动生成科学和谐的色彩搭配方案。

## 触发条件

当用户提到以下关键词时激活：
- 配色 / 配色方案
- 颜色搭配 / 色彩搭配 / 色彩组合
- 给我一个/几种颜色
- HEX / RGB / HSL 颜色码
- 设计配色 / UI配色

## 输入格式

用户可输入以下任意颜色格式：
- HEX: `#FF5733` 或 `FF5733`
- RGB: `rgb(255, 87, 51)` 或 `255, 87, 51`
- HSL: `hsl(11, 100%, 60%)` 或 `11, 100, 60`

同时指定需要搭配数量（1-5种），如不指定则提供完整5种方案。

## 色彩理论算法

### 搭配类型定义

| 搭配类型 | 色轮角度差 | 适用场景 |
|---------|----------|---------|
| **互补色** | 180° | 高对比、强调重点 |
| **类似色** | ±30° | 和谐、柔和、渐进 |
| **三角配色** | 120°×3 | 平衡、活力 |
| **分裂互补** | 180°±30° | 互补+类似结合 |
| **双分裂互补** | 90°±30° | 复杂、和谐 |
| **中性色** | 30°内 | 背景、衬托 |

### 色彩转换函数

```
HEX → RGB: 每2位转为10进制
RGB → HSL: 标准转换算法
HSL → HEX: 标准转换算法
```

### 搭配生成逻辑

1. **解析输入**：识别颜色格式并转换为HSL
2. **生成变体**：基于HSL生成各搭配类型
3. **验证对比度**：确保搭配有足够可读性
4. **排序输出**：按对比度从高到低排列

## 输出格式

### 用户界面展示

```
┌─────────────────────────────────────────────────┐
│  🎨 科学色彩搭配结果                              │
├─────────────────────────────────────────────────┤
│  主色: #FF5733                                  │
│  HSL: hsl(11°, 100%, 60%)                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  🌈 互补色搭配 (180°)                            │
│  ┌────┐ ┌────┐                                 │
│  │████│ │████│  #FF5733 + #57FF33              │
│  └────┘ └────┘                                 │
│  高对比度，适合强调重点                          │
│                                                 │
│  🌈 类似色搭配 (30°)                             │
│  ┌────┐ ┌────┐ ┌────┐                          │
│  │████│ │████│ │████│  #FF5733 + #FF8A57 + ... │
│  └────┘ └────┘ └────┘                          │
│  柔和过渡，自然和谐                              │
│                                                 │
│  [继续展示其他搭配类型...]                       │
└─────────────────────────────────────────────────┘
```

### 颜色卡片展示

每个搭配包含：
- 颜色色块预览（可视化方块）
- 精确HEX代码（可复制）
- RGB值
- HSL值
- 搭配说明与适用场景

## 质量标准

1. **准确性**：所有颜色转换必须精确
2. **实用性**：提供真实可用的设计建议
3. **可读性**：界面清晰，颜色信息完整
4. **对比度**：确保搭配满足WCAG可访问性标准

## 脚本实现

### scripts/color_theory.js

```javascript
// HSL颜色转换工具
function hexToHsl(hex) {
  // HEX to RGB
  let r = parseInt(hex.slice(1, 3), 16) / 255;
  let g = parseInt(hex.slice(3, 5), 16) / 255;
  let b = parseInt(hex.slice(5, 7), 16) / 255;

  const max = Math.max(r, g, b), min = Math.min(r, g, b);
  let h, s, l = (max + min) / 2;

  if (max === min) {
    h = s = 0;
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }
  return { h: h * 360, s: s * 100, l: l * 100 };
}

function hslToHex(h, s, l) {
  s /= 100; l /= 100;
  const a = s * Math.min(l, 1 - l);
  const f = n => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color).toString(16).padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

// 色彩搭配生成
const harmonyTypes = {
  complementary: (h, s, l) => [{ h: h, s: s, l: l }, { h: (h + 180) % 360, s: s, l: l }],
  analogous: (h, s, l) => [
    { h: (h - 30 + 360) % 360, s: s, l: l },
    { h: h, s: s, l: l },
    { h: (h + 30) % 360, s: s, l: l }
  ],
  triadic: (h, s, l) => [
    { h: h, s: s, l: l },
    { h: (h + 120) % 360, s: s, l: l },
    { h: (h + 240) % 360, s: s, l: l }
  ],
  splitComplementary: (h, s, l) => [
    { h: h, s: s, l: l },
    { h: (h + 150) % 360, s: s, l: l },
    { h: (h + 210) % 360, s: s, l: l }
  ],
  tetradic: (h, s, l) => [
    { h: h, s: s, l: l },
    { h: (h + 90) % 360, s: s, l: l },
    { h: (h + 180) % 360, s: s, l: l },
    { h: (h + 270) % 360, s: s, l: l }
  ]
};

function generateHarmony(inputColor, count = 5) {
  const hsl = hexToHsl(inputColor);
  const results = [];

  // 根据数量选择搭配类型
  const typeMap = { 1: 'complementary', 2: 'analogous', 3: 'triadic', 4: 'tetradic', 5: 'splitComplementary' };
  const type = typeMap[Math.min(count, 5)] || 'triadic';

  const colors = harmonyTypes[type](hsl.h, hsl.s, hsl.l);
  return colors.map(c => ({
    hex: hslToHex(c.h, c.s, c.l),
    rgb: hexToRgb(hslToHex(c.h, c.s, c.l)),
    hsl: c
  }));
}
```

## 验证规则

1. 输入必须为有效颜色格式
2. 数量范围：1-5
3. 输出颜色必须符合色彩理论关系
4. 提供WCAG对比度检查（建议≥4.5:1）
