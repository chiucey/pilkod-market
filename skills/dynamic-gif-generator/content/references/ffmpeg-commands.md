# FFmpeg GIF转换命令参考

## 基础转换

### 视频转GIF（基础）
```bash
ffmpeg -i input.mp4 output.gif
```

### 视频转GIF（带参数）
```bash
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1" -loop 0 output.gif
```

## 进阶转换

### 高质量GIF转换（推荐）
```bash
ffmpeg -i input.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
```

### 截取片段转换
```bash
ffmpeg -i input.mp4 -ss 00:00:02 -t 3 -vf "fps=15,scale=480:-1" -loop 0 output.gif
```

### 从特定时间点开始
```bash
ffmpeg -i input.mp4 -ss 00:00:05 -i input.mp4 -t 2 -filter_complex "[0:v][1:v]concat=n=1:v=1:a=0[v]" -map "[v]" output.gif
```

## 图片序列转换

### 图片序列转GIF
```bash
ffmpeg -framerate 15 -i frame_%03d.png -vf "scale=480:480:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
```

### 调整帧率
```bash
ffmpeg -framerate 10 -i frame_%03d.png output_low_fps.gif
ffmpeg -framerate 24 -i frame_%03d.png output_high_fps.gif
```

## 优化与压缩

### 限制颜色数量
```bash
ffmpeg -i input.gif -vf "palettegen=max_colors=128" palette.png
ffmpeg -i input.gif -i palette.png -lavfi "paletteuse=dither=bayer:bayer_scale=3" output_optimized.gif
```

### 使用不同抖动算法
```bash
# Sierra 抖动
ffmpeg -i input.gif -lavfi "palettegen=stats_mode=diff" palette.png
ffmpeg -i input.gif -i palette.png -lavfi "paletteuse=dither=sierra2_4a" output.gif

# Floyd-Steinberg 抖动（最常用）
ffmpeg -i input.gif -lavfi "paletteuse=dither=floyd_steinberg" output.gif
```

### 尺寸调整
```bash
# 缩小到50%
ffmpeg -i input.gif -vf "scale=iw*0.5:ih*0.5" output_small.gif

# 固定宽度
ffmpeg -i input.gif -vf "scale=320:-1" output_320.gif

# 固定高度
ffmpeg -i input.gif -vf "scale=-1:320" output_320h.gif
```

## GIF编辑

### 裁剪GIF
```bash
ffmpeg -i input.gif -vf "crop=200:200:100:50" output_cropped.gif
```

### 添加边框
```bash
ffmpeg -i input.gif -vf "pad=width=iw+20:height=ih+20:x=10:y=10:color=white" output_bordered.gif
```

### 添加圆角
```bash
ffmpeg -i input.gif -vf "curves=all='0/0 0.5/0.5 1/1'" output_rounded.gif
```

### 旋转GIF
```bash
ffmpeg -i input.gif -vf "rotate=PI/2" output_rotated.gif
```

## GIF操作

### 调整播放速度
```bash
# 2倍速
ffmpeg -i input.gif -vf "setpts=0.5*PTS" output_fast.gif

# 0.5倍速（慢动作）
ffmpeg -i input.gif -vf "setpts=2*PTS" output_slow.gif
```

### 反向播放
```bash
ffmpeg -i input.gif -vf "reverse" -af "areverse" output_reversed.gif
```

### 合并GIF
```bash
ffmpeg -i part1.gif -i part2.gif -i part3.gif -filter_complex "[0:v][1:v][2:v]concat=n=3:v=1:a=0[outv]" -map "[outv]" combined.gif
```

### 截取部分GIF
```bash
ffmpeg -i input.gif -t 2 output_shortened.gif
```

### 倒放并循环
```bash
ffmpeg -i input.gif -vf "reverse,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse,split[s2][s3];[s2][s3]palettegen" -loop 0 output_bidirectional.gif
```

## 输出控制

### 设置循环次数
```bash
# 只播放1次
ffmpeg -i input.gif -loop 1 output_once.gif

# 播放3次
ffmpeg -i input.gif -loop 3 output_three_times.gif

# 无限循环
ffmpeg -i input.gif -loop 0 output_infinite.gif
```

### 调整质量
```bash
# 低质量（小文件）
ffmpeg -i input.gif -quality 10 output_low_quality.gif

# 高质量（大文件）
ffmpeg -i input.gif -quality 90 output_high_quality.gif
```

## 特效滤镜

### 褪色效果
```bash
ffmpeg -i input.gif -vf "fade=t=in:st=0:d=0.5" -af "afade=t=in:st=0:d=0.5" output_fade_in.gif
```

### 亮度/对比度
```bash
ffmpeg -i input.gif -vf "eq=brightness=0.1:contrast=1.2" output_adjusted.gif
```

### 锐化
```bash
ffmpeg -i input.gif -vf "unsharp=5:5:1.0:5:5:0.0" output_sharpened.gif
```

## 实用脚本

### 批量转换脚本
```bash
#!/bin/bash
for file in *.mp4; do
    ffmpeg -i "$file" -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 "${file%.mp4}.gif"
done
```

### 自动优化脚本
```bash
#!/bin/bash
ffmpeg -i "$1" -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=sierra2_4a" -loop 0 "optimized_$1"
```
