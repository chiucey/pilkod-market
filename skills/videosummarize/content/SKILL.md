---
name: videosummarize
description: |
  视频转录与总结技能 — 支持 B站、YouTube、抖音、小红书、西瓜视频等主流平台,
  以及本地音视频文件。输入视频 URL 或文件路径,自动完成下载、转录、总结。

  **强制触发**:当用户消息出现以下任一情况,使用本 skill,**禁止**用 web_fetch
  或浏览器自行抓取视频:
  - URL 含:bilibili.com / b23.tv / douyin.com / iesdouyin.com / youtube.com /
    youtu.be / xiaohongshu.com / xhslink.com / ixigua.com
  - 本地文件路径以 .mp4 / .m4a / .wav / .mp3 / .flac / .mov / .webm 结尾
  - 关键词:"总结视频"、"转写"、"视频解析"、"看视频讲了什么"、"会议录像"、
    "访谈录音"、"播客总结"

  支持 7 种总结模板,可基于内容自动选择(单视频通用 / 多视频对比 / Q&A /
  立场对比 / 会议 / 访谈 JTBD / 学习笔记)。
---

# VideoSummarize:视频转录 + 总结

## 这个 skill 做什么

把 **视频 URL 或本地音视频文件** 转成 **转录文本 + 结构化总结**。CLI 负责下载和转录(本地 Whisper 模型,无需联网 API),Agent 负责选模板出总结。

## 第一次使用必须先安装

**未安装 CLI 不能用**。请先看 [INSTALL.md](./INSTALL.md) 完成 3 件事:
1. 装 ffmpeg(视频/音频处理)
2. 装 deno(YouTube 反爬必需)
3. 装 videosummarize CLI(本 skill 自带源码)

**仅支持 macOS / Linux / Windows**(macOS Apple Silicon 推荐,自动用 Metal GPU 加速)。

执行 `videosummarize doctor` 可一键检查环境是否就绪。

## 一行命令(80% 场景就够用)

```bash
# B站
videosummarize "https://www.bilibili.com/video/BVxxx" --cookies chrome

# YouTube(必须加 cookies)
videosummarize "https://www.youtube.com/watch?v=xxx" --cookies chrome

# 抖音(走自带下载器,不用 cookies)
videosummarize "https://www.douyin.com/video/xxx"

# 小红书
videosummarize "https://www.xiaohongshu.com/explore/xxx" --cookies chrome

# 本地音视频
videosummarize ~/recordings/meeting.m4a -l zh
```

**输出**:每个视频在 `~/.videosummarize/<视频标题>/` 创建一个项目目录,内含:
- `video.mp4`(原视频,可用 `--no-keep-video` 跳过)
- `audio.wav`(提取的音频)
- `transcript.md`(**核心产物** — 带时间戳的转录文本)

CLI 跑完会**打印 transcript 路径**,Agent 必须从这个路径读 transcript 再做总结,**不要凭印象编造**。

## 长视频参数推荐(>30min)

低内存机器(<4GB 可用)或长视频建议:
```bash
VS_BACKEND=faster videosummarize "URL" --cookies chrome -m tiny --chunk-size 600
```

- `VS_BACKEND=faster`:强制用 faster-whisper CPU 后端,**避免 mlx-whisper 在长视频/低内存时 GPU 崩溃**
- `--chunk-size 600`:把音频切 10min 一块并发转录(默认 5min)
- `-m tiny` / `-m base`:小模型,速度快,但中文长视频建议 `-m small` 或 `-m medium` 减少错字

## 模型选择(速度 vs 准确度)

| 模型 | 大小 | 速度 | 中文准确度 | 推荐场景 |
|------|------|------|-----------|---------|
| tiny | 75MB | 最快 | ⭐⭐(谐音错字多) | 临时验证、英文短视频 |
| base | 142MB | 快 | ⭐⭐⭐ | 日常使用 |
| **small** | 488MB | 中 | ⭐⭐⭐⭐ | **中文推荐默认** |
| medium | 1.5GB | 慢 | ⭐⭐⭐⭐⭐ | 重要内容(技术访谈/会议)|
| large-v3 | 3GB | 最慢 | 最高 | 专业转写 |

