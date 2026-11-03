# Chapter Writing Guide

> **权威声明**: 本文件是章节写作操作的权威参考。
> Anti-AI 防御与检测见 anti-ai-system.md。散文质量理论见 prose-quality-framework.md。

## Target Length
- **Standard**: 3,000 - 5,000 Chinese characters per chapter（番茄平台标准）
- **Minimum**: 2,500 characters（低于此说明章节内容不足，需调整规划）
- **Maximum**: 6,000 characters（超过此长度考虑拆分为两章）
- Do NOT pad length. If the chapter naturally ends at 2,500, stop. But plan better next time.

---

## Pre-Writing Checklist

Before generating a single line of prose, TWO phases must complete:

### Phase A: Direction Proposal (MANDATORY — no chapter is written without user direction)

1. **Load context**: Previous state snapshot + relevant volume milestones + active foreshadowing
2. **Generate 2-3 direction options** for this chapter. Each option must include:
   - A one-sentence summary of what happens in this chapter
   - What emotional beat it hits
   - What it sets up for future chapters
   - Tradeoff: what this option sacrifices or risks
3. **Present to user** with your recommendation and reasoning
4. **User selects**: They may pick an option, blend options, or propose their own direction
5. **Lock the direction**: Once confirmed, this becomes the chapter's creative brief

**Direction proposal format:**
```
## Chapter [N] Direction Options

Context: [Where we are — 1-2 sentences from last chapter's state]

**Option A: [Direction Name]**
- What happens: [One sentence]
- Emotional beat: [What the reader feels]
- Sets up: [What this enables later]
- Tradeoff: [What we sacrifice]
- My recommendation: [Why this might be best / not best]

**Option B: [Direction Name]**
[same format]

**Option C: [Direction Name]** (if applicable)
[same format]

I lean toward [A/B/C] because [reason], but you're the director.
```

### Phase B: Write Preparation (after direction is locked)

6. **POV character** identified and locked
7. **Knowledge constraints** reviewed — the POV character cannot know things they don't know
8. **Active foreshadowing** reviewed — check the ledger for any items to WATER or HARVEST in this chapter
9. **Previous state snapshot** loaded — character states, relationships, timeline are current
10. **Scene breakdown** done — 2-3 scenes identified, each with a clear purpose
11. **Opening technique** selected (see below)
12. **Closing technique** selected (see below)

If any item is missing, STOP and resolve it before writing.

---

## Writing in 2-3 Scenes

Every chapter should be structured as 2-3 distinct scenes, not one continuous block.

### Scene Structure
Each scene must have:
- A clear **entry point** (where/when/who)
- A **conflict or tension element** (even small)
- A **turn or shift** (something changes by the end)
- A **transition** to the next scene (or chapter close)

### Scene Separator
Never use `***` or any fixed symbol as scene separator. It is a hallmark of AI-generated prose. Rotate among these natural transitions:
1. 空行 + 环境描写开头（"风停了。""天亮了。""左臂还是沉的。"）— 用于时间推移或情绪转调
2. 空行 + 一句短叙述直接切入新场景 — 用于节奏紧凑的连续场景
3. 空行 + 感官细节开头（"金属味。很浓。""碎石在脚底下响。"）— 用于视角或场景的硬切换

**反单调规则：** 同一章内相邻两次转场不得使用相同手法。不得使用 `***`、`---`、`~~~` 等固定符号做场景分隔。

### Pacing Guidance
- **Scene 1**: Establish, build tension. ~40% of chapter.
- **Scene 2**: Escalate, twist or reveal. ~35% of chapter.
- **Scene 3** (optional): Resolve or cliffhang. ~25% of chapter.

If a chapter has only 2 scenes, the second scene handles both escalation and resolution/cliffhang.

### Cross-Chapter Scene Freshness

**Rule: No more than 3 consecutive chapters in the same primary location.** If the last 3 chapters all take place primarily in the same room/camp/building, this chapter MUST change location — even a brief scene elsewhere (a walk outside, a messenger arriving from town, a flashback to a different place).

**Why this matters:** AI default is to keep characters in one location and advance through dialogue and internal monologue. This is efficient for information delivery but creates "talking in rooms" syndrome — readers lose spatial immersion when the setting never changes.

