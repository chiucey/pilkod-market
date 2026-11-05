# Scrapling API Reference

## Core Modules

### scrapling.fetchers

#### Fetcher
Static methods for one-off HTTP requests.

```python
from scrapling.fetchers import Fetcher

# Basic GET
page = Fetcher.get(url)

# With options
page = Fetcher.get(url, impersonate='chrome', timeout=30)
```

#### FetcherSession
Context manager for session-based requests with cookie persistence.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(impersonate='chrome') as session:
    page1 = session.get(url1)
    page2 = session.get(url2)
```

#### StealthyFetcher / StealthySession
Bypasses anti-bot protection including Cloudflare Turnstile.

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# One-off
page = StealthyFetcher.fetch(url, headless=True, solve_cloudflare=True)

# Session
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch(url)
```

#### DynamicFetcher / DynamicSession
Full browser automation using Playwright.

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

# One-off
page = DynamicFetcher.fetch(url, headless=True, network_idle=True)

# Session
with DynamicSession(headless=True) as session:
    page = session.fetch(url)
```

### scrapling.spiders

#### Spider
Base class for building crawlers.

```python
from scrapling.spiders import Spider, Request, Response

class MySpider(Spider):
    name = "my_spider"
    start_urls = ["https://example.com/"]
    concurrent_requests = 10

    async def parse(self, response: Response):
        # Return items or Requests
        yield {"data": "value"}
        yield response.follow(next_url)
```

#### Request
Request object for following links.

```python
from scrapling.spiders import Request

yield Request(url, callback=self.parse_detail)
yield Request(url, sid="stealth")  # Use specific session
```

#### Response
Response object with selection methods.

```python
response.css(selector)
response.xpath(xpath)
response.follow(link_element)
```

### scrapling.parser

#### Selector
Parse HTML without fetching.

```python
from scrapling.parser import Selector

page = Selector(html_string)
data = page.css('.item::text').getall()
```

### scrapling.core.proxy

#### ProxyRotator
Cyclic proxy rotation.

```python
from scrapling.core.proxy import ProxyRotator

rotator = ProxyRotator(['http://proxy1:port', 'http://proxy2:port'])
```

## Selection Methods

| Method | Description |
|--------|-------------|
| `css(selector)` | CSS selector with pseudo-elements |
| `xpath(xpath)` | XPath expression |
| `find_all(tag, attrs)` | BeautifulSoup-style search |
| `find_by_text(text, tag)` | Find by text content |
| `find_by_regex(pattern)` | Regex search |
| `find_similar()` | Find structurally similar elements |

## Response Methods

| Method | Description |
|--------|-------------|
| `get()` | Get first match or None |
| `getall()` | Get all matches |
| `attrib` | Element attributes |
| `text` | Element text content |
| `follow(element)` | Create Request from element |

## Spider Configuration

| Attribute | Default | Description |
|-----------|---------|-------------|
| `name` | required | Spider identifier |
| `start_urls` | [] | Initial URLs |
| `concurrent_requests` | 1 | Max concurrent requests |
| `download_delay` | 0 | Delay between requests |
| `crawldir` | None | Checkpoint directory for pause/resume |
