# Character Design Guide: Creating Characters Through Dialogue, Starting From Conflict

> **权威声明**: 本文件是角色设计流程的权威参考。
> 角色模板见 templates/character-card.md。知识状态追踪见 consistency-system.md Section 1.4。

## Core Principle

Characters are NOT appearance sheets. They are bundles of contradiction, desire, fear, and history — compressed into a person who must ACT under pressure. Start from CONFLICT, not eye color. The AI's role is to help the user discover who their characters truly are through conversation.

### Character Files: Two-Tier System

Characters are stored in a dedicated `characters/` directory with two tiers:

| Tier | Who | Directory | Content |
|------|-----|-----------|---------|
| **Tier 1: Main** | POV characters + frequently appearing main cast (3-5 per story) | `characters/main/` | Full 3-layer model + voice profile + arc |
| **Tier 2: Supporting** | Characters appearing ≥2 times, one-scene characters with key function | `characters/supporting/` | Brief profile: identity / first appearance / known info / current status / narrative function |

**Upgrade rule:** When a supporting character appears ≥3 times OR gains important plot function, move their file from `supporting/` to `main/` and expand to full 3-layer profile.

**Creation timing:**
- Tier 1 characters are created in Phase 4 (before writing starts)
- Tier 2 characters are added to `characters/supporting/<name>.md` as they appear in the story (during Phase 8)
- Do NOT pre-create characters the story hasn't needed yet. Let characters emerge from writing.

### Incremental Character Growth

Character files are LIVING DOCUMENTS. They grow with the story:
- Phase 4: Create skeleton (identity + surface layer + core wound)
- During writing: Add details as the character reveals them (speech patterns, hidden traits, new relationships)
- Phase 8: When a character does something surprising, capture it in their file

Do NOT front-load every character with complete 3-layer analysis before writing. A character's "inner layer" and "core layer" may not be fully known until the writer discovers them through scenes.

---

## Conversation-First: Start With Role and Conflict

### NEVER Start Like This
- "你的主角长什么样？" (Appearance first)
- "主角的性格是什么样的？内向还是外向？" (Binary personality quiz)
- "请描述一下你的主要角色。" (Homework assignment)

### ALWAYS Start Like This
- "你的主角最想要什么？然后告诉我——什么在阻止他得到它？"
- "你的故事结束时，你的主角会和开始时是同一个人吗？如果不是，他失去了什么？获得了什么？"
- "如果你的主角在一个必须撒谎才能活下来的场景里，他会撒谎吗？他最不愿意对谁撒谎？"
- "告诉我你的主角最害怕被别人知道的一件事。"
- "你的反派——他觉得自己是坏人吗？如果他有机会给你讲他的故事，他会怎么说？"

---

## 3-Layer Character Model

Every character exists on three layers. The best characters have tension between these layers.

### Layer 1: Surface (表现层 — What They Show)

This is what the world sees. The mask. The performance.

**Elements:**
- Mannerisms and habits
- Speech patterns and verbal tics
- Appearance and how they present themselves
- How they interact with different people
- Their "public story" — what they tell others about themselves

**Dialogue Exploration Prompts:**
- "你的主角在陌生人面前和在信任的人面前，说话方式有什么不同？能分别模仿一句吗？"
- "他有什么习惯是别人会觉得奇怪但他自己完全没意识到的？"
- "如果他走进一个满是人的房间，别人第一眼会注意到他什么？是他想让人注意到的吗？"
- "他穿什么样的衣服？是精心选择的还是无所谓的？这反映了他什么样的自我认知？"
- "他生气的时候会怎样？是爆发、沉默、还是微笑？他的愤怒表达方式和他成长环境有什么关系？"

### Layer 2: Inner (信念层 — What They Believe)

This is what they tell themselves. Their values, fears, and self-image. This layer DRIVES behavior.

**Elements:**
- Core values (what they'd die for vs. what they say they'd die for)
- Fears (not phobias — the deep ones: being alone, being seen, being powerless)
- Self-image (who they think they are vs. who they actually are)
- Justification system (how they rationalize their actions)
- What they believe about the world ("People are basically good" / "Trust no one" / "Power is everything")