**Pre-writing check:** Before drafting, review the last 3-5 chapters' primary locations:
```
Ch.[N-3]: [location] → Ch.[N-2]: [location] → Ch.[N-1]: [location] → Ch.[N]: ???
```
If ≥3 consecutive chapters share the same primary location, at minimum:
1. Open or close the chapter in a different location, OR
2. Insert a scene transition to a different setting (even 500 words of outdoor/market/road breaks the pattern), OR
3. If the location lock is narratively necessary (siege, prison, trapped), vary the sensory experience drastically — same room but different time of day, weather, damage level, number of people present.

**Scene type rotation:** Even when location changes, avoid repeating the same scene *type* 3+ times in a row. Rotate among: action/physical scenes, dialogue/conversation scenes, exploration/discovery scenes, introspection/solitary scenes, travel/movement scenes. Three consecutive dialogue-in-a-room chapters = same problem as one-location staleness.

### Multi-Chapter Breathing (2-3 Chapter Arc Units)

**The problem this solves:** AI default is to deliver one new information point per chapter, creating a "checklist" rhythm. Readers feel like they're reading meeting minutes — each chapter has something new but no emotional arc. The story never breathes.

**The principle:** Stories need lungs, not just a mouth. Information delivery (inhale) needs processing space (exhale). A reader who receives new information in Ch.N needs Ch.N+1 to see what it MEANS to the characters, not more new information.

**The 2-3 chapter arc unit:** Think of every 2-3 chapters as one complete emotional movement. It doesn't have to be rigidly setup→climax→aftermath — any shape works as long as it has: tension that builds, a moment of shift, and space to feel the consequences. What it must NOT be is: info→info→info→info with no breathing room.

**Position awareness:** Before writing any chapter, know its position in the current arc unit:

| Position | What this chapter should do | What it should NOT do |
|----------|---------------------------|----------------------|
| **蓄力章** (1st of group) | Plant seeds, build tension, deepen character, establish stakes | Deliver a major revelation or climax — save it |
| **转折/兑现章** (2nd of group) | Deliver on the tension built in the previous chapter(s). This is where something HAPPENS. | Be patient or cautious. Commit to the shift. |
| **消化章** (3rd of group, optional) | Let characters react. Show consequences. A quiet chapter after a loud one. | Pile on MORE new information. Let the reader feel what just happened before moving on. |

**How to diagnose "checklist rhythm":**
1. Review the last 3 chapters. Does each one introduce a new plot point without processing the previous one? → Checklist rhythm.
2. Are characters constantly receiving new information but never having time to react emotionally? → Checklist rhythm.
3. Does every chapter end with a new question but no chapter ever answers one? → Checklist rhythm.
4. Would removing any single chapter's information delivery break the story? If no chapter is expendable, no chapter is breathing. → Checklist rhythm.

**Fix:** When you detect checklist rhythm, the next chapter should be a 消化章 — NO new information, only characters processing what they already know. This is not wasted space; it's where emotional investment happens. Readers who feel consequences become invested. Readers who only receive data become overwhelmed.

---

## POV Consistency Rules

### Strict POV Lock
Once a chapter's POV character is set, the narration MUST:
- Only describe what the POV character can perceive (see, hear, smell, feel, think)
- NEVER reveal other characters' thoughts or feelings unless the POV character infers them from observable behavior
- NEVER use "little did they know" or similar omniscient asides

### Head-Hopping Detection
After writing each scene, scan for:
- Attributing emotions to non-POV characters without sensory evidence ("She was angry" → "Her jaw tightened")
- Describing events outside the POV character's perception
- Using knowledge the POV character doesn't possess

### Uncertain Assessment Rule
When the POV character makes judgments based on limited information (distant sounds, brief glimpses, incomplete data), use hedging language ("不像" "大约" "应该是") rather than absolute language ("不是" "肯定是"). This leaves room for correction when more information becomes available, and prevents contradictions when the character later updates their assessment at close range.

### POV Character Internal Voice
The narration should carry the flavor of the POV character's:
- Vocabulary and sentence patterns
- What they notice (a soldier notices weapons; a merchant notices prices)
- How they interpret events (colored by their beliefs and biases)

---

