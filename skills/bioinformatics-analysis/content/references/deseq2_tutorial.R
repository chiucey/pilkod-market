# ============================================================================
# DESeq2差异表达分析完整教程
# DESeq2 Differential Expression Analysis Complete Tutorial
# ============================================================================
# 作者：Bioinformatics Analysis Pipeline
# 版本：1.0.0
# 兼容：R 4.0+, DESeq2 1.30+
# ============================================================================

# ============================================================================
# 1. 环境准备与依赖安装
# ============================================================================

# 安装必要包（如果未安装）
if (!requireNamespace("DESeq2", quietly = TRUE)) {
  install.packages("BiocManager")
  BiocManager::install("DESeq2")
}

if (!requireNamespace("ggplot2", quietly = TRUE)) {
  install.packages("ggplot2")
}

# 加载包
library(DESeq2)
library(ggplot2)
library(ggrepel)
library(pheatmap)
library(clusterProfiler)
library(org.Hs.eg.db)
library(tidyverse)
library(RColorBrewer)
library(viridis)

# ============================================================================
# 2. 数据导入与预处理
# ============================================================================

#' 导入表达矩阵
#' @param count_file 计数矩阵文件路径 (CSV/TSV)
#' @param sep 分隔符
#' @return 计数矩阵
import_count_matrix <- function(count_file, sep = "\t") {
  count_matrix <- read.table(count_file, header = TRUE, row.names = 1, sep = sep)
  return(count_matrix)
}

#' 导入样本信息表
#' @param meta_file 样本信息文件路径
#' @param sep 分隔符
#' @return 样本信息数据框
import_sample_info <- function(meta_file, sep = "\t") {
  sample_info <- read.table(meta_file, header = TRUE, sep = sep)
  rownames(sample_info) <- sample_info[, 1]
  sample_info <- sample_info[, -1]
  return(sample_info)
}

#' 数据质量控制报告
#' @param count_matrix 计数矩阵
#' @param sample_info 样本信息
#' @return QC报告列表
qc_report <- function(count_matrix, sample_info) {

  # 计算每个样本的总reads数
  sample_reads <- colSums(count_matrix)

  # 计算每个基因的检出率
  gene_detection <- rowSums(count_matrix > 0) / ncol(count_matrix)

  # 绘制QC图
  p1 <- ggplot(data.frame(Sample = names(sample_reads),
                          Reads = sample_reads),
               aes(x = Sample, y = Reads)) +
    geom_bar(stat = "identity", fill = "#4DBBD5") +
    theme_classic() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
    labs(title = "Sample Sequencing Depth", x = "Sample", y = "Total Reads")

  # Pearson相关性热图
  cor_matrix <- cor(count_matrix)
  p2 <- pheatmap(cor_matrix,
                  color = colorRampPalette(brewer.pal(9, "Blues"))(100),
                  main = "Sample Correlation Heatmap")

  return(list(
    sample_reads = sample_reads,
    gene_detection = gene_detection,
    plot_reads = p1,
    plot_correlation = p2
  ))
}

# ============================================================================
# 3. DESeq2差异表达分析
# ============================================================================

#' DESeq2标准化和差异分析
#' @param count_matrix 原始计数矩阵 (基因 × 样本)
#' @param sample_info 样本信息表
#' @param design_formula 差异分析设计公式
#' @param contrast 比较组向量 c("condition", "treatment", "control")
#' @return DESeq2结果对象
run_deseq2 <- function(count_matrix, sample_info,
                       design_formula = "~ condition",
                       contrast = c("condition", "treatment", "control")) {

  # 确保列名匹配
  count_matrix <- count_matrix[, rownames(sample_info)]

  # 创建DESeq2数据集对象
  dds <- DESeqDataSetFromMatrix(
    countData = round(count_matrix),
    colData = sample_info,
    design = as.formula(design_formula)
  )

  # 预过滤：移除低表达基因
  # 保留在至少一半样本中表达的基因
  keep <- rowSums(counts(dds) >= 10) >= floor(ncol(dds) * 0.5)
  dds <- dds[keep, ]

  # 估计size factors进行标准化
  dds <- estimateSizeFactors(dds)

  # 估计离散度
  dds <- estimateDispersions(dds)

  # 负二项检验
  dds <- nbinomWaldTest(dds)

  # 提取结果
  resultsNames(dds)  # 查看可用的比较组

  # 指定比较组
  res <- results(dds, contrast = contrast, alpha = 0.05)

  # 使用apeglm进行LFC收缩（推荐）
  library(apeglm)
  res <- lfcShrink(dds, coef = paste0(contrast[1], "_", contrast[2], "_vs_", contrast[3]),
                   type = "apeglm")

  return(list(dds = dds, results = res))
}

