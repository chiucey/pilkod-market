# 浏览器打印 PDF 设置详解

## Chrome / Edge 设置

```
1. 按 Ctrl + P 打开打印对话框
2. 目标打印机选择「另存为 PDF」
3. 布局选择「横向」
4. 边距选择「无」
5. 缩放选择「100%」（不得选「适合页面」）
6. 点击「更多设置」→ 勾选「背景图形」
7. 纸张大小手动输入：
   - 宽度：338.67mm
   - 高度：190.5mm
8. 点击保存
```

## Firefox 设置

```
1. 按 Ctrl + P 打开打印对话框
2. 打印到 PDF 选择「另存为 PDF」
3. 页面大小选择「自定义」
4. 宽度 338.67mm，高度 190.5mm
5. 边距选择「无」
6. 缩放默认或 100%
7. 勾选「打印背景颜色和图像」
```

## 常见打印问题

### 问题：PDF 尺寸与预期不符

**原因**：浏览器默认纸张为 A4，与 16:9 不匹配

**解决**：必须手动设置纸张大小为 338.67mm × 190.5mm

### 问题：图表在打印预览中显示正常，但 PDF 中空白

**原因**：Canvas 未正确渲染

**解决**：
```javascript
// 确保在打印前刷新图表
window.addEventListener('beforeprint', () => {
  charts.forEach(chart => {
    chart.resize();
    chart.update('none');
  });
});
```

### 问题：内容被截断

**原因**：高度未锁定

**解决**：在 @media print 中设置：
```css
.slide {
  height: 190.5mm;
  min-height: 190.5mm;
  max-height: 190.5mm;
  overflow: hidden;
}
```