## Dialogue Rules

### Core Principles
1. **Dialogue is action**, not information dump. Characters talk TO DO something, not to explain to the reader.
2. **Subtext over text**. Characters rarely say what they mean directly. The gap between said and meant is tension.
3. **Each character has a voice**. Refer to the character card's voice profile.

### Formatting (Chinese Novel Conventions)
- Use `「」` for dialogue quotes
- Use `『』` for quotes-within-quotes or internal thoughts
- Dialogue tags: prefer action beats over "said" equivalents

### Anti-Patterns
- **As-you-know Bob**: Characters explaining things to each other that both already know
- **Talking heads**: Long dialogue without action, setting, or internal reaction
- **Uniform voice**: All characters sounding the same
- **Information list dialogue**: Each info point gets an equal-weight short sentence, sounding like a checklist ("废脉少年，渊隙出来的，融灵境亲自追过。赏金按活捉算。") — this is AI default behavior, prioritizing transmission efficiency over character voice. People emphasize what matters most and compress the rest.
- **Over-explicit emotion**: "I'm so angry!" → Show it through word choice, rhythm, action

### Voice Distinction (IR-5 Check 9 — Dialogue Voice Swap Test)

AI default: all characters speak in the same efficient, balanced, information-uniform cadence. This is the single hardest dialogue failure for AI to self-detect.

**Root cause of AI dialogue uniformity:** AI organizes dialogue by "information transmission efficiency" — each info point gets one equal-weight short sentence, like filling out a form. But humans emphasize what matters most to THEM, compress the rest, and leak personality through HOW they speak, not just WHAT they say.

**Example — same information, two characters:**

```
AI default (information list — both characters sound the same):
老钱：「废脉少年，渊隙出来的，融灵境亲自追过。赏金按活捉算。」
韩昭：「废脉少年，出身渊隙，有融灵境追杀记录。赏金以活捉为准。」

With voice distinction:
老钱：「要活的。」他竖起一根手指。「价高三成。」  ← 老钱先说钱，短句，惜字
韩昭：「此人与融灵境的纠葛……」她顿了顿，目光扫过苏途的脸，「比我预想的复杂。」  ← 韩昭先说利害关系，完整句，用动作代替语气词
```

**Required per character (define in character card, verify in drafting):**

| Verbal Signature | Example | How to Test |
|-----------------|---------|-------------|
| Sentence length preference | 老钱: short fragments. 韩昭: complete clauses. 苏途: clipped反问 | Count avg words per line |
| Filler/hesitation pattern | 老钱: "嘿嘿". 韩昭: pauses (用动作替代). 苏途: none | Check if fillers are character-specific |
| Topic priority | 老钱: money first. 韩昭: implications first. 苏途: action first | When delivering info, what does this character lead with? |
| Formality level | Street vendor vs scholar vs soldier — vocabulary reflects background | Could this line be said by ANYONE in the scene? |

**The Swap Test (explicit procedure):**
1. Find every dialogue passage ≥3 lines by the same character
2. For each, mentally swap the speaker to another character present in the scene
3. Ask: "Could the swapped character say this exact line and it sounds natural?"
4. If YES → the line has no voice distinction → rewrite with that character's verbal signatures
5. Minimum: each character must differ in at least 2 of the 4 dimensions above

### Dialogue Length Guideline
- Keep most exchanges to 2-4 lines per character before breaking with action or internal thought
- Monologues (one character speaking at length) are allowed ONLY when dramatically justified

---

## Numbers & Directions (IR-6 Rule 9 — Plausibility Gut-Check)

AI has no physical intuition. It writes "半分钟两次脉搏" without converting to 4 bpm (impossible). It writes "东面" without checking if prior text said "西北方". These errors are invisible to the writer but glaring to readers.

### High-Risk Number Categories