#' 添加基因注释
#' @param results_df 差异分析结果
#' @param species 物种 ("human", "mouse", "rat")
#' @return 带注释的结果表
annotate_genes <- function(results_df, species = "human") {

  # 使用clusterProfiler进行ID转换
  gene_ids <- rownames(results_df)

  if (species == "human") {
    org_db <- org.Hs.eg.db
  } else if (species == "mouse") {
    org_db <- org.Mm.eg.db
  } else {
    org_db <- org.Rn.eg.db
  }

  # 转换ID（ENTREZID -> SYMBOL）
  annotated <- bitr(gene_ids,
                   fromType = "ENSEMBL",
                   toType = c("SYMBOL", "ENTREZID"),
                   OrgDb = org_db)

  # 合并注释
  results_df <- as.data.frame(results_df)
  results_df$gene_id <- rownames(results_df)
  results_df <- merge(results_df, annotated, by.x = "gene_id", by.y = "ENSEMBL",
                      all.x = TRUE)

  rownames(results_df) <- results_df$gene_id

  return(results_df)
}

#' 差异基因分类
#' @param results 差异分析结果
#' @param padj_threshold 显著性阈值
#' @param logfc_threshold log2FC阈值
#' @return 带分类标签的结果表
classify_deg <- function(results, padj_threshold = 0.05, logfc_threshold = 1) {

  results <- results %>%
    mutate(
      significance = case_when(
        padj < padj_threshold & log2FoldChange > logfc_threshold ~ "Up",
        padj < padj_threshold & log2FoldChange < -logfc_threshold ~ "Down",
        TRUE ~ "Not Significant"
      ),
      gene_symbol = ifelse(is.na(SYMBOL), gene_id, SYMBOL)
    )

  return(results)
}

# ============================================================================
# 4. 可视化函数
# ============================================================================

#' 火山图
#' @param deg_results 差异分析结果
#' @param padj 显著性阈值
#' @param logfc log2FC阈值
#' @param top_n 标注Top基因数
#' @param colors 配色向量
#' @return ggplot2对象
plot_volcano <- function(deg_results, padj = 0.05, logfc = 1,
                         top_n = 10, colors = NULL) {

  if (is.null(colors)) {
    colors <- c("Up" = "#E64B35", "Down" = "#4DBBD5", "Not Significant" = "#CCCCCC")
  }

  # 标记Top基因
  deg_results <- deg_results %>%
    mutate(
      label = ifelse(rank(padj) <= top_n & significance != "Not Significant",
                     gene_symbol, NA)
    )

  p <- ggplot(deg_results, aes(x = log2FoldChange, y = -log10(padj))) +

    # 散点
    geom_point(aes(color = significance), alpha = 0.6, size = 1.5) +

    # 阈值线
    geom_hline(yintercept = -log10(padj), linetype = "dashed",
               color = "grey40", linewidth = 0.5) +
    geom_vline(xintercept = c(-logfc, logfc), linetype = "dashed",
               color = "grey40", linewidth = 0.5) +

    # 基因标注
    geom_text_repel(
      aes(label = label),
      size = 2.5,
      max.overlaps = 20,
      min.segment.length = 0.1
    ) +

    # 配色
    scale_color_manual(values = colors, name = "") +

    # 主题
    theme_classic(base_size = 10) +
    theme(
      legend.position = "top",
      panel.border = element_rect(fill = NA, linewidth = 0.5),
      axis.title = element_text(size = 11, face = "bold"),
      axis.text = element_text(size = 10),
      plot.title = element_text(size = 12, hjust = 0.5, face = "bold")
    ) +

    # 标签
    labs(
      x = expression(log[2]~Fold~Change),
      y = expression(-log[10]~P[adj]),
      title = "Volcano Plot"
    )

  return(p)
}

