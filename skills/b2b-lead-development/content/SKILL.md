---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2e7f8bdd572440f49c0ef46d32964073
    PropagateID: 2e7f8bdd572440f49c0ef46d32964073
    ReservedCode1: 304502200f48f9c7903ddc26d00092b5430f24d5e032490a674d7f073fd17cda4564194d022100cd8a7d6af283a6fc95cceadf40299314c06d908a3a2748a233f354c4fbaaabd7
    ReservedCode2: 3045022100a3b522bbc0c3fb1535b26217b5bd5dd5ce2ffe79c036296beaa8f4fbd85727ba02203559860f2dc49fdc316bc22628c1d02e8da47a5dc52e008e77be4f3786de6d32
description: 外贸B2B线索开发全流程自动化技能。当用户要求开发客户、开发N个某国产品客户、找国外/海外客户、筛选公司、补邮箱whatsapp联系人、深挖现有客户、批量开发PDF目录展商名单公司名单时使用。输入产品/国家/客户类型，输出可直接跟进的客户包。
name: b2b-lead-development
---

# B2B线索开发技能

## 核心原则（硬规矩）

### 🔴 原则1: Browser-First（强制）

**必须使用受控浏览器走Google搜索**，模拟真人操作：
- 像人一样搜索、点击、浏览
- web_search/脚本搜索仅作为**辅助或救急手段**
- 不能代替主流程

### 🔴 原则2: 完成客户包优先

**单个公司做到"可跟进"优先于多而浅**：
- 每家公司必须完成：官网验证 → 联系方式 → 关键人 → 话术
- 不允许只留公司名+网址就跳过
- 宁可少而精，不要多而滥

### 🔴 原则3: 去重策略

**发现已存在 → 默认跳过（不自动合并）**：
- 检查公司名、域名、联系人邮箱是否已存在
- 遇到重复记录直接跳过，不覆盖
- 除非用户明确要求合并

### 🔴 原则4: 社媒优先级

**Facebook > LinkedIn > Instagram > TikTok > YouTube**

- 优先找Facebook商业主页
- 其次LinkedIn公司主页/个人主页
- Instagram/TikTok/Youtube作为补充信息源

### 🔴 原则5: 尽量找"人"

**能挖到人级联系人就不满足于通用邮箱**：
- 至少挖到一个人：老板/销售/采购/GM
- 有个人邮箱 > 只有info/sales通用邮箱
- 优先找决策人邮箱

---

## 标准工作流（一次跑完的流水线）

### Step 1: 解析意图

**输入**: 用户需求文本

**解析内容**:
- **国家**: 目标市场国家（墨西哥、美国、德国等）
- **产品**: 产品关键词（HVAC空调配件）
- **客户类型**: 进口商、分销商、经销商、零售商、批发商

**输出**:
```json
{
  "intent": {
    "country": "Mexico",
    "country_code": "MX",
    "product": "HVAC air conditioning parts",
    "product_keywords": ["HVAC", "air conditioning", "AC parts", "cooling system"],
    "customer_type": ["importer", "distributor"],
    "target_count": 5
  }
}
```

---

### Step 2: Google搜索发现候选公司

**Browser-First强制执行**:

1. 打开受控浏览器
2. 搜索: `[产品关键词] + importer/distributor + [国家]`
3. 搜索: `[产品关键词] + wholesale + [国家]`
4. 搜索: `[产品关键词] + [国家] + supplier`
5. 逐个点击自然搜索结果（不点广告）
6. 收集候选公司官网

**搜索模式**:
```
"HVAC parts" importer Mexico
"air conditioning" distributor Mexico
"AC components" wholesale Mexico
"HVAC supplier" Mexico
```

**输出**:
```json
{
  "candidates": [
    {
      "name": "Company Name",
      "website": "https://www.example.com",
      "search_query": "used to find",
      "position": 3,
      "source": "google_organic"
    }
  ]
}
```

---

### Step 3: 进官网验证

**必须检查页面**:
- [ ] 首页（Home）
- [ ] 关于我们（About Us）
- [ ] 联系页面（Contact Us）
- [ ] 页头（Header）—— 导航、CTA按钮
- [ ] 页脚（Footer）—— 地址、电话、社交图标
- [ ] 浮窗/弹窗（Popups）—— WhatsApp、订阅表单
- [ ] 产品页（Products）—— 确认产品相关性

**验证内容**:
- 公司名称与网站是否一致
- 公司地址是否在目标国家
- 是否正常运营（非停机、无效域名）
- 产品线是否与目标产品相关

**输出**:
```json
{
  "verified": {
    "name": "公司名",
    "website": "官网",
    "address": "地址",
    "country": "国家",
    "operating_status": "active/suspended/unknown",
    "product_relevance": "high/medium/low",
    "verified_pages": ["home", "about", "contact", "products"]
  }
}
```

---

### Step 4: 抽取联系方式

