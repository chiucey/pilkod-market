---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022033596459d808f02ddd0fb77d9f850fac4d893718f7ed079ee078b648c3b6ace60221008cd0f97805a51a90ea6a083fffacd68ed0326136a02572eb426b66eff4519734
    ReservedCode2: 3044022061d9027c0dedcb7d394d91835a9a5971a8f0aa4cd1a366fd0769cae829cc4feb0220433b7995ce1b156b884919505bed2606c9683d9a29e7f29603ca61b3ae6ef207
---

# 配色提取指南

## 常用配色系统

### 1. 主色/辅色/强调色 比例 (60-30-10法则)
- 主色：60% - 页面的主导颜色
- 辅色：30% - 次要元素
- 强调色：10% - CTA按钮、重要提示

### 2. 色彩模式

| 模式 | 描述 | 适用场景 |
|------|------|----------|
| 单色系 | 同一色相不同明度 | 高端、简约 |
| 邻近色 | 色轮上相邻的颜色 | 和谐、自然 |
| 互补色 | 色轮对面 | 强调、对比 |
| 分裂互补 | 互补色两侧 | 平衡对比 |
| 三角色 | 均匀分布的三角 | 丰富、多彩 |

### 3. 常用色彩工具

- **Coolors**: https://coolors.co
- **Colormind**: http://colormind.io
- **Material Design Colors**: https://material.io/resources/color

### 4. 无障碍对比度

WCAG 2.1 标准：
- AA级：文字与背景对比度 ≥ 4.5:1
- AAA级：文字与背景对比度 ≥ 7:1
- 大文字(>18px)：对比度 ≥ 3:1

### 5. 配色提取流程

```
1. 分析页面主色调
2. 识别强调色（CTA、链接、图标）
3. 检测渐变使用
4. 计算比例分布
5. 输出标准化色值
```

### 6. CSS渐变模式

```css
/* 线性渐变 */
background: linear-gradient(90deg, #color1 0%, #color2 100%);

/* 径向渐变 */
background: radial-gradient(circle, #color1 0%, #color2 100%);

/* 多色渐变 */
background: linear-gradient(45deg, #color1 0%, #color2 50%, #color3 100%);
```

## 设计风格色彩趋势

### 2024-2025趋势色
- 柔和粉彩（Pastel）
- 活力渐变（Vibrant Gradients）
- 深色模式原生色（Dark Mode Native）
- 自然灵感色（Nature-inspired）
- 复古霓虹（Retro Neon）
