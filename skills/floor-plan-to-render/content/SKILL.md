---
name: floor-plan-to-render
description: |
  将平面图、手稿、线图转换为效果图，或将实景图进行风格迁移。当用户说以下内容时使用：
  - "把平面图生成效果图"、"帮我把这个设计图纸渲染出来"、"生成效果图"
  - "手稿转效果图"、"线图渲染"、"CAD图转效果图"、"装修效果图"
  - "实景图风格迁移"、"改造效果图"、"这个场景用XX风格渲染"
  - "露台改造"、"庭院设计"、"室内装修效果图"、"商业空间设计"
  - "把这个图变成日式风格"、"用新中式风格渲染"、"法式田园风"
  支持：景观设计、建筑渲染、室内设计、商业空间、庭院花园、阳台露台等场景。
---

# 平面图转效果图与实景图风格迁移技能

## 技能概述

本技能处理两大类图像生成任务：
1. **平面图/手稿/线图 → 效果图**：将设计图纸转化为逼真的效果图
2. **实景图 → 效果图**：对现有场景进行风格迁移和改造设计

---

## 规则一：平面图/手稿/线图 转效果图

### 触发场景

当用户提供以下类型的图像并要求生成效果图时触发：
- 平面布置图
- 手绘设计稿
- CAD 线图
- 景观规划图
- 建筑布局图
- 室内设计图

### 核心工作流程

#### 阶段一：深度分析（必须执行）

1. **识别所有功能区域**
   - 逐一标注图中文字
   - 记录每个区域的名称和位置

2. **分析空间布局结构**
   - 确定整体朝向（横向/纵向）
   - 标注各区域相对位置关系
   - 记录尺寸和比例信息

3. **提取设计风格线索**
   - 从标注和元素判断风格（田园/现代/中式/日式等）
   - 识别关键景观元素（植物、水体、道路等）

#### 阶段二：精准生成（严格遵守）

- **1:1 比例还原**：每个区域位置必须与原图完全一致
- **方位精确**：使用方位词精确定位（左上角/右下侧/中部等）
- **中文标注**：所有功能区域使用中文标注
- **风格统一**：整体视觉效果与设计意图一致

#### 阶段三：输出规范

- **格式**：JPG/PNG 高清图片
- **标注**：每个功能区域清晰可见
- **质量**：根据需要调整分辨率

### 提示词模板

```英文提示词
Professional [landscape/interior/architectural] design rendering, bird's eye view perspective.
EXACT layout matching the reference floor plan with 1:1 ratio precision.
Strictly follow the original layout positions:
[T上方/北] - [区域A名称]
[中间] - [区域B名称]
[T下方/南] - [区域C名称]
[左] - [区域D名称]
[右] - [区域E名称]
Surrounding lush green vegetation and natural environment.
All functional zones clearly labeled in Chinese with elegant typography.
Realistic rendering style, vivid natural colors, professional quality visualization.
High detail, soft natural lighting, [季节/时间] atmosphere.
```

### 完整使用示例

#### 示例一：郊野休闲农场

**用户输入**：用户提供一张标注清晰的农场规划平面图

**布局分析**：
```
- 露营天地：最上方狭长横条区域
- 主通道：中部横向蓝色道路，贯穿东西
- 亲子农场：通道下方偏左位置
- 萌宠乐园：通道下方偏右位置
- 运动区（篮球场+匹克球场）：左侧中部及下方
- 餐厅和烧烤区：运动区右侧、钓鱼区上方（关键位置标注）
- 烘焙坊：左下角
- 钓鱼区：底部中央临水区域
- 大型综合馆：右侧纵长区域
```

