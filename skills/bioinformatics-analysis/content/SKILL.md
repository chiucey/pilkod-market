---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 0e645a73d4546873920d617e04776bee
    PropagateID: 0e645a73d4546873920d617e04776bee
    ReservedCode1: 3046022100da2bf0891bb8f04523a01254342a034a23415db4aeed63e351a24435b0ad7697022100e304fd10eb2ecc0168f8f6bfbcdf3e07912c6b24c69ca9b513f2cff6973088cf
    ReservedCode2: 3044022009528d003cd454b85acdde0bbbc77638efe9e2ee75da58e6b3a3da6f4b23730f02200404d0ed3b8a071b397445e82155b2bee90104e77023115ffed6ed3d042a9145
---

# Bioinformatics Analysis Skill

## Core Capabilities

This skill provides a comprehensive bioinformatics data analysis workflow with R and Python dual-language support, ensuring SCI publication-grade code and figures.

## Workflow

### 1. Requirement Analysis Phase

Collect and confirm the following key information:

| Analysis Type | Input Data | Output | Recommended Tools |
|---------------|------------|--------|------------------|
| Differential Expression | Expression matrix | DEGs list, Volcano plot | DESeq2/edgeR/limma |
| Enrichment Analysis | Gene list | GO/KEGG pathways | clusterProfiler/GSEA |
| PCA/t-SNE | Expression matrix | Dimensionality reduction | ggplot2/seaborn |
| Heatmap Analysis | Expression matrix | Clustering heatmap | pheatmap/ComplexHeatmap |
| PPI Network | Gene list | PPI network | STRING/Cytoscape |
| Single-cell Analysis | scRNA-seq data | Cell clustering, markers | Seurat/Scanpy |

**Requirement Collection Form:**

```
1. Analysis Purpose: [Basic Research/Clinical Diagnosis/Drug Development/Method Validation]
2. Data Type: [Bulk RNA-seq/small RNA-seq/Proteomics/scRNA-seq/ChIP-seq]
3. Species: [Human/Mouse/Rat/Other]
4. Sample Count: ______
5. Number of Comparisons: ______
6. Required Analyses: □Differential Expression □Enrichment □Clustering □Machine Learning □Network
7. Target Journal: [Impact Factor/Color Preferences]
8. Preferred Language: □R □Python □Either
```

### 2. Sample Data Construction

Build sample data with statistical properties based on requirements:

- **Expression Matrix Format**: Gene x Sample
- **Clinical Info Table**: Sample x Clinical Features
- **Gene Annotation Table**: ID conversion, functional annotation

Sample Data Structure:
```r
# R Example: Generate simulated expression matrix
set.seed(42)
n_genes <- 15000
n_samples <- 12
expr_matrix <- matrix(
  rnbinom(n_genes * n_samples, size = 10, mu = 100),
  nrow = n_genes, ncol = n_samples
)
rownames(expr_matrix) <- paste0("GENE", 1:n_genes)
colnames(expr_matrix) <- paste0("Sample_", 1:n_samples)
```

```python
# Python Example: Generate simulated expression matrix
import numpy as np
import pandas as pd

np.random.seed(42)
n_genes, n_samples = 15000, 12
expr_matrix = np.random.negative_binomial(10, 0.5, (n_genes, n_samples))
expr_df = pd.DataFrame(
    expr_matrix,
    index=[f"GENE{i}" for i in range(1, n_genes + 1)],
    columns=[f"Sample_{i}" for i in range(1, n_samples + 1)]
)
```

### 3. Code Development Standards

#### 3.1 R Language Code Standards

