# 素材生成优化技巧

## 提示词(Prompt)优化

### 基础结构
```
[主体描述] + [风格标签] + [质量增强词] + [技术参数]
```

### 示例

**图标:**
```
cute alien character game icon, pixel art style, centered, transparent background, vibrant colors, 512x512
```

**角色:**
```
space warrior character sprite, pixel art, 8-bit style, idle pose, transparent background, game asset
```

**背景:**
```
space nebula game background, parallax layers, seamless tile, dark blue purple gradient, game scenery
```

## 像素风格控制

### 风格参数

| 风格 | pixel_size | color_reduction | 适用场景 |
|-----|------------|-----------------|---------|
| 复古 | 4 | 32 | 经典像素游戏 |
| Q版 | 3 | 48 | 可爱风格 |
| 简约 | 2 | 16 | 现代简约 |

### 自定义配置

```python
from pixel_art import PixelArtGenerator, PixelStyle, PixelConfig

config = PixelConfig(
    style=PixelStyle.RETRO,
    pixel_size=4,
    line_weight=2,
    color_reduction=32,
    sharpness=1.8
)

generator = PixelArtGenerator()
generator.apply_style("input.png", "output.png", custom_config=config)
```

## 色彩优化

### 自动匹配
系统根据游戏类型自动生成配色：
- 解压类 → 柔和 pastel
- 竞技类 → 鲜明 vibrant
- 暗黑类 → 深沉 dark

### 手动覆盖
```python
request = GameArtRequest(
    theme_keywords="太空 科技",
    color_preference="cold"  # 冷色调
)
```

## 动画帧生成

### 支持的动画类型
- `idle`: 待机动画（上下浮动）
- `move`: 移动动画（左右晃动）
- `attack`: 攻击动画（缩放+位移）
- `reward`: 奖励动画（放大+粒子）

### 使用示例
```python
frames = generator.pixel_generator.create_animation_frames(
    base_image_path="character.png",
    output_dir="./frames",
    frame_count=4,
    animation_type="idle"
)
```

## 素材尺寸规范

### Construct3推荐尺寸

| 类型 | 推荐尺寸 | 最大尺寸 |
|-----|---------|---------|
| 图标 | 512x512 | 1024x1024 |
| 角色 | 256x256 | 512x512 |
| 道具 | 64x64 | 256x256 |
| 背景 | 800x600 | 1920x1080 |

### TikTok小游戏规范
- 图标: 512x512 PNG
- UI: 适配移动端(最小44pt)
- 背景: 支持竖屏(9:16)

## 生成成功率提升

### 1. 详细的Prompt
```
# 差
cat game

# 好
cute cartoon cat character, kawaii style, pink nose, big eyes, game sprite, transparent background
```

### 2. 添加参考词
```
pixel art, game asset, sprite sheet, transparent background, high quality, sharp pixels
```

### 3. 避免负面词
```
# 避免
blurry, low quality, watermark, text, logo
```

## 版权与合规

### 版权说明
- 生成的素材可用于商业用途
- 避免生成已知IP相关内容
- 人物设计避免真人照片风格

### 合规建议
1. 原创角色设计
2. 通用游戏主题
3. 无品牌标识
