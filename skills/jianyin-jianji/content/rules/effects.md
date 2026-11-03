---
name: effects
description: 视频转场、滤镜、调色、特效、关键帧动画。
tags: effects, transitions, filters, color, keyframe
---

# 视频特效规则

## 转场（Transitions）

> 注意：OpenClaw 环境（Linux）可通过 FFmpeg 视频滤镜实现转场，无需剪映。

```bash
# 溶解（Dissolve）：淡入淡出重叠
ffmpeg -i part1.mp4 -i part2.mp4 -filter_complex \
  "[0:v][1:v]blend=all_expr='A*(1-if(t-{dur},0,1))+B*if(t-{dur},0,1)'" \
  -pix_fmt yuv420p transition.mp4

# 硬切（无转场）
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# 叠化（Cross-dissolve）：经典电影感
ffmpeg -i part1.mp4 -i part2.mp4 -filter_complex \
  "[0:v][1:v]xfade=transition=fade:duration=1:offset=9" \
  -c:v libx264 -c:a aac transition.mp4
```

**常用 xfade 参数**：
| 转场类型 | transition 参数 | 时长建议 |
|---|---|---|
| 淡入淡出 | `fade` | 0.5~1.5s |
| 滑入 | `slideright/slideleft/slideup/slidedown` | 0.5~1s |
| 模糊 | `blur` | 1~2s |
| 放大 | `zoomout` | 0.5~1s |
| 圆形 | `circleclose` | 1s |

## 调色（Color Grading）

```bash
# 提亮（曝光补偿）
ffmpeg -i input.mp4 -vf "eq=brightness=0.08:saturation=1.2" output.mp4

# 电影感（LUT 风格）
ffmpeg -i input.mp4 -vf "colorbalance=rs=0.2:gs=0.1:bs=0.15:rm=-0.1:gm=-0.05:bm=-0.1" cinematic.mp4

# 冷色调（科技/忧郁）
ffmpeg -i input.mp4 -vf "colortemperature=6500:blue=0.3:red=-0.1" cool.mp4

# 暖色调（活力/回忆）
ffmpeg -i input.mp4 -vf "colortemperature=4200:red=0.2:blue=-0.15" warm.mp4

# 高对比度（电影黑帮感）
ffmpeg -i input.mp4 -vf "curves=all='0/0 0.2/0.05 0.5/0.5 0.8/0.95 1/1'" contrast.mp4
```

## 滤镜效果

```bash
# 磨皮（人像美颜）
ffmpeg -i input.mp4 -vf "fastdemoise=w=3:p=1" denoise.mp4

# 锐化
ffmpeg -i input.mp4 -vf "unsharp=5:5:0.5:3:3:0.3" sharp.mp4

# 虚化背景（景深）
ffmpeg -i input.mp4 -vf "boxblur=5:1,scale=800:450,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" bokeh.mp4

# 4:3 复古效果
ffmpeg -i input.mp4 -vf "curves=vintage,scale=1440:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" retro.mp4
```

## 文字特效（FFmpeg drawtext）

```bash
# 基础文字水印
ffmpeg -i input.mp4 -vf "drawtext=text='@你的账号':fontsize=48:fontcolor=white:x=(w-text_w)-20:y=h-text_h-20:shadow=2:shadowcolor=black@0.5" output.mp4

# 动态文字（滚动）
ffmpeg -i input.mp4 -vf "drawtext=text='片头字幕':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=h/2:enable='between(t,0,2)':alpha=0.8" output.mp4
```

## 片头片尾模板

```bash
# 片头：黑场 + 标题文字（3s）
# 片尾：白场淡出 + 账号信息
# 全流程：
# 1. 生成片头 MP4（纯色 + 文字）
# 2. FFmpeg concat 拼接
# 3. 合成 BGM + 配音
```

## 特效合成检查清单

- [ ] 转场不超过视频总时长 5%（避免拖沓）
- [ ] 调色统一（色温/饱和度/对比度一致）
- [ ] 片头片尾时长合理（片头 1~3s，片尾 2~5s）
- [ ] 运动特效不要过于剧烈（易晕）