**生成提示词**：
```
Professional landscape design rendering, bird's eye view.
EXACT layout matching: Top strip = 露营天地, Middle = 主通道,
Lower-left = 亲子农场, Lower-right = 萌宠乐园, Left side = 运动区（篮球场+匹克球场）,
Right side upper = 餐厅和烧烤区, Bottom center = 钓鱼区临水, Right vertical = 大型综合馆.
Surrounding lush green forest vegetation.
All zones labeled in Chinese: 露营天地, 亲子农场, 萌宠乐园, 篮球场, 匹克球场, 餐厅和烧烤区, 烘焙坊, 钓鱼区, 大型综合馆.
Realistic rendering, vivid colors, professional landscape visualization.
```

#### 示例二：日式庭院室内设计

**用户输入**：提供日式室内布局图，要求生成效果图

**布局分析**：
```
- 玄关：入口左侧
- 客厅：中央主区域
- 茶室：右侧
- 庭院：与客厅相邻的采光区域
- 洗手间：后方角落
```

**生成提示词**：
```
Japanese traditional interior design rendering, perspective view from entrance.
EXACT layout: Left entrance with 玄关, Center main 客厅 with tatami area,
Right side 茶室, Adjacent interior garden 庭院 with stone lantern and bamboo,
Rear corner 洗手间. Japanese shoji screens, wooden elements, tokonoma alcove.
Soft warm lighting, serene atmosphere, authentic Japanese aesthetic.
All rooms labeled in Chinese: 玄关, 客厅, 茶室, 庭院, 洗手间.
High quality 3D render, detailed textures, natural wood grain.
```

---

## 规则二：实景图转效果图（风格迁移）

### 触发场景

当用户提供以下类型的图像组合时触发：
- 实景照片（改造前）+ 参考效果图（目标风格）
- 现有空间照片，要求应用特定风格
- 场景改造需求，包含"改成XX风格"、"改造"、"设计"

### 核心工作流程

#### 阶段一：双图分析

**分析实景图**：
- 识别场景类型（露台/庭院/室内/商业空间等）
- 记录原有结构（墙体/柱子/护栏/地面材质）
- 确定空间尺寸和布局

**分析参考图**：
- 识别目标风格（日式禅意/新中式/轻奢/现代等）
- 提取关键设计元素（水景/植物/材料/装饰）
- 理解光影和色彩风格

#### 阶段二：智能融合

- **保留原有结构**：墙体、柱子、护栏等必须保留
- **风格精准迁移**：按参考图完全重新设计
- **布局一致性**：空间结构与实景图保持一致
- **元素合理融入**：将参考图设计元素适配到实景空间

#### 阶段三：输出规范

- **格式**：JPG/PNG 高清图片
- **风格**：与参考图风格完全一致
- **质量**：专业级渲染效果

### 提示词模板

```英文提示词
Transform this [实景图场景描述] using [参考图风格描述] as reference.
Keep existing structural elements: [保留的结构].
Apply design elements from reference: [参考图的设计元素].
Target style: [目标风格详细描述].
Maintain original spatial layout and proportions.
Professional architectural visualization, photorealistic rendering.
```

### 完整使用示例

#### 示例一：高层露台改造（日式禅意）

**用户输入**：
- 实景图：高层露台，荒废杂乱，有白墙、立柱、金属护栏、积垢地面
- 参考图：禅意日式庭院风格

**分析结果**：
```
保留元素：白墙、立柱、金属护栏（结构不变）
改造内容：锦鲤池、汀步路、木桥、青苔、松树盆景、石灯笼
风格：日式禅意、宁静雅致、枯山水元素
```

**生成提示词**：
```
Transform this high-rise balcony with white walls, pillars, and metal railing
into Japanese Zen garden style. Keep existing structure: white walls, pillars, metal railing.
Add: koi pond (锦鲤池) with wooden bridge (木桥), stepping stones (汀步路),
moss garden (青苔), pine bonsai (松树盆景), stone lantern (石灯笼).
Japanese Zen aesthetic: minimalist design, natural stone, wooden elements,
bamboo accents, peaceful atmosphere. Traditional Japanese garden with modern balcony structure.
Professional architectural visualization, photorealistic rendering, soft natural lighting.
```

#### 示例二：普通庭院改造（新中式）

