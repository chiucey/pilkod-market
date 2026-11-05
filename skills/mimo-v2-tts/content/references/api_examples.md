# MiMo V2 TTS API 调用示例

## cURL 示例

```bash
curl --location --request POST 'https://api.xiaomimimo.com/v1/chat/completions' \
--header "api-key: $MIMO_API_KEY" \
--header 'Content-Type: application/json' \
--data-raw '{
"model": "mimo-v2-tts",
"messages": [
{
n"role": "user",
"content": "Hello, MiMo, have you had lunch?"
},
{
"role": "assistant",
"content": "Yes, I had a sandwich."
}
],
"audio": {
"format": "wav",
"voice": "mimo_default"
}
}'
```

## Python SDK 示例

```python
import os
from openai import OpenAI
import base64

client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://api.xiaomimimo.com/v1"
)

completion = client.chat.completions.create(
    model="mimo-v2-tts",
    messages=[
        {
            "role": "user",
            "content": "Hello, MiMo, have you had lunch?"
        },
        {
            "role": "assistant",
            "content": "Yes, I had a sandwich."
        }
    ],
    audio={
        "format": "wav",
        "voice": "mimo_default"
    }
)

# 解码并保存音频
message = completion.choices[0].message
audio_bytes = base64.b64decode(message.audio.data)
with open("audio_file.wav", "wb") as f:
    f.write(audio_bytes)
```

## 中文示例

```python
completion = client.chat.completions.create(
    model="mimo-v2-tts",
    messages=[
        {
            "role": "assistant",
            "content": "你好，欢迎使用小米语音合成服务"
        }
    ],
    audio={
        "format": "wav",
        "voice": "default_zh"
    }
)
```

## 带风格的示例

```python
# 开心风格
completion = client.chat.completions.create(
    model="mimo-v2-tts",
    messages=[
        {
            "role": "assistant",
            "content": "<|style:_Happy|>今天天气真不错！"
        }
    ],
    audio={"format": "wav", "voice": "default_zh"}
)

# 唱歌风格
completion = client.chat.completions.create(
    model="mimo-v2-tts",
    messages=[
        {
            "role": "assistant",
            "content": "<|sing|>门前大桥下，游过一群鸭"
        }
    ],
    audio={"format": "wav", "voice": "default_zh"}
)
```

## Node.js 示例

```javascript
const fetch = require('node-fetch');
const fs = require('fs');

async function synthesize(text, voice = 'mimo_default', format = 'wav') {
    const response = await fetch('https://api.xiaomimimo.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'api-key': process.env.MIMO_API_KEY
        },
        body: JSON.stringify({
            model: 'mimo-v2-tts',
            messages: [
                { role: 'assistant', content: text }
            ],
            audio: { format, voice }
        })
    });

    const data = await response.json();
    const audioBuffer = Buffer.from(data.choices[0].message.audio.data, 'base64');
    fs.writeFileSync('output.wav', audioBuffer);
    return audioBuffer;
}

synthesize('你好，欢迎使用小米语音合成');
```
