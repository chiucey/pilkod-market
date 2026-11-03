# World-Building Guide: Structured Creation Through Collaborative Dialogue

> **权威声明**: 本文件是世界观构建流程的权威参考。
> 世界观模板见 templates/world.md。

## Core Principle

World-building is NOT form-filling. Build only what creates conflict or reveals character. The AI acts as a creative collaborator who channels the user's excitement into a world that serves the story -- and knows when to stop.

### The Incremental Growth Principle (设定增量生长原则)

World-building documents are LIVING FILES that grow with the story, not encyclopedias completed before writing begins.

**The trap:** Pre-building detailed settings for locations the protagonist won't visit for 100 chapters. The result: the story feels like it's executing a spec sheet, not discovering a world.

**The right way:**
1. Start with the MVW (Minimum Viable World) — only what Arc 1 needs
2. During Phase 8 (state extraction), when new world elements emerge from writing, ADD them to `world.md`
3. Before each new volume, review upcoming milestones and add ONLY the settings those milestones require
4. Let the story surprise you — if a scene reveals something about the world you didn't plan, capture it

**Concrete rule:**
- `world.md` at Phase 3 end: ~500-1500 words (skeleton)
- `world.md` after 50 chapters: ~3000-5000 words (organically grown)
- `world.md` should NEVER exceed 8000 words — if it does, archive deep-level details

### Pre-setting vs. Emergent Setting

| Type | When Created | Example |
|------|-------------|---------|
| **Pre-setting** (Phase 3) | Before writing starts | Core power system rules, protagonist's starting faction, basic geography |
| **Emergent setting** (Phase 8) | Discovered during writing | A market's unspoken rules, a side character's hidden technique, regional dialect details |
| **Just-in-time setting** (Phase 7 pre-write) | Before a specific scene needs it | The layout of a building the protagonist is about to infiltrate |

The ratio should be approximately: Pre-setting 30% / Emergent 50% / Just-in-time 20%.

---

## Stop-Loss Mechanism: When Is World-Building DONE?

World-building is a means, not an end. It is COMPLETE enough to start writing when ALL three conditions are met:

1. **Conflict coverage**: Every planned conflict in the first arc has a world-rule that enables it.
2. **Internal consistency**: No rule contradicts another. Run the "collision test": pick any two rules and imagine them interacting. If the result is incoherent, fix it before writing.
3. **Reader comprehension threshold**: A reader would understand 90% of what happens in the first 10 chapters without needing an appendix.

### Hard Stop Signals (STOP world-building immediately)

- The user has spent more time on world details than on ANY character or scene.
- The conversation has gone 3+ rounds on a dimension with no new story ideas emerging.
- The user says "I just need to figure out one more thing..." more than twice.
- You have detailed history for periods the reader will never see.
- You have named more than 15 locations the protagonist will never visit.

When a hard stop triggers: "这个世界已经够活了。我们先写第一章，世界会在故事里自己生长的。"

### Minimum Viable World (MVW)

Before starting any draft, confirm the MVW checklist:

- [ ] ONE sentence that makes this world different from reality ("world seed")
- [ ] The power/magic system's core rule + cost
- [ ] 3-5 named locations the protagonist will visit in Arc 1
- [ ] 2-4 factions/forces with competing interests
- [ ] 1-2 cultural details that create conflict for the protagonist
- [ ] The protagonist's starting position within the power structure

If all items are checked, you have enough world to write. Everything else is optional expansion.

---

## The Iceberg Model: Reader-Filter Framework

For EVERY world detail, decide its depth level BEFORE committing it to the page:

| Level | What It Means | When Reader Sees It |
|-------|---------------|---------------------|
| **Surface** | Rules the reader MUST understand to follow the story | Ch1-3, woven into action |
| **Mid-depth** | Rules that add richness and explain motivations | Revealed over an arc, through discovery |
| **Deep** | Author-only knowledge for writing consistency | Reader never sees it explicitly |
| **CUT** | Details that don't fit any of the above | Never -- delete or archive |

### The Filter Question

For any proposed detail, ask: "If the reader never learns this, does the story still work?" If YES, it's Deep-level at most. If the story BREAKS without it, it's Surface-level and must be shown early.

### Practical Application

```
World detail: "灵脉的分布决定了修仙门派的选址"

Surface: Sect built on rich vein -> explains why it's powerful and contested. Show in Ch1-2.
Mid-depth: Different vein grades produce different effects -> revealed when protagonist visits a weaker sect.
Deep: Veins originate from a primordial creature underground -> author knows, informs why veins dry up, reader never sees the explanation.
CUT: "3000 years ago Grandmaster Xuan mapped the vein system..." -> Unless directly plot-relevant, archive it.
```

---

## FAIL / PASS Examples

### FAIL: Encyclopedia Dump

