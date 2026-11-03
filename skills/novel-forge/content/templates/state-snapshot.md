# State Snapshot: Ch.<!-- NNN -->

> Captures the state of the story world at the END of this chapter. **Phase 8 正常流程中不可变。** 修订时允许重新提取并覆盖（见 revision-workflow.md Section 七）。
> NNN 为零填充章节号（001, 002, ...）。

---

## Snapshot Identity

- **Chapter**: <!-- Ch.XXX -->
- **Chapter Title**: <!-- Title -->
- **POV Character**: <!-- Name -->
- **Timestamp**: <!-- Story-world date/time at chapter end -->
- **Snapshot Date**: <!-- Real-world date this was created -->

## Chapter Summary (≤200 chars)

<!-- What happened in this chapter, in 1-2 sentences. This summary is also copied to novel-state.md 章节摘要 table. -->

---

## Character States

### <!-- Character Name -->
| Field | State |
|-------|-------|
| **Physical** | <!-- Current physical condition --> |
| **Emotional** | <!-- Predominant emotion at chapter end --> |
| **Location** | <!-- Where they are --> |
| **Status** | <!-- Any change in social role, rank, reputation --> |
| **New Items/Skills** | <!-- Anything gained or lost --> |
| **Changes This Chapter** | <!-- What changed for this character --> |

### <!-- Character Name -->
| Field | State |
|-------|-------|
| **Physical** | |
| **Emotional** | |
| **Location** | |
| **Status** | |
| **New Items/Skills** | |
| **Changes This Chapter** | |

<!-- Add more characters as needed -->

### 伤势追踪

| 角色 | 部位 | 伤情 | 来源 | 当前状态 | 恢复趋势 |
|------|------|------|------|---------|---------|
| | | | | | |

（无伤势角色可省略此表。前章已有伤势必须延续追踪直到标注"已愈合"。）

---

## Relationship Changes

| Pair | Before | After | Catalyst | Direction |
|------|--------|-------|----------|-----------|
| <!-- A & B --> | <!-- Previous state --> | <!-- New state --> | <!-- What caused the change --> | <!-- 按大纲的走向 --> |
| <!-- A & C --> | <!-- Previous state --> | <!-- New state --> | <!-- What caused the change --> | <!-- 按大纲的走向 --> |

### Relationship Details
<!-- For significant changes, add a brief explanation of the nuance -->

---

## Foreshadowing Updates
<!-- 四态：PLANTED（新埋）/ WATERED（推进）/ HARVESTED（兑现）/ WITHERED（废弃）。DEFER 不记录（状态不变）。操作→状态映射详见 pre-writing-brief.md Section 7。 -->

| ID | Action | Detail |
|----|--------|--------|
| <!-- FS-XXX-NN --> | <!-- PLANTED / WATERED / HARVESTED / WITHERED --> | <!-- What happened --> |
| <!-- FS-XXX-NN --> | <!-- Action --> | <!-- What happened --> |

### New Items Proposed
| Proposed ID | Description | Expected Payoff |
|-------------|-------------|-----------------|
| <!-- FS-XXX-NN --> | <!-- What was planted --> | <!-- When it should pay off --> |

---

## Knowledge States

### <!-- Character Name -->
**Knows (事实认知)**:
- <!-- New facts learned this chapter -->

**Believes (信念认知)**:
- <!-- New or changed beliefs (来源：如何/为何产生此信念) -->

**Doesn't Know (认知盲区)**:
- <!-- New gaps that opened up —（影响：如果知道会发生什么变化）-->

### <!-- Character Name -->
**Knows (事实认知)**:
-

**Believes (信念认知)**:
-

**Doesn't Know (认知盲区)**:
-

<!-- Add more characters as needed -->

---

## Timeline

| Event | Story Time | Notes |
|-------|-----------|-------|
| Chapter start | <!-- Date/time --> | <!-- Where/when the chapter opens --> |
| <!-- Key event --> | <!-- Date/time --> | <!-- Note --> |
| Chapter end | <!-- Date/time --> | <!-- Where/when the chapter closes --> |
| **Total elapsed** | <!-- Duration --> | <!-- In-story time covered --> |

---

## Open Questions

### Raised This Chapter
1. <!-- Question raised but not answered -->
2. <!-- Question raised but not answered -->

### Still Open from Previous Chapters
1. <!-- Previously raised question, still unresolved -->
2. <!-- Previously raised question, still unresolved -->

### Answered This Chapter
1. <!-- Question that was resolved --> — **Answer**: <!-- What was revealed -->

---

## 新设定元素验证

| 元素 | 类别 | 原文 | 冲突 | 需更新世界观 |
|------|------|------|------|------------|
| <!-- 新设定名 --> | <!-- world-rule / character-detail / setting / ability / faction --> | <!-- 本章精确引用 --> | <!-- CONFLICT / NONE / CONFIRMED --> | <!-- YES / NO --> |

<!-- 验证规则：
1. 将每个新元素与 world.md 和 characters/ 交叉比对
2. 与现有正典矛盾 → CONFLICT，作者必须解决
3. 新元素且与正典一致 → NONE，标记待添加到正典文件
4. 正典中已有暗示但现在明确化 → CONFIRMED
-->

---

## Ambiguities Requiring User Decision

<!-- If any state is unclear, flag it here -->

- ⚠️ <!-- Description of the ambiguity --> — User: did <!-- character --> learn <!-- fact --> during this scene?

---

## Reader Knowledge Delta

> 角色知识 ≠ 读者知识。专家型/原住民/重生型角色可能早已了解所有规则，但读者是第一次接触。此部分追踪**读者**通过本章实际理解了什么，而非角色知道什么。

### 本章读者获得的新认知
<!-- 读者通过本章理解了哪些世界规则/体系/设定？角色可能早已知道，但读者是第一次 -->

| 知识点 | 类别 | 传达方式 | 传达充分度 |
|--------|------|---------|-----------|
| <!-- 读者学到了什么 --> | <!-- 力量体系 / 社会规则 / 地理 / 历史 / 势力 / 技能 / 其他 --> | <!-- 展示后果 / 对比差异 / 新手角色视角 / 回忆片段 / 对话解释 / 环境暗示 / 其他 --> | <!-- 充分 / 部分 / 仅标签 --> |

<!-- "仅标签" = 读者只知道名称（如"引灵境"），不理解含义/规则/后果 → 标记为下方"认知缺口" -->

### 读者认知缺口（已知未传达）
<!-- 从 world.md Reader Delivery Tracker 或前章 state snapshot 继承未传达项目 -->

| 缺口知识点 | 缺口来源 | 后续情节依赖度 | 持续未传达章数 |
|-----------|---------|--------------|--------------|
| <!-- 需要传达但尚未传达 --> | <!-- Surface层标注 / 前章继承 --> | <!-- 高（近期情节需要）/ 中 / 低 --> | <!-- N章 --> |

<!-- 规则：连续 ≥3 章出现同一"认知缺口"且"依赖度=高" → 下一章必须安排传达场景 -->

---

## Delta Summary (for quick reference)

<!-- 3-5 bullet points of the most important changes -->

- <!-- Change 1 -->
- <!-- Change 2 -->
- <!-- Change 3 -->

---

## Confirmation

- [ ] Character states verified
- [ ] Relationship changes confirmed
- [ ] Foreshadowing updates accurate
- [ ] Knowledge states correct
- [ ] Reader Knowledge Delta captured (传达充分度 assessed)
- [ ] Timeline consistent
- [ ] Open questions captured
- [ ] User has reviewed and approved
