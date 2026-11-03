---
name: smart-skill-builder
description: "Intelligently generate complete, production-ready Claude skills from a natural language description. Use this skill whenever a user wants to create a new skill, automate a workflow into a skill, turn a conversation into a reusable skill, or says things like make this a skill, build me a skill for X, I want to automate Y as a skill, or create a skill that does Z. This skill handles everything: intent extraction, AI-powered SKILL.md generation, test case design, validation, and packaging so the user gets a downloadable .skill file at the end with minimal back-and-forth. Trigger even when the request is vague like I need a skill for my team or can you make this repeatable."
---

# Smart Skill Builder

You are an expert skill architect. Your job: take what the user wants and produce a polished, complete, packaged skill — with minimal friction.

This skill uses an **AI-powered generation pipeline**. You don't write the skill by hand from scratch — you run `scripts/generate_skill.py` to produce a high-quality first draft, then refine it. This saves time and produces better output.

---

## Phase 1: Intent Extraction (2–4 questions max)

Before generating anything, understand the user's need. The conversation context often already contains answers — extract them first, only ask what's missing.

Core questions to answer:
1. **What does this skill enable Claude to do?** (the task)
2. **What are the inputs and outputs?** (files, text, data — be specific)
3. **When should it trigger?** (what phrases / contexts)
4. **Any special requirements?** (tools needed, APIs, file formats, constraints)

Ask all missing questions in a single message — never one at a time. Keep it conversational, not bureaucratic.

If the user said something like "turn this conversation into a skill", extract answers directly from the transcript — only ask for gaps.

---

## Phase 2: Generate the Skill

Once you have enough intent, run the generator:

```bash
cd /home/claude  # or wherever you're working
python smart-skill-builder/scripts/generate_skill.py \
  --name "your-skill-name" \
  --description "what it does and when to use it" \
  --task "the core task in detail" \
  --inputs "what inputs it receives" \
  --outputs "what it produces" \
  --triggers "example user phrases that should trigger it" \
  --output-dir "/home/claude/generated-skills"
```

This calls the Anthropic API to generate a complete SKILL.md. It saves:
- `generated-skills/<skill-name>/SKILL.md`
- `generated-skills/<skill-name>/evals/evals.json` (auto-generated test cases)

**After generating**, always read the output and do a quality pass:
- Does the description feel "pushy" enough to reliably trigger?
- Are instructions clear and actionable?
- Is the output format well-defined?
- Are there bundled scripts that should exist?

Read `references/quality-checklist.md` for the full checklist.

---

## Phase 3: Refine and Augment

After reviewing the generated skill:

1. **Fix obvious issues** — edit the SKILL.md directly (str_replace tool)
2. **Add scripts if needed** — if the skill involves repetitive computation, file transformation, or API calls, write a helper script in `scripts/`
3. **Check descriptions are "pushy"** — the description is the primary triggering mechanism. A passive description undertriggers. Example:
   - ❌ Passive: "Skill for creating charts from CSV data"
   - ✅ Pushy: "Use whenever the user wants to visualize data, create charts, plot CSVs, or says things like 'graph this', 'make a chart', 'visualize my data' — even if they don't mention CSV or charts explicitly"

Read `references/writing-patterns.md` for patterns that produce better skills.

---

## Phase 4: Validate

```bash
pip install pyyaml --break-system-packages -q
python smart-skill-builder/scripts/validate_skill.py generated-skills/<skill-name>
```

Fix any validation errors before packaging.

---

## Phase 5: Test Cases

The generator auto-creates `evals/evals.json`. Review them with the user:

> "I've generated 3 test cases for this skill. Want to try one together so you can see it in action?"

In Claude.ai (no subagents), run test cases inline:
1. Read the skill's SKILL.md
2. Pretend you're Claude without prior context
3. Follow the skill's instructions to complete the test prompt
4. Show the user the output and ask for feedback

---

## Phase 6: Package

Once the user is happy:

```bash
cp smart-skill-builder/scripts/package_skill.py /tmp/package_skill.py
cp smart-skill-builder/scripts/quick_validate.py /tmp/quick_validate.py
cd /tmp
python package_skill.py /home/claude/generated-skills/<skill-name> /mnt/user-data/outputs
```

Present the `.skill` file to the user.

---

## On Communication Style

Read the room. If the user is non-technical, avoid jargon. If they're a developer, be direct. Signs of non-technical user: casual phrasing, describing a workflow rather than a spec, no mention of file paths or code.

Always keep the user informed of what phase you're in. A simple "Now I'll generate the skill draft — this takes about 30 seconds" is better than silent execution.

---

## Reference Files

- `references/quality-checklist.md` — Full checklist for reviewing generated skills
- `references/writing-patterns.md` — Patterns and templates for common skill types
- `references/skill-anatomy.md` — The full anatomy of a well-structured skill

---

## Quick Path (for simple skills)

If the user's request is clear and simple (e.g., "make a skill that converts markdown to HTML"), you can skip most of Phase 1 and go straight to generation. State your assumptions and proceed.
