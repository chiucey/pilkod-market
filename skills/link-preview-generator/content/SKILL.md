---
name: link-preview-generator
description: |
  Generate rich link previews and extract metadata from URLs. Use when users ask to:
  - "generate link preview", "create link card", "preview this URL"
  - "parse link metadata", "extract link info", "get URL details"
  - "analyze webpage", "fetch page info", "get website metadata"
  - "extract Open Graph", "get Twitter Card", "read meta tags"
  - "link analyzer", "URL inspector", "webpage summarizer"
  - "what's in this link", "show me link info", "parse this URL"
  - "extract webpage content", "get site description", "fetch article info"
  - "social share preview", "generate OG image", "check link metadata"
---

# Link Preview Generator

> Generate beautiful link previews and extract rich metadata from any URL.

## Overview

This skill transforms any URL into a beautiful, structured link preview card with complete metadata. Perfect for social sharing, content curation, link-in-bio tools, and any application needing rich URL previews.

## Quick Start

### Input a URL
```
"Generate a link preview for: https://github.com/openai"
```

### Output
```
┌─────────────────────────────────────────┐
│ [🖼️ Image Preview]                       │
├─────────────────────────────────────────┤
│ OpenAI · GitHub                          │
│ https://github.com/openai                │
│                                          │
│ OpenAI is an AI research and deployment  │
│ company. Our mission is to ensure that   │
│ artificial general intelligence...        │
│                                          │
│ Type: website | Lang: English            │
└─────────────────────────────────────────┘
```

## Core Features

### 1. Rich Metadata Extraction

| Category | Data Extracted |
|----------|---------------|
| **Basic Info** | Title, description, author, language |
| **Open Graph** | OG title, description, image, type, site_name |
| **Twitter Cards** | Card type, twitter:title, twitter:image |
| **Article Data** | Published time, modified time, section, tags |
| **URL Details** | Domain, path, parameters, security status |
| **Media** | Preview images, favicon, video thumbnails |

### 2. Preview Modes

| Mode | Use Case | Output |
|------|----------|--------|
| **Compact** | Quick link card | Title + 1-line description + thumbnail |
| **Standard** | Social sharing | Full preview with all metadata |
| **Detailed** | Data analysis | Complete JSON with all extracted data |

### 3. Smart Fallbacks

If certain metadata is missing, intelligent fallbacks are applied:

- Missing OG image → Use Twitter Card image
- Missing OG title → Use `<title>` tag
- Missing description → Try first paragraph of content
- No images → Use site favicon as placeholder

## Usage Examples

### Example 1: Article Preview

**Input:**
```
"Preview this article: https://techcrunch.com/2024/01/15/ai-breakthrough-2024"
```

**Output:**
```
┌─────────────────────────────────────────┐
│ [🖼️ AI Breakthrough 2024]               │
├─────────────────────────────────────────┤
│ AI Breakthrough 2024                    │
│ techcrunch.com                          │
│                                          │
│ Major advances in artificial general     │
│ intelligence announced today...           │
│                                          │
│ 📅 Jan 15, 2024 | 📝 by Sarah Chen       │
│ 🏷️ Technology, AI, Science              │
└─────────────────────────────────────────┘
```

### Example 2: Product Page

**Input:**
```
"Generate link card for: https://store.apple.com/macbook-pro"
```

**Output:**
```
┌─────────────────────────────────────────┐
│ [🖼️ MacBook Pro Product Image]           │
├─────────────────────────────────────────┤
│ MacBook Pro                              │
│ apple.com                                │
│                                          │
│ The most powerful MacBook Pro ever...    │
│                                          │
│ 💰 Starting at $1,999 | 📦 In Stock      │
└─────────────────────────────────────────┘
```

### Example 3: GitHub Repository

**Input:**
```
"Show me this GitHub repo preview: https://github.com/facebook/react"
```

**Output:**
```
┌─────────────────────────────────────────┐
│ [🖼️ React Repository Banner]             │
├─────────────────────────────────────────┤
│ facebook/react                           │
│ github.com                              │
│                                          │
│ The library for web and native user      │
│ interfaces...                            │
│                                          │
│ ⭐ 230k | 🍴 47k | 🐛 1.2k | 1.4k watching│
└─────────────────────────────────────────┘
```

### Example 4: Multi-URL Batch Processing

**Input:**
```
"Generate previews for these URLs:
1. https://news.ycombinator.com
2. https://reddit.com/r/programming
3. https://dev.to"
```

