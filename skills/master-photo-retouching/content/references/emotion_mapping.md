# 情绪色彩映射表

## 色彩情绪理论基础

### 色相情绪关联

| 色相范围 | 情绪关键词 | 文化内涵 | 视觉强度 |
|---------|-----------|---------|---------|
| 红 0-30 | 热情、活力、危险、爱 | 中国-喜庆，西方-爱情 | 高饱和高张力 |
| 橙 30-60 | 温暖、创意、友好、能量 | 快乐、创造力 | 中高饱和 |
| 黄 60-90 | 阳光、乐观、警醒、年轻 | 快乐、希望 | 高明度特征 |
| 绿 90-150 | 自然、平静、成长、治愈 | 和谐、新生 | 中饱和为主 |
| 青 150-180 | 清凉、理智、科技、未来 | 专业、冷静 | 中低饱和 |
| 蓝 180-270 | 沉静、信任、忧郁、神秘 | 专业、权威 | 低饱和深调 |
| 紫 270-330 | 高贵、梦幻、浪漫、神秘 | 皇权、灵性 | 中高饱和 |
| 粉红 330-360 | 柔美、浪漫、少女、温柔 | 爱情、甜蜜 | 高饱和浅调 |

### 明度情绪映射

| 明度范围 | 情绪特征 | 视觉表现 | 调整策略 |
|---------|---------|---------|---------|
| 高调 (80-100%) | 轻盈、开放、希望、纯真 | 高光主导、留白多 | 提升整体曝光、降低对比 |
| 中调 (40-80%) | 平衡、真实、自然、稳定 | 灰阶丰富、过渡平滑 | 保持原明度、调整分布 |
| 低调 (0-40%) | 沉重、神秘、深邃、压抑 | 暗部主导、阴影深 | 降低曝光、提升对比 |

### 饱和度情绪映射

| 饱和度范围 | 情绪特征 | 视觉表现 | 调整策略 |
|-----------|---------|---------|---------|
| 高饱和 (70-100%) | 强烈、刺激、热情、冲突 | 色彩鲜明、视觉冲击 | 提升饱和度、增强对比 |
| 中饱和 (30-70%) | 温和、真实、自然、舒适 | 色彩平衡、层次丰富 | 保持饱和度、适当微调 |
| 低饱和 (0-30%) | 沉稳、内敛、忧郁、高级 | 灰调为主、氛围感强 | 大幅降低饱和度 |

## 复合情绪色彩方案

### 1. 愉悦/活力型
```
色彩配置：
- 主色调：暖色系（红15% + 橙35% + 黄50%）
- 饱和度：+20至+40
- 明度：高调为主（70-90%）
- 对比度：中高度（+20至+40）
- 高光：轻微过曝以增强活力感
- 阴影：保留细节以维持自然感

情感参数：
{
  "emotionType": "joyful_vibrant",
  "saturationShift": +30,
  "brightnessShift": +15,
  "contrastAdjust": +25,
  "temperatureShift": +500K,
  "curveShape": "S-curve_light",
  "colorGrade": "warm_highlight"
}
```

### 2. 平静/安宁型
```
色彩配置：
- 主色调：冷色系（蓝40% + 青30% + 绿30%）
- 饱和度：-20至-40
- 明度：中间调（50-70%）
- 对比度：低至中（-10至+10）
- 曲线：柔和过渡、反差较小

情感参数：
{
  "emotionType": "calm_serene",
  "saturationShift": -30,
  "brightnessShift": 0,
  "contrastAdjust": -5,
  "temperatureShift": -800K,
  "curveShape": "gentle_smooth",
  "colorGrade": "cool_low_saturation"
}
```

### 3. 戏剧/张力型
```
色彩配置：
- 主色调：高对比色（互补或分裂互补）
- 饱和度：极高（+50至+80）
- 明度：高对比分布（亮部极亮、暗部极暗）
- 对比度：高（+40至+60）
- 曲线：强S形或高反差曲线

情感参数：
{
  "emotionType": "dramatic_intense",
  "saturationShift": +60,
  "brightnessShift": +10,
  "contrastAdjust": +50,
  "temperatureShift": +300K,
  "curveShape": "dramatic_S_curve",
  "colorGrade": "high_contrast_split"
}
```

