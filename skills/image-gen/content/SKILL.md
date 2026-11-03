---
name: image-gen
description: "AI图像生成与编辑，支持文生图、图+文生图、风格转换。当用户要求画图、生成图片、编辑图片时使用。支持多种比例（1:1到21:9）和分辨率（标准/2K/4K）。"
---

# AI 图像生成

通过脚本调用 Gemini Flash Image API 生成图片。

## 环境变量

- `IMAGE_GEN_API_KEY` — API 密钥
- `IMAGE_GEN_BASE_URL` — API基础地址（默认：https://code.newcli.com/gemini）

## 核心用法

```bash
export IMAGE_GEN_API_KEY="your-api-key"
export IMAGE_GEN_BASE_URL="https://code.newcli.com/gemini"
python3 scripts/generate_image.py "提示词" --model gemini-3.1-flash-image-2k-16x9 --output output.png
```

## 比例与模型选择

| 用途 | 推荐模型 |
|------|---------|
| 社交媒体头像 | gemini-3.1-flash-image（1:1） |
| 横版照片/视频封面 | gemini-3.1-flash-image-2k-16x9（16:9） |
| 竖版海报 | gemini-3.1-flash-image-2k-3x4（3:4） |
| 手机壁纸/短视频 | gemini-3.1-flash-image-2k-9x16（9:16） |
| 超宽屏 | gemini-3.1-flash-image-2k-21x9（21:9） |

分辨率：标准 → 2K（推荐） → 4K（最高质量）

## 提示词结构

- 主体描述（人物/场景/物品）
- 风格指定（水彩/油画/赛博朋克/吉卜力/摄影等）
- 光线/色调
- 构图（视角/景深）
- 比例指定

## 与nano-banana-pro的关系

两者都是Gemini图像API：
- **nano-banana-pro**：Gemini 3 Pro Image，适合精细创作
- **image-gen**：Gemini Flash Image 1.1，速度快，比例选择更丰富

根据需要选择使用。
