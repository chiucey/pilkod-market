"""
DESeq2差异表达分析 Python实现
Python Implementation of DESeq2 Differential Expression Analysis
===============================================================================
作者：Bioinformatics Analysis Pipeline
版本：1.0.0
依赖：rpy2, pandas, numpy, plotly
===============================================================================

本模块提供DESeq2的Python封装，支持通过rpy2调用R的DESeq2包，
同时提供纯Python风格的接口。
"""

from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# 数据类定义
# ============================================================================

@dataclass
class AnalysisConfig:
    """分析配置参数"""
    padj_threshold: float = 0.05
    logfc_threshold: float = 1.0
    lfc_shrinkage: bool = True
    filter_min_count: int = 10
    filter_min_samples: int = 3
    species: str = "human"
    test_method: str = "Wald"  # "Wald" or "LRT"


@dataclass
class Comparison:
    """比较组定义"""
    condition_column: str
    treatment: str
    control: str

    def to_r_contrast(self) -> List:
        """转换为R的contrast格式"""
        return [self.condition_column, self.treatment, self.control]


# ============================================================================
# 核心分析类
# ============================================================================

class Deseq2Analysis:
    """
    DESeq2差异表达分析主类

    提供完整的差异表达分析流程，包括数据预处理、差异分析、
    结果可视化和报告生成。

    Example
    -------
    >>> config = AnalysisConfig(padj_threshold=0.05, logfc_threshold=1.0)
    >>> comparison = Comparison("condition", "treatment", "control")
    >>> analyzer = Deseq2Analysis(config)
    >>> results = analyzer.run(count_matrix, sample_info, comparison)
    """

    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        初始化分析器

        Parameters
        ----------
        config : AnalysisConfig, optional
            分析配置参数
        """
        self.config = config or AnalysisConfig()
        self._r_environment = None
        self.results_ = None
        self.dds_ = None

    def _init_r_environment(self) -> None:
        """初始化R环境"""
        try:
            import rpy2.robjects as ro
            from rpy2.robjects import pandas2ri
            from rpy2.robjects.packages import importr

            # 激活自动转换
            pandas2ri.activate()

            # 导入DESeq2
            self._deseq2 = importr('DESeq2')
            self._apeglm = importr('apeglm')

            # 设置随机种子
            ro.r('set.seed(42)')

            self._r_environment = True
            logger.info("R environment initialized successfully")

        except ImportError as e:
            logger.error(f"Failed to import rpy2: {e}")
            raise ImportError(
                "Please install rpy2: pip install rpy2"
            )

    def _validate_data(
        self,
        count_matrix: pd.DataFrame,
        sample_info: pd.DataFrame
    ) -> None:
        """
        验证输入数据

        Parameters
        ----------
        count_matrix : pd.DataFrame
            计数矩阵 (基因 × 样本)
        sample_info : pd.DataFrame
            样本信息 (样本 × 特征)

        Raises
        ------
        ValueError
            数据格式不正确时抛出
        """
        # 检查样本匹配
        common_samples = set(count_matrix.columns) & set(sample_info.index)
        if len(common_samples) == 0:
            raise ValueError(
                "No matching samples between count_matrix and sample_info"
            )

        # 检查计数矩阵是否为非负整数
        if (count_matrix < 0).any().any():
            raise ValueError("Count matrix contains negative values")

        logger.info(f"Validated {len(common_samples)} common samples")

    def _preprocess_counts(
        self,
        count_matrix: pd.DataFrame,
        min_count: int,
        min_samples: int
    ) -> pd.DataFrame:
        """
        预处理计数矩阵 - 过滤低表达基因

        Parameters
        ----------
        count_matrix : pd.DataFrame
            原始计数矩阵
        min_count : int
            最小表达阈值
        min_samples : int
            最小检出样本数

        Returns
        -------
        pd.DataFrame
            过滤后的计数矩阵
        """
        # 计算每个基因在多少样本中表达
        detection_rate = (count_matrix >= min_count).sum(axis=1)

        # 过滤
        keep_genes = detection_rate >= min_samples
        filtered = count_matrix.loc[keep_genes]

        logger.info(
            f"Filtered from {len(count_matrix)} to {len(filtered)} genes "
            f"(min_count={min_count}, min_samples={min_samples})"
        )

        return filtered

    def _to_r_dataframe(self, df: pd.DataFrame) -> 'pandas2ri.PandasDataFrame':
        """将pandas DataFrame转换为R DataFrame"""
        from rpy2.robjects import pandas2ri
        return pandas2ri.py2rpy(df)

    def run(
        self,
        count_matrix: pd.DataFrame,
        sample_info: pd.DataFrame,
        comparison: Comparison,
        gene_annotation: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        运行差异表达分析

        Parameters
        ----------
        count_matrix : pd.DataFrame
            计数矩阵 (基因 × 样本)
        sample_info : pd.DataFrame
            样本信息 (样本 × 临床特征)
        comparison : Comparison
            比较组定义
        gene_annotation : pd.DataFrame, optional
            基因注释表

        Returns
        -------
        pd.DataFrame
            差异分析结果表
        """
        # 初始化R环境
        if self._r_environment is None:
            self._init_r_environment()

        # 数据验证
        self._validate_data(count_matrix, sample_info)

        # 预处理
        count_matrix = count_matrix[sample_info.index]
        count_matrix = self._preprocess_counts(
            count_matrix,
            self.config.filter_min_count,
            self.config.filter_min_samples
        )

        import rpy2.robjects as ro
        from rpy2.robjects import pandas2ri

        # 转换数据
        r_counts = pandas2ri.py2rpy(count_matrix)
        r_sample_info = pandas2ri.py2rpy(sample_info)

        # 设置design formula
        design_formula = f"~ {comparison.condition_column}"

        # 创建DESeq2数据集
        logger.info("Creating DESeq2 dataset...")
        dds = self._deseq2.DESeqDataSetFromMatrix(
            countData=r_counts,
            colData=r_sample_info,
            design=ro.Formula(design_formula)
        )

        # 设置参考组
        ro.globalenv['dds'] = dds
        ref_level = comparison.control
        ro.r(f'colData(dds)${comparison.condition_column} <- '
             f'factor(colData(dds)${comparison.condition_column})')
        ro.r(f'colData(dds)${comparison.condition_column} <- '
             f'relevel(colData(dds)${comparison.condition_column}, ref="{ref_level}")')

        # 运行分析
        logger.info("Running DESeq2 analysis...")
        ro.r('dds <- DESeq(dds, test="Wald")')

        # 提取结果
        contrast_str = f'"{comparison.condition_column}", "{comparison.treatment}", "{comparison.control}"'
        res = ro.r(f'results(dds, contrast=c({contrast_str}), alpha={self.config.padj_threshold})')

        # 转换为pandas DataFrame
        results_df = pandas2ri.rpy2py(res)

        # LFC收缩（可选）
        if self.config.lfc_shrinkage:
            try:
                logger.info("Applying LFC shrinkage (apeglm)...")
                coef = f"{comparison.condition_column}_{comparison.treatment}_vs_{comparison.control}"
                ro.r(f'''
                    resLFC <- lfcShrink(dds, coef="{coef}", type="apeglm")
                ''')
                res_lfc = ro.r('resLFC')
                lfc_df = pandas2ri.rpy2py(res_lfc)
                results_df['log2FoldChange_shrunken'] = lfc_df['log2FoldChange']
            except Exception as e:
                logger.warning(f"LFC shrinkage failed: {e}")

        # 添加基因注释
        if gene_annotation is not None:
            results_df = results_df.merge(
                gene_annotation,
                left_index=True,
                right_index=True,
                how='left'
            )

        # 分类差异基因
        results_df = self._classify_genes(results_df)

        self.results_ = results_df
        self.dds_ = dds

        return results_df

    def _classify_genes(self, results: pd.DataFrame) -> pd.DataFrame:
        """分类差异基因"""
        results['significance'] = 'Not Significant'

        up_mask = (
            (results['padj'] < self.config.padj_threshold) &
            (results['log2FoldChange'] > self.config.logfc_threshold)
        )
        down_mask = (
            (results['padj'] < self.config.padj_threshold) &
            (results['log2FoldChange'] < -self.config.logfc_threshold)
        )

        results.loc[up_mask, 'significance'] = 'Up'
        results.loc[down_mask, 'significance'] = 'Down'

        return results

    def get_deg_summary(self) -> Dict:
        """获取差异基因统计"""
        if self.results_ is None:
            raise ValueError("Run analysis first")

        summary = self.results_['significance'].value_counts()
        return summary.to_dict()

    def export_results(self, output_dir: Union[str, Path]) -> None:
        """导出结果"""
        if self.results_ is None:
            raise ValueError("Run analysis first")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 全量结果
        self.results_.to_csv(
            output_dir / 'differential_expression_results.tsv',
            sep='\t'
        )

        # 上调基因
        up_genes = self.results_[
            self.results_['significance'] == 'Up'
        ].sort_values('padj')
        up_genes.to_csv(
            output_dir / 'upregulated_genes.tsv',
            sep='\t'
        )

        # 下调基因
        down_genes = self.results_[
            self.results_['significance'] == 'Down'
        ].sort_values('padj')
        down_genes.to_csv(
            output_dir / 'downregulated_genes.tsv',
            sep='\t'
        )

        logger.info(f"Results exported to {output_dir}")