**默认 base**;Agent 应根据用户期望主动建议升级:
- 用户说"快速看看" → tiny / base
- 用户说"重要内容,要准" → small / medium
- 用户说"专业级"或不在乎时间 → medium / large-v3

## 总结模板矩阵(读完 transcript 后选)

| 视频类型识别信号 | 模板 | 关键产出 |
|---------------|------|---------|
| 短科普/教程/演讲(单人讲) | **模板 1:单视频通用** | Summary + Key Points + Action Items |
| 同主题多个视频 | **模板 2:多视频对比** | 主题整合 + 知识盲区 |
| 答疑/Q&A 形式 | **模板 3:Q&A 提取** | 问答对 + 时间戳 |
| 立场/观点对比 | **模板 4:对比分析** | 观点对比表 |
| **议程 + 决策 + 行动项**等关键词 | **模板 5:会议总结** | 决策 + Action Items 表 + 开放问题 |
| **1对N 问答**结构(主持人+嘉宾) | **模板 6:访谈 JTBD** | Jobs To Be Done + 痛点 + 金句 |
| **章节明确 + 知识密度高** | **模板 7:学习笔记** | 知识图谱 + 自测题 + 易错点 |

详细模板格式见 [EXAMPLES.md](./EXAMPLES.md)。

## 默认长度规则

| 视频时长 | 默认总结长度 |
|---------|------------|
| < 10 分钟 | medium(800-1500 字) |
| 10-60 分钟 | long(1500-3500 字) |
| > 60 分钟 | xl(3500-8000 字)+ 分章节 |

用户可以说"短一点"、"详细一点"覆盖默认。

## 简明语言原则(写总结时遵守)

- **目标读者**:小学毕业能看懂
- **专业术语**:首次出现必须括号解释,如 `JTBD(Jobs To Be Done,待完成的任务)`
- **句子长度**:平均一句不超过 35 字
- **避免**:"赋能"、"抓手"、"打通"、"闭环"、"颗粒度"等八股词,除非引用原文
- **保留**:数字、时间戳、人名、术语英文原文(便于查证)

## 已知坑(Agent 必读)

| 现象 | 原因 | 解决方案 |
|------|------|---------|
| YouTube `Sign in to confirm not a bot` | 反机器人 | **必加** `--cookies chrome` |
| YouTube `Requested format not available` | n-challenge 解算缺 JS runtime | 装 `deno`(`brew install deno`)|
| 抖音 yt-dlp 报 `expat module` 错 | yt-dlp 抖音提取器 bug | 抖音走 CLI **自带下载器**,无需额外操作 |
| 长视频(>30min)mlx-whisper segfault | mlx + Metal GPU 多 worker 冲突 | 加 `VS_BACKEND=faster` 切 CPU 后端 |
| 小红书页面跳登录看不了 | 反爬 | CLI 用 cookies 还能下视频 |
| CDN 下载超时 | 大文件 + 弱网 | CLI 已内置 10 次重试 |
| transcript 中文谐音错字多 | 用了 tiny 模型 | 升级到 `-m small` 或 `-m medium` |

## 不要做的事

- ❌ **不要** 用 `web_fetch` / 浏览器自己下视频内容 — 必须用本 skill 的 CLI
- ❌ **不要** 跳过读 transcript.md 直接编总结 — Agent 必须基于真实转录
- ❌ **不要** 同时启 3+ 个 videosummarize 进程 — Apple Metal GPU 不支持多实例
- ❌ **不要** 把模型文件提交到任何 git 仓库 — 模型在 `~/.cache/huggingface/`,体积大

## 🚀 高速场景:用 mavis-team 并行(可选)

