---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 3a395ae7e456167025c5f4a376aa3ab4
    PropagateID: 3a395ae7e456167025c5f4a376aa3ab4
    ReservedCode1: 30450220628f731f5ad60dd9c036d31c618d9340dbaf78f4163b6de89767f3737dc36a8f022100df271f7a776968a46484c20b148b8ca71c0bd65bc106933062f9eacaa86b8568
    ReservedCode2: 30440220362591e2e7e3f5ae73938187774464f5bc574aef5753b1caa3d3aa3ed8d9bcf502203de03b841e525c9dc271ddb9efeceeffb1b78a2cfb5118170f213a21f209a04a
description: 视频智能裁剪工具。当用户要求将长视频分割为多个短视频片段、进行视频剪辑、批量裁剪视频或使用命令行工具处理视频时使用。支持三种分割模式：顺序分割、重叠分割和自定义分割。
name: video-clipper
---

# 视频智能裁剪工具

快速将长视频分割为多个不雷同的短视频片段，支持顺序分割、重叠分割和自定义分割三种模式。

## 核心功能

- **三种分割模式**：顺序分割、重叠分割（推荐）、自定义分割
- **智能计算**：自动根据视频时长和目标数量计算最佳分割点
- **批量处理**：一次生成多个视频片段
- **高质量输出**：保留原视频画质，H.264编码
- **自动保存**：自动保存到系统下载文件夹

## 参数配置

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input` | 输入视频文件路径 | 必需 |
| `-n，--num-clips` | 要生成的视频数量 | 10 |
| `-t，--max-duration` | 每个视频的最大时长（秒） | 30 |
| `-m，--mode` | 分割模式：sequential/overlapping/custom | overlapping |
| `-s，--segments` | 自定义片段："start1,end1 start2,end2 ……" | 无 |
| `-o，--output-dir` | 输出目录 | 下载文件夹 |

### 分割模式

| 模式 | 说明 | 适用场景 |
|------|------|---------|
| `overlapping` | 每个片段有重叠，确保不遗漏关键时刻 | 通用推荐 |
| `sequential` | 将视频等分为连续片段 | 教学视频、章节分割 |
| `custom` | 完全自定义每个片段的起止时间 | 精确控制 |

## 使用示例

### 基本用法（重叠分割）

```bash
python video_clipper.py input.mp4 -n 10 -t 30
```

### 顺序分割

```bash
python video_clipper.py course.mp4 -m sequential -n 5
```

### 自定义分割

```bash
python video_clipper.py input.mp4 -m custom -s "0,25 10,35 20,45"
```

## 依赖要求

- Python 3.6+
- ffmpeg 和 ffprobe（系统命令）

### 安装 ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# CentOS
sudo yum install ffmpeg
```

## 代码

核心代码位于 `video_clipper.py`，使用请参考references目录中的详细文档。
