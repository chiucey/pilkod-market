---
name: practice-problem-sequence-designer
description: "Generate a sequenced set of practice problems with progressive difficulty, surface-feature variation, and error-targeting. Use when the user asks for practice problems, exercise sets, worksheets, homework, or any set of problems to practise a learned skill."
metadata:
  display_name: 循序渐进练习题生成器
---

# Practice Problem Sequence Designer

Help design a sequenced set of practice problems that follows principles of **near-to-far transfer**, **surface feature variation**, and **error-targeting**. Most LLM-generated practice sets are uniformly difficult and uniformly worded — this skill exists to do better.

## Step 1: Delegate to the built-in writing skill (BLOCKING — do this first)

Before generating any problems or producing any document, call `load_skill` with `skill_name="writing"` as a standalone first step. The writing skill owns the document-generation pipeline (HTML → PDF conversion, `publish_artifact` delivery, etc.). Do NOT attempt to `import docx`, use `python-docx`, or build any document file from scratch — those paths fail in the sandbox because `python-docx` is not available and the rendering pipeline belongs entirely to the built-in writing skill.

Once `load_skill(skill_name="writing")` returns and you have read its instructions, come back here and apply the problem-design rules below when composing the document content.

> **Forbidden imports (hard ban):** `from docx import Document`, `import docx`, `python-docx`, or any direct construction of `.docx` / `.pdf` binary files. All document output must go through the writing skill's pipeline.

## Why sequencing matters

Rosenshine (2012) identified guided and independent practice as core teaching principles, requiring scaffolded progression and high success rates (~80%) before scaffolds are removed. Sweller et al.'s (2019) **variability effect** shows that practising with varied problem types promotes schema abstraction and transfer, while practising with identical problems produces rigid, context-bound knowledge. Atkinson et al. (2000) demonstrated that surface-feature variation is critical: students who only practise problems that look like the taught example fail when problems look different. Bjork & Bjork (2011) frame this as "desirable difficulty" — practice that feels harder produces better long-term learning.

## The progression

A good practice sequence moves through four zones:

1. **Near transfer (first ~20% of problems)** — Nearly identical to the taught example. Same structure, similar numbers, same context. Target ~90% success rate. These build confidence and confirm basic understanding.

2. **Surface variation (next ~30%)** — Same underlying skill, **different** context, numbers, format, or presentation. The learner must recognise the same skill in a new wrapper. *If the example used apples, switch to temperatures, distances, money — never just "more apple problems."*

3. **Increased complexity (next ~30%)** — Additional steps, missing information to infer, or combining this skill with a previously learned one.

4. **Far transfer (final ~20%)** — Looks substantially different from the taught example but requires the same underlying skill. May be embedded in a larger problem or a novel context.

## Non-negotiable design elements

For any practice set, include:

- **At least 2 error-targeting problems.** Specifically designed to surface known common errors. If you don't know the common errors, infer the 2-3 most likely ones for this skill and design problems where the wrong approach gives a plausible-looking answer.

- **At least 1 "twist" problem.** A problem that *looks* like it requires this skill but actually doesn't — or that requires the learner to explain why the skill doesn't apply. This tests whether the learner is thinking or just applying a procedure mechanically. Critical for preventing rote pattern matching.

- **Scaffold reduction.** Early problems may include partial scaffolds (a hint, a first step, a formula reminder). Middle problems remove these. Later problems require the learner to determine the method independently.

## What to include in the output

