"""
GraphPad Prism Automation Script
================================
Automated analysis with Prism 9.x / 10.x support.

Features:
    - Auto-detect Prism installation
    - COM interface connection (Windows)
    - Pure Python analysis fallback

Version: 2.0.0
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

import pandas as pd
import numpy as np
from scipy import stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PrismVersion:
    """Prism version information."""
    version: str
    major: int
    minor: int
    path: str

    @property
    def is_prism_10(self) -> bool:
        return self.major >= 10

    @property
    def is_prism_9(self) -> bool:
        return self.major == 9

    def __str__(self):
        return f"GraphPad Prism {self.version} ({self.path})"


class PrismDetector:
    """Detect local Prism installations."""

    COMMON_PATHS = [
        r"C:\Program Files\GraphPad Prism 10",
        r"C:\Program Files\GraphPad Prism 9",
        r"C:\Program Files (x86)\GraphPad Prism 10",
        r"C:\Program Files (x86)\GraphPad Prism 9",
        r"D:\Prism10",
        r"D:\Prism9",
        r"D:\GraphPad\Prism 10",
        r"D:\GraphPad\Prism 9",
        r"E:\Program Files\GraphPad Prism 10",
        r"E:\Program Files\GraphPad Prism 9",
    ]

    REGISTRY_PATHS = [
        r"SOFTWARE\GraphPad\Prism",
        r"SOFTWARE\Wow6432Node\GraphPad\Prism",
    ]

    @classmethod
    def detect_all_installations(cls) -> List[PrismVersion]:
        """Detect all Prism installations on the system."""
        installations = []

        # Check common file paths
        for path in cls.COMMON_PATHS:
            prism_exe = os.path.join(path, "Prism.exe")
            if os.path.exists(prism_exe):
                version = cls._get_version_from_path(path)
                if version:
                    installations.append(version)

        # Check Windows Registry
        if sys.platform == "win32":
            installations.extend(cls._detect_from_registry())

        # Remove duplicates by path
        seen_paths = set()
        unique = []
        for inst in installations:
            if inst.path not in seen_paths:
                unique.append(inst)
                seen_paths.add(inst.path)

        # Sort by version descending
        unique.sort(key=lambda x: (x.major, x.minor), reverse=True)
        return unique

    @classmethod
    def _detect_from_registry(cls) -> List[PrismVersion]:
        """Detect Prism from Windows Registry."""
        installations = []
        try:
            import winreg
            for reg_path in cls.REGISTRY_PATHS:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    ver_value, _ = winreg.QueryValueEx(key, "Version")
                    path_value, _ = winreg.QueryValueEx(key, "InstallPath")
                    winreg.CloseKey(key)

                    major = int(ver_value.split('.')[0])
                    minor = int(ver_value.split('.')[1]) if '.' in ver_value else 0

                    installations.append(PrismVersion(
                        version=ver_value,
                        major=major,
                        minor=minor,
                        path=path_value
                    ))
                except (FileNotFoundError, OSError):
                    continue
        except ImportError:
            logger.warning("winreg not available, skipping registry detection")
        return installations

    @classmethod
    def auto_detect(cls) -> Optional[PrismVersion]:
        """Auto-detect the first available Prism installation."""
        installations = cls.detect_all_installations()
        return installations[0] if installations else None

    @classmethod
    def _get_version_from_path(cls, path: str) -> Optional[PrismVersion]:
        """Extract version from installation path."""
        if "Prism 10" in path:
            return PrismVersion(version="10.0.0", major=10, minor=0, path=path)
        elif "Prism 9" in path:
            return PrismVersion(version="9.0.0", major=9, minor=0, path=path)
        return None


class PrismConnection:
    """Connection to Prism via COM interface."""

    def __init__(self, prism_path: str = None, version: PrismVersion = None):
        self._version = version
        self._prism_app = None
        self._connected = False

        if version:
            self.prism_path = version.path
        elif prism_path:
            self.prism_path = prism_path
            self._version = PrismDetector._get_version_from_path(prism_path)
        else:
            detected = PrismDetector.auto_detect()
            if detected:
                self.prism_path = detected.path
                self._version = detected

        self.prism_exe = os.path.join(self.prism_path, "Prism.exe") if self.prism_path else None

    @classmethod
    def auto_detect(cls) -> 'PrismConnection':
        """Auto-detect and connect to Prism."""
        connection = cls()
        detected = PrismDetector.auto_detect()

        if detected:
            connection.prism_path = detected.path
            connection._version = detected
            connection.prism_exe = os.path.join(detected.path, "Prism.exe")
            logger.info(f"Found: {detected}")
            connection._connect_com()
        else:
            logger.warning("No Prism installation found")

        return connection

    def _connect_com(self):
        """Connect via COM interface (Windows only)."""
        if sys.platform != "win32":
            logger.warning("COM connection only available on Windows")
            return

        try:
            import win32com.client

            prog_id = "Prism10.Application" if (
                self._version and self._version.is_prism_10
            ) else "Prism9.Application" if (
                self._version and self._version.is_prism_9
            ) else None

            if prog_id:
                try:
                    self._prism_app = win32com.client.Dispatch(prog_id)
                    self._connected = True
                    logger.info(f"Connected via COM: {prog_id}")
                except Exception as e:
                    logger.error(f"Failed to connect to {prog_id}: {e}")

            # Fallback: try both versions
            if not self._connected:
                for pid in ["Prism10.Application", "Prism9.Application"]:
                    try:
                        self._prism_app = win32com.client.Dispatch(pid)
                        self._connected = True
                        logger.info(f"Connected via COM: {pid}")
                        break
                    except Exception:
                        continue

        except ImportError:
            logger.warning("pywin32 not installed - COM connection unavailable")

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def version_info(self) -> Optional[PrismVersion]:
        return self._version

    # Delegate analysis to DataAnalyzer
    def analyze_ic50(self, data: Dict, experiment_name: str = "IC50_Analysis"):
        analyzer = DataAnalyzer()
        return analyzer.analyze_ic50(data, experiment_name)

    def two_sample_ttest(self, group1: List, group2: List,
                         paired: bool = False, name: str = "t_test"):
        analyzer = DataAnalyzer()
        return analyzer.two_sample_ttest(group1, group2, paired, name)

    def one_way_anova(self, groups: Dict[str, List], name: str = "one_way_anova"):
        analyzer = DataAnalyzer()
        return analyzer.one_way_anova(groups, name)

    def create_standard_curve(self, data: Dict, title: str = "Standard Curve"):
        analyzer = DataAnalyzer()
        return analyzer.create_standard_curve(data, title)


class DataAnalyzer:
    """Pure Python data analysis (no Prism required)."""

    def __init__(self, output_dir: str = "./prism_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def analyze_ic50(self, data: Dict,
                     experiment_name: str = "IC50_Analysis") -> 'IC50Result':
        """
        IC50 analysis using 4-parameter logistic regression.

        Args:
            data: Dict with 'concentration' and 'response' lists
            experiment_name: Name for the experiment

        Returns:
            IC50Result object with EC50, Hill slope, R², etc.
        """
        from scipy.optimize import curve_fit

        conc = np.array(data['concentration'])
        response = np.array(data['response'])

        def logistic4(x, bottom, top, ec50, hill_slope):
            return bottom + (top - bottom) / (1 + (ec50 / x) ** hill_slope)

        try:
            # Initial parameter estimates
            bottom_init = min(response)
            top_init = max(response)
            ec50_init = np.median(conc)
            hill_init = 1.0

            popt, pcov = curve_fit(
                logistic4, conc, response,
                p0=[bottom_init, top_init, ec50_init, hill_init],
                maxfev=10000
            )

            bottom, top, ec50, hill_slope = popt

            # Calculate R²
            predicted = logistic4(conc, *popt)
            ss_res = np.sum((response - predicted) ** 2)
            ss_tot = np.sum((response - np.mean(response)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)

            result = IC50Result(
                ec50=ec50, hill_slope=hill_slope,
                bottom=bottom, top=top,
                r_squared=r_squared,
                experiment_name=experiment_name
            )
            result.plot_path = self._plot_ic50(conc, response, popt, experiment_name)
            logger.info(f"IC50 analysis complete: EC50 = {ec50:.4f}")
            return result

        except Exception as e:
            logger.error(f"IC50 analysis failed: {e}")
            return None

    def _plot_ic50(self, conc, response, popt, title):
        """Generate IC50 plot."""
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 6))
        plt.scatter(conc, response, color='black', s=50, zorder=5, label='Data')

        # Fit curve
        x_fit = np.logspace(np.log10(min(conc)), np.log10(max(conc)), 100)
        y_fit = logistic4(x_fit, *popt)
        plt.plot(x_fit, y_fit, 'r-', linewidth=2, label='Fit')

        # EC50 marker
        ec50 = popt[2]
        y_ec50 = logistic4(ec50, *popt)
        plt.axvline(x=ec50, color='blue', linestyle='--', alpha=0.5)
        plt.axhline(y=y_ec50, color='blue', linestyle='--', alpha=0.5)
        plt.scatter([ec50], [y_ec50], color='blue', s=100, zorder=6)
        plt.annotate(f'EC50 = {ec50:.4f}', (ec50, y_ec50),
                     textcoords="offset points", xytext=(10, 10), fontsize=10)

        plt.xscale('log')
        plt.xlabel('Concentration', fontsize=12)
        plt.ylabel('Response (%)', fontsize=12)
        plt.title(f'{title}\nIC50 Analysis', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)

        plot_path = os.path.join(self.output_dir, f'{title}_IC50.pdf')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        return plot_path

    def two_sample_ttest(self, group1: List, group2: List,
                         paired: bool = False,
                         name: str = "t_test") -> Dict:
        """
        Two-sample t-test (independent or paired).

        Args:
            group1: First group data
            group2: Second group data
            paired: If True, paired t-test
            name: Analysis name

        Returns:
            Dict with t-statistic, p-value, effect size, etc.
        """
        g1 = np.array(group1)
        g2 = np.array(group2)

        if paired:
            t_stat, p_value = stats.ttest_rel(g1, g2)
        else:
            t_stat, p_value = stats.ttest_ind(g1, g2)

        # Cohen's d effect size
        pooled_std = np.sqrt((np.var(g1) + np.var(g2)) / 2)
        cohens_d = (np.mean(g1) - np.mean(g2)) / pooled_std if pooled_std > 0 else 0

        result = {
            'name': name,
            'test_type': 'Paired t-test' if paired else 'Independent t-test',
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'mean_group1': float(np.mean(g1)),
            'mean_group2': float(np.mean(g2)),
            'std_group1': float(np.std(g1, ddof=1)),
            'std_group2': float(np.std(g2, ddof=1)),
            'n_group1': len(g1),
            'n_group2': len(g2),
            'cohens_d': float(cohens_d),
            'significant': bool(p_value < 0.05)
        }
        self._plot_ttest(g1, g2, result, name)
        logger.info(f"t-test complete: p = {p_value:.4e}")
        return result

    def _plot_ttest(self, g1, g2, result, name):
        """Generate t-test plot."""
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Box plot
        ax1.boxplot([g1, g2], labels=['Group 1', 'Group 2'])
        ax1.scatter([1]*len(g1), g1, alpha=0.5, color='blue')
        ax1.scatter([2]*len(g2), g2, alpha=0.5, color='red')
        ax1.set_ylabel('Value')
        ax1.set_title(f'{name}\nBox Plot')
        ax1.grid(True, alpha=0.3)

        # Scatter plot
        ax2.scatter(range(1, len(g1)+1), g1, label='Group 1', alpha=0.7)
        ax2.scatter(range(1, len(g2)+1), g2, label='Group 2', alpha=0.7)
        ax2.axhline(np.mean(g1), color='blue', linestyle='--', alpha=0.5)
        ax2.axhline(np.mean(g2), color='red', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Sample')
        ax2.set_ylabel('Value')
        ax2.set_title(f'Means: G1={np.mean(g1):.2f}, G2={np.mean(g2):.2f}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # P-value annotation
        p_val = result['p_value']
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "ns"
        fig.suptitle(f't-test Result: p = {p_val:.4e} ({sig})', fontsize=12)

        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, f'{name}_ttest.pdf')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()

    def one_way_anova(self, groups: Dict[str, List],
                      name: str = "one_way_anova") -> Dict:
        """
        One-way ANOVA with Tukey HSD post-hoc test.

        Args:
            groups: Dict mapping group names to data lists
            name: Analysis name

        Returns:
            Dict with ANOVA table and post-hoc results
        """
        group_arrays = [np.array(g) for g in groups.values()]
        f_stat, p_value = stats.f_oneway(*group_arrays)

        # ANOVA table calculations
        all_data = np.concatenate(group_arrays)
        grand_mean = np.mean(all_data)
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in group_arrays)
        ss_total = np.sum((all_data - grand_mean)**2)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0

        df_between = len(groups) - 1
        df_within = sum(len(g) - 1 for g in group_arrays)
        df_total = df_between + df_within
        ms_between = ss_between / df_between if df_between > 0 else 0
        ss_within = ss_total - ss_between
        ms_within = ss_within / df_within if df_within > 0 else 0

        result = {
            'name': name,
            'f_statistic': float(ms_between / ms_within) if ms_within > 0 else 0,
            'p_value': float(p_value),
            'df_between': df_between,
            'df_within': df_within,
            'df_total': df_total,
            'ss_between': float(ss_between),
            'ss_within': float(ss_within),
            'ss_total': float(ss_total),
            'ms_between': float(ms_between),
            'ms_within': float(ms_within),
            'eta_squared': float(eta_squared),
            'significant': bool(p_value < 0.05),
            'group_means': {k: float(np.mean(v)) for k, v in groups.items()}
        }

        # Tukey HSD post-hoc
        if p_value < 0.05:
            result['post_hoc'] = self._tukey_hsd(group_arrays, list(groups.keys()))
            logger.info("ANOVA significant, post-hoc analysis performed")

        self._plot_anova(group_arrays, groups.keys(), result, name)
        logger.info(f"ANOVA complete: F = {result['f_statistic']:.2f}, p = {p_value:.4e}")
        return result

    def _tukey_hsd(self, groups, group_names) -> Dict:
        """Tukey HSD post-hoc test."""
        from scipy.stats import tukey_hsd
        result = tukey_hsd(*groups)
        post_hoc = {}
        for i, name1 in enumerate(group_names):
            for j, name2 in enumerate(group_names):
                if i < j:
                    key = f"{name1} vs {name2}"
                    post_hoc[key] = {
                        'p_value': float(result.pvalue[i, j]),
                        'significant': bool(result.pvalue[i, j] < 0.05)
                    }
        return post_hoc

    def _plot_anova(self, groups, group_names, result, name):
        """Generate ANOVA plot."""
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Box plot
        colors = plt.cm.Set3(np.linspace(0, 1, len(groups)))
        bp = ax1.boxplot(groups, labels=group_names, patch_artist=True)
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        for i, g in enumerate(groups):
            ax1.scatter([i+1]*len(g), g, alpha=0.5, color='black', s=20)
        ax1.set_ylabel('Value')
        ax1.set_title(f'{name}\nOne-way ANOVA')
        ax1.grid(True, alpha=0.3, axis='y')

        # Bar plot with error bars
        means = [np.mean(g) for g in groups]
        stds = [np.std(g, ddof=1) for g in groups]
        x_pos = range(1, len(groups) + 1)
        ax2.bar(x_pos, means, yerr=stds, capsize=5, color=colors, alpha=0.8)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(group_names)
        ax2.set_ylabel('Mean ± SD')
        ax2.set_title('Group Means Comparison')

        if result['significant']:
            max_y = max(means) + max(stds) + 5
            ax2.annotate('*', (len(groups)/2, max_y), fontsize=20, ha='center')

        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, f'{name}_anova.pdf')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()

    def create_standard_curve(self, data: Dict,
                              title: str = "Standard Curve") -> 'StandardCurveResult':
        """
        Linear regression for standard curve.

        Args:
            data: Dict with 'concentration' and 'response' lists
            title: Curve title

        Returns:
            StandardCurveResult with slope, intercept, R²
        """
        conc = np.array(data['concentration'])
        response = np.array(data['response'])

        slope, intercept, r_value, p_value, std_err = stats.linregress(
            conc, response
        )
        r_squared = r_value ** 2

        plot_path = self._plot_standard_curve(
            conc, response, slope, intercept, r_squared, title
        )

        result = StandardCurveResult(
            slope=slope, intercept=intercept, r_squared=r_squared,
            equation=f"y = {slope:.4f}x + {intercept:.4f}",
            plot_path=plot_path, title=title
        )
        logger.info(f"Standard curve complete: R² = {r_squared:.4f}")
        return result

    def _plot_standard_curve(self, x, y, slope, intercept, r2, title):
        """Generate standard curve plot."""
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 6))
        plt.scatter(x, y, color='black', s=80, zorder=5, label='Standard')

        x_fit = np.linspace(min(x), max(x), 100)
        y_fit = slope * x_fit + intercept
        plt.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Fit (R² = {r2:.4f})')

        equation = f'y = {slope:.4f}x + {intercept:.4f}'
        plt.text(0.05, 0.95, equation, transform=plt.gca().transAxes,
                 fontsize=11, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.xlabel('Concentration', fontsize=12)
        plt.ylabel('Response (OD)', fontsize=12)
        plt.title(f'{title}\nStandard Curve', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)

        plot_path = os.path.join(self.output_dir, f'{title}_standard_curve.pdf')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        return plot_path

    def calculate_unknowns(self, curve_result: 'StandardCurveResult',
                           unknown_od: List[float]) -> Dict:
        """Calculate unknown concentrations from OD values."""
        slope = curve_result.slope
        intercept = curve_result.intercept
        concentrations = [(od - intercept) / slope for od in unknown_od]
        return {
            'unknown_ods': unknown_od,
            'calculated_concentrations': concentrations,
            'equation_used': curve_result.equation
        }

    def survival_analysis(self, time: List, event: List,
                          group: List = None,
                          name: str = "survival") -> Dict:
        """
        Kaplan-Meier survival analysis.

        Args:
            time: Survival times
            event: Event indicators (1=event, 0=censored)
            group: Optional group labels for log-rank test
            name: Analysis name

        Returns:
            Dict with survival probabilities and statistics
        """
        from scipy.stats import chi2

        time = np.array(time)
        event = np.array(event)

        if group is None:
            # Single group Kaplan-Meier
            sorted_idx = np.argsort(time)
            time_sorted = time[sorted_idx]
            event_sorted = event[sorted_idx]

            n = len(time)
            survival_prob = []
            time_points = []
            survived = n

            for i, (t, e) in enumerate(zip(time_sorted, event_sorted)):
                at_risk = n - i
                if e == 1:
                    survived -= 1
                prob = survived / at_risk
                survival_prob.append(prob)
                time_points.append(t)

            result = {
                'name': name,
                'median_survival': float(np.median(time[event == 1])),
                'survival_times': time_points,
                'survival_probabilities': survival_prob
            }
            self._plot_survival(time_points, survival_prob, name, None, result)

        else:
            # Log-rank test for two groups
            groups = np.array(group)
            unique_groups = np.unique(groups)

            if len(unique_groups) == 2:
                g1_mask = groups == unique_groups[0]
                g2_mask = groups == unique_groups[1]

                t1, e1 = time[g1_mask], event[g1_mask]
                t2, e2 = time[g2_mask], event[g2_mask]

                all_times = sorted(set(t1) | set(t2))
                observed1, expected1 = 0, 0

                for t in all_times:
                    at_risk1 = np.sum(t1 >= t)
                    at_risk2 = np.sum(t2 >= t)
                    events1 = np.sum((t1 == t) & (e1 == 1))
                    if at_risk1 + at_risk2 > 0:
                        expected1 += events1 * (at_risk1 / (at_risk1 + at_risk2))
                    observed1 += events1

                var_e1 = 1 if (at_risk1 + at_risk2) == 0 else (
                    at_risk1 * at_risk2 * (observed1 / (at_risk1 + at_risk2)) *
                    (1 - at_risk1 / (at_risk1 + at_risk2))) / (at_risk1 + at_risk2)
                chi2_stat = (observed1 - expected1) ** 2 / var_e1 if var_e1 > 0 else 0
                p_value = 1 - chi2.cdf(chi2_stat, 1)

                result = {
                    'name': name,
                    'groups': unique_groups.tolist(),
                    'log_rank_chi2': float(chi2_stat),
                    'p_value': float(p_value),
                    'significant': bool(p_value < 0.05)
                }
                self._plot_survival(time, event, name, group, result)
            else:
                result = {'error': 'Only 2 groups supported for log-rank test'}

        logger.info(f"Survival analysis complete: {result.get('p_value', 'N/A')}")
        return result

    def _plot_survival(self, time, survival_prob, name, group, result):
        """Generate Kaplan-Meier plot."""
        import matplotlib.pyplot as plt

        plt.figure(figsize=(8, 6))
        if group is None:
            plt.step(time, survival_prob, where='post', linewidth=2, color='blue')
            plt.scatter(time, survival_prob, color='blue', s=50, zorder=5)
        else:
            for g in np.unique(group):
                mask = np.array(group) == g
                g_time = np.array(time)[mask]
                plt.step(range(len(g_time)), g_time, where='post', label=f'Group {g}')

        plt.xlabel('Time', fontsize=12)
        plt.ylabel('Survival Probability', fontsize=12)
        plt.title(f'{name}\nKaplan-Meier Curve', fontsize=14)

        if 'p_value' in result:
            p = result['p_value']
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            plt.text(0.05, 0.15, f'Log-rank p = {p:.4e} ({sig})',
                     transform=plt.gca().transAxes, fontsize=10)

        if 'median_survival' in result:
            plt.text(0.05, 0.05, f'Median: {result["median_survival"]:.1f}',
                     transform=plt.gca().transAxes, fontsize=10)

        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 1.05)

        plot_path = os.path.join(self.output_dir, f'{name}_survival.pdf')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()


# Helper functions for logistic4 (module-level for reuse)
def logistic4(x, bottom, top, ec50, hill_slope):
    """4-parameter logistic function."""
    return bottom + (top - bottom) / (1 + (ec50 / x) ** hill_slope)


# Module-level convenience functions
def detect_prism() -> Optional[PrismVersion]:
    """Convenience function to detect Prism."""
    return PrismDetector.auto_detect()


def analyze_ic50_from_excel(filepath: str, sheet_name: int = 0,
                            conc_col: str = "concentration",
                            response_col: str = "response",
                            output_dir: str = "./prism_output") -> IC50Result:
    """Analyze IC50 from Excel file."""
    analyzer = DataAnalyzer(output_dir)
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    data = {
        'concentration': df[conc_col].tolist(),
        'response': df[response_col].tolist()
    }
    return analyzer.analyze_ic50(data, experiment_name=Path(filepath).stem)


def batch_ttest_from_excel(filepath: str,
                            output_dir: str = "./prism_output") -> pd.DataFrame:
    """Batch t-test from Excel with multiple comparisons."""
    analyzer = DataAnalyzer(output_dir)
    df = pd.read_excel(filepath)
    results = []
    for _, row in df.iterrows():
        name = row.iloc[0]
        group1 = [float(x) for x in str(row.iloc[1]).split(',')]
        group2 = [float(x) for x in str(row.iloc[2]).split(',')]
        result = analyzer.two_sample_ttest(group1, group2, name=name)
        results.append(result)
    return pd.DataFrame(results)


class IC50Result:
    """IC50 analysis result container."""

    def __init__(self, ec50, hill_slope, bottom, top, r_squared, experiment_name):
        self.ec50 = ec50
        self.hill_slope = hill_slope
        self.bottom = bottom
        self.top = top
        self.r_squared = r_squared
        self.experiment_name = experiment_name
        self.plot_path = None

    def __repr__(self):
        return (f"IC50 Result: EC50 = {self.ec50:.4f}, "
                f"Hill Slope = {self.hill_slope:.2f}, R² = {self.r_squared:.4f}")

    def save(self, filepath: str):
        """Save results to text file."""
        with open(filepath.replace('.pdf', '.txt'), 'w') as f:
            f.write(f"IC50 Analysis Results\n")
            f.write(f"=" * 40 + "\n")
            f.write(f"Experiment: {self.experiment_name}\n")
            f.write(f"EC50: {self.ec50:.6f}\n")
            f.write(f"Hill Slope: {self.hill_slope:.4f}\n")
            f.write(f"Bottom: {self.bottom:.4f}\n")
            f.write(f"Top: {self.top:.4f}\n")
            f.write(f"R²: {self.r_squared:.6f}\n")


class StandardCurveResult:
    """Standard curve result container."""

    def __init__(self, slope, intercept, r_squared, equation, plot_path, title):
        self.slope = slope
        self.intercept = intercept
        self.r_squared = r_squared
        self.equation = equation
        self.plot_path = plot_path
        self.title = title

    def __repr__(self):
        return f"Standard Curve: {self.equation}, R² = {self.r_squared:.4f}"

    def export_equation(self, filepath: str):
        """Export equation to text file."""
        with open(filepath, 'w') as f:
            f.write(f"Standard Curve Equation\n")
            f.write(f"=" * 40 + "\n")
            f.write(f"Title: {self.title}\n")
            f.write(f"Equation: {self.equation}\n")
            f.write(f"Slope: {self.slope:.6f}\n")
            f.write(f"Intercept: {self.intercept:.6f}\n")
            f.write(f"R²: {self.r_squared:.6f}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("GraphPad Prism Data Analysis Tool (v2.0.0)")
    print("=" * 60)

    # Detect Prism
    print("\n[1] Detecting Prism installation...")
    detected = detect_prism()
    if detected:
        print(f"    Found: {detected}")
    else:
        print("    Not found - using pure Python mode")

    # IC50 demo
    print("\n[2] IC50 analysis demo...")
    analyzer = DataAnalyzer(output_dir="./test_output")
    ic50_data = {
        'concentration': [0.001, 0.01, 0.1, 1, 10, 100],
        'response': [105, 98, 85, 50, 15, 5]
    }
    result = analyzer.analyze_ic50(ic50_data, experiment_name="Drug_A")
    print(f"    Result: {result}")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