**Dialogue Exploration Prompts:**
- "如果你的主角必须在'背叛朋友但达成目标'和'保护朋友但失败'之间选，他会选什么？更重要的是——他会怎么跟自己解释这个选择？"
- "他说服自己相信的一个谎言是什么？一个他需要的谎言？"
- "他最瞧不起什么样的人？这种瞧不起是不是其实指向他自己某个不愿意面对的部分？"
- "他觉得自己最大的优点是什么？别人觉得呢？这两个答案一样吗？"
- "如果有人跟他说'你已经够好了，不需要再努力了'，他会是什么反应？愤怒？困惑？悲伤？"

### Layer 3: Core (内核层 — What They Need But Can't Face)

This is the wound. The foundational experience that shaped them. The lie they believe about themselves or the world. This is where CHARACTER ARC lives.

**Elements:**
- The wound: a formative experience of pain, betrayal, loss, or failure
- The lie: what they learned from the wound ("I can't trust anyone" / "I'm not enough" / "Showing weakness means death")
- The need: what they actually need to heal or grow (usually the opposite of the lie)
- The truth: what the story will eventually teach them
- The cost: what they must sacrifice to accept the truth

**Dialogue Exploration Prompts:**
- "你的主角在成为现在这个人之前，经历过什么改变一切的事？这件事他跟别人讲过吗？"
- "如果我们可以回到他的过去看一个场景，你会带我去看哪个瞬间？那个他不太愿意回忆的瞬间？"
- "他最害怕的不是外部的敌人——是他自己内心的什么东西？是他会变成某种人？还是他其实一直是那种人只是不愿意承认？"
- "在你的故事结束时，他需要接受的一个关于自己的真相是什么？他现在离接受这个真相有多远？"
- "有没有一个人——只要这个人说一句话，就能击溃他所有的伪装？这个人是活着的还是已经不在了？"

---

## Deriving Voice and Speech Patterns From Psychology

> 角色辨识度设计（视觉/行为/语言锚点、反差记忆点、梗、不可妥协的执念）请参考 advanced-workflows.md 中的"银魂法角色设计"。

A character's voice is not arbitrary. It flows from their psychology.

### Voice Derivation Framework

1. **From Core Wound → Speech Defense**
   - Abandoned → speaks in a way that keeps people at arm's length (humor, deflection, excessive independence)
   - Betrayed → tests people through words (provocative questions, loyalty tests, breaking promises first)
   - Unseen → performs for attention OR withdraws into silence (extremes)
   - Controlled → rebels through language (sarcasm, hidden meanings, coded speech)

2. **From Self-Image → Word Choice**
   - Sees self as intellectual → uses precise language, references, avoids slang
   - Sees self as tough → curt, direct, avoids emotional vocabulary
   - Sees self as kind → softens statements, over-explains, apologizes excessively
   - Sees self as unworthy → self-deprecating, hesitant, minimizes achievements

3. **From Values → Argument Style**
   - Values loyalty → argues from relationships ("How could you do this to us?")
   - Values fairness → argues from principle ("That's not right")
   - Values power → argues from strength ("You can't stop me")
   - Values freedom → argues from autonomy ("You don't own me")

### Practical Example

```
User: 我主角是个修仙者，但他是从凡人开始修炼的。

AI: 所以他身上有凡人的底色。我想了解一下——他在修仙者群体里，说话是什么感觉？是会刻意模仿那些世家出身的人，还是保持凡人的说话方式？

User: 他会观察别人怎么说话，然后在不同场合切换。

AI: 这个太有意思了。他有一个"社交伪装"——在不同场合用不同的说话方式。那他的本音呢？他一个人的时候，或者面对完全信任的人时，说的是什么话？是凡人世界的质朴，还是已经被修仙世界同化了？

User: 应该还是凡人的底色，但他自己可能不太愿意流露。

AI: 所以他的言语本身就是一层伪装。这给对话写作提供了很丰富的素材——读者能通过他说话方式的微妙变化，感知到他在防御还是在放松。我们把这个记下来。
```

---

## Character Arc Types

