# OpenAI Whisper 本地语音转文字技能

适配 Minimax Agent 的离线语音处理技能，基于 OpenAI Whisper CLI 封装，无任何第三方平台依赖，无需 API 密钥，全程本地处理。

## 功能特性
- ✅ 本地离线语音转录，支持99种语言
- ✅ 语音翻译（任意语言转英文）
- ✅ 支持 mp3、m4a、wav、flac 等主流音频格式
- ✅ 支持 txt、srt、vtt、json 等多种输出格式
- ✅ 多档位模型可选，平衡速度与准确率
- ✅ 无网络依赖（首次模型下载除外），数据全程本地留存

## 开源协议
MIT-0 协议，可免费使用、修改、重新分发，无需署名。

## 前置环境要求
1. Python 3.8+ 环境
2. 已安装 OpenAI Whisper CLI，安装命令：
   ```bash
   # MacOS（Homebrew，推荐）
   brew install openai-whisper

   # 其他系统通用安装方式
   pip install openai-whisper
   ```
3. 已安装 ffmpeg（Whisper 依赖），未安装可执行：
   ```bash
   # MacOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # Windows
   choco install ffmpeg
   ```

## 安装与导入
1. 将本目录导入到 Minimax Agent 技能管理中
2. 启用技能后即可使用

## 使用示例
### 基础语音转录
```
帮我转录这个音频：/Users/xxx/Documents/meeting.mp3
```

### 语音翻译
```
把这个日语音频翻译成英文：/Users/xxx/Documents/japanese_audio.m4a
```

### 自定义参数调用
```
用 medium 模型转录这个音频，输出 srt 字幕文件：
{
  "audio_path": "/Users/xxx/Documents/interview.wav",
  "model": "medium",
  "output_format": "srt",
  "output_dir": "/Users/xxx/Documents/transcript_result"
}
```

## 权限说明
- `read:file`：仅读取用户指定的音频文件
- `write:file`：仅向指定目录写入转录结果文件
- `network:false`：技能本身不访问任何外部网络

## 注意事项
1. 首次运行时，Whisper 会自动下载对应模型到 `~/.cache/whisper` 目录
2. 模型越大，准确率越高，但运行速度越慢
3. 敏感音频请在可信的本地环境中运行

## 常见问题排查
1. **提示 `whisper: command not found`**
   - 确认已安装 Whisper CLI，执行 `whisper --version` 能正常输出版本号
2. **执行卡住**
   - 大概率是首次运行正在下载模型
3. **音频处理失败，提示 ffmpeg 相关错误**
   - 确认已安装 ffmpeg，执行 `ffmpeg -version` 能正常输出
