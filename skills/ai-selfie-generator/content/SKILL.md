---
name: ai-selfie-generator
description: AI Selfie Generator. Uses a fixed character image (clawra.png) to autonomously generate selfies in various scenes. Supports expression variations, pose diversity, and scene adaptation. Trigger phrases: "generate selfie", "take a selfie", "change scene", "AI photo", "different scenes".
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4a8288002372f22ee48ce021165f513d
    PropagateID: 4a8288002372f22ee48ce021165f513d
    ReservedCode1: 3045022100dfae530ade90306375b64ab5f1f775d589c3cd6e2020ff969521fb0f64b6898402202205d5a819a6846ea1bd9c3ff58351967986b47b37c1f685d244144361864f40aeb
    ReservedCode2: 3046022100b9adc659c42d1dee2d8e4d36714f4bc124e23efa923fdcee1e0108c6469774d802210083126c49d66135b7db0daf3f4e71daafcf3efcb341621aa62d2bc9d884f25e4c
---

# AI自拍照生成器 (AI Selfie Generator)

## 功能概述

使用固定角色图片（clawra.png）作为角色基础，自主生成该角色在不同场景下的自拍照。强调表情变化、姿势多样性和场景适配性。

## 角色基础信息

**角色图片路径**: `/workspace/user_input_files/clawra.png`

**角色特征（已配置）**:

| 特征类别 | 详细描述 |
|---------|---------|
| **面部特征** | 柔和椭圆脸型，瓷白色肌肤，脸颊有粉色红晕，小而精致的鼻子，感染力的灿烂笑容 |
| **发型发色** | 长波浪黑发，蓬松感，额前有空气刘海 |
| **眼睛特征** | 大而明亮的杏仁眼，深棕色瞳孔，有卧蚕，长而卷曲的睫毛 |
| **整体风格** | K-pop偶像风格，温暖、活力、纯真、无暇之美 |
| **服装风格** | 白色圆领T恤，肩披黑白格纹针织开衫，预科风、休闲时尚、极简 |
| **妆容** | "伪素颜"妆容，自然肌肤，细眼线，渐变粉色唇彩 |

## 核心工作流程

### 步骤1：确定生成任务

**触发方式**：
- 用户请求生成自拍照
- 用户指定场景或风格
- 用户要求批量生成

**处理方式**：
1. 确定生成数量（单张或批量）
2. 确定场景选择（用户指定或自动多样选择）
3. 进入提示词构建阶段

### 步骤2：场景与表情选择

**预置场景库**：

| 场景类别 | 具体场景 |
|---------|---------|
| 自然风光 | 海滩日落、热带海岛、森林草坪、山顶日出、花海、湖泊倒影、樱花树下 |
| 城市建筑 | 都市天际线、咖啡馆、书店、老街巷、霓虹街道、露台天台 |
| 室内环境 | 温馨客厅、阳光卧室、开放式厨房、阳台花园、文艺工作室 |
| 旅行打卡 | 埃菲尔铁塔、威尼斯运河、京都寺庙、撒哈拉沙漠、极光背景 |
| 创意风格 | 赛博朋克、水墨国风、复古胶片、电影感、马卡龙色系 |

**多样性控制策略**：

1. **表情轮换**（每次必须使用不同表情）：
   - 灿烂笑容 - 开心场合、海滩、户外
   - 优雅微笑 - 正式场合、商务、室内
   - 酷感表情 - 时尚、街拍、创意场景
   - 温柔凝视 - 浪漫场景、近距离特写
   - 俏皮表情 - 可爱场景、生活照
   - 沉思表情 - 文艺场景、书店、咖啡馆
   - 自信表情 - 职业照、正式场合

2. **角度变化**：
   - 正面照、45度角、侧脸、回眸、仰望、低头沉思、托腮

3. **光线风格**：
   - Golden Hour（日落暖光）、Blue Hour（蓝调时刻）、柔光、侧光、逆光剪影

4. **姿态多样**：
   - 站姿、坐姿、倚靠、回眸、挥手、比心、自然抓拍

### 步骤3：生成提示词构建

根据角色特征和选定场景，构建详细的图像生成提示词。

**提示词模板**：

```
[角色面部描述], [发型描述], [服装描述], [场景描述], [表情描述], [姿势描述], [光线描述], high quality selfie photo, professional photography, [风格标签]
```

