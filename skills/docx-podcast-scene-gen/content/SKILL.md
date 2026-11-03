---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e325b3033dd843c5bdccdc93e7bb39c2
    PropagateID: e325b3033dd843c5bdccdc93e7bb39c2
    ReservedCode1: 3046022100be8721db7d0ef258ec39d5e2b503b2b5b703e535238bda29a1a233d4d4da6f3e022100aa0337a4e8ef04d359442c4a2df1be1a6b9e89d75fc85845a9b8a1cc91baade3
    ReservedCode2: 3045022041548c552c61fa587297d26de76760a0cb21bae894efc3aa341373fcf664390c022100e7bf1f395880ee377c2326680cf87ec34fb0506f9e0b12bd30c72cddf0532d61
description: 将播客/口播文案（.docx文件）自动拆分为多个场景，并为每个场景生成9:16竖屏图片。触发条件：用户上传了 .docx 文案文件，并要求生成配套图片、生成短视频素材、生成场景图、按文案出图、图文配套。
name: docx-podcast-scene-gen
---

# docx-podcast-scene-gen

将播客/口播文案（.docx）自动生成9:16竖屏场景图的工作流。

## 工作流程

### 第1步：读取 .docx 文件

docx 文件路径从消息的 `file_path` 或媒体附件路径获取。

使用脚本读取：
```bash
python3 /workspace/skills/docx-podcast-scene-gen/scripts/read_docx.py <docx文件路径>
```

### 第2步：切分场景

使用 LLM（自己分析）将文案按主题切分为独立场景，每场景生成：
- 场景标题（中文，10字以内）
- 场景描述（用于生成图片的prompt参考）
- 对应文案片段

**常见场景模式（优先匹配）：**

| 场景类型 | 关键词 | 图片方向 |
|---------|--------|---------|
| 开场/介绍 | 欢迎收听、大家好、开场 | 演播室/主播/温暖氛围 |
| 食材/产品展示 | 三位食材、食材搭配、主角 | 陈列桌/实物特写 |
| 功效讲解A | 牛大力、补腰肾、强筋骨 | 人物久坐/腰部特写 |
| 功效讲解B | 枸杞、养肝、明目、眼干 | 眼睛疲劳/屏幕 |
| 功效讲解C | 猪尾、胶原蛋白、胶质 | 炖汤/胶原蛋白特写 |
| 功效总结 | 核心作用、总结、适合人群 | 图文信息图 |
| 烹饪方法 | 做法、炖、焯水、步骤 | 厨房/烹饪过程 |
| 食用建议 | 多久一次、每周、坚持 | 家庭喝汤场景 |
| 结尾告别 | 拜拜、下期、再见 | 主播挥手告别 |

**场景数量控制：** 优先保留6~10个关键场景，去除重复内容。

### 第3步：为每个场景生成9:16图片

每张图使用 `image_synthesize`，比例 `aspect_ratio: "9:16"`，分辨率 `resolution: "2K"`。

Prompt 撰写原则：
- 以**场景画面描述**为主，不要出现图片文字
- 包含：主体、动作、环境、光线、情绪、风格
- 避免文字出现在图里（交给剪映/配音处理）
- 风格统一：插画/手绘风 or 实拍风，整套保持一致
- 每张图的 prompt 都加上 `Chinese podcast vertical 9:16 scene, ...`

批量生成（最多10张/次），超过10张分批调用。

### 第4步：发送图片到微信

使用 `message` tool，`action=send`，`channel=openclaw-weixin`，`media` 参数传本地路径。

每张图配合简短文字说明（如"场景① 开场介绍"），逐张发送，每次最多连续发5张避免频率限制。

### 第5步：输出素材清单

发送完毕后，总结输出：
- 场景数量
- 每张图的序号、标题、对应文案关键词
- 告知用户文件路径：`/workspace/scene01.png` ~ `scene0N.png`
- 提示用户直接用于剪映配合语音合成

## 注意事项

- **语音不生成**：用户只需图片，语音由用户自行处理
- **视频不生成**：用户用图片+语音在剪映里合成
- **分批发送**：每批最多5张，避免触发频率限制
- **文件命名**：按序号 scene01.png, scene02.png... 命名，方便用户排序
- **风格统一**：同一套图保持相同艺术风格（开场/结尾用插画风，全套统一）
- **docx 路径**：从消息附件路径读取，格式：`/root/.openclaw/media/inbound/xxx.docx`
