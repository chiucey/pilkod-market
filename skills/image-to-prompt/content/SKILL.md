---
name: image-to-prompt
description: 当用户发送图片并要求反推prompt时使用。适用于提取图片中的视觉元素、风格特征、构图方式等，用于文生图时的参考提示词生成。触发短语：分析这张图、反推prompt、图生提示词、这个图怎么画、帮我生成提示词、反向工程提示词
---

# Image to Prompt Generator

将图片反向工程为详细的文生图提示词。

## 工作流程

### Step 1: 图片分析

使用 `images_understand` 工具深度分析图片内容：

**必须提取的元素**：
1. **主体内容** - 人物、动物、物体、场景等
2. **风格特征** - 艺术风格、渲染方式（写实/插画/动漫/水彩等）
3. **构图方式** - 视角、景别、取景范围
4. **光线氛围** - 光源方向、软硬、情绪氛围
5. **色彩基调** - 主色调、配色方案、色彩风格
6. **细节特征** - 材质、纹理、特效、背景元素
7. **技术参数** - 宽高比、参考风格方向

### Step 2: Prompt 构建

按照以下结构生成prompt：

```
[主体] + [动作/状态] + [场景/环境] + [风格] + [光线] + [色彩] + [构图] + [质量修饰词]
```

### Step 3: 输出格式

分两部分输出：

**结构化分析**：
```
📸 **图片分析结果**

- **主体**: [识别到的主体]
- **风格**: [艺术风格/渲染方式]
- **构图**: [视角/景别]
- **光线**: [光源类型/氛围]
- **色彩**: [色调/配色]
- **细节**: [重要细节/特效]
```

**推荐Prompt**：
```
[反向工程得出的完整prompt]
```

**使用建议**：
- 推荐的宽高比
- 可选的风格变体建议
- 调整参数提示

## Prompt 增强模板

根据分析结果自动添加以下质量修饰词：

- **高质量**: highly detailed, masterpiece, best quality, ultra detailed
- **光线**: cinematic lighting, soft lighting, dramatic lighting
- **细节**: intricate details, fine texture, 8k resolution
- **氛围**: ethereal, atmospheric, dreamy
- **构图**: professional composition, award-winning

## 示例

**输入**: 用户发送一张赛博朋克城市夜景图

**输出**:

📸 **图片分析结果**

- **主体**: 未来都市天际线，霓虹灯建筑群
- **风格**: 赛博朋克、数字艺术、科幻美学
- **构图**: 俯视/仰视混合，城市中心对称
- **光线**: 霓虹灯光源，多彩点光源，强烈明暗对比
- **色彩**: 蓝紫色调为主，霓虹粉/青点缀
- **细节**: 雨滴效果、全息广告牌、飞行器

**推荐Prompt**:
```
A futuristic cyberpunk cityscape at night, neon-lit skyscrapers, holographic billboards, flying vehicles, rain-slicked streets reflecting neon lights, dramatic cinematic lighting, blue and purple color palette with pink and cyan accents, wide-angle perspective, highly detailed, masterpiece, best quality, atmospheric, volumetric lighting
```

**使用建议**:
- 推荐宽高比: 16:9
- 可尝试添加: "blade runner aesthetic", "sci-fi concept art"
- 光线可强调: "volumetric fog", "lens flare"

## 注意事项

1. **分析优先**: 先准确识别图片元素，再构建prompt
2. **结构化输出**: 保持分析结果和prompt分离，便于用户理解
3. **可调整性**: prompt应作为起点，用户可自行增删调整
4. **多风格选项**: 尽量提供1-2个变体建议
5. **中文友好**: prompt保留英文，分析结果使用中文
