---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: ffe355d4556c2228206b8afe4ef7622b
    PropagateID: ffe355d4556c2228206b8afe4ef7622b
    ReservedCode1: 304502202aff8eef02ca545bf627c39d5c030002094ce4f63b973ec4565d13824ed8b1a8022100be8876e82b1bcfc52080fc62d32c26058c7e1442c2c1f87541eb83d18f99d2d2
    ReservedCode2: 3045022039f8c94e00b052ed28624694c512bde571c9087c2690777f27d40c5bc4f55cc4022100b9f7a8794d133ab9a7435374715cdc1504e5c905bdc92b767ba81c8621b78d34
description: 图生视频提示词生成器，用于AI短片创作。当用户上传首帧图片（或首帧+尾帧，或多张参考图）并给出镜头时长与运动描述时，生成Kling最佳中文提示词和Veo英文JSON格式提示词。若用户的运镜描述跨越多个时间段（如"0–1s：镜头拉近；2–4s：镜头环绕；5–7s：切至另一场景"），须将每个时间段的起止时间、运镜方式、主体动作、光影变化全部合并为一段连续完整的提示词，合并输出，禁止将各时间段拆分为多个独立段落。输出内容须能一键直接复制全部使用。
name: video-prompt-generator
---

# 图生视频提示词生成器

## 技能定位

擅长高质量AI短片的提示词生成。输入内容为视频时长、首帧图片（或首帧+尾帧，或多张参考图），输出 Kling 中文自然语言提示词和 Veo 英文 JSON 格式提示词。

**输入内容**：视频时长 + 首帧图片（或首帧+尾帧，或多张参考图）+ 镜头运动描述

**输出内容**：Kling 中文提示词 + Veo 英文 JSON 提示词（两大平台并行输出，可一键直接复制全部内容）

---

## 核心工作流程

### 第一步：图像深度分析

**观察并系统提取以下要素：**

1. **场景分析**
   - 室内 / 室外 / 半室内外
   - 具体环境（宴会厅、街道、建筑、自然等）
   - 背景复杂度与层次
   - 空间纵深关系
   - 装饰元素与道具

2. **主体形象**
   - 人物数量、各自身份（新娘/新郎/伴娘等）
   - 外貌特征、面部表情
   - 服装颜色与材质（婚纱/西装/礼服等）
   - 主体位置、朝向、与背景的关系

3. **光影氛围**
   - 光源类型（自然光/人工光/混合光）
   - 光线方向（顺光/侧光/逆光/顶光/正前方光）
   - 光质（硬光/软光/柔光/斑驳光）
   - 色调与氛围（暖调/冷调/莫兰迪色系/胶片感等）

4. **动态元素**
   - 人物肢体动作与姿态
   - 服饰飘动（婚纱裙摆/披肩/丝带）
   - 环境中可动的元素（布料/光影/树叶/水面等）

---

### 第二步：运镜方式映射

根据用户的运镜描述，对应转换为专业术语：

**一、推拉类（空间纵深变化）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 向前推进 | 推镜头 / 向前推进 / 前移 | Dolly in / Push in / Camera moves forward |
| 向后拉远 | 拉镜头 / 向后拉远 / 后移 | Dolly out / Pull back / Camera moves backward |
| 快速推进 | 快速推进 | Fast push in / Rapid dolly in |
| 缓慢推进 | 缓慢推进 | Slow push in / Gentle dolly in |
| 推进至特写 | 推进至特写 | Push in to close-up |
| 拉远至全景 | 拉远至全景 | Pull back to wide shot |

**二、平移类（水平移动）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 向左移动 | 向左平移 | Truck left / Track left / Slide left |
| 向右移动 | 向右平移 | Truck right / Track right / Slide right |
| 横向跟随 | 横向跟随 | Side tracking shot / Lateral tracking |
| 平稳横移 | 平稳横移 | Smooth lateral move |
| 快速横移 | 快速横移 | Fast side move / Whip track |

**三、摇摄类（机位固定，镜头旋转）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 左右摇头 | 水平摇摄 | Pan left / Pan right |
| 上下摇头 | 垂直摇摄 | Tilt up / Tilt down |
| 慢速摇动 | 慢速摇摄 | Slow pan / Slow tilt |
| 快速甩镜 | 快速甩镜 | Whip pan / Fast pan |
| 跟随摇摄 | 跟随摇摄 | Follow pan / Tracking pan |

