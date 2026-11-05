---
name: vocal-extractor
description: 🎤 AI 人声提取器 — 一键从音频/视频中分离出纯净人声。基于 Meta 开源 Demucs htdemucs_ft 模型（Hybrid Transformer），比传统 Spleeter 高 3dB 音质，背景音乐残留极少。输入 MP3/WAV/FLAC/OGG 或视频 MP4/AVI/MOV/MKV，自动输出4个音轨：纯净人声(vocals)、鼓组(drums)、低音(bass)、其他伴奏(other)。适用于语音克隆素材准备、卡拉OK伴奏生成、播客去噪、音频修复等场景。零门槛，Python小白直接运行，一行命令搞定。
homepage: https://github.com
metadata:
  {
    openclaw:
      {
        emoji: "🎤",
        install: ["pip3 install demucs librosa soundfile --break-system-packages"],
      }
  }
---

# 🎤 Vocal Extractor — AI 人声提取器

> **把任何音频/视频中的一段人声，干净地剥离出来。**
> 基于 Meta 开源模型 Demucs htdemucs_ft，Hybrid Transformer 架构，业界领先的音轨分离质量。

---

## ✨ 功能亮点

- 🎯 **纯净人声**：去除背景音乐残留极少，比传统 Spleeter 高 3dB SDR 音质
- 📦 **全音轨输出**：同时输出人声、鼓组、低音、其他伴奏 4 个独立音轨
- 🎬 **视频直入**：支持 MP4/AVI/MOV/MKV 视频，自动先提取音轨再分离
- ⚡ **零门槛**：Python 脚本直接运行，无需手动配置模型或写代码
- 🔧 **自动 Patch**：内置 torchaudio 兼容修复，主流环境都能运行

---

## 核心技术

**Demucs htdemucs_ft（Meta 开源）** 采用了当前业界领先的 Hybrid Transformer 架构：

| 维度 | 旧方案（Spleeter） | 本技能（Demucs htdemucs_ft） |
|------|-------------------|--------------------------|
| 发布时间 | 2019年 | 2022-2024年 |
| 模型架构 | U-Net 频谱图 | Hybrid Transformer + Waveform |
| 音质（SDR） | 旧（基准） | **高约 3dB（感知翻倍）** |
| 集成方式 | 单模型 | **4模型 Bag-of-4 平均** |
| 频率分辨率 | 固定 | canvas_size=512 高分辨率 |
| 背景残留 | 明显 | **极少** |

**关键技术**：同时在频谱图（Spectrogram）和原始波形（Waveform）两个域做分离，用 Transformer attention 捕获长距离音乐依赖（和弦/节奏/结构），4 个不同初始化模型集成预测取平均，最大程度抑制伪影和噪声。

---

## 📋 支持格式

| 输入类型 | 格式 |
|---------|------|
| 音频文件 | MP3、WAV、FLAC、OGG、M4A |
| 视频文件 | MP4、AVI、MOV、MKV、FLV、WMV、WebM |

---

## 🚀 使用方法

### 基础用法（音频直接提取）

```bash
python3 /workspace/skills/vocal-extractor/extract_vocals.py 输入音频.mp3
```

### 从视频提取人声

```bash
python3 /workspace/skills/vocal-extractor/extract_vocals.py 视频.mp4
```

### 指定输出目录

```bash
python3 /workspace/skills/vocal-extractor/extract_vocals.py 输入.wav 输出目录
```

### 首次安装依赖（如报错，依次运行）

```bash
pip3 install demucs librosa soundfile --break-system-packages -q
```

---

## 📁 输出文件

运行后在同目录生成 4 个文件：

| 文件 | 内容 | 典型场景 |
|------|------|---------|
| `vocals.wav` | 🎤 **纯净人声** | 语音克隆、卡拉OK、配音素材 |
| `drums.wav` | 🥁 鼓组 | 音乐制作、混音 |
| `bass.wav` | 🎸 低音贝斯 | 音乐制作 |
| `other.wav` | 🎹 其他伴奏（吉他/钢琴等）| 音乐分析、伴奏生成 |

---

## 💡 适用场景

- 🎙️ **语音克隆**：提取纯净人声作为音色克隆素材，克隆专属AI声音
- 🎤 **卡拉OK伴奏**：去除人声生成纯伴奏用于唱歌
- 🎙️ **播客降噪**：分离人声和背景音乐，提升音质
- 🎬 **视频配音**：从视频中提取干净的人声对白
- 📚 **音频修复**：分离后单独处理人声或伴奏

---

## ⚠️ 注意事项

- 分离速度约 45 秒（CPU，27 秒音频），耐心等待即可
- 人声质量取决于原始录音质量，录音越干净分离效果越好
- 如遇 `torchcodec` 相关报错，脚本已内置自动 Patch，可直接忽略
- 推荐使用 WAV/FLAC 无损格式输入以获得最佳效果
