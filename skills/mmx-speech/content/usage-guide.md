---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8162f240008cb0189d5e771037684133
    PropagateID: 8162f240008cb0189d5e771037684133
    ReservedCode1: 304402202cac52acb7ff8b886e407758bf5f61d9bc38688f0427882ea63966588c7856dd022055dd1ba45a2beb6833ba2ece51078eb0888b92a6fb657227e83e131f7467b577
    ReservedCode2: 3045022100a074f44aa79928989478d1e2f0fd0c20f03c3bf478072b05f4e666265c2c24e70220287cf4c63e909b1203126e8f196cfc5062c79f5f20b8b5780fd8ba7943b94f6d
---

# 🌐 MiniMax CLI 语音合成 · 完整指南

> **适用版本：** mmx-cli（v1.x）+ MiniMax API Key
> **更新日期：** 2026-04-17
> **特点：** 用自己的 API Key，不消耗平台积分，支持多音色调节

---

## 🎯 为什么选择 mmx CLI 而不是 MCP？

| 维度 | MCP（平台积分） | mmx CLI（自持 Key）✅ |
|------|---------------|----------------------|
| 费用归属 | 消耗平台积分 | 用自己的 MiniMax 账号 |
| 额度控制 | 平台统一配额 | 自己充值，透明可控 |
| 音色选择 | 固定音色 | 多音色可选 |
| 响应速度 | 经 MCP Server 转发 | 直连 API，本地 CLI |
| 适用场景 | 通用生成 | **语音/TTS 首选** |

**结论：** 语音合成用 mmx CLI，音乐/图片/视频继续用 MCP（平台提供）。

---

## 🚀 第一步：安装 mmx CLI

### 1.1 全局安装

```bash
npm install -g mmx-cli
```

### 1.2 登录 API Key

```bash
mmx auth login --api-key sk-xxxxx
```

> API Key 从 MiniMax 控制台获取：https://platform.minimaxi.com

### 1.3 验证安装

```bash
mmx
```

终端显示如下信息表示成功：
```
 MiniMax CLI 🌀

 resources   → 可用能力
 flags       → 支持的参数选项
 用量信息     → 剩余额度与配额
 帮助入口    → 使用方法
```

---

## 🔊 语音合成：核心命令

### 基础用法

```bash
mmx speech synthesize --text "要朗读的文本" --out 输出.mp3
```

### 参数详解

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--text` | ✅ | 要朗读的文本 | `--text "你好世界"` |
| `--out` | ✅ | 输出文件路径 | `--out voice.mp3` |
| `--voice` | ❌ | 音色选择 | `--voice female-qn-qingse` |
| `--speed` | ❌ | 语速 [0.5~2.0] | `--speed 1.0`（默认1.0） |
| `--volume` | ❌ | 音量 [0~10] | `--volume 1.0`（默认1.0） |
| `--pitch` | ❌ | 音调 [-12~12] | `--pitch 0`（默认0） |

---

## 🎨 音色速查表

| 音色 ID | 风格描述 | 最佳场景 |
|---------|---------|---------|
| `female-qn-qingse` | 🌸 温柔女声，青叔音色 | 轻声朗读、情感表达、睡前故事 |
| `female-shaosheng` | 🌟 活泼女声，少胜音色 | 活泼讲解、广告配音、儿童内容 |
| `female-yunyang` | 🎙️ 知性女声，云扬音色 | 新闻播报、有声书、正式场合 |
| `male-qn-qingse` | 🎻 沉稳男声，青叔音色 | 叙述旁白、纪录片、沉稳解说 |
| `male-baiyang` | 🎭 磁性男声，白云音色 | 深夜电台、情感朗读、高品质旁白 |
| `male-honroso` | ☀️ 阳光男声，哈妮音色 | 活力讲解、体育解说、青春内容 |

> 查看完整音色列表：`mmx speech voices`

---

## 💡 场景化示例

### 场景 1：温柔女声·品牌介绍

```bash
mmx speech synthesize \
  --text "欢迎使用 MiniMax Token Plan，让你的 AI Agent 拥有全模态能力，一句话生成视频、音乐、图片和语音。" \
  --voice female-qn-qingse \
  --speed 1.0 \
  --out /workspace/voice/brand_intro.mp3
```

### 场景 2：磁性男声·深夜播客

```bash
mmx speech synthesize \
  --text "在这个寂静的夜晚，让我们暂时放下所有的忙碌，一起来聆听星空中最温柔的声音。" \
  --voice male-baiyang \
  --speed 0.85 \
  --pitch -2 \
  --out /workspace/voice/night_podcast.mp3
```

### 场景 3：活泼女声·产品解说

```bash
mmx speech synthesize \
  --text "今天给大家带来一款超级好用的 AI 工具，五分钟就能生成一段专业级配音！" \
  --voice female-shaosheng \
  --speed 1.3 \
  --out /workspace/voice/product_demo.mp3
