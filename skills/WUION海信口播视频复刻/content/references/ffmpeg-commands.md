# ffmpeg/ffprobe 命令清单

复刻视频时常用的确定性命令。按调用顺序排列。

## 1. ffprobe 读元数据

```bash
ffprobe -v error -show_format -show_streams <video>
```

提取字段：
- `format.duration`：容器时长（秒，浮点）
- `stream[0].duration`：视频流时长
- `stream[0].width × height`
- `stream[0].avg_frame_rate`：帧率（"60/1" 表示 60fps）
- `stream[0].nb_frames`：总帧数
- `stream[1].duration`：音频时长
- `stream[1].sample_rate`：采样率
- `stream[1].channels`：声道数

**取总时长优先级**：视频流 duration × 帧率 / 帧率（最准）> 视频流 duration > format duration。0.01s 精度四舍五入。

## 2. 抽帧（0.2s 间隔）

```bash
mkdir -p frames_200ms
ffmpeg -i <video> \
  -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,0.2)',showinfo" \
  -vsync vfr frames_200ms/f_%03d.jpg
```

生成的 `f_001.jpg` ~ `f_NNN.jpg` 对应 0.0s, 0.2s, 0.4s, ... 时间点。
**注意**：showinfo 输出里会写实际 pts_time，与 0.2s 整数倍有微小偏差（受源视频帧率限制），但都在 ±0.1s 内，足够用于视觉分析。

替代方案（按帧号精确抽帧）：
```bash
# 0.2s × 60fps = 12 帧间隔
ffmpeg -i <video> -vf "select='not(mod(n\,12))',showinfo" -vsync vfr frames/f_%03d.jpg
```

## 3. 抽帧（2fps 粗筛，用于 0.5s 间隔快速预览）

```bash
ffmpeg -i <video> -vf "fps=2" frames_2fps/f_%03d.jpg
```

`f_001.jpg` = 0.5s, `f_002.jpg` = 1.0s, ... 用于快速看视频大致内容。

## 4. 提取音频（不保存，仅用于转录）

```bash
ffmpeg -i <video> -vn -acodec pcm_s16le -ar 44100 -ac 2 /tmp/_ref_audio.wav
```

参数说明：
- `-vn`：不要视频流
- `-acodec pcm_s16le`：转 16-bit PCM（listen_audio 兼容）
- `-ar 44100`：44.1kHz 采样率
- `-ac 2`：立体声

## 5. 上传到 mcode-tools

```bash
mcode-tools upload_temp_url /tmp/_ref_audio.wav
```

返回字段：
- `temp_url`：1 小时有效的 HTTPS URL
- `expires_in_seconds`：3600

## 6. 调用 audios_understand 转录

```bash
mcode-tools connector call connector__matrix__audios_understand --args '{
  "audio_info":[{
    "url":"<temp_url>",
    "prompt":"逐字转录中文口播，句级时间戳精确到 0.01s。格式：开始秒-结束秒: 文本。总时长 X.XX 秒，最后一句的结束秒必须 ≤ X.XX。"
  }]
}'
```

替代 listen_audio（更精确但慢）：
```bash
mcode-tools connector call connector__matrix__listen_audio --args '{
  "audio_info":{
    "url":"<temp_url>",
    "prompt":"verbatim 逐字转录中文，词级时间戳 0.01s。"
  }
}'
```

**多次转录策略**：如果两次结果不一致（常见），以 listen_audio 的句级结果为主，audios_understand 的词级结果为辅（拆分冲突时再调）。

## 7. 抽帧 + 保存到工作目录

```bash
WORK=/workspace/work
mkdir -p $WORK
cp <video> $WORK/ref.mp4
cd $WORK
ffmpeg -i ref.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 /tmp/_ref_audio.wav
ffmpeg -i ref.mp4 -vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,0.2)'" \
  -vsync vfr frames/f_%03d.jpg
```

## 8. 验证时长精度

```bash
# 视频流精确时长 = duration_ts / time_base_scale
ffprobe -v error -select_streams v -count_packets -show_entries stream=duration_ts,time_base -of csv=p=0 ref.mp4
```

## 9. 提取最后一帧

```bash
# 抽最后一帧用于验证视频是否完整
ffmpeg -sseof -0.1 -i ref.mp4 -update 1 -q:v 1 last_frame.jpg
```

## 常见错误

- **抽帧错位**：`fps=2` 抽的帧 pts_time 是 0.5s, 1.0s, ... 但 select filter 的 pts_time 受源视频 frame rate 限制有偏移。**总是用 showinfo 检查实际 pts_time**。
- **音频转码失败**：`pcm_s16le` 在某些 hevc 视频上需先 `-c:v copy -an`，但本场景只抽音频不需要。
- **上传文件失败**：检查文件大小 < 50MB（本 skill 抽的 wav 通常 1-2MB，问题不大）。
