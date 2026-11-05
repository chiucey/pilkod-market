# PPT编辑工作流

## 场景识别

当用户要求修改PPT时，首先判断意图：

| 意图 | 关键词 | 处理方式 |
|------|--------|----------|
| **新增PPT** | "生成PPT"、"制作PPT" | 进入新增流程 |
| **编辑PPT** | "编辑PPT"、"修改PPT" | 进入编辑流程 |
| **仅修改某页** | "第X页"、"改一下第3页" | 定位目标页，仅修改指定页 |

---

## 编辑流程

```
1. 定位目标页 → 2. 分析修改需求 → 3. 仅修改指定页 → 4. 保持其他页不变
```

---

## 修改类型

### 1. 修改页面标题
```javascript
slide.addText("新标题", {
  x: 0.5, y: 0.3, w: 9, h: 0.8,
  fontSize: 32, fontFace: "Microsoft YaHei",
  color: theme.primary, bold: true
});
```

### 2. 修改内容要点
```javascript
slide.addText("新内容", {
  x: x, y: y, w: w, h: h,
  fontSize: 14, fontFace: "Microsoft YaHei",
  color: theme.secondary
});
```

### 3. 修改配色
```javascript
const theme = {
  ...theme,
  primary: "新主色",
  accent: "新强调色"
};
```

---

## 注意事项

1. **仅修改指定页**：其他页面保持不变
2. **保持风格一致**：修改后与其他页面风格统一
3. **重新打包**：修改完成后生成新的PPTX文件
