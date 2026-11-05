# PPT转培训视频 - API参考

## 核心工具调用

### 1. extract_ppt_content

提取PPT幻灯片内容：

```python
# 使用 pptx-generator 技能
invoke skill: pptx-generator
action: extract_text
file: "path/to/training.pptx"
```

返回格式：
```json
{
  "slides": [
    {
      "index": 1,
      "title": "培训标题",
      "content": ["要点1", "要点2"],
      "notes": "演讲者备注"
    }
  ]
}
```

### 2. gen_audios / batch_text_to_audio

生成语音旁白：

```json
{
  "audio_requests": [
    {
      "text": "接下来为大家介绍培训内容...",
      "output_file": "audio/slide_001.mp3",
      "voice": "female-qn-qingse",
      "speed": 1.0,
      "emotion": "happy"
    }
  ]
}
```

### 3. batch_image_to_video

生成视频片段：

```json
{
  "count": 1,
  "image_file_list": ["images/slide_001.png"],
  "output_file_list": ["videos/slide_001.mp4"],
  "prompt_list": ["专业培训演示，文字动画效果"],
  "duration_list": [6],
  "resolution_list": ["768P"]
}
```

### 4. ffmpeg 合并

```bash
# 创建文件列表
for f in videos/*.mp4; do echo "file '$f'" >> filelist.txt; done

# 合并视频
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# 添加音频（如果需要）
ffmpeg -i output.mp4 -i audio/combined.mp3 -c:v copy -c:a aac output_final.mp4
```

## 完整流程脚本

```python
import subprocess
import json
import os

def ppt_to_video(ppt_path, output_dir="output"):
    """完整转换流程"""

    # 1. 提取内容
    slides = extract_ppt_content(ppt_path)

    # 2. 生成旁白并转语音
    audio_files = []
    for i, slide in enumerate(slides):
        narration = generate_narration(slide)
        audio_file = f"{output_dir}/audio/slide_{i:03d}.mp3"
        gen_audio(narration, audio_file)
        audio_files.append(audio_file)

    # 3. 生成视频
    video_files = []
    for i, slide in enumerate(slides):
        img_file = f"{output_dir}/images/slide_{i:03d}.png"
        video_file = f"{output_dir}/videos/slide_{i:03d}.mp4"
        create_video(img_file, video_file)
        video_files.append(video_file)

    # 4. 合并最终视频
    final_output = f"{output_dir}/training_video.mp4"
    merge_videos(video_files, audio_files, final_output)

    return final_output
```

## 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| E001 | PPT文件不存在 | 检查文件路径 |
| E002 | 不支持的格式 | 转换为.pptx |
| E003 | 语音生成失败 | 更换语音或重试 |
| E004 | 视频生成失败 | 检查API额度 |
| E005 | FFmpeg未安装 | 安装FFmpeg |