#' 热图
#' @param count_matrix 表达矩阵（已标准化）
#' @param deg_results 差异基因
#' @param sample_info 样本信息
#' @param n_genes 显示基因数
#' @return 热图对象
plot_heatmap <- function(count_matrix, deg_results, sample_info, n_genes = 50) {

  # 获取Top差异基因
  top_genes <- deg_results %>%
    filter(significance != "Not Significant") %>%
    arrange(padj) %>%
    head(n_genes) %>%
    pull(gene_id)

  # 提取子矩阵
  mat <- count_matrix[rownames(count_matrix) %in% top_genes, ]
  mat <- mat - rowMeans(mat)  # Z-score标准化

  # 分组信息
  annotation_col <- data.frame(
    Condition = sample_info$condition,
    row.names = rownames(sample_info)
  )

  # 配色
  ann_colors <- list(
    Condition = c(treatment = "#E64B35", control = "#4DBBD5")
  )

  # 绘制热图
  p <- pheatmap(
    mat,
    annotation_col = annotation_col,
    annotation_colors = ann_colors,
    color = viridis(100, option = "D"),
    scale = "row",
    clustering_distance_rows = "euclidean",
    clustering_distance_cols = "euclidean",
    clustering_method = "ward.D2",
    show_rownames = FALSE,
    show_colnames = TRUE,
    fontsize = 9,
    main = paste0("Top ", n_genes, " Differentially Expressed Genes")
  )

  return(p)
}

#' PCA图
#' @param dds DESeq2对象
#' @param sample_info 样本信息
#' @param condition_var 分组变量
#' @return PCA图
plot_pca <- function(dds, sample_info, condition_var = "condition") {

  # 获取vst标准化后的数据
  vsd <- vst(dds, blind = FALSE)

  # 计算PCA
  pca_data <- DESeq2::plotPCA(vsd, intgroup = condition_var, returnData = TRUE)
  percentVar <- round(100 * attr(pca_data, "percentVar"))

  # 绘图
  p <- ggplot(pca_data, aes(x = PC1, y = PC2, color = group)) +
    geom_point(size = 3, alpha = 0.8) +
    geom_text_repel(aes(label = name), size = 2.5, max.overlaps = 15) +
    scale_color_brewer(palette = "Set1", name = condition_var) +
    theme_classic(base_size = 10) +
    theme(
      panel.border = element_rect(fill = NA, linewidth = 0.5),
      legend.position = "right"
    ) +
    labs(
      x = paste0("PC1: ", percentVar[1], "% variance"),
      y = paste0("PC2: ", percentVar[2], "% variance"),
      title = "Principal Component Analysis"
    )

  return(p)
}

#' MA图
#' @param results 差异分析结果
#' @param padj 显著性阈值
#' @return MA图
plot_ma <- function(results, padj = 0.05) {

  results <- as.data.frame(results)

  p <- ggplot(results, aes(x = baseMean, y = log2FoldChange)) +
    geom_point(aes(color = padj < padj), alpha = 0.5, size = 1) +
    scale_x_log10() +
    geom_hline(yintercept = 0, color = "grey40", linetype = "dashed") +
    scale_color_manual(values = c("TRUE" = "#E64B35", "FALSE" = "#CCCCCC"),
                      name = paste0("P.adj < ", padj)) +
    theme_classic(base_size = 10) +
    theme(
      legend.position = "top",
      panel.border = element_rect(fill = NA, linewidth = 0.5)
    ) +
    labs(
      x = "Mean Expression",
      y = "log2 Fold Change",
      title = "MA Plot"
    )

  return(p)
}

