---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 61a3f2980f1b4329cf4e84a3361d659d
    PropagateID: 61a3f2980f1b4329cf4e84a3361d659d
    ReservedCode1: 304502204b04ae3ee344fc479eaabade86054f1646b575b6145a2fc5a5432410fe09a29d022100fa1b9feaeaa8c8ff3b43adba609bcdc68abdcc6997c8cc9de6c225923f33433d
    ReservedCode2: 3045022100f493537605bfe4d618c1b3a5dd19928015f84463e7cb59982605cdfff57edaea022039ddf1a5e9d1fc3cb241fd02383ee5ae08984e7854dbf9ed214c9cad9db743e5
description: 从多模态输入（文字/图片/混合）生成视频故事。当用户要求创作视频故事、生成AI短剧、制作剧情视频、剧本转视频、图片生成视频、多模态视频创作时使用。触发短语包括：生成视频故事、AI短剧、剧情视频、剧本转视频、图片生成视频、多模态创作等。
name: multimodal-video-story
---

# 多模态视频故事生成技能

## 核心能力

将用户的多模态输入（纯文字、单图/多图、图文混合）转化为结构化的视频生成方案，输出包含分镜脚本、风格参数和连贯性保障的完整创作流水线。

## 四维工作流程

### 维度1：多模态理解与对齐 (Input Analysis)

**执行策略**：

```
IF 输入类型 == "纯文字":
    → 调用LLM进行语义扩充
    → 自动补全：环境描写、情感基调、角色描述
    → 示例："老人与海" → "破旧渔船在金色落日下摇晃，海浪拍打船舷，苍老渔夫眼神坚毅"

ELIF 输入类型 == "单图":
    → 识别核心元素：主体、场景、构图、光影、色彩基调
    → 输出结构化视觉描述词

ELIF 输入类型 == "多图":
    → 分析图片间逻辑关系
    → 判断：同场景多角度 OR 故事情节顺序
    → 建立图片间的叙事连贯性

ELIF 输入类型 == "图文混合":
    → 以图片为视觉基准 (Consistency)
    → 以文字为动作指令 (Instruction)
    → 示例：图片"猫" + 文字"在月球跳舞" → 保持猫的特征，月球场景，动作合成
```

**输出格式**：
```json
{
  "input_type": "mixed",
  "visual_baseline": {
    "subject": "赛博风格建筑",
    "colors": ["蓝色霓虹", "深灰金属"],
    "mood": "冷酷、紧张"
  },
  "action_instructions": ["黑客奔跑", "雨中穿梭", "高楼跳跃"],
  "semantic_expansion": "湿润的街道倒映着霓虹灯光..."
}
```

### 维度2：智能脚本与分镜规划 (Storyboarding)

**执行策略**：

1. **剧情扩写**：自动生成包含"起承转合"的短篇脚本
2. **分镜拆解**：将脚本转化为每一秒的视觉描述 (Prompt)
3. **时长适配**：根据用户选择动态调整

**分镜模板**：

| 时间节点 | 镜头类型 | 视觉描述 | 运镜方式 |
|---------|---------|---------|---------|
| 0-3s | 全景 | 赛博都市雨夜全景 | Drone Up |
| 3-6s | 中景 | 黑客侧身跑过巷弄 | Pan Left |
| 6-10s | 特写 | 雨水打在面罩上 | Zoom In |

**时长参数映射**：
- 10s → 3-4个分镜，2-3个场景切换
- 30s → 6-8个分镜，3-4个场景切换
- 60s → 10-12个分镜，5-6个场景切换

**输出格式**：
```json
{
  "script": {
    "act_1_setup": "黑客在阴暗巷弄中苏醒，发现被追踪",
    "act_2_conflict": "雨中疾跑，穿过霓虹闪烁的街道",
    "act_3_climax": "站在高楼边缘，回头望一眼，然后纵身跃下"
  },
  "storyboard": [
    {
      "index": 1,
      "time_range": "0-3s",
      "shot_type": "wide_shot",
      "description": "俯拍赛博都市雨夜，霓虹灯光倒映在积水路面",
      "camera_movement": "drone_up",
      "prompt": "A cyberpunk cityscape at night in heavy rain, neon lights reflecting on wet streets, cinematic wide shot, drone rising..."
    }
  ]
}
```

### 维度3：风格与参数控制 (Style & Control)

**预设选项矩阵**：

**视觉风格**：
- `cinematic` - 电影感：宽幅比例、深景深、胶片颗粒
- `anime` - 2D动漫：线条清晰、色彩饱和、扁平化
- `cyberpunk` - 赛博朋克：霓虹光效、数据流、高对比
- `realistic` - 写实摄影：自然光线、浅景深、真实材质
- `oil_painting` - 油画质感：笔触感、暖色调、艺术化
- `pixar_3d` - 皮克斯3D：圆润建模、活力配色、表情丰富

