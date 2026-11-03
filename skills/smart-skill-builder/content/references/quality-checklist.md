# Skill Quality Checklist

Use this after generating a skill to ensure it meets production standards.

---

## Frontmatter

- [ ] `name` is kebab-case, under 64 characters
- [ ] `description` clearly states WHAT the skill does
- [ ] `description` lists WHEN to trigger it (specific phrases, contexts)
- [ ] `description` is "pushy" — it lists synonyms, adjacent use cases, casual phrasings
- [ ] `description` contains no angle brackets, is under 1024 characters

### Description Quality Test
Read the description aloud. Would you trigger this skill if you saw:
- A formal version of the request ("I need to process my quarterly CSV data")
- A casual version ("can u help w/ this spreadsheet lol")
- An adjacent request that needs this skill even if not named directly

If any of those would NOT trigger based on the description, improve it.

---

## Body / Instructions

- [ ] The first section explains WHAT Claude should do in 1–2 sentences
- [ ] Instructions are in imperative form ("Do X", not "You should do X")
- [ ] WHY is explained for non-obvious requirements
- [ ] Output format is defined explicitly, with an example
- [ ] Edge cases are addressed (what to do when input is ambiguous, missing, or malformed)
- [ ] Asks for clarification policy is defined (when to ask vs. proceed with assumptions)
- [ ] Not too long — under 500 lines

---

## Completeness

- [ ] Does the skill reference any scripts that should exist but don't?
- [ ] Are there file transformations that would benefit from a bundled script?
- [ ] Are there large reference documents that should be in `references/` instead of inline?

---

## Anti-patterns to fix

| Anti-pattern | Better approach |
|---|---|
| `ALWAYS use this exact format` | Explain why the format matters |
| `NEVER do X` | Explain what problem X causes |
| Huge wall of numbered instructions | Organize by phases/sections |
| Output format buried in prose | Give it its own section with example |
| Trigger description is one sentence | List synonyms, contexts, user types |
| Body > 500 lines | Move details to references/ |

---

## Description Pushiness Scale

**1 (too passive)**: "Skill for converting files"  
**3 (ok)**: "Use when user wants to convert between file formats"  
**5 (good)**: "Use when user wants to convert files, change formats, transform data between types, or says things like 'change this to PDF', 'I need an xlsx', 'convert my CSV' — even if they don't mention the output format"  
**10 (overdone)**: Pages of scenarios. Keep it focused.

Aim for a 4–5.