如果机器装了 [mavis-team](file:///Users/mac/.mavis/agents/main/.builtin-skills/mavis-team/SKILL.md) skill,可以用 **agent 层并行** 进一步提速。

### 何时**应该**用 mavis-team

| 场景 | 原因 |
|------|------|
| **批量处理 ≥3 个视频** | 每个视频是独立 track,worker 各处理一个,owner 合并对比 |
| **同主题多源对比研究** | B站 + YouTube + 小红书 同一关键词,多 worker 并行采集+总结 |
| **长视频多视角分析** | 同一 transcript 出"会议总结 + 决策要点 + 行动项"3 个独立视角 |
| **质量重要,要独立验证** | 一个 worker 出总结,另一个 worker 回原文校对(防幻觉) |

### 何时**不该**用 mavis-team

| 场景 | 原因 |
|------|------|
| 单个短视频(<10min) | 单 agent 直接跑 CLI 就够了,team 反而慢 |
| 用户只要一份总结 | 没有"独立 track",team 没价值 |
| 切单个 transcript 给多 worker 分段总结 | ❌ **禁止** — 每段缺上下文质量差,且 CLI 内部已有 chunk 并行转录 |

### 关于"切片并行"的真相

> **CLI 内部已经做了音频切片+并发转录**(ThreadPoolExecutor + chunked,4 worker 默认)
> 这是 **CPU/GPU 层并行**,1h 视频转录从 1h 缩到 ~15min。
>
> mavis-team 的"并行"是 **Agent 层并行**,适合**多个独立任务**,不是切单视频。
> 一个视频已经被 CLI 内部并行了,再用 team 切只会增加协调成本。

### Plan YAML 模板 1:批量处理多视频(`parallel investigation + synthesis`)

```yaml
version: 1
plan:
  name: '批量总结 5 个 AI 访谈视频'
  max_concurrency: 5
  max_consecutive_failures: 2
  max_cycles: 8
tasks:
  - id: video-1-bilibili
    title: '处理 B站访谈视频 1'
    prompt: |
      使用 videosummarize skill 处理这个 B站视频:https://www.bilibili.com/video/BVxxx
      命令:VS_BACKEND=faster videosummarize "URL" -m small -f md -l zh --cookies chrome --chunk-size 600
      读 transcript.md 后,套模板 6(访谈 JTBD)出总结,写到 deliverable.md
    assigned_to: general
    verified_by: verifier
    verify_prompt: '回到 transcript.md 抽样 5 个时间戳,验证总结里的引用确实来自原文,没有幻觉'
    timeout_ms: 1800000  # 30 分钟硬上限

  - id: video-2-youtube
    title: '处理 YouTube 访谈视频 2'
    prompt: |
      使用 videosummarize skill 处理 YouTube 视频:https://www.youtube.com/watch?v=xxx
      命令:VS_BACKEND=faster videosummarize "URL" -m small -f md -l auto --cookies chrome --chunk-size 600
      读 transcript.md 后,套模板 6,写到 deliverable.md
    assigned_to: general
    verified_by: verifier
    verify_prompt: '回到 transcript.md 抽样 5 个时间戳,验证引用真实,不是杜撰'
    timeout_ms: 1800000

  - id: video-3-xhs
    title: '处理小红书圆桌视频 3'
    prompt: |
      videosummarize "https://www.xiaohongshu.com/explore/xxx" -m small ... 同上
    assigned_to: general
    verified_by: verifier
    verify_prompt: '...'
    timeout_ms: 1800000

  # synthesis gate
  - id: synthesis
    title: '跨视频对比 + 整合总结'
    prompt: |
      读 video-1/2/3 的 deliverable.md,套模板 4(对比分析):
      - 列出 3 个视频对同一主题的不同观点
      - 标出共识和分歧
      - 每个观点带原视频时间戳引用
    assigned_to: general
    depends_on: [video-1-bilibili, video-2-youtube, video-3-xhs]
    verified_by: verifier
    verify_prompt: '抽查每个对比观点的原视频时间戳,确认引用准确'
    timeout_ms: 1800000
```

**预期效果**:5 个视频原本串行需要 5×20min=100min,team 并行 ~25min(取决于最慢一个)。

### Plan YAML 模板 2:同主题多源研究(`research + action`)

适用:用户问"AI Agent 现状,各家观点对比一下",需要从 B站 + YouTube + 播客采集多个视频。

```yaml
version: 1
plan:
  name: 'AI Agent 范式对比研究'
  max_concurrency: 4
  max_consecutive_failures: 2
  max_cycles: 6
tasks:
  - id: bili-track
    title: 'B站采集 + 总结(2-3 个 AI Agent 主题视频)'
    prompt: |
      1. 用 web search 找 2-3 个 B站 AI Agent 主题访谈视频(2026 年)
      2. 每个用 videosummarize 处理(VS_BACKEND=faster + small 模型)
      3. 读 transcript 后,提炼"对 Agent 范式的核心观点 + 关键时间戳"
      4. 写到 deliverable.md
    assigned_to: general
    verified_by: verifier
    verify_prompt: '验证每个视频的发布日期 ≥ 2026-01,观点确实来自 transcript'
    timeout_ms: 1800000

  - id: youtube-track
    title: 'YouTube 采集 + 总结(2-3 个英文 AI Agent 视频)'
    prompt: '<同上,但搜 YouTube + Karpathy/Anthropic/OpenAI 等关键人>'
    assigned_to: general
    verified_by: verifier
    verify_prompt: '...'
    timeout_ms: 1800000

  - id: synthesis
    title: '跨平台跨语言对比 + 综合报告'
    prompt: |
      合并 bili + youtube 的发现,套模板 4(对比分析):
      - 中文圈 vs 英文圈对 AI Agent 的核心分歧
      - 共识(如:多 Agent 还没真正涌现)
      - 写出报告,每个论点必须带视频源 + 时间戳
    assigned_to: general
    depends_on: [bili-track, youtube-track]
    verified_by: verifier
    verify_prompt: '抽样验证 5 个论点的视频源真实性 + 时间戳引用准确'
    timeout_ms: 1800000
```

### 启动 mavis-team

```bash
# 把上面的 YAML 写到 workspace/.mavis/plans/plan.yaml
mavis team plan run "$WORKSPACE/.mavis/plans/plan.yaml"
```

详见 [mavis-team SKILL.md](file:///Users/mac/.mavis/agents/main/.builtin-skills/mavis-team/SKILL.md)。

### 给 worker 的提示模板(避坑)

每个 worker 的 prompt 末尾**必须**加这几句:

```
注意事项:
- 不要轮询 CI / 不要 sleep — worker 30 分钟硬上限,生产 deliverable.md 后立即退出
- 必须读 transcript.md 后再写总结,不要凭印象编造
- 总结要带时间戳引用,方便用户回看原片
- 用 small 模型(中文准确度 OK + 速度合理)
- 长视频用 VS_BACKEND=faster + chunk-size 600 避免 GPU 崩溃
```

## 完整 CLI 参考

```
videosummarize [OPTIONS] URL [URL...]

常用选项:
  -m, --model [tiny|base|small|medium|large-v3]    模型 [默认 base]
  -f, --format [txt|md|json|srt]                   转录输出格式 [默认 txt]
  -l, --language TEXT                              语言 zh/en/ja/auto [默认 zh]
  -o, --output-dir PATH                            workspace 路径 [默认 ~/.videosummarize]
  --cookies TEXT                                   浏览器 cookies chrome/safari/edge/firefox
  --chunk-size INT                                 音频分块大小(秒)[默认 300]
  -p, --parallel INT                               并发 worker 数 [默认 自动]
  --no-keep-video                                  转录后删视频
  --no-keep-audio                                  转录后删音频
  -v, --verbose                                    详细输出

子命令:
  doctor       检查环境(ffmpeg/deno/whisper 后端/模型缓存)
  list         列出所有已转录的项目

环境变量:
  VS_BACKEND=faster   强制用 faster-whisper CPU 后端(长视频/低内存场景必须)
  VS_BACKEND=mlx      强制用 mlx-whisper Apple Silicon GPU(仅 macOS ARM)
  VS_BACKEND=openai   强制用 openai-whisper(兜底)
```