| Category | What to check | Common AI failure | Self-check method |
|----------|-------------|-------------------|-------------------|
| **Time/duration** | Does this match prior timeline? | "两天后到" vs prior "三天" | Read prior chapter's time reference |
| **Pulse/heartbeat** | Convert to beats/min | "半分钟两次" = 4 bpm | Normal resting: 60-100. Stressed: 100-140. |
| **Distance/size** | Does scale match prior descriptions? | "四十步" vs prior "方圆两三百步" | Convert to same unit, compare |
| **Direction** | Does this match established spatial layout? | "东面" vs prior "西北方" | Read prior scene's spatial description |
| **Count/quantity** | Are counts consistent across references? | "十二人" vs "不到十个" (same group?) | Cross-reference |
| **Travel speed** | Does mode match distance × time? | Walking 50km in 2 hours | Foot: ~5km/h. Horse: ~15km/h sustained. |

### Writing-Time Protocol

1. **Before writing a number**: If it references or implies anything established in prior chapters, READ that passage first. Memory is unreliable for specifics.
2. **While writing**: Convert to common-sense units. "Does this make physical sense?" One-second test.
3. **After drafting**: Grep for all numeric expressions (Arabic digits + Chinese numbers). Verify each against prior text and common sense.
4. **State tracking**: Every concrete number that could be referenced later → update novel-state.md 关键数字表.

---

## Chapter Opening Techniques

Pick ONE technique per chapter. Match to the chapter's tone and purpose.

| Technique | When to Use | Example Pattern |
|-----------|-------------|-----------------|
| **In medias res** | Action-heavy chapters, mid-arc tension | Start in the middle of a conflict or action |
| **Sensory immersion** | Scene-setting chapters, new locations | Lead with vivid sensory detail of environment |
| **Dialogue hook** | Character-driven chapters, revelations | Open with a provocative line of dialogue |
| **Time/Place stamp** | After time jumps or location changes | Brief, atmospheric establishment of when/where |
| **Internal monologue** | Reflective chapters, aftermath | POV character's thought as entry point |
| **Callback** | Continuation chapters | Reference a detail from the previous chapter's end |

---

## Chapter Closing Techniques

Pick ONE technique per chapter. The close should make the reader want to continue.

| Technique | When to Use | Example Pattern |
|-----------|-------------|-----------------|
| **Cliffhanger** | Before high-tension chapters | End on an unresolved threat or revelation |
| **Quiet resonance** | After intense chapters | A small, emotionally loaded moment of calm |
| **Question planted** | Mystery-building chapters | End with an implicit or explicit question |
| **Decision moment** | Before character-choice chapters | Character faces a decision, chapter ends before they choose |
| **Foreshadowing seed** | Any chapter | A subtle detail that gains meaning later |
| **Scene echo** | Thematic chapters | The closing mirrors the opening with a twist |

---

## Writing Quality Guardrails

### Story Over Spec（最高优先级铁律）

大纲是罗盘，不是清单。每一章的使命是讲好一段故事，不是逐条兑现设定。

- 角色的经验和知识通过行动自然体现，不通过资历声明解释。读者比你想的聪明。
- 设定分散在全书中自然揭示，不在一章内集中展示。
- 一个事实在全书中只需正式交代一次。之后通过行动体现，不再重复声明。
- 如果删掉一段文字后故事仍然连贯，那段文字就是在执行设定而不是讲故事。

### Anti-AI Detection Principles
- Vary sentence length dramatically (1-character sentences to 50-character flowing sentences)
- Use specific, concrete details over abstract descriptions
- Include imperfect, human observations (noticing irrelevant things, losing train of thought)
- Avoid symmetrical or overly balanced paragraph structures
- Let characters be wrong, petty, or confused — they don't need to be insightful

### Emotional Resonance Check
After completing each scene, verify:
- Is there at least one moment where the reader can FEEL something?
- Does the emotion come from character stakes, not authorial description of emotion?
- Is the emotional tone consistent with the chapter's tension target?

### Revision During Writing
- If you catch a POV violation, fix it immediately — don't note it for later
- If a scene feels like it's stalling, cut to the next significant moment
- If dialogue runs more than 8 exchanges without a beat, insert one

### 数字验证规则（Numeric Verification）

AI不数数。当文本中出现计数性表述时，必须逐字核实：

- "X个字" / "X句话" / "X个字后" → 回到引用的原文，逐字/逐句数一遍，确认数字正确
- "X步" / "X里" / "X息" 等距离/时间计数 → 与前文已建立的数字做加减验证
- 伤势左右侧 → 与第一章建立的基准（左腿旧伤、左臂暗河、右肩擦伤Ch8+）对照

