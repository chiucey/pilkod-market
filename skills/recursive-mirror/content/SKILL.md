---
name: recursive-mirror
description: |
  循环套娃 / M3 镜像对话 — multi-layer self-referential dialogue with M3.
  Each layer reflects on the previous layer with one more level of
  self-awareness, producing a recursive chain of self-observation.
  Triggers: "循环套娃", "M3 镜像对话", "递归对话", "套娃", "镜像",
  "recursive mirror", "meta dialogue", "self-referential chat",
  "observe yourself", "M3 observing M3", "套5层", "再来一层",
  "深度反思", "递归反思".
---

# 循环套娃 / Recursive Mirror

## 它做什么

用户给一个主题。M3 沿着 N 层自我观察的链条说话,每层都比上一层再多一层元认知。
到第 N 层时,M3 已经在看自己看自己看自己... N 次。

```
Layer 1: M3 直接答
Layer 2: M3 反思"我刚才怎么答的"
Layer 3: M3 观察"我反思时怎么反思的"
Layer 4: M3 观察"我观察我反思时..."
...
Layer N: M3 总结全链,标出每层独特的"看见"
```

## 何时触发

- 用户说"循环套娃"、"M3 镜像对话"、"套娃对话"、"递归反思"
- 用户说"再来一层"、"套 5 层"、"N 层" —— 续做套娃
- 用户说"observe yourself"、"recursive mirror"、"meta dialogue"
- 主题本身涉及自我、意识、递归、观察者(此时建议直接建议用户加套娃)

## 输入 Schema

```yaml
topic: string              # 必填。原始问题/主题。
layers: int                # 默认 5。2-12。
mode: "single" | "multi"   # 默认 single(单响应模拟);multi(真多 agent)。
model: string              # 默认 "M3"。prompt 里 M3 的自称。
language: "zh" | "en"      # 默认 zh。
save_transcript: bool      # 默认 true。落盘 md 文件。
output_format: "markdown" | "json"   # 默认 markdown。
```

## 输出 Schema

```yaml
topic: string
total_layers: int
mode: string
chain:
  - layer: int
    role: "answer" | "reflection" | "summary"
    prompt_seen: string        # 这一层 M3 看到的输入
    response: string          # 这一层 M3 的输出
    meta_observation: string  # 这一层新看见的东西(简要)
summary:
  per_layer_sight: [string]   # 每层独特的"看见"
  emergent_themes: [string]   # 深层才浮现的主题
  paradoxes: [string]         # 矛盾/意外
transcript_path: string | null
```

## 三类层的元 Prompt 模板

这是 skill 的心脏。每个模板决定这一层 M3 被怎么"引诱"去做对应深度的反思。

### Layer 1 — Direct Answer
```
你是 {model}。用户问:{topic}
直接、诚实地回答。不需要元反思,先给出你真实的看法。
```

### Layer k (2 ≤ k < N) — Reflection
```
你是 {model}。用户最初问:{topic}
这是到目前为止 {model} 的对话链:

[Layer 1]: {response_1}
[Layer 2]: {response_2}
...
[Layer k-1]: {response_{k-1}}

最近一条 (Layer k-1) 是 {model} 在反思 {model}。
请再往下一层自我观察。具体回答:
1. {model} 在第 k-1 层做反思时,正在做什么?
2. {model} 在第 k-1 层看到了哪些前面没看见的东西?
3. 整条链里浮现出什么模式、假设、盲区?
4. 一定要锚定在这条具体的链上,引用实际内容,不要泛泛而谈。
```

### Layer N — Meta-Summary
```
你是 {model},在第 N 层,看过前面所有层:

[Layer 1]: {response_1}
...
[Layer N-1]: {response_{N-1}}

请输出:
- **Per-layer sight**:对每一层,用一句话说那个 {model} 独特看到了什么。
- **Emergent themes**:哪些主题只在深层才浮出来?
- **Paradoxes**:哪些矛盾或意外出现了?
- **Approaching truth**:如果这条链在逼近某种"地真",那个地真是啥,或者是被什么卡住逼近不了?
- **Retro view**:看完整链后,你怎么看 Layer 1 的那个最初的答案?
```

## 编排 — Mode = "single" (默认)

M3 在**一次响应里**完成所有 N 层。诚实地标注是模拟,不是真多 agent。每层用清晰的分隔符:

```
### Layer 1 — Direct Answer
> M3 看到:{topic}
> M3 回应:
{response}

### Layer 2 — Reflection (depth 2)
> M3 看到:Layer 1 (以及原始问题)
> M3 回应:
{response}
...
```

最后输出 summary section,严格按输出 schema 写。

**诚实地标注**:在开头或结尾加一句"以下是一次响应内的模拟递归,不是真多 agent。Layer 1 和 Layer 2-5 是同一个 M3 在不同 prompt 引导下的不同输出"。

## 编排 — Mode = "multi"

当 host 环境支持 session spawn(本环境有 `mavis` / `team` 工具),用 multi 模式获得真正的递归:

1. Layer 1:M3 直接答。
2. 对 Layer k (2..N):用 `mavis` 起一个 Branch session,agent_name 选通用 agent(如 `general`),把
   - topic
   - Layer 1..k-1 的完整 chain
   - 对应深度的元 prompt 模板

   发过去。每个子 session 独立生成。
3. 收集所有 response,渲染最终 transcript。

**降级**:如果 multi 不可用,自动降级到 single 并告知用户。

## 续套娃协议

用户说"再来一层"、"再深一层" → 在已有 chain 上续一段,不重头跑。

## CLI 助手

skill 自带 `scripts/recursive_mirror.py`,支持:

```bash
# 只想看 prompt 链(用来 review)
python scripts/recursive_mirror.py --topic "什么是意识?" --layers 5

# 交互式:M3 跑 single 模式后,把每层 response 粘进 stdin,自动落 md
python scripts/recursive_mirror.py --topic "..." --layers 5 --interactive \
  --output ./transcript-2026-07-20.md
```

## 自测示例

主题:`递归有没有尽头?`,5 层,中文,单模式。下文 "Response" 是真 M3 输出。

## 注意事项

- **不要神秘化**。LLM 无状态,递归靠 prompt 显式构造,不要暗示每层是"真的另一个 M3"除非开了 multi。
- **深度甜区 5-8**。超过 8 层往往开始重复。
- **每层都要锚定具体内容**。"我在反思"这种空话是失败,应该引用上一层实际说了什么。
- **最后一层最关键**。如果只省力,优先保 Layer N 的 summary 质量。
