"""
Publication-Quality Chart Templates for Scientific Charter Skill

This module provides ready-to-use templates for common scientific charts.
Each function creates a properly formatted, publication-ready figure.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# Default publication-quality settings
PUBLICATION_RCPARAMS = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Computer Modern Roman"],
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "axes.linewidth": 1.0,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": ":",
    "legend.fontsize": 10,
    "legend.frameon": True,
    "legend.fancybox": True,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.format": "pdf",
    "savefig.bbox": "tight"
}

def apply_publication_style():
    """Apply publication-quality styling to all subsequent plots."""
    plt.rcParams.update(PUBLICATION_RCPARAMS)

def create_line_chart(data, x_col, y_cols, output_file='line_chart.pdf',
                      title='', xlabel='', ylabel='', legend_labels=None,
                      figsize=(8, 5), colors=None, markers=None):
    """
    Create a publication-quality line chart.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Data containing x and y columns
    x_col : str
        Column name for x-axis
    y_cols : list
        List of column names for y-axis (multiple lines)
    output_file : str
        Output file path
    title, xlabel, ylabel : str
        Chart labels
    legend_labels : list
        Custom legend labels (optional)
    figsize : tuple
        Figure size (width, height) in inches
    colors : list
        Custom colors (optional)
    markers : list
        Custom markers (optional)
    """
    apply_publication_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, len(y_cols)))
    
    if markers is None:
        markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'H']
    
    for idx, y_col in enumerate(y_cols):
        label = legend_labels[idx] if legend_labels else y_col
        marker = markers[idx % len(markers)]
        color = colors[idx]
        
        ax.plot(data[x_col], data[y_col], 
                marker=marker, markersize=6, 
                linewidth=2, color=color, 
                label=label, markeredgewidth=1.5, 
                markeredgecolor='white')
    
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontweight='bold')
    
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle=':')
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    
    return output_file

def create_scatter_plot(data, x_col, y_col, output_file='scatter_plot.pdf',
                        title='', xlabel='', ylabel='', 
                        color_col=None, size_col=None, 
                        figsize=(7, 5)):
    """
    Create a publication-quality scatter plot with optional coloring and sizing.
    """
    apply_publication_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    if color_col and color_col in data.columns:
        scatter = ax.scatter(data[x_col], data[y_col], 
                           c=data[color_col], 
                           s=data[size_col]/10 if size_col else 50,
                           alpha=0.6, cmap='viridis', 
                           edgecolors='white', linewidth=0.5)
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(color_col, fontsize=10)
    else:
        ax.scatter(data[x_col], data[y_col], 
                  alpha=0.6, color='#2E86AB',
                  edgecolors='white', linewidth=0.5)
    
    # Add trend line
    z = np.polyfit(data[x_col], data[y_col], 1)
    p = np.poly1d(z)
    ax.plot(data[x_col], p(data[x_col]), 
            '--', color='red', linewidth=1.5, alpha=0.8,
            label=f'Trend: y={z[0]:.2f}x+{z[1]:.2f}')
    
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel if ylabel else y_col)
    if title:
        ax.set_title(title, fontweight='bold')
    
    ax.legend(frameon=True, fancybox=True)
    ax.grid(True, alpha=0.3, linestyle=':')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    
    return output_file

def create_bar_chart(data, cat_col, val_col, output_file='bar_chart.pdf',
                     title='', xlabel='', ylabel='', 
                     figsize=(9, 5), color='steelblue',
                     error_bars=None):
    """
    Create a publication-quality bar chart with optional error bars.
    """
    apply_publication_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    x_pos = np.arange(len(data))
    bars = ax.bar(x_pos, data[val_col], 
                   yerr=error_bars,
                   capsize=5, capthick=2,
                   color=color, alpha=0.8, 
                   edgecolor='black', linewidth=1.5)
    
    # Add value labels on top of bars
    for idx, (bar, value) in enumerate(zip(bars, data[val_col])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.1f}',
                ha='center', va='bottom', fontsize=9)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(data[cat_col], rotation=45, ha='right')
    ax.set_xlabel(xlabel if xlabel else cat_col)
    ax.set_ylabel(ylabel if ylabel else val_col)
    if title:
        ax.set_title(title, fontweight='bold')
    
    ax.grid(True, alpha=0.3, linestyle=':', axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    
    return output_file

def create_heatmap(data, output_file='heatmap.pdf',
                    title='', figsize=(8, 6),
                    cmap='RdBu_r', center=0,
                    annotate=True):
    """
    Create a publication-quality correlation heatmap.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        DataFrame with numeric columns (will compute correlation)
        or pre-computed correlation matrix
    """
    apply_publication_style()
    
    # If data is not already a correlation matrix, compute it
    if not all(data.index == data.columns):
        corr_matrix = data.corr()
    else:
        corr_matrix = data
    
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(corr_matrix.values, cmap=cmap, 
                    vmin=-1 if center == 0 else None,
                    vmax=1 if center == 0 else None,
                    aspect='auto')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Correlation', rotation=270, labelpad=20)
    
    # Set ticks and labels
    ax.set_xticks(range(len(corr_matrix.columns)))
    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
    ax.set_yticks(range(len(corr_matrix.index)))
    ax.set_yticklabels(corr_matrix.index)
    
    # Annotate with correlation values
    if annotate:
        for i in range(len(corr_matrix.index)):
            for j in range(len(corr_matrix.columns)):
                text = ax.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                               ha='center', va='center', 
                               color='white' if abs(corr_matrix.iloc[i, j]) > 0.5 else 'black',
                               fontsize=9)
    
    if title:
        ax.set_title(title, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    
    return output_file

def create_box_plot(data, group_col, val_col, output_file='box_plot.pdf',
                    title='', xlabel='', ylabel='', 
                    figsize=(9, 5)):
    """
    Create a publication-quality box plot.
    """
    apply_publication_style()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    bp = ax.boxplot([data[data[group_col] == group][val_col] 
                     for group in data[group_col].unique()],
                    labels=data[group_col].unique().tolist(),
                    patch_artist=True, showmeans=True)
    
    # Customize box colors
    colors = plt.cm.Set3(np.linspace(0, 1, len(bp['boxes'])))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    # Style median lines
    for median in bp['medians']:
        median.set_color('red')
        median.set_linewidth(2)
    
    ax.set_xlabel(xlabel if xlabel else group_col)
    ax.set_ylabel(ylabel if ylabel else val_col)
    if title:
        ax.set_title(title, fontweight='bold')
    
    ax.grid(True, alpha=0.3, linestyle=':', axis='y')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    
    return output_file

def create_multi_panel_figure(data_dict, output_file='multi_panel.pdf',
                              figsize=(12, 8), 
                              panel_labels=['(A)', '(B)', '(C)', '(D)']):
    """
    Create a multi-panel figure with 2x2 subplots.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary with keys 'ax1', 'ax2', 'ax3', 'ax4' containing
        tuples of (plot_type, data, kwargs)
    """
    apply_publication_style()
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()
    
    for idx, (ax_key, ax) in enumerate(zip(['ax1', 'ax2', 'ax3', 'ax4'], axes)):
        if ax_key in data_dict:
            plot_type, plot_data, kwargs = data_dict[ax_key]
            
            if plot_type == 'line':
                for y_col in kwargs.get('y_cols', [plot_data.columns[1]]):
                    ax.plot(plot_data[plot_data.columns[0]], plot_data[y_col],
                           label=y_col, linewidth=2)
                ax.legend()
            
            elif plot_type == 'scatter':
                ax.scatter(plot_data[plot_data.columns[0]], 
                          plot_data[plot_data.columns[1]],
                          alpha=0.6)
            
            elif plot_type == 'bar':
                x_pos = np.arange(len(plot_data))
                ax.bar(x_pos, plot_data[plot_data.columns[1]],
                      alpha=0.8, edgecolor='black')
                ax.set_xticks(x_pos)
                ax.set_xticklabels(plot_data[plot_data.columns[0]], 
                                   rotation=45, ha='right')
            
            elif plot_type == 'hist':
                ax.hist(plot_data[plot_data.columns[0]], 
                        bins=30, edgecolor='black', alpha=0.7)
            
            # Add panel label
            ax.text(0.02, 0.98, panel_labels[idx],
                   transform=ax.transAxes, 
                   fontsize=12, fontweight='bold',
                   va='top', ha='left')
            
            ax.grid(True, alpha=0.3, linestyle=':')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            if 'title' in kwargs:
                ax.set_title(kwargs['title'])
    
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    
    return output_file

def create_3d_scatter(data, x_col, y_col, z_col, 
                      output_file='3d_scatter.pdf',
                      title='', figsize=(10, 8),
                      color_col=None):
    """
    Create a 3D scatter plot.
    """
    apply_publication_style()
    
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    if color_col and color_col in data.columns:
        scatter = ax.scatter(data[x_col], data[y_col], data[z_col],
                           c=data[color_col], cmap='viridis',
                           s=50, alpha=0.6)
        fig.colorbar(scatter, ax=ax, label=color_col)
    else:
        ax.scatter(data[x_col], data[y_col], data[z_col],
                  c='steelblue', s=50, alpha=0.6)
    
    ax.set_xlabel(xlabel if 'xlabel' in dir() else x_col)
    ax.set_ylabel(ylabel if 'ylabel' in dir() else y_col)
    ax.set_zlabel(zlabel if 'zlabel' in dir() else z_col)
    
    if title:
        ax.set_title(title, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    
    return output_file

# Example usage and testing
if __name__ == '__main__':
    # Generate sample data
    np.random.seed(42)
    n_samples = 100
    
    sample_data = pd.DataFrame({
        'Time': np.linspace(0, 10, n_samples),
        'Temperature': np.sin(np.linspace(0, 10, n_samples)) + np.random.randn(n_samples) * 0.1,
        'Pressure': np.cos(np.linspace(0, 10, n_samples)) + np.random.randn(n_samples) * 0.1,
        'Category': np.random.choice(['A', 'B', 'C', 'D'], n_samples),
        'Value': np.random.randn(n_samples) * 10 + 50
    })
    
    # Create sample bar chart data
    bar_data = pd.DataFrame({
        'Category': ['Control', 'Treatment A', 'Treatment B', 'Treatment C'],
        'Mean': [20, 35, 30, 25],
        'SEM': [2, 3, 2.5, 2]
    })
    
    # Test each chart type
    print("Creating sample charts...")
    
    create_line_chart(sample_data, 'Time', ['Temperature', 'Pressure'],
                     output_file='example_line_chart.pdf',
                     title='Temperature and Pressure over Time',
                     xlabel='Time (s)', ylabel='Value')
    print("  ✓ Line chart created")
    
    create_scatter_plot(sample_data, 'Temperature', 'Pressure',
                      output_file='example_scatter_plot.pdf',
                      title='Temperature vs Pressure')
    print("  ✓ Scatter plot created")
    
    create_bar_chart(bar_data, 'Category', 'Mean',
                     output_file='example_bar_chart.pdf',
                     title='Treatment Effects',
                     error_bars=bar_data['SEM'])
    print("  ✓ Bar chart created")
    
    # Create correlation heatmap
    corr_data = sample_data[['Temperature', 'Pressure', 'Value']].copy()
    create_heatmap(corr_data, output_file='example_heatmap.pdf',
                   title='Correlation Matrix')
    print("  ✓ Heatmap created")
    
    print("\nAll example charts created successfully!")
