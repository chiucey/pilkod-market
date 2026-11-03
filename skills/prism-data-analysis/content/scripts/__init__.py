"""
Prism Data Analysis Scripts
============================
GraphPad Prism automation and template generation tools.

Exports:
    - PrismDetector: Detect local Prism installations
    - PrismConnection: COM connection to Prism
    - DataAnalyzer: Pure Python data analysis (no Prism required)
    - PrismTemplate: Generate .pzfx project templates
    - generate_template: Factory function for templates
"""

from .prism_automation import (
    PrismDetector,
    PrismConnection,
    DataAnalyzer,
    PrismVersion,
    IC50Result,
    StandardCurveResult,
    detect_prism,
    analyze_ic50_from_excel,
    batch_ttest_from_excel,
)

from .pzfx_generator import (
    PrismTemplate,
    generate_template,
    create_ic50_template,
    create_standard_curve_template,
    create_anova_template,
    create_ttest_template,
)

__version__ = "1.0.0"
__all__ = [
    # Detection
    "PrismDetector",
    "PrismConnection",
    "PrismVersion",
    "detect_prism",
    # Analysis
    "DataAnalyzer",
    "IC50Result",
    "StandardCurveResult",
    "analyze_ic50_from_excel",
    "batch_ttest_from_excel",
    # Templates
    "PrismTemplate",
    "generate_template",
    "create_ic50_template",
    "create_standard_curve_template",
    "create_anova_template",
    "create_ttest_template",
]
