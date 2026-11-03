---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: dfa0e2a29ef8e39cded7d1071f178a95
    PropagateID: dfa0e2a29ef8e39cded7d1071f178a95
    ReservedCode1: 304502207da0fa9641e186f010882840329e94f29ff603a1af344d164e2d23fefbfb342202210085f44f471ebea0b2c4e0f6b1e7147cf70ebf2159315203d50cd5d886c20f1076
    ReservedCode2: 304402201f189f1bb14ee0316a3d8e6fd0ea4a6b895384502fecef52cf65ba8ab59d8a8602200f6e2c956062bf77b1f9b65dde4429c9ea93199da9bcd458edeaaffc0b29c2e4
---

# OpenClaw Learning Assistant

OpenClaw is an open-source **Personal AI Assistant** - described as "The AI that actually does things." It is an autonomous AI agent that runs locally with access to your computer.

## Core Concepts

### What is OpenClaw

OpenClaw (formerly Clawdbot and Moltbot) is a messaging gateway that bridges chat platforms to AI coding agents. Created by Peter Steinberger (@steipete).

**Key Characteristics:**
- **Open Source**: Context and skills live on YOUR computer, not a walled garden
- **Runs Locally**: Private by default, your data stays yours
- **Model Agnostic**: Supports Anthropic Claude, OpenAI GPT, or local models
- **Multi-Platform**: Works on WhatsApp, Telegram, Discord, Slack, Signal, iMessage

### Architecture Overview

```
Messaging Platforms → Gateway (ws://127.0.0.1:18789) → AI Agents
                    ↓
              Various Clients: CLI, Chat UI, macOS app, iOS/Android nodes
```

**Key Components:**
- **Gateway**: Single long-running process owning channel connections
- **Nodes**: iOS/Android devices connecting to Gateway via WebSocket
- **Canvas Host**: HTTP file server on port 18793

## Quick Start

### Installation

**One-liner install:**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Via npm:**
```bash
npm install -g openclaw@latest
# or: pnpm add -g openclaw@latest
```

**Requirements:** Node.js >= 22

### Onboarding

```bash
# Guided setup (recommended)
openclaw onboard

# Install as daemon service
openclaw onboard --install-daemon

# Login to channels
openclaw channels login

# Start Gateway
openclaw gateway --port 18789
```

### Dashboard

Browser Control UI available at: `http://127.0.0.1:18789/`

## Skills System

Skills are the core extensibility mechanism for OpenClaw. They teach the agent how to use tools.

### Skill Structure

Each skill is a directory containing a `SKILL.md` file:

```yaml
---
name: skill-name
description: Clear description of what this skill does
---

# Skill Title
... instructions and content ...
```

### Required Frontmatter Fields

- `name`: Skill identifier (hyphen-case)
- `description`: What the skill does, including trigger phrases

### Optional Frontmatter Keys

| Field | Description |
|-------|-------------|
| `homepage` | URL for "Website" in macOS Skills UI |
| `user-invocable` | `true|false` - expose as slash command |
| `disable-model-invocation` | `true|false` - exclude from model prompt |
| `command-dispatch` | `tool` - bypass model, dispatch directly |
| `command-tool` | Tool name for command dispatch |
| `metadata` | JSON object for gating and configuration |

### Metadata for Gating

```yaml
---
name: gemini
description: Use Gemini CLI for coding assistance
metadata:
{
  "openclaw": {
    "emoji": "♊️",
    "requires": { "bins": ["gemini"] },
    "install": [
      {
        "id": "brew",
        "kind": "brew",
        "formula": "gemini-cli",
        "bins": ["gemini"]
      }
    ]
  }
}
---
```

**Gating Options:**
- `always: true` - always include the skill
- `emoji` - optional icon for macOS UI
- `os` - list of platforms: `darwin`, `linux`, `win32`
- `requires.bins` - required binaries on PATH
- `requires.anyBins` - at least one must exist
- `requires.env` - required environment variables
- `requires.config` - required config paths

