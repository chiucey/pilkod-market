---
name: kids-english-readalong
description: |
  Read English book pages aloud for a young child (default age 6) to follow along:
  transcribe the exact printed English from an uploaded/photographed page, then produce
  two standard American English audio passes — one slow (speed 0.7) and one normal (speed 1.0) —
  plus a written Chinese translation that is never spoken aloud. Use this skill whenever the
  user shares an image of an English book and wants it read: triggers include "读一下这页",
  "这本书怎么读", "给孩子念一下", "跟读", "美音朗读", "标准美音", "点读", "raz", "牛津树",
  "分级阅读", "phonics", "自然拼读", "read this page aloud", "pronounce this for my kid".
  Do NOT use for Chinese-only pages, for transcribing an existing audio file (use listen_audio),
  or for grammar/vocabulary explanation when no page image is involved.
---

# Kids English Read-Aloud

把一张英文书页变成两遍音频 + 一份中文译文。孩子对着书跟读，所以**转写保真度 > 一切**。

## Inputs to collect

- **图片**（必需）。没有图就不要往下走，先跟用户要。
- **不用问的**：年龄默认按 6 岁（学龄前/小学低年级）处理；音色默认美音女声。
  除非用户明确说了偏好，否则直接做，不要拿这两个问题去打断家长。

## Procedure

### 1. 用 Read 工具直接看图，逐字转写

不要为了 OCR 去调 `describe_images`——Read 工具本身就能读图，你自己就是 OCR。
先确认 Read 能出图；只有在拿到的是一个远程 URL 且无法落盘时，才走
`upload_temp_url` + `describe_images` 兜底。

转写规则（错一个字这条音频就废了，所以这步最要紧）：

- **逐字照抄**书上的拼写、大小写、标点。
- **不要顺手"修正"原书**。分级读物常有 `he go home`、`I has a cat`、`colour`、
  故意重复的韵脚（`A bug, a bug, a big bug`）。这些要**照读**，然后单独标注出来给家长看。
- 页面有单词框/词表就**单独成组**列出来，和句子分开处理——它们的朗读节奏不同。
- 页面同时有词表和正文，就两组都给音频。
- 看不清、被手指/反光遮住、被裁掉一半 → **不要猜**。标 `[看不清]`，
  并明确请用户重拍这一页。给一段编出来的音频比不给更糟，孩子会照着错音跟读。

### 2. 决定朗读单元和停顿

- **单词页**：单词之间用逗号连起来（`rabbit, carrot, jump`），TTS 会在逗号处自然停顿，
  听感像老师一个个点名。
- **句子/段落**：按原顺序整段送入，句号自带停顿。
- **超过 400 字符**：按句号切分成 2–3 组，每组一套慢速/正常，文件名用 `-1`/`-2` 后缀。
  一次音频超过 1 分钟，6 岁孩子跟读会跟丢。

### 3. 一次调用合成两遍音频

走 `mcode-tools` CLI（前提：已在 PATH 上）。把 requests 写成文件再发，
避免中文/引号被 shell 吃掉：

```bash
# 1) 写参数文件 tts.json（下面是一组"慢速+正常"的完整内容）
cat > /workspace/output/tts.json <<'JSON'
{"requests":[
  {"text":"<慢速文本>","voice_id":"English_Graceful_Lady","speed":0.7,"output_file":"<name>-slow.mp3"},
  {"text":"<正常文本>","voice_id":"English_Graceful_Lady","speed":1.0,"output_file":"<name>-normal.mp3"}
]}
JSON

# 2) 调用（bash 的 timeout 字段设 600）
mcode-tools connector call connector__matrix__batch_text_to_audio \
  --args-file /workspace/output/tts.json
```

一组慢速+正常 = 2 个 request；有词表又有正文 = 4 个 request，**一次调用传完**
（该工具单次最多 10 个）。返回值里取 `success_items[].node_id`。

- **voice_id 默认 `English_Graceful_Lady`**（标准美音，音色温暖清晰，适合亲子朗读）。
  备选：`English_Trustworthy_Man`（美音男声）、`English_Diligent_Man`（美音男声，更沉稳）。
  **不要用 `English_Aussie_Bloke`**——那是澳音，孩子学的是美音。