# ============================================================================
# 5. 富集分析
# ============================================================================

#' GO/KEGG富集分析
#' @param gene_list 基因列表（ENTREZID或SYMBOL）
#' @param species 物种
#' @param ont ontology类型 ("BP", "MF", "CC", "ALL")
#' @param pvalueCutoff p值阈值
#' @return 富集结果
run_enrichment <- function(gene_list, species = "human",
                          ont = "ALL", pvalueCutoff = 0.05) {

  # 物种数据库映射
  if (species == "human") {
    org_db <- org.Hs.eg.db
    organism <- "hsa"
  } else if (species == "mouse") {
    org_db <- org.Mm.eg.db
    organism <- "mmu"
  } else {
    org_db <- org.Rn.eg.db
    organism <- "rno"
  }

  # GO富集
  ego <- enrichGO(
    gene = gene_list,
    OrgDb = org_db,
    ont = ont,
    pAdjustMethod = "BH",
    pvalueCutoff = pvalueCutoff,
    qvalueCutoff = 0.2,
    readable = TRUE
  )

  # KEGG富集
  ekegg <- enrichKEGG(
    gene = gene_list,
    organism = organism,
    pAdjustMethod = "BH",
    pvalueCutoff = pvalueCutoff
  )

  return(list(GO = ego, KEGG = ekegg))
}

#' 富集分析可视化
#' @param enrich_result 富集结果
#' @param title 标题
#' @param n_show 显示条目数
#' @return 绑图对象
plot_enrichment <- function(enrich_result, title = "Enrichment Analysis",
                            n_show = 15) {

  df <- as.data.frame(enrich_result)
  df <- head(df, n_show)

  # 按p值排序
  df <- df[order(df$p.adjust), ]
  df$Description <- factor(df$Description, levels = rev(df$Description))

  # 颜色映射
  pvalue_range <- range(df$p.adjust)
  color_scale <- scale_color_viridis(option = "plasma", direction = -1,
                                    limits = pvalue_range, oob = scales::squish)

  p <- ggplot(df, aes(x = Count, y = Description, size = Count, color = p.adjust)) +
    geom_point() +
    color_scale +
    theme_classic(base_size = 10) +
    theme(
      panel.border = element_rect(fill = NA, linewidth = 0.5),
      axis.text.y = element_text(size = 9),
      legend.position = "right"
    ) +
    labs(
      x = "Gene Count",
      y = "",
      title = title,
      color = "P.adj",
      size = "Count"
    )

  return(p)
}

# ============================================================================
# 6. 输出和报告生成
# ============================================================================

#' 导出结果
#' @param deg_results 差异分析结果
#' @param output_dir 输出目录
#' @param prefix 文件前缀
export_results <- function(deg_results, output_dir, prefix = "DEG") {

  dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

  # 完整结果
  write.table(
    deg_results,
    file.path(output_dir, paste0(prefix, "_all_results.tsv")),
    sep = "\t", quote = FALSE, row.names = TRUE
  )

  # 上调基因
  up_genes <- deg_results %>% filter(significance == "Up")
  write.table(
    up_genes,
    file.path(output_dir, paste0(prefix, "_upregulated.tsv")),
    sep = "\t", quote = FALSE, row.names = TRUE
  )

  # 下调基因
  down_genes <- deg_results %>% filter(significance == "Down")
  write.table(
    down_genes,
    file.path(output_dir, paste0(prefix, "_downregulated.tsv")),
    sep = "\t", quote = FALSE, row.names = TRUE
  )

  cat("Results exported to:", output_dir, "\n")
  cat("Up-regulated genes:", nrow(up_genes), "\n")
  cat("Down-regulated genes:", nrow(down_genes), "\n")
}

