---
name: image-host-uploader
description: Image hosting upload skill. Used when users want to upload images to freeimage.host, share image links, get direct image links, or need to upload local/web images to an image hosting service.
---

# Image Host Uploader Skill

## Overview

This skill uploads images to the freeimage.host image hosting service and returns direct links and share links.

## API Configuration

**Request Method**: GET

**API Endpoint**: `http://freeimage.host/api/1/upload/`

**Required Parameters**:
| Parameter | Description | Source |
|-----------|-------------|--------|
| `key` | API Key | User provided: `6d207e02198a847aa98d0a2a901485a5` |
| `source` | Image URL (must be URL encoded) | User provided or system generated |
| `format` | Response format | Fixed value: `json` |

**Full Request Example**:
```
http://freeimage.host/api/1/upload/?key=6d207e02198a847aa98d0a2a901485a5&source=https://example.com/image.jpg&format=json
```

## Execution Flow

1. **Receive Image Source**
   - Prefer using user-provided image URL
   - If user uploads a local file, first upload to temp storage to get URL

2. **Build Request**
   - URL encode the image URL
   - Construct the complete API request URL

3. **Call API**
   - Use GET method to request freeimage.host API

4. **Parse Response**
   - Check if `status_code` is 200
   - Extract key fields from response:
     - `image.url` - Original image direct link
     - `image.display_url` - Medium size link
     - `image.thumb.url` - Thumbnail link
     - `image.url_viewer` - Online preview link

5. **Return Results**
   - Return formatted image link information
   - Include ready-to-use Markdown image syntax

## Response Field Reference

| Field | Description |
|-------|-------------|
| `image.url` | Original image direct link |
| `image.width` / `image.height` | Image dimensions |
| `image.size_formatted` | File size |
| `image.thumb.url` | Thumbnail link (160px) |
| `image.medium.url` | Medium size link (500px) |
| `image.display_url` | Display link |
| `image.url_viewer` | Online view page |

## Success Response Example

```json
{
  "status_code": 200,
  "success": {
    "message": "image uploaded",
    "code": 200
  },
  "image": {
    "url": "http://freeimage.host/images/2024/01/15/example.png",
    "display_url": "http://freeimage.host/images/2024/01/15/example.md.png",
    "thumb": {
      "url": "http://freeimage.host/images/2024/01/15/example.th.png"
    },
    "medium": {
      "url": "http://freeimage.host/images/2024/01/15/example.md.png"
    },
    "url_viewer": "http://freeimage.host/image/L"
  },
  "status_txt": "OK"
}
```

## Usage Example

**User Input**: "Upload this image: https://example.com/photo.jpg"

**Execution**:
```
GET http://freeimage.host/api/1/upload/?key=6d207e02198a847aa98d0a2a901485a5&source=https%3A%2F%2Fexample.com%2Fphoto.jpg&format=json
```

**Return Result**:
```
Upload successful!

**Direct Link**: http://freeimage.host/images/2024/01/15/example.png

**Markdown Reference**:
![image](http://freeimage.host/images/2024/01/15/example.png)

**Online Preview**: http://freeimage.host/image/L
```

## Error Handling

| Error Type | Handling |
|------------|----------|
| API returns non-200 status code | Return error message, prompt user to check image URL |
| Network request failed | Retry once, report error if still failing |
| Invalid image URL | Prompt user to provide a valid image address |
