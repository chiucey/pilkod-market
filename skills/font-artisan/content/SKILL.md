---
name: font-artisan
description: Handle font glyph extraction to SVG, format conversion (Type 1/PFB to OTF/WOFF2), font merging (e.g., merging Latin with CJK fonts), and font metrics tuning (vertical metrics, line height, and monospacing adjustments). Trigger this skill when the user needs to merge fonts, fix line height issues, or extract icons/glyphs from font files.
---

# font-artisan

处理字体的提取、转换、合并及度量调优。

## 触发条件
- 用户请求从字体中提取特定字符为 SVG。
- 用户需要转换旧式字体格式（如 PFB/Type 1）为现代 Web 格式（OTF, TTF, WOFF2）。
- 用户需要合并两个字体，并解决合并后的宽度（等宽性）或行高（垂直度量）不匹配问题。

## 核心能力

### 1. 字符提取 (Glyph to SVG)
使用 `fontTools` 提取单个字符的矢量路径。
- **关键点**：必须计算正确的 `viewBox`。高度通常为 `ascender - descender`，宽度从 `hmtx` 表获取。
- **坐标转换**：字体坐标系 Y 轴向上，SVG 坐标系 Y 轴向下，需进行 `scale(1, -1)` 变换。

### 2. 格式转换 (Format Conversion)
- **Type 1 (PFB) -> OTF**：优先使用 `fontforge`。
- **OTF/TTF -> WOFF2**：使用 `fontTools` 的 `save` 方法并设置 `flavor='woff2'`。

### 3. 字体合并 (Font Merging)
使用 `fontforge` 进行深度合并。
- **EM Size 统一**：合并前必须将两个字体的 `em` 设置为一致（通常以中文字体为准）。
- **范围替换**：通过 `selection.select` 选择 Unicode 范围（如 `0x20-0xFF`）进行复制粘贴。
- **度量同步**：若以西文字体为行高基准，需在合并后将 `ascent`, `descent`, `os2_typoascent` 等垂直度量值强制设为西文字体的值。
- **等宽强制**：遍历 Unicode 范围，强制将 `glyph.width` 设置为基准宽度（如西文为半宽，中文为全宽）。

### 4. 度量调优 (Metrics Tuning)
解决“行高过大”或“字符错位”：
- **垂直度量**：检查 `hhea` 和 `OS/2` 表中的 `Ascender`, `Descender`, `LineGap`。
- **等宽一致性**：确保西文宽度正好是中文宽度的一半（或根据需求设为一致）。

## 推荐工具栈
- `fontTools` (Python 库)：适合路径处理、WOFF2 压缩、元数据修改。
- `fontforge` (命令行/Python 模块)：适合格式转换、复杂合并、度量计算。

## 示例脚本结构
### 提取 SVG
```python
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
# ... 加载字体，获取 glyph，绘制路径，计算坐标并保存 ...
```

### 合并与调整
```python
import fontforge
base = fontforge.open("base.ttf")
source = fontforge.open("latin.ttf")
source.em = base.em
# ... 执行复制粘贴 ...
# 还原垂直度量以控制行高
base.ascent = source.ascent
base.os2_typoascent = source.os2_typoascent
# ... 保存结果 ...
```