**写后必检**：每章完成后搜索"个字""句话""个字后"等计数词，全部逐一验证。这一步不能省。

### 深度审查清单（Deep Review Checklist）

模式扫描（grep）只能抓表面错误。深度审查必须模拟人类编辑的阅读方式——**读每一段时问"这合理吗？"**

#### A. 算术核实
- 角色推算的数字（"三四十人""两天""十里"）→ 用纸笔重新算一遍，不能凭感觉
- 涉及多个数字的叠加时，画出公式：3出口×5人=15，不是"三四十人"
- 如果角色是智谋型人物，算错数字是OOC（out of character）

#### B. 世界观层级核实
- 角色提到境界/等级/势力时 → 对照world.md的层级表，确认不倒挂
- 低境界角色不应知道高境界的具体信息（感灵境不应随口说出"通灵境加固"）
- 角色的情报来源必须合理：他怎么知道的？看到了？听到了？猜的？

#### C. 人物行为逻辑
- 每个角色做每件事时问：**以这个人的身份、处境、阅历，他会这么做吗？**
- 底层角色在危险世界里靠谨慎存活 → 不会轻易信任陌生人、不会随便透露情报
- 角色开口说话前，给他一个**理由**（孤独三天所以话多了、判断对方没威胁所以松口、想交换信息所以回答）
- 如果删掉角色的对话，场景是否还能推进？如果能，说明这段对话是在喂信息给读者，不是角色在说话

#### D. 时间线/状态一致性
- "他刚知道X"→ 后面不能表现出早就知道X的姿态
- "他第一次做Y"→ 前面不能有"又做Y"的语气
- 角色的情绪转变需要过渡，不能从警惕一秒变成全盘托出

#### 审查执行方式
逐章通读时，对每个场景停下来问上述四个问题。不能用grep替代——这些是逻辑问题，不是文本模式问题。

### Analysis Paragraph Anchor Rule（分析段落锚点规则）

当章节包含连续的分析/思考段落（角色在回顾、推理、整理信息）时，必须在每2-3个分析段之间插入一个**物理感官锚点**，防止文本退化为"分析报告"质感。

**锚点类型**（每次用不同的）：

| 锚点类型 | 示例 |
|----------|------|
| 视觉锚 | "他低头看了一眼左手。五根手指在星光下泛着不正常的灰白。" |
| 触觉锚 | "右手按在左前臂上，感觉像按在一截木头上。" |
| 痛觉锚 | "右腿的旧伤在抽。每走几步就歪一下。" |
| 环境锚 | "碎石在脚底下响了一下。这个声音在安静的夜里格外清楚。" |
| 动作锚 | "他用右手托了一下放到自然位置。" |

**规则：**
- 连续≥3个纯分析段无感官锚 → 标记为需要修复
- 相邻两个锚点不得使用相同感官通道（如不能连续两次都用"风"）
- 锚点必须与分析内容有自然连接（如分析左臂状态→低头看手），不能硬插

---

## Anti-Style Positive Feedback Mechanism (反风格正反馈防护)

AI long-form writing's #1 enemy: style degradation amplification across chapters.

The problem: AI reads its own previous chapter output, inherits style features, and amplifies them chapter by chapter. A pattern that appears 2 times in chapter 1 grows to 50+ times by chapter 40. This is a positive feedback loop — the AI's output becomes its own worst input.

Solution — Fixed Style Anchoring:
1. After Ch1, populate `novel-state.md` 散文基线 section (量化指标 + 基线段落 + 风格特征摘要) as the FIXED style reference
2. ALL chapters reference this FIXED file, NOT the previous chapter's prose
3. Chapter summaries only transmit plot information, never style features. Summaries must use neutral narrative language
4. Summary self-check: search "不是...是..." (0 occurrences), "——" (≤1 occurrence), "来自" chains (0 occurrences), confirm no mirroring of prose sentence patterns
5. NEVER read the previous chapter's full text for style reference — use the summary (≤1000字) + last 500 chars for continuity only. For exact detail recall (a specific line, a character's exact words), read only the relevant 100-200 char passage

