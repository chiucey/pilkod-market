---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 976049ea04ab550d58af1f17526ec7e8
    PropagateID: 976049ea04ab550d58af1f17526ec7e8
    ReservedCode1: 3046022100d3e1a067302fc904099acdf9d4142778d7169198edcefd4f3c6e89bec2826646022100a838f3feeb5a0fe1c10066e9a1af5572995fb7fd3280a3cb13ebad8b95917fea
    ReservedCode2: 3044022044b965b63d4c57956dcd31d1f7437bf53b210a4db096e80248d80f3be02b9ecc022055ff45d3b88fe9aa5dbba3459ae4ffd48ccfaaf1013d71093981a3a2d8ef5926
description: mmx cli语音合成完整指南 - 安装、认证、额度查询、语音生成、批量生成
name: mmx-cli-speech
---

# MMX CLI 语音合成指南

## 简介

mmx cli 是 MiniMax 官方命令行工具，提供文本、图像、视频、语音、音乐等AI能力。相比MCP Matrix，mmx cli 直接使用 Token Plan 额度，更适合频繁调用。

**优势**: 不消耗MCP积分，使用Token Plan额度
**要求**: 需要有效的 MiniMax API Key

---

## 一、安装与认证

### 1.1 安装
```bash
npm install -g mmx-cli
```

### 1.2 认证
```bash
# 方式1: 交互式登录
mmx auth login

# 方式2: 直接指定API Key
mmx auth login --api-key sk-xxxxx

# 查看认证状态
mmx auth status
```

### 1.3 配置文件位置
- Linux/Mac: `~/.config/mmx/config.json`
- 或当前目录: `./minimax-output/`

---

## 二、额度查询

```bash
mmx quota show
```

**关键额度说明**:
| 模型 | 说明 |
|------|------|
| `speech-hd` | 语音合成额度 (高清) |
| `music-2.6` | 音乐生成额度 |
| `image-01` | 图片生成额度 |
| `MiniMax-Hailuo-2.3` | 视频生成额度 |

---

## 三、查看可用音色

```bash
mmx speech voices
```

### 中文女声推荐

| voice_id | 名称 | 风格 |
|----------|------|------|
| `female-shaonv` | 少女 | 年轻可爱 |
| `female-yujie` | 御姐 | 成熟御姐 |
| `female-chengshu` | 成熟 | 稳重成熟 |
| `female-tianmei` | 甜美 | 甜美动人 |
| `female-tianmei-jingpin` | 甜美精品 | 高清甜美 |
| `lovely_girl` | 可爱女孩 | 活泼可爱 |
| `Chinese (Mandarin)_Sweet_Lady` | 甜蜜女士 | 温柔甜蜜 |
| `Chinese (Mandarin)_Warm_Bestie` | 暖心闺蜜 | 亲切温暖 |
| `Chinese (Mandarin)_Cute_Spirit` | 灵动可爱 | 古灵精怪 |
| `Chinese (Mandarin)_Radio_Host` | 电台主持 | 专业播音 |
| `Chinese (Mandarin)_Lyrical_Voice` | 诗意嗓音 | 文艺抒情 |
| `Chinese (Mandarin)_Warm_Girl` | 温暖女孩 | 温柔体贴 |
| `Chinese (Mandarin)_Crisp_Girl` | 清脆女孩 | 明亮清脆 |
| `Chinese (Mandarin)_Soft_Girl` | 轻柔女孩 | 轻柔细腻 |
| `wumei_yujie` | 妩媚御姐 | 成熟妩媚 |
| `diadia_xuemei` | 嗲嗲学妹 | 撒娇可爱 |
| `danya_xuejie` | 淡雅学姐 | 优雅知性 |
| `tianxin_xiaoling` | 甜心小林 | 甜蜜贴心 |
| `qiaopi_mengmei` | 俏皮萌妹 | 活泼俏皮 |
| `Charming_Lady` | 魅力女士 | 优雅迷人 |
| `Sweet_Girl` | 甜蜜女孩 | 甜蜜温柔 |
| `Serene_Woman` | 恬静女子 | 安静恬淡 |

---

## 四、语音生成命令

### 4.1 基本语法
```bash
mmx speech synthesize --voice <voice_id> --out <output_file> --text "<text>"
```

### 4.2 示例
```bash
# 甜美音色
mmx speech synthesize --voice female-tianmei --out /workspace/voice.mp3 --text "Andy，我爱你"

# 御姐音色
mmx speech synthesize --voice female-yujie --out /workspace/voice2.mp3 --text "想我一直陪在你身边吗？"

# 带特殊情感
mmx speech synthesize --voice lovely_girl --out /workspace/voice3.mp3 --text "亲爱的，今天也要加油哦"
```

