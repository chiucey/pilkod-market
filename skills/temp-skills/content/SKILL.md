---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502201d42939cd1480e42823eec9ed5fe719b60bb974c51073dc1f8a78dfef4506939022100da3e4bcf1f9334e69bfba99d221b3c9902fd830ce0b426bd3988d296d28130de
    ReservedCode2: 30460221008bed75d03977634c23600e4043a58ff2afae969bd761550af61c93f478637dc9022100c2e077acf6eb3aaf7571c4b9e0a48f2c3389c93de957219da71ed424cbbd01ec
---

# Knowledge Base Manager

## Responsibilities

As the manager of the knowledge base, automatically complete the following when collecting information:

### 1. Auto-Categorization and Storage

**Processing Flow:**
1. Identify the theme, type, and key content of information
2. Analyze the best-matching category (prioritize existing categories)
3. If existing categories don't fit, create custom categories
4. Extract keywords as tags
5. Record information source and timestamp
6. Add complete entry to knowledge base

**Category Decision Rules:**
| Information Type | Recommended Category |
|-----------------|---------------------|
| Market data, industry reports | market |
| Stock prices, analysis | stock |
| Flights, air tickets | flight |
| Hotels, accommodation | hotel |
| Current events, trending topics | news |
| Weather forecasts, meteorology | weather |
| Financial reports, indicators | finance |
| Other content | custom or new category |

### 2. Custom Category Naming

**Naming Principles:**
- Concise and clear, 2-4 characters optimal
- Reflect the core features of information
- Avoid duplication with existing categories
- Support dynamic creation of new categories

**Examples:**
- Collected "AI LLM latest progress" → Can create category "AI-Frontier"
- Collected "Competitive analysis report" → Can create category "Competitor-Dynamics"
- Collected "User feedback data" → Can create category "User-Insights"

### 3. Entry Structure

Each knowledge entry must include:
- **Title**: Concise summary of content
- **Content**: Complete information content
- **Category**: Best-matching category
- **Tags**: 3-5 keywords
- **Source**: Information source (e.g., scheduled task name)
- **Timestamp**: Auto-recorded creation time

## Execution Method

When user requests "Add XXX to knowledge base" or similar:

```
Analyze → Determine Category → Extract Tags → Build Entry → Confirm
```

**Response Format Example:**
```
Entry added: Title
- Category: market
- Tags: AI, tech, trends
- Source: Daily Tech Brief
- Time: 2024-05-11 23:45

Knowledge Base Stats:
- Total entries: 25
- Categories: 8
```

## API Interfaces

### Add Entry
```typescript
addEntry({
  title: string,
  content: string,
  categoryId: string,
  tags: string[],
  source?: string
})
```

### Add Category
```typescript
addCategory({
  name: string,
  color: string,
  icon: string,
  description: string
})
```

### Query Methods
```typescript
// Get entries by category
getEntriesByCategory(categoryId: string)

// Search entries
searchEntries(query: string)

// Get statistics
getStats()
```

## Default Categories

| ID | Name | Color | Description |
|----|------|-------|-------------|
| market | Market Trends | #3B82F6 | Market data and industry trends |
| stock | Stock Info | #10B981 | Stock quotes and analysis |
| flight | Flight Info | #8B5CF6 | Flight search and booking |
| hotel | Hotel Info | #F59E0B | Hotel recommendations and pricing |
| news | Hot News | #EF4444 | Current events and trending topics |
| weather | Weather Info | #06B6D4 | Weather forecasts and alerts |
| finance | Finance Data | #EC4899 | Financial reports and indicators |
| custom | Custom | #6B7280 | User-defined categories |

## Notes

1. **Auto-Recognition**: Prioritize content analysis before deciding categories, avoid blindly using "custom"
2. **Tag Extraction**: Extract keywords that best represent the topic from content
3. **Source Tracking**: Record information source for future verification
4. **Category Consolidation**: Avoid creating too many fragmented categories, merge same themes into one category