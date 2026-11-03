# Bio-Tools Reference

## 序列处理工具

### FASTA/FASTQ 操作

| 功能 | 工具 | 说明 |
|------|------|------|
| 序列提取 | seqkit | 快速FASTA/Q处理 |
| 质量控制 | FastQC | 测序质量评估 |
| 序列比对 | BLAST | 局部比对搜索 |
| 多序列比对 | Muscle/Clustal | 全局比对 |

### BAM/BED 文件处理

```bash
# BAM文件操作
samtools view -bS input.sam > output.bam
samtools sort input.bam -o sorted.bam
samtools index sorted.bam

# BED文件操作
bedtools intersect -a file1.bed -b file2.bed
bedtools closest -a genes.bed -b peaks.bed
```

### BLAST 比对

```bash
# 本地BLAST搜索
makeblastdb -in database.fasta -dbtype prot -out mydb
blastp -query query.fasta -db mydb -outfmt 6 -out results.txt
```

## 变异分析工具

### VCF/BCF 处理

```bash
# VCF过滤
bcftools filter -s LOWQUAL -e 'QUAL < 20' input.vcf

# VAF计算
bcftools +fill-tags input.vcf -- -t VAF
```

### 常用变异注释数据库

- **ClinVar**: 临床变异意义
- **dbSNP**: 单核苷酸多态性
- **gnomAD**: 人群频率
- **COSMIC**: 癌症体细胞突变

## 单细胞分析

### AnnData 操作

```python
import scanpy as sc

# 加载数据
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')

# 质控
sc.pp.calculate_qc_metrics(adata)

# 标准化
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# 聚类
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.leiden(adata, resolution=0.5)
```

## 调控网络分析

### GRNBoost2/GENIE3

```python
from arboreto.algo import grnboost2

# 构建基因调控网络
network = grnboost2(
    expression_data=expression_matrix,
    gene_names=gene_names,
   TF_names=tf_list
)
```

## 蛋白互作网络

### STRING 数据库

- 整合多种蛋白互作数据源
- 支持物种特异性网络
- 提供功能富集分析

### 节点属性

| 属性 | 说明 |
|------|------|
| score | 置信度分数 (0-1) |
| channel | 证据渠道类型 |
| nscore | 基因共表达分数 |
| fscore | 融合预测分数 |
| pscore | 同源预测分数 |
| ascore | 基因组邻居分数 |

## 通路分析

### KEGG 通路

- 代谢通路
- 信号通路
- 疾病相关通路

### Reactome 通路

- 分层通路结构
- 反应注释
- 疾病模块

## 质量控制检查清单

- [ ] 测序深度充足 (通常 > 30x)
- [ ] GC含量正常
- [ ] 无明显偏好性
- [ ] 重复率可接受 (<20%)
- [ ] 样本相关性高
