# Scrapling Usage Examples

## Real-World Scraping Patterns

### E-commerce Product Scraper

```python
from scrapling.fetchers import FetcherSession
from scrapling.spiders import Spider, Request, Response

class ProductSpider(Spider):
    name = "products"
    start_urls = ["https://books.toscrape.com/"]
    concurrent_requests = 5

    async def parse(self, response: Response):
        # Extract product links
        products = response.css('.product_pod h3 a')
        for product in products:
            yield response.follow(product, callback=self.parse_product)

        # Pagination
        next_page = response.css('.next a')
        if next_page:
            yield response.follow(next_page[0])

    async def parse_product(self, response: Response):
        yield {
            "title": response.css('.product_main h1::text').get(),
            "price": response.css('.price_color::text').get(),
            "availability": response.css('.availability::text').get(),
            "category": response.css('.breadcrumb li:nth-child(3) a::text').get(),
            "url": response.url,
        }

result = ProductSpider().start()
result.items.to_json("products.json")
```

### News Aggregator with Cloudflare Bypass

```python
from scrapling.fetchers import StealthySession
from scrapling.spiders import Spider, Response

class NewsSpider(Spider):
    name = "news"
    start_urls = ["https://news.example.com/"]
    stealth = True

    async def parse(self, response: Response):
        for article in response.css('.article'):
            yield {
                "headline": article.css('h2::text').get(),
                "summary": article.css('.summary::text').get(),
                "published": article.css('.date::text').get(),
                "author": article.css('.author::text').get(),
            }

        next_page = response.css('.pagination .next a')
        if next_page:
            yield response.follow(next_page[0])

result = NewsSpider().start()
result.items.to_jsonl("news.jsonl")
```

### Multi-Session Crawler

```python
from scrapling.fetchers import FetcherSession, AsyncStealthySession
from scrapling.spiders import Spider, Request, Response

class HybridSpider(Spider):
    name = "hybrid"
    start_urls = ["https://example.com/"]

    def configure_sessions(self, manager):
        manager.add("fast", FetcherSession(impersonate="chrome"))
        manager.add("stealth", AsyncStealthySession(headless=True), lazy=True)

    async def parse(self, response: Response):
        public_links = response.css('a.public::attr(href)').getall()
        private_links = response.css('a.private::attr(href)').getall()

        for link in public_links:
            yield Request(link, sid="fast", callback=self.parse_public)

        for link in private_links:
            yield Request(link, sid="stealth", callback=self.parse_stealth)

    async def parse_public(self, response: Response):
        yield {"type": "public", "content": response.css('.content::text').get()}

    async def parse_stealth(self, response: Response):
        yield {"type": "private", "content": response.css('.content::text').get()}
```

### Adaptive Scraping for Changing Sites

```python
from scrapling.fetchers import StealthyFetcher

# Enable adaptive mode to handle website changes
StealthyFetcher.adaptive = True

# First scrape - elements are saved automatically
page = StealthyFetcher.fetch('https://example.com/products')
products = page.css('.product', auto_save=True)

# Later scrapes - elements are relocated even if selectors change
page = StealthyFetcher.fetch('https://example.com/products')
products = page.css('.product', adaptive=True)  # Smart relocation
```

### Streaming Large Crawls

```python
from scrapling.spiders import Spider, Response

class StreamSpider(Spider):
    name = "stream"
    start_urls = [f"https://example.com/page/{i}" for i in range(1, 101)]

    async def parse(self, response: Response):
        for item in response.css('.item'):
            yield {"data": item.css('::text').get()}

# Stream results in real-time
spider = StreamSpider()
async for item in spider.stream():
    print(item)
```

### Proxy Rotation Setup

```python
from scrapling.fetchers import FetcherSession
from scrapling.core.proxy import ProxyRotator

proxies = [
    "http://user1:pass1@proxy1.example.com:8080",
    "http://user2:pass2@proxy2.example.com:8080",
    "http://proxy3.example.com:8080",
]

rotator = ProxyRotator(proxies, strategy="random")  # or "cyclic"

with FetcherSession(proxy_rotator=rotator) as session:
    page = session.get('https://example.com')
```

### Async Parallel Requests

```python
import asyncio
from scrapling.fetchers import AsyncStealthySession

async def scrape_all(urls):
    async with AsyncStealthySession(max_pages=10) as session:
        tasks = [session.fetch(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [r.css('.data::text').getall() for r in results]

urls = [f"https://example.com/item/{i}" for i in range(50)]
data = asyncio.run(scrape_all(urls))
```