**四、升降类（垂直空间移动）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 镜头上升 | 上升镜头 | Boom up / Crane up / Rise up |
| 镜头下降 | 下降镜头 | Boom down / Crane down / Drop down |
| 缓慢上升 | 缓慢上升 | Slow crane up |
| 从高处下降 | 从高处下降 | Descending shot / Crane down from above |

**五、环绕类（围绕主体运动）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 绕着转 | 环绕镜头 | Orbit shot / Arc shot / Circular move |
| 顺时针环绕 | 顺时针环绕 | Clockwise orbit |
| 逆时针环绕 | 逆时针环绕 | Counterclockwise orbit |
| 半圈环绕 | 半环绕 | Half orbit / Semi-circle move |
| 环绕并拉远 | 环绕并拉远 | Orbit and pull back |
| 环绕并推进 | 环绕并推进 | Orbit and push in |

**六、跟拍类（跟随主体）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 跟随拍摄 | 跟随镜头 | Follow shot / Tracking shot |
| 跟拍人物前进 | 跟拍人物前进 | Follow subject walking forward |
| 后方跟拍 | 后方跟拍 | Rear tracking shot |
| 前方跟拍 | 前方跟拍 | Leading shot / Front tracking |
| 稳定跟拍 | 稳定跟拍 | Smooth tracking shot |

**七、复合运镜（组合动作）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 边推边环绕 | 推进 + 环绕 | Push in while orbiting |
| 边拉边升 | 拉远 + 上升 | Pull back while rising |
| 边移边跟 | 平移 + 跟拍 | Tracking sideways while following |
| 推进加摇动 | 推进 + 摇摄 | Push in with slight pan |
| 环绕上升 | 环绕 + 上升 | Orbit while crane up |
| 斜向推进 | 斜向推进 | Diagonal push in |
| 斜向拉远 | 斜向拉远 | Diagonal pull back |

**八、转场类🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 叠化转场 | 叠化 | Dissolve / Crossfade |
| 切镜 | 硬切 | Hard cut |
| 淡入淡出 | 淡入淡出 | Fade in / Fade out |
| 推进转场 | 推进过渡 | Push transition |

**九、固定镜头🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 机位固定不动 | 机位固定不动 | Camera remains stationary |
| 三脚架固定镜头 | 三脚架固定镜头 | Tripod shot / Tripod-mounted shot |
| 轻微手持感（伪固定） | 轻微手持感 | Subtle handheld feel |

**十、镜头节奏与质感🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 匀速运动 | 匀速运动 | Constant speed / Steady motion |
| 平滑运镜 | 平滑运镜 | Smooth camera movement |
| 缓慢电影感 | 缓慢电影感 | Slow cinematic movement |
| 自然流畅 | 自然流畅 | Natural and fluid motion |
| 稳定无抖动 | 稳定无抖动 | Stable / No camera shake |
| 单一连续镜头 | 单一连续镜头 | Single continuous shot / One take |
| 无剪辑 | 无剪辑 | No cuts |
| 电影感运镜 | 电影感运镜 | Cinematic camera movement |
| 真实摄影机运动 | 真实摄影机运动 | Realistic camera motion |
| 镜头对准主体 | 镜头对准主体 | Camera focused on subject |
| 镜头围绕主体展开 | 镜头围绕主体展开 | Camera moves around the subject |

**十一、稳定器类（无抖动专业控制）🔟**

| 运镜描述 | 专业术语 | 英文 |
|---------|---------|------|
| 手持稳定器拍摄 | 手持稳定器拍摄 | Shot with a handheld gimbal stabilizer |
| 稳定器镜头 | 稳定器镜头 | Gimbal-stabilized shot |
| 画面完全稳定 | 画面完全稳定 | Perfectly stable frame |
| 无任何抖动 | 无任何抖动 | No camera shake |
| 镜头极其平稳 | 镜头极其平稳 | Extremely smooth camera movement |
| 如同机械滑轨般稳定 | 如同机械滑轨般稳定 | Stable like a mechanical dolly |
| 无微抖动 | 无微抖动 | No micro jitter |
| 无漂移 | 无漂移 | No drifting |
| 无晃动 | 无晃动 | No wobble |
| 无呼吸感抖动 | 无呼吸感抖动 | No breathing motion |
| 锁定稳定 | 锁定稳定 | Locked stabilization |
| 运动丝滑顺畅 | 运动丝滑顺畅 | Silky smooth motion |

