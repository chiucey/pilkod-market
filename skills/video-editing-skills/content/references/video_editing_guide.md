# 视频剪辑技术指南

## FFmpeg 常用命令

### 基础操作

```bash
# 查看视频信息
ffmpeg -i input.mp4

# 剪切视频
ffmpeg -i input.mp4 -ss 00:00:10 -t 00:00:30 -c copy output.mp4

# 合并视频
ffmpeg -f concat -i filelist.txt -c copy output.mp4

# 格式转换
ffmpeg -i input.avi -c:v libx264 -crf 23 output.mp4
```

### 音频处理

```bash
# 提取音频
ffmpeg -i input.mp4 -vn -acodec copy audio.aac

# 添加背景音乐
ffmpeg -i video.mp4 -i bgm.mp3 -filter_complex amix=inputs=2:duration=first output.mp4

# 音量调整
ffmpeg -i input.mp4 -af "volume=2.0" output.mp4

# 音频降噪
ffmpeg -i input.mp4 -af "anoisesuper=r=0.5" output.mp4
```

### 视频特效

```bash
# 添加水印
ffmpeg -i input.mp4 -i watermark.png -filter_complex "overlay=10:10" output.mp4

# 画中画
ffmpeg -i main.mp4 -i pip.mp4 -filter_complex "[1:v]scale=200:-1[pip];[0:v][pip]overlay=W-w-10:10" output.mp4

# 调整播放速度
ffmpeg -i input.mp4 -filter:v "setpts=2.0*PTS" output.mp4  # 慢放2倍
```

### 调色

```bash
# 增加亮度
ffmpeg -i input.mp4 -vf "eq=brightness=0.1" output.mp4

# 增加对比度
ffmpeg -i input.mp4 -vf "eq=contrast=1.2" output.mp4

# 暖色调
ffmpeg -i input.mp4 -vf "colorbalance=rs=0.3" output.mp4
```

## 输出格式参考

| 平台 | 分辨率 | 宽高比 | 码率 | 格式 |
|-----|-------|-------|-----|-----|
| 抖音 | 1080x1920 | 9:16 | 8-15 Mbps | MP4 |
| 快手 | 1080x1920 | 9:16 | 8-15 Mbps | MP4 |
| B站 | 1920x1080 | 16:9 | 10-20 Mbps | MP4 |
| YouTube | 1920x1080 | 16:9 | 10-20 Mbps | MP4 |
| 微信 | 1080x1920 | 9:16 | 5-10 Mbps | MP4 |

## 字幕规范

### 时间轴格式（SRT）

```
1
00:00:01,000 --> 00:00:04,000
这是第一行字幕

2
00:00:04,500 --> 00:00:07,000
这是第二行字幕
```

### 字幕设计规范

- 字体大小：画面高度的 1/15 ~ 1/20
- 字体颜色：白色（#FFFFFF）
- 描边：2-3px 黑色
- 位置：底部留 10% 边距
- 每行字数：不超过 15 个汉字
