# 产线 C｜分镜三步搞定影视感

固定三步，**不要跳步**。跳步的结果就是"AI 味视频"——单张好看但串起来很假。

---

## 第 1 步｜定"审美基调"

写一段定调提示词，锁定镜头语言、焦段、光、画幅。**这一段是全片的地基**，后面每个分镜都从它派生。

必备要素：

| 要素 | 作用 | 示例 |
|---|---|---|
| 镜头类型 | 定视点 | `A long low-angle tracking shot of` |
| 主体动作 | 定事件 | `a sleek black SUV speeding along a dusty desert road` |
| 环境细节 | 定空间 | `heat haze rippling in the distance` |
| 动态质感 | 定真实度 | `fast motion blur on the road surface` |
| 光 | 定调性 | `warm golden hour light` |
| 摄影标签 | 定媒介 | `cinematography, shot on 35mm anamorphic lens` |
| 画幅 | 定构图 | `8K, --ar 21:9 --style raw` |

**固定尾巴**：`8K, --ar 16:9 --style raw`（或按需换画幅）。`--style raw` 是影视感的关键，别省。

---

## 第 2 步｜造"多景别分身"

用**图生图**（模型风格选 Nano Banana 一类的高一致图生图模型）基于第 1 步的定调图，造出分镜图。

### 景别库

| 景别 | 英文 | 用途 |
|---|---|---|
| 大远景 | extreme wide shot | 交代环境与规模感 |
| 远景 | wide shot | 人与环境关系 |
| 全景 | full shot | 完整人物动作 |
| 中景 | medium shot | 上半身 + 手部动作 |
| 近景 | medium close-up | 表情与情绪 |
| 特写 | close-up | 关键细节（手、眼睛、材质） |
| 大特写 | extreme close-up | 极致质感 |
| 仰视 | low-angle shot | 强化主体宏大 |
| 俯视 | high-angle shot | 交代地理关系 |
| 过肩 | over-the-shoulder | 对话/第三人视角 |

### 数量

**默认 3 个分镜**：`远景/全景（定场）` → `中景（叙事）` → `近景/特写（情绪或细节）`。

复杂内容可扩到 4–5 个，但每个分镜必须承担**不同的叙事职能**，不要只是换角度。

### 描述文案写法

每个分镜配一句**中文描述**（12–20 字），说明这一镜在讲什么。描述文案会直接变成第 3 步的视频提示词。

> 远处的雪山全景
> 登山者攀登的近景，细腻展示人物的动作
> 从山脚下仰视登山者的背影

---

## 第 3 步｜让"分镜动起来"

每个分镜配一段视频提示词 = **运镜 + 节奏 + 氛围**。

### 运镜库

| 类型 | 描述文案写法 |
|---|---|
| 固定镜头 | 镜头保持静止，让环境自然变化 |
| 推进 | 镜头从远景缓缓向前推进 |
| 拉远 | 镜头缓缓拉远，揭示更大场景 |
| 跟拍 | 跟随主体移动，保持主体在画面中 |
| 环绕 | 镜头缓缓环绕主体一圈，细腻展示…的动作 |
| 摇摄 | 镜头从左向右平移扫过 |
| 升降 | 镜头缓缓上升/下降 |
| 手持 | 轻微手持晃动，纪实感 |
| 侧跟 | 侧后方的跟拍，捕捉到主体的细节纹理 |

### 节奏

短句写清楚**快慢**：缓缓 / 快速 / 逐渐 / 突然。缺节奏的提示词会生成呆板的匀速运动。

### 氛围

从 `de-ai-flavor.md` 的随机词库里取 1–2 个（光影/氛围/环境类，**不要用静态肤色缺陷类**）。

### 完整拆解示例

| # | 景别 | 中文描述 | 运镜 | 视频提示词 |
|---|---|---|---|---|
| 1 | 远景 | 镜头从低角度缓缓向前推进 | 推进 | 镜头从低角度缓缓向前推进，尘埃在阳光中漂浮，暖金色黄昏氛围 |
| 2 | 全景 | 车身从画面中快速驶过，带起漫天沙尘 | 跟拍 | 车身从画面中快速驶过，带起漫天沙尘，动态模糊，热浪扭曲感 |
| 3 | 近景 | 侧后方的跟拍，捕捉到车身的细节纹理 | 侧跟 | 侧后方的跟拍，捕捉到车身的细节纹理与反光，尘土颗粒在光束中漂浮 |

---

## 6 个完整案例

### 案例 1｜汽车疾驰（沙漠落日）

**第 1 步 · 审美基调**
```
A long low-angle tracking shot of a sleek black SUV speeding along a dusty desert road at sunset, wheels kicking up sand and dust, low sun flaring directly into the lens, heat haze rippling in the distance, dramatic wide landscape, fast motion blur on the road surface, shallow depth of field, warm golden hour light, cinematography, shot on 35mm anamorphic lens, 8K, --ar 21:9 --style raw
```