**用户输入**：
- 实景图：普通现代庭院，空旷草地
- 参考图：新中式庭院风格

**分析结果**：
```
保留元素：庭院基本结构
改造内容：月洞门、假山流水、迎客松、白墙漏窗
风格：新中式、典雅大方、东方韵味
```

**生成提示词**：
```
Transform this ordinary modern courtyard into Chinese contemporary garden style (新中式).
Keep basic courtyard structure. Add: moon gate (月洞门), rockery with water feature (假山流水),
welcoming pine tree (迎客松), white walls with decorative windows (白墙漏窗).
Chinese contemporary aesthetic: traditional Chinese elements with modern simplicity,
elegant proportions, refined details, scholarly atmosphere.
Stone pathways, bamboo groves, subtle water features.
Professional rendering, warm natural lighting, authentic Chinese garden ambiance.
All areas labeled in Chinese.
```

#### 示例三：商业空间改造（轻奢现代）

**用户输入**：
- 实景图：普通店铺空间，简易装修
- 参考图：轻奢现代商业空间

**生成提示词**：
```
Transform this ordinary retail space into luxury modern commercial style.
Keep spatial layout and basic structure.
Apply: marble flooring, gold accent details, elegant display shelves,
ambient lighting fixtures, premium materials.
Modern luxury aesthetic: clean lines, neutral colors with gold accents,
high-end finishes, sophisticated atmosphere.
Professional commercial interior visualization.
```

---

## 常见场景类型速查

| 场景类型 | 典型元素 | 推荐风格 |
|---------|---------|---------|
| 阳台/露台 | 栏杆、墙面、地面 | 日式禅意、现代简约、轻奢 |
| 庭院花园 | 草地、水体、植物 | 法式田园、中式古典、日式枯山水 |
| 室内客厅 | 沙发、茶几、窗户 | 现代简约、北欧风、新中式 |
| 餐厅空间 | 餐桌、灯具、装饰 | 轻奢、侘寂、工业风 |
| 商业店面 | 柜台、展架、门面 | 轻奢、现代、极简 |
| 公共区域 | 座椅、绿植、步道 | 自然生态、现代景观 |

## 常见风格关键词

| 风格 | 关键词 | 核心元素 |
|-----|-------|---------|
| 日式禅意 | Japanese Zen, Wabi-sabi | 枯山水、松竹、禅意 |
| 新中式 | Chinese Contemporary | 月洞门、假山、水墨 |
| 轻奢现代 | Modern Luxury | 大理石、金色、高品质 |
| 法式田园 | French Country | 碎花、铁艺、暖色 |
| 北欧极简 | Nordic Minimalist | 白木、简洁、功能性 |
| 工业风 | Industrial | 金属、混凝土、复古 |
| 侘寂风 | Wabi-sabi | 素朴、寂静、残缺美 |

## 通用优化技巧

### 提高生成质量

- 提供多角度参考图
- 明确标注关键元素位置
- 说明光照和时间氛围
- 列出必须保留的原有元素

### 加快生成速度

- 降低分辨率要求（避免4K）
- 简化提示词描述
- 使用单张参考图
- 减少复杂细节要求

### 精准控制位置

- 使用方位词：上方/下方/左侧/右侧/中部
- 使用相对关系：XX的左边/Y的右边
- 说明比例关系：占整个空间的1/3
- 标注参考点：靠近XX的位置

---

## 快速参考卡

### 平面图转效果图检查清单

- [ ] 识别所有功能区域和名称
- [ ] 分析整体布局结构
- [ ] 提取设计风格关键词
- [ ] 按1:1比例生成效果图
- [ ] 所有区域中文标注

### 实景图风格迁移检查清单

- [ ] 分析实景图结构和元素
- [ ] 确定目标参考风格
- [ ] 列出保留的原有结构
- [ ] 列出新增的设计元素
- [ ] 生成风格统一的效果图

---

**版本**：2.0
**更新日期**：2026-03-28
**作者**：MiniMax Agent
