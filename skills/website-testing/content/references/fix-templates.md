# Fix Templates Reference

Ready-to-use code snippets for the most common audit findings.

---

## Security Headers (Cloudflare)

Add via: Cloudflare Dashboard → Rules → Transform Rules → Modify Response Headers → Add

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https://fonts.gstatic.com
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

> **Note**: The CSP above is permissive to avoid breaking WordPress plugins. Tighten after testing.

---

## WordPress Performance (wp-config.php)

```php
// Enable object caching
define('WP_CACHE', true);

// Disable unnecessary features
define('CONCATENATE_SCRIPTS', false);
define('COMPRESS_SCRIPTS', true);
define('COMPRESS_CSS', true);
```

WP Rocket recommended settings:
- Cache → Enable caching for mobile devices ✅
- File Optimization → Minify CSS/JS ✅
- File Optimization → Combine CSS/JS ✅ (test carefully)
- Media → Lazy load images ✅
- Preload → Preload cache ✅

---

## Schema.org JSON-LD (Article / Book)

For knowledge/content sites like Art of War:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Book",
  "name": "The Art of War",
  "author": {
    "@type": "Person",
    "name": "Sun Tzu"
  },
  "description": "Ancient Chinese military treatise attributed to Sun Tzu",
  "inLanguage": ["en", "zh"],
  "url": "https://sun-tzu.ai/the-art-of-war/"
}
</script>
```

---

## Meta Tags Template (WordPress — add to header.php or via Yoast SEO)

```html
<!-- Primary Meta Tags -->
<meta name="title" content="[Page Title] | Sun-Tzu.AI">
<meta name="description" content="[120-160 character description with primary keyword]">

<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="[canonical URL]">
<meta property="og:title" content="[Page Title]">
<meta property="og:description" content="[Description]">
<meta property="og:image" content="[1200x630 image URL]">

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="[canonical URL]">
<meta property="twitter:title" content="[Page Title]">
<meta property="twitter:description" content="[Description]">
<meta property="twitter:image" content="[Image URL]">
```

---

## Bulk Alt Attribute Fix (WordPress SQL — use carefully)

```sql
-- Find images without alt text in post content
SELECT ID, post_title, post_content
FROM wp_posts
WHERE post_status = 'publish'
  AND post_content LIKE '%<img%'
  AND post_content NOT LIKE '%alt="%'
LIMIT 50;
```

Use the WordPress Media Library bulk editor or a plugin like "Bulk Auto-Generate Alt Text" for safer fixes.

---

## robots.txt Template

```
User-agent: *
Allow: /

# Block admin and sensitive paths
Disallow: /wp-admin/
Disallow: /wp-login.php
Disallow: /wp-includes/
Disallow: /?s=

# Sitemap
Sitemap: https://yourdomain.com/sitemap.xml
```
