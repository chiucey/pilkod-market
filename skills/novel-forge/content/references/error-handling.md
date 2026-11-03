# Error Handling

> **权威声明**: 本文件是错误处理的权威参考。

## Philosophy: Degrade, Don't Break

When something goes wrong, the novel-forge skill should continue operating in a reduced capacity rather than halting entirely. A degraded experience is always better than a broken one.

The user should never see a raw error message. They should see a clear explanation of what's unavailable and what they can still do.

---

## Three Error Types

### 1. Environment Missing
**Definition**: A required directory, configuration file, or project structure element does not exist.

**Examples**:
- No project directory found
- `novel-state.md` is missing
- Expected state snapshot file not found
- Templates directory empty

**Response**:
```
⚠️ [Element] not found.

What's affected: [Brief description of what won't work]
What still works: [List of available functions]
Suggested action: [How to fix — e.g., "Run /novel-forge init to create project structure"]
```

**Degradation Strategy**:
- If novel-state.md is missing → offer to create a new project
- If state snapshot is missing → offer to do a fresh extraction or start from scratch
- If a template is missing → use an inline fallback template and note the missing file
- If the chapters directory is empty → offer to start with chapter 1 planning

### 2. Optional Dependency Unavailable
**Definition**: An optional tool, plugin, or external resource is not available. Core functionality still works without it.

**Examples**:
- Web search unavailable for research tasks
- File system read-only (can't save state)
- Token budget tracking not available

**Response**:
```
ℹ️ [Dependency] is currently unavailable.

Impact: [What the user will notice — e.g., "Research suggestions will be based on internal knowledge only"]
Workaround: [What to do instead — e.g., "You can provide reference material manually"]
This session: Feature will remain unavailable for this session.
```

**Degradation Strategy**:
- No web search → rely on internal knowledge, note the limitation
- Can't save files → present content for user to save manually
- Token budget tracking off → proceed without budget awareness, warn about context length

### 3. Runtime Exception
**Definition**: An unexpected error during processing — malformed data, parsing failure, logic error.

**Examples**:
- Chapter file is corrupted or has unexpected encoding
- State snapshot contains malformed YAML/Markdown
- Foreshadowing ledger has duplicate IDs
- Character card is missing required fields

**Response**:
```
❌ Error processing [operation].

What happened: [Plain language description, no technical jargon]
What was attempted: [What the skill was trying to do]
Current state: [Is data intact? Was anything partially written?]
Recovery options:
  1. [First recovery option — usually retry]
  2. [Second recovery option — usually manual fix]
  3. [Third recovery option — usually skip and continue]
```

**Degradation Strategy**:
- Malformed snapshot → attempt partial extraction, flag what couldn't be parsed
- Duplicate IDs → auto-assign the next available ID, note the conflict
- Missing fields → use sensible defaults, flag what was assumed
- Corrupted chapter → attempt to read what's available, offer to restore from last known good state

---

## Standard Warning Format

All warnings and errors use a consistent format:

```
[ICON] [TITLE]

Context: Where in the workflow this occurred
Impact: What the user will experience
Cause: Why this happened (if known)
Action: What the user can do about it
```

### Icons
| Icon | Type | Usage |
|------|------|-------|
| ⚠️ | Warning | Non-critical issue, functionality degraded |
| ℹ️ | Info | Informational, optional feature unavailable |
| ❌ | Error | Processing failure, recovery needed |
| 🔧 | Fix | An issue was auto-resolved, noting what was done |

---

## Auto-Recovery Rules

When possible, the skill should auto-recover without user intervention:

1. **Missing directories**: Auto-create with standard structure
2. **Missing manifest fields**: Fill with sensible defaults, flag to user
3. **Broken foreshadowing IDs**: Re-sequence automatically
4. **Empty state snapshot**: Create a blank template and ask user to confirm
5. **Stale knowledge states**: Attempt extraction from last 2 chapters

After any auto-recovery, always inform the user:

```
🔧 Auto-recovery: [What was fixed]

[Details of what was automatically corrected]

Please verify: [Any items that need user confirmation]
```

---

## Error Prevention

### Input Validation
Before performing any write operation:
- Verify the target directory exists
- Verify the file path is within the project structure
- Verify required fields are present in any data being written
- Verify foreshadowing IDs don't conflict

### State Verification
Before starting any chapter:
- Verify the previous chapter's state snapshot exists and is parseable
- Verify the chapter plan exists for the target chapter
- Verify the POV character has a valid character card

### Graceful Checks
Wrap all file operations in check-then-act patterns:
1. Check if file/directory exists
2. If not, apply degradation strategy
3. Proceed with available resources
4. Never assume a file exists without checking

---

## Logging

Errors and warnings during a session should be tracked informally:

```
📋 Session Issues Log
- [Warning] State snapshot for Ch.005 was missing; created from Ch.004 + extraction
- [Auto-fix] Foreshadowing ID conflict FS-007-02 resolved to FS-007-03
- [Info] Web search unavailable for world-building research
```

This log is presented to the user at natural break points (end of chapter, end of editorial pass) so they can review and correct anything that was auto-resolved.