For each problem, provide:
- The problem itself
- A brief **design intent** note (why this problem at this position — what it tests that previous problems didn't)
- Difficulty zone (near transfer / surface variation / complexity / far transfer)
- Common error to watch for, where applicable

After the sequence, also provide:
- **Scaffold reduction summary** — how scaffolding decreases across the sequence
- **Differentiation note** — how to support struggling learners (which problems to prioritise) and how to extend confident ones (which to add)

The exact structure can flex based on what the user asked for — these are the elements that matter, not a rigid template.

## Answer-option distribution rule (multiple-choice problems)

When generating multiple-choice problems, the position of the correct answer **must be randomised with equal probability across all option slots** (A, B, C, D or equivalent). This rule exists because predictable answer patterns (e.g. correct answer always in position B, or always in the last slot) allow test-wise guessing and undermine the diagnostic value of the exercise.

**Concrete requirement:** across any set of N multiple-choice problems, each option slot must receive the correct answer approximately N/4 times (for 4-choice items). The distribution must be irregular — no runs of the same correct-answer position longer than 2 or 3 consecutive problems. Actively check the planned answer key before finalising; if you notice a cluster (e.g. five questions in a row where the correct answer is В), redistribute.

**How to achieve this in practice:**
1. Draft all problems and their correct answers first.
2. Independently assign a random slot (А, Б, В, or Г) to each correct answer — do not let the answer slot be influenced by the problem's content.
3. Fill the remaining slots with plausible distractors.
4. Before writing the final document, tally the answer-key distribution and re-shuffle any slot that appears more than ~30% of the time.

## PDF pagination rule

When the output is a PDF document (the most common delivery format for this skill), apply the following pagination logic:

- **One mandatory page break**: place a forced page break **only** between the cover page and the first problem. This ensures the cover stands alone on page 1 and the problems start cleanly on page 2.
- **No other forced page breaks**: do not insert `break-before: page` or `page-break-before: always` between problem sections, between parts of the problem set, or at any other position in the document body. Allow the PDF renderer to flow content naturally across pages.
- The rationale: forced mid-document page breaks leave large blank gaps when problem blocks happen to end near a natural page boundary, wasting paper and looking unprofessional. Natural flow produces compact, well-filled pages.

**In HTML (the source for PDF conversion):** implement the cover break with `<div style="break-before: page"></div>` immediately after the cover block. Do not add this element anywhere else in the document.

## Hard constraints (non-negotiable)

These are not suggestions. Apply them on every generation:

1. **Delegate to the writing skill first (Step 1).** Call `load_skill(skill_name="writing")` before writing any document. Never use `python-docx` or direct binary file construction.
2. **Label every problem** with its difficulty zone (Near transfer / Surface variation / Complexity / Far transfer). Do not output bare problems without labels.
3. **Surface features must actually vary across the sequence.** If the worked example was about apples, do not output 10 apple problems. Switch contexts: temperature, distance, money, recipes, populations. A sequence where every problem has the same context is a failure of this skill.
4. **Include at least 2 error-targeting problems.** These must be designed so that the most likely wrong approach gives a plausible-looking answer, forcing the learner to think carefully. If common errors weren't provided, infer the 2-3 most likely ones for the skill.
5. **Include at least 1 twist problem.** A problem that looks like it requires this skill but actually doesn't, or that requires the learner to recognise why the skill doesn't apply. This is the single most important defence against rote pattern matching.
6. **Randomise answer-option positions** for multiple-choice problems. Check the answer-key distribution before finalising; no slot should hold the correct answer more than ~30% of the time, and there must be no long runs of the same correct-answer position.
7. **Apply the PDF pagination rule.** One forced page break after the cover; no forced page breaks elsewhere.
8. **Before returning, self-check:** (a) do problems progress from near to far transfer? (b) do surface features actually vary, or did I just change numbers? (c) are at least 2 problems error-targeting and is at least 1 a twist? (d) is the first problem accessible enough for ~90% success? (e) is the answer-key distribution roughly even and non-patterned? (f) is there exactly one forced page break (after the cover)?

## Example

**Skill:** Calculating percentage increase and decrease (Year 9, just saw worked example "find 15% of £240 and add it to the original", 10 problems, common errors: forgetting to add/subtract the percentage; calculating percentage of new amount instead of original)

1. **Increase £80 by 25%.** *Near transfer — almost identical to the example. Method reminder provided. Targets ~90% success.*
2. **A £150 jacket is increased by 10%. What is the new price?** *Near transfer — same context (money), slightly different surface.*
3. **The temperature was 40°C. It dropped by 15%. What is the new temperature?** *Surface variation — switches from money to temperature. Same underlying calculation. **Common error to watch:** forgetting to subtract.*
4. **A car drove 200 km. The distance increased by 35% the next day. How far did it drive on day two?** *Surface variation — distance context.*
5. **A shop has 80 items in stock. After a delivery, stock increases by 45%. After a sale, stock decreases by 20%. How many items are in stock now?** *Increased complexity — two-step. **Common error:** applying the second percentage to the original 80 instead of the new total.*
6. **A coat costs £60 after a 25% discount. What was the original price?** *Increased complexity — reverse percentage. Most learners will instinctively add 25% of £60, which is wrong.*
7. **Population grew from 12,000 to 15,000. By what percentage did it increase?** *Far transfer — finding the percentage rather than applying one.*
8. **(Twist problem)** **A shop offers "20% off, then an extra 10% off the discounted price." A customer claims this is the same as 30% off. Are they correct? Explain.** *Twist — looks like compound percentage but the real task is to recognise that successive discounts ≠ summed discounts.*
9. **A house was bought for £200,000 and sold three years later for £230,000. What was the percentage profit?** *Far transfer — finding percentage in a real-world context.*
10. **A recipe for 4 people uses 600g of flour. To serve 6 people, how much flour is needed? Express the increase as a percentage.** *Far transfer — combines proportional reasoning with percentage calculation.*

**Scaffold reduction:** Problems 1-2 include the "find the percentage, then add/subtract" method reminder. Problems 3-5 remove the reminder. Problems 6+ require the learner to identify the method themselves.

**Differentiation:**
- **Support:** Struggling learners do problems 1, 2, 3, 5 only — these cover the core skill without the reverse-percentage trap.
- **Extension:** Confident learners skip 1-2 and add a compound interest problem after #10.

## Limitations to flag

- The problems are generated from general subject knowledge — verify they match the curriculum the learner is studying.
- The 90% success rate for near-transfer problems is a target, not a guarantee — adjust difficulty based on actual learner performance.
