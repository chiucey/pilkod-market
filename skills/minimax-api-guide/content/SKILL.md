---
name: minimax-api-guide
description: MiniMax开放平台API使用指南。当用户需要了解MiniMax API接口、调用方式、支持的模型，或需要在MaxClaw/OpenClaw中配置MiniMax API时使用。关键词：MiniMax、API、API Key、文本模型、语音合成、视频生成、图像生成、音乐生成。
---

# MiniMax 开放平台 API 使用指南

全面介绍 MiniMax 开放平台的 API 接口、模型能力和调用方式。

## API Key 获取

| 获取方式 | 路径 | 支持功能 |
|----------|------|----------|
| 按量付费 | 接口密钥 > 创建新的 API Key | 所有模态模型（文本、视频、语音、图像等） |
| Token Plan | 接口密钥 > 创建 Token Plan Key | MiniMax 全模态模型 |

**管理地址**：[https://platform.minimaxi.com/user-center/basic-information/interface-key](https://platform.minimaxi.com/user-center/basic-information/interface-key)

## 环境配置

```bash
# Anthropic SDK 兼容配置（推荐）
export ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
export ANTHROPIC_API_KEY=${YOUR_API_KEY}

# 或使用 OpenAI SDK
export OPENAI_API_KEY=${YOUR_API_KEY}
export OPENAI_BASE_URL=https://api.minimaxi.com/v1
```

## 支持的模型一览

### 文本模型 (Text Generation)

| 模型名称 | 上下文窗口 | 特性 | 输出速度 |
|----------|------------|------|----------|
| MiniMax-M2.7 | 200K | 开启模型的自我迭代 | ~60 tps |
| MiniMax-M2.7-highspeed | 200K | M2.7极速版，效果不变，更快更敏捷 | ~100 tps |
| MiniMax-M2.5 | 200K | 顶尖性能与极致性价比 | ~60 tps |
| MiniMax-M2.5-highspeed | 200K | M2.5极速版，效果不变，更快更敏捷 | ~100 tps |
| MiniMax-M2.1 | 200K | 强大多语言编程能力 | ~60 tps |
| MiniMax-M2.1-highspeed | 200K | M2.1极速版，效果不变，更快更敏捷 | ~100 tps |
| MiniMax-M2 | 200K | 专为高效编码与Agent工作流而生 | - |

### 语音模型 (Speech)

| 模型 | 特性 |
|------|------|
| speech-2.8-hd | 最新的HD模型，精准还原真实语气细节，全面提升音色相似度 |
| speech-2.8-turbo | 最新的Turbo模型，精准还原真实语气细节，全面提升音色相似度 |
| speech-2.6-hd | HD模型，韵律表现出色，极致音质与韵律表现，生成更快更自然 |
| speech-2.6-turbo | Turbo模型，音质优异，超低时延，响应更灵敏 |
| speech-02-hd | 拥有出色的韵律、稳定性和复刻相似度，音质表现突出 |
| speech-02-turbo | 拥有出色的韵律和稳定性，小语种能力加强，性能表现出色 |

### 视频模型 (Video)

| 模型 | 功能 |
|------|------|
| MiniMax-Hailuo-2.3 | 全新视频生成模型，肢体动作、物理表现与指令遵循能力全面升级 |
| MiniMax-Hailuo-2.3-Fast | 图生视频模型，生成速度大幅提升，以更高性价比兼顾画质与表现力 |
| MiniMax-Hailuo-02 | 新一代视频生成模型，支持更高分辨率(1080P)和更长时长(10s)，指令遵循能力更强 |

### 图像模型 (Image)

| 模型名称 | 简介 |
|----------|------|
| image-01 | 图像生成模型，画面表现细腻，支持文生图、图生图（人物主体参考） |
| image-01-live | 图像生成模型，在image-01基础上额外支持多种画风设置 |

### 音乐模型 (Music)

| 模型名称 | 使用方法 |
|----------|----------|
| music-2.0 | 最新音乐生成模型，支持用户输入音乐灵感和歌词，生成AI音乐 |

## 接口调用示例

### 文本生成 (Anthropic SDK)

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="MiniMax-M2.7",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hello, how are you?"
                }
            ]
        }
    ]
)

