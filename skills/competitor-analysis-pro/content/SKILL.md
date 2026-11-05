---
name: competitor-analysis-pro
description: A competitor analysis tool with web search. Use when users want to analyze competitors, find similar products from different brands, search competitor information, conduct market research, or compare products. Supports real competitor search, shopping links from Taobao/Tmall/JD, and SWOT/4P analysis reports.
---

# Competitor Analysis Pro Skill

## Core Capabilities

1. **Web Search for Real Competitors** - Use web search to find real brands and models of similar products
2. **Get Purchase Links** - Search for real purchase links on Taobao, Tmall, JD.com and other platforms
3. **Competitor Comparison** - Detailed specs, price, and feature comparison
4. **SWOT/4P Analysis** - Generate strategic analysis reports

## Workflow

### Step 1: Understand User Requirements

1. Identify the product type the user input
2. Determine if it's a generic category (e.g., "smartphone") or a specific product (e.g., "iPhone 15 Pro")
3. Clarify the analysis purpose (market research, competitor comparison, pricing strategy, etc.)

### Step 2: Web Search for Competitors

Use `batch_web_search` tool for multi-dimensional search:

```typescript
// Search strategy
const searchQueries = [
  `{Product Name} competitor comparison`,
  `{Product Name} {Brand1} {Brand2} {Brand3}`,
  `{Product Name} Tmall purchase link`,
  `{Product Name} JD.com purchase`,
  `{Product Type} ranking 2024`
];
```

### Step 3: Extract Competitor Details

Use `extract_content_from_websites` tool to extract info from:

1. **Brand Official Websites** - Get official specs and pricing
2. **E-commerce Platforms** - Get real-time prices, sales volume, reviews
3. **Review Websites** - Get professional comparison data

### Step 4: Organize Competitor Data

For each competitor, collect:
- Product name and brand
- Price range
- Core specs (processor/chip, memory, storage, screen, battery, etc.)
- Main selling points/features
- Purchase links (Taobao/Tmall/JD/official website)
- Pros and cons analysis

### Step 5: Generate Analysis Report

#### 5.1 Competitor Comparison Table
Show core specs comparison of all competitors

#### 5.2 SWOT Analysis
- **S (Strengths)** - Internal advantages
- **W (Weaknesses)** - Internal disadvantages
- **O (Opportunities)** - External opportunities
- **T (Threats)** - External threats

#### 5.3 4P Marketing Analysis
- **Product** - Product strategy
- **Price** - Pricing strategy
- **Place** - Distribution strategy
- **Promotion** - Promotion strategy

#### 5.4 Purchase Links Summary
Organize all competitor purchase channel links

## Common Product Category Search Templates

### Smartphones
```
Search: "flagship phone comparison", "iPhone Samsung Huawei Xiaomi OPPO", "high-end phone purchase link"
```

### Bluetooth Headphones
```
Search: "noise canceling headphones comparison", "AirPods Sony Bose Huawei", "wireless earbuds Tmall purchase"
```

### Laptops
```
Search: "thin laptop comparison 2024", "MacBook ThinkPad Huawei Xiaomi", "laptop purchase link"
```

### Tablets
```
Search: "tablet comparison iPad Huawei Xiaomi", "tablet purchase Tmall"
```

### Smartwatches
```
Search: "smartwatch comparison Apple Watch Huawei Samsung", "watch purchase link"
```

### Cameras/Mirrorless
```
Search: "mirrorless camera comparison Sony Canon Fujifilm", "camera purchase Tmall JD"
```

### Gaming Consoles
```
Search: "gaming console comparison PS5 Xbox Switch", "gaming console purchase link"
```

### Robot Vacuums
```
Search: "robot vacuum comparison Ecovacs Roborock Narwal", "robot vacuum purchase link"
```

## Output Format

### Competitor Info Card
```
┌─────────────────────────────┐
│ [Brand] Product Name        │
│ ¥Price | ⭐Rating | Sales  │
├─────────────────────────────┤
│ Processor: xxx              │
│ Memory/Storage: xxx         │
│ Screen: xxx                 │
│ Battery: xxx                │
├─────────────────────────────┤
│ Features: [Tag1] [Tag2]   │
├─────────────────────────────┤
│ ✅ Pros: xxx               │
│ ❌ Cons: xxx               │
├─────────────────────────────┤
│ 🛒 Purchase:               │
│ [Taobao] [Tmall] [JD] [Official] │
└─────────────────────────────┘
```

### SWOT Analysis Matrix
```
┌─────────────┬─────────────┐
│ Strengths S │ Weaknesses W│
├─────────────┼─────────────┤
│Opportunities│   Threats T │
└─────────────┴─────────────┘
```

## Purchase Link Format

Provide purchase links for each competitor:

```json
{
  "taobaoUrl": "https://s.taobao.com/search?q={product_name}",
  "tmallUrl": "https://list.tmall.com/search_product.htm?q={product_name}",
  "jdUrl": "https://search.jd.com/Search?keyword={product_name}",
  "officialUrl": "{brand_official_website}"
}
```

Prioritize **specific product detail page links** over search page links.

## Quality Standards

1. **Authenticity** - All competitors must be real existing products
2. **Completeness** - Each competitor must include complete price, specs, purchase links
3. **Timeliness** - Prices and links must be currently accessible
4. **Actionability** - Purchase links must be directly accessible

## Notes

1. If user inputs a specific product, search for similar competitors (same type, different brands/models)
2. If user inputs a product category, search for mainstream flagship products in that category
3. Prioritize official flagship stores or high-sales stores for purchase links
4. Analysis reports should combine specific product features, avoid generic statements

## Tools Reference

See `references/search_strategy.md` for detailed search templates and e-commerce platform link formats.
