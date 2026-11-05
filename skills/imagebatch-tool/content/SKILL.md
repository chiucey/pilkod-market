---
name: imagebatch-tool
description: 图片批量处理工具 - 一键将图片批量导出为指定分辨率，支持30+预设尺寸（证件照、屏幕分辨率、社交媒体、图标等）。当用户要求批量处理图片、制作证件照、统一图片尺寸、生成缩略图、适配游戏纹理、社交媒体配图时使用。
---

# ImageBatch 图片批量处理工具

## 技能概述

ImageBatch 是一款功能强大的图片批量处理CLI工具，可一键将图片批量导出为指定分辨率。

## 核心功能

### 1. 丰富的预设尺寸库 (30+预设)

**证件照类 (中国标准, 300DPI)**
- `id_1寸` - 295x413 标准1寸照片
- `id_2寸` - 413x579 标准2寸照片
- `id_小1寸` - 260x378 小1寸照片
- `id_小2寸` - 354x472 小2寸照片

**正方形分辨率**
- `sq_64`, `sq_128`, `sq_256`, `sq_512`, `sq_1024`, `sq_2048`, `sq_4096`

**屏幕/视频分辨率**
- `hd_720p` (1280x720), `hd_1080p` (1920x1080), `qhd_1440p` (2560x1440)
- `uhd_4k` (3840x2160), `uhd_8k` (7680x4320)
- `portrait_1080p` (1080x1920), `portrait_4k` (2160x3840)

**社交媒体**
- `social_微信朋友圈` (1080x1080), `social_微信头像` (200x200)
- `social_小红书` (1080x1350), `social_抖音封面` (1080x1920)
- `social_微博封面`, `social_B站封面`, `social_微信公众号`

**应用图标**
- `icon_16` ~ `icon_1024`

**缩略图**
- `thumb_150`, `thumb_300`, `thumb_480`, `thumb_600`

### 2. 灵活的缩放模式

| 模式 | 说明 | 命令示例 |
|-----|------|---------|
| 预设尺寸 | 直接选择预设 | `-p hd_1080p` |
| 百分比 | 按原图百分比缩放 | `--mode percent --percent 50` |
| 固定尺寸 | 指定宽高像素 | `--mode fixed --width 1920` |

**宽高比模式:**
- `fit` - 保持宽高比，以宽度为基准
- `fill` - 保持宽高比，以高度为基准
- `stretch` - 强制拉伸

### 3. 批量处理能力

- **输入格式**: PNG, JPG, BMP, TGA, TIFF, WebP, PSD, GIF
- **输出格式**: PNG, JPG, BMP, TGA, TIFF, WebP
- **处理模式**: 单文件、多文件、目录(递归/非递归)

### 4. 输出控制

- JPG/WebP质量可调 (1-100)
- 自定义文件名后缀
- 自动附加分辨率信息
- 预览模式 (dry-run)
- JSON格式输出

## 安装

```bash
pip install imagebatch
```

## 使用示例

### 基本用法

```bash
# 使用预设尺寸批量导出
imagebatch ./photos -o ./output -p hd_1080p

# 按百分比缩放
imagebatch ./photos -o ./output --mode percent --percent 50

# 固定尺寸，保持宽高比
imagebatch ./photos -o ./output --mode fixed --width 1920 --aspect-mode fit
```

### 预览模式

```bash
# 不实际导出，只显示处理预览
imagebatch ./photos -o ./output -p sq_512 --dry-run
```

### JSON输出

```bash
# 输出JSON格式，便于程序化处理
imagebatch ./photos -o ./output -p social_微信头像 --json
```

### 递归处理目录

```bash
# 递归处理子目录
imagebatch ./photos -o ./output -p hd_1080p -r
```

### 制作证件照

```bash
imagebatch ./photos -o ./output -p id_1寸 -f jpg
```

### 批量生成缩略图

```bash
imagebatch ./photos -o ./thumbs --mode percent --percent 25
```

### 生成App图标

```bash
imagebatch ./app_icon.png -o ./icons -p icon_256 -f png
```

## 命令行选项

| 选项 | 说明 |
|------|------|
| `input_path` | 输入文件或目录 |
| `-o, --output` | 输出目录 |
| `-m, --mode` | 缩放模式: preset/percent/fixed |
| `-p, --preset` | 预设尺寸名称 |
| `--percent` | 百分比缩放 (1-500) |
| `--width` | 目标宽度 |
| `--height` | 目标高度 |
| `--aspect-mode` | 宽高比模式: fit/fill/stretch |
| `-f, --format` | 输出格式: png/jpg/bmp/tga/tiff/webp |
| `-q, --quality` | 输出质量 (1-100) |
| `--suffix` | 文件名后缀 |
| `--add-resolution` | 文件名附加分辨率 |
| `--dry-run` | 预览模式 |
| `--json` | JSON格式输出 |
| `-r, --recursive` | 递归处理子目录 |
| `--list-presets` | 列出所有预设尺寸 |

## Python API

```python
from imagebatch import ImageProcessor, ProcessSettings, ResizeMode

settings = ProcessSettings(
    mode=ResizeMode.PRESET,
    preset_name="hd_1080p",
    output_format="png",
    output_dir="./output"
)

processor = ImageProcessor(settings)
results = processor.process_path("./photos")

for result in results:
    print(f"{result.status}: {result.input_path}")
```

## 输出示例

```
╔══════════════════════════════════════════════════════╗
║            ImageBatch 图片批量处理工具 v1.0.0          ║
╚══════════════════════════════════════════════════════╝
📁 输入路径: ./photos
📁 输出目录: ./output
🔄 处理模式: preset
📐 预设尺寸: hd_1080p (1920x1080)
🖼️ 输出格式: PNG
📁 找到 3 个图片文件

✅ photo1.png -> photo1.png (4000x3000 -> 1920x1080)
✅ photo2.jpg -> photo2.jpg (4000x3000 -> 1920x1080)
✅ photo3.webp -> photo3.webp (4000x3000 -> 1920x1080)

==================================================
📊 总数: 3
✅ 成功: 3
❌ 失败: 0
⏱️ 耗时: 715毫秒
==================================================
```

## 技术规格

- **语言**: Python 3.8+
- **依赖**: Pillow, Click
- **测试**: 27个单元测试全部通过
- **许可**: MIT License