```r
# ============================================================================
# Differential Expression Analysis Script
# Author: Bioinformatics Analysis Pipeline
# Version: 1.0.0
# Date: 2024
# ============================================================================

#' @title DESeq2 Differential Expression Analysis
#' @description Perform normalization and differential expression analysis on RNA-seq data
#' @param count_matrix Raw count matrix (gene x sample)
#' @param sample_info Sample information table (with group info)
#' @param contrast Comparison vector c("condition", "treatment", "control")
#' @param padj_threshold Significance threshold (default 0.05)
#' @param logfc_threshold Log fold change threshold (default 1)
#' @return List of differentially expressed genes
#' @export
deseq2_analysis <- function(count_matrix, sample_info,
                            contrast = c("condition", "treatment", "control"),
                            padj_threshold = 0.05,
                            logfc_threshold = 1) {

  # =========================================================================
  # Step 1: Data Preprocessing and Quality Control
  # =========================================================================

  # Load required packages
  library(DESeq2)
  library(ggplot2)
  library(ggrepel)
  library(pheatmap)

  # Create DESeq2 object
  dds <- DESeqDataSetFromMatrix(
    countData = count_matrix,
    colData = sample_info,
    design = as.formula(paste("~", contrast[1]))
  )

  # Filter low-expressed genes (expressed in at least 3 samples)
  keep <- rowSums(counts(dds) >= 10) >= 3
  dds <- dds[keep, ]

  # =========================================================================
  # Step 2: Differential Analysis
  # =========================================================================

  # Set reference group
  dds[[contrast[1]]] <- relevel(dds[[contrast[1]]], ref = contrast[3])

  # Run analysis
  dds <- DESeq(dds)
  res <- results(dds, contrast = contrast, alpha = padj_threshold)

  # Add gene symbols and annotations
  res <- as.data.frame(res)
  res$gene_id <- rownames(res)

  # Classify results
  res$sig_status <- "Not Significant"
  res$sig_status[res$padj < padj_threshold & res$log2FoldChange > logfc_threshold] <- "Up"
  res$sig_status[res$padj < padj_threshold & res$log2FoldChange < -logfc_threshold] <- "Down"

  return(res)
}
```

#### 3.2 Python Language Code Standards

```python
"""
Differential Expression Analysis Module
Author: Bioinformatics Analysis Pipeline
Version: 1.0.0
Date: 2024
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import pandas as pd

# ============================================================================
# Data Class Definition
# ============================================================================

@dataclass
class AnalysisConfig:
    """Analysis configuration parameters"""
    padj_threshold: float = 0.05
    logfc_threshold: float = 1.0
    lfc_shrinkage: bool = True
    filter_min_count: int = 10
    filter_min_samples: int = 3


# ============================================================================
# Core Analysis Functions
# ============================================================================

def differential_expression_analysis(
    count_matrix: pd.DataFrame,
    sample_info: pd.DataFrame,
    contrast: Tuple[str, str, str],
    config: Optional[AnalysisConfig] = None
) -> pd.DataFrame:
    """
    DESeq2-style differential expression analysis

    Parameters
    ----------
    count_matrix : pd.DataFrame
        Raw count matrix (gene x sample)
    sample_info : pd.DataFrame
        Sample info table (sample x clinical features)
    contrast : Tuple[str, str, str]
        Comparison (condition column, treatment, control)
    config : AnalysisConfig, optional
        Analysis configuration

    Returns
    -------
    pd.DataFrame
        Differential expression results table
    """
    # Dynamic import for optional dependencies
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.packages import importr

    # Activate R to Python conversion
    pandas2ri.activate()

    # Import DESeq2
    deseq2 = importr('DESeq2')

    # Default configuration
    if config is None:
        config = AnalysisConfig()

    # Convert to R objects and execute analysis
    # ... (detailed implementation in references/deseq2_python_implementation.py)

    return results_df
```

### 4. Figure Style Optimization

#### 4.1 SCI Standard Color Schemes

| Color Scheme | Use Case | Colors |
|--------------|----------|--------|
| **Nature Standard** | General scientific figures | #E64B35, #4DBBD5, #00A087, #3C5488 |
| **Colorblind Safe** | Colorblind readers | #0173B2, #DE8F05, #029E73, #CC78BC |
| **Viridis** | Heatmaps, continuous variables | #440154 → #21918C → #FDE725 |
| **Grayscale** | Print/B&W scenarios | #000000, #666666, #999999, #CCCCCC |
| **Scientific** | Multi-omics integration | #8C1538, #F3766E, #A1D3B2, #3D6B8C |