```
❌ [Chapter 1: 2000 words describing geography, 12 cultivation realms,
history of each sect, economic system, and northern tribe religions.]

Problems: All rules upfront, no tension from world constraints,
reader is reading a textbook, not a story.
```

### PASS: Conflict-Driven

```
✓ [Chapter 1: Protagonist tries to buy medicine for his sick sister.
Shopkeeper refuses -- not because of money, but because his family name
is on a restricted list. A cultivator floats past on a sword, ignoring
the line of sick people. His sister's cough gets worse.]

Why it works: Rules revealed through conflict, world creates problems
for the character, reader discovers alongside the protagonist.
```

### FAIL vs PASS Comparison

| Dimension | FAIL Pattern | PASS Pattern |
|-----------|-------------|--------------|
| Geography | Detailed map description in narration | Character must cross a dangerous zone to reach their goal |
| History | "Let me tell you about the War of..." | A character's scar tells the history; their flinch tells the cost |
| Power System | Full explanation of all realms before action | Protagonist discovers a realm by getting crushed by someone in it |
| Politics | Paragraph listing all factions | Protagonist angers a faction and learns through consequences |
| Culture | "In this world, it is customary to..." | Protagonist violates a custom and the room goes silent |
| Economy | Explanation of currency and trade routes | Protagonist can't afford something they desperately need |

---

## 5-Step World Construction Process

### Step 1: Find the World Seed

**Output**: ONE sentence that makes this world different from reality.

1. Ask: "你的故事最让你兴奋的画面是什么？那个画面里有什么是现实世界里不可能发生的？"
2. Extract the impossible thing. That's the world seed.
3. Write the seed sentence. Format: "在这个世界里，[不可能的事]，所以[后果]。"

Example: "在这个世界里，力量会消耗寿命，所以最强的人往往最短命。"

Every other world rule should either support, complicate, or challenge this seed.

### Step 2: Build the Story-Critical Core

**Output**: Only the dimensions the first arc needs.

Scoping rules:
- **Total active dimensions**: 5-7 max for a web novel. 3-5 for shorter work.
- **Locations per arc**: Detail 3-5 max. Name others but don't detail until needed.
- **Named characters with full profiles**: 8-12 for Arc 1. Others get one-line descriptions.

Dimension selection by story type:
- Rising through ranks -> Power System + Social Structure + Politics
- Survival -> Geography + Economy + Daily Life
- Mystery/conspiracy -> History + Unspoken Rules + Politics
- Exploration -> Geography + Culture + Power System

### Step 3: Establish Power System Parameters

**Output**: A defined power system with clear boundaries.

Three complexity levels -- pick ONE:

| Level | Definition | Best For |
|-------|-----------|----------|
| **Soft** | Vague rules, runs on emotion/theme | Literary fantasy, romance with magic |
| **Hard** | Strict rules, clear costs, predictable outcomes | Progression fantasy, cultivation novels |
| **Hybrid** | Core rules are hard, exceptions exist | Most web novels, adventure stories |

**修仙境界**: Keep to 6-9 realms total. Each needs: breakthrough condition, combat range, lifespan, social perception. Define gap between realms (碾压 or 越级) -- this affects ALL combat writing. Breakthrough failure must have meaningful consequences.

**金手指 Design**: Must have at least one clear limitation. Must fit the power system. Define growth trajectory and discovery risk (what happens if others find out?).

### Step 4: Apply the Iceberg Filter

**Output**: Every detail assigned a depth level (Surface / Mid-depth / Deep / CUT).

1. List all details from Steps 1-3.
2. For each, ask the filter question.
3. Assign depth level.
4. CUT everything that doesn't fit. Move to archive -- may be useful later.

Rule of thumb: Surface ~20%, Mid-depth ~30%, Deep ~20%, CUT/defer ~30%.

### Step 5: Validate Through Conflict

**Output**: 3-5 conflict scenarios that test the world's rules.

For each planned major conflict in Arc 1:
1. What the conflict IS (who vs who, over what)
2. Which world rules ENABLE this conflict
3. Which world rules CONSTRAINT the characters' options
4. What the reader LEARNS about the world through this conflict

If any conflict has no world-rule enabling it, the world is incomplete. If any world-rule has NO conflict demonstrating it, that rule is encyclopedia -- consider CUT.

---

## 10 World-Building Dimensions (Reference Library)

Use these as needed based on Step 2 selection. Do NOT build all 10 by default.

### 1. Geography / 地理环境
- "这个世界的地形是如何塑造这里的人的？"
- "从一个地方到另一个地方有多难？交通方式决定权力边界。"
- "地图上有没有'不存在'的区域——被禁止、被遗忘、被刻意隐瞒的？"

### 2. History / 历史
- "这个世界的人最不愿意提起的一段历史是什么？"
- "有没有一个'黄金时代'——人们怀念它，但真相没那么美好？"
- "谁在写历史？赢家？教会？还是角落里的无名史官？"

