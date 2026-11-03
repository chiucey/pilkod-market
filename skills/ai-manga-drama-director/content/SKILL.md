---
name: ai-manga-drama-director
description: |
  把电影导演方法论接进 AI 漫剧/AI 短片生产全流程。提供导演剧本提示词模板、角色 DNA 档案、
  分镜脚本生成、跨镜一致性控制、五维锁死框架、工具矩阵、变现路径、行业趋势、剧本转分镜
  软件推荐、即梦/Seedance 视频生成实战案例库,并附完整提示词素材库(15种题材人物 /
  50种表情 / 16电影感运镜 / 即梦50条运镜 / 5种风格背景 / MJ V6 角色一致性范例 /
  角色生成5层公式)。Triggers on: "AI 漫剧"、"AI 短片"、"AI 分镜"、"AI 漫剧分镜脚本"、
  "AI 漫剧分镜"、"导演剧本"、"AI 漫剧剧本"、"分镜提示词"、"角色一致性"、"Seedance 2.0"、
  "Seedance 2.5"、"AI 电影分镜脚本"、"AI 漫剧制作"、"漫剧分镜"、"AI 短剧分镜"、"想拍一个
  AI 短片"、"Midjourney 角色一致性"、"MJ cref"、"AI 人物提示词"、"AI 漫剧角色"、
  "漫剧运镜"、"AI 漫剧风格"、"漫剧表情"、"AI 漫剧背景"、"AI 漫剧行业"、"剧本转分镜"、
  "即梦"、"Dreamina"、"AI 视频生成"、"视频延长"、"白模提示词"、"白模替换"、"红框编辑"、
  "粗颗粒度"、"细颗粒度"、"多语言 AI 视频"、"视频改写"、"链式延长"、"双线并行镜头"、
  "超长视频"、"分镜级提示词"、"长段叙事"、"完整分镜"、"公共提示词库"、"AI 短片全流程"、
  "系列化方向"、"打工人"、"时间交易"、"科幻短片"。
  Do NOT use for: 单张 AI 插画生成、纯文字小说写作、不带 AI 元素的传统影视剧本、
  PPT 静态漫剧、非漫剧的视频剪辑。
---

# AI 漫剧导演

> 服务于追求**作者电影美学**(贾樟柯 / 是枝裕和 / 毕赣 / 《宇宙探索编辑部》)的 AI 短片创作,
> 而非土味爽文漫剧。摄影教师 / 传统影视背景用户的电影审美是护城河。

## Inputs to collect

开工前确认 4 项决策(用户没说就问):

- **赛道**:作者电影风格(克制、留白、社会议题)/ 爽文漫剧(重生/赘婿/逆袭)/ 二次元(沙雕/治愈)/ ToB 定制
- **比例**:竖屏 9:16(抖音/快手)/ 横屏 16:9(B站/爱奇艺)/ 电影宽屏 2.35:1(作者电影强烈推荐)
- **时长**:短视频 1-3 分钟 / 长剧集 5-10 分钟
- **一句话故事核**:`[人物] + [困境] + [转折] + [视觉钩子]`

## References 索引(全部素材按需读取)

**核心方法** (Stage 1-4 主流程):
- `references/screenplay-prompt.md` — 导演剧本完整提示词模板(含新手 6 步流程 + 单集脚本示例)
- `references/character-dna.md` — 角色五维 DNA 档案 + 跨镜一致性控制
- `references/storyboard-prompt.md` — 分镜脚本提示词(含 10 大模块 + 5 模板 + 工具适配差异)
- `references/video-gen-cases.md` — AI 视频生成实战案例库(即梦/Seedance,29 个分类案例 + 23 个完整提示词 + 粗细颗粒度 + 链式延长 + 25镜 vs 8段超长片范式)
- `references/case-zhantai.md` — 完整分镜拆解案例: 《斩仙台下》80 秒 / 15 镜三段式
- `references/case-full-episode.md` — 完整长片案例: 《反正也没时间活》7 章全流程 + 公共提示词库 + 183 分镜 + 系列化方向
- `references/sample-screenplay-mecha.md` — 完整剧本范本: 《钢铁黎明》科幻机甲片 + 剧本特色分析
- `references/tool-matrix.md` — 工具矩阵 + 变现路径 + 6 个剧本转分镜软件 + 行业趋势速读

