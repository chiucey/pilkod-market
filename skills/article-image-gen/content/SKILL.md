---
name: article-image-gen
description: 根据微信公众号文章内容，生成配图。使用 image_synthesize 工具生成适合公众号风格的图片。触发条件：用户说"生成配图"、"帮我配图"、"给文章配图"、"插入图片"。
---

# article-image-gen 公众号文章配图生成

## 用户风格偏好

- 积极阳光，明亮温暖，避免阴暗沉重感
- 适配公号封面图，比例为16:9

## 配图格式规范

- 在文章可以配图的地方配图
- 每篇配图3张，其中1张为标讯真实数据截图

## 生成参数

- 分辨率：2K
- 图片比例：16:9
- 使用 image_synthesize 工具生成图片

## 数据截图提示词模板（图1）

```
A clean professional Chinese government procurement notice screenshot,
white background, official document style.

【来源网站 · 日期】

招标单位：XXX
预算金额：XXX万元
核心采购内容：
• XXX
来源：URL

Clean official table layout, authentic government document aesthetic
```

## 输出格式

每张图附带：
- 图片
- 插入位置：文章第X段后
- 说明：图片内容描述

## 发送方式

使用 message 工具发送图片（media参数）给企业微信 wangpei
