---
description: 生成黑白风格的ER实体关系图。当用户要求绘制数据库ER图、实体属性图、方框圆形椭圆连线图表时使用。
name: er-diagram-generator
---

# ER实体关系图生成器

使用 AI 图像生成黑白风格的实体关系图。

## 执行流程

1. **接收需求**：确定需要的ER图内容（实体、属性、关系）
2. **AI 生成图像**：使用 image_synthesize 工具生成黑白风格的ER图
3. **保存文件**：输出为 .png 文件到工作目录

## 提示词模板

```
Black and white entity-relationship diagram (ER diagram) on white background, showing database tables with rectangles for entities, ovals for attributes, lines connecting them, clean technical diagram style, minimalist black lines only
```
