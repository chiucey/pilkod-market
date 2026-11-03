# Editorial Report: Ch.<!-- XXX -->

> Generated after editorial review. Documents all findings and proposed fixes.
> 六大编辑角色定义见 references/editorial-roles.md。

---

## Overview

| Field | Value |
|-------|-------|
| **Chapter** | <!-- Ch.XXX --> |
| **Review Date** | <!-- YYYY-MM-DD --> |
| **Editors Run** | <!-- Which of the 6 editors were applied --> |
| **Total Issues** | <!-- Count --> |
| **Critical** | <!-- Count --> |
| **Major** | <!-- Count --> |
| **Minor** | <!-- Count --> |
| **Verdict** | <!-- Pass / Revise Required / Major Rework --> |

---

## Editor: Continuity Editor (一致性编辑)

### Findings

<!-- If no issues found: "No continuity issues detected." -->

#### [CRITICAL] <!-- Issue title -->
**Location**: Ch.<!-- XXX -->, Scene <!-- N -->, Paragraph <!-- M -->
**Issue**: <!-- Description of the continuity error -->
**Context**: <!-- What was established previously that contradicts this -->
```
old_string: |
  <!-- Exact text with the error -->
new_string: |
  <!-- Proposed fix -->
```

#### [MAJOR] <!-- Issue title -->
**Location**: Ch.<!-- XXX -->, Scene <!-- N -->, Paragraph <!-- M -->
**Issue**: <!-- Description -->
```
old_string: |
  <!-- Exact text -->
new_string: |
  <!-- Proposed fix -->
```

#### [MINOR] <!-- Issue title -->
**Location**: Ch.<!-- XXX -->, Scene <!-- N -->, Paragraph <!-- M -->
**Issue**: <!-- Description -->
```
old_string: |
  <!-- Exact text -->
new_string: |
  <!-- Proposed fix -->
```

---

## Editor: Pacing Editor (节奏编辑)

### Findings

<!-- Duplicate the finding format above for each issue -->

---

## Editor: Voice Editor (声音编辑)

### Findings

<!-- Duplicate the finding format above for each issue -->

---

## Editor: Story Editor (故事编辑)

### Findings

<!-- Duplicate the finding format above for each issue -->

---

## Editor: Reader Sim Editor (读者模拟编辑)

### Findings

<!-- Duplicate the finding format above for each issue -->

---

## Editor: Repetition Detection Editor (重复检测编辑)

### Findings

<!-- Duplicate the finding format above for each issue -->

---

## Anti-AI Scan

### Passages Flagged for AI-Like Quality
| Location | Issue | Suggestion |
|----------|-------|------------|
| <!-- Scene N, Para M --> | <!-- e.g., Overly balanced structure, generic phrasing, tells instead of shows --> | <!-- How to make it more human --> |

### Anti-AI Checklist
<!-- 量化阈值见 anti-ai-system.md 附录 和 pre-writing-brief.md Section 3.2-3.3 -->
- [ ] Sentence length variation is natural (段落长度CV ≥ 0.15)
- [ ] Concrete details outweigh abstract descriptions
- [ ] Character observations are imperfect/human (noticing irrelevant things)
- [ ] No symmetrical paragraph structures
- [ ] Characters are allowed to be wrong, petty, or confused
- [ ] Emotional moments earn their impact (not declared)
- [ ] No "as you know, Bob" dialogue
- [ ] Dialogue voices are distinct per character
- [ ] 对话通过换说测试（IR-5 Check 9：≥3行对话段落中，交换说话人后不应仍然自然；信息清单式对话等重罗列必须重写）
- [ ] 高风险词汇密度 ≤ 5个/千字
- [ ] 惊讶词密度 ≤ 1次/3000字（IR-6 Rule 3）
- [ ] 无元叙事标记泄漏（grep `Ch\d+` `第\d+章` `FS-\d+` 零匹配）（IR-5 Check 7, IR-6 Rule 8）
- [ ] 关键数字通过物理合理性检查（IR-6 Rule 9）：时间线连续、脉搏60-100bpm范围、距离/方位与已建立空间一致、旅行速度与交通方式匹配、计数前后一致

---

## Summary of Proposed Changes

| # | Severity | Location | Summary | Status |
|---|----------|----------|---------|--------|
| 1 | <!-- Critical/Major/Minor --> | <!-- Location --> | <!-- One-line summary --> | <!-- Pending / Approved / Applied / Rejected --> |
| 2 | | | | |
| 3 | | | | |

---

## Verdict

<!-- One of: -->

### PASS
No critical or major issues. Minor issues are stylistic preferences. Chapter is ready for the next step.

### REVISE REQUIRED
<!-- Count --> critical and <!-- Count --> major issues need surgical fixes. Apply approved changes and re-run affected editors.

### MAJOR REWORK
<!-- Count --> critical issues indicate fundamental problems. Recommend revisiting the chapter plan before rewriting.

---

## Notes

<!-- Any additional observations, patterns noticed across chapters, or suggestions for future chapters -->
