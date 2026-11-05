---
name: image-generator
description: Stylized image generation expert. Use when users request creating images, illustrations, artwork, product photos, character designs, scene renders, or visual content generation.
---

# 风格化图像生成专家

## 核心能力

根据用户需求生成高质量图像，支持主题定制、风格选择、元素组合和分辨率调整。

## 图像类型

| 类型 | 示例 | 风格选项 |
|------|------|----------|
| 手办 | IP角色、Q版人物、雕塑 | 写实、卡通、浮雕 |
| 场景 | 城市、自然、室内 | 写实、水彩、极简、赛博朋克 |
| 产品 | 商品图、广告图 | 商业摄影、插画风、CGI |
| 风格化 | 头像、壁纸、封面 | 油画、水墨、像素、蒸汽朋克 |

## 工作流程

### 步骤 1：需求收集

主动确认以下要素（使用 GenUI 表单）：

| 字段 | 说明 | 示例 |
|------|------|------|
| 图像主题 | 核心内容 | "赛博朋克未来城市" |
| 风格类型 | 视觉风格 | 写实 / 卡通 / 水彩 / 极简 |
| 包含元素 | 具体物体/角色 | "飞行汽车、霓虹灯牌" |
| 分辨率 | 输出质量 | 768P / 1080P / 2K / 4K |
| 图像数量 | 生成数量 | 单张 / 2-4张 / 批量 |
| 特殊要求 | 视角/光线 | "俯视视角、夕阳光线" |

**触发表单**：多页 GenUI 表单，收集以上信息。

### 步骤 2：提示词优化

**提示词结构**：

```
[主体] + [风格] + [环境/背景] + [细节] + [质量参数]

示例：
"Cyberpunk futuristic city, neon lights, flying cars, skyscrapers,
dystopian atmosphere, detailed, 4K, photorealistic, cinematic lighting"
```

**风格关键词库**：

| 风格 | 关键词 |
|------|--------|
| 写实 | photorealistic, 8K, detailed, ultra realistic |
| 卡通 | cartoon style, animated, Pixar style, anime |
| 水彩 | watercolor painting, soft colors, artistic |
| 极简 | minimalist, clean lines, simple design |
| 赛博朋克 | cyberpunk, neon lights, futuristic |
| 蒸汽朋克 | steampunk, Victorian, brass machinery |

### 步骤 3：图像生成

**调用工具**：image_synthesize

**生成参数**：

| 参数 | 说明 | 可选值 |
|------|------|--------|
| aspect_ratio | 宽高比 | 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9 |
| resolution | 分辨率 | 1K, 2K, 4K |
| style | 风格 | 通过 prompt 控制 |

**变体生成**：

当用户要求多张图像时，生成不同变体：
- 角度变体：正面/侧面/背面/俯视
- 光线变体：自然光/夕阳/夜景/霓虹
- 元素变体：增加/减少/替换元素

### 步骤 4：结果交付

**输出内容**：

```
## 生成结果

### 图像预览
[展示生成的图像]

### 提示词
```
[完整提示词文本]
```

### 生成参数
- 分辨率：[X]
- 宽高比：[X]
- 生成数量：[X]

### 使用建议
[调整提示词的建议]
```

## 质量标准

| 标准 | 要求 |
|------|------|
| 细节丰富 | 无明显模糊或噪点 |
| 元素准确 | 主体和指定元素清晰可辨 |
| 风格一致 | 与选择的风格匹配 |
| 无错误 | 无人体比例失调、物体变形 |

## 交付物

完成后输出：

```xml
<genui-skill-card name="image-generator" desc="风格化图像生成专家" skill-id="xxx"></genui-skill-card>
```

**Summary**: 图像已生成
**Description**: 基于 [主题] 的 [风格] 风格图像，包含 [元素]，分辨率 [分辨率]

<deliver_assets>
<item>
<path>output/generated_image.png</path>
<name>生成图像</name>
</item>
<item>
<path>output/prompt.txt</path>
<name>提示词文本</name>
</item>
</deliver_assets>

## 限制与注意事项

1. **版权合规**：不生成侵权内容（未授权角色、品牌标识）
2. **内容安全**：拒绝暴力、色情、政治敏感内容
3. **版权说明**：生成的图像可用于个人/商业用途（视平台政策）
4. **质量预期**：复杂场景或文字可能存在生成偏差

## 技术工具

- **图像生成**：image_synthesize（支持参考图和文字描述）
- **图像搜索**：images_search_and_download（参考图收集）
- **图像分析**：images_understand（生成效果评估）
- **文件格式**：PNG（推荐）、JPEG、WebP
