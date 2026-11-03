---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022064012f031e15e2e17b5493e9253b64eedc62d71764fbd38482c1cdeb3640cbeb022100855022bf3ec12ed9182e26ed66bd2b0b26267a1cfe80c514319c37a1ec7a31f0
    ReservedCode2: 30450221009fa0fd8ecf54789e06b61bdabded71a821e4146a73aaaa60939b35a088a73c7002205c448addd990068d4372b26e054f0f317df6203ce56ad111557288cb43e83f78
description: 专业的电商美工技能。能对产品图片进行理解，根据客户描述以及图片自动识别产品，上网搜寻产品特点，优化卖点并结合卖点，并生成该产品的主图、详情页、SKU图。当用户要求创建电商产品图片、设计主图、生成详情页、制作SKU图、优化产品卖点时使用。
name: ecommerce-product-designer
---

# 电商产品美工设计师

专业的电商图片生成技能，能够理解产品、搜索卖点、优化设计并生成各类电商素材。

## 核心能力

1. **产品图片理解** - 使用 AI 分析产品图片，识别产品类型、特征、颜色、材质等
2. **智能产品识别** - 根据描述和图片自动识别产品类别和属性
3. **卖点研究** - 搜索产品特点、竞争优势、用户痛点
4. **卖点优化** - 结合产品特征和市场需求优化营销卖点
5. **图片素材生成** - 生成主图、详情页、SKU图等电商素材

## 工作流程

### 步骤 1：产品理解与分析

**输入收集：**
- 产品图片（用户上传或URL）
- 产品描述（名称、特点、目标用户等）
- 产品类别（可选）

**执行操作：**
使用 `images_understand` 工具分析产品图片：
```
分析产品图片内容，包括：
- 产品类型和类别
- 外观特征（颜色、形状、材质）
- 使用场景
- 目标用户群体
- 与竞品的差异化特征
```

### 步骤 2：卖点研究与收集

**执行操作：**
使用 `batch_web_search` 搜索产品相关信息：

搜索维度：
1. 产品核心卖点
2. 竞品对比优势
3. 用户关注点/痛点
4. 行业趋势和热点
5. 营销关键词

**输出：**
收集全面的产品卖点和营销素材

### 步骤 3：卖点优化整合

**执行操作：**
整合分析结果，优化生成：

1. **核心卖点（USP）** - 3-5个最具吸引力的卖点
2. **营销文案** - 主标题、副标题、详情描述
3. **视觉关键词** - 用于图片生成的描述词
4. **差异化亮点** - 与竞品对比的独特优势

### 步骤 4：电商素材生成

根据用户需求生成以下素材：

#### 主图（Main Image）
- 尺寸要求：800x800px 或 1000x1000px（正方形）
- 背景：白底或渐变背景
- 元素：产品主体、品牌标识、核心卖点标签
- 风格：简洁、专业、突出产品

#### 详情页（Detail Page）
- 多张图片组合展示
- 包含：产品细节、使用场景、功能特点、规格参数
- 布局：竖版设计，适合手机端浏览

#### SKU图（SKU Image）
- 展示产品变体（颜色、尺寸、款式）
- 清晰的变体对比
- 规格信息标注

## 输出格式

生成的图片保存到 `/workspace/output/ecommerce/` 目录：

```
output/ecommerce/
├── main_images/          # 主图
│   ├── main_image_1.png
│   ├── main_image_2.png
│   └── main_image_3.png
├── detail_pages/         # 详情页
│   ├── detail_01.png
│   └── detail_02.png
├── sku_images/           # SKU图
│   └── sku_color_*.png
└── references/           # 参考素材
    └── style_guide.md
```

## 图片生成提示词模板

### 主图提示词
```
Professional e-commerce product photography, [产品名称] on clean white background,
centered composition, soft studio lighting, high-end product shot style,
minimalist design, [颜色] color scheme, include subtle brand logo placement,
commercial photography quality, 4K resolution, product showcase style
```

### 详情页提示词
```
Modern e-commerce product detail page design, [产品名称] showing:
- Product close-up details
- Usage scenario demonstration
- Size comparison reference
- Feature highlights with icons
Clean layout, mobile-friendly vertical design, professional retail photography style
```

### SKU图提示词
```
E-commerce SKU display, [产品名称] color variants comparison,
showing [颜色1], [颜色2], [颜色3] options side by side,
clear product labels, size reference, professional catalog photography,
organized grid layout, commercial product photography
```

## 使用示例

### 示例 1：生成基础电商素材
```
用户：请为这款无线蓝牙耳机生成主图和详情页素材
图片：[上传耳机图片]
描述：入耳式设计，降噪功能，续航30小时
```

### 示例 2：批量生成SKU图
```
用户：需要生成这款背包的5个颜色SKU图
图片：[上传背包图片]
颜色：黑色、深蓝、军绿、灰色、卡其色
```

## 质量标准

1. **图片质量**：高清、清晰、无失真
2. **卖点突出**：核心优势一目了然
3. **视觉统一**：风格、配色、字体协调一致
4. **信息完整**：规格、参数、使用说明齐全
5. **合规性**：避免绝对化用语、虚假宣传

## 注意事项

- 图片生成默认比例 1:1，可根据平台要求调整
- 如需特定风格（如INS风、简约风、国潮风），请在描述中注明
- SKU图数量根据产品变体数量确定
- 生成的图片仅供电商平台使用参考

## 错误处理

- 图片理解失败：请求用户补充更清晰的产品图片
- 卖点搜索无结果：基于图片分析和常识推断产品特点
- 图片生成不满意：调整提示词重新生成，或提供多个版本供选择
