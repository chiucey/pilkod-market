---
name: 语音转文字助手生成器
description: 生成优雅高效的语音转文字工具，支持拖拽上传音频/视频文件，自动转换为可编辑文本。适用于会议录音、课程录音、采访音频、短视频语音等场景。
keywords:
  - 语音转文字
  - speech to text
  - audio transcription
  - 录音转文字
  - audio to text
  - 音频转文字
---

# 语音转文字助手 - Speech-to-Text Assistant

## 1. 技能概述

- **技能标识**: speech-to-text-assistant
- **适用场景**: 会议录音转写、课程录音转写、采访音频转写、短视频语音转写

## 2. 功能描述

一款优雅高效的本地语音转文字工具，将音频/视频文件快速准确地转换为可编辑的文本内容。界面设计灵感来自专业录音室的控制台，结合现代极简美学，营造出专注、高效的工作氛围。支持多种常见音视频格式，让用户在任何场景下都能轻松完成转写任务。

## 3. 设计规范

### 3.1 色彩体系
| 用途 | 色值 | 说明 |
|------|------|------|
| 主色 | `#6366F1` (Indigo) | 主操作按钮、强调元素 |
| 辅助色 | `#22D3EE` (Cyan) | 进度条、活跃状态 |
| 强调色 | `#F472B6` (Pink) | 重要提示、完成状态 |
| 背景色 | `#0F172A` (Slate 900) | 主背景 |
| 表面色 | `#1E293B` (Slate 800) | 卡片和面板 |
| 边框色 | `#334155` (Slate 700) | 边框和分隔线 |
| 主文字 | `#F1F5F9` (Slate 100) | 主要文字 |
| 次文字 | `#94A3B8` (Slate 400) | 次要文字 |

### 3.2 字体规范
- **主字体**: Inter, system-ui, sans-serif
- **等宽字体**: JetBrains Mono, monospace (时间戳、代码)
- **字号层级**: 14px(正文) / 16px(副标题) / 24px(标题) / 36px(大标题)

### 3.3 空间系统
- 基础单位: 4px
- 卡片内边距: 24px
- 区块间距: 32px
- 圆角: 12px(卡片) / 8px(按钮) / 16px(大容器)

### 3.4 动效规范
- 文件拖拽: scale 1.02 + 阴影提升, 200ms ease-out
- 进度条: 平滑渐变动画
- 按钮悬停: 微发光 + scale 1.02, 150ms
- 文本出现: 淡入 + 上滑, 间隔 50ms

## 4. 布局结构

```
┌─────────────────────────────────────────┐
│  Header: Logo + Title + Settings        │
├─────────────────────────────────────────┤
│  Drop Zone: Drag & Drop or Click       │
│  (Large central area, 200px height)    │
├─────────────────────────────────────────┤
│  File Info Panel                       │
│  - Waveform | Filename | Duration      │
├─────────────────────────────────────────┤
│  Control Bar                            │
│  [ Transcribe ] [ Pause ] [ Stop ]      │
│  Progress Bar with percentage          │
├─────────────────────────────────────────┤
│  Transcript Display Area               │
│  - Real-time transcription display     │
│  - Timestamp labels                    │
│  - Editable area                       │
├─────────────────────────────────────────┤
│  Action Bar: [ Copy ] [ Download ]     │
└─────────────────────────────────────────┘
```

### 响应式策略
- **桌面端** (>1024px): 全功能布局
- **平板端** (768-1024px): 紧凑布局
- **移动端** (<768px): 单列布局

## 5. 功能模块

### 5.1 文件上传
- 支持拖拽上传和点击选择
- 支持格式: MP3, WAV, M4A, OGG, MP4, WEBM, MOV, AVI
- 最大文件限制: 500MB
- 拖拽视觉反馈

### 5.2 语音转写引擎
- 使用 Web Speech API 进行浏览器端语音识别
- 支持中文、英文混合识别
- 模型加载进度显示

### 5.3 实时进度显示
- 文件加载进度
- 转写进度百分比
- 预估剩余时间

### 5.4 转写结果处理
- 显示时间戳
- 一键复制到剪贴板
- 下载为 TXT 文件
- 文本可编辑修正

## 6. 组件清单

### DropZone
- **默认**: `#1E293B` 背景, `#334155` 虚线边框
- **悬停**: 边框 `#6366F1`, 微发光
- **拖拽中**: 边框实线 `#6366F1`, 背景 `rgba(99, 102, 241, 0.1)`, scale 1.02

### FileInfoCard
- 左侧: 音频波形缩略图
- 右侧: 文件名、格式、时长、大小
- 删除按钮(悬停显示)

### ProgressBar
- 背景: `#334155`
- 填充: 线性渐变 `#6366F1` → `#22D3EE`
- 动画: 渐变流动效果

### TranscriptPanel
- 容器: `#1E293B` 背景, 24px 内边距
- 时间戳: `#6366F1` 文字
- 转写文本: 18px 字号, 1.8 行高

### ActionButton
- **主按钮**: `#6366F1` 背景, 白色文字, 悬停发光
- **次按钮**: `#334155` 背景
- **禁用**: 50% 透明度

### WaveformVisualizer
- Canvas 绘制波形
- 蓝色渐变条形
- 动态播放动画

## 7. 技术方案

### 架构
- 单页 HTML + CSS + JavaScript
- Web Speech API (语音识别)
- WaveSurfer.js (音频可视化)
- Lucide Icons (图标库)

### 外部资源
- Google Fonts: Inter, JetBrains Mono
- unpkg CDN: lucide, wavesurfer.js

### 数据流
1. 文件选择 → 文件读取 → 格式验证
2. 音频解码 → 初始化识别器
3. 分块处理音频 → 实时输出文本
4. 文本累积 → 显示转写结果
5. 用户操作 → 复制/下载/编辑

## 8. 浏览器兼容性
- Chrome 90+
- Firefox 88+
- Safari 15+
- Edge 90+

## 9. 使用说明

1. 打开部署的网页
2. 拖拽音频/视频文件到上传区域，或点击选择文件
3. 点击"开始转写"按钮
4. 等待转写完成
5. 复制或下载转写结果

## 10. 实现代码模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>语音转文字助手</title>
    <!-- 引入字体、图标库、波形库 -->
</head>
<body>
    <!-- 主要布局结构 -->
    <script>
        // 使用 Web Speech API 实现语音识别
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'zh-CN';
    </script>
</body>
</html>
```

## 11. 部署信息

- **部署命令**: deploy tool with dist directory
- **部署路径**: dist/index.html

## 12. 注意事项

- Web Speech API 需要浏览器支持语音识别功能
- 建议使用 Chrome 浏览器以获得最佳体验
- 大文件处理可能需要较长时间
- 转写结果支持手动编辑修正