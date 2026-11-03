# 观众偏好数据库

## 偏好类型分类体系

### 一、商业摄影方向

#### 1.1 时尚/奢侈品品牌
```
核心偏好特征：
- 极致细节与质感呈现
- 品牌色精准还原
- 主体清晰度与背景分离
- 高端氛围感与精致感

参数适配：
{
  "sharpening": 65-80,
  "clarity": 15-25,
  "texture": 20-30,
  "contrast": 15-25,
  "saturation": -5 to +5,
  "highlightRecovery": 70-90,
  "shadowRecovery": 20-35,
  "colorProfile": "Adobe RGB/sRGB品牌规范",
  "cmsEnabled": true
}

输出标准：
- 分辨率: 300 DPI+
- 色彩空间: 目标平台规范
- 文件格式: PSD分层/TIFF
```

#### 1.2 快消品/大众品牌
```
核心偏好特征：
- 色彩鲜明、视觉吸引力强
- 主体突出、与背景高对比
- 清爽干净的视觉风格
- 符合大众审美习惯

参数适配：
{
  "sharpening": 55-70,
  "clarity": 10-20,
  "contrast": 25-40,
  "saturation": +10 to +25,
  "vibrance": +15 to +30,
  "highlightRecovery": 50-70,
  "shadowRecovery": 25-40,
  "vignette": 0-15
}

输出标准：
- 社交媒体优化尺寸
- 色彩空间: sRGB
- 压缩率: 根据平台调整
```

#### 1.3 企业形象/专业服务
```
核心偏好特征：
- 专业、可信、稳重
- 色彩中性或品牌色一致
- 清晰度高、文字可读
- 适度保守但不失现代感

参数适配：
{
  "sharpening": 50-65,
  "clarity": 5-15,
  "contrast": 10-25,
  "saturation": -10 to +5,
  "temperature": 品牌规范±200K,
  "highlightRecovery": 40-60,
  "shadowRecovery": 15-30,
  "grain": 0-5
}

输出标准：
- 多尺寸版本
- 色彩空间: sRGB
- 品牌色容差: ΔE < 2
```

### 二、艺术摄影方向

#### 2.1 风光/自然艺术
```
核心偏好特征：
- 情绪表达优先于技术完美
- 独特的色彩语言与氛围
- 宽广的动态范围
- 细节与质感的平衡

参数适配：
{
  "sharpening": 30-50,
  "clarity": 20-40,
  "texture": 15-30,
  "dehaze": -10 to +20,
  "contrast": 20-40,
  "saturation": -20 to +30,
  "highlightRecovery": 60-85,
  "shadowRecovery": 30-50,
  "curveType": "artistic_S_curve",
  "grain": 5-20,
  "colorGrade": "emotion_guided"
}

情绪调整示例：
- 壮丽: 高饱和 + 暖色 + 强对比
- 宁静: 低饱和 + 冷色 + 柔和对比
- 神秘: 暗调 + 强调色 + 高对比
```

#### 2.2 人文/纪实艺术
```
核心偏好特征：
- 真实感与情感传达
- 色调统一与氛围营造
- 保留现场感与时代感
- 适度噪点接受度

参数适配：
{
  "sharpening": 35-55,
  "clarity": 5-20,
  "contrast": 15-35,
  "saturation": -15 to +10,
  "temperature": 场景光源±300K,
  "grain": 10-30,
  "vignette": 0-20,
  "colorGrade": "documentary_tone"
}

黑白模式参数：
{
  "saturation": -100,
  "grain": 15-40,
  "contrast": 25-45,
  "toneCurve": "film_bw_preset"
}
```

#### 2.3 人像艺术
```
核心偏好特征：
- 皮肤质感自然真实
- 光影立体感与情绪
- 背景虚化与分离
- 个性化风格表达

参数适配（商业人像）：
{
  "sharpening": 40-60,
  "clarity": 0-15,
  "smoothness": 15-30,
  "contrast": 10-25,
  "saturation": -10 to +5,
  "temperature": 肤色还原±200K,
  "skinToneProtection": true,
  "eyeEnhancement": 15-30
}

参数适配（艺术人像）：
{
  "sharpening": 25-45,
  "clarity": 10-25,
  "contrast": 20-40,
  "saturation": 场景依赖,
  "grain": 5-20,
  "colorGrade": "artistic_interpretation",
  "moodAlignment": "emotion_priority"
}
```

### 三、社交媒体方向

#### 3.1 Instagram/Facebook
```
核心偏好特征：
- 高对比度与视觉冲击力
- 饱和度偏向讨好性色彩
- 清新明亮的整体风格
- 竖版构图友好

参数适配：
{
  "sharpening": 55-75,
  "contrast": 25-45,
  "saturation": +15 to +35,
  "vibrance": +20 to +40,
  "temperature": +200K to +800K,
  "highlights": -10 to -30,
  "shadows": +5 to +20,
  "vignette": 10-25,
  "filterStyle": "social_warm_bright"
}

构图建议：
- 主体位置: 黄金分割点或中心
- 边缘留白: 10-15%
- 文字空间: 考虑平台特性
```