**提取优先级**:

1. **邮箱**: 域名邮箱 > info/sales通用邮箱
2. **电话**: 国际格式（+国码开头）
3. **WhatsApp**: 查找wa.me链接或显示的电话
4. **地址**: 完整地址（含邮编）
5. **表单**: Contact Form的action URL
6. **CTA按钮**: "Contact Us", "Get Quote", "Request Sample"

**提取字段**:
```json
{
  "contact": {
    "emails": [
      {"type": "domain", "value": "john@example.com", "confidence": "high"},
      {"type": "generic", "value": "info@example.com", "confidence": "medium"}
    ],
    "phones": [
      {"type": "landline", "value": "+52 55 1234 5678", "has_whatsapp": true},
      {"type": "mobile", "value": "+52 1 55 1234 5678", "has_whatsapp": true}
    ],
    "whatsapp": "+52 55 1234 5678",
    "address": "Av. Principal 123, Col. Centro, Mexico City, CP 06000",
    "form_url": "https://www.example.com/contact"
  }
}
```

---

### Step 5: 社媒二次挖掘

**社媒优先级**: Facebook > LinkedIn > Instagram > TikTok > YouTube

**执行步骤**:

1. 从官网页脚/页头找社交图标
2. 点击进入社交主页
3. 在社交页面二次挖掘：
   - 邮箱/电话是否直接显示
   - WhatsApp Business按钮
   - 官网链接
   - 联系人信息

**输出**:
```json
{
  "social_media": {
    "facebook": {
      "url": "https://facebook.com/example",
      "has_email": true,
      "has_phone": true,
      "has_whatsapp": false,
      "followers": "1.5K"
    },
    "linkedin": {
      "url": "https://linkedin.com/company/example",
      "followers": "500"
    },
    "instagram": {
      "url": "https://instagram.com/example"
    }
  }
}
```

---

### Step 6: 反向搜索补全

**当官网不够全时执行**:
- 官网无邮箱/电话
- 社交媒体信息不足
- 需要更多公司信息

**补全手段**:

1. **Google直接搜索公司名**:
   - `"公司名" + contact`
   - `"公司名" + email`
   - `"公司名" + phone`

2. **Google Maps搜索**:
   - 查看商家信息
   - 评价中的联系方式

3. **Hunter.io / Apollo查询**:
   - 输入域名查邮箱
   - 查公司员工邮箱

4. **LinkedIn站内搜索**:
   - 搜索公司名
   - 查看员工列表

**输出**:
```json
{
  "enriched": {
    "emails_found": 2,
    "phones_found": 1,
    "contacts_found": 3,
    "sources": ["google_search", "hunter_io", "linkedin"]
  }
}
```

---

### Step 7: 关键联系人搜索

**目标**: 把"公司级联系人"升级为"人级联系人"

**职位优先级**:

| 优先级 | 职位 | 价值 |
|--------|------|------|
| P1 | CEO/President/Owner | 最终决策人 |
| P1 | VP/Director of Purchasing | 采购决策 |
| P1 | Purchasing Manager | 执行采购 |
| P2 | Sales Manager/Director | 销售对接 |
| P2 | Product Manager | 产品线负责人 |
| P3 | Marketing Manager | 市场合作 |

**搜索方法**:

1. **LinkedIn个人主页搜索**:
   - 公司名 + 职位关键词
   - 查看公司页面员工

2. **官网团队页面**:
   - About Us -> Team
   - Meet the Team
   - Our Staff

3. **社媒帖子评论**:
   - 查看公司发帖人
   - 查看帖子评论中的公司员工

**输出**:
```json
{
  "key_contacts": [
    {
      "name": "Juan Garcia",
      "title": "Purchasing Manager",
      "linkedin": "https://linkedin.com/in/juangarcia",
      "email": "jgarcia@company.com",
      "email_confidence": "high",
      "decision_maker": true,
      "source": "linkedin"
    }
  ]
}
```

---

### Step 8: 评分（1-5星）

**评分维度**:

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| **联系方式完整性** | 25% | 有决策人邮箱=5★, 通用邮箱=3★, 仅官网=1★ |
| **WhatsApp可用性** | 20% | 有WhatsApp直接联系=5★, 无=0 |
| **产品相关性** | 20% | 产品高度匹配=5★, 中等=3★, 低=1★ |
| **公司规模** | 15% | 年营业额>1000万USD=5★, >500万=4★, >100万=3★ |
| **社媒活跃度** | 10% | 多平台活跃=5★, 仅官网=2★, 无社媒=1★ |
| **信息可验证性** | 10% | 多源验证=5★, 单源=3★, 未验证=1★ |

**最终评分**:
```
总评分 = Σ(维度评分 × 权重)
```

