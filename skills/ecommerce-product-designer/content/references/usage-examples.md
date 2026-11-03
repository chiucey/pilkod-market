---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502201f742a5edb08aaf9a37af0a84a8af33e3509a7f6e88377a8dfd6ac68b023337d022100c515d2e73350e8fccecc6ccd83b28be58e9d03b576f406753002d1564cb1e5ad
    ReservedCode2: 3046022100e79ed1112dc7074c328617159476571147f05a7008a000b2ff07fd83b2e269df022100c87a48bdccfa33d613bdc61d93368066937f28f6fe5eb0f87df4380126f0d9ee
---

# 电商美工技能使用示例

## 示例1：蓝牙耳机主图生成

**用户输入**:
```
请为这款无线蓝牙耳机生成电商主图
图片: [上传耳机图片]
产品描述: 真无线蓝牙耳机，入耳式设计，主动降噪，续航30小时
目标平台: 淘宝店铺
风格: 简约专业
```

**执行流程**:

1. **图片分析**:
使用 `images_understand` 分析图片，提取产品特征：
- 产品类型: 无线蓝牙耳机
- 外观特征: 入耳式、哑光黑色外壳
- 配件: 充电盒、可替换耳塞
- 目标用户: 商务人士、音乐爱好者

2. **卖点搜索**:
搜索 "蓝牙耳机 卖点 降噪 续航" 获取营销素材

3. **卖点整合**:
```
核心卖点:
- 主动降噪 - 嘈杂环境也能沉浸聆听
- 30小时续航 - 全天候不断电
- 真无线设计 - 自由无束缚
- 音质认证 - Hi-Fi级音效
```

4. **主图生成**:
提示词:
```
Professional e-commerce product photography, wireless bluetooth earphones
on clean white background, earbuds in charging case centered,
active noise cancellation highlighted, sleek matte black finish,
studio lighting with soft shadows, minimalist design,
include subtle audio wave icon suggesting sound quality,
commercial photography quality, 4K resolution
```

## 示例2：女装连衣裙详情页

**用户输入**:
```
需要生成一套女装连衣裙的详情页图片
图片: [上传裙子图片]
颜色: 酒红色、墨绿色、深蓝色
风格: 轻奢优雅
目标: 详情页5张图
```

**生成计划**:
1. 详情01: 主图+核心卖点Banner
2. 详情02: 面料细节+工艺展示
3. 详情03: 颜色选择+上身效果
4. 详情04: 尺码表+身材参考
5. 详情05: 场景穿搭+购买引导

**各页面提示词**:

**Page 1 - 卖点展示**:
```
Elegant dress product detail page design, luxurious fabric texture,
highlight showing "Premium Silk Blend" and "Elegant Drape",
sophisticated wine red color, minimalist layout with elegant typography,
soft lighting emphasizing fabric quality, professional fashion photography
```

**Page 2 - 细节工艺**:
```
Close-up detail shots of [产品名称] dress showing:
- Intricate stitching details
- Premium zipper closure
- Delicate hem finishing
- Fabric texture close-up
Clean white background comparison, professional garment photography,
luxury fashion detail showcase, mobile-friendly vertical layout
```

## 示例3：运动鞋多色SKU图

**用户输入**:
```
为这款跑鞋生成5个颜色的SKU图
图片: [上传跑鞋图片]
颜色列表: 经典白/黑、荧光绿、深灰蓝、珊瑚橙、纯黑色
用途: 淘宝SKU选择页
```

**SKU图提示词**:
```
E-commerce SKU display grid, [品牌] running shoes showing 5 color variants:
1. Classic White/Black - clean athletic style
2. Neon Green - vibrant energetic look
3. Deep Gray Blue - mature sporty aesthetic
4. Coral Orange - fresh summer vibe
5. Pure Black - sleek stealth design

Each shoe clearly visible, color-coded labels, white background,
consistent angle and lighting across all variants,
professional product photography, size reference included,
organized grid layout suitable for SKU selection page
```

## 示例4：护肤品套装

**用户输入**:
```
为这套护肤品生成主图和详情页
产品: 保湿修护套装（含水、乳、霜、精华）
风格: 医美级专业感
卖点: 深层补水、敏感肌适用、7天见效
```

**主图提示词**:
```
Professional skincare product photography, [品牌] moisturizing skincare set
arranged elegantly (toner, lotion, cream, serum bottles),
medical-grade professional aesthetic, clean clinical white background,
hyaluronic acid and ceramide ingredients highlighted,
calm soothing color palette, soft studio lighting,
luxury skincare branding, dermatologist recommended badge,
commercial product photography, 4K resolution
```

**详情页系列提示词**:

```
[Page 1 - 套装全景]:
Complete skincare routine display, 4 products beautifully arranged,
minimalist skincare aesthetic, soft pink accent colors,
"Deep Hydration & Repair" main tagline, clean professional layout

[Page 2 - 成分亮点]:
Skincare ingredients visualization, hyaluronic acid molecule structure,
ceramide layer diagram, "72-hour moisture lock" highlight,
scientific skincare research aesthetic, clean modern design

[Page 3 - 使用步骤]:
Step-by-step skincare routine guide, morning and evening application,
4-step application order with product photos, simple icon illustrations,
"7 Days Visible Results" before/after concept, clean mobile layout

[Page 4 - 适用人群]:
Skincare product suitable for sensitive skin, dermatologist tested badge,
all skin types icon, gentle formula highlights, calming blue/white color scheme,
professional skincare marketing design
```

## 示例5：家具类产品

**用户输入**:
```
为这款人体工学办公椅生成场景化主图
图片: [上传椅子图片]
场景: 现代简约办公室
核心卖点: 透气网布、腰椎支撑、可调节扶手
```

**场景化主图提示词**:
```
Modern ergonomic office chair in a contemporary minimalist office setting,
sleek black mesh office chair with lumbar support visible,
adjustable armrests in natural position, contemporary desk setup background,
bright natural window lighting, professional workplace photography,
comfort and productivity themes, commercial product lifestyle shot,
ultra detailed, architectural photography style
```

## 常见问题处理

### Q1: 图片生成不理想怎么办？
**解决方案**:
- 调整产品描述的详细程度
- 指定更具体的颜色、材质、风格关键词
- 要求生成多个版本选择

### Q2: 如何保持品牌一致性？
**解决方案**:
- 在描述中明确品牌调性（高端/简约/活泼）
- 统一色彩关键词（如"莫兰迪色系"）
- 参考品牌VI规范指定设计元素

### Q3: 不同平台尺寸要求不同？
**解决方案**:
| 平台 | 主图尺寸 | 详情页宽度 |
|------|---------|-----------|
| 淘宝 | 800x800 | 750px |
| 天猫 | 800x800 | 790px |
| 京东 | 800x800 | 720px |
| 拼多多 | 800x800 | 自适应 |
| 跨境电商 | 1600x1600 | 1200px |