#### 3.2 短视频封面
```
核心偏好特征：
- 极高视觉吸引力
- 主体识别度高
- 色彩鲜明、对比强烈
- 适应小屏预览

参数适配：
{
  "sharpening": 60-80,
  "contrast": 35-55,
  "saturation": +20 to +40,
  "clarity": 15-35,
  "vignette": 15-30,
  "edgeEnhancement": 10-25,
  "frameOptimization": "center_focus"
}

视频素材额外要求：
- 关键帧选择: 高光瞬间或动作高潮
- 色彩稳定性: 避免大幅波动
- 字幕区域: 留出安全边距
```

#### 3.3 专业摄影社区（500px/视觉中国）
```
核心偏好特征：
- 高技术质量要求
- 独特审美与创意
- 色彩科学性优先
- 细节极致追求

参数适配：
{
  "sharpening": 45-65,
  "clarity": 15-30,
  "texture": 20-35,
  "contrast": 15-30,
  "saturation": 0 to +15,
  "highlightRecovery": 60-80,
  "shadowRecovery": 25-45,
  "grain": 0-10,
  "colorGrade": "scientific_balanced"
}

质量门槛：
- 无色阶丢失
- 无色彩溢出
- 动态范围最大化保留
```

### 四、印刷输出方向

#### 4.1 杂志/书籍印刷
```
核心偏好特征：
- 高分辨率细节
- 色彩准确与一致性
- 跨版本色差控制
- 印刷适性优化

参数适配：
{
  "sharpening": 50-70,
  "resolution": 300 DPI,
  "colorMode": "CMYK/Adobe RGB",
  "saturation": -10 to +10,
  "blackPoint": 精确校准,
  "highlightRecovery": 40-60,
  "shadowRecovery": 20-40,
  "inkLimiting": 300%,
  "totalInk": 320-380%
}

色彩配置文件：
- 期刊印刷: SWOP v2 / GRACoL
- 艺术画册: Fogra39 / ISO Coated v2
- 新闻印刷: SNAP
```

#### 4.2 展览/画廊输出
```
核心偏好特征：
- 极致色彩还原
- 材质质感呈现
- 艺术微喷标准
- 长效保存稳定性

参数适配（颜料墨水）：
{
  "colorSpace": "Adobe RGB/ProPhoto",
  "saturation": 原始场景饱和度,
  "contrast": 最小化调整,
  "sharpening": 30-50,
  "metallicInkOption": 增强金属感,
  "paperSimulation": "专业棉纸/艺术纸"
}

参数适配（艺术品微喷）：
{
  "colorSpace": "ProPhoto RGB",
  "blackPoint": 纯黑保护,
  "saturation": 零压缩,
  "contrast": 无压缩,
  "grain": 原生保留
}
```

## 跨平台适配矩阵

| 平台类型 | 饱和度偏移 | 对比度调整 | 锐化强度 | 色温倾向 |
|---------|-----------|-----------|---------|---------|
| Instagram | +15 to +35 | +25 to +45 | 55-75 | +500K |
| Facebook | +10 to +25 | +15 to +30 | 50-65 | +300K |
| 小红书 | +20 to +40 | +20 to +40 | 55-75 | +600K |
| 微信公众号 | +5 to +15 | +10 to +25 | 45-60 | +200K |
| 摄影社区 | 0 to +15 | +15 to +30 | 45-65 | 原始 |
| 商业印刷 | -10 to +10 | +10 to +20 | 50-70 | 标准 |
| 艺术展览 | 原始 | 最小 | 30-50 | 原始 |

## 敏感度分析方法

### 快速识别流程
1. **内容分析**：识别画面主体类型（人物/风光/产品/建筑）
2. **受众定位**：确定目标受众群体特征
3. **平台规范**：了解发布平台的技术要求
4. **风格偏好**：评估观众对色彩/对比的接受范围
5. **敏感边界**：识别可能的文化/审美敏感点

### 敏感度评分模型
```json
{
  "sensitivityAnalysis": {
    "technicalPrecision": 70-95,
    "emotionalExpression": 60-90,
    "culturalAcceptability": 80-100,
    "aestheticAlignment": 65-95,
    "platformFit": 75-100
  },
  "overallScore": "weightedAverage",
  "adjustmentPriority": [
    "platformCompliance",
    "audienceExpectation",
    "contentIntegrity",
    "emotionalResonance"
  ]
}
```

### 边界条件处理
- **高敏感度内容**：优先技术质量、降低艺术表达
- **低敏感度内容**：可增加创意自由度
- **跨文化内容**：中性化处理、避免文化偏向
- **争议性内容**：审慎评估、必要时建议保守处理