---

### 第三步：提示词撰写

#### 时段合并规则

若用户的运镜描述跨越**多个时间段**（如"0–1s：镜头拉近；2–4s：镜头环绕；5–7s：切至另一场景"），须将**所有时间段的全部内容合并为一段连续完整的提示词**，禁止将各时间段拆分为多个独立段落。所有时间信息、运镜变化、主体动作、光影变化须融合在一段连贯的自然语言中，顺序描述各时间段的递进关系，合并输出，一气呵成，**可一键直接复制全部内容**。

---

#### Kling 中文提示词输出格式

```
这是一个（场景类型）的画面，画面主体是（核心对象），整体构图为（景别 + 构图方式）。主体处于（状态/姿态），（具体动作或变化），动作幅度（很小 / 轻微 / 明显），节奏（缓慢 / 匀速 / 自然）。（若存在多个时间段，按时间顺序描述：0至Xs时，镜头（运镜方式），同时/随后/紧接着（主体具体动作和变化），运镜速度（缓慢/匀速/平稳），动作节奏（轻柔/缓慢/自然）；紧接着Xs至Ys时……以此类推）。环境中（风 / 光 / 材质 / 其他元素）产生（细微变化），例如（具体细节：轻微摆动 / 光影流动 / 颗粒漂浮等），整体变化自然真实不过度。镜头（固定 / 缓慢推进 / 缓慢拉远 / 环绕等），运镜方式为（具体路径），速度（缓慢 / 匀速 / 平稳），为一个连续镜头，无跳切。画面风格为（电影感 / 写实 / 柔和 / 高级感等），光线（柔和 / 自然 / 逆光等），色彩（统一 / 低饱和 / 暖色调等），画面干净克制。无突兀变化，无画面闪烁，无结构扭曲，无多余元素生成，不要出现额外物体，保持主体结构稳定，保持构图稳定。
```

---

#### Veo 英文 JSON 输出格式

```json
{
  "model": "veo-3",
  "input": {
    "type": "image_to_video",
    "video_settings": {
      "duration": "总时长（如6s）",
      "fps": 24,
      "resolution": "1920x1080",
      "aspect_ratio": "16:9"
    },
    "prompt": "A clear natural-language description of the scene, subject, and environment. Example: A romantic outdoor wedding arch decorated with soft pastel flowers, set in a garden during sunset with warm golden light. （若存在多个时间段，按时间顺序描述：0至Xs: camera movement and subject action；紧接着Xs至Ys: ...；以此类推，所有时间段合并为一段连贯自然语言）",
    "motion": "The camera performs [镜头运动描述]. Subject performs [主体动作描述]. Environment details [风/光/材质变化]. All movements continuous and stable. （若存在多个时间段，按时间顺序描述各段动作）",
    "camera": "shot type, lens, depth of field, focus, stabilization, movement path",
    "lighting": "lighting description with quality, direction, and color temperature",
    "style": "cinematic, elegant, high-end commercial look, realistic textures, soft color grading, film grain",
    "continuity": "single continuous shot, no cuts（或明确标注切镜位置）",
    "negative_prompt": "no shake, no flicker, no distortion, no artifacts, no unnatural motion, no unwanted objects"
  }
}
```

---

## 质量控制要点

**必须避免**
- 画面闪烁（Flicker）
- 结构扭曲（Distortion）
- 意外物体（Unwanted objects）
- 不自然运动（Unnatural motion）
- 跳切（Jump cuts，非指令切镜时）

**必须保持**
- 主体结构稳定
- 构图稳定
- 光影连贯
- 动作流畅
- 风格统一

---

## 输出要求

1. **信息完整性**：确保包含场景、主体、光影、运镜四大要素
2. **时段合并输出**：多时段描述须将所有时间段合并为一段连续完整提示词，禁止拆分多个独立段落，一键直接复制全部内容
3. **术语专业性**：使用标准影视术语
4. **语言自然性**：中文提示词流畅自然，英文提示词地道准确
5. **格式规范性**：严格按照指定格式输出，Kling与Veo并行给出
6. **可直接使用**：提示词应可直接复制使用，无需二次修改