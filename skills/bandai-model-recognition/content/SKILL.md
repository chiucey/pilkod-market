---
name: bandai-model-recognition
description: Bandai model image recognition and identification skill. Use when users upload Bandai model images and require identification, product search, pricing and specifications lookup. Triggers include "identify this Gundam", "what model is this", "search Bandai products", "RG vs MG difference", "what does HG mean", etc.
---

# Bandai Model Image Recognition and Identification

## Skill Overview

This skill is designed for recognizing and analyzing Bandai products, supporting multiple series including Gundam models, figures, and Saint Seiya Myth Cloth product search and information lookup.

## Core Capabilities

### 1. Image Recognition
Receive user-uploaded model images and analyze visual features:
- Model series (HG/MG/RG/PG/MEGA SIZE)
- Specific mobile suit model (e.g., RX-78-2, MS-06S)
- Production batch and year
- Scale and difficulty level

### 2. Image-Text Search
Multiple search methods supported:
- Text description search (e.g., "red Zaku", "fleet escort ship")
- Specification search (e.g., "1/144 scale", "fully articulated")
- Series-specific search (e.g., "RG series only")

### 3. Product Information Lookup
Detailed product information provided:
- Product number and series name
- Scale and dimensions
- Part count
- Release date and price range
- Special features and accessories

## Recognition Process

```
1. Receive Image → 2. Feature Extraction → 3. Series Classification → 4. MS Matching → 5. Output
```

### Step 1: Image Reception
Accept PNG/JPG/WEBP format images, max 10MB

### Step 2: Feature Extraction
Analyze key visual features:
- Head design (antenna, V-shape, etc.)
- Color scheme (Federation/Zeon/Other)
- Proportions and build
- Special equipment and weapons

### Step 3: Series Classification
Determine series based on features:
| Feature | HG | MG | RG | PG |
|---------|-----|-----|-----|-----|
| Scale | 1/144 | 1/100 | 1/144 | 1/60 |
| Detail | Basic | Medium | Fine | Ultra-fine |
| Frame | None | Partial | Full | Complete |

### Step 4: Mobile Suit Matching
Match with knowledge base combining visual features

### Step 5: Information Output
Provide complete product info and recommendations

## Output Format

### Recognition Result
```json
{
  "matched": true,
  "product": {
    "series": "RG",
    "name": "RX-78-2 Gundam",
    "number": "RG-01",
    "scale": "1/144",
    "grade": "Real Grade",
    "year": "2010",
    "specs": {
      "height": "12.5cm",
      "parts": 230,
      "price_range": "¥2,000-3,000"
    },
    "features": ["inner frame", "fully articulated", "rich stickers"]
  },
  "confidence": 0.95,
  "alternatives": [...]
}
```

## Knowledge Base

### Gundam Model Grade Guide

| Grade | Japanese | Scale | Difficulty | Features |
|-------|----------|-------|------------|----------|
| HG | High Grade | 1/144 | Entry | Easy assembly, affordable |
| MG | Master Grade | 1/100 | Intermediate | Partial inner frame, rich details |
| RG | Real Grade | 1/144 | Advanced | Full inner frame, high detail at small scale |
| PG | Perfect Grade | 1/60 | Master | Complete inner frame, motorized functions |
| MEGA | Mega Size | 1/48 | Intermediate | Large scale display type |

### Common Series Abbreviations
- **PB**: Premium Bandai (Limited)
- **PGB**: Perfect Grade Build Burning
- **HCM**: High Complete Model
- **MGS**: Metal Build Series

## Search Examples

### Example 1: Image Recognition
```
User: [Upload RX-78-2 image]
Skill: Recognition Result:
       Mobile Suit: RX-78-2 Gundam
       Series: RG 01
       Scale: 1/144
       Features: First Real Grade, exquisite inner frame
       Suitable for: Intermediate to advanced builders
```

### Example 2: Text Search
```
User: "Find a red MS-06 Zaku"
Skill: Search Results:
       1. RG MS-06S Char's Zaku (red)
       2. MG MS-06S Zeon Commander's Custom
       3. HGUC MS-06R-1 High Mobility Type Zaku
```

### Example 3: Series Comparison
```
User: "Which is better for beginners, RG or MG?"
Skill: Comparison Analysis:
       - HG → Recommended first choice for beginners
       - RG → Detail-oriented progression
       - MG → Best value for money
```

## Limitations and Notes

1. **Image Quality**: Blurry or poorly angled images may affect recognition accuracy
2. **Limited Edition**: Some limited editions may not be recognized
3. **New Product Delay**: Latest releases may not yet have data
4. **Custom Paint**: Extensively modified kits may not match accurately

## Related Skill Calls

For enhanced web search capabilities, combine with:
- `web-search` - Search latest product information
- `image-understanding` - Deep image analysis
