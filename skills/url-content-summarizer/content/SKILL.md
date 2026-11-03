---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8f913f69f0c090aa18dde298e32b8c69
    PropagateID: 8f913f69f0c090aa18dde298e32b8c69
    ReservedCode1: 30450220258971f38e4ba50a86e052920b4dd3a2a83c425c219895cdaec57104ac5b5716022100dd05fe9a9fe409595852c84dcb091560e70ab6f2d5823236a82351c3c94106bd
    ReservedCode2: 304502204ce5c477a65b7f7591f759758a6995fef78ea22cc5d2b9d7ac9a37536e13b301022100d85b41b2c5018ab5d47604b8bcb90c1b8382c087e1fdc39c5944d78af7499fb1
---

# URL Content Summarizer

Quickly extract and summarize content from various sources including web pages, documents, and media.

## Supported Content Types

| Type | Description | Examples |
|------|-------------|----------|
| Web Pages | URLs and articles | News sites, blogs, documentation |
| PDFs | Document files | Research papers, reports |
| Video | YouTube, local videos | Tutorials, presentations |
| Audio | Podcasts, music | NPR podcasts, interviews |
| Text | Plain text input | Paste content directly |

## Workflow

### Step 1: Identify Content Source

Determine the content type:
- **URL**: Web page or media link (YouTube, podcast)
- **File**: Local PDF, video, or audio file
- **Text**: Direct paste content

### Step 2: Extract Content

Use appropriate extraction method:

**For URLs:**
```
Use extract_content_from_websites tool with prompt to extract main content
```

**For PDFs:**
```
Use extract_pdfs_key_info or extract_pdfs_full_content tool
```

**For Media (YouTube, videos):**
```
Use videos_understand tool with summary prompt
```

**For Audio:**
```
Use audios_understand tool with transcription/summary request
```

### Step 3: Generate Summary

Create a concise summary following these rules:

1. **Length**: Match user's implied needs (brief overview vs detailed summary)
2. **Format**: Use markdown with clear structure
3. **Key Points**: Lead with the most important takeaways
4. **Tone**: Professional, informative, objective

### Summary Structure

```markdown
## Summary

[2-3 sentence overview of the main topic]

## Key Points

- [Point 1]
- [Point 2]
- [Point 3]

## Details

[Additional relevant information if needed]
```

## Length Options

| Option | Use Case |
|--------|----------|
| `short` | Quick overview (2-3 sentences) |
| `medium` | Standard summary (1 paragraph + 3-5 points) |
| `long` | Detailed summary with full context |

## Examples

**Example 1: Web Page Summary**
```
User: summarize https://example.com/article
Tool: extract_content_from_websites
Output: Generate 1-2 paragraph summary with key points
```

**Example 2: Video Summary**
```
User: 总结这个视频 https://youtube.com/watch?v=xxx
Tool: videos_understand with summary prompt
Output: Extract main topics and key timestamps
```

**Example 3: Quick Summary**
```
User: tl;dr https://news-site.com/article
Tool: extract_content_from_websites
Output: Very brief 1-2 sentence summary
```

## Quality Checklist

- [ ] Identified correct content type
- [ ] Used appropriate extraction tool
- [ ] Summary is accurate to source material
- [ ] Key points are included
- [ ] Length appropriate for request
- [ ] Markdown formatting applied

## Fallback Handling

If primary extraction fails:
1. Try alternative tool (e.g., if extract_content fails, try batch_web_search)
2. Search for cached/mirrored content
3. Inform user if content is inaccessible
