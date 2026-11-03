---
name: song-craft
description: |
  Compose a full Chinese song (lyrics + vocal track) from a topic, mood, or scene the user describes. Use this skill whenever the user wants to "写歌", "来首歌", "写一首关于...的歌", "给我作一首歌", "generate a song about", "compose a song for...". The skill writes original Chinese lyrics (with optional English hook) and renders them to an mp3 in one shot — no musical knowledge required from the user. Do NOT use for: pure background music / BGM without vocals (use a dedicated ambient-music skill), cases where the user has already written the lyrics and only wants the melody, video score work, or sound-effect / SFX generation.
---

# Song Craft

## Inputs to collect
- **Topic / scene / mood** (required): what the song is about. Free-form — "深圳下雨的夜晚"、"第一次带女儿坐飞机"、"和室友毕业散伙饭" 都行。
- **Use case** (optional, ask if unclear): 生日祝福、表白、纪念日、毕业、安慰人、自我鼓励、品牌主题曲。如果用户没提,默认按"用户自己想听/想发朋友圈"处理。
- **Length** (optional): 短(主歌+副歌,30s 内)/ 标准(完整一段,1 分钟左右)/ 完整(主歌+副歌+桥段,90s+)。默认标准。
- **Vocal preference** (optional): 男声/女声/对唱/合唱。默认按情绪推断(深情类用男声,轻快类用女声)。

问的方式:**先一句话确认主题**,其它缺省就按情绪推断,不要问 4 个问题。用户已经给你关键词就够了。

## Procedure

### 1. 提炼 prompt 关键词(给 music 模型用)
从用户输入里抽出 3-5 个稳定信号:
- 风格标签:Pop / Folk / R&B / Rock / Lo-fi / Electronic / Ballad / Hip-hop / Jazz
- 情绪标签:happy / sad / romantic / energetic / melancholic / peaceful / hopeful / nostalgic
- 节奏暗示:BPM 范围或 "slow / mid / fast"
- 乐器暗示:acoustic guitar / piano / synth / strings / lo-fi drum / 808
- 人声:male vocal / female vocal / duet

**为什么**:music 模型靠 prompt 关键词定调,模糊的"好听"是出不来东西的。

### 2. 写中文歌词(核心差异化)
歌词要求:
- 长度 **200-500 字**(留给 prompt 字符空间;超出后 music 模型可能截断)
- 主歌(verse)两段 + 副歌(chorus)两遍,简短直接
- 至少一句 **hook** —— 容易记住、能当标题
- 主题画面感强,避免空洞抒情("我的心好痛" < "你走的那天地铁站 / 报站声还是那句到站")
- 押韵宽松,不刻意凑;中文常用偶数句末押韵即可
- 必要时可加一句 **English hook** 在副歌头(增强记忆点)

写完先自检三件事:
1. 念出来顺不顺?(避免堆词、避免翻译腔)
2. hook 是不是够抓人?
3. 整体长度 ≤ 500 字吗?

### 3. 调 `batch_text_to_music`
参数:
- `prompt`: 第 1 步的关键词,英文为主,中英混合可
- `lyrics`: 第 2 步的歌词,原样传入
- `output_file_path`: `songs/<kebab-case-title>-<yyyymmdd>.mp3`(workspace 相对路径,放 `songs/` 目录)
- `sample_rate`: 44100(默认够用)
- `bitrate`: 256000(质量好,文件不太大)
- `format`: mp3

**为什么这些参数**:44100 Hz 是标准 CD 采样率,256kbps 是 mp3 的甜区(再高边际收益小,文件大)。目录前缀 `songs/` 便于用户后续在 drive 里找。

### 4. 验证 + 交付
- 读取 `batch_text_to_music` 返回的 file 路径,确认文件存在(`test -f` 或 `ls -la`)
- 用 `<deliver-assets>` 把音频文件交付给用户
- 同步给用户:歌名(取 hook 那句)、一句话创作说明(为什么这么写)、歌词全文(可选,用户想发朋友圈用得上)

## Output contract
- 一个 mp3 文件,workspace 路径 `songs/<title>-<date>.mp3`
- 用户消息里至少包含:歌名、歌词、创作意图一句话
- 必须用 `<deliver-assets>` 包裹音频文件,不要只发路径

## Failure handling
- **music API 报错** → 把完整 error 信息贴给用户,问要不要重试或调 prompt(通常换风格关键词就能成)
- **生成失败但歌词写得好** → 把歌词单独给用户,告诉用户曲子这边没跑通,可以稍后再试
- **主题太抽象**("写一首开心的歌") → 追问一个具体场景/画面,不要硬上(抽象主题 = 没主题)
- **歌词超 500 字** → 砍。宁可短一点让 music 模型完整处理,也不要让用户拿到一截断裂的副歌
- **用户已经写好歌词** → 不要用本 skill 的写词流程,直接进"我帮生成曲子"分支,跳到 Procedure 3 把歌词原样传入

## Examples

### Example 1: 简短主题
**Input**: "我想一首关于深圳下雨的夜晚的歌,要有点孤独但不要丧"
**Output**:
- 歌名:《末班车的窗》
- prompt: `slow indie folk, melancholic, rainy night, acoustic guitar, soft male vocal, lo-fi`
- lyrics: 主歌写雨夜地铁、城市灯、副歌 hook "雨落在末班车窗 / 玻璃映着我的脸 / 不孤独 / 只是有点想见"
- 交付:mp3 + 歌词全文 + 一句话"末班车 + 窗 = 城市孤独的视觉符号,孤独但不丧,所以副歌给了出口"

### Example 2: 用途驱动
**Input**: "我妈下周生日,想要一首能发朋友圈的歌,不要太煽情,要轻松点"
**Output**:
- 歌名:《小厨房》
- prompt: `warm pop, happy, family, light ukulele, female vocal, mid-tempo`
- lyrics: 主歌写"妈妈在厨房 / 油烟和笑声 / 红烧肉和拌黄瓜"日常细节,副歌 hook "小厨房 / 大世界 / 谢谢你 / 一直给我热饭"
- 交付:mp3 + 歌词 + 提示"日常细节比'妈妈我爱你'更打动人,所以选了厨房场景"
