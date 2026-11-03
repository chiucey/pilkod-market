---
name: video-generate
description: 即梦/Seedance 图片生视频、视频拼接、素材组装。
tags: video, generation, image-to-video, jimeng, seedance, i2v
---

# AI 视频生成规则

## 工具选择

| 场景 | 工具 |
|---|---|
| 文字生成视频（T2V） | `batch_text_to_video` |
| 图片生成视频（I2V） | `batch_image_to_video` |
| 高质量视频生成 | `gen_videos`（支持更长时长/更高分辨率）|
| 多段视频拼接 | FFmpeg concat |

## 文生视频（T2V）规范

```python
# 提示词结构
batch_text_to_video(
    count=1,
    prompt_list=["[主体]在[场景]中[动作]，画面[风格描述]"],
    output_file_list=["/path/to/output.mp4"],
    duration_list=[6],    # 6s 或 10s
    resolution_list=["768P"]  # 或 "1080P"
)
```

**提示词技巧**：
- 主体要具体："一位穿汉服的中国女孩" 而非 "女孩"
- 场景要交代："在古风茶馆里"、"海边日落"
- 风格要明确："电影感"、"宫崎骏动画风格"、"写实纪录片"
- 运镜描述："镜头缓慢推进"、"航拍视角"、"微距特写"

## 图生视频（I2V）规范

```python
batch_image_to_video(
    count=1,
    image_file_list=["/path/to/input.png"],
    output_file_list=["/path/to/output.mp4"],
    prompt_list=["[描述视频运动方式]"],
    reference_type_list=["first_frame"],  # 锁定首帧
    duration_list=[6],
    resolution_list=["768P"]
)
```

**首帧要求**：
- 图片最短边 ≥ 300px
- 避免文字过多（首帧有文字会导致视频变形）
- 推荐 1920×1080 或 1080×1920 纯色/实拍图

## 视频拼接（FFmpeg concat）

```bash
# 拼接多个视频（相同编码）
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# filelist.txt 内容：
# file 'part1.mp4'
# file 'part2.mp4'
# file 'part3.mp4'

# 不同编码则重编码：
ffmpeg -f concat -safe 0 -i filelist.txt -c:v libx264 -c:a aac output.mp4
```

## 分辨率与比例一致性

```bash
# 统一分辨率（缩放+裁剪）
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" output.mp4

# 竖屏转横屏（加黑边）
ffmpeg -i vertical.mp4 -vf "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black" output.mp4
```

## 时长控制

- 即梦单次生成最长 10s
- 超过 10s：分段生成 → FFmpeg 拼接
- 建议 AI 生成视频控制在 6s/段，质量最稳定