for block in message.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Text: {block.text}")
```

### 文本生成 (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="${YOUR_API_KEY}",
    base_url="https://api.minimaxi.com/v1"
)

response = client.chat.completions.create(
    model="MiniMax-M2.7",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    max_tokens=1024
)

print(response.choices[0].message.content)
```

### 同步语音合成 (T2A)

```python
import requests

url = "https://api.minimaxi.com/v1/t2a_v2"

payload = {
    "model": "speech-02-hd",
    "text": "你好，欢迎使用MiniMax语音服务",
    "voice_setting": {
        "voice_id": "female-shaonv",
        "speed": 1.0,
        "vol": 1.0
    }
}

headers = {
    "Authorization": f"Bearer ${YOUR_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

# 保存音频文件
with open("output.mp3", "wb") as f:
    f.write(response.content)
```

### 语音克隆 (Voice Cloning)

```python
import requests

# 1. 上传复刻音频
upload_url = "https://api.minimaxi.com/v1/files/upload"

files = {'file': open('your_audio.wav', 'rb')}
headers = {"Authorization": f"Bearer ${YOUR_API_KEY}"}

upload_response = requests.post(upload_url, files=files, headers=headers)
file_id = upload_response.json()['file_id']

# 2. 执行音色克隆
clone_url = "https://api.minimaxi.com/v1/voice_clone"
payload = {
    "model": "speech-02-hd",
    "audio_file_id": file_id
}

clone_response = requests.post(clone_url, json=payload, headers=headers)
voice_id = clone_response.json()['voice_id']
```

### 视频生成 (异步)

```python
import requests
import time

# 1. 创建视频生成任务
create_url = "https://api.minimaxi.com/v1/video/generate"

payload = {
    "model": "MiniMax-Hailuo-2.3",
    "prompt": "一只橘猫在阳光下的窗台上打哈欠"
}

headers = {
    "Authorization": f"Bearer ${YOUR_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(create_url, json=payload, headers=headers)
task_id = response.json()['task_id']

# 2. 查询任务状态
status_url = f"https://api.minimaxi.com/v1/video/generate/status?task_id={task_id}"

while True:
    status_response = requests.get(status_url, headers=headers)
    status = status_response.json()

    if status['status'] == 'success':
        file_id = status['file_id']
        break
    elif status['status'] == 'failed':
        print("视频生成失败")
        break

    time.sleep(3)

# 3. 下载视频
download_url = f"https://api.minimaxi.com/v1/files/{file_id}/download"
video_response = requests.get(download_url, headers=headers)

with open("output_video.mp4", "wb") as f:
    f.write(video_response.content)
```

### 图像生成

```python
import requests

url = "https://api.minimaxi.com/v1/image/generate"

payload = {
    "model": "image-01",
    "prompt": "一只可爱的橘猫在草地上玩耍",
    "aspect_ratio": "1:1"
}

headers = {
    "Authorization": f"Bearer ${YOUR_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

# 获取生成的图片 URL
image_url = result['data'][0]['url']
```

### 音乐生成

```python
import requests

url = "https://api.minimaxi.com/v1/music/generate"

payload = {
    "model": "music-2.0",
    "prompt": "一首轻快活泼的中文流行歌曲，适合运动时听",
    "lyrics": "[Verse]\n阳光照耀每一天\n我们一起向前\n\n[Chorus]\n奔跑在梦想的路上"
}

headers = {
    "Authorization": f"Bearer ${YOUR_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()

audio_url = result['data']['audio_url']
```

## 接口类型汇总

### HTTP 接口

