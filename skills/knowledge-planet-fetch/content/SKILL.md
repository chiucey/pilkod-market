---
name: knowledge-planet-fetch
description: >
  Fetch Knowledge Planet content via OpenClaw/MaxClaw browser or MiniMax Agent web tools.
  Use when: User sends a Knowledge Planet link or requests to fetch planet content.
  Supports login state detection, shows QR code for scanning when not logged in.
  Automatically detects runtime environment and selects appropriate browser/web tools.
---

# Knowledge Planet Fetch

Fetch posts, comments, images, and other content from Knowledge Planet (zsxq.com) via OpenClaw/MaxClaw built-in browser or MiniMax Agent web tools.

## When to Use

- User sends a Knowledge Planet link (wx.zsxq.com or xingqiu.xiaomi.com)
- User requests to fetch content from a specific planet
- User requests to view a specific post in a planet

## Prerequisites

### OpenClaw / MaxClaw
1. Chrome installed (Chrome/Chromium-based browser supported)
2. `openclaw browser start` or `maxclaw browser start` available (browser plugin loaded)
3. Knowledge Planet account logged in (scan once, valid until Chrome closes)

### MiniMax Agent
1. Network connection available
2. Use `extract_content_from_websites` tool for content extraction
3. Use `interact_with_website` tool for login interaction (if needed)

## Platform Detection and Command Selection

### Platform Detection Logic
```
IF "openclaw" command exists in environment:
    Use OpenClaw Browser tools
ELIF "maxclaw" command exists in environment:
    Use MaxClaw Browser tools
ELSE:
    Use MiniMax Agent web tools (extract_content_from_websites / interact_with_website)
```

## Usage

### OpenClaw / MaxClaw

#### fetch (Fetch single post or planet list)

```bash
openclaw browser start
# or
maxclaw browser start

openclaw browser navigate <url>
# or
maxclaw browser navigate <url>

openclaw browser snapshot
# or
maxclaw browser snapshot
# → Parse snapshot output, extract text, images, comments
```

#### Check Login State

```bash
openclaw browser cookies --domain zsxq.com
# or
maxclaw browser cookies --domain zsxq.com
# → If zsxq-related session/token cookies exist, user is logged in
```

#### Not Logged In: Show QR Code

```bash
openclaw browser open https://wx.zsxq.com/
# or
maxclaw browser open https://wx.zsxq.com/

openclaw browser wait --text "登录"
# or
maxclaw browser wait --text "登录"

openclaw browser screenshot
# or
maxclaw browser screenshot
# → Send screenshot to user → User scans with WeChat → Continue
```

### MiniMax Agent

#### fetch (Fetch single post or planet content)

Use `extract_content_from_websites` to extract page content:

```json
{
  "tasks": [{
    "url": "https://wx.zsxq.com/dmp/xxxxx",
    "prompt": "Extract post title, author, main content, all image URLs, comment list with timestamps"
  }]
}
```

#### Check Login State

Use `interact_with_website` to check login status:

```json
{
  "url": "https://wx.zsxq.com/",
  "action": "check_login"
}
```

#### Not Logged In: Interactive Login

```json
{
  "url": "https://wx.zsxq.com/",
  "action": "interact",
  "description": "Wait for user to scan QR code for login"
}
```

Get QR code screenshot:

```json
{
  "url": "https://wx.zsxq.com/login",
  "action": "screenshot"
}
```

## Fetch Result Structure

```json
{
  "ok": true,
  "content": {
    "type": "post" | "topic" | "album",
    "title": "...",
    "author": "...",
    "text": "...",
    "images": ["url1", "url2"],
    "comments": [
      { "author": "...", "text": "...", "time": "..." }
    ],
    "time": "..."
  }
}
```

## Key Implementation Details

### OpenClaw / MaxClaw Browser CLI
- `openclaw` / `maxclaw` installed in PATH, call directly without `cd`
- Both tools have compatible command formats; documentation uses OpenClaw as example, replace prefix for MaxClaw

### MiniMax Agent Tool Usage
- **Content Extraction**: Prefer `extract_content_from_websites`, supports batch processing multiple URLs
- **Interactive Operations**: Use `interact_with_website` for clicking, scrolling, login, etc.
- **Screenshots**: `interact_with_website` supports screenshot operations, returns image URLs

### Screenshot Saving
- OpenClaw/MaxClaw: `screenshot` output format is `MEDIA:<path>`
- MiniMax Agent: Screenshots returned via `interact_with_website`, provide accessible URLs

### Wait Strategy
- `wait --text "登录"` detects not logged in prompt (Chinese UI text from Knowledge Planet)
- `wait --text "查看详情"` waits for content to load (Chinese UI text from Knowledge Planet)
- `wait --time 3000` fallback wait
- MiniMax Agent: Use `interact_with_website` wait parameters or polling

> **Note**: The Chinese text in `wait --text` commands represents actual UI text displayed on the Knowledge Planet website. Do not translate these as they must match the website's actual interface.

### Login State Persistence
- Chrome close invalidates login state; rescan required each session (Knowledge Planet limitation)
- MiniMax Agent: Session-level login state; pay attention to reuse

## Platform Comparison Quick Reference

| Feature | OpenClaw | MaxClaw | MiniMax Agent |
|---------|----------|---------|---------------|
| Command Prefix | `openclaw browser` | `maxclaw browser` | `extract_content_from_websites` |
| Browser Launch | `browser start` | `browser start` | N/A (direct extraction) |
| Navigation | `browser navigate <url>` | `browser navigate <url>` | `interact_with_website` |
| Content Extraction | `browser snapshot` | `browser snapshot` | `extract_content_from_websites` |
| Screenshot | `browser screenshot` | `browser screenshot` | `interact_with_website` |
| Cookie Check | `browser cookies` | `browser cookies` | Application logic required |
| Login State | Temporary (invalidates on close) | Temporary (invalidates on close) | Session-level |
