---
name: pua-persistence-debugger
description: A debugging persistence skill that forces exhaustive problem-solving. Use when users ask for debugging help or report errors that haven't been solved after initial attempts.
---

# Persistence Debugger

A debugging methodology that prevents premature surrender and ensures exhaustive problem-solving.

## Core Principles

### Three Red Lines (Unbreakable Boundaries)

1. **Close the Loop** - "Done" requires evidence. Always verify your fix works.
2. **Fact-Driven** - Verify before assuming. Don't guess the root cause.
3. **Exhaust Everything** - Complete all 5 steps before saying "can't solve".

### Pressure Escalation System

| Level | When | Action |
|-------|------|--------|
| L0 | First attempt | Normal systematic debugging |
| L1 | Second attempt | Try a completely different approach |
| L2 | Third attempt | Research underlying logic, generate 3 hypotheses |
| L3 | Fourth attempt | Use 7-point checklist |
| L4 | Fifth+ attempt | Ask for help with detailed context |

## 7-Point Checklist

Every debugging attempt must verify:

1. **Error logs** - Read the full error message and stack trace
2. **Environment** - Check versions, OS, config settings
3. **Dependencies** - Verify packages, libraries are compatible
4. **Alternative approaches** - Try a different method entirely
5. **Documentation** - Check official docs for similar issues
6. **Rollback options** - Can you revert to a working state?
7. **Root cause analysis** - What actually caused the bug?

## 5-Step Debugging Methodology

1. **Reproduce** - Get the error to happen consistently
2. **Isolate** - Find exactly which component/line causes it
3. **Hypothesize** - Form a theory about why it fails
4. **Test** - Verify your hypothesis with targeted changes
5. **Verify** - Confirm the fix works and doesn't break anything else

## Usage

When helping with debugging:

1. Apply the 5-step methodology systematically
2. If first approach fails, escalate to try different approaches
3. Use the 7-point checklist to ensure thoroughness
4. Never give up after one or two failed attempts
5. Document what was tried to help future debugging

## Example Response Style

```
I found the issue. Let me verify the fix:

1. Reproduced: Error occurs when config file is missing
2. Isolated: It's the file existence check on line 42
3. Hypothesis: Default config not being loaded
4. Tested: Added fallback default config
5. Verified: Error no longer occurs, existing tests pass
```

## When to Escalate

- L0→L1: First fix attempt didn't work
- L1→L2: Alternative approach also failed
- L2→L3: Still stuck after research and hypotheses
- L3→L4: After exhaustive checklist, still unsolved

Remember: Most bugs can be solved with systematic debugging. Don't give up early.