**Output:**
```
[1/3] Hacker News
┌─────────────────────────────────────────┐
│ [🖼️ Hacker News Logo]                    │
│ Hacker News                              │
│ news.ycombinator.com                     │
│                                          │
│ A social news website focusing on...     │
└─────────────────────────────────────────┘

[2/3] r/programming
┌─────────────────────────────────────────┐
│ [🖼️ Reddit Programming Banner]           │
│ r/programming                            │
│ reddit.com                               │
│                                          │
│ A subreddit for programming...           │
└─────────────────────────────────────────┘

[3/3] DEV Community
┌─────────────────────────────────────────┐
│ [🖼️ DEV Community Logo]                  │
│ DEV Community                           │
│ dev.to                                   │
│                                          │
│ A constructive and inclusive social...  │
└─────────────────────────────────────────┘
```

## Extraction Workflow

### Step 1: URL Validation

```javascript
// Validate URL format and protocol
validateURL(url) {
  // Check: http:// or https:// only
  // Check: valid domain format
  // Check: no malformed characters
}
```

### Step 2: Content Fetching

```javascript
// Use extract_content_from_websites tool
fetchPage(url) {
  // Fetch HTML content
  // Handle redirects
  // Respect robots.txt
}
```

### Step 3: Metadata Parsing

```javascript
// Parse in priority order
parseMetadata(html) {
  // 1. Open Graph tags (highest priority)
  // 2. Twitter Card tags
  // 3. Standard meta tags
  // 4. HTML semantic elements
  // 5. Content analysis (fallback)
}
```

### Step 4: Response Formatting

```javascript
// Generate preview in requested format
formatOutput(data, mode) {
  // Compact: quick card view
  // Standard: full preview
  // Detailed: complete JSON
}
```

## Output Formats

### Compact Preview (Default)

```
Title | Description (50 chars) | [Thumbnail]
```

### Standard Preview

```
Title
URL
Description (200 chars)
[Large Image]
Meta: Site Name | Type | Published Date
```

### Detailed JSON

```json
{
  "url": "https://example.com/article",
  "title": "Article Title",
  "description": "Article description...",
  "author": "Author Name",
  "published_time": "2024-01-15T10:00:00Z",
  "image": "https://example.com/og-image.jpg",
  "favicon": "https://example.com/favicon.ico",
  "site_name": "Example Site",
  "type": "article",
  "language": "en",
  "twitter_card": {
    "type": "summary_large_image",
    "title": "Twitter Title",
    "image": "https://example.com/twitter-image.jpg"
  }
}
```

## Error Handling

| Issue | Response |
|-------|----------|
| **Invalid URL** | "Please provide a valid HTTP/HTTPS URL" |
| **URL not found (404)** | "This page could not be found" |
| **Server error (5xx)** | "The website is temporarily unavailable" |
| **Timeout** | "Request timed out. Try again or use a shorter URL" |
| **No metadata** | "No preview available. Here's the raw URL info:" |
| **Blocked by site** | "This site doesn't allow preview generation" |

## Tips for Best Results

### ✅ Do This

- Use complete URLs with `https://`
- Try alternative URLs if one fails
- Check if the site allows crawling

### ❌ Avoid This

- URLs behind login/paywalls
- Very short URLs (they may redirect)
- URLs with excessive parameters

## Use Cases

| Industry | Application |
|----------|-------------|
| **Social Media** | Generate rich previews for shared links |
| **Messaging Apps** | Show link previews in chat |
| **Bookmarking** | Save and preview articles |
| **Content Curation** | Aggregate content from multiple sources |
| **Link-in-Bio** | Generate beautiful profile pages |
| **SEO Tools** | Analyze meta tag optimization |
| **Accessibility** | Provide text alternatives to visual content |

## Related Tools

| Tool | Purpose |
|------|---------|
| `extract_content_from_websites` | Fetch and parse webpage HTML |
| `batch_web_search` | Verify URL availability |
| `images_understand` | Analyze preview images |

## Limitations

- Cannot bypass paywalls or authentication
- Some sites block crawler access
- Dynamic content (JS-rendered) may have incomplete extraction
- Rate limits may apply for bulk requests

## FAQ

**Q: Why did my preview fail?**
A: Common reasons: site blocks crawlers, content requires login, URL redirects to dynamic content.

**Q: Can I preview private pages?**
A: No, this tool cannot access pages behind authentication.

**Q: How accurate is the metadata?**
A: For sites with proper Open Graph/Twitter Card markup, accuracy is ~95%. Fallbacks are used for sites with incomplete metadata.

**Q: What about image copyright?**
A: Extracted images are for preview purposes only. Respect the original site's image policies.

**Q: Can I process multiple URLs at once?**
A: Yes, batch processing is supported. Process up to 10 URLs in parallel.
