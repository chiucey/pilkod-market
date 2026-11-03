---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 88959f2e8ea976cb2e39da2c283f68d7
    PropagateID: 88959f2e8ea976cb2e39da2c283f68d7
    ReservedCode1: 30450221009d2f6d1bb7fc9592f4c877b8acb693a2298f37c85a387ae834edf4522075ab8a02201d2307a08c950342d54a6fa00cd741c9895bc449c3741a10bdb36f97c363f8ed
    ReservedCode2: 3046022100e0bd182fad0ef70ed029fd753ccf7edfe7db235bd45d3dd401bacc25ee663473022100930b825d8b601f3a237ea7c39a72848818e0e77656d093b51e290c94282f23df
description: 提取短剧人物三视图和小说场景的工具。帮助从小说或剧本中提取人物三视图和场景。关键词：提取人物、提取三视图、提取场景、人物三视图、小说三视图、小说场景。当用户说要提取人物、提取三视图、提取场景，或提到人物+三视图、小说+三视图、小说+场景时触发。生成多张独立图片（非三合一）。
name: drama-person-scene-prompt
---

# 小说短剧人物与场景提示词生成器

## 核心功能

从小说章节或剧本内容中，智能提取核心人物和场景，分别生成适配AI绘画的**人物三视图提示词**和**场景描述提示词**。

## 使用方式

### 用法1：默认指令（仅生成提示词）

当用户提供章节内容，要求生成人物和场景提示词时，执行以下流程：

**1. 人物提示词生成规则**

| 要素 | 要求 | 示例 |
|------|------|------|
| 外貌 | 脸型、五官、发型、身高、肤色具体描述 | "鹅蛋脸，眉眼温婉，黑长直发约170cm，瓷白肌肤" |
| 穿搭 | 风格、颜色、细节，贴合时代/题材 | "浅灰色羊绒大衣，内搭米白针织衫，黑色细高跟鞋" |
| 性格体现 | 通过外貌/穿搭暗示性格 | "温柔知性→穿搭简约素雅；干练利落→职业套装+手表" |
| 核心特征 | 辨识度强的细节（可选） | "戴细框眼镜、扎低马尾、手腕戴银镯" |

**输出格式：**

```
【人物N：身份名称】
- 性别/年龄范围：[如：女性/25-30岁]
- 外貌描述：[详细外貌描写，适配三视图]
- 穿搭描述：[具体穿搭风格和颜色]
- 性格特质：[通过外貌体现的性格]
- 辨识细节：[核心特征/配饰]
- 提示词（英文，适合AI绘图）：
"[Full body shot, 3 views: front, side, back], [具体外貌], [具体穿搭], [背景：纯色或简单布景], [画质要求], [风格标签]"
```

**2. 场景提示词生成规则**

| 要素 | 要求 | 示例 |
|------|------|------|
| 场景类型 | 明确场景名称 | "现代写字楼大厅、深夜小雨街道" |
| 场景细节 | 布局、家具、装饰、光线 | "落地玻璃窗、暖黄灯光、皮质沙发" |
| 场景氛围 | 情感基调 | "温馨暖光、清冷悬疑、热闹市井" |
| 剧情关联 | 标注适配的剧情片段 | "适配：主角初遇、雨夜送伞情节" |

**输出格式：**

```
【场景N：场景名称】
- 场景类型：[如：现代都市/古风/校园等]
- 场景细节：[布局、家具、光线等]
- 氛围基调：[情感氛围描述]
- 适配剧情：[对应的剧情片段]
- 提示词（英文，适合AI绘图）：
"[具体场景描述], [光线氛围], [色调风格], [画质要求], [构图要求]"
```

**3. 生成后确认**

生成完所有人物和场景提示词后，**不要自动生成图片**，而是询问用户：

> "提示词已生成完毕。请问需要先按照第一个提示词生成图片吗？"

等待用户确认后，再执行图片生成。

### 用法2：根据提示词生成三视图/场景图

当用户提供提示词并要求生成图片时，执行以下规则：

**判断条件：**
- 如果提示词包含"三视图"、"人物"、"角色"、"character"、"three view"等关键词 → 生成人物三视图
- 如果提示词包含"场景"、"scene"、"背景"等关键词 → 生成场景图

**图片生成规则：**

