# 音频切片

用于制作父句音频、Base64 嵌入和相对时间轴。

## 切片策略

- Step 04 的唯一输入是 `work/step03-learning-data/learning_data.json`。
- 执行前必须检查 Step 03 已在 `task.yaml` 中标为 `done`，且 `learning_data.json` 已通过 Step 03 完成标准。
- 禁止直接读取 `work/step02-subtitle-alignment/aligned.json`、`learning_data_draft.json` 或翻译批次文件来制作音频切片。
- 每个父句生成一个物理 MP3 切片。
- 切片以 Base64 形式写入该句 `a` 字段，保证页面离线可播放。
- 不生成子句音频。
- 不生成选中目标音频。
- 选中目标播放时复用父句音频，并用 `currentTime` 跳到首词时间。

## Padding

默认父句切片范围：

```text
slice_start = sentence_start - 0.08s
slice_end   = sentence_end + 0.12s
```

注意：

- `slice_start` 不得小于 0。
- 如果抽查发现首词被切掉，可增大 start padding。
- 如果大量句子整体错位，先检查字幕同源性，不要只靠 padding 掩盖。

## 相对时间轴

最终页面中的词级时间必须相对父句切片起点：

```text
word_relative_start = word_absolute_start - slice_start
word_relative_end   = word_absolute_end   - slice_start
```

父句 `s/e` 可以保留原音频绝对时间，用于显示时间戳和排查问题。

## 输出要求

- 输出固定放入 `work/step04-audio-slicing/data_with_audio.json`。
- 输出必须保留 Step 03 的 `translation`、`rh`、`c` 字段，不得被音频切片步骤丢弃。
- 输出完成后再把 `task.yaml` 中 `step04_audio_slicing` 标为 `done`，并把 `current_output` 指向 `work/step04-audio-slicing/data_with_audio.json`。

## 码率

- 默认不额外压缩，使用原视频或原音频的码率。
- 如果 HTML 体积过大，先评估是否需要降低音频码率；不要直接删除词级数据或学习功能。

## 抽查

至少抽查：

- 第一条父句首词是否完整。
- 中间随机 3 条父句是否同步。
- 最后一条父句是否完整结束。
- 选中目标播放是否能从首词跳到末词并自动停止。
