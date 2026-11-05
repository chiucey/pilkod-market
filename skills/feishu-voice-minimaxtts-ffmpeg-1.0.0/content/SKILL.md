---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 226249bd30cea7ebc431346705f0e69e
    PropagateID: 226249bd30cea7ebc431346705f0e69e
    ReservedCode1: 3045022031d9b215c2f2b421789b58b7080c7f51acd11629f343cc24728933ececec7813022100e99656df8dfcda9b9e1e900ccb024fc7a81ee92e80eee199953d74b1e87cbf46
    ReservedCode2: 3046022100da966964d903979600c47f5cd825a7e6c2f3f6ab439e3fa9073d7a79f6f0bf9d0221008bc42643542497bd64ec95890bd6f98ba79f11b0c80d71a904fce6b59200c772
description: 飞书语音消息发送。当需要用语音回复用户时触发，包括：用户说"发一条语音"、"用语音回复"、或任何要求语音回复的场景。执行 TTS → FFmpeg 转 OGG-Opus → 上传 → 发送的完整流程。
name: feishu-voice-minimaxtts-ffmpeg-1.0.0
---

# feishu-voice-minimaxtts-ffmpeg-1.0.0

用飞书语音气泡回复用户。

## 工作流程

1. **生成 TTS WAV**：`scripts/gen_voice.py <文字内容> [输出路径]`
2. **上传 CDN**：`upload_to_cdn` 工具上传生成的 OGG 文件
3. **发送语音**：`message action=send media=<CDN_URL> asVoice=true`

## 关键参数（默认）

- 音色：`female-yujie`（御姐音）
- 语速：`1.2`
- 音频：`单声道、16kHz、32kbps、OGG-Opus`
- FFmpeg 路径：`/workspace/installed_software/ffmpeg-pkg2/node_modules/@ffmpeg-installer/linux-x64/ffmpeg`

## 额度注意事项

- **每天 4000 字**，00:00 北京时间重置
- 调用前需评估字数：
  - 短内容（<100字）：可直接调用
  - 长内容：先告知用户预计消耗，确认后再调用
- 不要在回复中加"白泽说"等前缀，直接是内容

## 文件结构

```
feishu-voice/
├── SKILL.md                    ← 本文件
├── scripts/
│   └── gen_voice.py           ← 主脚本（TTS→OGG）
└── references/
    └── voice-options.md        ← 音色/参数参考
```

## 快速参考

```bash
# Step 1: 生成语音（OGG）
python3 /workspace/skills/feishu-voice/scripts/gen_voice.py "你好，这是测试。" /tmp/test.ogg

# Step 2: 上传 CDN（用 upload_to_cdn 工具）

# Step 3: 发飞书语音气泡（用 message 工具）
message action=send media=<CDN_URL> asVoice=true
```

详细音色和参数见 `references/voice-options.md`。