# ============================================================================
# 可视化模块
# ============================================================================

class Deseq2Visualizer:
    """DESeq2结果可视化类"""

    # SCI标准配色
    COLORS = {
        'up': '#E64B35',      # 红色
        'down': '#4DBBD5',   # 青色
        'ns': '#CCCCCC',      # 灰色
        'primary': '#3C5488',  # 深蓝
        'secondary': '#00A087', # 绿色
    }

    def __init__(self, results: pd.DataFrame):
        """
        初始化可视化器

        Parameters
        ----------
        results : pd.DataFrame
            差异分析结果
        """
        self.results = results

    def plot_volcano(
        self,
        padj_threshold: float = 0.05,
        logfc_threshold: float = 1,
        top_n: int = 10,
        width: int = 600,
        height: int = 500
    ) -> go.Figure:
        """
        绘制交互式火山图

        Parameters
        ----------
        padj_threshold : float
            显著性阈值
        logfc_threshold : float
            log2FC阈值
        top_n : int
            标注Top基因数
        width : int
            图形宽度
        height : int
            图形高度

        Returns
        -------
        go.Figure
            Plotly图形对象
        """
        df = self.results.copy()

        # 计算-log10(padj)
        df['-log10(padj)'] = -np.log10(df['padj'])

        # 创建悬停文本
        df['hover_text'] = (
            '<b>' + df.index + '</b><br>' +
            'log2FC: ' + df['log2FoldChange'].round(2).astype(str) + '<br>' +
            'P.adj: ' + df['padj'].apply(lambda x: f'{x:.2e}' if x < 0.001 else f'{x:.4f}') +
            '<br>Status: ' + df['significance']
        )

        # 创建图形
        fig = make_subplots(
            rows=1, cols=1,
            subplot_titles=('',)
        )

        # 添加散点
        for sig, color, name in [
            ('Up', self.COLORS['up'], 'Up-regulated'),
            ('Down', self.COLORS['down'], 'Down-regulated'),
            ('Not Significant', self.COLORS['ns'], 'Not Significant')
        ]:
            subset = df[df['significance'] == sig]
            fig.add_trace(
                go.Scatter(
                    x=subset['log2FoldChange'],
                    y=subset['-log10(padj)'],
                    mode='markers',
                    name=name,
                    marker=dict(
                        color=color,
                        size=6,
                        opacity=0.6,
                        line=dict(width=0.5, color='white')
                    ),
                    text=subset['hover_text'],
                    hovertemplate='%{text}<extra></extra>'
                ),
                row=1, col=1
            )

        # 添加阈值线
        fig.add_hline(
            y=-np.log10(padj_threshold),
            line_dash="dash",
            line_color="gray",
            line_width=1,
            row=1, col=1
        )
        fig.add_vline(
            x=logfc_threshold,
            line_dash="dash",
            line_color="gray",
            line_width=1,
            row=1, col=1
        )
        fig.add_vline(
            x=-logfc_threshold,
            line_dash="dash",
            line_color="gray",
            line_width=1,
            row=1, col=1
        )

        # 布局设置
        fig.update_layout(
            width=width,
            height=height,
            template='plotly_white',
            font=dict(family='Arial', size=11),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255,255,255,0.8)'
            ),
            xaxis_title='log<sub>2</sub> Fold Change',
            yaxis_title='-log<sub>10</sub> (P<sub>adj</sub>)',
            hovermode='closest'
        )

        return fig

    def plot_heatmap(
        self,
        count_matrix: pd.DataFrame,
        top_n: int = 50,
        width: int = 700,
        height: int = 600
    ) -> go.Figure:
        """
        绘制热图

        Parameters
        ----------
        count_matrix : pd.DataFrame
            标准化后的表达矩阵
        top_n : int
            显示Top基因数

        Returns
        -------
        go.Figure
            热图
        """
        # 获取Top差异基因
        top_genes = self.results[
            self.results['significance'] != 'Not Significant'
        ].nsmallest(top_n, 'padj').index

        # 提取子矩阵
        mat = count_matrix.loc[count_matrix.index.isin(top_genes)]

        # Z-score标准化
        mat = mat.subtract(mat.mean(axis=1), axis=0)
        mat = mat.divide(mat.std(axis=1), axis=0)

        # 创建热图
        fig = go.Figure(data=go.Heatmap(
            z=mat.values,
            x=mat.columns,
            y=mat.index,
            colorscale='RdBu_r',
            zmid=0,
            hovertemplate='Gene: %{y}<br>Sample: %{x}<br>Z-score: %{z:.2f}<extra></extra>'
        ))

        fig.update_layout(
            width=width,
            height=height,
            template='plotly_white',
            font=dict(family='Arial', size=10),
            xaxis_title='Sample',
            yaxis_title='Gene',
            yaxis_nticks=20
        )

        return fig

    def plot_ma(self, padj_threshold: float = 0.05) -> go.Figure:
        """
        绘制MA图

        Parameters
        ----------
        padj_threshold : float
            显著性阈值

        Returns
        -------
        go.Figure
            MA图
        """
        df = self.results.copy()
        df['significant'] = df['padj'] < padj_threshold

        fig = go.Figure()

        # 添加散点
        for sig, color, name in [
            (True, self.COLORS['up'], f'Significant (P.adj < {padj_threshold})'),
            (False, self.COLORS['ns'], 'Not Significant')
        ]:
            subset = df[df['significant'] == sig]
            fig.add_trace(
                go.Scatter(
                    x=subset['baseMean'],
                    y=subset['log2FoldChange'],
                    mode='markers',
                    name=name,
                    marker=dict(
                        color=color,
                        size=5,
                        opacity=0.5
                    )
                )
            )

        # 添加零线
        fig.add_hline(
            y=0,
            line_dash="solid",
            line_color="gray",
            line_width=1
        )

        fig.update_layout(
            width=600,
            height=450,
            template='plotly_white',
            font=dict(family='Arial', size=11),
            xaxis_title='Mean Expression',
            yaxis_title='log<sub>2</sub> Fold Change',
            xaxis_type='log',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )

        return fig

    def save_figure(
        self,
        fig: go.Figure,
        filename: str,
        format: str = 'png',
        scale: int = 2
    ) -> None:
        """
        保存图形

        Parameters
        ----------
        fig : go.Figure
            Plotly图形对象
        filename : str
            输出文件名
        format : str
            输出格式 ('png', 'svg', 'pdf', 'html')
        scale : int
            分辨率缩放因子
        """
        if format == 'html':
            fig.write_html(filename)
        else:
            fig.write_image(filename, format=format, scale=scale)
        logger.info(f"Figure saved to {filename}")


