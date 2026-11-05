---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b57c00988cbc2985b072ccc8132a6fa9
    PropagateID: b57c00988cbc2985b072ccc8132a6fa9
    ReservedCode1: 3045022100e01ab4a82734b086e2848dd39bddbf2f7f5a9684d9fcd21a7ff32f40a658110202200dd6b5fa65f40103b2623d30dbf6f9bad00789abd9a5e5077bf2561b082c1d8f
    ReservedCode2: 3044022023ea28d7fd99b5e4d6351ca27dfbcbbc84707448963a2637d692c3b173b440ca02201154bb08ae8a88568d95e489d71832c137d7cb0e72e94661d4c2a6e6bd4a3e27
---

# 飞书语音 - 音色与参数参考

## MiniMax TTS API

- **端点**: `https://api.minimaxi.com/v1/t2a_v2`
- **模型**: `speech-2.8-hd`
- **额度**: 每天 4000 字，每天 00:00（北京时间）重置
- **格式**: WAV（32kHz，16bit，单声道）

## 可用音色（voice_id）

| voice_id | 音色描述 | 适用场景 |
|----------|---------|---------|
| `female-yujie` | 御姐音 | 默认，已验证✅ |
| `female-tianmei` | 甜美女声 | 温和场景 |
| `male-qn-qingse` | 男声青秋 | 正式/男性角色 |

## 语速（speed）

| 值 | 描述 |
|----|------|
| 1.0 | 正常语速 |
| 1.2 | 略快（默认） |
| 1.4 | 较快（测试过） |

## FFmpeg 参数

```
-acodec libopus   # Opus 编码器（Feishu 原生支持）
-ac 1             # 单声道
-ar 16000         # 16kHz（Feishu 推荐）
-b:a 32k          # 32kbps 码率
-f ogg            # OGG 容器格式
```

## 飞书语音消息限制

- 支持格式：OGG-Opus（唯一可用）
- 不支持：MP3、WAV、AAC（会变成附件而非语音气泡）
- 文件扩展名必须是 `.ogg`