**角色固定描述**：

```
beautiful young East Asian woman, oval face shape, porcelain fair skin with rosy cheeks, small refined nose, bright infectious smile, large expressive almond-shaped dark eyes with aegyo-sal, long wavy jet-black hair with wispy see-through bangs, wearing white crew-neck t-shirt with black-and-white grid-patterned sweater draped over shoulders, natural "no-makeup" makeup look
```

**示例提示词**：

| 场景 | 表情 | 提示词 |
|------|------|--------|
| 海滩日落 | 灿烂笑容 | [角色描述], standing on a golden beach at sunset, bright radiant smile showing teeth, slightly tilted head, warm golden hour lighting, holding hair in wind, wearing white dress instead of sweater, professional travel selfie photo, authentic and lively expression |
| 咖啡馆 | 温柔凝视 | [角色描述], sitting in a cozy vintage cafe with warm lighting, soft gentle smile, holding a ceramic coffee cup with both hands, natural window light, contemplative gaze looking at camera, wearing cozy cardigan, candid selfie style, warm atmosphere |
| 赛博朋克 | 酷感表情 | [角色描述], with subtle blue hair highlights added, standing in neon-lit cyberpunk city at night, cool confident expression with slight smirk, leaning against railing, dramatic neon lighting reflections, wearing futuristic leather jacket over white top, cinematic composition, high-tech aesthetic |
| 樱花树下 | 优雅微笑 | [角色描述], standing under cherry blossom trees with pink petals falling, elegant gentle closed-lip smile, soft pink flower petals in hair, gentle breeze effect, warm spring sunlight, wearing romantic white dress, dreamy Japanese spring atmosphere, professional portrait photography |
| 复古胶片 | 沉思表情 | [角色描述], in vintage 35mm film photography style, contemplative expression looking away, grainy film texture, warm faded tones, sepia undertones, wearing vintage striped t-shirt, sitting on old wooden bench in autumn park, nostalgic and artistic mood |

### 步骤4：图像生成

使用 `image_synthesize` 工具生成最终图片：

**必填参数**：
- `prompt`: 构建好的提示词（包含角色固定描述）
- `input_files`: 角色固定图片 `/workspace/user_input_files/clawra.png`
- `output_file`: 输出文件路径（如 `selfies/beach_sunset.png`）

**可选参数**：
- `aspect_ratio`: "1:1"（头像自拍）、"3:4"（竖版）、"16:9"（横版）
- `resolution`: "1K"（快速预览）、"2K"（高清）

### 步骤5：输出与交付

**交付内容**：
1. 生成的场景自拍照
2. 简要说明（场景类型、表情风格、光线特点）

**确认机制**：
- 询问用户是否满意当前效果
- 如需调整，可修改：场景、表情、光线、风格等
- 可连续生成多组不同场景的照片

## 高级功能

### 批量生成模式

当用户要求"生成多张"或"不同场景"时：

1. **批量数量**：默认3-5张不同场景
2. **场景分配**：确保场景多样性（自然+城市+室内+创意混搭）
3. **表情轮换**：每张照片必须使用不同的表情类型
4. **并行生成**：使用 `image_synthesize` 批量提交多个任务

**批量生成示例**：

用户：生成5张不同场景的自拍照

生成计划：
| 序号 | 场景类别 | 具体场景 | 表情 | 角度 |
|------|---------|---------|------|------|
| 1 | 自然风光 | 海滩日落 | 灿烂笑容 | 侧面回眸 |
| 2 | 城市建筑 | 咖啡馆 | 温柔凝视 | 正面 |
| 3 | 创意风格 | 赛博朋克 | 酷感表情 | 倚靠姿势 |
| 4 | 室内环境 | 阳光卧室 | 俏皮表情 | 托腮 |
| 5 | 旅行打卡 | 樱花树下 | 优雅微笑 | 低头浅笑 |

### 风格迁移

支持以下风格转换：

| 风格名称 | 特点描述 | 适用场景 |
|---------|---------|---------|
| 清新自然 | 柔和光线、自然妆容、生活化场景 | 日常自拍、居家照 |
| 复古胶片 | 颗粒感、褪色色调、暖色系 | 文艺场景、怀旧风格 |
| 电影感 | 宽比例、戏剧性光线、深景深 | 氛围感大片 |
| 赛博朋克 | 霓虹灯、未来感、强烈对比 | 创意时尚 |
| 水墨国风 | 中国风元素、淡雅色调 | 传统节日、古风 |
| 油画感 | 古典油画风格、厚重质感 | 艺术肖像 |

