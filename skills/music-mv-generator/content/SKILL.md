---
name: music-mv-generator
description: 基于用户提供的音频(及可选图片)生成专业音乐MV视频。当用户需要为歌曲/音频制作音乐视频、动态可视化、演唱画面、MV时使用。包含环境校验、分镜规划、Remotion代码生成、渲染到MP4的完整流程。
---

# 音乐 MV 生成技能

将音频文件制作成完整的音乐视频（Music Video），支持音频频谱可视化、人物画面、歌词字幕等多种视觉元素。

## 触发场景

- 用户提供音频/歌曲，要求"生成MV / 音乐视频 / 动态可视化"
- 用户要求给歌曲配画面、配动态背景、做成视频
- 用户提供人物照片/图片要求做成演唱MV

## 输入需求

- **必选**：音频文件（MP3/WAV，建议压缩格式减小体积）
- **可选**：人物肖像图片、专辑封面、歌词文本、品牌配色

## 工作流程

### 1. 环境校验
```bash
node --version        # 需 v16+
ffmpeg -version       # 需可用
cd "$PROJECT_DIR" && npm install remotion@^4.0.0 @remotion/cli@^4.0.0 react@^19.0.0 react-dom@^19.0.0 @remotion/media-utils
```

### 2. 获取音频时长（决定视频总长度）
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio.wav
```
总帧数 = `时长秒 × fps(30)`

### 3. 分镜规划（五幕结构）
| 幕 | 时间 | 内容 |
|---|---|---|
| Scene1 | 0-15s | 标题淡入，氛围光，署名 |
| Scene2 | 15-55s | 人物肖像电影感慢推、镜头晃动、色彩叠加 |
| Scene3 | 55-115s | 音频频谱条形图实时响应 |
| Scene4 | 115-185s | 特写变焦、浮光粒子、冷暖渐变 |
| Scene5 | 185-结束 | 拉远淡出至黑，署名定格 |

### 4. 生成 Remotion 代码
- 项目结构：
```
src/compositions/[video-name]/
├── VideoComposition.tsx   # 主合成(Sequence编排)
├── Scene1..5.tsx          # 各场景组件
└── constants.ts           # 可编辑常量(配色/时间/文案)
```
- 遵循 Remotion 规范：`useCurrentFrame()` + `interpolate`/`spring` 驱动动画，禁止 CSS transition；资源用 `staticFile()`；字体用 `@remotion/google-fonts`

### 5. 音频可视化（Scene3）
```typescript
import { useAudioData, visualizeAudio } from "@remotion/media-utils";
const audioData = useAudioData(audioSrc);
if (!audioData) return null;
const samples = visualizeAudio({ fps, frame, audioData, numberOfSamples: 64, smoothing: true });
```
> ⚠️ `numberOfSamples` 必须是 2 的幂（32/64/128），否则报错。

### 6. 渲染 MP4
```bash
npx remotion render src/index.ts music-mv out/music-mv.mp4 --concurrency=4 --jpeg-quality=80
```

## 质量要点

- [ ] 频谱条数用 2 的幂
- [ ] 场景间淡入淡出交叉过渡(15-25帧)
- [ ] 配色统一，标题可读
- [ ] 音频与画面每帧对齐
- [ ] 常量集中在文件顶部便于修改
- [ ] 720p/1080p，30fps 输出

## 常见错误与解决

| 错误 | 解决 |
|---|---|
| `bars must be a power of two` | 频谱条数改为 64/128 |
| `staticFile not found` | 资源放 public/ 下，路径用 `assets/xxx` |
| `Failed to launch browser` | 补齐 chrome-headless-shell 及 .pak 资源文件 |
| 音频404 | 用 `staticFile("assets/audio.wav")` 并放对位置 |