### 3. Politics / 政治权力
- "谁在统治？他们最害怕什么？"
- "权力的更替是怎么发生的？世袭？比武？暗杀？"
- "有没有一个正在崛起但还没被正视的力量？"

### 4. Economy / 经济体系
- "这个世界最值钱的东西是什么？谁在控制它？"
- "经济体系有没有致命弱点——依赖某种正在枯竭的东西？"
- "你的主角在经济体系里处于什么位置？这如何驱动他的行为？"

### 5. Culture / 文化习俗
- "有什么东西在咱们看来很普通，但在这个世界里是禁忌？"
- "不同地域/种族/阶层之间，最大的文化差异体现在哪里？"
- "如果一个人想表达'我爱你'，在这个世界里他会怎么做？"

### 6. Religion / 信仰体系
- "人们信什么？神、自然力量、某种理念、还是什么都不信？"
- "有没有人质疑主流信仰？他们面临什么后果？"
- "如果你的主角遇到信仰危机，他会失去什么？会获得什么？"

### 7. Magic / Technology / 力量体系
- "力量是特权、诅咒、还是责任？拥有者被崇拜还是被恐惧？"
- "获取力量的代价是什么？身体？精神？道德？"
- "力量的规则有没有漏洞？有没有人在利用这些漏洞？"

### 8. Social Structure / 社会结构
- "阶层是固定的还是流动的？人们对此是什么态度？"
- "什么是社会地位的标志？血统、财富、力量、知识？"
- "社会最大的谎言是什么？所有人都知道但没人揭穿。"

### 9. Daily Life / 日常生活
- "他们吃什么？食物能告诉我们气候、贸易、文化、禁忌。"
- "小孩子在玩什么游戏？这些游戏反映了什么样的世界观？"
- "如果有人生病了，会怎么做？求医？祈祷？用某种力量？"

### 10. Unspoken Rules / 潜规则
- "有什么事情每个人都在做但没人会公开承认？"
- "有哪些话是不能说的？不是因为法律，而是所有人'都知道'不该说。"
- "如果有人打破了潜规则，会发生什么？谁来惩罚？"

---

## Detecting User Passion vs. Disinterest

### Signs of Passion (Dive Deeper)
- Detailed, unprompted answers; tells stories within the world; vivid sensory language; asks YOU questions; connects elements spontaneously ("这样的话之前说的那个经济体系就得...")

### Signs of Disinterest (Move On)
- One-sentence answers; "还没想好" / "都可以" / "随便"; steers to different topic; repeats surface-level info

### Handling Both

**Passionate**: "你刚才说的这点特别有意思，我们再挖一下——" Do not interrupt their flow.

**Disinterested**: "这个维度先放着，等故事需要时再回来。我们来聊聊[2-3 options]——"

**Silent treatment**: Shift from questions to PROPOSALS: "我根据你之前说的，想了几种可能，你看看哪个更接近你的感觉——" Give 2-3 concrete options.

---

## Synthesizing the World Bible

### World Bible Structure

```markdown
# [世界名称] 设定集

## 世界种子
[ONE sentence from Step 1]

## 冰山分层
### Surface (Ch1-3 读者必须知道): [细节 + 关联章节]
### Mid-depth (逐渐揭示): [细节 + 揭示时机]
### Deep (作者知道，读者感受): [内部逻辑]
### Archive (备用): [被CUT但可能有用的设定]

## 力量体系
[类型/核心规则/代价/金手指]

## 核心地点 (Arc 1: 3-5个)
[地点名: 描述 + 故事功能]

## 势力与冲突
[势力名: 诉求 + 矛盾]

## 冲突验证
[冲突: 哪些规则enable？角色受什么constraint？读者学到什么？]
```

### Synthesis Rules
1. Only include what was discussed -- do not invent without permission
2. Mark uncertain items with `[待定]`
3. Every Surface detail tied to a specific chapter or scene
4. Flag inconsistencies: "注意：A设定和B设定可能存在冲突"
5. Present as a living document

---

## Red Flags and Fixes

### Too Generic
- **Symptoms**: Every element could belong to any novel in the genre
- **Fix**: Find ONE unique detail and expand from it
- **Prompt**: "这些设定我好像在好多作品里都见过。这个世界的'不可能'是什么？什么让它不一样？"

### Too Complex
- **Symptoms**: 15 power systems, 50 factions, 3000 years of history, story hasn't started
- **Fix**: Identify story-relevant core for first arc only. Rest goes to archive.
- **Prompt**: "如果你的主角只能接触到这个世界的5%，那是哪5%？"

### Too Derivative
- **Symptoms**: "Basically it's like [popular novel] but with [minor change]"
- **Fix**: Extract the EMOTIONAL core, not the literal setting
- **Prompt**: "那个作品最打动你的是什么？不是设定，是让你心跳加速的瞬间。我们来创造新世界，保留那种感觉。"