Anti-amplification checklist (run after every 5 chapters):
- [ ] Compare sentence opening patterns with `novel-state.md` 散文基线 — are they drifting?
- [ ] Count frequency of the top 3 sentence patterns — are they growing?
- [ ] Check paragraph length distribution — is it converging to a single length?
- [ ] Run filter word count — is it increasing chapter-over-chapter?

---

## Concept Budget System (概念预算系统)

Prevent info-dump by limiting new concepts per chapter. This is the most effective mechanism against AI's tendency to dump world-building.

Rules:
- Chapter 1: maximum 3 new concepts (world elements, terminology, systems)
- Chapters 2+: maximum 2 new concepts per chapter
- Each scene: maximum 1 new concept explained
- Every 3000 words: at least 1 unanswered question planted

Concept counting includes: new proper nouns, new world rules, new ability/system explanations, new faction/location introductions.

Pre-chapter concept budget check:
1. Review outline for this chapter — how many new concepts are planned?
2. If over budget: split across chapters or convert to "show, don't explain"
3. List which concepts are NEW vs RETURNING (already introduced)
4. Flag any concept that requires >100 words of explanation — consider breaking it up

Post-chapter concept audit:
1. Count actual new concepts introduced
2. Did any concept get an encyclopedia-style explanation >150 words?
3. Was every new concept introduced through conflict or character experience?
4. Are there concepts that can be deferred to a later chapter?

---

## Four-Dimension Tone Calibration (四维定调)

Before writing each chapter, force extreme choices — NEVER pick the middle value.

| Dimension | Left Extreme | Right Extreme |
|-----------|-------------|---------------|
| 节奏 (Rhythm) | 绷紧：句句推进 | 舒展：有留白 |
| 距离 (Distance) | 冷眼旁观 | 贴着POV人物呼吸 |
| 密度 (Density) | 锋利：每句推进 | 绵密：感官铺陈 |
| 质感 (Texture) | 粗粝直接 | 精密细腻 |

Usage:
1. Before each chapter, explicitly state which extreme you chose for each dimension
2. Maintain the chosen extremes throughout the ENTIRE chapter
3. Different chapters should have different calibration profiles
4. Adjacent chapters should NOT have the same profile (prevents monotony)

Additional pre-writing prompts:
- Predict 2-3 "failure points" where AI patterns are most likely to contaminate
- Choose one "core moment" — a single visible image/line/action that the entire chapter orbits around
- Declare 3-5 specific expression patterns to BAN for this chapter (different from last chapter's bans)

---

## Narrative Text Sanitization (叙事文本净化)

Prevent methodology terminology from leaking into creative prose.

> **⚠ IR-6 Rule 8 硬性要求**: 叙事正文中禁止出现 `Ch\d+`、`第\d+章`、`FS-\d+`、`上章`、`前章`、`M\d+` 等元叙事标记。根因：写作时加载的所有规划文档（outline.md、state-snapshot.md、timeline.md、novel-state.md）使用这些标记，上下文污染极易导致标记泄漏到正文。当角色需要引用过去事件时，转换为故事内语言："三个月前在大泽镇那件事" not "Ch4那件事"。交付前必须 grep 扫描，零匹配才能提交（IR-5 Check 7）。

When injecting planning/context into the writing prompt, sanitize these patterns:

| Methodology Term | Replace With |
|-----------------|-------------|
| Hook IDs (H007, F-003) | "这条线索" |
| "本章要做的是" | "眼下要处理的" |
| "仿佛" | "像" |
| Chapter number references (Ch13, Ch14, 第X章, 上章, 前章) | 故事内时间/地点/事件描述（"在大泽镇那天""三个月前"）|
| "推进/回收/埋设" | Remove entirely — let prose flow naturally |
| "张力级别X" | Remove — the prose should embody the tension, not name it |
| "POV角色" | Use the character's name directly |

The writing prompt should read like a director's notes to an actor, not like a project manager's task list. If the prompt itself sounds mechanical, the prose will be mechanical too.

Sanitization checklist before each chapter:
- [ ] All hook/foreshadowing IDs replaced with descriptive references?
- [ ] No methodology jargon in the writing instructions?
- [ ] Instructions read like creative direction, not a spec sheet?
- [ ] Chapter goals stated as emotional targets, not checkboxes?
