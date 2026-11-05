# ASR 调用片段(口播转录)

> 本文件是 WUION1011海信动作 skill 的 ASR 工具调用模板。复刻以下命令即可获得 0.01s 精度的句级时间戳。

## 流程总览

1. ffmpeg 抽离 wav → 本地路径
2. `mcode-tools upload_temp_url` 上传 → 拿到 temp_url
3. `connector__matrix__listen_audio` 或 `connector__matrix__audios_understand` → 转录 + 时间戳
4. 解析 JSON,提取每句的 start / end / text
5. 段数 N = 分镜数

## 步骤 1:ffmpeg 抽离(参考视频 → wav)

```bash
ffmpeg -y -i "<参考视频.mp4>" -vn -acodec pcm_s16le -ar 44100 -ac 2 /tmp/参考音频.wav
```

## 步骤 2:上传 wav 拿 temp_url

```bash
mcode-tools upload_temp_url /tmp/参考音频.wav --mime-type audio/wav
```

返回 JSON 形如:
```json
{
  "file": "/tmp/参考音频.wav",
  "filename": "参考音频.wav",
  "bytes": 1466446,
  "mime_type": "audio/wav",
  "temp_url": "https://matrix-internal-cn.oss-cn-shanghai.aliyuncs.com/...wav?...",
  "expires_in_seconds": 3600
}
```

把 `temp_url` 复制下来,下一步用。

## 步骤 3a:listen_audio(整段转录,适合 ASR 简单句)

```bash
mcode-tools connector call connector__matrix__listen_audio --args '{
  "audio_info": {
    "url": "<temp_url>",
    "prompt": "verbatim transcription in Chinese, with sentence-level timestamps in 0.01s precision. Format: start_seconds - end_seconds: text"
  }
}'
```

返回 JSON 形如:
```json
{
  "code": 0,
  "message": "ok",
  "transcription": "00:00.00 - 00:08.52: 春天来了,给家里来个大扫除,顺便换个新电视,...",
  "error": ""
}
```

**注意**:listen_audio 倾向返回 1 段连续时间戳,适合 5 秒以内的极短视频;超过 5 秒或多句口播,推荐用步骤 3b。

## 步骤 3b:audios_understand(强制拆句,0.01s 精度)

```bash
mcode-tools connector call connector__matrix__audios_understand --args '{
  "audio_info": [{
    "url": "<temp_url>",
    "prompt": "请逐句转录这段中文口播,在每个自然换气点(标点/停顿)拆段,每段单独一行,格式:开始秒-结束秒:文本。请确保不漏掉任何字。如果有重复词、语气词都保留。"
  }]
}'
```

返回 JSON 形如:
```json
{
  "code": 0,
  "message": "ok",
  "results": [{
    "success": true,
    "description": "0.00-0.81:春天来了\n0.81-2.05:给家里来了个大扫除\n2.05-4.22:顺便换个新电视感觉整个家都活过来了\n4.22-6.33:这次我选择的是海信电视85E7S Pro\n6.33-8.00:53毫米超薄机身",
    "error": "",
    "source": "..."
  }]
}
```

把 `description` 字段按 `\n` 拆分,得到 5 段口播。

## 步骤 4:与画面时间戳对齐校准

ASR 给出的时间戳是基于音频的,可能与画面字幕切换点有 ±0.2s 偏差。校准方法:
1. 抽帧(Step 2)中找到字幕切换的精确秒数
2. 把 ASR 时间戳的 start / end 向字幕切换点对齐(以字幕切换点为准)
3. 若 ASR 漏了某段口播(如"上墙后就像一幅画"出现在字幕里但 ASR 没识别到),以字幕为准手动补一行

校准后的口播段数 N = 分镜数。

## 失败模式与应对

| 失败 | 原因 | 应对 |
|---|---|---|
| listen_audio 返回整段 1 行 | 工具特性 | 改用 audios_understand |
| audios_understand 把 2-3 句合并 | 模型判断为同句 | 接受合并(语义连贯,不必硬拆);若用户强烈要求拆,prompt 加"每个标点都要单独成行" |
| audios_understand 拆得过碎(每字一行) | prompt 误读 | 合并相邻短句(单段 ≤ 4 秒),按语义整合 |
| 音频太短,ASR 报"无法识别" | 音频 < 1 秒 | 用 listen_audio 重试;仍失败则在最终文件口播段留空,标"待人工标注" |
| 时间戳格式异常(如 MM:SS 而非 ss.ss) | 工具误判 | 当 MM:SS 处理:00:00 = 0.00s,00:01 = 1.00s |

## 已知工具能力

- `connector__matrix__listen_audio`:单段,适合 < 5s
- `connector__matrix__audios_understand`:可自定义 prompt,适合任意长度
- 两者均需 HTTPS URL(本地路径必须先 upload_temp_url)
