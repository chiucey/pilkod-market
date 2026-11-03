# Competitor Search Strategy Reference

## Web Search Tool Usage

### batch_web_search Tool

Used for batch searching multiple keywords, returns search result lists.

**Parameters:**
```typescript
{
  queries: [
    { query: "search keyword", num_results: 10, data_range: "m" }
  ]
}
```

**data_range options:**
- `h` - Last 1 hour
- `d` - Last 1 day
- `m` - Last 1 month
- `y` - Last 1 year
- empty - Unlimited

### extract_content_from_websites Tool

Used for extracting structured content from web pages.

**Parameters:**
```typescript
{
  tasks: [
    { url: "webpage URL", prompt: "extraction description", task_name: "task name" }
  ],
  mode: "auto" | "curl_only" | "browser_only"
}
```

**Recommended: Use browser_only mode** - Good for dynamically loaded e-commerce pages

---

## Product Category Search Templates

### 1. Smartphones

**Search Queries:**
```
1. "flagship phone comparison 2024" - Find mainstream flagship models
2. "iPhone 15 Pro Tmall purchase" - Specific product purchase links
3. "Samsung S24 Ultra JD.com" - Competitor purchase channels
4. "high-end phone brand ranking" - Market positioning info
5. "Xiaomi 14 Pro review comparison" - Detailed specs comparison
```

**E-commerce Link Format:**
- Taobao: `https://s.taobao.com/search?q={product_name}`
- Tmall: `https://detail.tmall.com/item.htm?id={item_id}`
- JD: `https://search.jd.com/Search?keyword={product_name}`

**Data Source Websites:**
- smzdm.com (What to Buy)
- manmanbuy.com (Price Comparison)
- zol.com.cn (ZOL Tech)
- ithome.com (IT Home)

---

### 2. Bluetooth Headphones

**Search Queries:**
```
1. "noise canceling headphones comparison 2024" - Competitor positioning
2. "AirPods Pro 2 Tmall purchase link" - Apple products
3. "Sony WF-1000XM5 JD.com" - Sony competitors
4. "Huawei FreeBuds Pro 3 comparison" - Chinese flagship
5. "true wireless earbuds ranking" - Market ranking
```

---

### 3. Laptops

**Search Queries:**
```
1. "thin laptop recommendation 2024 comparison" - Find competitors
2. "MacBook Pro 14 Tmall" - Apple products
3. "ThinkPad X1 Carbon JD.com purchase" - Business laptops
4. "Huawei MateBook comparison" - Chinese brands
5. "gaming laptop value ranking" - Gaming market
```

---

### 4. Tablets

**Search Queries:**
```
1. "tablet recommendation 2024 comparison" - Find competitors
2. "iPad Pro Tmall purchase" - Apple products
3. "Huawei MatePad Pro comparison" - Chinese flagship
4. "Xiaomi Pad 6 Max" - Xiaomi products
5. "tablet value ranking" - Market analysis
```

---

### 5. Smartwatches

**Search Queries:**
```
1. "smartwatch recommendation 2024" - Find competitors
2. "Apple Watch Tmall purchase" - Apple products
3. "Huawei Watch GT4 JD.com" - Huawei products
4. "Samsung Watch comparison" - Samsung competitors
5. "sports watch value ranking" - Market analysis
```

---

### 6. Cameras/Mirrorless

**Search Queries:**
```
1. "mirrorless camera recommendation 2024" - Find competitors
2. "Sony A7M4 Tmall purchase" - Sony products
3. "Canon R6 JD.com" - Canon products
4. "Fujifilm camera comparison" - Fujifilm products
5. "full-frame mirrorless ranking" - Market analysis
```

---

### 7. Gaming Consoles

**Search Queries:**
```
1. "gaming console recommendation 2024" - Find competitors
2. "PS5 Tmall purchase" - PlayStation
3. "Xbox Series X JD.com" - Xbox
4. "Nintendo Switch OLED" - Nintendo
5. "gaming console comparison review" - Comprehensive comparison
```

---

### 8. Robot Vacuums

**Search Queries:**
```
1. "robot vacuum recommendation 2024" - Find competitors
2. "Ecovacs X2 Tmall purchase" - Ecovacs products
3. "Roborock G20 JD.com" - Roborock products
4. "Narwal robot comparison" - Narwal products
5. "robot vacuum value ranking" - Market analysis
```

---

### 9. Air Purifiers

**Search Queries:**
```
1. "air purifier recommendation 2024" - Find competitors
2. "Xiaomi air purifier Tmall" - Xiaomi products
3. "Dyson air purifier JD.com" - Dyson products
4. "Philips air purifier comparison" - Philips products
5. "air purifier ranking" - Market analysis
```

---

### 10. Projectors

**Search Queries:**
```
1. "projector recommendation 2024 home" - Find competitors
2. "Xgimi projector Tmall purchase" - Xgimi products
3. "Dangbei projector JD.com" - Dangbei products
4. "JMGO projector comparison" - JMGO products
5. "home projector value ranking" - Market analysis
```

---

## Competitor Info Extraction Template

### Required Fields

```json
{
  "name": "Product Name",
  "brand": "Brand",
  "price": "Price",
  "priceRange": "Price Range",
  "rating": 4.5,
  "reviews": "Review Count",
  "specs": {
    "processor": "Processor/Chip",
    "camera": "Camera (for camera products)",
    "battery": "Battery Life",
    "screen": "Screen Specs",
    "memory": "Memory/Storage"
  },
  "features": ["Feature 1", "Feature 2", "Feature 3"],
  "officialUrl": "Official Website URL",
  "taobaoUrl": "Taobao Link",
  "tmallUrl": "Tmall Link",
  "jdUrl": "JD Link",
  "source": "Data Source",
  "pros": ["Advantage 1", "Advantage 2", "Advantage 3"],
  "cons": ["Disadvantage 1", "Disadvantage 2"]
}
```

### Purchase Link Search Priority

1. **Official Flagship Store** - Most reliable
2. **Tmall Flagship** - Quality guaranteed
3. **JD.com Self-run** - Fast delivery
4. **Taobao High-Sales Stores** - May be cheaper
5. **Brand Official Website** - Most accurate info

---

## E-commerce Platform Search Tips

### Taobao Search

**Search URL Format:**
```
https://s.taobao.com/search?q={keyword}&sort={sort_method}
```

**Sort Methods:**
- `sale-desc` - Sales high to low
- `price-asc` - Price low to high
- `price-desc` - Price high to low
- `ratesum-desc` - Credit high to low

### Tmall Search

**Search URL Format:**
```
https://list.tmall.com/search_product.htm?q={keyword}
```

**Product Detail Page Format:**
```
https://detail.tmall.com/item.htm?id={item_id}
```

### JD.com Search

**Search URL Format:**
```
https://search.jd.com/Search?keyword={keyword}&enc=utf-8
```

**Product Detail Page Format:**
```
https://item.jd.com/{item_id}.html
```

---

## Data Validation Checklist

Before outputting competitor info, verify:

- [ ] Product name and brand are correct
- [ ] Price is current market price
- [ ] Purchase links are accessible
- [ ] Core specs are accurate
- [ ] Pros/cons analysis is objective
