---
name: video-captioner
description: VideoCaptioner (卡卡字幕助手) 技能，用于视频字幕处理。当用户需要处理视频字幕、语音识别、字幕翻译、视频下载或字幕烧录时使用。支持Bilibili、YouTube等平台，支持 Whisper/faster-Whisper 本地语音识别和 LLM 智能字幕优化翻译。
---

# VideoCaptioner - 卡卡字幕助手

VideoCaptioner 是一款基于 LLM 的视频字幕处理助手，支持语音识别、字幕分割、优化、翻译的完整工作流程。

## 核心功能

### 1. 多平台视频下载与处理
- 支持 Bilibili、YouTube、TikTok、X 等主流视频平台
- 自动提取和处理已有字幕

### 2. 专业语音识别引擎
| 接口 | 语言 | 模式 | 说明 |
|------|------|------|------|
| B接口 | 中英文 | 在线 | 免费、快速 |
| J接口 | 中英文 | 在线 | 免费、快速 |
| WhisperCpp | 99+语言 | 本地 | 需下载模型 |
| fasterWhisper (推荐) | 99+语言 | 本地 | 支持CUDA，高精度 |

### 3. 智能字幕校正
- 自动优化专业术语、代码片段、数学公式
- 基于上下文进行分割优化
- 支持文档提示实现精确分割

### 4. 高质量字幕翻译
- 基于上下文智能翻译
- 通过 LLM 反思机制改进翻译
- 模糊匹配算法确保时间戳一致

### 5. 字幕样式调整
- 丰富的字幕样式模板（教育、新闻、动漫风格）
- 多种字幕视频格式支持（SRT、ASS、VTT、TXT）

## 快速开始

### Windows 用户
1. 从 [Release](https://github.com/WEIFENG2333/VideoCaptioner/releases) 或 [蓝奏云](https://wwwm.lanzoue.com/ii14G2pdsbej) 下载预编译版本
2. 安装并启动程序
3. 配置 LLM API（用于字幕分割和校正）
4. 配置翻译设置
5. 配置语音识别
6. 拖入视频文件开始处理

### macOS / Linux 用户
```bash
git clone https://github.com/WEIFENG2333/VideoCaptioner.git
cd VideoCaptioner
chmod +x run.sh
./run.sh
```

### 手动安装 (macOS)
```bash
brew install ffmpeg
brew install aria2
brew install python@3.11
git clone https://github.com/WEIFENG2333/VideoCaptioner.git
cd VideoCaptioner
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## LLM API 配置

### 推荐服务商
| 提供商 | 地址 | 说明 |
|--------|------|------|
| SiliconCloud | https://cloud.siliconflow.cn | 低并发推荐 |
| DeepSeek | https://platform.deepseek.com/ | 使用 deepseek-v3 模型 |
| OpenAI 兼容 | 使用 base_url 和 api_key | 通用配置 |
| VideoCaptioner API (推荐) | https://api.videocaptioner.cn/v1 | 从个人中心获取 API-key |

### 模型推荐
- 高质量：`gemini-2.5-pro`、`claude-sonnet-4-5-20250929`
- 中高：`gpt-5-2025-08-07`、`claude-haiku-4-5-20251001`
- 中等：`gpt-5-mini`、`gemini-2.5-flash`

## 本地 Whisper 模型选择

| 模型 | 磁盘空间 | 内存需求 | 说明 |
|------|----------|----------|------|
| Tiny | 75 MiB | ~273 MB | 基础测试 |
| Small | 466 MiB | ~852 MB | 英文效果好 |
| Medium | 1.5 GiB | ~2.1 GB | 中文最低要求 |
| Large-v2 | 2.9 GiB | ~3.9 GB | 推荐使用 |
| Large-v3 | 2.9 GiB | ~3.9 GB | 可能存在幻觉问题 |

## 翻译配置选项

1. **LLM 模型翻译** - 最佳质量
2. **Microsoft Translator** - 速度快
3. **Google Translate** - 需要访问 Google 网络

## 使用流程

```
语音识别 → 字幕分割(可选) → 字幕优化/翻译(可选) → 视频合成
```

### 字幕转录页面
- **VAD 过滤**：过滤非语音片段，减少幻觉
- **音频分离**：使用 MDX-Net 降噪（用于嘈杂视频）

### 字幕优化翻译页面
- **智能分割**：生成词级时间戳，使用 LLM 进行分割
- **字幕校正**：通过 LLM 修正大小写、标点、错字
- **反思翻译**：迭代改进翻译质量
- **文档提示**：提供上下文用于优化

### 字幕视频合成页面
- **硬字幕合成**：将字幕烧录到视频中
- **软字幕**：快速处理，需要兼容播放器

## 项目结构

```
VideoCaptioner/
├── runtime/          # 运行时环境
├── resources/       # 软件资源 (faster-whisper, 图标)
├── work-dir/        # 处理视频输出目录
├── AppData/         # 应用数据
├── cache/           # 转录和 LLM 请求缓存
├── models/          # Whisper 模型文件
├── logs/            # 日志文件
├── settings.json    # 用户设置
└── cookies.txt      # 视频平台 cookies
```

## 依赖项

- Python (99.3%)
- ffmpeg (必需)
- aria2 (用于下载)
- PyQt (GUI)
- faster-whisper 或 whisper (ASR)
- OpenAI API 兼容库

## 常见问题

### Q: 视频下载失败怎么办？
A: 在 AppData 目录放置 cookies.txt 文件（从浏览器导出的 cookies）

### Q: 语音识别速度慢？
A: 推荐使用 fasterWhisper + CUDA，或选择 B/J 接口在线识别

### Q: 如何提高翻译质量？
A: 使用高质量 LLM 模型（如 gemini-2.5-pro），启用反思翻译功能

### Q: 字幕时间轴不准？
A: 启用词级时间戳功能，或手动在文档提示中提供原文稿

## 资源链接

- 官网：https://www.videocaptioner.cn
- GitHub：https://github.com/WEIFENG2333/VideoCaptioner
- 在线文档：https://weifeng2333.github.io/VideoCaptioner/
- API 中间服务：https://api.videocaptioner.cn/