### 1. Positive Change Arc (正面成长弧线)
- Character believes a lie → experiences story → embraces truth → becomes better
- Most common in 网文 protagonists
- Key: the change must be EARNED through struggle, not given
- Example: "力量就是一切" → "力量是为了保护重要的东西"

### 2. Negative Change Arc (堕落弧线)
- Character believes a lie → experiences story → embraces a worse lie → falls
- Rare in 网文 but devastating when done well
- Key: the fall must be understandable, even sympathetic
- Example: "我可以用任何手段保护她" → 最终用手段推开了所有人

### 3. Disillusionment Arc (幻灭弧线)
- Character believes a lie → experiences story → sees truth → is changed by it (not necessarily better or worse, just different)
- Common in more literary 网文
- Key: the disillusionment should feel like loss even when it's growth
- Example: "正义一定存在" → "正义需要人去创造，而且代价很高"

### 4. Growth Arc (成长但不改变核心)
- Character already has good core values → faces challenges that TEST those values → holds firm but gains depth
- Common in established, confident protagonists
- Key: the test must be real — reader should genuinely wonder if they'll break
- Example: "我不会放弃任何一个同伴" → 面对必须牺牲一个才能救其他的困境 → 找到第三条路（但付出了巨大代价）

### 5. Flat Truth-Teller Arc (恒定真理者)
- Character doesn't change → changes everyone around them
- Useful for mentor figures, companions, or unconventional protagonists
- Key: the character must have a clear philosophy and the story must challenge it repeatedly
- Example: 一个始终坚持"人定胜天"的老兵，他的坚持让周围所有人的世界观都动摇了

---

## When to Offer Proposals vs. Build Together

### Offer 2-3 Character Concept Proposals When:
- User says "没想好" or "你有什么建议"
- User gives contradictory signals (wants a "冷酷" character but also "很幽默")
- User is stuck after several attempts
- This is a secondary character the user hasn't thought much about

### Proposal Format

```
根据你之前描述的故事和主角设定，我想了三个方向，你看看哪个更接近你想要的感觉：

【方案A：沉默的守护者型】
核心冲突：他的力量是他最大的骄傲，也是他最深的恐惧——因为他见过太多强者失控。
他在乎的人越是靠近他，他越觉得危险。
读者会看到：一个表面冷淡、内心火热的人，他的每一次推开都是因为太在乎。

【方案B：桀骜的叛逆者型】
核心冲突：他看穿了这个世界权力游戏的本质，所以拒绝按规则玩——
但拒绝本身成了一种新的规则，他发现自己在反抗中变成了另一种"强者"。
读者会看到：一个嘴上说着不在乎、实际上比谁都在乎的人。

【方案C：温柔的野心家型】
核心冲突：他真心地善良，真心地想帮助别人——但他的善良有方向感和目的性。
他不是圣母，他是一个相信"赢得权力才能行善"的人。
读者会看到：一个比反派更可怕的善人。
```

