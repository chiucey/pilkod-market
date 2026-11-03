# GitHub URL Patterns Reference

## Common GitHub URL Formats

### Repository URLs
```
https://github.com/{owner}/{repo}
https://github.com/{owner}/{repo}/
github.com/{owner}/{repo}
{owner}/{repo}
```

### Sub-pages
```
https://github.com/{owner}/{repo}/issues
https://github.com/{owner}/{repo}/pulls
https://github.com/{owner}/{repo}/releases
https://github.com/{owner}/{repo}/actions
https://github.com/{owner}/{repo}/insights
https://github.com/{owner}/{repo}/tree/{branch}/{path}
https://github.com/{owner}/{repo}/blob/{branch}/{path}
https://github.com/{owner}/{repo}/raw/{branch}/{path}
```

### Search URLs
```
https://github.com/search?q={query}
https://github.com/search?q=language:{language}
https://github.com/search?q=user:{username}
```

## URL Parsing Patterns

### JavaScript
```javascript
function parseGitHubUrl(input) {
  const patterns = [
    /^https?:\/\/github\.com\/([^\/]+)\/([^\/\s]+)\/?$/,
    /^github\.com\/([^\/]+)\/([^\/\s]+)\/?$/,
    /^([^\/]+)\/([^\/\s]+)$/
  ];

  for (const pattern of patterns) {
    const match = input.match(pattern);
    if (match) {
      return { owner: match[1], repo: match[2].replace(/\/$/, '') };
    }
  }
  return null;
}
```

### Python
```python
import re

def parse_github_url(input_str):
    patterns = [
        r'https?://github\.com/([^/]+)/([^/\s]+)/?',
        r'github\.com/([^/]+)/([^/\s]+)/?',
        r'([^/]+)/([^/\s]+)'
    ]
    for pattern in patterns:
        match = re.match(pattern, input_str)
        if match:
            return {'owner': match.group(1), 'repo': match.group(2).rstrip('/')}
    return None
```

## Raw Content Access

### Direct File Access
```
https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
```

### Directory Listing
```
https://github.com/{owner}/{repo}/tree/{branch}/{path}
```

## API Endpoints (for advanced usage)

```
https://api.github.com/repos/{owner}/{repo}
https://api.github.com/repos/{owner}/{repo}/contents/{path}
https://api.github.com/repos/{owner}/{repo}/git/trees/{sha}
```

Note: API has rate limits (60 requests/hour for unauthenticated)
