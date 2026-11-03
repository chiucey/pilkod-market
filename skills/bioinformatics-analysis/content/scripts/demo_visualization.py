#!/usr/bin/env python3
"""
Bioinformatics Visualization Demo
Bioinformatics Analysis Visualization Examples
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from pathlib import Path

# Set output directory
OUTPUT_DIR = Path(__file__).parent.parent / "assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SCI Standard Color Palette
# ============================================================================

SCI_COLORS = {
    'up': '#E64B35',       # Nature Red
    'down': '#4DBBD5',     # Nature Cyan
    'ns': '#CCCCCC',       # Gray
    'primary': '#3C5488',  # Dark blue
    'secondary': '#00A087', # Green
    'accent1': '#F39B7F',  # Orange
    'accent2': '#8491B4',  # Gray-blue
}

VIRIDIS_COLORS = [
    '#440154', '#482878', '#3E4A89', '#31688E', '#26828E',
    '#1F9E89', '#35B779', '#6DCD59', '#B4DE2C', '#FDE725'
]

# ============================================================================
# 1. Volcano Plot
# ============================================================================

def create_volcano_plot(n_genes=5000, seed=42):
    """Create volcano plot example"""
    np.random.seed(seed)

    # Simulate differential expression results
    results = pd.DataFrame({
        'gene_id': [f'GENE_{i:05d}' for i in range(n_genes)],
        'log2FoldChange': np.random.normal(0, 1.5, n_genes),
        'padj': np.random.uniform(0, 1, n_genes)
    })

    # Add some significant genes
    up_genes = np.random.choice(n_genes, 150, replace=False)
    down_genes = np.random.choice([i for i in range(n_genes) if i not in up_genes], 150, replace=False)

    results.loc[up_genes, 'log2FoldChange'] = np.random.uniform(1.5, 5, 150)
    results.loc[up_genes, 'padj'] = np.random.uniform(0, 0.05, 150)

    results.loc[down_genes, 'log2FoldChange'] = np.random.uniform(-5, -1.5, 150)
    results.loc[down_genes, 'padj'] = np.random.uniform(0, 0.05, 150)

    results['-log10(padj)'] = -np.log10(results['padj'])

    # Classify significance
    results['significance'] = 'Not Significant'
    results.loc[(results['padj'] < 0.05) & (results['log2FoldChange'] > 1), 'significance'] = 'Up'
    results.loc[(results['padj'] < 0.05) & (results['log2FoldChange'] < -1), 'significance'] = 'Down'

    # Create figure
    fig = go.Figure()

    for sig, color, name in [
        ('Up', SCI_COLORS['up'], 'Up-regulated'),
        ('Down', SCI_COLORS['down'], 'Down-regulated'),
        ('Not Significant', SCI_COLORS['ns'], 'Not Significant')
    ]:
        subset = results[results['significance'] == sig]
        fig.add_trace(go.Scatter(
            x=subset['log2FoldChange'],
            y=subset['-log10(padj)'],
            mode='markers',
            name=name,
            marker=dict(color=color, size=6, opacity=0.6, line=dict(width=0.5, color='white')),
            text=subset['gene_id'],
            hovertemplate='<b>%{text}</b><br>log2FC: %{x:.2f}<br>-log10(Padj): %{y:.2f}<extra></extra>'
        ))

    # Add threshold lines
    fig.add_hline(y=-np.log10(0.05), line_dash="dash", line_color="gray", line_width=1)
    fig.add_vline(x=1, line_dash="dash", line_color="gray", line_width=1)
    fig.add_vline(x=-1, line_dash="dash", line_color="gray", line_width=1)

    # Label top genes
    top_genes = results[(results['significance'] != 'Not Significant')].nsmallest(10, 'padj')
    for _, row in top_genes.iterrows():
        fig.add_annotation(
            x=row['log2FoldChange'],
            y=row['-log10(padj)'],
            text=row['gene_id'],
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            ax=20,
            ay=-20,
            font=dict(size=8, color='black')
        )

    fig.update_layout(
        title=dict(text='<b>Volcano Plot</b><br><sup>Differential Gene Expression Analysis</sup>', x=0.5),
        width=700, height=550,
        template='plotly_white',
        font=dict(family='Arial', size=11),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor='rgba(255,255,255,0.8)'),
        xaxis_title='<b>log<sub>2</sub> Fold Change</b>',
        yaxis_title='<b>-log<sub>10</sub> (P<sub>adj</sub>)</b>',
        hovermode='closest'
    )

    return fig

# ============================================================================
# 2. Heatmap
# ============================================================================

def create_heatmap_demo(n_genes=30, n_samples=12, seed=42):
    """Create heatmap example"""
    np.random.seed(seed)

    # Generate data
    genes = [f'GENE_{i:04d}' for i in range(n_genes)]
    samples = [f'S{i}' for i in range(1, n_samples + 1)]

    # Create expression matrix
    data = np.random.randn(n_genes, n_samples)

    # Add gene expression patterns
    for i in range(n_genes // 3):
        data[i, :4] += 2  # High expression in control
        data[i, 4:] += 1
    for i in range(n_genes // 3, 2 * n_genes // 3):
        data[i, :4] -= 1
        data[i, 4:] += 2  # High expression in treatment

    # Z-score normalization
    data = (data - data.mean(axis=1, keepdims=True)) / data.std(axis=1, keepdims=True)

    # Create annotations
    annotations = []
    for i in range(n_samples):
        if i < 4:
            annotations.append('Control')
        elif i < 8:
            annotations.append('Treatment A')
        else:
            annotations.append('Treatment B')

    # Create heatmap using plotly
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=samples,
        y=genes,
        colorscale='RdBu_r',
        zmid=0,
        hovertemplate='<b>%{y}</b><br>Sample: %{x}<br>Z-score: %{z:.2f}<extra></extra>',
        colorbar=dict(title=dict(text='Z-score', side='right'))
    ))

    # Update layout
    fig.update_layout(
        title=dict(text='<b>Expression Heatmap</b><br><sup>Hierarchical Clustering of Top DEGs</sup>', x=0.5),
        width=800, height=600,
        template='plotly_white',
        font=dict(family='Arial', size=10),
        xaxis=dict(
            title='',
            tickangle=45,
            tickfont=dict(size=9)
        ),
        yaxis=dict(title='', tickfont=dict(size=8), ticksuffix=' '),
        plot_bgcolor='white'
    )

    # Add group annotations
    for i, (start, end, group, color) in enumerate([
        (0, 4, 'Control', SCI_COLORS['down']),
        (4, 8, 'Treatment A', SCI_COLORS['up']),
        (8, 12, 'Treatment B', SCI_COLORS['secondary'])
    ]):
        fig.add_shape(
            type="rect",
            x0=start - 0.5, x1=end - 0.5,
            y0=-1, y1=n_genes + 0.5,
            fillcolor=color,
            opacity=0.1,
            line=dict(width=0)
        )

    return fig

# ============================================================================
# 3. PCA Plot
# ============================================================================

def create_pca_plot(n_samples=12, n_genes=5000, seed=42):
    """Create PCA plot example"""
    np.random.seed(seed)

    # Generate simulated data
    data = np.random.randn(n_genes, n_samples)

    # Add group differences
    for i in range(n_genes):
        if i < n_genes // 3:
            data[i, 4:] += 1.5
        elif i < 2 * n_genes // 3:
            data[i, 4:] -= 1.5

    # Sample information
    groups = ['Control'] * 4 + ['Treatment'] * 4 + ['Control'] * 4
    replicates = [1, 2, 3, 4] * 3
    samples = [f'S{i}' for i in range(1, n_samples + 1)]

    # Calculate PCA
    from sklearn.decomposition import PCA
    pca = PCA(n_components=3)
    pca_result = pca.fit_transform(data.T)

    variance_explained = pca.explained_variance_ratio_ * 100

    # Create DataFrame
    pca_df = pd.DataFrame({
        'PC1': pca_result[:, 0],
        'PC2': pca_result[:, 1],
        'PC3': pca_result[:, 2],
        'Sample': samples,
        'Group': groups,
        'Replicate': replicates
    })

    # Create figure
    fig = px.scatter(
        pca_df, x='PC1', y='PC2',
        color='Group',
        symbol='Group',
        text='Sample',
        color_discrete_map={
            'Control': SCI_COLORS['down'],
            'Treatment': SCI_COLORS['up']
        },
        symbol_map={
            'Control': 'circle',
            'Treatment': 'square'
        },
        title='<b>Principal Component Analysis</b><br><sup>Sample Clustering Visualization</sup>'
    )

    fig.update_traces(
        marker=dict(size=12, line=dict(width=1, color='white')),
        textposition='top center',
        textfont=dict(size=9)
    )

    fig.update_layout(
        width=600, height=500,
        template='plotly_white',
        font=dict(family='Arial', size=11),
        legend=dict(
            yanchor="top", y=0.99,
            xanchor="right", x=0.99,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        xaxis_title=f'<b>PC1 ({variance_explained[0]:.1f}% variance)</b>',
        yaxis_title=f'<b>PC2 ({variance_explained[1]:.1f}% variance)</b>'
    )

    return fig

# ============================================================================
# 4. Enrichment Analysis Barplot
# ============================================================================

def create_enrichment_plot():
    """Create enrichment analysis barplot"""
    # Simulate KEGG enrichment results
    kegg_results = pd.DataFrame({
        'Pathway': [
            'PI3K-Akt signaling pathway',
            'MAPK signaling pathway',
            'Ras signaling pathway',
            'Apoptosis',
            'Cell cycle',
            'p53 signaling pathway',
            'NF-kB signaling pathway',
            'TNF signaling pathway',
            'Wnt signaling pathway',
            'Hedgehog signaling pathway'
        ],
        'Count': [45, 38, 35, 28, 25, 22, 20, 18, 15, 12],
        'P.adjust': [0.001, 0.003, 0.005, 0.008, 0.012, 0.018, 0.025, 0.032, 0.045, 0.058]
    })

    # Sort by p-value
    kegg_results = kegg_results.sort_values('P.adjust')

    # Color mapping
    kegg_results['Color'] = kegg_results['P.adjust'].apply(
        lambda x: VIRIDIS_COLORS[9] if x < 0.01 else
                  VIRIDIS_COLORS[6] if x < 0.02 else
                  VIRIDIS_COLORS[3] if x < 0.05 else
                  VIRIDIS_COLORS[0]
    )

    # Create barplot
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=kegg_results['Pathway'],
        x=kegg_results['Count'],
        orientation='h',
        marker_color=kegg_results['Color'],
        text=kegg_results['Count'],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Gene Count: %{x}<br>P.adjust: %{customdata:.4f}<extra></extra>',
        customdata=kegg_results['P.adjust']
    ))

    fig.update_layout(
        title=dict(text='<b>KEGG Pathway Enrichment</b><br><sup>Top 10 Enriched Pathways</sup>', x=0.5),
        width=700, height=500,
        template='plotly_white',
        font=dict(family='Arial', size=10),
        xaxis_title='<b>Gene Count</b>',
        yaxis_title='',
        yaxis=dict(autorange='reversed'),
        plot_bgcolor='white',
        margin=dict(l=200, r=20, t=80, b=40)
    )

    return fig

# ============================================================================
# 5. Boxplot Comparison
# ============================================================================

def create_boxplot_comparison():
    """Create expression level boxplot comparison"""
    np.random.seed(42)

    # Simulate data
    genes = ['GENE_00001', 'GENE_00002', 'GENE_00003']
    groups = ['Control', 'Treatment']

    data = []
    for gene in genes:
        for i, group in enumerate(groups):
            values = np.random.exponential(10, 50)
            if group == 'Treatment':
                values = values * (1.5 if gene == 'GENE_00001' else 0.8)
            for v in values:
                data.append({
                    'Gene': gene,
                    'Group': group,
                    'Expression': v
                })

    df = pd.DataFrame(data)

    fig = px.box(
        df, x='Gene', y='Expression', color='Group',
        color_discrete_map={
            'Control': SCI_COLORS['down'],
            'Treatment': SCI_COLORS['up']
        },
        title='<b>Gene Expression Comparison</b><br><sup>Control vs Treatment</sup>',
        points='all'
    )

    fig.update_layout(
        width=600, height=450,
        template='plotly_white',
        font=dict(family='Arial', size=11),
        legend=dict(
            yanchor="top", y=0.99,
            xanchor="right", x=0.99,
            bgcolor='rgba(255,255,255,0.8)'
        ),
        xaxis_title='<b>Gene</b>',
        yaxis_title='<b>Expression Level</b>'
    )

    return fig

# ============================================================================
# 6. GO Chord Diagram
# ============================================================================

def create_go_chord_demo():
    """Create GO enrichment chord diagram effect"""
    # Simulate data
    categories = ['Cellular Component', 'Molecular Function', 'Biological Process']
    genes = ['GENE_0001A', 'GENE_0002B', 'GENE_0003C', 'GENE_0004D', 'GENE_0005E']

    # Create connection data
    connections = []
    for i, gene in enumerate(genes):
        n_cats = np.random.randint(1, 3)
        cats = np.random.choice(categories, n_cats, replace=False)
        for cat in cats:
            connections.append({'Gene': gene, 'Category': cat})

    conn_df = pd.DataFrame(connections)

    # Create color mapping
    cat_colors = {
        'Cellular Component': SCI_COLORS['primary'],
        'Molecular Function': SCI_COLORS['secondary'],
        'Biological Process': SCI_COLORS['up']
    }

    gene_colors = {
        'GENE_0001A': '#E64B35',
        'GENE_0002B': '#4DBBD5',
        'GENE_0003C': '#00A087',
        'GENE_0004D': '#3C5488',
        'GENE_0005E': '#F39B7F'
    }

    # Create sankey-style connections
    fig = go.Figure()

    for cat in categories:
        cat_genes = conn_df[conn_df['Category'] == cat]['Gene'].unique()

        for gene in cat_genes:
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[categories.index(cat), list(conn_df['Gene'].unique()).index(gene)],
                mode='lines',
                line=dict(
                    color=cat_colors[cat],
                    width=3
                ),
                opacity=0.5,
                showlegend=False,
                hoverinfo='skip'
            ))

    # Add nodes
    for i, cat in enumerate(categories):
        fig.add_trace(go.Scatter(
            x=[0], y=[i],
            mode='markers+text',
            marker=dict(size=20, color=cat_colors[cat]),
            text=cat.split()[0],  # Abbreviate
            textposition='middle right',
            showlegend=False
        ))

    unique_genes = list(conn_df['Gene'].unique())
    for i, gene in enumerate(unique_genes):
        fig.add_trace(go.Scatter(
            x=[1], y=[i],
            mode='markers+text',
            marker=dict(size=15, color=gene_colors.get(gene, '#CCCCCC')),
            text=gene,
            textposition='middle left',
            showlegend=False
        ))

    fig.update_layout(
        title=dict(text='<b>GO Enrichment Connections</b><br><sup>Genes to GO Categories</sup>', x=0.5),
        width=600, height=400,
        template='plotly_white',
        showlegend=False,
        xaxis=dict(showticklabels=False, zeroline=False),
        yaxis=dict(showticklabels=False, zeroline=False)
    )

    return fig

# ============================================================================
# Main Program
# ============================================================================

def main():
    print("=" * 60)
    print("Generating bioinformatics visualization examples...")
    print("=" * 60)

    # Generate all charts
    charts = {
        'volcano_plot.html': create_volcano_plot(),
        'heatmap.html': create_heatmap_demo(),
        'pca_plot.html': create_pca_plot(),
        'enrichment_barplot.html': create_enrichment_plot(),
        'boxplot_comparison.html': create_boxplot_comparison(),
        'go_chord.html': create_go_chord_demo()
    }

    # Save charts
    for filename, fig in charts.items():
        output_path = OUTPUT_DIR / filename
        fig.write_html(output_path)
        print(f"Saved: {output_path}")

    print()
    print("=" * 60)
    print("All visualizations generated successfully!")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    main()
