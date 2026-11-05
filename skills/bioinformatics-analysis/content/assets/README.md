# Bioinformatics Visualization Gallery

This directory contains bioinformatics analysis visualization examples based on SCI standard color schemes.

## Example Charts

| Chart Type | Filename | Description |
|------------|----------|-------------|
| Volcano Plot | `volcano_plot.html` | Differential expression results visualization |
| Heatmap | `heatmap.html` | Gene expression clustering heatmap |
| PCA Plot | `pca_plot.html` | Principal component analysis scatter plot |
| Enrichment Barplot | `enrichment_barplot.html` | KEGG/GO pathway enrichment analysis |
| Boxplot | `boxplot_comparison.html` | Gene expression comparison |
| GO Chord | `go_chord.html` | GO enrichment connections |

## Color Schemes

### Nature Standard (Primary Palette)
- Up-regulated: `#E64B35` (Red)
- Down-regulated: `#4DBBD5` (Cyan)
- Not Significant: `#CCCCCC` (Gray)

### Viridis Continuous Variable
- Range: `#440154` → `#21918C` → `#FDE725`
- Features: Colorblind-friendly, print-friendly

## Usage

All charts are interactive HTML format, can be opened in browser:
- Hover for detailed information
- Zoom and pan
- Export to PNG/SVG/PDF

## Generation Code

See `scripts/demo_visualization.py` for complete Python code.