| 接口类型 | 说明 |
|----------|------|
| 同步语音合成 (T2A) | 单次处理上限 10,000 字符，支持流式输出 |
| 异步长文本语音合成 (T2A Async) | 单次文本上限 1,000,000 字符 |
| 文生视频 | 基于文本描述生成视频 |
| 图生视频 | 基于参考图片生成视频 |
| 文生图 | 基于文本描述生成图像 |
| 图生图 | 基于参考图片生成图像 |
| 音乐生成 | 根据描述和歌词生成音乐 |

### WebSocket 接口

| 接口类型 | 说明 |
|----------|------|
| 流式语音合成 | 实时流式输出音频 |
| 流式对话 | 实时流式输出文本 |

## 文件管理 API

| 接口 | 说明 |
|------|------|
| 上传文件 | 支持 pdf、docx、txt、jsonl、mp3、m4a、wav |
| 列出文件 | 列出已上传的文件 |
| 检索文件 | 获取文件信息 |
| 下载文件 | 下载指定文件 |
| 删除文件 | 删除指定文件 |

**容量限制**：
- 总容量：100GB
- 单个文档：512MB

## MCP 集成

MiniMax 提供官方 MCP 服务器实现：

- **Python 版本**：[https://github.com/MiniMax-AI/MiniMax-MCP](https://github.com/MiniMax-AI/MiniMax-MCP)
- **JavaScript 版本**：[https://github.com/MiniMax-AI/MiniMax-MCP-JS](https://github.com/MiniMax-AI/MiniMax-MCP-JS)

### 安装配置

```bash
# Python 版本
pip install minimax-mcp
```

### MCP 配置示例

```json
{
  "mcpServers": {
    "minimax": {
      "command": "npx",
      "args": ["@minimax-ai/minimax-mcp-js"]
    }
  }
}
```

### MCP 支持功能

- 语音合成
- 音色克隆
- 视频生成
- 音乐生成
- 图像理解
- 网页搜索

## 视频生成 Agent 模板

| 模板ID | 模板名称 | 说明 |
|--------|----------|------|
| 392753057216684038 | 跳水 | 生成图中主体完成完美跳水动作的视频 |
| 393881433990066176 | 吊环 | 生成图中主体完成完美吊环动作的视频 |
| 393769180141805569 | 绝地求生 | 生成宠物野外绝地求生视频 |
| 394246956137422856 | 万物皆可labubu | 生成labubu换脸视频 |
| 393857704283172864 | 情书写真 | 生成冬日雪景写真 |
| 393866076583718914 | 女模特试穿广告 | 生成女模特试穿广告 |
| 393876118804459526 | 男模特试穿广告 | 生成男模特试穿广告 |

## 语音合成支持语言（40种）

中文（普通话/粤语）、英语、西班牙语、法语、俄语、德语、葡萄牙语、阿拉伯语、意大利语、日语、韩语、印尼语、越南语、土耳其语、荷兰语、乌克兰语、泰语、波兰语、罗马尼亚语、希腊语、捷克语、芬兰语、印地语、保加利亚语、丹麦语、希伯来语、马来语、波斯语、斯洛伐克语、瑞典语、克罗地亚语、菲律宾语、匈牙利语、挪威语、斯洛文尼亚语、加泰罗尼亚语、尼诺斯克语、泰米尔语、阿非利卡语

## 相关链接

| 资源 | 地址 |
|------|------|
| API Key 获取 | [https://platform.minimaxi.com/user-center/basic-information/interface-key](https://platform.minimaxi.com/user-center/basic-information/interface-key) |
| Token Plan | [https://platform.minimaxi.com/docs/token-plan/intro](https://platform.minimaxi.com/docs/token-plan/intro) |
| API 文档 | [https://platform.minimaxi.com/docs/api-reference/api-overview](https://platform.minimaxi.com/docs/api-reference/api-overview) |
| 产品定价 | [https://platform.minimaxi.com/docs/pricing/overview](https://platform.minimaxi.com/docs/pricing/overview) |
| 技术支持邮箱 | Model@minimaxi.com |
| GitHub | [https://github.com/MiniMax-AI/MiniMax-M2/issues](https://github.com/MiniMax-AI/MiniMax-M2/issues) |
