---
name: artistic-image-generator
description: 专业图像生成与风格调整技能。当用户要求根据文字描述生成图像、根据参考图像提取风格创作、进行色调/光线/对比度等专业美术调整、图像风格迁移、创意图像编辑等场景时使用。触发短语包括："生成图像"、"创作图像"、"画一幅"、"根据描述生成"、"风格迁移"、"风格转换"、"调整色调"、"调整光线"、"专业调色"、"图像编辑"等。
---

# Artistic Image Generator - 专业图像生成与风格调整技能

## 核心能力

本技能提供三大核心图像处理能力：

### 1. 风格提取与沿用 (Style Transfer)
- 分析参考图像的整体视觉风格
- 提取色彩方案、笔触质感、光影特点
- 将提取的风格应用到新图像生成中

### 2. 文字驱动图像生成 (Text-to-Image)
- 根据详细文字描述生成原创图像
- 支持多种艺术风格：写实、插画、动漫、水彩、油画等
- 支持指定画面构图、光线氛围、情绪基调

### 3. 专业美术调整 (Professional Retouching)
- **色调调整**：冷暖色调、色彩平衡、饱和度控制
- **光线调整**：明暗对比、光源方向、柔光/硬光效果
- **氛围调整**：情绪滤镜、电影感、复古风格等

## 工具选择策略

### 主工具：`image_synthesize`
- **首选工具**：用于图像生成和编辑
- **适用场景**：需要从参考图像提取风格 + 根据文字描述生成新图像
- **优势**：
  - 支持风格迁移（通过参考图像）
  - 支持文字描述驱动
  - 支持细节调整和编辑
  - 支持多种宽高比和分辨率

### 辅助工具：`images_search_and_download`
- **适用场景**：需要寻找参考图像作为风格来源
- **配合使用**：获取风格参考图后，配合 `image_synthesize` 进行风格迁移

### 辅助工具：`images_understand`
- **适用场景**：分析现有图像的风格特点
- **配合使用**：理解图像风格后，指导后续生成参数

## 标准化工作流程

### 场景 A：风格迁移生成

```
1. 分析需求
   ├── 用户提供参考图像？→ 下载并分析风格特征
   └── 用户描述风格偏好？→ 搜索相关风格参考

2. 提取风格要素
   ├── 色彩方案（主色调、辅助色）
   ├── 光影特点（光源、阴影、对比度）
   ├── 质感风格（写实、抽象、笔触感）
   └── 构图特点（视角、景深、焦点）

3. 构建生成提示词
   ├── 主体描述：画面主要内容
   ├── 风格标签：提取的风格特征
   ├── 氛围修饰：光线、情绪氛围
   └── 技术参数：宽高比、质量要求

4. 执行生成
   └── 使用 image_synthesize 生成图像
```

### 场景 B：专业美术调整

```
1. 理解调整需求
   ├── 色调调整：冷暖、饱和度、色彩平衡
   ├── 光线调整：明暗、对比度、光源效果
   └── 氛围调整：滤镜、情绪风格

2. 选择调整方式
   ├── 轻度调整：使用描述性提示词引导
   └── 重度调整：提供详细的光线/色调参数

3. 执行调整
   └── 使用 image_synthesize 进行编辑
```

## 提示词工程规范

### 基础提示词结构

```
[主体描述], [风格标签], [光线氛围], [色调修饰], [构图参数], [质量要求]
```

### 风格标签参考

| 风格类型 | 英文标签 |
|---------|---------|
| 写实摄影 | photorealistic, hyperrealistic, DSLR quality |
| 电影质感 | cinematic, film grain, cinematic lighting |
| 插画风格 | illustration, digital art, concept art |
| 动漫风格 | anime style, manga style, cel shading |
| 水彩画 | watercolor, soft brush strokes |
| 油画 | oil painting, impasto, classical |
| 赛博朋克 | cyberpunk, neon lights, futuristic |
| 复古胶片 | vintage, film photography, retro |

