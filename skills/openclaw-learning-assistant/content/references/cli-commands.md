---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fb8cb168aacdb559984587b0783f8995
    PropagateID: fb8cb168aacdb559984587b0783f8995
    ReservedCode1: 30450221009d5fa885e9317469c87dcce1fb90d3a4678fec469026eb761699b624d9b004be02200ce05d961c135d8b00e458e9c87b3cbb1916c8f1ce95b723ac7dae230beb25ad
    ReservedCode2: 304402201cf609a86f437c0a59bc6c586340f56bd1b73a449dd3ee8da6491704c503a6240220760b4d8755edcb714a08f3ed0616ce47741e3356f85c88b1d6672182e8ae5f36
---

# OpenClaw CLI Quick Reference

## Installation & Setup

```bash
# One-liner install
curl -fsSL https://openclaw.ai/install.sh | bash

# npm install
npm install -g openclaw@latest

# Install via git (hackable)
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git

# Onboarding
openclaw onboard
openclaw onboard --install-daemon
```

## Gateway Management

```bash
# Start gateway
openclaw gateway --port 18789

# Check status
openclaw status

# View logs
openclaw logs

# Restart service
openclaw restart
```

## Channel Management

```bash
# Login to channels
openclaw channels login

# Logout from channels
openclaw channels logout

# Add specific channel
openclaw channels add telegram
openclaw channels add discord

# Check channel status
openclaw channels status
```

## Skills Management

```bash
# Install from ClawHub
clawhub install <skill-name>

# Update all skills
clawhub update --all

# Sync skills
clawhub sync --all

# List installed skills
clawhub list

# Remove skill
clawhub uninstall <skill-name>
```

## Configuration

```bash
# Open config file
openclaw config edit

# View current config
openclaw config show

# Validate config
openclaw config validate
```

## Health & Diagnostics

```bash
# Check health
openclaw health

# Debug mode
openclaw --debug

# Version info
openclaw --version
```

## Ports & Network

| Port | Service | Description |
|------|---------|-------------|
| 18789 | Gateway | WebSocket control plane |
| 18793 | Canvas | HTTP file server for nodes |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `CLAWHUB_DISABLE_TELEMETRY` | Disable telemetry (set to 1) |

## Config File Locations

- **Main config**: `~/.openclaw/openclaw.json`
- **Skills directory**: `~/.openclaw/skills`
- **Logs**: `~/.openclaw/logs/`
- **Cache**: `~/.openclaw/cache/`
