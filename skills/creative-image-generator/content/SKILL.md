---
name: creative-image-generator
description: 专精于创意图片生成的专家。当用户输入热梗、脑洞、想法、段子或创意描述，希望生成配图、海报、明信片、表情包、创意图片、社交媒体配图等各类图片时使用。支持生成梗图、幽默图片、节日贺卡、主题海报等场景。触发词：生成图片、做图、配图、海报、明信片、梗图、表情包、创意图、做张图
---

# 创意图片生成专家

## 核心能力

将用户的热梗、脑洞、想法或创意描述转化为专业的图片生成提示词，并生成高质量图片。

## 工作流程

### 第一步：理解用户意图

**输入分析**：
- 识别用户描述的核心创意或梗
- 判断图片类型需求（配图/海报/明信片/梗图/表情包等）
- 确定风格方向（搞笑/温馨/酷炫/文艺/简约等）
- 提取关键元素和场景描述

**类型识别**：
| 类型 | 特征关键词 |
|------|----------|
| 梗图/表情包 | 网络热梗、段子、金句、搞笑 |
| 海报 | 主题宣传、活动、广告、电影感 |
| 明信片 | 风景、祝福、旅行、纪念 |
| 配图 | 文章配图、社交媒体、公众号 |
| 创意合成 | 跨界混搭、意想不到的组合 |

### 第二步：构建专业提示词

**提示词结构**：
```
[主体描述] + [场景/背景] + [风格/氛围] + [构图/角度] + [画质要求]
```

**风格关键词库**：
- 写实系：photorealistic, 8K, high detail, cinematic lighting
- 插画系：digital art, illustration, vibrant colors, flat design
- 动漫系：anime style, manga, cel shading, vibrant
- 复古系：vintage, retro, 80s style, poster art
- 极简系：minimalist, clean, negative space, typography

**质量增强词**：
- 高画质：8K, ultra-detailed, 4K, masterpiece
- 专业感：professional, studio lighting, award-winning
- 氛围感：dramatic lighting, golden hour, volumetric light

### 第三步：生成图片

使用 `image_synthesize` 工具生成图片：

```
工具：image_synthesize
参数：
- prompt: 优化后的专业提示词
- output_file: 生成的图片路径（建议使用 .png 格式）
- aspect_ratio: 根据类型选择（海报 3:4，风景 16:9，社交媒体 1:1，方图 1:1）
```

### 第四步：优化与迭代

**如果结果不理想**：
1. 增强风格描述的精确性
2. 添加更多细节描述
3. 更换风格关键词
4. 调整构图描述

## 常用场景提示词模板

### 梗图/表情包

```
[核心梗/金句文字] + 背景选择：
- 搞笑风格：weird expression, meme format, internet humor
- 表情包：emoji-inspired, cartoon face, expressive
```

### 节日祝福明信片

```
[节日主题元素] + 风格选择：
- 温馨：warm colors, soft lighting, greeting card style
- 传统：festive atmosphere, traditional patterns, paper texture
```

### 主题海报

```
[核心主题] + [文字/标语] + 风格选择：
- 商业风：corporate style, bold typography, professional
- 艺术风：concept art, dramatic composition, artistic
```

### 社交媒体配图

```
[内容主题] + 风格选择：
- 小红书：trendy, lifestyle photography, warm tones
- 微博：eye-catching, meme-ready, viral format
- 公众号：clean, editorial style, readable
```

## 输出格式

生成完成后，提供：
1. **生成的图片**：展示图片预览
2. **使用的提示词**：供用户参考和复用
3. **图片参数**：尺寸、格式等信息

## 注意事项

- **中文输入**：直接使用中文描述需求，无需翻译
- **细节越多越好**：丰富的描述能获得更精确的结果
- **风格明确**：指定风格关键词可大幅提升效果
- **尺寸选择**：根据使用场景选择合适的比例
