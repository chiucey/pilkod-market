# 图片关联生成提示词模板

## 风格保持核心要素

1. **主色调**：提取图片中占主导的颜色
2. **标志性元素**：如霓虹灯、水墨、特定建筑风格
3. **光影特征**：如柔和阴影、强烈对比、漫反射
4. **构图风格**：如俯视、仰视、对称、斜线

## 场景变换类型

### 1. 时间维度变换
- 日间 → 黄昏 → 夜晚 → 黎明
- 四季变换（风景类）

### 2. 视角变换
- 全景 ↔ 特写
- 正视 ↔ 侧视 ↔ 背视
- 航拍 ↔ 地面
- 主观视角（第一人称）

### 3. 情绪氛围变换
- 欢快 → 平静 → 忧郁 → 紧张
- 温暖 → 冷峻 → 神秘

### 4. 元素聚焦
- 从全景中提取某个元素进行特写
- 展示该元素的更多细节或不同角度

## 提示词示例

### 赛博朋克风格
```
Cyberpunk futuristic city street view at night with neon lights,
rain-soaked streets reflecting pink and blue neon signs, towering
skyscrapers covered in holographic advertisements, flying vehicles
passing between buildings, detailed cyberpunk atmosphere
```

### 自然风景
```
Breathtaking mountain landscape at golden hour, misty valleys below,
majestic peaks touching clouds, serene lake reflecting mountains,
cinematic composition, National Geographic quality
```

### 人物肖像
```
Elegant portrait with dramatic lighting, [original style elements],
intimate atmosphere, professional photography, studio quality
```

### 建筑摄影
```
Modern architectural masterpiece, [original building style],
dramatic angles, clean lines, glass and steel details,
architectural photography style
```

### 美食摄影
```
Gourmet dish presentation, [original food style],
elegant plating, warm restaurant lighting,
food photography by Michelin star photographer
```

## 批量生成策略

1. **多样性与一致性平衡**：
   - 50% 保持高度一致的变体
   - 30% 适度变化的场景
   - 20% 大胆的风格延伸

2. **横向扩展**：生成不同但相关的场景
3. **纵向深挖**：对同一场景进行不同细节呈现

## 常见问题处理

| 问题 | 解决方式 |
|------|----------|
| 风格不一致 | 在提示词中明确列出核心风格元素 |
| 颜色偏离 | 指定主色调："dominant blue tones" |
| 元素丢失 | 将关键元素放在提示词开头 |
| 过于相似 | 添加差异描述："different angle than before" |