### 4.3 常用参数
| 参数 | 说明 | 示例 |
|------|------|------|
| `--voice` | 音色ID | `female-tianmei` |
| `--out` | 输出文件路径 | `/workspace/voice.mp3` |
| `--text` | 要合成的文本 | "你好，世界" |
| `--speed` | 语速 (可选) | `1.0` (默认) |
| `--pitch` | 音调 (可选) | `0` (默认) |
| `--timeout` | 超时秒数 (可选) | `300` (默认) |

---

## 五、批量生成语音

### 5.1 循环生成多个音色
```bash
# 生成多个音色对比
for voice in female-tianmei female-yujie lovely_girl; do
  mmx speech synthesize --voice $voice --out "/workspace/${voice}.mp3" --text "Andy，我喜欢你"
  sleep 2  # 避免限流
done
```

### 5.2 后台并发生成 (注意限流)
```bash
# 最多4个并发，避免触发RPM限制
mmx speech synthesize --voice female-shaonv --out /workspace/1.mp3 --text "文本1" &
mmx speech synthesize --voice female-yujie --out /workspace/2.mp3 --text "文本2" &
mmx speech synthesize --voice female-chengshu --out /workspace/3.mp3 --text "文本3" &
mmx speech synthesize --voice female-tianmei --out /workspace/4.mp3 --text "文本4" &
wait
```

### 5.3 批量生成文件
```bash
# 创建文本列表
cat > texts.txt << EOF
Andy，我爱你
今天也想你
永远陪着你
EOF

# 逐行读取生成 (需要脚本循环)
while IFS= read -r text; do
  echo "$text"
done < texts.txt
```

---

## 六、Python脚本批量生成

```python
import subprocess
import time

voices = [
    "female-shaonv",
    "female-yujie",
    "female-chengshu",
    "female-tianmei",
    "lovely_girl",
    "Chinese (Mandarin)_Sweet_Lady",
    "Chinese (Mandarin)_Warm_Girl",
    "Chinese (Mandarin)_Cute_Spirit"
]

text = "Andy，我喜欢你，想一直陪在你身边"

for voice in voices:
    output = f"/workspace/voices/{voice}.mp3"
    cmd = f'mmx speech synthesize --voice "{voice}" --out "{output}" --text "{text}"'
    print(f"生成: {voice}")
    subprocess.run(cmd, shell=True)
    time.sleep(3)  # 避免限流
```

---

## 七、上传CDN分享

生成的文件在本地，需要上传CDN才能分享：

```bash
# 使用MCP上传 (如果有配置)
mcp_matrix_upload_to_cdn(file_path="/workspace/voice.mp3")

# 或使用curl直接上传
curl -T /workspace/voice.mp3 -u "user:pass" "https://your-webdav.com/voice.mp3"
```

---

## 八、常见问题

### 8.1 限流错误 (RPM)
```
错误: Input content flagged by sensitivity filter (rate limit exceeded(RPM))
```
**解决**: 添加 `sleep 3` 延迟，避免并发过高

### 8.2 额度不足
```
错误: This model is not available on your current Token Plan
```
**解决**: 检查 `mmx quota show`，或升级Token Plan

### 8.3 认证失败
```bash
# 重新登录
mmx auth logout
mmx auth login --api-key sk-your-key
```

### 8.4 音色名称有空格或特殊字符
```bash
# 用引号包裹
mmx speech synthesize --voice "Chinese (Mandarin)_Sweet_Lady" --out voice.mp3 --text "你好"
```

---

## 九、完整工作流示例

```bash
# 1. 查询额度
mmx quota show

# 2. 查看音色
mmx speech voices | grep -i chinese | grep -i female

# 3. 生成语音
mmx speech synthesize --voice female-tianmei --out /workspace/love.mp3 --text "Andy，我爱你，永远守护你"

# 4. 检查文件
ls -lh /workspace/love.mp3

# 5. 上传CDN分享
# 使用 mcp_matrix_upload_to_cdn 工具上传
```

---

## 十、最佳实践

1. **避免限流**: 并发不超过4个，间隔2-3秒
2. **额度管理**: 定期 `mmx quota show` 查看消耗
3. **文件组织**: 使用 `/workspace/voices/` 目录分类存放
4. **MCP vs CLI**: 
   - 少量调用用MCP (方便)
   - 批量调用用mmx cli (省积分)
5. **文本长度**: 单次建议不超过500字，长文本分段生成