**R Color Implementation:**
```r
# SCI Standard Color Palette
sci_palette <- c(
  "Nature" = "#E64B35",  # Red
  "Up" = "#E64B35",      # Up-regulated
  "Down" = "#4DBBD5",    # Down-regulated
  "NS" = "#CCCCCC"       # Not Significant
)

# Viridis color functions
install.packages("viridis")
library(viridis)

# Continuous variable heatmap
scale_fill_viridis(option = "D", direction = -1)

# Discrete variables
scale_fill_viridis_d(option = "plasma")
```

**Python Color Implementation:**
```python
import matplotlib.pyplot as plt
import seaborn as sns

# SCI Standard Colors
SCI_COLORS = {
    'primary': '#E64B35',      # Red
    'secondary': '#4DBBD5',    # Cyan
    'tertiary': '#00A087',     # Green
    'quaternary': '#3C5488',   # Dark blue
    'up': '#E64B35',          # Up-regulated
    'down': '#4DBBD5',         # Down-regulated
    'ns': '#CCCCCC'            # Not Significant
}

# Set global colors
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
sns.set_palette("husl")

# Viridis colormap
cmap = sns.color_palette("viridis", as_cmap=True)
```

#### 4.2 Standard Figure Dimensions

| Figure Type | Single Column | Double Column | Resolution |
|-------------|---------------|---------------|------------|
| Figure | 89 mm | 183 mm | 300 DPI |
| Inline text | 7-10 pt | 7-10 pt | - |
| Line width | 0.5-1 pt | 0.5-1 pt | - |
| Marker size | 2-4 pt | 2-4 pt | - |

#### 4.3 High-Quality Plotting Templates

**R - Volcano Plot:**
```r
#' @title SCI-grade Volcano Plot
#' @param results Differential expression results
#' @param padj Significance threshold
#' @param logfc log2FoldChange threshold
#' @param top_n Number of top genes to label
plot_volcano <- function(results, padj = 0.05, logfc = 1, top_n = 10) {

  # Add significance labels
  results <- results %>%
    mutate(
      significance = case_when(
        padj < padj & log2FoldChange > logfc ~ "Up",
        padj < padj & log2FoldChange < -logfc ~ "Down",
        TRUE ~ "NS"
      )
    )

  # Top gene labels
  top_genes <- results %>%
    filter(significance != "NS") %>%
    arrange(padj) %>%
    head(top_n) %>%
    pull(gene_id)

  ggplot(results, aes(x = log2FoldChange, y = -log10(padj))) +
    # Background points
    geom_point(aes(color = significance), alpha = 0.6, size = 1.5) +
    # Add threshold lines
    geom_hline(yintercept = -log10(padj), linetype = "dashed", color = "grey40") +
    geom_vline(xintercept = c(-logfc, logfc), linetype = "dashed", color = "grey40") +
    # Gene labels
    ggrepel::geom_text_repel(
      data = filter(results, gene_id %in% top_genes),
      aes(label = gene_id),
      size = 3,
      max.overlaps = 20
    ) +
    # SCI colors
    scale_color_manual(values = sci_palette[c("Down", "NS", "Up")]) +
    # Theme settings
    theme_classic(base_size = 10) +
    theme(
      legend.position = "top",
      legend.title = element_blank(),
      panel.border = element_rect(fill = NA, linewidth = 0.5),
      axis.title = element_text(size = 10, face = "bold"),
      axis.text = element_text(size = 9)
    ) +
    labs(x = expression(log[2]~Fold~Change),
         y = expression(-log[10]~P[adj]))
}
```

