---
name: amazon-bestseller-scraper
description: Automatically scrape Amazon Bestseller rankings across product categories. Triggered when users request scraping Amazon bestseller lists, retrieving top-selling products, or analyzing Amazon rankings.
---

# Amazon Bestseller Scraper

Automatically scrape Amazon Best Seller ranking pages to extract product names, image links, and product page links.

## Supported Categories

| Category Keyword | Amazon URL |
|------------------|------------|
| Electronics | `/gp/bestsellers/electronics/` |
| Apparel | `/gp/bestsellers/apparel/` |
| Books | `/gp/bestsellers/books/` |
| Kitchen | `/gp/bestsellers/kitchen/` |
| Toys & Games | `/gp/bestsellers/toys-and-games/` |
| Sports & Outdoors | `/gp/bestsellers/sports/` |
| Beauty | `/gp/bestsellers/beauty/` |
| Baby Products | `/gp/bestsellers/baby-products/` |
| Automotive | `/gp/bestsellers/automotive/` |
| Home & Garden | `/gp/bestsellers/home-garden/` |

## Workflow

### 1. Receive Category Request

Receive the user-specified category (electronics, apparel, books, etc.) and convert it to the corresponding Amazon URL.

### 2. Scrape Best Seller Page

Use `extract_content_from_websites` tool to extract page content:

```json
{
  "url": "https://www.amazon.com/gp/bestsellers/{category-path}/",
  "prompt": "Extract all product information from this Amazon Best Seller page. For each product, provide: 1) Product name/title, 2) Product image URL, 3) Product detail page URL/link. Return as structured data."
}
```

### 3. Parse Product Information

Parse and structure the extracted content:

| Field | Description |
|-------|-------------|
| rank | Ranking (1-50) |
| name | Product name |
| image_url | Product image URL |
| product_url | Product detail page link |
| category | Product category |

### 4. Format Output

Supported output formats:
- **Markdown Table**: Ideal for direct reading
- **JSON Array**: Ideal for programmatic processing
- **CSV Format**: Ideal for data analysis

## Anti-Scraping Handling

| Strategy | Implementation |
|----------|----------------|
| Request Interval | 2-3 seconds between requests |
| Headers | Use common browser User-Agent |
| Failure Retry | Maximum 3 retries |
| Fallback URL | Multiple subcategories per category |

## Output Example

```markdown
## Amazon Electronics Bestseller

| Rank | Product Name | Image | Link |
|------|--------------|-------|------|
| 1 | Apple AirPods (2nd Gen) | ![img](url) | [View](url) |
| 2 | Sony WH-1000XM4 | ![img](url) | [View](url) |
```

## Notes

- Only scrape publicly available Best Seller ranking pages
- Respect Amazon robots.txt specifications
- Image URLs may contain Amazon domain; download backup if needed
- Recommend no more than 50 products per request
