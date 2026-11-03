# 快速参考卡片

## 常用命令速查

### PPT生成

```javascript
// 使用 pptx-generator 技能
// 创建封面页
slide.addText("演示标题", {
  x: 0.5, y: 4.5, w: 9, h: 1,
  fontSize: 44, bold: true, color: "1E3A5F"
});

// 添加配图
slide.addImage("path/to/image.png", {
  x: 6.5, y: 2, w: 3, h: 2
});
```

### 图片生成

```javascript
// 使用 image_synthesize
{
  "prompt": "商务风格图表，蓝色主色调，现代简约设计",
  "output_file": "chart1.png",
  "aspect_ratio": "16:9"
}
```

### 语音合成

```javascript
// 使用 gen_audios
{
  "text": "大家好，今天我将为大家介绍人工智能的发展趋势。",
  "output_file": "voice1.mp3",
  "voice": "female-zh-CN",
  "speed": 1.0
}
```

### 视频生成

```javascript
// 使用 batch_image_to_video
{
  "count": 1,
  "image_file_list": ["slide1.png"],
  "output_file_list": ["clip1.mp4"],
  "prompt_list": ["演讲画面，保持稳定"],
  "duration": 6,
  "resolution": "1080P"
}
```

## 参数默认值

| 参数 | 默认值 | 范围 |
|------|--------|------|
| page_count | 自动计算 | 5-50页 |
| duration | 10分钟 | 1-60分钟 |
| style | 商务 | 商务/简约/创意/学术 |
| language | 中文 | 中文/英文 |
| resolution | 1080P | 720P/1080P/4K |

## 触发短语

- "生成PPT"
- "制作演示文稿"
- "创建PPT"
- "帮我做PPT"
- "生成演讲视频"
- "制作视频演示"
- "PPT和视频"
- "演示文稿生成"

## 文件命名规范

```
PPT文件: {主题}_{日期}.pptx
配图目录: {主题}_images/
语音目录: {主题}_audio/
视频文件: {主题}_video_{日期}.mp4
```

## 常用工具映射

| 功能 | 工具 |
|------|------|
| PPT创建 | pptx-generator 技能 |
| 图片搜索 | images_search_and_download |
| 图片生成 | image_synthesize |
| 语音合成 | gen_audios |
| 视频生成 | batch_image_to_video |
| 视频合并 | (使用视频编辑工具) |
