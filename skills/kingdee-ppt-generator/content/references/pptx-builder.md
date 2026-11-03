# 金蝶 PPT 技术构建规范 PPTX Builder

> 基于官方模板 2026 版

---

## 1. 构建脚本标准模板

```javascript
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3333" × 7.5"
pres.defineLayout({ name: "CUSTOM", width: 13.3333, height: 7.5 });
pres.layout = "CUSTOM";
```

## 2. 资源加载

```javascript
const fs = require("fs");
const path = require("path");

function loadAsset(filename) {
  const filePath = path.join(__dirname, "assets", filename);
  return fs.readFileSync(filePath, "base64");
}

const A = {
  BG_COVER: loadAsset("bg_cover.jpeg"),
  BG_TOC: loadAsset("bg_toc.png"),
  BG_SEC_A: loadAsset("bg_section_a.jpeg"),
  BG_SEC_B: loadAsset("bg_section_b.jpeg"),
  BG_SEC_C: loadAsset("bg_section_c.jpeg"),
  BG_CLOSING: loadAsset("bg_closing.jpeg"),
  CLOSING_THANKS: loadAsset("closing_thanks.png"),
  LOGO_C: loadAsset("logo_color.png"),
  LOGO_W: loadAsset("logo_white.png"),
};
```

## 3. Shadow 工厂函数

```javascript
const mkSh = () => ({ blur: 12, offset: 3, angle: 135, color: "000000", opacity: 0.10 });
const mkShS = () => ({ blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.07 });
const mkShB = () => ({ blur: 16, offset: 6, angle: 135, color: "1770EA", opacity: 0.12 });
```

## 4. 辅助函数

```javascript
function addLogo(slide, onDark) {
  slide.addImage({
    data: onDark ? A.LOGO_W : A.LOGO_C,
    x: 12.250, y: 0.187, w: 0.849, h: 0.433,
  });
}

function addFooter(slide, pageNum, onDark) {
  if (!onDark) {
    slide.addText("④ 内部公开 请勿外传", {
      x: 11.355, y: 7.017, w: 1.327, h: 0.190,
      fontSize: 8, color: "BFBFBF", fontFace: "Microsoft YaHei", margin: 0,
    });
  }
  slide.addText(String(pageNum), {
    x: 12.845, y: 7.051, w: 0.384, h: 0.150,
    fontSize: 10, color: onDark ? "FFFFFF" : "2971EB",
    align: "right", fontFace: "Microsoft YaHei", bold: false, margin: 0,
  });
}

function addContentTitle(slide, title, subtitle) {
  slide.addText(title, {
    x: 0.435, y: 0.230, w: 10.601, h: 0.513,
    fontSize: 24, color: "373838", bold: true, fontFace: "Microsoft YaHei",
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.435, y: 0.747, w: 8.523, h: 0.312,
      fontSize: 16, color: "BFBFBF", fontFace: "Microsoft YaHei",
    });
  }
}
```

## 5. 颜色序列

```javascript
const COLOR_SEQ = ["2971EB", "22AAFE", "05C8C8", "966EFF", "FFB61A"];
```

## 6. 执行命令序列

```bash
# 1. 生成 PPTX
cd /home/claude && node build_pptx.js

# 2. 转 PDF
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf output.pptx

# 3. 转预览图
pdftoppm -jpeg -r 150 output.pdf slide

# 4. 视觉 QA
# 5. 修复后重新执行 1-4
# 6. 交付
```

## 7. 视觉 QA 清单

| 类别 | 检查项 |
|------|-------|
| **Logo** | 白底页→彩色logo；蓝底页→反白logo |
| **页脚** | 页码右下角；内容页左下角有保密声明 |
| **封面** | 主标题在 y=2.247"；无Logo |
| **目录** | 大号序号蓝色左对齐 |
| **章节页** | 大数字125pt #00CCFE |
| **内容页** | 标题无竖线；内容从 y=1.503" 开始 |
| **对比度** | 蓝底页文字为白色 |
| **溢出** | 无文字超出文本框边界 |

## 8. 绝对禁止事项

| 错误做法 | 正确做法 |
|---------|---------|
| Hex色值加 `#` 号 | color: "2971EB" (不加#) |
| 复用 shadow 对象 | 使用工厂函数：`const mkSh = () => ({...})` |
| 错误幻灯片尺寸 | 使用 LAYOUT_WIDE |
| 封面/结尾页放Logo | 不添加 |
| 内容页标题加左侧竖线 | 不添加 |