**分级**:
- ⭐⭐⭐⭐⭐ (4.5-5.0): 立即跟进，优先发送开发信
- ⭐⭐⭐⭐ (3.5-4.4): 常规跟进
- ⭐⭐⭐ (2.5-3.4): 排期跟进
- ⭐⭐ (1.5-2.4): 低优先级
- ⭐ (<1.5): 暂不跟进

**输出**:
```json
{
  "scoring": {
    "total_score": 4.2,
    "stars": 4,
    "grade": "A",
    "breakdown": {
      "contact_completeness": 5,
      "whatsapp_available": 5,
      "product_relevance": 4,
      "company_size": 4,
      "social_activity": 3,
      "data_verifiability": 4
    },
    "recommendation": "立即跟进"
  }
}
```

---

### Step 9: 生成开发内容

**必须生成**:

1. **英文开发信**（邮件）
2. **当地语言开发信**（如需要西班牙语/德语/法语）
3. **WhatsApp话术**（短消息）

**个性化要点**:
- 提及公司名
- 提及具体产品
- 提及对方市场/行业动态
- 提及共同话题或竞争者信息

**邮件格式**:
```json
{
  "email": {
    "subject": "[产品] Solution for [公司名] - [独特价值主张]",
    "body": "Hi [姓名],\n\nI noticed [公司名] is... [个性化内容]\n\n[价值主张]\n\n[CTA]\n\nBest regards,\n[你的名字]"
  },
  "whatsapp": {
    "message": "Hi [姓名]! I came across [公司名] and think we could help with [产品需求]. Would you be open to a quick chat?"
  }
}
```

---

### Step 10: 去重检查 → 写入存储

**去重检查**:

1. **公司名查重**: 精确匹配 + 模糊匹配（相似度>90%跳过）
2. **域名查重**: exactmatch
3. **联系人邮箱查重**: exact match
4. **电话查重**: 去掉格式后对比

**发现重复 → 默认跳过**

**存储选项**:

1. **飞书Bitable**（默认）: 写入指定Bitable
2. **本地JSON**: 生成JSON文件备份
3. **飞书文档**: 生成结构化文档

**输出格式**:
```json
{
  "customer_record": {
    "id": "uuid",
    "created_at": "2026-03-21T17:00:00Z",
    "company": {
      "name": "公司名",
      "website": "官网",
      "country": "国家",
      "address": "地址"
    },
    "contact": {
      "emails": [],
      "phones": [],
      "whatsapp": "",
      "social_media": {}
    },
    "key_contacts": [],
    "scoring": {},
    "outreach": {},
    "status": "pending_followup",
    "follow_up_date": "2026-03-28"
  }
}
```

---

## 数据落地

### 存储配置

```json
{
  "storage": {
    "primary": "feishu_bitable",
    "secondary": ["local_json", "notion"],
    "feishu": {
      "app_id": "${FEISHU_APP_ID}",
      "app_secret": "${FEISHU_APP_SECRET}",
      "table_id": "${FEISHU_BITABLE_TABLE_ID}"
    }
  }
}
```

### Bitable字段映射

| 字段 | 类型 | 说明 |
|------|------|------|
| company_name | 文本 | 公司名称 |
| website | 文本 | 官网URL |
| country | 文本 | 国家 |
| emails | 多选 | 邮箱列表 |
| phones | 多选 | 电话列表 |
| whatsapp | 文本 | WhatsApp号码 |
| facebook | 文本 | Facebook主页 |
| linkedin | 文本 | LinkedIn主页 |
| key_contact_name | 文本 | 关键人姓名 |
| key_contact_title | 文本 | 关键人职位 |
| key_contact_email | 文本 | 关键人邮箱 |
| key_contact_linkedin | 文本 | 关键人LinkedIn |
| score | 数字 | 总评分 |
| status | 单选 | 待跟进/已联系/有意向/成交/无效 |
| outreach_email | 文本 | 开发邮件内容 |
| outreach_whatsapp | 文本 | WhatsApp话术 |
| notes | 文本 | 备注 |

---

## 输入示例

### 示例1: 开发N个某国产品客户
```
帮我开发5个墨西哥HVAC空调配件客户
```

### 示例2: 找国外客户
```
找美国的LED灯进口商，要采购经理的邮箱
```

### 示例3: 批量开发
```
从这份展商名单里筛选德国的机械制造商，提取联系方式
```

### 示例4: 深挖现有客户
```
补充这个客户的WhatsApp和采购负责人邮箱
```

---

## 输出产物

1. **客户包**: 每家公司完整档案（可跟进状态）
2. **CSV导出**: 可导入CRM的表格
3. **跟进计划**: 含优先级、建议联系时间、话术提示
4. **存储确认**: 写入Bitable的记录ID

---

## 适用场景

- 开发N个某国产品客户
- 找国外/海外客户
- 筛选公司、补邮箱/whatsapp/联系人
- 深挖现有客户
- 从PDF/目录/展商名单/公司名单批量开发
- 展会后客户跟进
- 竞争对手客户挖角