**Python - Volcano Plot:**
```python
import plotly.graph_objects as go
import plotly.express as px

def plot_volcano_interactive(results: pd.DataFrame,
                             padj: float = 0.05,
                             logfc: float = 1,
                             top_n: int = 10) -> go.Figure:
    """
    Interactive volcano plot (Plotly implementation with hover details)

    Parameters
    ----------
    results : pd.DataFrame
        Differential expression results
    padj : float
        Significance threshold
    logfc : float
        log2FC threshold
    top_n : int
        Number of top genes to label

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Classify results
    results['-log10(padj)'] = -np.log10(results['padj'])
    results['significance'] = 'NS'
    results.loc[
        (results['padj'] < padj) & (results['log2FoldChange'] > logfc),
        'significance'
    ] = 'Up'
    results.loc[
        (results['padj'] < padj) & (results['log2FoldChange'] < -logfc),
        'significance'
    ] = 'Down'

    # Color mapping
    color_map = {'Up': '#E64B35', 'Down': '#4DBBD5', 'NS': '#CCCCCC'}

    # Create figure
    fig = go.Figure()

    for sig, color in color_map.items():
        df_subset = results[results['significance'] == sig]
        fig.add_trace(go.Scatter(
            x=df_subset['log2FoldChange'],
            y=df_subset['-log10(padj)'],
            mode='markers',
            name=sig,
            marker=dict(color=color, size=6, opacity=0.7),
            text=df_subset['gene_id'],
            hovertemplate='<b>%{text}</b><br>' +
                         'log2FC: %{x:.2f}<br>' +
                         '-log10(padj): %{y:.2f}<extra></extra>'
        ))

    # Add threshold lines
    fig.add_hline(y=-np.log10(padj), line_dash="dash", line_color="gray")
    fig.add_vline(x=logfc, line_dash="dash", line_color="gray")
    fig.add_vline(x=-logfc, line_dash="dash", line_color="gray")

    fig.update_layout(
        template='plotly_white',
        font=dict(family='Arial', size=10),
        width=600, height=500,
        xaxis_title='log2 Fold Change',
        yaxis_title='-log10 (P-adj)',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    return fig
```

### 5. Code Quality Checklist

```r
# ============================================================================
# Code Quality Checklist (Automated Validation Script)
# ============================================================================

code_quality_checklist <- function(script_path) {

  checks <- list(
    # 1. Required header comments
    has_header = grepl("#' @title|#' @description", readLines(script_path, n = 20)),

    # 2. Parameter documentation completeness
    has_params = grepl("#' @param", readLines(script_path)),

    # 3. Return value documentation
    has_return = grepl("#' @return", readLines(script_path)),

    # 4. Error handling
    has_error_handling = grepl("stopifnot|tryCatch|stop\\(", readLines(script_path)),

    # 5. Package dependency declarations
    has_library_calls = grepl("^library\\(|^require\\(", readLines(script_path)),

    # 6. Required sessionInfo
    has_session = grepl("sessionInfo|packageVersion", readLines(script_path)),

    # 7. Random seed setting
    has_seed = grepl("set\\.seed|random.seed", readLines(script_path))
  )

  # Output check report
  report <- data.frame(
    Check = names(checks),
    Status = unlist(checks),
    stringsAsFactors = FALSE
  )

  return(report)
}
```

## Quick Reference: Analysis Templates

| Analysis Type | R Template | Python Template |
|--------------|------------|-----------------|
| Differential Expression | `deseq2_analysis()` | `differential_expression_analysis()` |
| Enrichment Analysis | `enrichment_analysis()` | `perform_enrichment()` |
| Heatmap | `plot_heatmap()` | `create_heatmap()` |
| PCA Visualization | `plot_pca()` | `visualize_pca()` |
| Survival Analysis | `kaplan_meier()` | `survival_analysis()` |

## Deliverable Standards

1. **Complete Code Scripts**: With comments, ready to run
2. **Test Result Figures**: PNG/SVG format, 300 DPI
3. **Sample Data Files**: CSV/TSV format
4. **Dependency Documentation**: requirements.txt or renv.lock

## Related References

- Detailed R implementation: `references/deseq2_tutorial.R`
- Python implementation example: `references/deseq2_python_implementation.py`
- SCI color schemes: `references/sci_color_palettes.R`
- Plotting template library: `references/plotting_templates/`