| 类型 | 生成数量 | 背景要求 | 示例 |
|------|----------|----------|------|
| 人物/角色三视图 | 3张 | 纯白色背景 | 正面、侧面、背面各1张 |
| 场景图 | 4张 | 贴合场景氛围 | 远景、近景、正面、侧面 |

**示例触发语：**
- "根据这个提示词生成三视图"
- "复制人物的女角色提示词，请帮我生成三视图"
- "根据场景提示词生成图片"

### 用法3：自定义指令生成

用户可以直接使用自定义指令生成三视图和场景图，默认按照标准模板生成。

---

## 标准模板

### 人物三视图提示词模板

```
[Full body shot, 3 views: front view, side view, back view],
[a beautiful Chinese woman, ovals face, gentle eyes, long black straight hair to waist, 170cm tall, porcelain pale skin, delicate features],
[wearing [具体穿搭描述], [颜色搭配], [配饰细节]],
[white background],
[ultra detailed, high quality, 4k, soft lighting],
[ultra realistic, photorealistic, hyperrealistic, high resolution photography]
```

### 场景图提示词模板

```
[具体场景描述],
[详细环境布置],
[光线氛围：如warm golden light, rainy night atmosphere],
[色调：如cinematic, moody, warm tones],
[ultra detailed, high quality, 4k, architectural visualization],
[电影感构图, 氛围感强]
```

---

## 默认风格设置

### 风格选择规则

当用户**未指定图片风格**时，默认使用**仿真人摄影风格**生成图片。

**默认禁用**：插画风格、时尚插画风格（除非用户明确指定）

| 风格选项 | 适用场景 | 关键词 |
|----------|----------|--------|
| **仿真人摄影风格（默认）** | 人物三视图、角色设计 | realistic, photorealistic, ultra realistic, photography |
| 3D动漫风格 | 动漫角色、游戏角色 | 3D anime, Pixar style, Disney style |
| 二次元风格 | 日系插画、轻小说 | anime, manga style, illustration |
| 古风风格 | 古装人物、历史场景 | traditional Chinese style, ancient |
| 插画/时尚插画风格 | 用户明确指定 | illustration, fashion illustration, digital art |

### 风格指定方式

用户可通过以下方式指定风格：
- 明确说明："请用3D动漫风格生成"
- 修改提示词：在提示词末尾添加风格标签
- 自定义描述：描述期望的画面风格

### 提示词风格标签示例

```
# 仿真人摄影风格（默认）
ultra realistic, photorealistic, 4k, high resolution photography, professional portrait

# 3D动漫风格
3D render, Pixar style, Disney animation, soft lighting

# 二次元风格
anime style, manga illustration, cel shading, vibrant colors

# 古风风格
traditional Chinese painting style, ink wash, classical Chinese aesthetics

# 插画风格（需明确指定）
digital illustration, fashion illustration, vector art style
```

---

## 示例演示

### 输入示例

```
林晚加班到深夜，走出写字楼时，天下着小雨，她没带伞，正手足无措站在门口，
忽然一把黑色雨伞举到她头顶。回头一看，是公司的顶流设计师沈砚，他穿着剪裁得体的
黑色西装，脸上没什么表情，只淡淡说了一句："顺路，我送你。"
林晚愣住，脸颊瞬间泛红，连忙摆手："不用不用，沈老师，我等雨小一点就好。"
沈砚却没收回伞，眼神落在她湿透的袖口，语气依旧平淡："走吧，别感冒了。"
```

### 输出示例

---

**【人物1：林晚】**
- 性别/年龄范围：女性/24-28岁
- 外貌描述：鹅蛋脸，眉眼温婉柔和，眼神略带羞涩，黑长直发约170cm，瓷白肌肤，表情青涩
- 穿搭描述：职业通勤装，浅灰色西装外套，内搭白色衬衫，黑色职业裙，黑色细高跟鞋，袖口微湿
- 性格特质：温柔内敛、略带羞涩、初入职场的新人气质
- 辨识细节：手腕戴简约银色手链，随身带帆布托特包
- 提示词（英文）：
```
[Full body shot, 3 views: front view, side view, back view],
[a beautiful young Chinese woman, oval face, gentle shy eyes, long black straight hair to waist, 170cm tall, porcelain pale skin, fresh and youthful appearance],
[wearing light grey blazer over white shirt, black pencil skirt, black stiletto heels, silver bracelet on wrist, slightly wet sleeves],
[white background],
[ultra detailed, high quality, 4k, soft lighting],
[ultra realistic, photorealistic, hyperrealistic, high resolution photography]
```

