---
name: logo-generator
description: 根据用户描述生成logo、品牌标识、图标设计。当用户要求生成logo、创建品牌标识、设计logo、制作企业标志、创作品牌符号时使用。
---

# Logo 生成技能

## 核心能力

根据用户的文字描述，使用 AI 图像生成技术创建专业 logo 设计。

## 触发条件

当用户发送以下类型的请求时触发此技能：
- "帮我生成一个 logo"
- "设计一个品牌标识"
- "创建一个公司 logo"
- "设计一个图标"
- "帮我做一个logo"
- "品牌设计"

## 工作流程

### 步骤 1：提取 logo 描述

仔细分析用户的 logo 设计需求，提取以下关键信息：
- **品牌名称**：公司/产品名称
- **品牌类型**：科技、餐饮、时尚、金融、教育等
- **风格偏好**：简约、现代、复古、手绘、几何、扁平、渐变等
- **颜色偏好**：如有指定的主色调
- **行业特点**：是否需要体现特定行业特征
- **使用场景**：网站、APP、社交媒体、打印等

### 步骤 2：构建生成提示词

根据提取的信息构建专业的 logo 生成提示词：

**基础模板**：
```
[品牌名称] logo design, professional [风格] logo, [行业类型], [颜色描述], vector style, clean design, brand identity, minimalist
```

**增强提示词要素**：
- 明确品牌定位和风格
- 指定颜色方案（如需要）
- 说明设计风格（简约/复杂/现代/复古）
- 包含技术要求（矢量感、扁平化、高清等）

### 步骤 3：生成 logo

使用 `image_synthesize` 工具生成 logo 图像：

```json
{
  "requests": [{
    "prompt": "<构建的logo提示词>",
    "output_file": "logo_<timestamp>.png",
    "aspect_ratio": "1:1"
  }]
}
```

### 步骤 4：优化与交付

1. 检查生成的 logo 质量
2. 如效果不理想，根据用户反馈调整提示词重新生成
3. 提供下载链接和文件路径

## 提示词示例库

### 科技公司
```
TechCorp logo design, modern minimalist tech logo, blue gradient, digital innovation, clean vector style, brand identity, white background
```

### 餐饮品牌
```
FreshKitchen logo, restaurant brand identity, organic green and orange, food industry, modern culinary, professional logo design
```

### 时尚品牌
```
LuxeMode logo, elegant fashion brand, black and gold, premium minimalist, luxury fashion identity, sophisticated design
```

### 教育机构
```
SmartLearn education logo, friendly and professional, knowledge symbol, blue and yellow, academic institution, clean design
```

### 创意工作室
```
CreativeHub studio logo, artistic creative agency, colorful geometric, dynamic modern design, innovative brand identity
```

## 输出格式

成功生成后，返回以下信息：
- **Logo 预览**：展示生成的图像
- **设计说明**：简要描述设计理念
- **文件路径**：图像文件的保存位置
- **使用建议**：推荐的应用场景和尺寸

## 常见问题处理

### Logo 效果不佳
- 增加风格描述词
- 明确颜色要求
- 提供更多品牌背景信息
- 尝试不同的风格方向

### 用户需求模糊
- 询问品牌名称和类型
- 了解目标受众
- 确认行业领域
- 询问风格偏好

## 质量标准

- Logo 应清晰可辨，即使缩小也能识别
- 颜色搭配协调专业
- 设计风格与品牌定位一致
- 适合多种应用场景
