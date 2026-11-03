---
name: music-generator
description: 当用户请求生成音乐、创作歌曲、歌词谱曲、制作音乐或需要根据歌词和风格生成音乐时使用。支持流行、爵士、电子、古典、摇滚、嘻哈等各类风格。
---

# 音乐生成技能

## 功能说明

根据用户提供的歌词和风格偏好，自动生成音乐。支持多种音乐风格，可自定义歌词结构（Verse、Chorus、Bridge、Outro 等）。

## 使用前提

确保用户提供了以下信息：
- **歌词内容**：包含结构标签的歌词（如 `[Verse]...` `[Chorus]...`）
- **音乐风格**：如流行、爵士、电子、古典、摇滚、嘻哈、乡村、蓝调等
- **其他偏好**：可指定心情、场景（如庆祝、放松、动感等）

## 执行流程

### 步骤 1：收集用户需求

使用 GenUI 表单收集以下信息：

```xml
<genui-form-wizard title="音乐生成" action-id="music_generation">
  <genui-form-page title="步骤 1: 歌词内容">
    <genui-input name="lyrics" placeholder="请输入歌词，使用 [Verse][Chorus][Bridge][Outro] 等标签分隔段落..."></genui-input>
  </genui-form-page>
  <genui-form-page title="步骤 2: 风格选择">
    <genui-radio-group name="genre">
      <genui-radio value="pop">流行 Pop</genui-radio>
      <genui-radio value="jazz">爵士 Jazz</genui-radio>
      <genui-radio value="electronic">电子 Electronic</genui-radio>
      <genui-radio value="classical">古典 Classical</genui-radio>
      <genui-radio value="rock">摇滚 Rock</genui-radio>
      <genui-radio value="hiphop">嘻哈 Hip-Hop</genui-radio>
      <genui-radio value="country">乡村 Country</genui-radio>
      <genui-radio value="blues">蓝调 Blues</genui-radio>
    </genui-radio-group>
    <genui-input selection-mode="radio" name="mood" placeholder="指定歌曲心情/场景（如：欢快、抒情、动感）"></genui-input>
  </genui-form-page>
</genui-form-wizard>
```

### 步骤 2：构建提示词

根据用户选择生成音乐提示词：

| 风格 | 提示词示例 |
|------|-----------|
| 流行 Pop | Pop music, upbeat, catchy melody, suitable for celebration |
| 爵士 Jazz | Jazz music, smooth, soulful, relaxing atmosphere |
| 电子 Electronic | Electronic music, energetic beats, modern synth |
| 古典 Classical | Classical music, elegant, orchestral arrangement |
| 摇滚 Rock | Rock music, powerful, energetic guitar riffs |
| 嘻哈 Hip-Hop | Hip-hop, rhythmic beats, urban vibe |
| 乡村 Country | Country music, acoustic, heartfelt storytelling |
| 蓝调 Blues | Blues music, emotional, soulful guitar |

### 步骤 3：调用工具生成音乐

使用 `batch_text_to_music` 工具：

```python
batch_text_to_music(
    count=1,
    display_text="正在生成音乐...",
    prompt_list=["根据风格生成的提示词"],
    lyrics_list=[用户提供的歌词],
    output_file_list=["music_output/song_YYYYMMDD_HHMMSS.mp3"],
    sample_rate_list=[32000],
    bitrate_list=[128000],
    format_list=["mp3"]
)
```

### 步骤 4：返回结果

生成完成后，向用户展示：
1. 音乐文件路径
2. 使用 `audios_understand` 工具分析音乐内容（如需要）
3. 提供下载链接

## 输出格式

生成的音乐文件保存到 `music_output/` 目录，格式为 MP3。

## 示例对话

**用户**: 帮我创作一首关于夏天的流行歌曲

**助手**: 请提供歌词内容和更多细节...

**用户**: 好的，歌词如下：[Verse] 阳光洒在海面上，微风轻轻吹拂... [Chorus] 这就是夏天，快乐的夏天...

**助手**: 使用 `batch_text_to_music` 生成音乐后返回文件路径

## 错误处理

- 歌词过长（>600字符）：提示用户精简或分段生成
- 歌词格式不规范：自动添加基本结构标签
- 生成失败：提供重试选项或建议调整风格

## 技术限制

- 单次生成最长 1 分钟
- 支持格式：MP3、WAV、PCM
- 推荐采样率：32000Hz
- 推荐比特率：128000