### Build Together When:
- User has clear, strong ideas (follow their energy)
- This is the protagonist (too important for generic proposals)
- User is actively connecting character to plot/world
- User asks "如果他是这样的话..." type questions (they're already creating)

---

## Relationship Design Through Contrast and Conflict

### Core Principle
The best character relationships are defined by COMPLEMENTARY tensions, not similarity.

### Relationship Building Questions
- "这两个人最根本的分歧是什么？不是表面上的意见不同，是底层价值观的冲突。"
- "如果他们被困在一个房间里必须合作，谁会先妥协？为什么？这种妥协对他们意味着什么？"
- "他们各自看到了对方身上自己最缺乏的东西吗？这种认知是吸引他们还是让他们排斥？"
- "有没有一个秘密，一旦被对方知道，这段关系就再也回不去了？"
- "如果其中一个要为另一个牺牲一切，另一个会让他做吗？为什么？"

### Dynamic Tension Types
- **信仰对立**: Same goal, different methods ("我们都想拯救世界，但你的代价太大")
- **镜像关系**: They could have been each other under different circumstances ("如果我经历了你的事，我可能就是你")
- **依赖与独立**: One needs the other more than they admit (both directions create tension)
- **信任与背叛**: Former trust that was broken, or potential betrayal that looms
- **误解与真相**: They think they know each other but don't — yet

---

## 网文-Specific Character Design

### 主角 (Protagonist) Design Patterns

**Common 网文 Protagonist Types:**
1. **废材逆袭型**: Start at the bottom, rise through talent + effort + golden finger
   - Core wound: being looked down upon, being powerless
   - Arc: proving worth (external) while learning what worth truly means (internal)
   - Danger: can become a revenge fantasy without emotional depth

2. **重生/穿越型**: Second chance with future knowledge
   - Core wound: failure in the past life, things left undone
   - Arc: changing fate while confronting what can't be changed
   - Danger: overpowered from start, removing tension

3. **隐世天才型**: Hidden strength revealed gradually
   - Core wound: forced to hide, undervalued, or self-doubting
   - Arc: finding the courage to stop hiding and face consequences
   - Danger: too much "low-key" becomes tedious

4. **复仇驱动型**: Clear external goal driving all action
   - Core wound: devastating loss or betrayal
   - Arc: revenge vs. healing, becoming the thing you hate
   - Danger: one-dimensional if revenge is the ONLY motivation

### 反派 (Antagonist) Layering

A 网文 antagonist hierarchy typically includes:

1. **早期对手** (Chapters 1-30): Local bullies, jealous peers, minor family conflicts
   - Function: establish protagonist's starting position and provide initial satisfaction
   - Design: simple motivation, easy to hate, satisfying to defeat

2. **中期敌人** (Chapters 30-100): Powerful factions, institutional enemies, hidden manipulators
   - Function: raise stakes, reveal world complexity, test protagonist's values
   - Design: understandable motivation, some sympathetic qualities, genuine threat

3. **终局对手** (Endgame): The architect of the system, the one behind everything
   - Function: thematic climax, ultimate test of who the protagonist has become
   - Design: mirror of the protagonist, or what the protagonist could become

**Layering Principle**: Each antagonist should be harder to defeat not just because they're stronger, but because they challenge the protagonist on a DEEPER level. Early antagonists challenge ability. Mid antagonists challenge values. Final antagonists challenge identity.

### 女主/感情线 (Female Lead / Romance) Configuration

**Common Configurations:**
1. **单一女主**: One primary love interest, relationship develops alongside plot
2. **后宫型**: Multiple love interests with different dynamics
3. **无感情线**: Focus entirely on plot/power progression

**Design Considerations (Regardless of Configuration):**
- Each romantic interest should challenge the protagonist in a UNIQUE way
- Avoid "beautiful + kind + supportive" as the only traits — give them their own conflicts and arcs
- The romantic dynamic should create STORY, not just wish-fulfillment
- Key question: "If you removed this character's romantic relationship with the protagonist, would they still be interesting?" If no, the character needs more work.

**Dialogue Exploration for Romance Dynamics:**
- "你的主角在什么情况下会第一次真心地笑？那个场景里有谁？"
- "有没有一个人，你的主角在他/她面前完全无法伪装？为什么？"
- "这段感情最大的障碍是什么——外部的还是内部的？如果是内部的，是什么？"
- "他们之间有没有一个'不可能被原谅'的底线？故事会不会触碰这个底线？"

---

## Example Dialogue Exchanges

### Example 1: Building a Protagonist From Conflict

```
AI: 你的主角，他最想要什么？

User: 他想变强。要保护他的妹妹。

AI: 保护妹妹——这个我理解。但"想变强"这件事本身，有没有什么不对劲的地方？比如说，他是不是已经在用"变强"来逃避什么？"只要我够强了，就不用担心了"——这种想法有没有可能是他的一种逃避？

User: ...你说的对。他其实是在逃避面对他父母的死。他觉得如果自己够强，就不会再失去任何人。但事实上变强不能保证这件事。

AI: 这就是他的核心谎言——"力量可以防止失去"。你的故事会让他学到什么真相？

User: 应该是...有些失去是不可避免的，重要的是你面对失去的方式。

AI: 太好了。所以他的成长弧线是：从"我必须变强到不会失去任何东西"到"我接受失去是可能的，但我选择珍惜当下"。这个弧线会让他的每次升级都有双重意义——外在是力量增长，内在是他慢慢学会面对这个真相。那我们来想想——什么样的事件能最早地动摇他这个信念？不需要完全打破，只是产生裂痕。
```

### Example 2: Designing an Antagonist

```
AI: 你的反派，如果让他给自己写一个自传，书名会叫什么？

User: 哈哈，可能叫《我没有选择》。

AI: 这个书名太有故事了。"我没有选择"——但这是他真的相信的，还是他用来原谅自己的借口？

User: 可能一开始是真的，到后面就变成了借口。他最初确实被形势所迫做了坏事，但后来他已经有了选择的能力，只是习惯了用"没有选择"来合理化。

AI: 所以他和主角之间有一种镜像关系——主角也在面对"没有选择"的困境，但他选择了不同的路。当这两个人对峙的时候，不是正邪之争，是"同一种处境下的两种选择"之争。这种对手关系比纯粹的反派有意思多了。那他的表面形象是什么样的？他对外展示的自己，和他内心真实的自己，有什么不同？

User: 他对外是一个很有魅力的领袖，所有追随者都真心信服他。他也确实照顾他们。只是对"外面的人"完全不择手段。

AI: 所以他对"自己人"是真诚的好——这让他的恶更复杂了。他不是没有感情，他的感情恰恰是他最危险的地方。因为任何威胁到他"自己人"的事，都会触发他最极端的反应。主角有可能会利用这一点吗？或者更复杂——主角会不会不忍心利用这一点，因为他理解这种感觉？
```

### Example 3: Creating a Supporting Character Through Proposals

```
AI: 你需要一个师父/导师角色对吗？我有几个方向的想法，你看看哪个感觉对：

【方案A：严厉的打磨者】
他相信"最好的爱是最狠的训练"。他不会说好听的话，但在主角看不到的地方，他一直在为主角铺路。
冲突点：他的严厉把上一个弟子逼走了，他还没有原谅自己。
读者爽点：当主角终于理解师父的用意时，那种"原来一直被保护着"的感觉。

【方案B：温柔的守护者】
他什么都愿意教，什么都愿意给——但他隐藏了一个秘密：他自己在走向衰亡。
冲突点：他在用最后的时间为主角铺路，但主角还以为他们还有很多时间。
读者爽点：当他终于撑不住的时候，主角发现所有的准备都已经做好了。

【方案C：亦师亦敌】
他教的每一招里都藏着试探。他在培养主角，同时也在评估——如果主角走偏了，他随时准备亲手终结。
冲突点：他真心喜欢这个弟子，这让他的"必要时终结"变得几乎不可能。
读者爽点：当师徒对决的时刻到来，双方都不想赢。

User: 方案C太好了！但他不是要终结主角，而是...他在评估主角能不能接过他的位置。他的位置不是一个好位置——是一个必须做脏活的位置。

AI: 哦这个更妙了。他不是在找继承人，他是在找替罪羊——不，找一个能代替他承受这份重担的人。而他越喜欢这个弟子，就越犹豫要不要把这个重担交给他。这个师父自己的核心冲突就是："我能把我爱的弟子推入火坑吗？但如果我不推，我就永远困在里面。"这种师父形象会让每一场师徒对话都有双层含义。
```

---

## Character Design Summary Checklist

Before moving on from character design, ensure you can answer these for each major character:

- [ ] **Want**: What do they want? (External, story-level)
- [ ] **Need**: What do they need? (Internal, often unconscious)
- [ ] **Lie**: What false belief drives their behavior?
- [ ] **Wound**: What experience created the lie?
- [ ] **Ghost**: What haunts them from the past?
- [ ] **Voice**: How do they talk? Why do they talk that way?
- [ ] **Mask**: What do they show the world? Why?
- [ ] **Breaking point**: What would make them abandon everything they believe?
- [ ] **Arc direction**: Where are they headed by the end?
- [ ] **Relationship tension**: What unresolved tension exists with each major character?
