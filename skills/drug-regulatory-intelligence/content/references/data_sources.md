# 数据源检索指南

## NMPA (中国国家药品监督管理局)

### 参比制剂查询
- **网址**: https://www.cde.org.cn/
- **检索词**: {药品名称} + 参比制剂
- **关键字段**: RLD持证商、规格、批准文号

### 上市药品查询
- **网址**: https://www.nmpa.gov.cn/
- **检索词**: 药品名称 + 批准文号

---

## FDA (美国食品药品监督管理局)

### Orange Book查询
- **网址**: https://www.accessdata.fda.gov/scripts/cder/daf/
- **检索词**: 药品名称或活性成分
- **关键字段**:
  - Patent (专利信息)
  - Exclusivity (独占期)
  - TE (治疗等效性评价)

### 药品审批查询
- **网址**: https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda
- **检索词**: NDA/ANDA编号或药品名称

### 审评报告 (Drug Approval Reports)
- **网址**: https://www.accessdata.fda.gov/scripts/cder/reports/

---

## EMA (欧洲药品管理局)

### EPAR (欧洲公共评估报告)
- **网址**: https://www.ema.europa.eu/en/medicines/EMAEPAR/{药品名称}
- **检索词**: 产品名称或活性成分
- **关键文档**:
  - Product Information (SmPC)
  - Assessment History

### 数据库检索
- **EPAR数据库**: https://www.ema.europa.eu/en/medicines
- **临床试验**: https://www.clinicaltrialsregister.eu/

---

## PMDA (日本药品医疗器械综合机构)

### 审议报告
- **网址**: https://www.pmda.go.jp/english/review-services/reviews/approved-information/
- **检索词**: 一般名或製品名

### 批准品目
- **网址**: https://www.pmda.go.jp/english/review-services/approval-information/

---

## BE试验数据源

### 中国临床试验注册中心 (ChiCTR)
- **网址**: http://www.chictr.org.cn/
- **检索词**: 生物等效性 + 药品名称

### ClinicalTrials.gov
- **网址**: https://clinicaltrials.gov/
- **检索词**: Bioequivalence + 药品名称

### 中国知网 (CNKI)
- **检索词**: 生物等效性 + 药品名称

---

## 文献数据库

### PubMed
- **网址**: https://pubmed.ncbi.nlm.nih.gov/
- **检索策略**:
  ```
  ({药品名称}[Title/Abstract]) AND (bioequivalence[Title/Abstract] OR BE[Title/Abstract])
  ```

### Embase
- 检索词: bioequivalent study + drug name

### Web of Science
- 检索词: 生物等效性研究

---

## 检索技巧

### 1. 专利独占期分析
1. 在Orange Book搜索活性成分
2. 记录所有专利编号和到期日
3. 核实是否为有效专利
4. 检查独占期类型(NCE/PED/GAT)

### 2. 参比制剂确认
1. 优先确认RLD/RS指定
2. 核实持证商信息
3. 验证规格是否一致

### 3. BE试验筛选
1. 优先选择空腹+餐后双餐研究
2. 核实样本量与统计方法
3. 检查生物分析方法验证

### 4. 多源交叉验证
- NMPA批准信息与FDA ANDA交叉核对
- 专利到期日与监管记录验证
- BE结果与文献数据对比
