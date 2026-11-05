# 风格预设详细指南

## 视觉风格详解

### 1. Cinematic (电影感)
**核心特征**：
- 宽幅比例 (2.39:1 或 16:9)
- 浅景深、电影感散景
- 胶片颗粒感
- 戏剧性光影
- 电影级色彩分级

**适用场景**：叙事性强的剧情短片、电影预告

**参数示例**：
```json
{
  "visual_style": "cinematic",
  "lens": "anamorphic 50mm",
  "color_grading": "teal_orange",
  "grain": "16mm film grain",
  "dof": "shallow with bokeh"
}
```

---

### 2. Anime (2D动漫)
**核心特征**：
- 清晰线条描边
- 高度饱和色彩
- 平面化阴影 (Cel-shading)
- 背景虚化
- 动漫摄影语言

**适用场景**：日漫风格短剧、动画短片、偶像MV

**参数示例**：
```json
{
  "visual_style": "anime",
  "render": "cel-shaded",
  "lineart": "clean black outlines",
  "colors": "vibrant_saturated",
  "atmosphere": "Studio_Ghibli"
}
```

---

### 3. Cyberpunk (赛博朋克)
**核心特征**：
- 霓虹光效
- 未来主义建筑
- 暗色调 + 高对比
- 数字/数据可视化元素
- 潮湿城市环境

**适用场景**：科幻短剧、科技产品展示、赛博朋克剧情

**参数示例**：
```json
{
  "visual_style": "cyberpunk",
  "colors": ["neon_blue", "neon_pink", "deep_purple"],
  "elements": ["holographic_displays", "rain_wet_streets", "towering_skyscrapers"],
  "atmosphere": "Blade_Runner",
  "lighting": "volumetric_neon"
}
```

---

### 4. Realistic (写实摄影)
**核心特征**：
- 自然光线
- 真实材质纹理
- 浅景深
- 纪录片质感
- 真实比例

**适用场景**：真实故事改编、纪录片风格、商业广告

**参数示例**：
```json
{
  "visual_style": "realistic",
  "lighting": "natural_daylight",
  "dof": "shallow_natural",
  "color": "natural_saturation",
  "texture": "photorealistic"
}
```

---

### 5. Oil Painting (油画质感)
**核心特征**：
- 笔触纹理
- 暖色调为主
- 柔和边缘过渡
- 古典构图
- 艺术化光影

**适用场景**：艺术短片、历史题材、审美类内容

**参数示例**：
```json
{
  "visual_style": "oil_painting",
  "texture": "visible_brushstrokes",
  "colors": "warm_romantic",
  "composition": "classical_renaissance",
  "lighting": "chiaroscuro"
}
```

---

### 6. Pixar 3D (皮克斯3D)
**核心特征**：
- 圆润建模
- 活力配色
- 丰富表情
- 毛发/布料仿真
- 温暖叙事感

**适用场景**：家庭娱乐、儿童内容、可爱风格短剧

**参数示例**：
```json
{
  "visual_style": "pixar_3d",
  "modeling": "rounded_soft_edges",
  "colors": "vibrant_family_friendly",
  "expression": "exaggerated_emotions",
  "render": "disney_pixar_quality"
}
```

---

## 运镜控制详解

### 基础运镜

| 运镜 | 效果 | Prompt写法 |
|-----|------|----------|
| **推 (Push In)** | 聚焦紧张感，逐渐逼近主体 | `dolly forward slowly, push into subject` |
| **拉 (Pull Out)** | 揭示环境，释放情绪 | `dolly backward, reveal the surroundings` |
| **摇 (Pan)** | 横向扫视 | `pan slowly to the right, revealing the corridor` |
| **移 (Truck)** | 横向跟随 | `truck shot following the runner` |

### 进阶运镜

| 运镜 | 效果 | Prompt写法 |
|-----|------|----------|
| **跟 (Track)** | 跟随主体移动 | `tracking shot, follow behind the figure` |
| **升降 (Crane)** | 垂直视角变化 | `crane up dramatically, rising above the scene` |
| **环绕 (Orbit)** | 绕主体旋转 | `orbit around the character, 360° sweep` |
| **POV** | 主观视角 | `first person POV, running forward` |

### 特殊效果

| 效果 | Prompt写法 |
|-----|----------|
| 慢动作 | `in slow motion, 120fps, cinematic slow-mo` |
| 快节奏 | `time-lapse, rapid cuts, high energy` |
| 手持感 | `handheld camera, subtle shake, documentary feel` |
| 稳定器 | `gimbal stabilized, smooth gliding movement` |

---

## 情感基调应用

### 欢快 (Joyful)
**视觉表现**：
- 明亮色调
- 暖色光
- 快节奏剪辑
- 正面构图

**Prompt后缀**：
```
, bright and cheerful, warm sunlight, upbeat mood,
vibrant colors, children laughing, joyful atmosphere
```

---

### 忧郁 (Melancholic)
**视觉表现**：
- 冷色调
- 低饱和度
- 慢动作
- 大量留白

**Prompt后缀**：
```
, melancholic atmosphere, overcast sky, muted colors,
lonely feeling, contemplative mood, rain falling
```

---

### 紧张 (Tense)
**视觉表现**：
- 高对比
- 快速剪辑
- 手持晃动
- 低角度

**Prompt后缀**：
```
, tense atmosphere, high contrast, building tension,
rapid breathing, danger approaching, ominous shadows
```

---

### 史诗 (Epic)
**视觉表现**：
- 航拍全景
- 宽幅构图
- 壮阔风景
- 神圣光效

**Prompt后缀**：
```
, epic scale, majestic scenery, heroic lighting,
legendary atmosphere, orchestral feeling, grand composition
```

---

### 温馨 (Cozy)
**视觉表现**：
- 柔光
- 暖色调
- 小景深
- 家庭场景

**Prompt后缀**：
```
, cozy and warm, soft diffused lighting, intimate setting,
gentle atmosphere, home feeling, heartwarming mood
```

---

## 比例适配指南

| 比例 | 场景数 | 分镜数 | 建议时长 |
|-----|-------|-------|---------|
| **16:9** | 3-4 | 6-8 | 15-30s |
| **9:16** | 2-3 | 4-6 | 10-15s |
| **1:1** | 1-2 | 2-4 | 5-10s |

### 16:9 横屏优化
- 优先使用全景和中景
- 利用宽度展示环境
- 适合横向运动镜头

### 9:16 竖屏优化
- 优先使用特写和中景
- 利用高度展示纵向场景
- 适合人物全身和环境上下延伸

### 1:1 方屏优化
- 优先使用中心构图
- 适合静态画面展示
- 社交媒体封面首选
