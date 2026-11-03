# AI绘图Prompt词库

## 影视风格库

### 电影感场景

```
# 都市夜景
"Cinematic night cityscape, Shanghai 1990s neon lights,
rain-soaked streets, moody lighting, film grain,
8K resolution, anamorphic lens flare"

# 怀旧色调
"Retro Chinese cinema aesthetic, faded photograph look,
warm color grading, 1980s Shanghai apartment,
soft focus background, nostalgic mood"

# 戏剧光影
"Theatrical lighting, chiaroscuro style,
single light source from window casting long shadows,
dark and light contrast, cinematic composition"
```

### 人物特写

```
# 情绪人像
"Close-up portrait, intense emotional moment,
cinematic lighting, shallow depth of field,
moody atmosphere, film photography aesthetic"

# 群像场景
"Dynamic group scene, 90s Chinese restaurant,
neon signs in background, warm tungsten lighting,
cinematic wideshot, anamorphic lens"
```

### 氛围渲染

```
# 霓虹美学
"Neon-soaked urban scene, cyberpunk Chinese style,
rain reflection on street, moody atmosphere,
cinematic color palette, Blade Runner 2049 inspired"

# 复古质感
"Vintage 90s Chinese film aesthetic,
slight overexposure, warm color tones,
dust particles in light beam, nostalgic mood"
```

## 配图场景Prompt

| 场景 | DALL-E Prompt | Midjourney Prompt |
|------|---------------|-------------------|
| 霓虹夜景 | "Cinematic Shanghai street at night, neon signs, rain reflection, moody atmosphere, film photography style, 8K" | "Shanghai night market --ar 16:9 --style raw --v 6" |
| 人物情绪 | "Close-up portrait with dramatic lighting, cinematic mood, film grain, anamorphic lens effect" | "Portrait cinematic lighting --ar 3:4 --style raw" |
| 空间意境 | "Minimalist Chinese aesthetic, negative space, single object, zen composition, soft natural light" | "Chinese ink painting style, minimalist composition --ar 16:9" |
| 年代感 | "1990s Chinese apartment interior, warm nostalgic lighting, vintage furniture, film photograph look" | "90s China nostalgic aesthetic --ar 4:3 --style raw" |

## 快速生成模板

### 模板1：电影感场景
```
[情绪/氛围] + [时间] + [地点] + [光线] + [电影风格]
```

示例：
```
"Rainy night, Shanghai 1990s, neon lights reflecting on wet street,
cinematic mood, Wong Kar-wai style, film photography"
```

### 模板2：人物情绪
```
[景别] + [情绪] + [光线类型] + [背景元素] + [风格参考]
```

示例：
```
"Close-up portrait, melancholic expression,
single warm light source from window,
blurred Shanghai skyline background,
cinematic film photography"
```

### 模板3：物件特写
```
[物件] + [材质/质感] + [光线] + [构图] + [风格]
```

示例：
```
"Vintage jade bracelet, intricate details,
warm tungsten light, centered composition,
studio photography, dark background"
```

## 公众号配图策略

### 封面图规格
- 尺寸：900 x 383 像素（公众号封面）
- 风格：简洁、留白、文字友好
- 色调：与文章主题呼应

### 内文配图
- 每400字插入一张
- 风格统一（建议固定使用一种AI风格）
- 添加轻微文字叠加（可选）

### 图片版权规避
```markdown
使用AI生成的原创图片 = 100%版权无忧
优势：
- 纯原创，无侵权风险
- 风格统一，视觉溢价
- 可定制化匹配内容
```

## 高级技巧

### 保持风格一致性
```
在每篇文章开头指定风格指南：

【本文视觉风格】
- 主色调：暖黄+深蓝（怀旧电影感）
- 光线：自然光+局部暖调
- 构图：三分法，大量留白
- 参考：Wong Kar-wai + 张艺谋色彩美学
```

### 批量生成技巧
```python
# 批量生成时保持风格一致
STYLE_PROMPT = """
Cinematic photography, film grain, warm color grading,
Shanghai aesthetic, nostalgic mood, 8K resolution
"""

def generate_image(scene_prompt, output_file):
    full_prompt = f"{scene_prompt}, {STYLE_PROMPT}"
    # 调用DALL-E/Midjourney API
    return generate(full_prompt, output_file)
```