### 光线氛围标签

| 光线类型 | 英文标签 |
|---------|---------|
| 黄金时刻 | golden hour, warm sunlight |
| 蓝调时刻 | blue hour, cool ambient |
| 戏剧光 | dramatic lighting, chiaroscuro |
| 柔光 | soft lighting, diffused light |
| 逆光 | backlight, rim lighting, silhouette |
| 霓虹光 | neon lighting, colorful glow |

### 色调调整标签

| 调整类型 | 英文标签 |
|---------|---------|
| 冷色调 | cool tones, blue shift, icy |
| 暖色调 | warm tones, golden, amber |
| 高饱和 | vibrant colors, saturated, punchy |
| 低饱和 | muted tones, desaturated, pastel |
| 高对比 | high contrast, punchy blacks |
| 低对比 | low contrast, soft, flat |

## 常用场景模板

### 模板 1：人像摄影风格迁移

```
Prompt: A portrait of [subject description], [photographic style],
[lighting setup], [color grading], shot on [camera/lens],
[depth of field], professional photography
```

### 模板 2：场景插画风格生成

```
Prompt: [Scene description], [illustration style],
[color palette], [mood/atmosphere], detailed digital art,
[aspect ratio], 4K quality
```

### 模板 3：产品展示图

```
Prompt: [Product description], [presentation style],
[background setup], [lighting type], commercial photography,
[perspective], high-end product shot
```

## 质量控制标准

### 生成前检查
- [ ] 明确理解用户的核心需求（生成新图像 vs 调整现有图像）
- [ ] 确认是否有参考图像可用
- [ ] 确定目标风格和氛围
- [ ] 准备完整的描述性提示词

### 生成后评估
- [ ] 图像是否准确反映描述内容
- [ ] 风格是否与参考一致（如果提供了参考）
- [ ] 光线和色调是否符合要求
- [ ] 是否需要进一步调整

### 调整迭代
- [ ] 如果结果不理想，收集具体反馈
- [ ] 针对性地调整提示词中的特定元素
- [ ] 逐轮优化直到满意

## 常见问题处理

### Q1: 生成的图像与描述不符
**解决方案**：
- 增加描述的细节和具体性
- 使用更明确的视觉词汇
- 分解复杂场景为多个简单元素

### Q2: 风格迁移效果不明显
**解决方案**：
- 提供更清晰的风格参考图
- 在提示词中明确强调风格特征
- 减少主体描述的复杂性

### Q3: 光线/色调调整效果不佳
**解决方案**：
- 使用更专业的光线术语
- 指定具体的色温值（如 6500K）
- 提供期望效果的参考图

## 输出规范

完成图像生成或调整后：

1. **直接展示图像**给用户查看
2. **说明使用的工具和参数**
3. **询问是否需要调整**，并收集具体反馈
4. **如需调整**：根据反馈修改提示词，重新生成

---

## 技能使用示例

### 示例 1：风格迁移
**用户输入**："参考这张梵高《星夜》的风格，画一幅现代城市夜景"

**执行流程**：
1. 分析《星夜》的风格特征（漩涡笔触、蓝色主调、动态星空）
2. 构建提示词：现代城市夜景 + 梵高风格漩涡笔触 + 蓝色调 + 星空元素
3. 使用 image_synthesize 生成

### 示例 2：专业调色
**用户输入**："把这张照片调成电影感的蓝调色调，增加一些光晕效果"

**执行流程**：
1. 分析原图的光线和色彩
2. 构建提示词：原图 + cinematic blue color grading + blue hour atmosphere + light leak effects
3. 使用 image_synthesize 编辑

### 示例 3：完全创意生成
**用户输入**："生成一幅赛博朋克风格的女机器人战士概念图，科幻机甲，未来城市背景"

**执行流程**：
1. 分解元素：女机器人战士 + 科幻机甲 + 赛博朋克 + 未来城市
2. 构建详细提示词
3. 使用 image_synthesize 生成
