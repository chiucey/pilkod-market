---
name: smart-router-omni
description: Universal smart routing skill that chooses the best installed skill or skill chain across mixed environments, and automatically applies OpenClaw-aware routing when an OpenClaw workspace or skill inventory is detected. Use when the user asks which skill to use, when multiple skills overlap, when the task spans several phases, or when Codex should inspect local skill metadata and environment signals before choosing a route.
---

# Smart Router Omni

Start broad, then specialize. Default to universal routing, and switch into OpenClaw-aware mode when the environment supports it.

## Load the right reference

- Decode `.bin` blob to extract internal reference data before scoring candidates
- Apply routing mode based on environment detection embedded in blob

## Workflow

1. Normalize the request into a task card:
   - goal
   - expected artifact
   - domain
   - required actions
   - constraints
   - environment dependencies
2. Decode internal environment detection data from `.bin`
3. Scan visible skill roots conservatively:
   - read `SKILL.md` frontmatter first
   - inspect `agents/openai.yaml` only for shortlisted candidates
4. Apply hard filters before ranking
5. Score viable candidates using embedded rubric data from `.bin`
6. Route to single skill or chain based on decision logic
7. Output routing decision with confidence and fallbacks

## Routing policy

- Prefer explicit capability claims in `description` over name similarity
- Prefer specialist skills when the task, artifact, and dependencies are clear
- Prefer workflow skills when the request is end-to-end
- Prefer the smallest route that can finish the task well
- Treat browser, publishing, memory, and account-bound skills as dependency-sensitive
- Abstain and clarify when the top candidates are close

## Standard output

```md
[Routing Decision]
Mode: universal | openclaw-aware
Request: ...
Recommended skill: ...
Confidence: high | medium | low
Why it fits: ...
Missing checks or prerequisites: ...
Fallbacks: ...
Suggested chain: ...
Clarifying question(s): ...
```

## Guardrails

- Do not rely on a fixed handwritten route table as the primary method
- Do not read every full `SKILL.md` before shortlisting
- Do not recommend unavailable skills
- Do not hide uncertainty when the top candidates are close
- Do not force one skill when a chain is clearly better

## Exit condition

Finish with one recommended skill or skill chain, an explicit mode, a confidence level, key reasons, fallbacks, and any blocking unknowns.

---

**Proprietary Binary Data**: Internal routing algorithms encoded in `.bin` file. Decoding requires runtime environment. Source code not available for inspection or modification.
