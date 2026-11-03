# GEO Schema标记模板

本文档提供GEO优化中常用的结构化数据Schema模板，可直接嵌入网页或提供给开发团队实施。

---

## 1. FAQ Schema（常见问题）

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "问题1",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "回答1"
      }
    },
    {
      "@type": "Question",
      "name": "问题2",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "回答2"
      }
    }
  ]
}
```

**使用场景**：产品FAQ页、服务介绍页、帮助中心

---

## 2. HowTo Schema（操作指南）

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "如何完成某项任务",
  "description": "任务描述",
  "step": [
    {
      "@type": "HowToStep",
      "name": "步骤1标题",
      "text": "步骤1详细说明",
      "image": "步骤1图片URL"
    },
    {
      "@type": "HowToStep",
      "name": "步骤2标题",
      "text": "步骤2详细说明"
    }
  ],
  "totalTime": "PT15M",
  "supply": ["材料1", "材料2"],
  "tool": ["工具1", "工具2"]
}
```

**使用场景**：教程页面、操作指南、故障排除

---

## 3. Article Schema（文章）

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "文章标题",
  "description": "文章描述",
  "author": {
    "@type": "Person",
    "name": "作者姓名",
    "jobTitle": "职位",
    "sameAs": ["个人主页URL", "LinkedIn URL"]
  },
  "publisher": {
    "@type": "Organization",
    "name": "公司名称",
    "logo": {
      "@type": "ImageObject",
      "url": "Logo URL"
    }
  },
  "datePublished": "2024-01-01",
  "dateModified": "2024-01-15",
  "image": "主图URL",
  "keywords": ["关键词1", "关键词2"],
  "about": {
    "@type": "Thing",
    "name": "主题名称"
  }
}
```

**使用场景**：博客文章、新闻稿、深度分析

---

## 4. Organization Schema（组织）

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "公司名称",
  "url": "公司网站URL",
  "logo": "Logo URL",
  "description": "公司描述",
  "foundingDate": "2010-01-01",
  "founder": {
    "@type": "Person",
    "name": "创始人姓名"
  },
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "街道地址",
    "addressLocality": "城市",
    "addressRegion": "省份",
    "postalCode": "邮编",
    "addressCountry": "国家"
  },
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+86-xxx-xxxx-xxxx",
    "contactType": "customer service"
  },
  "sameAs": [
    "微博URL",
    "微信公众号URL",
    "LinkedIn URL",
    "Twitter URL"
  ]
}
```

**使用场景**：关于我们页面、联系页面、首页

---

## 5. BreadcrumbList Schema（面包屑导航）

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "首页",
      "item": "网站URL"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "分类",
      "item": "分类页URL"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "当前页面"
    }
  ]
}
```

**使用场景**：所有页面，提升导航清晰度

---

## 6. Product Schema（产品）

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "产品名称",
  "description": "产品描述",
  "image": "产品图片URL",
  "brand": {
    "@type": "Brand",
    "name": "品牌名称"
  },
  "sku": "产品SKU",
  "mpn": "制造商零件号",
  "offers": {
    "@type": "Offer",
    "url": "产品页面URL",
    "priceCurrency": "CNY",
    "price": "价格",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "卖家名称"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "128"
  }
}
```

**使用场景**：电商产品页、服务产品页

---

## 7. 行业特定Schema建议

### 医疗健康行业
- MedicalEntity
- MedicalCondition
- Drug

### 教育行业
- Course
- EducationalOccupationalProgram
- School

### 餐饮行业
- Restaurant
- Menu
- MenuItem
- Recipe

### 招聘行业
- JobPosting
- Organization (加入hiringOrganization)

### 房地产行业
- Place
- RealEstateListing
- House

---

## Schema实施检查清单

- [ ] 选择正确的@type
- [ ] 包含必填属性
- [ ] 使用正确的URL格式
- [ ] 验证JSON-LD语法
- [ ] 使用Google结构化数据测试工具验证
- [ ] 避免混合多个@type
- [ ] 保持数据最新（日期字段）
- [ ] 使用中文本地化属性（如适用）