# ============================================================================
# 便捷函数
# ============================================================================

def differential_expression_analysis(
    count_matrix: pd.DataFrame,
    sample_info: pd.DataFrame,
    comparison: Tuple[str, str, str],
    config: Optional[AnalysisConfig] = None,
    gene_annotation: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    差异表达分析便捷函数

    Parameters
    ----------
    count_matrix : pd.DataFrame
        计数矩阵 (基因 × 样本)
    sample_info : pd.DataFrame
        样本信息 (样本 × 特征)
    comparison : Tuple[str, str, str]
        比较组 (条件列, 处理组, 对照组)
    config : AnalysisConfig, optional
        分析配置
    gene_annotation : pd.DataFrame, optional
        基因注释

    Returns
    -------
    pd.DataFrame
        差异分析结果

    Example
    -------
    >>> from sklearn.datasets import make_simulation
    >>> results = differential_expression_analysis(
    ...     count_matrix,
    ...     sample_info,
    ...     comparison=('condition', 'treatment', 'control')
    ... )
    """
    comp = Comparison(*comparison)
    analyzer = Deseq2Analysis(config)
    return analyzer.run(count_matrix, sample_info, comp, gene_annotation)


# ============================================================================
# 示例数据生成
# ============================================================================

def generate_demo_data(
    n_genes: int = 10000,
    n_samples: int = 6,
    n_degs: int = 200,
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    生成演示用模拟数据

    Parameters
    ----------
    n_genes : int
        基因数量
    n_samples : int
        样本数量
    n_degs : int
        差异基因数量
    seed : int
        随机种子

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (count_matrix, sample_info)
    """
    np.random.seed(seed)

    # 生成计数矩阵
    count_matrix = pd.DataFrame(
        np.random.negative_binomial(10, 0.5, (n_genes, n_samples)),
        index=[f'GENE_{i:05d}' for i in range(n_genes)],
        columns=[f'Sample_{i+1}' for i in range(n_samples)]
    )

    # 添加差异基因
    deg_indices = np.random.choice(n_genes, n_degs, replace=False)
    for idx in deg_indices:
        fold_change = np.random.choice([2, 3, 4, 0.5, 0.33, 0.25])
        count_matrix.iloc[idx, :3] = (count_matrix.iloc[idx, :3] * fold_change).astype(int)

    # 生成样本信息
    sample_info = pd.DataFrame({
        'sample': count_matrix.columns,
        'condition': ['control'] * 3 + ['treatment'] * 3,
        'replicate': [1, 2, 3, 1, 2, 3]
    }, index=count_matrix.columns)

    return count_matrix, sample_info


# ============================================================================
# 主程序入口
# ============================================================================

if __name__ == '__main__':
    # 生成演示数据
    print("Generating demo data...")
    counts, samples = generate_demo_data()

    print(f"Count matrix shape: {counts.shape}")
    print(f"Sample info shape: {samples.shape}")

    # 运行分析
    try:
        results = differential_expression_analysis(
            counts,
            samples,
            comparison=('condition', 'treatment', 'control')
        )

        print("\n=== Analysis Results ===")
        print(results.groupby('significance').size())

        # 可视化
        viz = Deseq2Visualizer(results)
        fig = viz.plot_volcano()
        fig.show()

    except ImportError as e:
        print(f"Note: {e}")
        print("rpy2 is required for full analysis. Install with: pip install rpy2")
