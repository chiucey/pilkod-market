---
name: agent-browser
description: High-performance Rust-based headless browser automation CLI with Node.js fallback. Use when user requests browser automation tasks such as navigation, clicking, typing, screenshots, or content extraction. Triggers: browser automation, headless browser, webpage automation, browser control, take screenshot, click element, navigate to, type input, browser CLI, playwright alternative, puppeteer alternative, Rust browser.
---

# Agent Browser - High-Performance Browser Automation CLI

## Overview

Agent Browser is a Rust-based high-performance headless browser automation tool with Node.js WASM fallback, supporting AI agents to execute browser operations via structured commands.

**Core Features:**
- Rust core engine for maximum performance
- Node.js WASM fallback for cross-platform compatibility
- Structured command interface for AI Agent integration
- CDP (Chrome DevTools Protocol) support
- Lightweight binary with fast startup

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent Layer                       │
│            (Structured JSON Commands)                    │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   Command Parser                        │
│              (Unified Command Interface)                │
└─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│   Rust Core Engine      │   │   Node.js WASM Fallback │
│   (Native Performance)  │   │   (Cross-Platform)      │
└─────────────────────────┘   └─────────────────────────┘
              │                           │
              └─────────────┬─────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Browser Engine (CDP)                       │
│         Chrome/Chromium Headless Instance               │
└─────────────────────────────────────────────────────────┘
```

## Command Structure

All commands use JSON format via stdin/stdout:

### Basic Commands

#### 1. Navigate Command

```json
{
  "command": "navigate",
  "params": {
    "url": "https://example.com",
    "timeout": 30000,
    "wait_until": "networkidle"
  }
}
```

**Parameters:**
- `url` (required): Target URL
- `timeout` (optional): Timeout in ms, default 30000
- `wait_until` (optional): Wait condition
  - `load`: Wait for load event
  - `domcontentloaded`: Wait for DOMContentLoaded
  - `networkidle`: Wait for network idle
  - `networkidle2`: Wait for 2s no network activity

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example Domain",
    "status": 200
  }
}
```

#### 2. Click Command

```json
{
  "command": "click",
  "params": {
    "selector": "#submit-button",
    "timeout": 10000
  }
}
```

**Parameters:**
- `selector` (required): CSS selector or XPath
- `timeout` (optional): Timeout in ms, default 10000
- `button` (optional): Mouse button (`left`, `right`, `middle`), default `left`
- `click_count` (optional): Number of clicks, default 1

#### 3. Type Command

```json
{
  "command": "type",
  "params": {
    "selector": "input[name='email']",
    "text": "user@example.com",
    "delay": 100,
    "clear": true
  }
}
```

**Parameters:**
- `selector` (required): Target input selector
- `text` (required): Text to type
- `delay` (optional): Delay between chars in ms, default 0
- `clear` (optional): Clear before typing, default true
- `press_enter` (optional): Press Enter after typing, default false

#### 4. Screenshot Command

```json
{
  "command": "screenshot",
  "params": {
    "path": "./screenshots/page.png",
    "full_page": false,
    "selector": null,
    "format": "png",
    "quality": 90
  }
}
```

**Parameters:**
- `path` (required): Save path
- `full_page` (optional): Capture full page, default false
- `selector` (optional): Capture specific element only
- `format` (optional): Format (`png`, `jpeg`, `webp`), default `png`
- `quality` (optional): Image quality (1-100), default 90

#### 5. Extract Command

```json
{
  "command": "extract",
  "params": {
    "selector": "article.post",
    "fields": {
      "title": "h2.title",
      "link": "a.read-more@href",
      "date": ".date::text"
    },
    "as": "json"
  }
}
```

**Parameters:**
- `selector` (required): Parent element selector
- `fields` (required): Field mapping to extract
- `as` (optional): Output format (`json`, `csv`, `text`)

**Special Selector Syntax:**
- `element@attr`: Get attribute value
- `element::text`: Get text content
- `element::html`: Get HTML content

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "title": "Article Title 1",
      "link": "/articles/1",
      "date": "2024-01-15"
    }
  ]
}
```

#### 6. Wait Command

```json
{
  "command": "wait",
  "params": {
    "for": "selector",
    "value": ".loading-spinner",
    "state": "hidden",
    "timeout": 15000
  }
}
```

**Wait Conditions:**
- `selector`: Wait for element to appear/disappear
- `timeout`: Wait for specified duration
- `function`: Wait for JS function to return true
- `navigation`: Wait for navigation to complete

**States:**
- `attached`: Element exists in DOM
- `visible`: Element is visible
- `hidden`: Element is hidden
- `enabled`: Element is enabled
- `disabled`: Element is disabled

#### 7. Evaluate Command

```json
{
  "command": "evaluate",
  "params": {
    "script": "() => document.title",
    "args": []
  }
}
```

Execute arbitrary JavaScript and return result.

#### 8. Scroll Command

```json
{
  "command": "scroll",
  "params": {
    "selector": ".infinite-scroll",
    "direction": "down",
    "amount": 500,
    "times": 3
  }
}
```

#### 9. Upload Command

```json
{
  "command": "upload",
  "params": {
    "selector": "input[type='file']",
    "files": ["./uploads/document.pdf"]
  }
}
```

#### 10. Close Command

```json
{
  "command": "close",
  "params": {}
}
```

Close current browser instance.

### Batch Commands

Execute multiple commands for efficiency:

```json
{
  "commands": [
    {"command": "navigate", "params": {"url": "https://example.com"}},
    {"command": "wait", "params": {"for": "selector", "value": "#content"}},
    {"command": "click", "params": {"selector": "#login-btn"}},
    {"command": "type", "params": {"selector": "#username", "text": "admin"}},
    {"command": "type", "params": {"selector": "#password", "text": "secret", "press_enter": true}},
    {"command": "screenshot", "params": {"path": "./screenshots/dashboard.png"}}
  ]
}
```

**Batch Response:**
```json
{
  "success": true,
  "results": [
    {"index": 0, "success": true, "data": {...}},
    {"index": 1, "success": true, "data": {...}},
    {"index": 2, "success": false, "error": "Element not found"}
  ]
}
```

## Usage

### CLI Interactive Mode

```bash
# Start interactive mode
agent-browser --interactive

