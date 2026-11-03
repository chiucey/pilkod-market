# 数据验证规则

## 1. 公司信息验证规则

### 1.1 必填字段验证

```json
{
  "required_fields": {
    "company_name": {
      "type": "string",
      "min_length": 2,
      "max_length": 200,
      "required": true
    },
    "country": {
      "type": "string",
      "required": true,
      "validation": "ISO 3166-1 alpha-2 code"
    },
    "website": {
      "type": "string",
      "required": true,
      "validation": "valid URL format"
    }
  }
}
```

### 1.2 公司规模验证

| 规模 | 员工数 | 年营业额 | 优先级 |
|------|--------|----------|--------|
| Large | 500+ | 5000万USD+ | P1 (最高) |
| Medium | 100-499 | 500万-5000万USD | P2 |
| Small | 20-99 | 50万-500万USD | P3 |
| Micro | <20 | <50万USD | P4 (最低) |

### 1.3 业务类型验证

```json
{
  "business_types": {
    "manufacturer": {
      "is_ideal_customer": true,
      "priority": 1,
      "notes": "可能是竞争对手，需评估"
    },
    "importer": {
      "is_ideal_customer": true,
      "priority": 1,
      "notes": "最佳目标客户"
    },
    "wholesaler": {
      "is_ideal_customer": true,
      "priority": 2,
      "notes": "批发商，订单量大"
    },
    "distributor": {
      "is_ideal_customer": true,
      "priority": 2,
      "notes": "分销商，有渠道优势"
    },
    "retailer": {
      "is_ideal_customer": false,
      "priority": 3,
      "notes": "零售商，订单量小"
    },
    "competitor": {
      "is_ideal_customer": false,
      "priority": 4,
      "notes": "直接竞争对手"
    }
  }
}
```

---

## 2. 联系方式验证规则

### 2.1 邮箱格式验证

```json
{
  "email_validation": {
    "format_check": true,
    "domain_verification": true,
    "disposable_email_check": true,
    "role_based_check": true
  },
  "email_scoring": {
    "firstname.lastname@domain.com": 100,
    "firstname@domain.com": 90,
    "initial.lastname@domain.com": 80,
    "info@domain.com": 60,
    "sales@domain.com": 50,
    "contact@domain.com": 50,
    "unknown pattern": 30
  }
}
```

### 2.2 电话号码验证

```json
{
  "phone_validation": {
    "country_code_required": true,
    "min_length": 8,
    "max_length": 15,
    "format": "E.164 international format"
  }
}
```

### 2.3 社媒链接验证

```json
{
  "social_media_validation": {
    "linkedin": {
      "required": true,
      "validation": "Valid LinkedIn URL pattern",
      "company_or_personal": "both"
    },
    "facebook": {
      "required": false,
      "validation": "Valid Facebook URL"
    },
    "twitter": {
      "required": false,
      "validation": "Valid Twitter/X URL"
    }
  }
}
```

---

## 3. 关键人信息验证

### 3.1 职位匹配度

```json
{
  "title_match_score": {
    "CEO/President/Owner": 100,
    "Managing Director": 100,
    "VP of Purchasing/Procurement": 95,
    "VP of Sales": 90,
    "Director of Purchasing": 90,
    "Director of [相关部门]": 80,
    "Procurement Manager": 85,
    "Purchasing Manager": 85,
    "Sourcing Manager": 85,
    "Product Manager": 75,
    "Sales Manager": 70,
    "Marketing Manager": 60,
    "Other": 30
  }
}
```

### 3.2 LinkedIn主页验证

```json
{
  "linkedin_profile_check": {
    "profile_photo": "recommended",
    "headline_complete": true,
    "experience_listed": true,
    "connection_count": ">100 preferred",
    "recent_activity": "within 30 days preferred"
  }
}
```

---

## 4. 数据去重规则

### 4.1 去重逻辑

```json
{
  "deduplication_rules": [
    {
      "field": "website",
      "type": "exact",
      "action": "merge",
      "priority": "keep_most_complete"
    },
    {
      "field": "company_name",
      "type": "fuzzy",
      "threshold": 0.9,
      "action": "review",
      "notes": "人工复核"
    },
    {
      "field": "email",
      "type": "exact",
      "action": "merge",
      "priority": "keep_newest"
    },
    {
      "field": "phone",
      "type": "exact",
      "action": "merge",
      "priority": "keep_most_complete"
    }
  ]
}
```

### 4.2 数据合并规则

```json
{
  "merge_strategy": {
    "conflict_resolution": {
      "contact_info": "keep_verified",
      "company_info": "keep_most_recent",
      "social_media": "keep_all_unique"
    }
  }
}
```

---

## 5. 优先级评分模型

### 5.1 综合评分计算

```json
{
  "priority_score": {
    "calculation": "weighted_sum",
    "weights": {
      "company_match": 0.25,
      "contact_quality": 0.30,
      "decision_maker": 0.25,
      "data_completeness": 0.20
    }
  }
}
```

### 5.2 评分标准

| 分数 | 等级 | 含义 |
|------|------|------|
| 90-100 | A+ | 立即跟进 |
| 80-89 | A | 优先跟进 |
| 70-79 | B+ | 常规跟进 |
| 60-69 | B | 排期跟进 |
| 50-59 | C | 低优先级 |
| <50 | D | 暂不跟进 |

---

## 6. 数据完整性检查

### 6.1 最小可行数据

```json
{
  "minimum_viable_record": {
    "company_name": "required",
    "country": "required",
    "website": "required",
    "one_contact_method": "required (email OR phone)"
  }
}
```

### 6.2 完整数据标准

```json
{
  "complete_record": {
    "basic_info": ["name", "country", "website", "address"],
    "business_info": ["business_type", "employee_count", "annual_revenue"],
    "contact_info": ["email", "phone", "general_email"],
    "social_media": ["linkedin", "facebook"],
    "key_contact": ["name", "title", "email", "linkedin"]
  }
}
```

---

## 7. 质量标记

### 7.1 数据质量标签

```json
{
  "quality_tags": {
    "verified": "通过多源验证",
    "unverified": "单源数据",
    "disputed": "存在冲突信息",
    "outdated": "超过6个月未更新",
    "incomplete": "缺少必填字段",
    "spam": "垃圾/无效数据"
  }
}
```

---

## 8. 常见问题处理

### 8.1 联系方式缺失

**处理流程**:
1. 尝试Hunter.io等工具查找
2. LinkedIn站内搜索
3. 官网Contact页面查找
4. 标记为"需手动跟进"

### 8.2 公司名不准确

**处理流程**:
1. 提取官网实际注册名
2. 交叉验证注册号
3. 与工商数据比对
4. 保留别名作为参考

### 8.3 多个相似公司

**处理流程**:
1. 分析是否为母公司/子公司
2. 判断是否为同一集团不同业务线
3. 优先跟进母公司
4. 记录所有关联公司