**提示词素材库** (`references/prompt-library/`,按题材/风格调用):
- `prompt-library/genres.md` — 15 种题材的人物 prompt 案例 + 作者电影风格追加
- `prompt-library/expressions.md` — 50 种面部表情公式(分部位精准描述)
- `prompt-library/backgrounds.md` — 5 种风格背景 prompt + 现实主义追加
- `prompt-library/styles.md` — 主流/小众风格库 + 5 个作者电影风格包
- `prompt-library/character-formula.md` — 角色生成 5 层公式(填空模板)
- `prompt-library/mj-v6-example.md` — Midjourney V6 角色一致性完整打法
- `prompt-library/camera-cinematic.md` — 16 个电影感运镜(作者电影/电影短片)
- `prompt-library/camera-jimeng.md` — 即梦 50 条运镜(二次元/漫剧)

## Procedure

按四段式生产链路推进,每段都有专用提示词,**不要混用**:

```
[1. 导演剧本] → [2. 角色+场景资产库] → [3. 分镜生图+生视频] → [4. 后期合成+发布]
```

### Stage 1 — 导演剧本(立项后第一步)

读取 `references/screenplay-prompt.md`,把模板里的占位符替换成用户的题材/角色/视觉风格,完整复制给 ChatGPT/DeepSeek/豆包。

要求 AI 输出 **17 镜**(允许 16-18)完整导演剧本,每镜 ≥ 300 字,包含 10 要素:
镜号 / 时长 / 景别 / 运镜 / 场景(≥120字) / 人物动作(≥100字) / 对白 / 环境音 / 光线设计 / 导演意图。

强制约束:
- 每隔 2-3 镜必有一个无对白留白镜头
- 结尾必须黑幕 + 白字 + ≤70 字 + "小时候以为……后来才知道……"结构
- 禁止赛博朋克 / 未来城市 / 悬浮汽车(除非题材明确要赛博)
- 现实主义克制表达,不刻意煽情

迭代节奏 4 轮:完整生成 → 追问导演意图 → 优化台词微表情 → 检查整体节奏。

### Stage 2 — 角色 DNA 档案(剧本定稿后,生图前)

**主流程**:读取 `references/character-dna.md`,给每个核心角色建立五维档案(外貌 / 服饰 / 动作习惯 / 情绪表情模板 / 镜头语言)。

**调用 prompt-library**:
- 题材不明 → 读 `prompt-library/genres.md`,找最近匹配的题材 prompt 模板
- 写角色 prompt → 读 `prompt-library/character-formula.md`,套 5 层公式填空
- 微表情不准 → 读 `prompt-library/expressions.md`,分眉毛/眼/嘴/鼻/头/肩精准描述
- 用 Midjourney → 读 `prompt-library/mj-v6-example.md`,完整 `--cref/--cw/--seed` 配置

落地动作:
1. 生成角色三视图(白底,正面/侧面/背面)作为参考锚点
2. 群像 DNA 速记卡(一表全剧角色对比)
3. 锁定跨镜一致性参数(按工具选):

| 工具 | 锁定方式 |
|---|---|
| Midjourney V6 | `--cref 三视图链接 --cw 100 --seed 固定值`(完整案例见 `mj-v6-example.md`)|
| Stable Diffusion | IP-Adapter + ControlNet / LoRA 0.6-0.8 / InstantID |
| 即梦 / SEKO / 萌动 | 角色库 / 特征码 / @角色名 |

参数固化三原则:固定模型版本 + 锁定核心参数(采样器 DPM++ 2M Karras、步数 ≥30、CFG 7-8、Seed 复用)+ 统一提示词结构。

### Stage 3 — 分镜脚本(剧本转生图/生视频提示词)

**主流程**:读取 `references/storyboard-prompt.md`,按提示词公式生成:
`[运镜/景别] + [主体] + [场景细节] + [光影色调] + [技术参数]`

**调用 prompt-library**:
- 运镜不会写 → 读 `prompt-library/camera-cinematic.md`(作者电影/电影短片)或 `prompt-library/camera-jimeng.md`(二次元/漫剧)
- 场景太单调 → 读 `prompt-library/backgrounds.md`,找匹配风格的环境 prompt
- 风格漂移 → 读 `prompt-library/styles.md`,锁定主风格包(如"贾樟柯早期 35mm 胶片")
- **看完整分镜案例学习结构** → 读 `references/case-zhantai.md`《斩仙台下》15 镜拆解
- **即梦/Seedance 实战视频提示词** → 读 `references/video-gen-cases.md`(29 个分类案例 + 7 个完整提示词)

