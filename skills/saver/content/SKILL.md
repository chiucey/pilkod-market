---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: faf8513095e8fe5b3953ef3c0fb10a64
    PropagateID: faf8513095e8fe5b3953ef3c0fb10a64
    ReservedCode1: 30460221009c7736932aa6b52607825ee300fc7ef2ad0a758bd90e514fc7c00fbf74ee87c9022100c027817a73e63d3da92177378bb1214ff38e412ee13d4628539a64127ba776f5
    ReservedCode2: 3046022100ff8e11ec1eee3ea053ae0b379b5d67a4d6096c510501c65fd1415d1c934f9c3c022100a64693769766a6e2c290243e0e1c72c82953fff88b9bcbab36e269a79e37a5e0
description: Smart shopping assistant for product search and price comparison. Use when users ask to search products, compare prices, find JD.com/Taobao deals, or get shopping recommendations. Supports requirement analysis, smart sorting, and affiliate link conversion.
name: saver
---

# Saver Skill

Smart shopping assistant - Connects to Saver MCP Server for product search and price comparison services.

**Note: Currently serving users in Mainland China only. More countries and regions coming soon.**

## Features

- 🎯 Requirement analysis (auto-determine if confirmation is needed)
- 🔍 Product search (JD.com / Taobao)
- 📊 Smart sorting (sales / price / rating)
- 🔗 Auto link conversion (generate affiliate links)
- 💰 Price calculation (coupon price + government subsidies)
- 🌊 **SSE Streaming** - Real-time progress updates

---

## ⚠️ Recommended Workflow (Important)

**AI Agent should call tools in the following order:**

```
┌─────────────────────────────────────────────────────────┐
│  User request: "Help me buy a phone"                    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Step 1: Call analyze_shopping_need                     │
│  Analyze requirements, determine if confirmation needed │
└─────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
    needConfirm=false            needConfirm=true
            │                           │
            │                           ▼
            │                 ┌─────────────────────┐
            │                 │ Communicate with    │
            │                 │ user to confirm     │
            │                 │ (price, brand, etc) │
            │                 └─────────────────────┘
            │                           │
            └─────────────┬─────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: Call unified_search                            │
│  Search → Sort → Link conversion (all in one call)      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: Return results to user                         │
│  Product names are hyperlinks, click to buy             │
└─────────────────────────────────────────────────────────┘
```

**Key Points**:
- ✅ Must call `analyze_shopping_need` first
- ✅ If requirements are unclear, communicate with user to confirm
- ✅ After requirements are clear, call `unified_search`

---

## Tools

| Tool | Description | When to use |
|-----|------|---------|
| `unified_search` | Search + Sort + Link conversion (all in one) | **After requirements are clear** |
| `analyze_shopping_need` | Analyze user requirements | **Must call first** |
| `complete_shopping` | Complete flow (auto analyze + search) | Alternative to above two |
| `search_products` | Search only (no link conversion) | Not recommended |

---

## unified_search Parameters

| Parameter | Type | Required | Description |
|-----|------|-----|------|
| keyword | string | ✅ | Search keyword |
| minPrice | number | ❌ | Minimum price |
| maxPrice | number | ❌ | Maximum price |
| pageSize | number | ❌ | Results per platform (default: 10) |
| sortBy | string | ❌ | Sort method (default: sales) |

**Sort Options**:
- `sales` - Sort by sales (default)
- `price_asc` - Sort by price ascending
- `price_desc` - Sort by price descending
- `rating` - Sort by rating

---

## Technical Details

- **MCP Server**: `http://81.70.235.20:3001/mcp`
- **Protocol**: MCP 2024-11-05 (Streamable HTTP + SSE)
- **Supported Platforms**: JD.com (self-operated only), Taobao (Tmall only)
- **No Authentication Required**: Public service, direct access
- **Capabilities**: streaming, sse

---

## Notes

- ⚠️ **Commission info is NOT exposed to users**
- ⚠️ Product names contain affiliate links, users can click to buy
- ⚠️ Only searches JD self-operated and Tmall products (quality first)

---

*Version: 1.2.0*