---
name: openclaw-memory-skill
description: Configure and manage long-term memory for OpenClaw using Alibaba Cloud Model Studio API. When users ask to set up OpenClaw memory, configure memory plugin, manage agent memory, search memory database, store memories, or implement cross-session context awareness.
---

# OpenClaw Long-Term Memory Skill

This skill enables long-term memory capabilities for OpenClaw agents through Alibaba Cloud Model Studio (百炼) API, providing cross-session context awareness and automatic memory capture and recall.

## Overview

The Model Studio Memory plugin runs within OpenClaw Gateway, interacting with Alibaba Cloud Bailian Long-Term Memory API through two lifecycle hooks: `before_agent_start` and `agent_end`. All read and write operations are sent via HTTPS requests to Alibaba Cloud Bailian server, which handles memory refinement, vectorization, and semantic retrieval.

## Features

- **Auto-Capture (autoCapture)**: Automatically extracts and stores key information after conversations
- **Auto-Recall (autoRecall)**: Automatically retrieves relevant memories before conversations
- **Semantic Search**: Natural language query support for memory retrieval
- **Memory Management**: Store, list, search, and delete memories via tools or CLI

## Installation

### Step 1: Verify OpenClaw Status

```bash
openclaw gateway status
```

Output should contain `Gateway: bind=loopback` and port information.

### Step 2: Obtain DashScope API Key

Get the API Key from the Alibaba Cloud Bailian (百炼) key management page.

### Step 3: Install Plugin

```bash
openclaw plugins install @modelstudio/modelstudio-memory-for-openclaw
```

### Step 4: Configure Plugin

Open `~/.openclaw/openclaw.json` and add configuration in the `plugins` section:

```json
{
  "plugins": {
    "slots": {
      "memory": "modelstudio-memory-for-openclaw"
    },
    "entries": {
      "modelstudio-memory-for-openclaw": {
        "enabled": true,
        "config": {
          "apiKey": "sk-xxx",
          "userId": "user_001"
        }
      }
    }
  }
}
```

**Configuration Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `apiKey` (required) | string | - | DashScope API Key (starts with sk-xxx) |
| `userId` (required) | string | - | User identifier for memory space isolation |
| `autoCapture` | boolean | `true` | Auto-extract and store memories after conversation |
| `autoRecall` | boolean | `true` | Auto-retrieve and inject memories before conversation |
| `topK` | number | `5` | Number of memories returned per recall |
| `minScore` | number | `0` | Minimum similarity threshold (0–100) |

### Step 5: Verify Installation

```bash
# View plugin information
openclaw plugins info modelstudio-memory-for-openclaw

# View memory status
openclaw modelstudio-memory stats

# Restart Gateway
openclaw gateway restart
```

## Memory Tools

The plugin registers four tools for the Agent:

### memory_search

Semantic search in memory database. Accepts natural language queries and returns the most similar memory entries.

### memory_store

Directly write to memory. Stores specified content directly to the memory database without conversation refinement.

### memory_list

Paginated listing of memories. Lists all memory entries for the current userId with pagination support.

### memory_forget

Delete specified memories by memory ID.

## CLI Commands

```bash
# Semantic search memories
openclaw modelstudio-memory search "user preference"

# Paginated list all memories
openclaw modelstudio-memory list --page 1 --size 10

# View memory statistics
openclaw modelstudio-memory stats
```

## Usage Examples

### Example: Without Memory Plugin

**First Conversation**:
- User: I'm working on a Python project using FastAPI framework
- Agent: Good, FastAPI is a high-performance web framework. How can I help?

**Second Conversation (New Session)**:
- User: Help me write an API endpoint
- Agent: What language and interface type are you using?
- Agent cannot remember the previous conversation context.

### Example: With Memory Plugin Enabled

**First Conversation**:
- User: I'm working on a Python project using FastAPI framework
- Agent: Good, FastAPI is a high-performance web framework. How can I help?

**Second Conversation (New Session)**:
- User: Help me write an API endpoint
- Agent retrieves relevant memory: "User is working on a FastAPI framework Python project"
- Agent starts helping write the endpoint immediately.

## Rate Limits and Performance

### API Rate Limits

| API Operation | Rate Limit |
|---------------|------------|
| AddMemory (write) | 120 requests/minute |
| SearchMemory (query) | 300 requests/minute |
| All operations combined | 3000 requests/minute |

### Performance Metrics

| Operation | Latency |
|-----------|---------|
| SearchMemory end-to-end | 200–500ms |
| AddMemory | 500–1000ms |
| Auto-capture | Asynchronous, no impact on response speed |

## Troubleshooting

### Gateway restart shows plugin as "not loaded"

Check if `plugins.entries.modelstudio-memory-for-openclaw.enabled` is set to `true` in openclaw.json, and verify `plugins.slots.memory` points to the correct plugin.

### InvalidApiKey error in logs

The DashScope API Key is invalid or expired. Log in to Alibaba Cloud Bailian console to verify API Key status.

### View plugin logs

**Linux/macOS**:
```bash
tail -f /tmp/openclaw/openclaw-$(date +%F).log | grep modelstudio-memory
```

**Windows PowerShell**:
```powershell
Get-Content "$env:TEMP\openclaw\openclaw-$(Get-Date -Format 'yyyy-MM-dd').log" -Wait | Select-String "modelstudio-memory"
```

## Expected Output

Plugin loaded successfully:
```
Memory (Bailian)
id: modelstudio-memory-for-openclaw
status: loaded
Tools: memory_search, memory_store, memory_list, memory_forget
CLI commands: modelstudio-memory
```

Status verification:
```
User: user_001
Total memories: 0
Auto-capture: true
Auto-recall: true
Top-K: 5
```

## Related Documentation

| Document | Description |
|----------|-------------|
| OpenClaw (Clawdbot/Moltbot) | Alibaba Cloud official OpenClaw integration guide |
| API Key Management | Alibaba Cloud Bailian API Key creation and management |
| Long-Term Memory API | Complete parameter descriptions and code examples for AddMemory, SearchMemory |
| Memory Database | Create and manage memory databases in console |