**运镜控制**：
- `push_in` - 推镜头：主体逐渐放大，增强紧张感
- `pull_out` - 拉镜头：揭示环境全貌
- `pan_left/right` - 摇镜头：横向扫视场景
- `track_shot` - 跟镜头：跟随主体移动
- `crane_up/down` - 升降镜头：垂直视角变化
- `orbit` - 环绕镜头：绕主体旋转

**情感基调**：
- `joyful` - 欢快：明亮色调、快节奏、暖音乐
- `melancholic` - 忧郁：冷色调、慢动作、留白
- `tense` - 紧张：手持感、快切、低音效
- `epic` - 史诗感：航拍、宽幅、神圣配乐
- `cozy` - 温馨：柔光、暖色、慢节奏

**画面比例**：
- `16:9` - 横屏（影视/电视）
- `9:16` - 竖屏（短视频/TikTok）
- `1:1` - 方屏（社交媒体）

**输出格式**：
```json
{
  "style_presets": {
    "visual_style": "cyberpunk",
    "camera_control": ["pan_left", "track_shot", "orbit"],
    "emotional_tone": "tense",
    "aspect_ratio": "16:9"
  },
  "render_params": {
    "resolution": "1080P",
    "frame_rate": 24,
    "duration_seconds": 10
  }
}
```

### 维度4：视频生成与连贯性维护 (Rendering & Consistency)

**核心保障机制**：

1. **角色一致性 (Character ID)**：
   - 提取首帧角色特征向量
   - 在后续帧中注入特征约束
   - 防止角色"变异"或"换脸"

2. **场景连贯性 (Scene Consistency)**：
   - 建立场景元素关键词库
   - 每帧生成时注入场景锚点
   - 保持光影方向、天气效果一致

3. **物理模拟优化**：
   - 水/雨：涟漪、溅射、流动
   - 火/烟：粒子扩散、阴影投射
   - 毛发：重力下垂、风吹动
   - 布料：褶皱动态、飘动规律

4. **智能配乐 (Optional)**：
   - 分析画面情感基调
   - 生成匹配的氛围BGM (30s)
   - 添加环境音效（雨声、脚步声、风声）

**输出格式**：
```json
{
  "render_config": {
    "character_id": {
      "enabled": true,
      "reference_frame": 1,
      "feature_lock": ["face", "clothing", "silhouette"]
    },
    "scene_consistency": {
      "keywords": ["neon_light", "wet_street", "blue_tone"],
      "light_direction": "top_right_45deg"
    },
    "physics_simulation": ["rain", "reflection"],
    "soundtrack": {
      "enabled": true,
      "mood": "tense",
      "ambient_sounds": ["rain", "footsteps"]
    }
  },
  "final_prompts": ["完整的每帧生成Prompt列表"]
}
```

## 端到端处理示例

**用户输入**：
> [上传赛博风格建筑图] + "一个黑客在雨中奔跑，最后跳下高楼"

**技能处理流程**：

```
Step 1: 提取图像特征
├── 主体：未来主义建筑群
├── 色调：蓝色霓虹 + 深灰金属
├── 氛围：冷酷、压抑
└── 光影：顶部霓虹光源

Step 2: 生成剧情脚本
├── 起：黑客从阴影中冲出，回望追踪者
├── 承：雨中疾跑，霓虹倒影在积水路面
├── 转：站在高楼边缘，雨水打在面罩
└── 合：纵身跃下，慢动作俯冲

Step 3: 生成10秒分镜
├── 0-2s: 侧面跟拍，巷弄中奔跑
├── 2-5s: 正面穿越雨幕，霓虹闪烁
├── 5-8s: 高楼边缘特写，回头凝视
└── 8-10s: 慢动作跳跃，俯冲视角

Step 4: 配置风格参数
├── 视觉风格: cyberpunk
├── 运镜: track_shot + drone_down
├── 情感: tense
└── 比例: 16:9

Step 5: 输出渲染配置
├── Character ID: 保持黑客服装/面罩一致
├── 场景锚点: 蓝色霓虹、雨水反射
├── 物理: 雨滴粒子、地面涟漪
└── 音效: 雨声 + 紧张节奏BGM
```

## 输出交付物

最终输出包含以下结构化内容：

1. **输入分析报告** - 提取的视觉元素和语义扩充
2. **剧情脚本** - 完整的起承转合文本
3. **分镜列表** - 每帧的时间、镜头类型、描述、Prompt
4. **风格配置单** - 选定的视觉风格、运镜、情感参数
5. **渲染配置单** - 一致性保障、物理模拟、配乐设置
6. **最终Prompt序列** - 可直接用于视频生成模型的完整Prompt列表

## 触发检查

使用此技能时，确认：
- [ ] 用户输入包含视频故事创作意图
- [ ] 输入形式为文字/图片/图文混合
- [ ] 用户未指定使用其他专项技能（如纯图片生成、语音合成等）
