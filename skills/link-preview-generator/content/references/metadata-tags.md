# URL Metadata Tags Reference

## Open Graph Protocol Tags

Open Graph protocol enables any web page to become a rich object in a social graph.

### Required Tags

| Property | Description |
|----------|-------------|
| `og:title` | The title of your object as it should appear within the graph |
| `og:type` | The type of your object (website, article, video, etc.) |
| `og:image` | An image URL which should represent your object within the graph |
| `og:url` | The canonical URL of your object that will be used as its permanent ID |

### Optional Tags

| Property | Description |
|----------|-------------|
| `og:description` | One to two sentences describing your object |
| `og:site_name` | A human-readable name for your site |
| `og:locale` | The locale of the resource (e.g., en_US) |
| `og:locale:alternate` | Other locales this page is available in |

### Article Object Tags

For `og:type = "article"`:

| Property | Description |
|----------|-------------|
| `article:published_time` | When the article was first published |
| `article:modified_time` | When the article was last modified |
| `article:author` | The author of the article |
| `article:section` | A high-level section name |
| `article:tag` | Tag words associated with this article |

### Image Object Tags

For `og:image`:

| Property | Description |
|----------|-------------|
| `og:image:url` | Identical to og:image |
| `og:image:secure_url` | An alternate url to use if the webpage requires HTTPS |
| `og:image:type` | MIME type of the image |
| `og:image:width` | Width of the image in pixels |
| `og:image:height` | Height of the image in pixels |

## Twitter Card Tags

### Card Types

| Value | Description |
|-------|-------------|
| `summary` | Default card |
| `summary_large_image` | Image card with large preview |
| `app` | App install card |
| `player` | Video/audio player card |

### Tags

| Property | Description |
|----------|-------------|
| `twitter:card` | Card type |
| `twitter:site` | @username of website |
| `twitter:title` | Title of the content |
| `twitter:description` | Description of the content |
| `twitter:image` | URL of image to use |
| `twitter:image:alt` | Alt text for the image |
| `twitter:player` | URL of player iframe |
| `twitter:player:width` | Width of player iframe |
| `twitter:player:height` | Height of player iframe |
| `twitter:player:stream` | URL to raw stream |

## Standard Meta Tags

### Basic Tags

| Name | Description |
|------|-------------|
| `description` | Brief description of the page |
| `keywords` | Comma-separated list of keywords |
| `author` | Author of the page |
| `robots` | Robots directive (index, follow, etc.) |
| `viewport` | Viewport settings for mobile |
| `generator` | Software used to create the page |

### Link Tags

| Name | Description |
|------|-------------|
| `canonical` | Preferred URL for the page |
| `shortlink` | Short URL to the page |
| `icon` | URL to favicon |
| `apple-touch-icon` | Icon for iOS bookmark |

### HTML Elements

| Element | Description |
|---------|-------------|
| `<title>` | Page title (most important) |
| `<link rel="canonical">` | Canonical URL |
| `<link rel="icon">` | Favicon |
| `<link rel="alternate">` | Alternative versions (RSS, mobile) |

## Example HTML Head Section

```html
<head>
  <!-- Basic -->
  <title>Article Title - Site Name</title>
  <meta name="description" content="Brief description of the article content...">
  <meta name="keywords" content="keyword1, keyword2, keyword3">
  <meta name="author" content="Author Name">
  <meta name="robots" content="index, follow">

  <!-- Open Graph -->
  <meta property="og:title" content="Article Title">
  <meta property="og:description" content="Brief description for social sharing...">
  <meta property="og:image" content="https://example.com/image.jpg">
  <meta property="og:url" content="https://example.com/article">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Site Name">
  <meta property="og:locale" content="en_US">

  <!-- Article-specific OG -->
  <meta property="article:published_time" content="2024-01-15T10:00:00Z">
  <meta property="article:author" content="Author Name">
  <meta property="article:section" content="Technology">
  <meta property="article:tag" content="AI">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@siteaccount">
  <meta name="twitter:title" content="Article Title">
  <meta name="twitter:description" content="Brief description...">
  <meta name="twitter:image" content="https://example.com/twitter-image.jpg">
  <meta name="twitter:image:alt" content="Image description">

  <!-- Links -->
  <link rel="canonical" href="https://example.com/article">
  <link rel="icon" href="https://example.com/favicon.ico">
  <link rel="apple-touch-icon" href="https://example.com/apple-touch-icon.png">
</head>
```

## JSON-LD Structured Data

### Article Schema

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "description": "Article description",
  "image": "https://example.com/image.jpg",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Site Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "datePublished": "2024-01-15T10:00:00Z",
  "dateModified": "2024-01-15T12:00:00Z"
}
```

### WebSite Schema

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Site Name",
  "url": "https://example.com",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://example.com/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

## Common Issues

1. **Missing og:image**: Falls back to Twitter card image or no image
2. **Wrong image size**: Twitter requires minimum 144x144px, Facebook prefers 1200x630px
3. **Title too long**: Truncate at 60-70 characters for display
4. **Description too long**: Truncate at 155-200 characters
5. **Inconsistent titles**: Ensure og:title matches <title> when possible
6. **HTTPS vs HTTP**: Use HTTPS for all URLs to avoid mixed content warnings
