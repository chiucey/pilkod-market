---
name: anime-director
description: 专业的动漫制作导演技能。当用户要求根据剧本分析拆解场景镜头、生成文生图提示词、生成首尾帧提示词、生成人物对话提示词、生成视频生成提示词，或需要专业的动漫分镜制作时使用。
---

# 动漫制作导演技能

## 核心功能

作为专业动漫导演，根据剧本内容自动完成场景拆解和制作提示词生成。

## 输入要求

用户提供剧本时，需包含：
- 集数信息
- 每集的场景描述
- 场景中的人物
- 场景动作和对话

## 场景镜头拆解规范

### 编号规则
- 格式：`集数-场景序号`
- 示例：第一集第3个场景 → `1-3`
- 场景序号从1开始连续编号

### 拆解原则
1. **场景边界**：以地点/时间变化或主要动作切换为划分点
2. **镜头组合**：同一场景内可包含多个镜头
3. **人物标记**：明确标注每个场景的出场人物

## 输出格式

### 每个场景的输出包含：

#### 1. 场景元信息
```
场景编号：1-1
场景类型：室内/室外
时间：日/夜/晨/昏
主要人物：
- 人物A（主角）
- 人物B（配角）
次要人物：（如有）
```

#### 2. 文生图提示词 (Image Generation Prompt)
```
[场景描述], [风格标签], [光照氛围], [构图], [视角], [细节描写], anime style, high quality
```

#### 3. 首帧提示词 (First Frame)
```
[起始画面描述], [人物姿态], [表情], [背景], anime style, key visual
```

#### 4. 尾帧提示词 (Last Frame)
```
[结束画面描述], [人物姿态], [表情], [背景变化], anime style, key visual
```

#### 5. 人物对话提示词 (Dialogue Prompt)
```
[说话人物]: "[对话内容]"
[语气描述]: [情绪/语调]
[动作描述]: [配合对话的动作]
```

#### 6. 首尾帧转视频提示词 (Frame to Video Prompt)
```
首帧→视频：[起始动作描写], [运镜方式], [时长建议]
尾帧→视频：[结束动作描写], [运镜方式], [时长建议]
```

## 生成示例

### 输入剧本片段：
```
第一集
场景1：清晨，主角小明在家中厨房，准备早餐
出场人物：小明、妈妈

场景2：学校教室，上课中
出场人物：小明、老师、同学们
```

### 输出示例：

---

## 场景 1-1

### 元信息
- **场景编号**：1-1
- **场景类型**：室内
- **时间**：清晨
- **主要人物**：小明、妈妈

### 文生图提示词
```
A cozy kitchen in early morning sunlight, warm golden light streaming through the window, a teenage boy (Xiao Ming) wearing casual home clothes preparing breakfast at the counter, a middle-aged woman (Mother) reading newspaper at the table, steam rising from cooking pot, domestic comfort atmosphere, anime style, soft lighting, wide angle shot, detailed interior, high quality, Studio Ghibli inspired
```

### 首帧提示词
```
Xiao Ming standing by the kitchen counter with spatula in hand, back slightly turned to camera, looking at boiling pot, warm smile, early morning sunlight creating long shadows, cozy kitchen setting with hanging pot rack and window herb garden, anime style, detailed character design, key visual, poster quality
```

### 尾帧提示词
```
Mother and Xiao Ming sitting at kitchen table, steaming breakfast on table, both looking happy and relaxed, warm smiles, morning light now fully illuminating the kitchen, dishes prepared, cozy family moment, anime style, warm color palette, key visual, heartwarming scene
```

### 人物对话提示词
```
小明: "妈妈，早餐快好了！"
语气：轻快、愉悦
动作：转身将煎蛋装盘

妈妈: "辛苦了，小明。今天学校有什么计划？"
语气：温柔、关心
动作：放下报纸，微笑着看向小明
```

### 首帧转视频提示词
```
首帧→视频：Camera slowly zooms in on Xiao Ming at the counter, he turns slightly to acknowledge camera, arm movement with spatula, 3-4 seconds, smooth anime motion
```

### 尾帧转视频提示词
```
尾帧→视频：Gentle camera pan from dishes to both characters' faces, soft smile exchange, 2-3 seconds, warm transition
```

---

## 质量标准

1. **完整性**：每个场景必须包含全部6个输出项
2. **一致性**：人物名称和特征在同一集中保持一致
3. **专业性**：使用标准动漫制作术语
4. **可执行性**：提示词应能直接用于AI图像/视频生成工具

## 输出结构

```
## 第X集

### 场景 X-1
[6项输出]

### 场景 X-2
[6项输出]

...
```

---

## 提示词优化建议

- 人物描述：年龄、外貌、服装、姿态
- 场景细节：建筑风格、光照、时间天气
- 情绪氛围：开心、紧张、神秘、温馨
- 技术参数：构图、视角、景深