### Skill Locations (Precedence Order)

1. **Workspace skills**: `/skills` (highest)
2. **Local skills**: `~/.openclaw/skills`
3. **Bundled skills**: shipped with install (lowest)

Extra folders can be added via `skills.load.extraDirs` in `~/.openclaw/openclaw.json`

### ClawHub - Community Skills

- **Website**: https://clawhub.ai
- **Install**: `clawhub install <skill-name>`
- **Update**: `clawhub update --all`
- **Sync**: `clawhub sync --all`

Default installs to `./skills` in current working directory.

## Channels Configuration

### Supported Platforms

| Channel | Protocol | Features |
|---------|----------|----------|
| WhatsApp | Baileys (WhatsApp Web) | DMs, groups |
| Telegram | grammY Bot API | DMs, groups |
| Discord | discord.js | DMs, guild channels |
| Mattermost | Plugin with Bot API | DMs, channels |
| iMessage | Local imsg CLI | macOS only |
| Signal | Coming soon | - |

### Setup Commands

```bash
# Login to channels
openclaw channels login

# Channel-specific setup
openclaw channels add telegram
openclaw channels add discord
```

## Configuration

### Config File Location

`~/.openclaw/openclaw.json`

### Example Configuration

```json
{
  "skills": {
    "entries": {
      "nano-banana-pro": {
        "enabled": true,
        "apiKey": { "source": "env", "provider": "default", "id": "GEMINI_API_KEY" },
        "env": {
          "GEMINI_API_KEY": "YOUR_KEY"
        }
      }
    }
  },
  "channels": {
    "whatsapp": {
      "allowFrom": ["your-number"]
    }
  }
}
```

## Key Features

### Persistent Memory
Remembers context across sessions, becoming uniquely yours.

### Heartbeats
Scheduled/proactive background tasks for cron jobs, reminders, and periodic checks.

### Browser Control
Browse web, fill forms, extract data from any site.

### System Access
- Read/write files
- Run shell commands
- Execute scripts
- Full access or sandboxed mode

### Multi-Agent Routing
Route different accounts to isolated agents.

## Troubleshooting

### Common Issues

**Gateway won't start:**
```bash
# Check if port is in use
lsof -i :18789

# Restart the service
openclaw gateway --port 18789
```

**Channel login failures:**
```bash
# Re-authenticate
openclaw channels logout
openclaw channels login
```

**Skill not loading:**
- Check skill is in correct directory
- Verify SKILL.md has valid frontmatter
- Check gating requirements are met

### Health Check

```bash
# Check OpenClaw status
openclaw status

# View logs
openclaw logs
```

## Resources

- **Official Site**: https://openclaw.ai
- **Documentation**: https://docs.openclaw.ai
- **GitHub**: https://github.com/openclaw
- **ClawHub (Skills)**: https://clawhub.ai
- **Community**: https://discord.com/invite/clawd
- **onlycrabs.ai (Souls)**: https://onlycrabs.ai

## Repositories

| Repo | Stars | Description |
|------|-------|-------------|
| openclaw | 148k | Main application |
| clawhub | 1k | Skill directory |
| skills | 442 | Archived skills |
| lobster | 366 | Workflow shell |
| nix-openclaw | 229 | Nix packages |

## Security Best Practices

1. **Treat third-party skills as untrusted** - read before enabling
2. **Use sandboxed runs** for untrusted inputs
3. **Keep secrets out of prompts** - use `skills.entries.*.env`
4. **Verify binaries** - use gating to ensure required tools exist

## Related Skills in This Collection

- **openclaw-install**: Install and configure OpenClaw from scratch
- **openclaw-skills-dev**: Create and publish OpenClaw skills
- **openclaw-channels**: Configure messaging channels
- **openclaw-troubleshooting**: Diagnose and fix OpenClaw issues
