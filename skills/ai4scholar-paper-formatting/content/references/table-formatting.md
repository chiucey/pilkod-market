# Three-Line Table Format Standards

## Three-Line Table Basic Rules

The three-line table (Three-line Table) is a commonly used format in academic papers with these characteristics:

1. **Only three horizontal lines**: top line, header line, bottom line
2. **No vertical lines**: avoid vertical borders
3. **No internal horizontal lines**: no horizontal dividers below headers
4. **Number alignment**: align numbers by decimal points

## LaTeX booktabs Syntax

```latex
\usepackage{booktabs}  % Requires booktabs package

\begin{table}[h]
\centering
\caption{Table X. Your table title in English}
\label{tab:example}
\begin{tabular}{lcc}
\toprule
\textbf{Column 1} & \textbf{Column 2} & \textbf{Column 3} \\
\midrule
Row 1 & Data & Data \\
Row 2 & Data & Data \\
\bottomrule
\end{tabular}
\begin{tablenotes}
  \item Note. Explanation of the table data.
\end{tablenotes}
\end{table}
```

## Statistical Significance Notation Rules

| Symbol | Meaning |
|-----|------|
| *   | p < 0.05 |
| **  | p < 0.01 |
| *** | p < 0.001 |

## Number Format Standards

- **Percentages**: one decimal place (e.g., 95.8%)
- **Mean ± Standard Deviation**: two decimal places (e.g., 85.23 ± 3.45)
- **Large numbers**: use thousands separators or scientific notation

## Example: Model Performance Comparison Table

**LaTeX Output**:
```latex
\begin{table}[h]
\centering
\caption{Table 1. F1 scores of three models on benchmark datasets}
\begin{tabular}{lcc}
\toprule
\textbf{Model} & \textbf{IMDB} & \textbf{SST-2} \\
\midrule
BERT           & 92.3\%        & 89.7\%         \\
RoBERTa        & 94.1\%        & 91.2\%         \\
GPT-4          & \textbf{95.8\%}** & \textbf{93.4\%}** \\
\bottomrule
\end{tabular}
\begin{tablenotes}
  \item Note. ** $p < 0.01$ compared to BERT baseline.
\end{tablenotes}
\end{table}
```

## Creating Three-Line Tables in Word

1. Insert table
2. Select entire table
3. Format → Borders and Shading
4. Settings: keep only top line, bottom line, and header underline
5. Remove internal borders and vertical lines