```

### 场景 4：知性女声·新闻播报

```bash
mmx speech synthesize \
  --text "今天的主要内容有：AI 技术新突破、语音合成能力升级、以及多模态应用的未来趋势。" \
  --voice female-yunyang \
  --speed 1.1 \
  --out /workspace/voice/news_briefing.mp3
```

---

## ⚙️ 高级调参技巧

### 语速调节

| 值 | 效果 | 适用 |
|----|------|------|
| `0.5` | 极慢（抒情、冥想） | 放松内容 |
| `0.8` | 稍慢（深夜朗读） | 情感内容 |
| `1.0` | 正常（默认） | 一般场景 |
| `1.2` | 稍快（新闻播报） | 信息密度高 |
| `1.5` | 快速（广告配音） | 高效传达 |

### 音调调节

| 值 | 效果 |
|----|------|
| `-6 ~ -1` | 降低音调（更深沉、磁性） |
| `0` | 默认音调 |
| `+1 ~ +6` | 提升音调（更清亮、活泼） |

**组合示例：磁性低沉男声**
```bash
mmx speech synthesize \
  --text "深夜的咖啡馆，灯火温暖。" \
  --voice male-baiyang \
  --speed 0.75 \
  --pitch -4 \
  --out night_cafe.mp3
```

---

## 🔄 批量合成：Shell 脚本

适合配音工作流，一次生成多个音频文件：

```bash
#!/bin/bash
# batch_voice.sh — 批量语音合成

OUTPUT_DIR="/workspace/voice_batch"
mkdir -p "$OUTPUT_DIR"

# 定义音色配置
VOICE="female-yunyang"
SPEED="1.0"

# 定义要合成的文本（一行一段）
declare -a TEXTS=(
  "清晨的第一缕阳光，洒在平静的海面上。"
  "微风穿过森林，带来泥土和树叶的芬芳气息。"
  "夜空中最亮的星，指引着每一个追梦人的方向。"
)

for i in "${!TEXTS[@]}"; do
  index=$((i+1))
  padded=$(printf '%02d' $index)
  echo "[$index/${#TEXTS[@]}] 正在合成..."
  
  mmx speech synthesize \
    --text "${TEXTS[$i]}" \
    --voice "$VOICE" \
    --speed "$SPEED" \
    --out "$OUTPUT_DIR/scene_$padded.mp3"
  
  echo "  ✅ 完成 → scene_$padded.mp3"
  sleep 3  # 避免请求过快
done

echo ""
echo "🎉 全部完成！共 ${#TEXTS[@]} 个文件"
ls -lh "$OUTPUT_DIR"
```

---

## 📊 额度计算参考

| 内容类型 | 字符数 | 约消耗 Tokens | 成本参考 |
|---------|--------|--------------|---------|
| 短句 | ~50 字 | ~70 Tokens | 极低 |
| 段落 | ~200 字 | ~280 Tokens | 低 |
| 长文 | ~1000 字 | ~1400 Tokens | 中等 |
| 有声书章节 | ~3000 字 | ~4200 Tokens | 中等偏高 |

> 实际成本请以 MiniMax 控制台为准，充值后使用更划算。

---

## 🆚 与 vocal-extractor 配合

mmx CLI 生成人声后，可配合 vocal-extractor 制作混音：

```
mmx speech synthesize（生成干声）
       ↓
vocal-extractor（提取人声轨）
       ↓
batch_text_to_music（生成背景伴奏）
       ↓
混音合并
       ↓
最终作品
```

---

## ❓ 常见问题

**Q：提示 "not found mmx"？**
```bash
# 重新安装
npm install -g mmx-cli

# 确认路径
which mmx
npm list -g mmx-cli
```

**Q：API Key 过期或无效？**
```bash
# 重新登录
mmx auth login --api-key sk-你的新key

# 查看当前登录状态
mmx auth status
```

**Q：合成失败/网络错误？**
```bash
# 检查网络
curl https://api.minimax.io

# 重试（稍等几秒）
sleep 5 && mmx speech synthesize --text "测试" --out test.mp3
```

**Q：输出文件默认存在哪？**
```bash
# 默认：当前目录/minimax-output/
ls minimax-output/

# 指定路径
mmx speech synthesize --text "..." --out /workspace/voice/demo.mp3
```

---

## 📦 相关工具链

| 工具 | 用途 | 用量 |
|------|------|------|
| `mmx speech synthesize` | 语音合成 | ✅ mmx CLI（自持 Key） |
| `batch_text_to_music` | 背景音乐生成 | ⚠️ MCP（平台积分） |
| `vocal-extractor` | 人声分离 | ✅ mmx CLI（自持 Key） |
| `audios_understand` | 音频转文字 | ⚠️ MCP（平台积分） |

> 建议：生成类（音乐/视频/图片）用 MCP 平台积分，语音/TTS 用 mmx CLI 自持 Key，分开使用更划算。