**第 2 步 · 多景别分身**（模型风格：Midjourney）
| # | 中文描述 |
|---|---|
| 1 | 镜头从低角度缓缓向前推进 |
| 2 | 车身从画面中快速驶过，带起漫天沙尘 |
| 3 | 侧后方的跟拍，捕捉到车身的细节纹理 |

**第 3 步 · 让分镜动起来**：见上表。

---

### 案例 2｜攀登雪山

**第 1 步**
```
A cinematic wide shot of a lone climber in a bright red jacket ascending a steep snowy ridge, kicking up light powder snow with each step, jagged peaks piercing the clouds behind, crisp air, golden light raking across the snow, breath visible in the cold, extreme scale contrast between the tiny human figure and the massive mountain, shot on 24mm lens, 8K, --ar 16:9 --style raw
```

**第 2 步**
| # | 中文描述 | 运镜类型 |
|---|---|---|
| 1 | 远处的雪山全景 | 固定镜头 |
| 2 | 登山者攀登的近景，细腻展示人物的动作 | 环绕镜头 |
| 3 | 从山脚下仰视登山者的背影 | 环绕镜头 |

---

### 案例 3｜女生跳舞

**第 1 步**
```
A graceful young Asian dancer mid-twirl, silk dress and long hair flowing dynamically, leaping slightly, arms extended like wings, motion blur on the dress hem, soft cinematic lighting, shallow depth of field, 85mm lens, 8K, --ar 16:9 --style raw
```

**第 2 步**
| # | 中文描述 | 运镜类型 |
|---|---|---|
| 1 | Medium shot of the dancer's upper body | 固定镜头 |
| 2 | Close-up portrait of a woman's face | 环绕镜头 |
| 3 | 全身镜头，展示裙摆的飘动 | 环绕镜头 |

> 注意第 2 步的"中文描述"本身就是中英混写的定调图提示词——**分镜描述可以直接用英文画格提示词**，模型识别更准。

---

### 案例 4｜巨浪与船只（暴雨夜）

**第 1 步 · 审美基调**
```
Massive waves crashing violently onto cargo ship decks, stormy night, lightning striking, illuminating the dark rolling waves, water droplets flying, high-tech color palette, dramatic light and shadow definition, epic composition, cinematic, dark moody, 8K, --ar 16:9 --style raw
```

**第 3 步 · 三镜视频提示词**（每镜都有独立的完整提示词，不复用第一段）
```
Close-up of crew member's hands gripping the ship's railing tightly, water droplets sliding down the rusty, metal surface, dramatic cinematic light and shadow, detailed water droplets, dramatic side lighting, cinematic portrait photography, ultra-detailed, 8K, --ar 16:9 --style raw
```
```
Large cargo ship struggling in massive waves during a stormy night, professional photography, highly detailed, dramatic cinematic, color grading, turbulent ocean, wave splash, storm clouds, dark turbulent ocean waves, motion blur, 8K, --ar 16:9 --style raw
```
> 铁律：**每个分镜给一段独立完整的提示词**，不要写"同上"或只写差异部分。

---

### 案例 5｜孩子放风筝

**第 1 步**
```
Sunny spring afternoon in a vast meadow, a young child running joyfully in an orange shirt, holding the string of a yellow kite soaring high in a clear blue sky, lush green grass, warm golden sunlight, dreamy and playful atmosphere, shot on 50mm lens, 8K, --ar 16:9 --style raw
```

**第 2 步 · 特写分镜**
```
Low angle close-up of a child's hand tightly gripping the kite string, wind pulling the string taut, fibers of the string visible, sunlight catching the string, shallow depth of field, warm tone, 8K, --ar 16:9 --style raw
```
- 中文描述：微距镜头特写，捕捉风筝的细节纹理
- 运镜：固定镜头

---

### 案例 6｜采蘑菇（中文场景，模型选 Nano Banana）

**第 1 步**
```
秋日森林深处，一个穿着旧棕色长外套的采蘑菇人，微微弯腰蹲在地上寻找蘑菇，森林光影斑驳，色调沉稳，8K
```

**第 2 步 · 多景别分身**
- 细分镜：细腻展示竹篮细节，展现其木质纹理和编织结构
- 视频：镜头缓缓环绕人物一圈，细腻展示人物蹲地寻找的动作，森林光斑在人物身上缓缓移动

---

## 交付格式

分镜表一行一镜，必须含：**编号 / 景别 / 中文描述 / 运镜 / 视频提示词**。

```
| # | 景别 | 中文描述 | 运镜 | 视频提示词 |
|---|---|---|---|---|
| 1 | 远景 | ... | 推进 | ... |
| 2 | 全景 | ... | 跟拍 | ... |
| 3 | 特写 | ... | 固定镜头 | ... |
```

表格后附一段完整的第 1 步定调提示词（中英）。
