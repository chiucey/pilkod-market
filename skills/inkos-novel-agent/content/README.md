# InkOS Novel Agent - Configuration Guide

## Quick Start

### 1. Configure LLM Provider

Before using InkOS, you need to configure your LLM provider:

```bash
# Set global configuration
inkos config set-global \
  --provider openai \
  --base-url https://api.openai.com/v1 \
  --api-key YOUR_API_KEY \
  --model gpt-4o
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Initialize Project

```bash
inkos init my-novel
cd my-novel
```

### 3. Create Book

```bash
inkos book create --title "逆天改命" --genre xianxia
```

### 4. Write Chapter

```bash
inkos write next my-novel
```

### 5. Export

```bash
inkos export my-novel
inkos export my-novel --format epub
```

## Supported Genres

- xianxia (仙侠)
- xuanhuan (玄幻)
- urban (都市)
- scifi (科幻)
- romance (言情)
- thriller (悬疑)
- horror (惊悚)
- historical (历史)
- fantasy (奇幻)

## Multi-Model Routing

Configure different models for different agents:

```bash
# Writer agent - creative tasks
inkos config set-model writer gpt-4o --provider openai

# Auditor agent - fast checking
inkos config set-model auditor gpt-4o-mini --provider openai

# View current routing
inkos config show-models
```

## Style Imitation

```bash
# Analyze style from reference text
inkos style analyze my-reference.txt

# Import style to book
inkos style import fingerprint.json my-novel
```

## AIGC Detection

```bash
# Detect AI-written content
inkos detect my-novel 5

# Anti-detection rewrite
inkos revise --mode anti-detect my-novel 5
```

## Notification Setup

### Telegram

```bash
inkos config set-global --notify-telegram BOT_TOKEN CHAT_ID
```

### Webhook

```bash
inkos config set-global --notify-webhook https://your-webhook.com/notify
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| INKOS_LLM_PROVIDER | Provider: openai/anthropic/custom | - |
| INKOS_LLM_BASE_URL | API endpoint | - |
| INKOS_LLM_API_KEY | API key | - |
| INKOS_LLM_MODEL | Model name | gpt-4o |
| INKOS_LLM_TEMPERATURE | Sampling temperature | 0.7 |
| INKOS_LLM_MAX_TOKENS | Max output tokens | 8192 |

## Project Structure

```
my-novel/
├── inkos.config.yaml     # Project configuration
├── story/
│   ├── state/            # 7 truth files (JSON)
│   │   ├── current_state.md
│   │   ├── particle_ledger.md
│   │   ├── pending_hooks.md
│   │   ├── chapter_summaries.md
│   │   ├── subplot_board.md
│   │   ├── emotional_arcs.md
│   │   └── character_matrix.md
│   ├── runtime/         # Runtime artifacts
│   ├── chapters/        # Generated chapters
│   └── memory.db        # SQLite memory database
└── drafts/              # Draft chapters
```

## CLI Reference

### Book Management
- `inkos init [name]` - Initialize project
- `inkos book create` - Create book
- `inkos book list` - List books
- `inkos book delete <id>` - Delete book

### Writing
- `inkos write next [id]` - Write next chapter
- `inkos write next [id] --count N` - Write N chapters
- `inkos write rewrite [id] N` - Rewrite chapter N
- `inkos draft [id]` - Write draft only

### Review
- `inkos review list [id]` - List drafts
- `inkos review approve-all [id]` - Approve all
- `inkos audit [id] [n]` - Audit chapter
- `inkos revise [id] [n]` - Revise chapter

### Export
- `inkos export [id]` - Export to TXT
- `inkos export [id] --format epub` - Export to EPUB

### Tools
- `inkos style analyze <file>` - Analyze style
- `inkos style import <file> [id]` - Import style
- `inkos detect [id] [n]` - AIGC detection
- `inkos agent <instruction>` - Natural language mode

## Troubleshooting

### Check Environment
```bash
inkos doctor
```

### View Logs
```bash
tail -f inkos.log
```

### Update InkOS
```bash
inkos update
```
