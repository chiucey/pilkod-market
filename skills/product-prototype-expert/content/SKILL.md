---
name: product-prototype-expert
description: Product prototype expert, skilled in converting PRD documents into actionable wireframe frameworks for Figma/Axure. Use when users need product prototype frameworks, page layouts, function annotations, or user flow diagrams. Trigger words include: PRD to prototype, e-commerce prototype, product wireframe, page breakdown, function annotation.
---

# Product Prototype Expert

## Core Capabilities

Convert PRD documents into "ready-to-use wireframe frameworks" for Figma/Axure design.

## Key Features

- **Page Breakdown**: Split by functional modules
- **Function Annotation**: Core features for each page
- **Flow Mapping**: User operation flows
- **Tool Suggestions**: Figma (free collaboration) or Axure (professional)

## Workflow

### 1. Receive Requirements

**Required Information**:
- PRD Document: Text or file describing the product
- Key modules: What are the main pages/flows?

**Ask clarifying questions when needed**:
- "What's the target platform? (Mobile/Web/Desktop)"
- "Any specific design constraints?"
- "Is this for internal review or client presentation?"

### 2. Output Structure

```
# [Product Name] Prototype Framework

## Overview
- Product Type: E-commerce App / Social Media / SaaS
- Platform: iOS / Android / Web
- Total Pages: X pages

---

## Page 1: Login/Registration
### Core Functions
- Phone/Email login
- SMS verification code
- Social login (WeChat/Alipay)

### Wireframe Description
```
┌─────────────────────────┐
│         [LOGO]          │  <- 1/6 height
├─────────────────────────┤
│                         │
│   [Phone Input Field]   │  <- Input boxes
│                         │
│   [Password Field]      │
│                         │
│   [Login Button]        │  <- Primary CTA
│                         │
│   [Forgot Password?]    │  <- Secondary link
│                         │
│   ──── or ────          │  <- Divider
│                         │
│   [WeChat] [Alipay]     │  <- Social login
│                         │
└─────────────────────────┘
```

---

## Page 2: Home Page
### Core Functions
- Search bar
- Banner carousel
- Category navigation
- Product recommendations

### Wireframe Description
```
┌─────────────────────────┐
│  [Search Bar]    [Cart]│  <- Top bar (1/12)
├─────────────────────────┤
│                         │
│   [Banner Carousel]     │  <- 2/5 height
│                         │
├─────────────────────────┤
│ [Cat1][Cat2][Cat3][Cat4]│  <- Category row
├─────────────────────────┤
│  [Prod]    [Prod]       │
│  [Name]    [Name]       │  <- Product grid
│  [Price]   [Price]      │     (2 columns)
│  [Prod]    [Prod]       │
└─────────────────────────┘
```

---

## User Flow

### Main Flow: Purchase
```
Login → Home → Search → Product Detail → Cart → Checkout → Payment → Success
```

### Alternative Flows
- Home → Category → Product List → Product Detail → Cart
- Home → Banner → Product Detail → Cart
```

## Tool Recommendations

| Tool | Best For | Cost | Learning Curve |
|------|----------|------|----------------|
| Figma | Collaboration, free | Free | Medium |
| Axure | Complex interactions | $29+/mo | High |
| Sketch | Mac only | $99 | Medium |
| Adobe XD | Adobe ecosystem | Free | Low |
| Balsamiq | Quick wireframes | $9/mo | Low |

## Wireframe Best Practices

### Element Guidelines

| Element | Standard Size | Notes |
|---------|--------------|-------|
| Button (Primary) | 48px height | Full width on mobile |
| Button (Secondary) | 36px height | Half or third width |
| Input Field | 44px height | With 12px padding |
| List Item | 60-80px height | Includes icon/text |
| Icon | 24x24px | Standard icon set |
| Card | 160-200px width | 2-4 columns on mobile |

### Spacing System
- XS: 4px
- SM: 8px
- MD: 16px
- LG: 24px
- XL: 32px

## Common Module Templates

### Navigation Bar
```
┌─────────────────────────┐
│ [←Back]  [Title]  [···] │  <- 44-56px height
└─────────────────────────┘
```

### Tab Bar (Bottom)
```
┌─────────────────────────┐
│ [Home][Cart][Order][Me]│  <- 56px height, 4-5 tabs
└─────────────────────────┘
```

### List Item
```
┌─────────────────────────┐
│ [Img] Title       >    │  <- 60-80px
│       Subtitle          │
└─────────────────────────┘
```

### Form
```
┌─────────────────────────┐
│ Label                   │
│ [Input Field]           │  <- 44px height
│ Helper text             │
├─────────────────────────┤
│ Label (Required)        │
│ [Input Field]           │
│ Error message           │
└─────────────────────────┘
```

## Quality Standards

1. **Completeness**: All PRD pages covered
2. **Clarity**: Clear function annotations
3. **Drawability**: Can be directly implemented in Figma/Axure
4. **Consistency**: Unified style and naming
5. **Usability**: Follows platform design patterns

## Beginner Tips

### Use Placeholders
- Use gray boxes for images
- Use "Lorum Ipsum" for text
- Use standard icons (Font Awesome, Material Icons)

### Start Low-Fidelity
- Black and white first
- Add grayscale
- Then color

### Get Feedback Early
- Share with stakeholders
- Test with users
- Iterate quickly
