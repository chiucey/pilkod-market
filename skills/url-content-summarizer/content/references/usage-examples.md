# Usage Examples Reference

## Web Page Summarization

### Basic URL Summary
```
User: summarize https://github.com/steipete/summarize
Tool: extract_content_from_websites
Prompt: Extract the main content, key features, and purpose of this repository
Output: Generate structured summary
```

### Quick Overview (tl;dr)
```
User: tl;dr https://news-site.com/article
Tool: extract_content_from_websites
Prompt: Give me a 2-sentence summary of this article
Output: Brief summary
```

### Multi-Page Article Extraction
```
User: summarize this article with all sections
Tool: extract_content_from_websites
Prompt: Extract full article content including all sections, headings, and key points
Output: Complete structured summary
```

## PDF Summarization

### Research Paper Summary
```
User: summarize this paper /path/to/paper.pdf
Tool: extract_pdfs_key_info
Prompt: Extract main findings, methodology, conclusions, and key takeaways
Output: Academic summary format
```

### Full PDF Extraction
```
User: read and summarize this document
Tool: extract_pdfs_full_content
Prompt: Comprehensive extraction for detailed analysis
Output: Full content with summary
```

## Video Content Summary

### YouTube Video
```
User: summarize this video https://youtube.com/watch?v=xxx
Tool: videos_understand
Prompt: Extract the main topics discussed, key insights, and important timestamps
Output: Video summary with time markers
```

### Local Video File
```
User: what is this video about /path/to/video.mp4
Tool: videos_understand
Prompt: Describe the main content, topics, and key moments
Output: Video description and summary
```

## Audio Content Summary

### Podcast Episode
```
User: summarize this podcast episode
Tool: audios_understand
Prompt: Transcribe and summarize the main topics and key points discussed
Output: Podcast summary with chapters/topics
```

### Interview or Lecture
```
User: extract key points from this audio
Tool: audios_understand
Prompt: Identify main themes, key quotes, and important conclusions
Output: Structured key points
```

## Document Types Reference

| Document Type | Best Tool | Best Practice |
|---------------|-----------|---------------|
| News Article | extract_content_from_websites | 1-2 paragraph summary |
| Technical Doc | extract_content_from_websites | Detailed with code examples |
| Research Paper | extract_pdfs_key_info | Structured academic format |
| Blog Post | extract_content_from_websites | Brief overview |
| Product Page | extract_content_from_websites | Feature-focused summary |
| GitHub README | extract_content_from_websites | Project overview format |
