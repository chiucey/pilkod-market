"""
GraphPad Prism Template Generator
=================================
Generate .pzfx format Prism project files.

Features:
    - IC50 templates
    - Standard curve templates (ELISA, qPCR)
    - t-test templates
    - ANOVA templates
    - Survival analysis templates

Version: 1.0.0
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class PrismTemplate:
    """Prism project template."""
    title: str
    analysis_type: str
    data_columns: int
    replicates: int
    groups: int
    x_values: bool = True

    def save(self, filepath: str):
        """
        Save template as .pzfx file.

        Args:
            filepath: Output file path
        """
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zf:
            # info.plist
            info_plist = self._generate_info_plist()
            zf.writestr('info.plist', info_plist)

            # Prisms.mpd (main data file)
            prisms_mpd = self._generate_prisms_mpd()
            zf.writestr('Prisms.mpd', prisms_mpd)

        print(f"[Success] Template saved: {filepath}")

    def _generate_info_plist(self) -> str:
        """Generate info.plist content."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{self.title}</string>
    <key>AnalysisType</key>
    <string>{self.analysis_type}</string>
</dict>
</plist>'''

    def _generate_prisms_mpd(self) -> str:
        """Generate Prisms.mpd XML content."""
        root = ET.Element("PrismsData", version="10.0")

        # Table info
        table_info = ET.SubElement(root, "TableInfo")
        ET.SubElement(table_info, "Title").text = self.title
        ET.SubElement(table_info, "AnalysisType").text = self.analysis_type
        ET.SubElement(table_info, "DataColumns").text = str(self.data_columns)
        ET.SubElement(table_info, "Replicates").text = str(self.replicates)
        ET.SubElement(table_info, "Groups").text = str(self.groups)

        # Data table
        data_table = ET.SubElement(root, "DataTable", id="0", name="Data 1")

        # Add format based on analysis type
        format_map = {
            "ic50": self._add_ic50_data_format,
            "standard_curve": self._add_standard_curve_format,
            "paired_ttest": self._add_ttest_format,
            "two_group_ttest": self._add_ttest_format,
            "one_way_anova": self._add_anova_format,
            "survival": self._add_survival_format,
        }

        formatter = format_map.get(self.analysis_type, self._add_generic_format)
        formatter(data_table)

        return ET.tostring(root, encoding='unicode', method='xml')

    def _add_ic50_data_format(self, data_table):
        """Add IC50 data format."""
        headers = ET.SubElement(data_table, "Headers")
        ET.SubElement(headers, "Column", type="x", label="Concentration")
        for i in range(self.replicates):
            ET.SubElement(headers, "Column", type="y", label=f"Replicate {i+1}")

        x_values = [0.001, 0.01, 0.1, 1, 10, 100]
        x_row = ET.SubElement(data_table, "Row", row="0")
        for xv in x_values[:self.data_columns]:
            ET.SubElement(x_row, "X").text = str(xv)

        for row_idx in range(self.replicates):
            y_row = ET.SubElement(data_table, "Row", row=str(row_idx + 1))
            for _ in range(self.data_columns):
                ET.SubElement(y_row, "Y").text = ""

    def _add_standard_curve_format(self, data_table):
        """Add standard curve data format."""
        headers = ET.SubElement(data_table, "Headers")
        ET.SubElement(headers, "Column", type="x", label="Concentration (X)")
        for i in range(self.replicates):
            ET.SubElement(headers, "Column", type="y", label=f"Replicate {i+1}")

        concentrations = ["0", "3.125", "6.25", "12.5", "25", "50", "100"]
        for i, conc in enumerate(concentrations[:self.data_columns]):
            row = ET.SubElement(data_table, "Row", row=str(i))
            ET.SubElement(row, "X").text = conc
            for _ in range(self.replicates):
                ET.SubElement(row, "Y").text = ""

    def _add_ttest_format(self, data_table):
        """Add t-test data format."""
        headers = ET.SubElement(data_table, "Headers")
        ET.SubElement(headers, "Column", type="entry", label="Pair/Entry")
        ET.SubElement(headers, "Column", type="y", label="Group A")
        ET.SubElement(headers, "Column", type="y", label="Group B")

        for i in range(self.data_columns):
            row = ET.SubElement(data_table, "Row", row=str(i))
            ET.SubElement(row, "X").text = f"Entry {i+1}"
            ET.SubElement(row, "Y").text = ""
            ET.SubElement(row, "Y").text = ""

    def _add_anova_format(self, data_table):
        """Add ANOVA data format."""
        headers = ET.SubElement(data_table, "Headers")
        ET.SubElement(headers, "Column", type="entry", label="Subject")
        for g in range(self.groups):
            ET.SubElement(headers, "Column", type="y", label=f"Group {chr(65+g)}")

        for i in range(self.data_columns):
            row = ET.SubElement(data_table, "Row", row=str(i))
            ET.SubElement(row, "X").text = f"Subject {i+1}"
            for _ in range(self.groups):
                ET.SubElement(row, "Y").text = ""

    def _add_survival_format(self, data_table):
        """Add survival analysis data format."""
        headers = ET.SubElement(data_table, "Headers")
        ET.SubElement(headers, "Column", type="entry", label="Subject")
        ET.SubElement(headers, "Column", type="x", label="Time")
        ET.SubElement(headers, "Column", type="y", label="Event (1=death, 0=censor)")
        ET.SubElement(headers, "Column", type="group", label="Group")

        for i in range(self.data_columns):
            row = ET.SubElement(data_table, "Row", row=str(i))
            ET.SubElement(row, "X").text = f"Subject {i+1}"
            ET.SubElement(row, "Y").text = ""
            ET.SubElement(row, "Y").text = ""
            ET.SubElement(row, "Y").text = ""

    def _add_generic_format(self, data_table):
        """Add generic two-column format."""
        headers = ET.SubElement(data_table, "Headers")
        ET.SubElement(headers, "Column", type="x", label="X")
        ET.SubElement(headers, "Column", type="y", label="Y")
        for i in range(self.data_columns):
            row = ET.SubElement(data_table, "Row", row=str(i))
            ET.SubElement(row, "X").text = str(i + 1)
            ET.SubElement(row, "Y").text = ""


# Factory functions
def generate_template(analysis_type: str,
                     data_columns: int = 6,
                     replicates: int = 4,
                     groups: int = 2,
                     title: str = "Prism Template") -> PrismTemplate:
    """
    Generate a Prism template.

    Args:
        analysis_type: One of: ic50, standard_curve, paired_ttest,
                      two_group_ttest, one_way_anova, survival
        data_columns: Number of data points/rows
        replicates: Number of replicates
        groups: Number of groups
        title: Template title

    Returns:
        PrismTemplate object
    """
    return PrismTemplate(
        title=title,
        analysis_type=analysis_type,
        data_columns=data_columns,
        replicates=replicates,
        groups=groups
    )


def create_ic50_template(concentrations: Optional[List[float]] = None,
                          replicates: int = 4,
                          title: str = "IC50 Template") -> PrismTemplate:
    """
    Create IC50 analysis template.

    Args:
        concentrations: Custom concentration values (default: standard range)
        replicates: Number of replicates per concentration
        title: Template title

    Returns:
        PrismTemplate for IC50 analysis
    """
    n = len(concentrations) if concentrations else 6
    return generate_template("ic50", n, replicates, title=title)


def create_standard_curve_template(standard_points: int = 7,
                                   replicates: int = 3,
                                   title: str = "Standard Curve") -> PrismTemplate:
    """
    Create standard curve template (ELISA, qPCR, etc.).

    Args:
        standard_points: Number of standard points
        replicates: Number of replicates per point
        title: Template title

    Returns:
        PrismTemplate for standard curve analysis
    """
    return generate_template(
        "standard_curve",
        standard_points,
        replicates,
        title=title
    )


def create_anova_template(groups: int,
                          samples_per_group: int,
                          title: str = "One-way ANOVA") -> PrismTemplate:
    """
    Create one-way ANOVA template.

    Args:
        groups: Number of groups
        samples_per_group: Samples per group
        title: Template title

    Returns:
        PrismTemplate for ANOVA analysis
    """
    return generate_template(
        "one_way_anova",
        samples_per_group,
        groups,
        groups,
        title
    )


def create_ttest_template(n_pairs: int,
                          paired: bool = True,
                          title: str = "t-test") -> PrismTemplate:
    """
    Create t-test template.

    Args:
        n_pairs: Number of pairs/samples
        paired: If True, paired t-test; else independent
        title: Template title

    Returns:
        PrismTemplate for t-test analysis
    """
    at = "paired_ttest" if paired else "two_group_ttest"
    return generate_template(at, n_pairs, title=title)


def create_survival_template(n_subjects: int,
                              n_groups: int = 2,
                              title: str = "Survival Analysis") -> PrismTemplate:
    """
    Create Kaplan-Meier survival analysis template.

    Args:
        n_subjects: Number of subjects
        n_groups: Number of groups (1 for overall, 2 for comparison)
        title: Template title

    Returns:
        PrismTemplate for survival analysis
    """
    return generate_template(
        "survival",
        n_subjects,
        groups=n_groups,
        title=title
    )


if __name__ == "__main__":
    print("=" * 60)
    print("GraphPad Prism Template Generator")
    print("=" * 60)

    output_dir = Path("./prism_templates")
    output_dir.mkdir(exist_ok=True)

    # IC50 template
    print("\n[1] Creating IC50 template...")
    ic50 = create_ic50_template(title="Drug_Screening_IC50")
    ic50.save(str(output_dir / "ic50_template.pzfx"))

    # Standard curve template
    print("\n[2] Creating standard curve template...")
    curve = create_standard_curve_template(title="ELISA_Standard_Curve")
    curve.save(str(output_dir / "standard_curve_template.pzfx"))

    # ANOVA template
    print("\n[3] Creating ANOVA template...")
    anova = create_anova_template(groups=4, samples_per_group=10, title="Drug_Treatment_ANOVA")
    anova.save(str(output_dir / "anova_template.pzfx"))

    # t-test template
    print("\n[4] Creating t-test template...")
    ttest = create_ttest_template(n_pairs=20, paired=True, title="Paired_Samples_ttest")
    ttest.save(str(output_dir / "ttest_template.pzfx"))

    # Survival template
    print("\n[5] Creating survival template...")
    surv = create_survival_template(n_subjects=50, n_groups=2, title="Treatment_Comparison")
    surv.save(str(output_dir / "survival_template.pzfx"))

    print("\n" + "=" * 60)
    print(f"Templates saved to: {output_dir.absolute()}")
    print("=" * 60)
