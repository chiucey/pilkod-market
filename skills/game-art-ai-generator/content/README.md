# Game Art AI Generator - 游戏美术AI生成器

全自动AI生成游戏美术素材包的Skill插件，无需人工设计、无需手动调整，生成的素材可直接导入Construct3项目，适配TikTok小游戏视觉规范。

## Features

- **AI图像生成**: 支持Midjourney/Stable Diffusion双API自动切换
- **像素艺术**: 三种像素风格（复古/Q版/简约），自动调整密度线条
- **UI组件**: 统一化生成按钮/进度条/弹窗等组件
- **色彩匹配**: 基于游戏类型自动生成适配配色
- **音效匹配**: 自动生成音效元数据
- **一键打包**: 生成完整素材包，适配Construct3导入

## 与前序插件协同

```
游戏类型 + 主题关键词
         ↓
   [game-art-ai-generator]
   AI自动生成美术素材包
         ↓
   [c3p-project-auto-editor]
   自动注入Construct3项目
         ↓
   [tiktok-dev-api-auto-integrator]
   上架TikTok小程序
         ↓
     商业化变现
```

## Installation

```bash
pip install requests Pillow numpy mutagen
```

## Quick Start

### 1. 配置API密钥

```python
from scripts.main import GameArtGenerator

# 至少需要一个API密钥
generator = GameArtGenerator(
    midjourney_key="your_mj_key",
    stable_diffusion_key="your_sd_key"
)
```

### 2. 生成素材包

```python
from scripts.main import GameArtGenerator, GameArtRequest

generator = GameArtGenerator()

request = GameArtRequest(
    game_type="敏捷挑战",
    theme_keywords="复古像素 太空闯关 可爱外星人",
    art_style="pixel",
    pixel_style="复古",
    generate_sound=True
)

result = generator.generate(request, on_progress=lambda step, pct, d:
    print(f"[{step}] {pct:.1f}%")
)

if result.success:
    print(f"素材包: {result.package_path}")
    print(f"色彩方案: {result.color_scheme}")
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| game_type | string | 是 | 游戏类型 |
| theme_keywords | string | 是 | 主题关键词 |
| art_style | string | 否 | 像素/扁平/卡通，默认像素 |
| pixel_style | string | 否 | 复古/Q版/简约 |
| color_preference | string | 否 | 色彩偏好 |
| generate_sound | bool | 否 | 是否生成音效，默认True |

### 游戏类型

- 解压闯关
- 合成养成
- 敏捷挑战
- 趣味竞技
- 放置收集

## 输出内容

### 完整素材包(ZIP)

```
game_assets.zip/
├── manifest.json          # 素材清单
├── README.txt            # 使用说明
├── icons/               # 游戏图标(512x512)
├── ui/                  # UI组件
│   ├── btn_*.png        # 按钮
│   ├── popup_*.png      # 弹窗
│   └── progress_*.png   # 进度条
├── characters/          # 角色
├── props/               # 道具
├── backgrounds/         # 背景
├── animations/          # 动画帧
└── audio/               # 音效元数据
```

## 插件结构

```
game-art-ai-generator/
├── SKILL.md
├── skill.json
├── _meta.json
├── README.md
├── scripts/
│   ├── main.py              # 主协调器
│   ├── image_generator.py   # AI图像生成
│   ├── pixel_art.py         # 像素艺术
│   ├── color_matcher.py     # 色彩匹配
│   ├── ui_generator.py      # UI组件
│   ├── sound_generator.py   # 音效匹配
│   ├── asset_packer.py      # 素材打包
│   └── sync_manager.py      # 协同同步
└── references/
    ├── api_config.md        # API配置教程
    └── asset_guide.md       # 素材优化指南
```

## 协同使用

### 完整流水线

```python
# 1. 生成素材
art_gen = GameArtGenerator(midjourney_key="...", stable_diffusion_key="...")
result = art_gen.generate(GameArtRequest(...))

# 2. 同步到C3P项目
art_gen.sync_to_c3p("path/to/project.c3p")

# 3. 准备TikTok发布
tiktok_config = art_gen.prepare_tiktok_publish("My Game")
# 传递给 tiktok-dev-api-auto-integrator
```

## 常见问题

**Q: 需要API密钥吗？**
A: 至少需要一个（Midjourney或Stable Diffusion）

**Q: 生成的素材可以商用吗？**
A: 可以，AI生成内容无版权风险

**Q: 支持哪些游戏类型？**
A: 所有主流休闲游戏类型都支持

**Q: 生成失败怎么办？**
A: 系统会自动重试，配置双API可提高成功率

## License

MIT License
