# B2B线索开发数据源参考

## 1. 海关数据平台

### 免费资源
- **ImportYeti** (importyeti.com) - 美国进口数据，免费额度
- **Datahawk** (datahawk.io) - 多国海关数据
- **Trade Map** (trademap.org) - ITC贸易数据

### 付费资源
- **Panjiva** (panjiva.com) - 美国海关数据
- **ImportGenius** (importgenius.com) - 深度美国进口商数据
- **Flexport** (flexport.com) - 物流+海关数据
- **Dat.com** - 全球海关数据

### 搜索技巧
- 使用HS编码精确筛选
- 筛选"buyers of [产品]" + 目标国家
- 提取活跃进口商（近6个月内）

---

## 2. 展会名录

### 国际展会官网
- **Eurotrade** (eurotradefair.com) - 欧洲展会名录
- **Trade Fair Data** (tradefairdata.com) - 全球展会信息
- **Eventbrite** - 商业展会

### 行业垂直展会
- 汉诺威工业展 (Hannover Messe)
- 广交会 (Canton Fair)
- CES消费电子展
- MEDICA医疗展
- Bauma工程机械展

### 参展商名录提取
- 展会官网Exhibitor List
- 展会媒体合作伙伴名录
- Google搜索: "[展会名] exhibitor list 2024/2025"

---

## 3. LinkedIn搜索

### 搜索语法
```
产品关键词 + importer + 国家
产品关键词 + buyer + 国家
产品关键词 + purchasing + manager
产品关键词 + sourcing + director
```

### 筛选条件
- 公司类型: Manufacturer, Importer, Distributor
- 职位: CEO, President, Owner, VP, Director, Purchasing Manager, Procurement
- 地区: 目标国家

### 工具
- **LinkedIn Sales Navigator** - 高级搜索+CRM集成
- **Apollo.io** - B2B邮箱+LinkedIn数据
- **Hunter.io** - 公司员工邮箱验证
- **Snov.io** - 邮箱查找+验证

---

## 4. Google搜索

### 搜索模式
```
"[产品英文名]" + importer + [国家]
"[产品英文名]" + buyer + [国家]
"[产品英文名]" + wholesale + [国家]
"[产品英文名]" + distributor + [国家]
"[产品英文名]" + "purchasing manager"
"[产品英文名]" + "procurement"
```

### B2B平台
- **Alibaba** - 筛选Global Brands/OEM manufacturers
- **Made-in-China** - 筛选Verified suppliers
- **Global Sources** - 筛选Golden suppliers
- **ThomasNet** - 美国工业制造商
- **Kompass** - 全球B2B企业目录
- **Europages** - 欧洲B2B目录

### 行业数据库
- **D&B (Dun & Bradstreet)** - 企业信用信息
- **Crunchbase** - 科技公司融资+信息
- **ZoomInfo** - B2B联系数据库
- **LeadFuze** - B2B邮箱+联系信息

---

## 5. 邮箱验证工具

### 验证服务
- **Hunter.io** - 邮箱验证+格式猜测
- **ZeroBounce** - 高精度邮箱验证
- **Clearout** - 邮箱验证+评分
- **NeverBounce** - 实时验证API
- **Mailtester** - 免费邮箱格式检查

### 邮箱格式规律
```
firstname.lastname@company.com
firstname@company.com
initial.lastname@company.com
firstname_lastname@company.com
```

---

## 6. 公司信息验证

### 各国工商查询
- **美国**: SEC EDGAR, D&B, State Business Registry
- **英国**: Companies House
- **德国**: Bundesanzeiger
- **中国**: 天眼查, 企查查
- **印度**: MCA India
- **越南**: DANGKY.KINHPHAM.GOV.VN

### 网站质量评估
- 域名年龄（用WHOIS查询）
- 网站内容完整性
- SSL证书
- 社交媒体活跃度

---

## 7. 社媒挖掘

### LinkedIn公司页
- 员工数量
- 公司描述
- 总部位置
- 行业分类
- 最近帖子活跃度

### Facebook商业页
- Business Page信息完整性
- 评分和评论
- 帖子频率

### Twitter/X企业账号
- 关注者数量
- 推文频率
- 互动率

---

## 8. 关键人识别优先级

| 优先级 | 职位 | 价值 |
|--------|------|------|
| P0 | CEO/President/Owner | 最终决策人 |
| P1 | VP/Director of Purchasing | 采购决策 |
| P1 | VP/Director of Sales | 销售合作 |
| P2 | Procurement Manager | 执行采购 |
| P2 | Product Manager | 产品线负责人 |
| P3 | Sales Manager | 销售对接 |
| P3 | Marketing Manager | 市场合作 |

---

## 9. 数据质量评分

### 高质量数据 (90-100分)
- 有公司注册信息验证
- 有关键人姓名+职位
- 有可直接发送的邮箱
- LinkedIn主页可验证

### 中等质量数据 (60-89分)
- 公司信息完整
- 有通用联系邮箱
- 无个人关键人信息

### 低质量数据 (30-59分)
- 仅公司名+官网
- 无明确联系方式
- 需要进一步挖掘