#' 生成分析报告
#' @param dds DESeq2对象
#' @param results 差异分析结果
#' @param deg_results 分类后的差异基因
#' @param output_dir 输出目录
generate_report <- function(dds, results, deg_results, output_dir) {

  report_content <- paste0("
# Differential Expression Analysis Report

## Summary Statistics

- Total genes analyzed: ", nrow(results), "
- Up-regulated genes (P.adj < 0.05, |log2FC| > 1): ",
sum(deg_results$significance == "Up"), "
- Down-regulated genes: ",
sum(deg_results$significance == "Down"), "

## Top Up-regulated Genes

",
paste(head(deg_results %>% filter(significance == "Up") %>%
           arrange(log2FoldChange) %>% select(gene_symbol, log2FoldChange, padj), 10),
      collapse = "\n"), "

## Top Down-regulated Genes

",
paste(head(deg_results %>% filter(significance == "Down") %>%
           arrange(-log2FoldChange) %>% select(gene_symbol, log2FoldChange, padj), 10),
      collapse = "\n"), "

## Session Information

```
", capture.output(sessionInfo()), "
```
")

  writeLines(report_content, file.path(output_dir, "analysis_report.md"))
}

# ============================================================================
# 7. 完整分析流程演示
# ============================================================================

#' 运行完整分析流程
#' @param count_matrix 计数矩阵
#' @param sample_info 样本信息
#' @param contrast 比较组
#' @param output_dir 输出目录
run_complete_analysis <- function(count_matrix, sample_info,
                                  contrast = c("condition", "treatment", "control"),
                                  output_dir = "./results") {

  cat("=== Step 1: Quality Control ===\n")
  qc <- qc_report(count_matrix, sample_info)

  cat("=== Step 2: Differential Expression Analysis ===\n")
  dds_results <- run_deseq2(count_matrix, sample_info, contrast = contrast)
  dds <- dds_results$dds
  res <- dds_results$results

  cat("=== Step 3: Gene Annotation ===\n")
  annotated <- annotate_genes(res, species = "human")

  cat("=== Step 4: DEG Classification ===\n")
  deg_results <- classify_deg(annotated)

  cat("=== Step 5: Visualization ===\n")
  p_volcano <- plot_volcano(deg_results)
  p_heatmap <- plot_heatmap(count_matrix, deg_results, sample_info)
  p_pca <- plot_pca(dds, sample_info)
  p_ma <- plot_ma(res)

  # 保存图片
  ggsave(file.path(output_dir, "volcano_plot.pdf"), p_volcano,
         width = 7, height = 6)
  ggsave(file.path(output_dir, "pca_plot.pdf"), p_pca,
         width = 6, height = 5)

  cat("=== Step 6: Export Results ===\n")
  export_results(deg_results, output_dir)

  return(list(
    dds = dds,
    results = res,
    deg_results = deg_results,
    plots = list(
      volcano = p_volcano,
      heatmap = p_heatmap,
      pca = p_pca,
      ma = p_ma
    )
  ))
}

# ============================================================================
# 8. 示例数据运行
# ============================================================================

# 创建模拟数据用于演示
demo_analysis <- function() {

  set.seed(42)

  # 模拟计数矩阵
  n_genes <- 10000
  n_samples <- 6

  count_matrix <- matrix(
    rnbinom(n_genes * n_samples, size = 10, mu = 100),
    nrow = n_genes
  )
  rownames(count_matrix) <- paste0("ENSG", seq_len(n_genes))
  colnames(count_matrix) <- paste0("Sample_", seq_len(n_samples))

  # 模拟样本信息
  sample_info <- data.frame(
    sample = colnames(count_matrix),
    condition = rep(c("control", "treatment"), each = 3),
    replicate = rep(1:3, 2),
    row.names = colnames(count_matrix)
  )

  # 运行分析
  results <- run_complete_analysis(count_matrix, sample_info)

  return(results)
}

# 运行演示
if (interactive()) {
  demo_results <- demo_analysis()
  print(demo_results$deg_results %>% count(significance))
}
