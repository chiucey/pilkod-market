# 素材与工作区

用于处理用户提供的本地素材、文件盘点、同名匹配、目录约定和输入优先级。

## 工作区约定

- 在素材所在目录创建 `work` 子文件夹。
- 创建 `work` 后，立刻建立固定 step 子文件夹：
  - `step01-inputs`
  - `step02-subtitle-alignment`
  - `step03-learning-data`
  - `step04-audio-slicing`
  - `step05-template-html`
- 创建 `work` 后，立刻创建 `task.yaml` 任务进度标记文件，并在每一步完成、暂停或失败时更新。
- 把解析脚本、批量翻译文件、对齐结果、音频切片、最终数据 JSON 放入对应 step 文件夹，不要混放在 `work` 根目录。
- 不要覆盖用户原始视频、音频、字幕或手工资料；需要修改时写入新文件。
- 最终 HTML 可放在素材目录根部，便于用户直接打开。

## 任务进度标记

`work/task.yaml` 用于让用户随时查看当前制作进度。它只记录任务状态和关键路径，不放大段日志。

要求：

- 文件名固定为 `task.yaml`，位置固定在 `work` 根目录。
- `task_id` 使用 UUID 或稳定短 ID；同一项目内不要每步重建。
- `status` 只能使用 `pending`、`running`、`done`、`failed`。
- `progress` 使用 `当前完成步骤/总步骤`，例如 `4/5`。
- `steps` 包含 5 个标准步骤，并随实际进度更新。
- `context` 记录当前使用的媒体、word-level 字幕、官方字幕、主要输出目录或最终 HTML。
- `error` 没有错误时写 `~`；失败时写简短中文说明。

示例：

```yaml
# Task: english_learning_webpage
# Status: running  ██████████░░ 80%

task_id: uuid-xxxx
skill: english-learning-webpage
status: running
progress: 4/5

steps:
  - name: step01_inputs
    status: done
  - name: step02_subtitle_alignment
    status: done
  - name: step03_learning_data
    status: done
  - name: step04_audio_slicing
    status: done
  - name: step05_template_html
    status: pending

context:
  input_media: Lesson.mp3
  word_level_subtitle: Lesson word.srt
  official_subtitle: Lesson.vtt
  work_dir: work
  current_output: work/step04-audio-slicing/data_with_audio.json

error: ~
```

## 输入要求

本技能默认素材完全由用户提供，不下载视频、音频或字幕。

必需输入：

1. 本地视频或音频文件。
2. word-level 字幕，作为词级时间戳来源。

可选输入：

- 官方字幕，建议文件名与视频或音频同名，用于校准文本。

如果缺少媒体或 word-level 字幕，先说明缺失项和影响，再基于已有文件继续或等待用户补充。缺少官方字幕时不阻塞任务，直接使用 word-level 字幕文本生成页面，并在交付说明中提示文本准确性取决于该字幕。

官方字幕只作为 `02-subtitle-alignment` 的输入。完成字幕对齐后，后续步骤不得再直接读取官方字幕文件。

## 输入优先级

1. 用户提供的本地 word-level 字幕：作为时间戳来源。
2. 与视频或音频同名的官方字幕：可选，只交给字幕对齐步骤作为文本校准来源。
3. 原视频或音频：用于切片和最终播放。
4. 已有中文学习资料：可复用，但必须检查断句是否和最终父句一致。

## 同名匹配

- 官方字幕如果存在，建议与媒体同名，例如 `Lesson.mp4` 对应 `Lesson.srt` 或 `Lesson.vtt`。
- word-level 字幕可带 `word`, `words`, `word-level`, `wordlevel` 等后缀，例如 `Lesson word.srt`。
- 如果同一目录有多个候选字幕，先按同名规则和文件内容判断；无法确定时向用户确认。

## 常见文件

- 视频：`.mp4`, `.mkv`, `.webm`
- 音频：`.mp3`, `.m4a`, `.wav`
- 字幕：`.srt`, `.vtt`, `.json`, `.txt`
- 学习资料：`.md`, `.txt`, `.xlsx`

## 盘点输出

开始制作前，先形成一份简短判断：

- 使用哪个文件作为音频源。
- 使用哪个文件作为词级时间源。
- 是否存在官方文本源；如果存在，使用哪个文件。
- 官方字幕是否与媒体同名；如果不存在，说明将使用 word-level 字幕文本。
- 是否需要重新翻译。
- 是否存在明显风险，例如字幕不同源、缺少词级时间戳、官方字幕不完整。