### 4. 忧郁/沉思型
```
色彩配置：
- 主色调：低饱和蓝灰色系
- 饱和度：大幅降低（-50至-70）
- 明度：中低调（30-60%）
- 对比度：中高（+20至+40）
- 分色调：偏蓝紫

情感参数：
{
  "emotionType": "melancholic_contemplative",
  "saturationShift": -60,
  "brightnessShift": -10,
  "contrastAdjust": +30,
  "temperatureShift": -1500K,
  "curveShape": "pull_down_shadows",
  "colorGrade": "desaturated_blue_tint"
}
```

### 5. 神秘/深邃型
```
色彩配置：
- 主色调：深色+强调色
- 饱和度：中等偏低（-20至+10）
- 明度：暗调为主（20-50%）
- 对比度：高（+40至+70）
- 暗角：明显（30-50%强度）

情感参数：
{
  "emotionType": "mysterious_profound",
  "saturationShift": -10,
  "brightnessShift": -25,
  "contrastAdjust": +55,
  "temperatureShift": -500K,
  "curveShape": "deep_S_curve",
  "colorGrade": "dark_focus_vignette"
}
```

### 6. 浪漫/温馨型
```
色彩配置：
- 主色调：暖粉红/紫色系
- 饱和度：中饱和（+10至+30）
- 明度：中高（60-85%）
- 对比度：柔和至中（0至+25）
- 光晕效果：轻微暖色光晕

情感参数：
{
  "emotionType": "romantic_warm",
  "saturationShift": +20,
  "brightnessShift": +10,
  "contrastAdjust": +15,
  "temperatureShift": +800K,
  "curveShape": "soft_curve",
  "colorGrade": "warm_pink_tint"
}
```

### 7. 力量/权威型
```
色彩配置：
- 主色调：深蓝/深红/黑色
- 饱和度：中高至全饱和
- 明度：低调至中调（20-60%）
- 对比度：极高（+60至+80）
- 清晰度：增强结构感

情感参数：
{
  "emotionType": "powerful_authoritative",
  "saturationShift": +25,
  "brightnessShift": -15,
  "contrastAdjust": +65,
  "temperatureShift": +200K,
  "curveShape": "crushed_blacks",
  "colorGrade": "deep_saturated"
}
```

### 8. 未来/科技型
```
色彩配置：
- 主色调：青蓝/霓虹色
- 饱和度：中至高（+20至+50）
- 明度：高对比分布
- 对比度：高（+45至+65）
- 色调偏移：偏青/蓝

情感参数：
{
  "emotionType": "futuristic_tech",
  "saturationShift": +35,
  "brightnessShift": +5,
  "contrastAdjust": +55,
  "temperatureShift": -1200K,
  "curveShape": "tech_S_curve",
  "colorGrade": "cyan_blue_enhance"
}
```

## 曲线形态情绪映射

| 曲线类型 | 形态特征 | 情绪传达 | 参数描述 |
|---------|---------|---------|---------|
| 标准线性 | 对角线 | 真实、平衡 | 基准参考 |
| 柔和S形 | 轻微弯曲 | 温和、自然 | 高光+10/阴影-10 |
| 强S形 | 明显弯曲 | 戏剧、张力 | 高光+20/阴影-20 |
| 高对比 | 左下右下抬升 | 冲击、活力 | 暗部压暗/亮部提亮 |
| 反S形 | 反向弯曲 | 低沉、压抑 | 暗部提亮/亮部压暗 |
| 胶片曲线 | 柔和过渡+暗部压缩 | 复古、质感 | 保留高光/柔化暗部 |
| HDR曲线 | 平滑提亮 | 通透、自然 | 全范围提亮 |

## 情绪调整工作流

### 步骤一：情绪识别
1. 分析画面内容与主题
2. 确定目标情绪类型
3. 评估观众接受度

### 步骤二：参数预设
1. 根据情绪类型选择预设配置
2. 计算基础色彩偏移量
3. 确定曲线形态

### 步骤三：微调校准
1. 根据图像具体内容微调参数
2. 平衡整体与局部情绪
3. 确保色彩协调性

### 步骤四：验证反馈
1. 检查色彩是否传达目标情绪
2. 评估视觉舒适度
3. 确认技术质量（无色彩溢出、色阶丢失）