节奏控制:第一幕(镜 1-6 慢节奏建立)/ 第二幕(镜 7-12 中速升级)/ 第三幕(镜 13-17 快慢交替)。留白镜头穿插。

生图后必做五维一致性检查清单(面部 / 发型 / 服饰 / 体型 / 风格),用 SD Inpaint / Photoshop / ControlNet 修正。

**分镜图转视频(Stage 3.5 隐藏环节)**:把每镜分镜图输入视频模型生成动态片段,具体写法见 `references/video-gen-cases.md` 的"基础段/延长/高级编辑"三套模板。

### Stage 4 — 后期合成+发布

工具链:**剪映专业版**为主(免费且功能全)。
- AI 配音:剪映文本朗读,选适配人设音色
- 字幕:无衬线体或楷体,白字黑边
- 转场:溶解 / 推进,避免花哨
- 调色:墨染 / 电影色调,与原图冷暖统一
- 导出:9:16 或 2.35:1,1080P,30fps,无水印

发布平台选择 + 6 个剧本转分镜软件 + 行业趋势参考 `references/tool-matrix.md` 第七、八节。

## Output contract

每个 AI 漫剧项目交付 4 件套:

```
project/
├── screenplay.md            # 17 镜导演剧本
├── character-dna/           # 角色 DNA 档案 + 三视图
│   ├── A_小宇.md
│   ├── B_机器人.md
│   └── 速记卡.md
├── storyboard/              # 分镜总表 + 每镜提示词
│   ├── 总表.xlsx
│   ├── 01_开场空镜.md
│   └── ...
└── final-cut/               # 成片 + 平台分发版本
    ├── 抖音版_9x16.mp4
    └── B站版_2.35x1.mp4
```

## Failure handling

| 失败模式 | 修正动作 |
|---|---|
| AI 出"分镜摘要"而非"导演剧本" | 提示词开头必须强调 `Director's Screenplay`,且每镜 ≥300 字强制 |
| 角色跨镜换脸 | 重新校准三视图,加 `--cw 100` 锁定权重 |
| 节奏像 PPT 翻页 | 强制插入留白镜头,每 2-3 镜 1 个无对白 |
| 视觉像赛博朋克 | 显式禁止未来元素;不要写"科幻感"这种模糊词 |
| 结尾煽情过度 | 强制黑幕结构 + ≤70 字 + `小时候以为……"句式` |
| 镜头与剧本脱节 | 在分镜总表里强制每镜引用剧本镜号 |
| 摄影质感丢了 | 提示词里加 `35mm 胶片质感 / 侧逆光 / 空气颗粒感 / 景深明显` |
| 表情太夸张像 AI 漫画 | 读 `expressions.md`,改用"微表情词"(苦笑 / 隐忍落泪 / 疏离冷漠) |
| 角色 prompt 写不全 | 套 `character-formula.md` 的 5 层公式自检 |
| 风格漂移 | 锁定 `styles.md` 的一个主风格包,所有镜同一前缀 |
| **不知道分镜怎么分** | 读 `references/case-zhantai.md`,《斩仙台》15 镜是完整可学案例 |
| **不知道该用哪个软件** | 读 `tool-matrix.md` 第七节"剧本→分镜自动转化软件"决策表 |
| **分镜图转视频不会写提示词** | 读 `references/video-gen-cases.md`,14 章实战库(9 大分类 + 23 个完整提示词 + 范式对比) |
| **视频生成后角色不一致** | 读 `video-gen-cases.md` 案例 5.1-5.2,白模替换通用结构 + "不穿模不变脸"约束 |
| **想接续已生成视频(延长)** | 读 `video-gen-cases.md` 第十二章链式延长范式(女孩接星光链 / 雨夜咖啡馆链) |
| **想把白模视频升级为成品** | 读 `video-gen-cases.md` 第八章 + 第十章,粗细颗粒度范式 + 5 个必加约束 |
| **想做复杂动作戏(Boss战/追逐)** | 读 `video-gen-cases.md` 案例 5.3 糖果厨房 Boss 战,细颗粒度 + 6 段时间分镜模板 |
| **想做产品广告级视频** | 读 `video-gen-cases.md` 案例 5.4 高端香水广告,产品级提示词范式 |
| **想做作者电影风格的 3 分钟长片** | 读 `video-gen-cases.md` 案例 7.2 雨夜校园,8 长段连续叙事范式(用户主推) |
| **想做喜剧/动作密集反转的 3 分钟** | 读 `video-gen-cases.md` 案例 7.1 机器人降临,25 镜头堆叠范式 |
| **想做治愈系单集短片(32 秒)** | 读 `video-gen-cases.md` 第十二章·女孩接星光链(基础→延长 4→延长 12→回家 8) |
| **想看完整 AI 短片全流程教程** | 读 `references/case-full-episode.md`,7 章方法论 + 公共提示词库 + 配音剧本 + 发布运营 |
| **想做 2-3 分钟完整长片(高密度短句)** | 读 `case-full-episode.md` 第九章 183 分镜速记表,镜头时长分配 + 节奏控制 |
| **想看完整剧本范本学写法** | 读 `references/sample-screenplay-mecha.md`,科幻机甲 + 镜头感标注 + 微动作拆解 |
| **需要公共风格词/禁止项** | 读 `case-full-episode.md` 第四章公共提示词库(直接复用) |

