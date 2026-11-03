---
name: movie-downloader
description: 查找并下载想看的影视资源。当用户要求搜索电影、电视剧、动漫等视频资源，查找下载链接，或需要获取影视资源时使用。支持关键词搜索、资源筛选、下载功能。
---

# Movie Downloader Skill

## Core Capabilities

1. **Smart Search** - Search for resources based on movie/TV show name
2. **Resource Filtering** - Filter high-quality, ad-free, magnet links
3. **Local Download** - Download resources to specified directory

## Workflow

### Step 1: Understand User Requirements

Collect the following information:
- **Movie Name**: The movie/TV show/anime name
- **Preferred Format**: HD/Full HD/Blu-ray etc.
- **Download Location**: Where to save (default `/workspace/downloads`)

### Step 2: Search Movie Resources

Use `batch_web_search` with these keyword combinations:
- Movie name + "download"
- Movie name + "magnet"
- Movie name + "torrent"

### Step 3: Filter Quality Resources

Prioritize:
- Magnet links
- Direct download links (over cloud storage)
- HD/Blu-ray versions

Exclude:
- Resources requiring registration/login
- Invalid/expired links
- Cloud storage shares (non-priority)

### Step 4: Download Resources

For magnet links:
1. Use `batch_web_search` to find magnet parsing sites
2. Convert magnet link to direct download link
3. Use `download_file` to download to local

For direct download links:
1. Use `download_file` tool to download to specified directory

### Step 5: Confirm Download Result

Check if download succeeded, return:
- File save path
- File size
- Download status

## Output Format

Display to user:
```
Download complete!

**{Movie Name}**
- Format: {MP4/MKV etc.}
- Resolution: {720P/1080P/4K}
- Size: {file size}
- Save Location: {file path}

Notes:
- Magnet links require download tool to open
- Some resources may need subtitle files
```

## Error Handling

| Situation | Solution |
|-----------|----------|
| No resources found | Expand search keywords, try different platforms |
| Download failed | Provide alternative download links |
| File too large | Remind user to check disk space |

## Usage Example

**User Input**:
> Download "The Wandering Earth 2"

**Execution Flow**:
1. Search "The Wandering Earth 2 movie download"
2. Filter magnet/direct download links
3. Download to `/workspace/downloads/`
4. Return download result

## Notes

- Only provide public accessible resource search and download services
- No support for private resources requiring login authentication
- Comply with copyright laws, for learning and exchange purposes only
