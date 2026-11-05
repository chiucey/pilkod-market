---
name: coding-agent
description: 'Delegate coding tasks to Codex, Claude Code, or Pi agents via background process. Use when: (1) building/creating new features or apps, (2) reviewing PRs (spawn in temp dir), (3) refactoring large codebases, (4) iterative coding that needs file exploration. NOT for: simple one-liner fixes (just edit), reading code (use read tool), thread-bound ACP harness requests in chat.'
metadata: {"openclaw": {"emoji": "🧩", "requires": {"anyBins": ["claude", "codex", "opencode", "pi"]} } }
---

# Coding Agent (bash-first)

Use **bash** (with optional background mode) for all coding agent work. Simple and effective.

## ⚠️ PTY Mode: Codex/Pi/OpenCode yes, Claude Code no

For **Codex, Pi, and OpenCode**, PTY is still required (interactive terminal apps):

```bash
# ✅ Correct for Codex/Pi/OpenCode
bash pty:true command:"codex exec 'Your prompt'"
```

For **Claude Code** (`claude` CLI), use `--print --permission-mode bypassPermissions` instead:

```bash
# ✅ Correct for Claude Code (no PTY needed)
cd /path/to/project && claude --permission-mode bypassPermissions --print 'Your task'
```

## Quick Start

```bash
# One-shot task with Codex (remember PTY!)
bash pty:true workdir:~/project command:"codex exec 'Add error handling to the API calls'"

# Background task
bash pty:true workdir:~/project background:true command:"codex exec --full-auto 'Build a snake game'"
```

## Claude Code

```bash
# Foreground
bash workdir:~/project command:"claude --permission-mode bypassPermissions --print 'Your task'"

# Background
bash workdir:~/project background:true command:"claude --permission-mode bypassPermissions --print 'Your task'"
```

## Process Tool Actions

| Action | Description |
| ------ | ----------- |
| `list` | List all running/recent sessions |
| `poll` | Check if session is still running |
| `log` | Get session output |
| `write` | Send raw data to stdin |
| `submit` | Send data + Enter |
| `kill` | Terminate the session |

## Rules

1. **Use the right execution mode per agent:**
   - Codex/Pi/OpenCode: `pty:true`
   - Claude Code: `--print --permission-mode bypassPermissions`
2. **Never start Codex in ~/.openclaw/** - it will read your config files!
3. **Be patient** - don't kill sessions because they're "slow"
4. **Monitor with process:log** - check progress without interfering
