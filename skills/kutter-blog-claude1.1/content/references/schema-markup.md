# Structured Data Schema Markup Reference

This document provides complete JSON-LD schema markup templates for B2B manufacturing blog content.

## Base Layer Schema (Required for All Articles)

### 1. TechArticle Schema

```json
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Article Title (max 110 characters)",
  "description": "Article meta description (max 160 characters)",
  "author": {
    "@type": "Person",
    "name": "Mike Chen",
    "jobTitle": "Chief Engineer",
    "url": "https://yourdomain.com/about#mike-chen"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Your Company Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://yourdomain.com/logo.png"
    }
  },
  "datePublished": "2026-04-02",
  "dateModified": "2026-04-02",
  "proficiencyLevel": "Expert",
  "about": {
    "@type": "Thing",
    "name": "Primary Entity (e.g., SUS304 Stainless Steel)"
  }
}
```

### 2. FAQPage Schema

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question 1: How does X work?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text must be a complete paragraph with at least 50 characters."
      }
    },
    {
      "@type": "Question",
      "name": "Question 2: What is the difference between X and Y?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text must be a complete paragraph..."
      }
    }
  ]
}
```

### 3. BreadcrumbList Schema

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://yourdomain.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Category",
      "item": "https://yourdomain.com/category"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Article Title",
      "item": "https://yourdomain.com/article-slug"
    }
  ]
}
```

### 4. Person + Organization Schema

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "@id": "https://yourdomain.com/about#mike-chen",
      "name": "Mike Chen",
      "jobTitle": "Chief Engineer",
      "worksFor": {
        "@type": "Organization",
        "@id": "https://yourdomain.com/#organization"
      },
      "sameAs": [
        "https://www.linkedin.com/in/mikechen",
        "https://orcid.org/0000-0002-XXXX-XXXX"
      ]
    },
    {
      "@type": "Organization",
      "@id": "https://yourdomain.com/#organization",
      "name": "Your Company Name",
      "url": "https://yourdomain.com",
      "logo": {
        "@type": "ImageObject",
        "url": "https://yourdomain.com/logo.png"
      }
    }
  ]
}
```

---

## Enhanced Layer Schema (Add Based on Content Type)

### 5. HowTo Schema (How-To Guides)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "headline": "How to [Action]: Complete Guide",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step 1: [Title]",
      "text": "First, [complete action description with at least 2 sentences explaining the step in detail. Include specific measurements, tools, or conditions where applicable.]"
    },
    {
      "@type": "HowToStep",
      "name": "Step 2: [Title]",
      "text": "Next, [description]..."
    }
  ],
  "totalTime": "PT30M"
}
```

### 6. Product Schema (Product Showcase)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Model Number - Product Name",
  "description": "Product description...",
  "sku": "MODEL-001",
  "brand": {
    "@type": "Brand",
    "name": "Your Brand Name"
  },
  "manufacturer": {
    "@type": "Organization",
    "name": "Your Company Name"
  },
  "hasProductSpecification": [
    {
      "@type": "PropertyValue",
      "name": "Material",
      "value": "SUS304 Stainless Steel"
    },
    {
      "@type": "PropertyValue",
      "name": "Surface Finish",
      "value": "2B (Ra ≤ 0.8μm)"
    },
    {
      "@type": "PropertyValue",
      "name": "Thickness",
      "value": "1.0-3.0mm"
    }
  ],
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "127"
  }
}
```

### 7. Review Schema (Customer Reviews)

```json
{
  "@context": "https://schema.org",
  "@type": "Review",
  "reviewRating": {
    "@type": "Rating",
    "ratingValue": "5",
    "bestRating": "5"
  },
  "author": {
    "@type": "Person",
    "name": "John M."
  },
  "reviewBody": "Complete review text with at least 50 characters...",
  "itemReviewed": {
    "@type": "Product",
    "name": "Product Name"
  }
}
```

### 8. VideoObject Schema (Video Content)

```json
{
  "@context": "https://schema.org",
  "@type": "VideoObject",
  "name": "Video Title",
  "description": "Video description...",
  "thumbnailUrl": "https://yourdomain.com/video-thumbnail.jpg",
  "uploadDate": "2026-04-02",
  "duration": "PT5M30S",
  "contentUrl": "https://yourdomain.com/video.mp4",
  "embedUrl": "https://yourdomain.com/video-embed"
}
```

---

## AI Overviews Enhanced Schema (Claude 1.1 New)

### 9. ClaimReview Schema (Verifiable Claims)

```json
{
  "@context": "https://schema.org",
  "@type": "ClaimReview",
  "datePublished": "2026-04-02",
  "url": "https://yourdomain.com/article-slug",
  "claimReviewed": "Exact claim statement that can be verified...",
  "author": {
    "@type": "Person",
    "name": "Mike Chen"
  },
  "reviewRating": {
    "@type": "Rating",
    "ratingValue": "1",
    "bestRating": "1",
    "worstRating": "0",
    "alternateName": "True"
  }
}
```

### 10. Dataset Schema (Original Data)

```json
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "2026 Q1 [Product] Performance Test Results",
  "description": "Factory test data: [N] samples tested, per [Standard], [Conditions]",
  "creator": {
    "@type": "Organization",
    "name": "Your Company Name"
  },
  "datePublished": "2026-04-02",
  "distribution": [
    {
      "@type": "DataDownload",
      "contentUrl": "https://yourdomain.com/data/test-results-2026q1.pdf",
      "fileFormat": "application/pdf"
    }
  ]
}
```

### 11. QuantitativeValue + UnitCode (Standard Units)

```html
<!-- Use microdata to annotate values in HTML -->
<span itemscope itemtype="https://schema.org/QuantitativeValue">
  <span itemprop="value">15.3</span>
  <span itemprop="unitCode" content="P1">%</span>
</span>
```

Common UCUM unit codes:
- MMM: millimeters
- MTQ: cubic meters
- GRM: grams
- KGM: kilograms
- FAH: Fahrenheit
- CEL: Celsius
- P1: percent

---

## Validation Tools

1. **Google Rich Results Test**: https://search.google.com/test/rich-results
2. **Schema.org Validator**: https://validator.schema.org/
3. **JSON-LD Playground**: https://json-ld.org/playground/

## Deployment Checklist

- [ ] All JSON-LD wrapped in `<script type="application/ld+json">`
- [ ] Avoid duplicate types (no duplicate TechArticle on same page)
- [ ] @type first letter capitalized
- [ ] datePublished format: YYYY-MM-DD
- [ ] duration format: ISO 8601 (e.g., PT30M for 30 minutes)
- [ ] All URLs must be accessible
- [ ] Pass Google Rich Results Test validation