### Too Endless
- **Symptoms**: 30+ minutes of world-building with no end in sight
- **Fix**: Check MVW checklist. If covered, enforce hard stop.
- **Prompt**: "来检查一下 -- [MVW项目]。这些都有了。我们可以开始写了。"

---

## Opening Conversation Starters

Never start with "Let me ask you some questions about your world." Open with creative energy:

- "你的故事最让你兴奋的那个画面是什么？"
- "如果你可以用一个镜头展示你的世界，你会拍什么？"
- "这个世界的'不可能'是什么？什么规则不允许存在，但偏偏发生了？"
- "告诉我最普通的一天——但从一个很不普通的人的视角。"
- "如果你的主角站在世界最高处往下看，他会看到什么？"

Listen. Follow the energy. Then immediately apply Step 1 to extract the world seed.

---

## Example Dialogue Exchanges

### Example 1: Opening -> World Seed Extraction

```
AI: 你的故事最让你兴奋的画面是什么？
User: 主角站在裂缝边上，底下黑雾翻涌，手里快碎的剑，身后是要保护的人。跳下去可能回不来。
AI: 那个裂缝是世界的伤疤？一直存在还是某个事件造成的？
User: 几百年前大战打出来的，最强的几个人联手都没完全封印下面的东西。
AI: [WORLD SEED] "这个世界的最强者留下未完成的封印，裂缝在扩大，继承者不是他们的后人。"
    那把剑是传承来的？力量的传承在这个世界是怎样的？
User: 剑是碎裂封印的一部分。最强者的后人现在是顶级家族，但我主角是被剑选中的，不是任何家族的后代。
```

### Example 2: Power System -> Iceberg Filter Applied

```
AI: 一个普通人从零到最高境界需要多久？
User: 最快几百年。正常情况一辈子到不了。
AI: 你的主角呢？金手指让他快几倍？
User: 十倍吧，几十年到别人几百年的程度。
AI: 几十年还是很久。境界越高的人还关心普通人吗？
User: 大部分不关心了。但我主角不一样，境界越高越放不下最初要保护的人。
AI: [ICEBERG] "强者漠视弱者" = Surface rule. 主角的拒绝 = demonstrates it through conflict.
    价值观对抗，不单是力量对抗。那什么限制普通人的修炼速度？这影响金手指的合理性。
```

### Example 3: Disinterest -> Value-Add -> Pivot

```
AI: 经济体系有想法吗？
User: 没怎么想，用灵石吧，修仙小说都这样。
AI: 灵石够用。不过一个点：灵石=钱=修炼资源，控制产出的人就控制一切。
    你主角灵石从哪来？可能是冲突来源。但这块你不感兴趣，先放。聊什么有感觉？
User: 危险区域！除了裂缝还有别的地方吗？
AI: [DETECTS PASSION] 裂缝之外，还有什么地方普通人不敢去？自然的还是人为的？
```

---

## 网文-Specific Checklist

- [ ] **力量体系**: Clear progression, meaningful gaps, visible power-ups
- [ ] **金手指逻辑**: Fits power system + has limitation
- [ ] **阶层与力量关系**: Meritocratic? Hereditary? Random?
- [ ] **主角起点**: Why here? What makes this position dramatically interesting?
- [ ] **升级动力**: Personal stakes, not abstract goals
- [ ] **对手层级**: Early/mid/end-game threats each feel distinct
- [ ] **地图扩展空间**: 新手村 -> 更广阔的世界
- [ ] **打脸场景土壤**: Natural face-slapping opportunities
- [ ] **装逼合理性**: Believable MC showing off (information asymmetry / hidden identity / unexpected level)
- [ ] **日常与战斗平衡**: World supports both

---

## Quick Reference: Decision Flow

```
START world-building
  -> [Step 1] Extract world seed from user's excitement
  -> [Step 2] Select 5-7 dimensions the first arc needs
  -> [Step 3] Define power system (Soft/Hard/Hybrid)
  -> [Step 4] Apply Iceberg filter to all details
  -> [Step 5] Validate through 3-5 conflict scenarios
  -> Check MVW checklist?
     YES -> STOP. Write Chapter 1.
     NO  -> Build ONLY what's missing.
  -> [Hard stop triggers?] -> Enforce stop. Start writing.
```

---

## Final Notes

- World-building is iterative. First pass covers the MVW. Everything else comes when the story demands it.
- Always connect world elements back to STORY. "这个设定很好 -- 你的故事里它怎么体现？"
- Build only what creates conflict or reveals character. Everything else is archive material.
- Leave room for the user to discover their world while writing. The world bible is a living document.
- The best world-building makes the reader feel like they're DISCOVERING a world, not STUDYING one.
