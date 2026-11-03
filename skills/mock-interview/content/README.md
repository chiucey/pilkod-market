# Real Mock Interview Agent
 
An AI interviewer that actually **looks up what this company asks ( & format )**, and **supports audio**. Audio is what makes pacing, filler words, and your longest pause analyzable. None of that is visible in text, and it's usually the most surprising part of the debrief.
 
It doesn't pull from a static question list. Tell it you're interviewing at BCG and it goes and reads BCG's own published practice cases and candidate write-ups, works out what this round really tests, and builds from that. Cases, product sense, metric diagnostics, technicals, not just behavioral.
 
Built mainly for  **consulting and PM interviews**
 
[中文](#中文说明) · [Quick start](#quick-start) · [What's different](#whats-different)
 
<!-- Drop a 30-second GIF here: it searches for real questions → asks → follows up → report. This is the screen that decides whether people star the repo. -->
<!-- ![demo](docs/demo.gif) -->
 
---
 
## What's different
 
Most AI interview practice has the same three problems: it asks generic questions off a static list, it dumps twenty of them at once, only supports text interaction.
 
Real interviews are nothing like that. **A McKinsey first round is a case** Amazon scores every question against a Leadership Principle. A PM loop has an entire round that's just "this metric dropped 20%...what now?" Practicing all three with the same generic question set is barely practicing at all.
 
So this skill does three things.
 
**1. It researches the actual loop first**
 
Given a company and a role, it searches for how that company really interviews and what candidates report being asked — careers pages, candidate write-ups, and the practice cases MBB firms publish themselves. Before starting, it tells you what it found: *"your loop is one behavioral round and one interviewer-led case, so I'm weighting it that way."*
 
If it can't find anything, it says so and falls back to the built-in banks. It won't invent a plausible-sounding process to cover the gap.
 
**2. Supports Audio. Asks one question at a time,and it probes**
 
No previews, no mid-interview coaching. Vague answers, team credit taken as personal credit, results with no numbers, all draw a follow-up. Roughly half of all answers do, which is the ratio that makes it feel real. The follow-up is where most people actually fall apart, and it's the part practice usually skips.

The audio analysis feature allows it to analyze your phrases like "umm", "er", etc. Better help with presentation and speaking skills!
 
**3. It scores honestly**
 
3 out of 5 is an average real candidate, not a bad one. Feedback that scores everyone a 4 is worthless — and leaves you blindsided on the day.
 
---
 
## Coverage
 
| Type | What it does |
|---|---|
| **Cases (consulting)** | Full case protocol, distinguishing interviewer-led (McKinsey) from candidate-led (BCG/Bain). Two built-in cases with complete data exhibits — data is released only when you ask for it, and bad arithmetic gets probed. |
| **Product sense** | Propose a solution before naming a user and a problem and it interrupts you. That's the most common way PM candidates fail. |
| **Metric diagnostics** | A metric drops 18%; data is released layer by layer to see whether you segment first or start guessing causes. |
| **Estimation** | Market sizing, scored on decomposition and sanity-checking rather than the number. |
| **Technical / finance** | System design, the three statements, DCF, and *"explain this thing from your resume in plain language"* — the highest-signal question there is. |
| **Behavioral** | STAR, with follow-up ladders (including Amazon LP mapping). |
 
No live coding — that needs a real editor and a compiler, and simulating it just builds false confidence.
 
---
 
## The debrief
 
When the interview ends, you get an HTML report with per-question scores across structure, specificity, impact, and role fit; what was missing, concretely; and **a rewritten answer built only from material you actually gave it**.
 
Missing numbers are marked `[your number here]` rather than invented. A fabricated metric is how people get caught in the real thing.
 
---
 
## Quick start
 
**1. Download**
 
```bash
git clone https://github.com/ameliapeng-gif/real-mock-interview-agent.git
```
 
Or click the green `Code` button → `Download ZIP` and unzip it.
 
**2. Install**
 
Drop the whole folder into your agent's skills directory:
 
| Agent | Where |
|---|---|
| **MiniMax Code** (recommended) | Settings → Skills |
| Claude Code | `~/.claude/skills/` |
| Claude Desktop / Cowork | Settings → Capabilities → Skills |
| Anything else that reads `SKILL.md` | See its docs |
 
> Why MiniMax Code is listed first: this skill leans on two capabilities — **web research** to find the real questions, and **spoken questions** via TTS. Any agent that reads `SKILL.md` and can browse will run the core flow, but **voice mode calls MiniMax's API**, so that part only works there. Everything else is portable.
 
**3. Start**
 
```
Run a mock BCG summer internship interview using my resume.
```
 
Drag in your resume and name the company and role. It researches first, then asks how many questions you want and whether you want voice.
 
---
 
## Voice mode
 
Typing hides your problems — you don't say "um, so, like" on a keyboard. Voice is a lot more honest.
 
The full loop: **it asks out loud → you answer out loud → it transcribes and scores what you actually said.**
 
```bash
cp .env.example .env
```
 
Add a MiniMax API key ([global](https://platform.minimax.io/) · [domestic](https://platform.minimaxi.com/)).
 
Two ways to answer:
 
- **Dictation** (default, zero setup) — press Fn twice on macOS, or the keyboard mic on your phone. Speak, and the text lands in chat.
- **Recording** (better signal) — `python scripts/record.py`, Enter to stop. Audio is what makes pacing, filler words, and your longest pause analyzable. None of that is visible in text, and it's usually the most surprising part of the debrief.
Without a key it falls back to text automatically.


---
 
## Privacy
 
- Your resume and answers go to whichever model you're already using, exactly as if you'd pasted them into a chat. This repo collects, uploads, and stores nothing.
- `.env` is gitignored. **If you fork this, double-check your API key isn't committed** — keys leaked to GitHub get scraped within minutes.
- The sample resume in this repo is fictional.
---
 
## Contributing
 
The three most valuable PRs: **real questions from more industries**, **harsher follow-ups**, and **corrections to how specific companies actually interview**. Just interviewed somewhere? Come back and add what you got asked — that's where this repo's value lives.
 
---
 
## 中文说明
 
一个**先上网查这家公司真实面试题**、然后**会追问**的 AI 面试官。包括语音面试，可以分析你的停顿，口头禅，等。
 
不是从固定题库里抽题——你说要面 BCG，它去把 BCG 官网的 practice case 和候选人回忆帖翻一遍，弄清楚这一轮到底考什么，再开始问。case、product sense、metric 诊断、技术题，不是只有 behavioral。
 
**专为咨询和产品岗**做的——这两类是最难自己练的。
 
### 它和别的有什么不一样
 
市面上的 AI 模拟面试基本都是同一个毛病：一口气甩你二十道通用题，你答什么它都说"很好的回答！"，然后结束。
 
而真实面试根本不长这样。**麦肯锡一面是 case 不是聊天**，Amazon 每道题都对着一条 Leadership Principle 打分，PM 有一整轮就问"这个指标掉了 20%，你怎么办"。三件事都不一样，用同一套通用题去练，等于没练。
 
**1. 先查这一轮到底考什么**
 
拿到公司和岗位后，它会去搜这家公司的真实面试流程和被报告过的题目——公司官网的招聘页、候选人回忆帖、以及 MBB 自己公开发布的 practice case。开始之前它会告诉你查到了什么："你这一轮是一个 behavioral + 一个面试官主导的 case，我按这个配比来。"
 
查不到就直说，退回内置题库。它不会编一个听起来很像的流程糊弄你。
 
**2. 一次一题，而且会追问**
 
不提前剧透，不中途给提示。回答含糊、把团队功劳说成自己的、没有结果和数字——它会追着问。大约一半的回答会被追问，这个比例是照着真实面试来的。
 
追问才是大多数人当场崩掉的地方，也是练习时最容易被跳过的地方。
 
**3. 打分不放水**
 
3 分 = 真实面试中的平均水平，不是差。给所有人打 4 分的反馈等于没有反馈。
 
### 覆盖的题型
 
| 类型 | 内容 |
|---|---|
| **Case（咨询）** | 完整 case 协议，区分麦肯锡式（面试官主导）和 BCG/Bain 式（候选人主导）。内置两个带完整数据表的 case，数据要你开口问才给，算错了会被追。 |
| **Product sense** | 你没说清用户和问题就直接给方案，它会当场打断——这是 PM 面最常见的死法。 |
| **Metric 诊断** | 指标掉了 18%，逐层给你数据，看你是先做维度拆分还是上来就猜原因。 |
| **Estimation** | 市场估算，不看数字对不对，看拆解和有没有 sanity check。 |
| **技术 / 金融** | 系统设计、三张报表、DCF、以及"用大白话解释你简历上这个东西"——最见真章的一道题。 |
| **Behavioral** | STAR，带追问阶梯（含 Amazon LP 映射）。 |
 
不做实时 coding——那需要编辑器和编译器，模拟出来只会给你虚假的信心。
 
### 复盘报告
 
面完给你一份 HTML 报告：每题四个维度打分、缺了什么、以及**只用你自己说过的素材改写的更强版本**。
 
缺数字的地方标成 `[your number here]` 让你自己填，它不会替你编——编出来的漂亮答案在真面试里会把你害死。
 
### 快速开始
 
```bash
git clone https://github.com/ameliapeng-gif/real-mock-interview-agent.git
```
 
不用命令行的话，点右上角绿色 `Code` → `Download ZIP`，解压即可。
 
然后把整个文件夹放进你的 Agent 的 skills 目录：
 
| Agent | 位置 |
|---|---|
| **MiniMax Code**（推荐） | 设置 → Skills |
| Claude Code | `~/.claude/skills/` |
| Claude 桌面版 / Cowork | 设置 → Capabilities → Skills |
| 其他支持 `SKILL.md` 的 | 见各自文档 |
 
装好之后说一句：
 
```
用我这份简历，模拟一轮 BCG 的暑期实习面试
```
 
把简历拖进去，说清楚公司和岗位。它会先去查，然后问你要几道题、要不要语音。
 
> 为什么把 MiniMax Code 放第一：这个 skill 依赖两个能力——**联网查真题**和**语音提问**。任何能读 `SKILL.md` 且能联网的 Agent 都能跑核心流程，但**语音调的是 MiniMax 的接口**，只有在那儿能用。其余部分都是通用的。
 
### 语音面试
 
文字练习会藏住你的问题——你在键盘上不会说"嗯…这个…"。开语音会诚实很多。
 
完整闭环是：**它出声问 → 你出声答 → 它转写并按你实际说出口的内容打分。**
 
```bash
cp .env.example .env
```
 
在 `.env` 里填 MiniMax API key（[国内](https://platform.minimaxi.com/) · [海外](https://platform.minimax.io/)）。
 
回答有两种方式：
 
- **系统听写**（默认，零配置）：Mac 连按两下 Fn，手机按键盘上的话筒，说完文字就进对话框了
- **录音**（信号更好）：`python scripts/record.py`，回车结束。有音频才能分析你的语速、口头禅和最长的一次卡壳——这几项在文字里完全看不出来，而且往往是最扎心的
没配 key 也能用，自动退回文字模式。
 
### 隐私
 
- 你的简历和回答会作为对话内容发给你正在用的模型，和你平时直接粘贴给它是一样的。这个仓库不收集、不上传、不存储任何东西。
- `.env` 已经在 `.gitignore` 里。**如果你 fork 了这个仓库，提交前请再确认一次 API key 没有被 commit 进去**——key 泄露到 GitHub 会在几分钟内被爬走。
- 仓库里的示例简历是虚构的。
---
 
## License
 
MIT
 
<!-- If this project came out of a brand collaboration, add a disclosure line here, e.g.:
Built while testing MiniMax Code. Opinions are my own. -->