**文件命名**：`<页名>-<组名>-slow.mp3` / `<页名>-<组名>-normal.mp3`。
组名：整页一组就省略；词表用 `words`，正文用 `text`，切分多段再加 `-1`/`-2`。
例：`rabbit-words-slow.mp3`、`rabbit-text-normal.mp3`。

### 4. 下载

脚本依赖 `mcode-tools` 在 PATH 上。

```bash
bash .skills/kids-english-readalong/scripts/fetch_audio.sh /workspace/output \
  "<slow_node_id>:rabbit-words-slow.mp3" "<normal_node_id>:rabbit-words-normal.mp3"
```

### 5. 组装输出

慢速在前、正常在后，中文译文放最后——家长按顺序播放，孩子两遍听熟再看中文。

## Output contract

1. **识别到的英文原文**（让家长核对，这是信任基础）
2. **慢速音频**（speed 0.7）+ **正常语速音频**（speed 1.0），标准美音
3. **中文译文**——只写出来，**绝不对中文调用 TTS**。中文是给家长看的辅助，不是朗读内容。

交付音频用 `<deliver-assets>`，路径写 `/workspace/output/` 下的绝对路径。
caption 里标出倍速和内容组，家长一眼知道该先点哪个。
可以用 `ffprobe -v error -show_entries format=duration -of csv=p=0 <file>` 取时长一并标上，
家长靠这个判断该重点重听哪一遍。

译文风格：口语化、贴近 6 岁孩子的理解；直译生硬的句子要顺一遍再给。
原书有语法/拼写错误时，译文按**原书实际意思**给，并在译文旁加一行 `📖 原书如此`。

## Failure handling

- **图片模糊/文字不全** → 停下来要一张清晰的。宁可不产出，也不要错读。
- **页面不是英文**（中文课文、日文、只有插图） → 说明情况，问用户是要翻成英文还是别的处理，
  不要擅自用英语念中文。
- **文字太多** → 按上面规则切分，或告诉用户"这页内容较多，建议分两次"。
- **TTS 失败/返回 `failed_items`** → 把 `error_msg` 报给用户，不要静默换个参数重试。
- **用户嫌音色不好听** → 直接换 `voice_id` 重跑，不要反过来质疑用户。
- **用户想逐句单读** → 见下面的扩展。

### 扩展：逐句单读

用户问"能不能一句一句来"时，额外给一组每个句子一条的正常语速音频（≤ 8 句）。
在同一个 `batch_text_to_audio` call 的 requests 里追加即可，不用重跑慢速版。

## Examples

**Input**：家长发来一页牛津树照片，图上是词表 `rabbit / carrot / jump`
和句子 `The rabbit jumps over the carrot.`，说"帮我读一下，孩子跟着念"。

**Output**：

识别到的原文（词表和正文两组分开）：

```
rabbit
carrot
jump

The rabbit jumps over the carrot.
```

这一页没有拼写或语法错误，可以放心照读。

<deliver-assets>
<media src="/workspace/output/rabbit-words-slow.mp3" caption="单词框 · 慢速跟读 0.7x" />
<media src="/workspace/output/rabbit-words-normal.mp3" caption="单词框 · 正常语速 1.0x" />
<media src="/workspace/output/rabbit-text-slow.mp3" caption="句子 · 慢速跟读 0.7x" />
<media src="/workspace/output/rabbit-text-normal.mp3" caption="句子 · 正常语速 1.0x" />
</deliver-assets>

中文译文（仅文字，不朗读）：
- rabbit 兔子 · carrot 胡萝卜 · jump 跳
- 兔子跳过了那根胡萝卜。

建议顺序：单词框慢速 → 单词框正常 → 孩子自己念一次 → 句子慢速 → 句子正常。
一句话就够，别把小提示词写成百科全书——家长要的是"现在点哪个"。

一句话就够，别把小提示词写成百科全书——家长要的是"现在点哪个"。
