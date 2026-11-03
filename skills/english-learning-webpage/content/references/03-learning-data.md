# 学习数据、翻译与提示

用于生成中文翻译、符号化发音提示、固定搭配和瘦身 JSON。

## 数据字段

最终模板数据使用短字段：

- `t`：英文父句。
- `z`：自然中文翻译。
- `s/e`：父句绝对起止时间。
- `a`：父句 Base64 音频。
- `w`：词级数组，每项为 `{"t":"word","s":0.12,"e":0.34}`。
- `rh`：局部连读、弱读、失爆/不完全爆破、闪音 T 提示。
- `r`：整句提示，仅在没有局部提示时使用。
- `c`：固定搭配或高价值短语。

## 翻译规则

- 为每个父句生成自然中文，不要逐词硬翻。
- 任务超过 50 条时分批处理。
- 如果更换了断句或底稿，必须重新翻译或严格重新匹配旧翻译。
- 不允许出现空翻译、`暂无翻译`、`[Translated: ...]`、Markdown code fence 或占位文本。
- 每批翻译后程序化校验数组长度和 `index` 是否一致。
- 翻译批次、`translation_manifest.json`、`learning_data_draft.json` 都只是中间物，不能作为 Step 03 完成标志。
- Step 03 的正式产物固定为 `work/step03-learning-data/learning_data.json`，顶层必须包含 `sentences` 数组。

## Step 03 完成标准

只有同时满足以下条件，才允许把 `task.yaml` 中 `step03_learning_data` 标为 `done`：

- `work/step03-learning-data/learning_data.json` 已生成。
- 顶层结构是对象，且包含非空 `sentences` 数组；不要使用 `items` 作为正式结构。
- `sentences.length` 与 Step 02 的父句数量一致。
- 每个父句都有非空 `translation` 或后续模板可识别的 `z` 字段。
- 每个父句保留英文 `text`、`start`、`end` 和 `words`。
- 每个父句都带有 `rh` 与 `c` 字段；没有内容时使用空数组，不要省略。
- 不得把 `learning_data_draft.json`、翻译批次文件或 Step 02 的 `aligned.json` 交给 Step 04。

建议程序化检查：

```text
读取 learning_data.json
确认 Array.isArray(data.sentences)
确认 sentences 数量与 aligned.json 一致
确认每个 sentence.translation 非空
确认每个 sentence.words 非空
确认每个 sentence.rh 和 sentence.c 是数组
```

## 固定搭配

`c` 字段格式：

```json
[
  {"p": "end up", "z": "最终；结果是"}
]
```

选择规则：

- 每句 0 到 3 个。
- 优先选择高频短语、短语动词、固定表达、听力里容易整块理解的表达。
- 不要堆砌普通生词。
- 不生成例句，页面只展示原文短语和中文含义。

## 连读弱读提示

当需要生成或优化 `rh` 字段时，优先使用 `references/rh-subagent-prompt.md` 中的子 agent 提示词。把当前父句英文文本和词级数组传给子 agent，让它作为专业英语老师分析美式英语中的连读、弱读、变音、省音和失爆；再把返回的 JSON 数组写入该句 `rh`。

优先使用 `rh`：

```json
[
  {"from": 11, "to": 12, "t": "safe ‿ outside"},
  {"i": 18, "t": "righ(t)"}
]
```

规则：

- `from/to` 是从 0 开始的闭区间，适合跨词提示。
- `i` 只用于单词提示。
- 跨词连读优先用 `from/to`，不要只挂在第一个词上。
- `rh` 范围不得重叠；冲突时合并为更大词组或保留更影响听辨的提示。
- 标注要克制，只标影响听辨的地方，不把整句改成音标。
- `rh[].t` 只写符号化发音标注，不写中文解释。
- 连读使用 `‿`，如 `safe ‿ outside`。
- 弱读使用 `_斜体_` 形式，如 `_to_`。
- 失爆/不完全爆破使用括号包住弱化音，如 `righ(t)`、`jus(t)`。
- 闪音 T 使用 `t[d]`，如 `wa t[d] er`。
- 美式英语中词尾 `t/d` 失爆是重点：`it/that/what/but/not/just/and/n’t` 等在辅音前、停顿前或快速语流中应更积极标注，不要只标连读。
- 如果子 agent 返回解释文字或 Markdown，必须清理成合法 JSON 数组后再写入 `learning_data.json`。

## JSON 瘦身

- 时间保留 2 位小数。
- 移除 `duration`, `offset`, `confidence` 等页面不需要的字段。
- 长视频必须控制 HTML 体积；优先缩短字段名，而不是牺牲交互功能。
