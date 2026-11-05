# PptxGenJS API 速查

## 基础使用

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';

const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

slide.addText("标题", {
  x: 0.5, y: 0.5, w: 9, h: 1,
  fontSize: 32, fontFace: "Microsoft YaHei",
  color: "22223b", bold: true
});

pres.writeFile({ fileName: "output.pptx" })
  .then(() => console.log("Done"));
```

---

## 形状 (Shapes)

### 常用形状
- `pres.shapes.RECTANGLE` - 矩形
- `pres.shapes.ROUNDED_RECTANGLE` - 圆角矩形
- `pres.shapes.OVAL` - 椭圆
- `pres.shapes.LINE` - 线条

### 形状属性
```javascript
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 2, h: 1.5,
  fill: { color: "FFFFFF" },
  line: { color: "000000", width: 1 },
  rectRadius: 0.1,
  shadow: { type: "outer", blur: 4, offset: 2, angle: 45, opacity: 0.2 }
});
```

---

## 文字 (Text)

```javascript
slide.addText("文本内容", {
  x: 1, y: 2, w: 8, h: 1,
  fontSize: 18,
  fontFace: "Microsoft YaHei",
  color: "333333",
  bold: true,
  align: "center",
  valign: "middle",
  wrap: "square"
});
```

---

## 尺寸参考

| 属性 | 值 | 说明 |
|------|-----|------|
| 页面尺寸 | 10" x 5.625" | LAYOUT_16x9 |
| 颜色格式 | 6位hex无# | "FF0000" |

---

## 常用位置

| 位置 | x | y | w | h |
|------|---|---|---|---|
| 全屏背景 | 0 | 0 | 10 | 5.625 |
| 标题 | 0.5 | 0.3 | 9 | 0.8 |
| 正文区 | 0.5 | 1.2 | 9 | 3.8 |
| 页码徽章 | 9.3 | 5.1 | 0.4 | 0.4 |