**【人物2：沈砚】**
- 性别/年龄范围：男性/30-35岁
- 外貌描述：棱角分明的俊朗脸庞，剑眉星目，表情冷淡疏离，黑色短发约182cm，身姿挺拔
- 穿搭描述：剪裁考究的黑色西装套装，白色衬衫，深色领带，黑色牛津皮鞋
- 性格特质：冷峻内敛、高冷矜持、成熟稳重的设计师气质
- 辨识细节：手腕戴简约机械表，手持黑色长柄伞
- 提示词（英文）：
```
[Full body shot, 3 views: front view, side view, back view],
[a handsome Chinese man, sharp angular face, determined eyes, short black hair, 182cm tall, tall and straight posture, cold and aloof expression],
[wearing well-tailored black suit, white dress shirt, dark tie, black Oxford shoes, carrying a black long-handle umbrella],
[white background],
[ultra detailed, high quality, 4k, professional lighting],
[ultra realistic, photorealistic, hyperrealistic, high resolution photography]
```

---

**【场景1：深夜写字楼大厅】**
- 场景类型：现代都市/职场
- 场景细节：落地玻璃门窗、暖黄射灯、大理石地面、皮质等候沙发、前台绿植、门口有台阶
- 氛围基调：深夜冷清、暖黄灯光、略带孤独感
- 适配剧情：林晚加班结束走出公司
- 提示词（英文）：
```
[Modern office building lobby at night],
[glass floor-to-ceiling windows, warm yellow spotlights, marble floor, leather waiting sofa, reception desk with green plants, steps at entrance],
[soft warm lighting inside, dark rainy night visible through windows],
[cinematic, moody, warm interior tones contrasting with cold exterior],
[ultra detailed, high quality, 4k, architectural visualization],
[wide angle shot, atmospheric, lonely late night atmosphere]
```

**【场景2：雨夜街道】**
- 场景类型：现代都市/户外
- 场景细节：细雨蒙蒙、路灯昏黄、湿润的柏油路面、反光倒影、两侧写字楼、行道树
- 氛围基调：浪漫清冷、雨夜氛围、路灯暖光
- 适配剧情：沈砚为林晚撑伞雨中同行
- 提示词（英文）：
```
[Night street scene in light rain],
[wet asphalt road with light reflections, warm street lamps, modern office buildings on both sides, roadside trees, people with umbrellas],
[soft golden light from street lamps, drizzle falling],
[cinematic, romantic, cool blue and warm orange tones],
[ultra detailed, high quality, 4k, moody atmosphere],
[medium shot, shallow depth of field, romantic rainy night mood]
```

---

### 提示词示例

**人物提示词示例（林晚）：**
```
[Full body shot, 3 views: front view, side view, back view],
[a beautiful young Chinese woman, oval face, gentle shy eyes, long black straight hair to waist, 170cm tall, porcelain pale skin, fresh and youthful appearance],
[wearing light grey blazer over white shirt, black pencil skirt, black stiletto heels, silver bracelet on wrist, slightly wet sleeves],
[white background],
[ultra detailed, high quality, 4k, soft lighting],
[ultra realistic, photorealistic, hyperrealistic, high resolution photography]
```

---

## 注意事项

1. **提示词适配性**：生成的所有提示词均为英文，适合主流AI绘图工具（Midjourney、Stable Diffusion、DALL-E等）
2. **人物优先提取**：优先提取剧本中出现的主要角色，标注身份
3. **场景剧情匹配**：确保场景与人物形象、剧情调性一致
4. **细节具体化**：避免模糊描述，所有外貌、穿搭、场景元素均需具体
5. **默认风格规则**：未指定风格时，默认使用仿真人摄影风格，禁用插画/时尚插画风格
6. **默认分辨率**：未指定分辨率时，默认使用4K
7. **图片数量规则**：人物三视图生成3张（正面/侧面/背面），场景图生成4张（远景/近景/正面/侧面）
8. **生成后确认**：生成提示词后必须询问用户是否需要生成图片，**禁止自动生成**
9. **禁止三合一**：三视图必须是3张独立图片，禁止将三视图合并在一张图上