# Single command mode
echo '{"command": "navigate", "params": {"url": "https://example.com"}}' | agent-browser

# Read from file
agent-browser < commands.json

# Save output to file
agent-browser --output results.json < commands.json
```

### Programming Interface

#### Node.js SDK

```javascript
const { AgentBrowser } = require('agent-browser-sdk');

const browser = new AgentBrowser();

await browser.connect();
await browser.navigate('https://example.com');
await browser.click('#submit-btn');
const screenshot = await browser.screenshot({ path: './output.png' });
const data = await browser.extract('article', {
  title: 'h2::text',
  link: 'a@href'
});
await browser.close();
```

#### Python SDK

```python
from agent_browser import AgentBrowser

browser = AgentBrowser()
browser.connect()
browser.navigate('https://example.com')
browser.click('#submit-btn')
browser.screenshot(path='./output.png')
data = browser.extract('article', {'title': 'h2::text', 'link': 'a@href'})
browser.close()
```

### AI Agent Integration

```json
// AI Agent Request Format
{
  "action": "browser_automation",
  "tasks": [
    {"cmd": "navigate", "target": "https://github.com/login"},
    {"cmd": "wait", "target": "#username_field"},
    {"cmd": "type", "target": "#username_field", "value": "myuser"},
    {"cmd": "type", "target": "#password_field", "value": "mypass", "submit": true},
    {"cmd": "wait", "target": ".dashboard", "state": "visible"},
    {"cmd": "screenshot", "path": "github_dashboard.png"}
  ]
}
```

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "ELEMENT_NOT_FOUND",
    "message": "Selector '#submit-btn' not found within 10000ms",
    "details": {
      "selector": "#submit-btn",
      "timeout": 10000,
      "page_url": "https://example.com"
    }
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `ELEMENT_NOT_FOUND` | Element not found |
| `NAVIGATION_TIMEOUT` | Navigation timeout |
| `INVALID_SELECTOR` | Invalid selector |
| `JAVASCRIPT_ERROR` | JavaScript execution error |
| `NETWORK_ERROR` | Network request failed |
| `BROWSER_CRASHED` | Browser crashed |
| `PERMISSION_DENIED` | Permission denied |
| `TIMEOUT` | Operation timeout |

## Performance Optimization

### Connection Reuse

```bash
# Start persistent instance
agent-browser --daemon

# Connect to existing instance
agent-browser --connect localhost:9222
```

### Batch Operation Optimization

```json
{
  "command": "batch",
  "params": {
    "commands": [...],
    "parallel": false,
    "continue_on_error": true
  }
}
```

### Resource Management

```bash
# Limit memory usage
agent-browser --max-memory 512MB

# No-sandbox mode (faster)
agent-browser --no-sandbox

# GPU acceleration
agent-browser --enable-gpu
```

## Configuration Options

### Config File (~/.agent-browser/config.toml)

```toml
[defaults]
timeout = 30000
headless = true
user_agent = "AgentBrowser/1.0"

[performance]
max_concurrent = 5
connection_pool_size = 10
cache_enabled = true

[browser]
executable_path = null  # Auto-detect
args = ["--no-sandbox", "--disable-dev-shm-usage"]
viewport_width = 1920
viewport_height = 1080

[storage]
screenshot_dir = "./screenshots"
download_dir = "./downloads"
```

## Installation

### Quick Install

```bash
# macOS
brew install agent-browser

# Linux
curl -fsSL https://get.agent-browser.dev | sh

# Windows
winget install AgentBrowser

# npm
npm install -g agent-browser-cli
```

### Docker Deployment

```dockerfile
FROM agentbrowser/runtime:latest

COPY ./commands.json /app/commands.json
RUN agent-browser < /app/commands.json
```

## Troubleshooting

### Common Issues

1. **Startup failed: Chrome not found**
   ```bash
   agent-browser --install-chrome
   ```

2. **Element click not working**
   ```bash
   # Use JavaScript click
   agent-browser --eval "document.querySelector('#btn').click()"
   ```

3. **Page load timeout**
   ```bash
   # Increase timeout
   agent-browser --timeout 60000
   ```

4. **Blank screenshot**
   ```bash
   # Ensure page fully loaded
   agent-browser --wait-until networkidle
   ```

### Debug Mode

```bash
# Enable debug logging
agent-browser --debug

# Show CDP traffic
agent-browser --debug --verbose

# Record session
agent-browser --record session.json
```

## References

- [CDP Protocol Documentation](./references/cdp-protocol.md)
- [Selector Syntax Reference](./references/selectors.md)
- [SDK Examples](./references/sdk-examples/)
- [Configuration Reference](./references/config-reference.md)
