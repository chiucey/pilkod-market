---
name: scrapling-web-scraper
description: Adaptive Web Scraping framework for Python. Use when users ask to scrape websites, crawl pages, extract data from HTML, bypass anti-bot protection (Cloudflare), build web crawlers with pause/resume, perform stealthy HTTP requests, or need browser automation with Playwright. Triggers on keywords like "web scraping", "web crawl", "extract HTML data", "bypass Cloudflare", "Scrape websites", "automated web data extraction".
---

# Scrapling Web Scraper

Scrapling is an adaptive Web Scraping framework that handles everything from single requests to full-scale crawls.

## Quick Start

### Installation Check

Verify Scrapling is available:

```python
import scrapling
print(scrapling.__version__)
```

### Basic HTTP Request

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text').getall()
```

### Session-based Requests

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page = session.get('https://quotes.toscrape.com/')
    quotes = page.css('.quote .text::text').getall()
```

## Core Workflows

### 1. Simple Data Extraction

**Best for**: Single page, known structure

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://quotes.toscrape.com/')
data = []
for quote in page.css('.quote'):
    data.append({
        "text": quote.css('.text::text').get(),
        "author": quote.css('.author::text').get(),
    })
```

### 2. Bypass Anti-bot Protection

**Best for**: Cloudflare, stealth operations

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# One-off request
page = StealthyFetcher.fetch('https://example.com', headless=True)
data = page.css('#content a').getall()

# With session
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://example.com')
```

### 3. Browser Automation (Dynamic Content)

**Best for**: JavaScript-rendered pages, infinite scroll

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

# One-off
page = DynamicFetcher.fetch('https://example.com')
data = page.css('.item::text').getall()

# With session
with DynamicSession(headless=True, network_idle=True) as session:
    page = session.fetch('https://example.com')
```

### 4. Full Crawler with Spider

**Best for**: Multi-page crawling, pause/resume

```python
from scrapling.spiders import Spider, Request, Response

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        # Extract data
        for item in response.css('.item'):
            yield {
                "title": item.css('.title::text').get(),
                "link": item.css('a::attr(href)').get(),
            }
        # Follow pagination
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0].attrib['href'])

# Run spider
result = MySpider().start()
result.items.to_json("output.json")
```

### 5. Multi-Session Spider

**Best for**: Mix of fast and stealthy requests

```python
from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import FetcherSession, AsyncStealthySession

class MultiSessionSpider(Spider):
    name = "multi"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        for link in response.css('a::attr(href)').getall():
            if "protected" in link:
                yield Request(link, sid="stealth")
            else:
                yield Request(link, sid="fast", callback=self.parse)

result = MultiSessionSpider().start()
```

## Selection Methods

Scrapling supports multiple ways to find elements:

```python
# CSS selector
page.css('.quote .text::text')

# XPath
page.xpath('//div[@class="quote"]//span[@class="text"]/text()')

# BeautifulSoup-style
page.find_all('div', {'class': 'quote'})

# Text search
page.find_by_text('quote', tag='div')

# Regex
page.find_by_regex(r'\d+\s+\w+')
```

## Navigation API

```python
first_quote = page.css('.quote')[0]

# Navigate elements
parent = first_quote.parent
siblings = first_quote.next_sibling
children = first_quote.css('.tag')

# Find similar
similar = first_quote.find_similar()
```

## Proxy Rotation

```python
from scrapling.fetchers import FetcherSession
from scrapling.core.proxy import ProxyRotator

rotator = ProxyRotator(['http://proxy1:port', 'http://proxy2:port'])

with FetcherSession(proxy_rotator=rotator) as session:
    page = session.get('https://example.com')
```

## CLI Usage

```bash
# Interactive shell
scrapling shell

# Extract content
scrapling extract get 'https://example.com' content.md
scrapling extract fetch 'https://example.com' content.md --css-selector '#main'

# Stealthy fetch with Cloudflare bypass
scrapling extract stealthy-fetch 'https://example.com' result.html --solve-cloudflare
```

## Installation Reference

```bash
# Basic (parser only)
pip install scrapling

# With fetchers
pip install "scrapling[fetchers]"
scrapling install

# Full installation
pip install "scrapling[all]"
```

## Decision Guide

| Scenario | Recommended Approach |
|----------|---------------------|
| Simple static page | `Fetcher.get()` |
| Multiple requests | `FetcherSession` |
| Cloudflare protected | `StealthyFetcher` / `StealthySession` |
| JavaScript rendered | `DynamicFetcher` / `DynamicSession` |
| Multi-page crawl | `Spider` class |
| Complex anti-bot | `Spider` with multi-session |

## Error Handling

```python
from scrapling.fetchers import Fetcher
from scrapling.core.exceptions import ScraplingError

try:
    page = Fetcher.get('https://example.com', timeout=30)
except ScraplingError as e:
    print(f"Scraping error: {e}")
```
