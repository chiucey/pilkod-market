# 运镜提示词模板库

## 基础运镜模板

### 相机运动
```
基础格式：[movement], [speed], [angle]

示例：
- "slow dolly forward" - 缓慢推进
- "steady tracking shot left" - 稳定跟拍左移
- "crane up reveal" - 升降机上升揭示
```

### 镜头类型
| 类型 | 关键词 | 适用场景 |
|------|-------|---------|
| 特写 | close-up, extreme close-up | 表情、细节 |
| 中景 | medium shot, waist-up | 对话、动作 |
| 全景 | wide shot, establishing | 环境、氛围 |
| 过肩 | over-the-shoulder | 对话场景 |

### 运镜方式
| 方式 | 关键词 | 说明 |
|------|-------|------|
| 推 | push in, dolly in, zoom in | 聚焦注意力 |
| 拉 | pull out, dolly out | 揭示环境 |
| 摇 | pan left/right, tilt up/down | 扫描场景 |
| 移 | tracking shot, handheld | 跟随主体 |
| 跟 | follow shot, chase cam | 动态跟随 |

## 光影效果模板

### 光线质量
```
soft light, natural lighting
harsh shadows, dramatic lighting
rim lighting, backlight
volumetric light, god rays
```

### 天气/环境
```
rain, mist, fog, snow
sunset golden hour, blue hour
studio lighting, three-point lighting
neon lights, industrial lighting
```

## 情绪氛围模板

### 情绪类型
| 情绪 | 色调关键词 | 运镜特点 |
|------|----------|---------|
| 紧张 | desaturated, high contrast | 快速切换 |
| 浪漫 | warm tones, soft focus | 缓慢推进 |
| 悬疑 | dark shadows, cold tones | 缓慢摇镜 |
| 欢快 | bright, saturated colors | 跳切、跟随 |

### 氛围描述
```
cinematic atmosphere, moody lighting
emotional depth, subtle movement
dreamlike quality, surreal
grounded realism, documentary style
```

## 组合提示词模板

### 剧本驱动的完整模板
```
[镜头类型] [相机运动] [速度]
[光线描述], [光质]
[环境/天气效果]
[色调], [情绪氛围]
[画面风格]
```

### 示例：情感对话场景
```
剧本：角色A向角色B表白

提示词：
"medium close-up, slow push in on character's face,
warm golden hour sunlight through window,
soft volumetric light, subtle dust particles,
emotional tone, intimate atmosphere,
cinematic depth of field, shallow focus"
```

### 示例：动作场景
```
剧本：追逐戏

提示词：
"wide tracking shot, following the runner,
handheld camera for urgency, shake effect,
golden hour, long shadows,
dynamic movement, speed lines,
action cinematography, high energy"
```

### 示例：悬疑场景
```
剧本：发现隐藏秘密

提示词：
"low angle wide shot, slow dolly forward,
cold blue moonlight, harsh shadows,
fog rolling in, atmospheric mist,
suspenseful mood, tension building,
cinematic noir style, desaturated colors"
```

## 风格化提示词

### 电影感
```
cinematic grading, film grain
anamorphic lens flare
35mm film look, vintage cinema
letterbox aspect, cinematic black bars
```

### 商业/广告
```
high-key lighting, product focus
clean background, professional polish
brand-consistent, corporate style
lifestyle cinematography, aspirational mood
```

### 短视频/社交媒体
```
vertical 9:16 format, mobile-optimized
fast cuts, engaging pacing
bold colors, high contrast
trending audio sync, TikTok/Reels style
```

## 参考公式

### 快速生成公式
```
[镜头] + [运动] + [光线] + [氛围] + [风格]
```

### 详细描述公式
```
[主体] + [动作/状态] + [环境细节] +
[光线氛围] + [相机运动] + [情绪基调] + [画面风格]
```

## 注意事项

1. **避免过长**：提示词控制在 100 词以内
2. **关键词优先**：使用逗号分隔的关键词而非完整句子
3. **与画面匹配**：提示词必须与生成的图像内容一致
4. **情感先行**：先确定情绪基调，再选择技术参数
5. **测试迭代**：根据效果调整关键词组合