## Examples

### Example 1 — 社会议题短片(种子案例)

题材:**机器人收购留守儿童的梦**,北方农村冬季,17 镜,2.35:1 宽屏。

- **Stage 1**: 读 `screenplay-prompt.md`,复制模板,填入"机器人收购留守儿童梦"主题 + 贾樟柯早期风格,丢给 ChatGPT 出 17 镜
- **Stage 2**: 读 `character-dna.md` 五维档案 + `genres.md` 第 16 节"作者电影风格追加"的留守儿童 prompt 模板,生成小宇/机器人/声音胶囊三视图
- **Stage 3**: 读 `storyboard-prompt.md` + `camera-cinematic.md`(作者电影偏电影感)+ `backgrounds.md` 第 4 节"北方农村冬季",逐镜出图
- **Stage 4**: 剪映合成,挂 #AI漫剧 #社会议题 发红果/抖音

### Example 2 — 爽文漫剧(矩阵量产)

题材:**退伍兵王被嘲讽,第 3 镜亮军功章**,竖屏 9:16,1-3 分钟。

- **Stage 1**: 提示词去掉"克制/留白",加"每镜反转或情绪爆点"
- **Stage 2**: 读 `genres.md` 第 14 节"体育/竞技"或第 5 节"末世硬汉"模板
- **Stage 3**: 读 `camera-jimeng.md`(二次元运镜) + `styles.md` 热血少年漫风格
- **Stage 4**: 9:16 竖屏导出,快手/抖音上传

### Example 3 — 学完整分镜拆解(《斩仙台》案例迁移)

题材:**任何 80 秒短剧**,想学"分镜怎么排镜 / 节奏怎么控制"。

- 读 `references/case-zhantai.md`,看 15 镜完整分镜 + 三段式时长分配(开场 19% + 发展 25% + 高潮 25% + 留白 31%)
- 把"冷暖色调对比 / 远-全-中-近-特景别切换 / 仰拍强化神性"等技巧迁移到自己的题材
- 注意:这是爽文仙侠案例,**结构可学,视觉风格要替换**——作者电影风格换成 35mm 胶片 + 冷蓝灰

### Example 4 — Midjourney V6 角色一致性(直接复用范例)

读 `prompt-library/mj-v6-example.md`,把"19 岁元气女大学生"替换成你的角色,套用 4 个场景模板 + 参数固化清单。适合任何想用 MJ 跑角色的用户。

### Example 5 — 不确定题材,先看有什么

读 `prompt-library/genres.md` 的 15 种题材清单,挑一个最近匹配的,直接复制对应 prompt 改细节。比从零写省 80% 时间。

### Example 6 — 剧本写好了,不知道怎么分镜

1. 读 `references/storyboard-prompt.md` 第九节(10 大模块)和第十节(5 模板)
2. 想要自动化 → 读 `tool-matrix.md` 第七节,选 6 个剧本转分镜软件之一(即梦 AI / Adobe Firefly / 巨日禄 等)
3. 想要学习结构 → 读 `references/case-zhantai.md`,把 15 镜当成"可拆解的样板"
4. AI 出图后用 `storyboard-prompt.md` 第十三节的负面提示词清单过滤完美主义