## 表情详细系统

### 表情生成规则

**核心原则**：避免重复使用相同表情，确保每次生成都有新鲜感

**表情类型详解**：

| 表情类型 | 视觉特征 | 英文描述 | 适配场景 |
|---------|---------|---------|---------|
| 灿烂笑容 | 露齿笑，眼睛眯起，阳光活力 | bright radiant smile, showing teeth, eyes crinkling with joy | 海滩、户外、开心时刻 |
| 优雅微笑 | 嘴角上扬，温婉含蓄 | elegant gentle closed-lip smile, subtle and graceful | 室内、正式场合 |
| 酷感表情 | 淡定略带距离，神秘帅气 | cool confident expression, slight smirk, nonchalant | 街拍、时尚、创意 |
| 温柔凝视 | 眼神专注，柔情似水 | soft gazing eyes, tender look, looking directly into lens | 浪漫场景、特写 |
| 俏皮表情 | 活泼可爱，古灵精怪 | playful wink, mischievous grin, tongue out slightly | 生活照、可爱场景 |
| 沉思表情 | 若有所思，安静内敛 | contemplative, looking away thoughtfully, pensive | 文艺场景、阅读 |
| 自信表情 | 气场强大，充满力量 | confident power pose, direct eye contact, strong posture | 职业照、演讲 |

### 复合表情变体

| 表情组合 | 描述 | 使用场景 |
|---------|------|---------|
| 微笑+侧头 | Gentle smile with head tilted | 甜美可爱风 |
| 笑容+手势 | Smile with peace sign/victory sign | 活泼自然 |
| 冷酷+回眸 | Cool expression looking over shoulder | 时尚街拍 |
| 凝视+手托腮 | Soft gaze with hand on chin | 文艺气质 |
| 大笑+跳跃 | Big laugh with jumping pose | 活力运动 |

## 服装适配规则

**原则**：根据场景调整服装，保持角色特征的同时适配场景氛围

| 场景类型 | 服装建议 |
|---------|---------|
| 海滩/度假 | 白色连衣裙、泳装罩衫、度假风长裙 |
| 咖啡馆/书店 | 针织开衫、文艺衬衫、学院风 |
| 城市街拍 | 皮夹克、时尚外套、休闲套装 |
| 赛博朋克 | 未来感服装、LED装备、科幻元素 |
| 复古胶片 | 复古连衣裙、格子衬衫、vintage装 |
| 水墨国风 | 汉服、旗袍、民族风服装 |

**注意**：服装变化时必须保留白色T恤作为内搭基础

## 使用示例

### 示例1：用户请求特定场景

**用户**：生成一张在海边的自拍照

**执行流程**：
1. 确定场景：海滩日落
2. 选择表情：灿烂笑容（避免使用上次的表情）
3. 构建提示词：融入角色特征+场景+表情
4. 生成并交付

### 示例2：批量生成

**用户**：帮我生成5张不同场景的照片

**执行流程**：
1. 规划5个不同类别场景
2. 分配5种不同表情
3. 规划5种不同姿势/角度
4. 并行生成5张图片
5. 批量展示交付

### 示例3：指定风格

**用户**：生成一张赛博朋克风格的照片

**执行流程**：
1. 确定风格：赛博朋克
2. 选择场景：霓虹城市夜景
3. 选择表情：酷感表情
4. 调整服装描述
5. 生成并交付

## 错误处理

### 常见问题与解决

**问题1**：生成图片与角色特征不一致
- 解决：强化提示词中的角色特征描述
- 使用input_files传入角色原图

**问题2**：表情不够自然
- 解决：使用更具体的表情描述词
- 添加"自然"、"真实"等修饰词

**问题3**：场景与角色风格不搭
- 解决：调整服装描述以适配场景
- 添加场景氛围描述词

## 注意事项

1. **角色一致性**：必须使用clawra.png作为基础图片
2. **表情多样性**：每次生成必须选择不同的表情类型
3. **场景适配**：根据场景调整服装描述
4. **质量优先**：优先使用高清分辨率

## 技术依赖

- `image_synthesize`: 图像生成工具
- 角色基础图片：`/workspace/user_input_files/clawra.png`
