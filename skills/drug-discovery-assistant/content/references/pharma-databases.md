# Pharma Databases Reference

## 蛋白质结构数据库

### UniProt

**功能**: 通用蛋白质知识库

**主要数据**:
- 蛋白质序列
- 功能注释
- 分类信息
- 亚细胞定位
- 疾病关联

**访问方式**:
- Web: https://www.uniprot.org
- API: REST API可用

**关键字段**:
| 字段 | 说明 |
|------|------|
| Entry | UniProt ID |
| Gene Names | 基因符号 |
| Protein Names | 蛋白名称 |
| Length | 氨基酸长度 |
| Organism | 物种 |
| Function | 功能描述 |

### PDB (Protein Data Bank)

**功能**: 蛋白质3D结构数据库

**结构类型**:
- X-ray晶体学
- NMR
- Cryo-EM

**访问**: https://www.rcsb.org

**关键信息**:
- 分辨率
- 配体信息
- 链信息
- 实验方法

### AlphaFold

**功能**: AI预测蛋白质结构

**数据库**: https://alphafold.ebi.ac.uk

**优势**:
- 全蛋白质组覆盖
- 高精度预测
- 置信度分数 (pLDDT)

## 化合物数据库

### PubChem

**功能**: 化合物公共数据库

**数据内容**:
- 化合物结构
- 名称和别名
- 物理化学性质
- 生物活性
- 专利信息

**访问**: https://pubchem.ncbi.nlm.nih.gov

**API示例**:
```bash
# 化合物性质查询
curl "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/property/MolecularWeight,MolecularFormula/JSON"
```

### ChEMBL

**功能**: 药物化学活性数据

**数据内容**:
- 生物活性测定
- 靶点-化合物关系
- 药物发现项目

**访问**: https://www.ebi.ac.uk/chembl

### BindingDB

**功能**: 蛋白质-小分子结合亲和力

**数据**:
- Ki, Kd, IC50
- 实验条件
- 靶点信息

### DrugBank

**功能**: 药物和药物靶点信息

**数据内容**:
- 药物名称和结构
- 适应症
- 药物相互作用
- 靶点信息
- 药代动力学

**访问**: https://go.drugbank.com

## 靶点相关数据库

### OpenTargets

**功能**: 靶点-疾病关联证据

**数据源**:
- 遗传关联
- 表达数量性状位点(eQTL)
- 文本挖掘
- 药物关联

**平台**: https://platform.opentargets.org

### STRING

**功能**: 蛋白互作网络

**证据渠道**:
- 实验验证
- 数据库导入
- 共表达
- 基因融合
- 同源预测

### ClinVar

**功能**: 临床变异数据库

**变异解释**:
- Pathogenic
- Likely pathogenic
- Benign
- Likely benign
- Uncertain significance

## 临床研究数据库

### ClinicalTrials.gov

**功能**: 临床试验注册信息

**关键信息**:
- NCT编号
- 试验阶段
- 干预措施
- 入选标准
- 主要终点

### PubMed/MEDLINE

**功能**: 生物医学文献数据库

**检索策略**:
- MeSH词
- 自由词
- 布尔逻辑

### OpenAlex

**功能**: 开放学术文献

**数据**:
- 论文元数据
- 引用关系
- 开放获取状态

## API访问指南

### 通用原则

1. **速率限制**: 遵守API限制
2. **批量请求**: 使用批量接口
3. **缓存**: 缓存常用查询
4. **错误处理**: 实现重试机制

### 认证要求

| 数据库 | 认证需求 |
|--------|----------|
| UniProt | 无 |
| PDB | 无 |
| AlphaFold | 无 |
| PubChem | 无 |
| ChEMBL | 注册获取API key |
| OpenTargets | API key可选 |
| DrugBank | 需注册 |
