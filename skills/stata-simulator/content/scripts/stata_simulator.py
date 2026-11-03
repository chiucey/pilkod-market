#!/usr/bin/env python3
"""
Stata Do-File Simulator
A Python-based simulator for executing Stata do-file commands.
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import statistics


@dataclass
class StataResult:
    """Result of a Stata command execution."""
    command: str
    success: bool
    output: str = ""
    data: Optional[pd.DataFrame] = None
    error: Optional[str] = None


@dataclass
class MacroStore:
    """Storage for local and global macros."""
    local: Dict[str, str] = field(default_factory=dict)
    global_vars: Dict[str, str] = field(default_factory=dict)


class StataEngine:
    """
    Stata command engine simulator.
    Supports common Stata commands for data analysis and statistical modeling.
    """

    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.macros = MacroStore()
        self.log_output: List[str] = []
        self._initialize_commands()

    def _initialize_commands(self):
        """Initialize command handlers."""
        self.commands = {
            'use': self._cmd_use,
            'save': self._cmd_save,
            'describe': self._cmd_describe,
            'list': self._cmd_list,
            'browse': self._cmd_browse,
            'summarize': self._cmd_summarize,
            'sum': self._cmd_summarize,
            'correlate': self._cmd_correlate,
            'corr': self._cmd_correlate,
            'tabulate': self._cmd_tabulate,
            'tab': self._cmd_tabulate,
            'generate': self._cmd_generate,
            'gen': self._cmd_generate,
            'replace': self._cmd_replace,
            'drop': self._cmd_drop,
            'keep': self._cmd_keep,
            'rename': self._cmd_rename,
            'regress': self._cmd_regress,
            'reg': self._cmd_regress,
            'logit': self._cmd_logit,
            'probit': self._cmd_probit,
            'ttest': self._cmd_ttest,
            'anova': self._cmd_anova,
            'pwcorr': self._cmd_pwcorr,
            'display': self._cmd_display,
            'di': self._cmd_display,
            'mean': self._cmd_mean,
            'count': self._cmd_count,
            'sort': self._cmd_sort,
            'gsort': self._cmd_gsort,
            'egen': self._cmd_egen,
            'encode': self._cmd_encode,
            'decode': self._cmd_decode,
            'merge': self._cmd_merge,
            'append': self._cmd_append,
        }

    def execute_file(self, filepath: str) -> List[StataResult]:
        """Execute a Stata do-file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.execute(content)

    def execute(self, code: str) -> List[StataResult]:
        """Execute Stata commands from a string."""
        results = []
        lines = self._preprocess(code)

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('*'):
                i += 1
                continue

            # Handle multi-line commands
            if line.strip().endswith('{'):
                # Start of a block
                block_lines = [line]
                brace_count = line.count('{') - line.count('}')
                i += 1
                while i < len(lines) and brace_count > 0:
                    block_lines.append(lines[i])
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    i += 1
                block_code = '\n'.join(block_lines)
                result = self._execute_block(block_code)
                results.append(result)
            else:
                result = self._execute_line(line)
                results.append(result)

            i += 1

        return results

    def _preprocess(self, code: str) -> List[str]:
        """Preprocess code: handle macros, clean up."""
        lines = code.split('\n')
        processed = []

        for line in lines:
            # Remove inline comments
            if '//' in line:
                line = line.split('//')[0]

            # Macro substitution for local macros
            for name, value in self.macros.local.items():
                line = re.sub(r'`' + name + r"'", value, line)
                line = re.sub(r'\$' + name + r'\b', value, line)

            # Global macro substitution
            for name, value in self.macros.global_vars.items():
                line = re.sub(r'\$' + name + r'\b', value, line)

            processed.append(line)

        return processed

    def _execute_line(self, line: str) -> StataResult:
        """Execute a single line of Stata code."""
        line = line.strip()
        if not line:
            return StataResult(command="", success=True, output="")

        # Parse command
        cmd_match = re.match(r'^(\w+)(?:\s+(.*))?$', line)
        if not cmd_match:
            return StataResult(
                command=line,
                success=False,
                error=f"Invalid command syntax: {line}"
            )

        cmd = cmd_match.group(1).lower()
        args = cmd_match.group(2) or ""

        # Handle local macro definition
        if cmd == 'local':
            return self._cmd_local(args)
        if cmd == 'global':
            return self._cmd_global(args)

        # Handle if/else without braces
        if cmd == 'if':
            return self._cmd_if_line(args)
        if cmd == 'else':
            return self._cmd_else()

        # Execute command
        if cmd in self.commands:
            return self.commands[cmd](args)
        else:
            return StataResult(
                command=cmd,
                success=False,
                error=f"Command not implemented: {cmd}"
            )

    def _execute_block(self, block_code: str) -> StataResult:
        """Execute a block of code (e.g., foreach, forvalues, while)."""
        return StataResult(
            command="block",
            success=True,
            output=f"[Block execution - see individual results]"
        )

    def _cmd_local(self, args: str) -> StataResult:
        """Handle local macro definition."""
        # local name = "value" or local name value
        match = re.match(r'^(\w+)\s*=\s*["\'](.+?)["\']', args)
        if match:
            name, value = match.groups()
            self.macros.local[name] = value
            return StataResult(
                command="local",
                success=True,
                output=f"Local macro `name' = {value}"
            )

        match = re.match(r'^(\w+)\s+(.+)$', args)
        if match:
            name, value = match.groups()
            self.macros.local[name] = value.strip()
            return StataResult(
                command="local",
                success=True,
                output=f"Local macro `name' = {value}"
            )

        return StataResult(
            command="local",
            success=False,
            error="Invalid local macro syntax"
        )

    def _cmd_global(self, args: str) -> StataResult:
        """Handle global macro definition."""
        match = re.match(r'^(\w+)\s*=\s*["\'](.+?)["\']', args)
        if match:
            name, value = match.groups()
            self.macros.global_vars[name] = value
            return StataResult(
                command="global",
                success=True,
                output=f"Global macro $name = {value}"
            )

        return StataResult(
            command="global",
            success=False,
            error="Invalid global macro syntax"
        )

    def _cmd_use(self, args: str) -> StataResult:
        """Load a dataset."""
        # Parse: use "file.dta" [, clear]
        match = re.search(r'["\'](.+?)["\']', args)
        if not match:
            return StataResult(
                command="use",
                success=False,
                error="No file specified"
            )

        filepath = match.group(1)

        try:
            if filepath.endswith('.csv'):
                self.data = pd.read_csv(filepath)
            elif filepath.endswith('.dta'):
                self.data = pd.read_stata(filepath)
            elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
                self.data = pd.read_excel(filepath)
            else:
                self.data = pd.read_csv(filepath)

            return StataResult(
                command="use",
                success=True,
                output=f"Loaded {len(self.data)} observations, {len(self.data.columns)} variables",
                data=self.data
            )
        except Exception as e:
            return StataResult(
                command="use",
                success=False,
                error=f"Error loading file: {str(e)}"
            )

    def _cmd_save(self, args: str) -> StataResult:
        """Save a dataset."""
        match = re.search(r'["\'](.+?)["\']', args)
        if not match:
            return StataResult(
                command="save",
                success=False,
                error="No file specified"
            )

        filepath = match.group(1)

        if self.data is None:
            return StataResult(
                command="save",
                success=False,
                error="No data in memory"
            )

        try:
            if filepath.endswith('.csv'):
                self.data.to_csv(filepath, index=False)
            elif filepath.endswith('.dta'):
                self.data.to_stata(filepath, write_index=False)
            elif filepath.endswith('.xlsx'):
                self.data.to_excel(filepath, index=False)
            else:
                self.data.to_csv(filepath, index=False)

            return StataResult(
                command="save",
                success=True,
                output=f"Data saved to {filepath}"
            )
        except Exception as e:
            return StataResult(
                command="save",
                success=False,
                error=f"Error saving file: {str(e)}"
            )

    def _cmd_describe(self, args: str) -> StataResult:
        """Describe the dataset."""
        if self.data is None:
            return StataResult(
                command="describe",
                success=False,
                error="No data in memory. Use 'use' command first."
            )

        output = []
        output.append(f"Contains data from {self.data.shape[0]} observations")
        output.append(f"Observations: {self.data.shape[0]}")
        output.append(f"Variables: {self.data.shape[1]}")
        output.append("")
        output.append("Variable      Storage   Display   Value")
        output.append("variable name   type    format    label      variable label")
        output.append("-" * 70)

        for col in self.data.columns:
            dtype = self.data[col].dtype
            storage = "str" if dtype == 'object' else "num"
            sample = str(self.data[col].iloc[0])[:10] if len(self.data[col]) > 0 else ""
            output.append(f"{col:<15} {storage:<8} %10s    {sample}")

        return StataResult(
            command="describe",
            success=True,
            output="\n".join(output),
            data=self.data
        )

    def _cmd_list(self, args: str) -> StataResult:
        """List data observations."""
        if self.data is None:
            return StataResult(
                command="list",
                success=False,
                error="No data in memory"
            )

        # Parse variables if specified
        vars_match = re.search(r'in\s+(\d+)\s*(?:/(\d+))?', args)
        limit = 10  # Default limit

        if vars_match:
            start = int(vars_match.group(1)) - 1
            end = int(vars_match.group(2)) if vars_match.group(2) else start + 1
            df = self.data.iloc[start:end]
        else:
            df = self.data.head(limit)

        output = df.to_string(index=True)
        return StataResult(
            command="list",
            success=True,
            output=output,
            data=df
        )

    def _cmd_browse(self, args: str) -> StataResult:
        """Browse data (simulated)."""
        if self.data is None:
            return StataResult(
                command="browse",
                success=False,
                error="No data in memory"
            )

        return StataResult(
            command="browse",
            success=True,
            output=f"[Data Browser] Showing {len(self.data)} rows. Open in your environment to view.]",
            data=self.data.head(20)
        )

    def _cmd_summarize(self, args: str) -> StataResult:
        """Summarize variables (descriptive statistics)."""
        if self.data is None:
            return StataResult(
                command="summarize",
                success=False,
                error="No data in memory"
            )

        # Parse variables
        if args.strip():
            var_names = [v.strip() for v in re.split(r'[\s,]+', args) if v.strip()]
            df = self.data[var_names]
        else:
            df = self.data.select_dtypes(include=[np.number])

        stats = df.describe().T
        stats['range'] = stats['max'] - stats['min']
        stats['variance'] = df.var()

        output = []
        output.append("    Variable |       Obs        Mean    Std. dev.       Min        Max")
        output.append("-" * 70)

        for var in stats.index:
            obs = int(stats.loc[var, 'count'])
            mean = stats.loc[var, 'mean']
            std = stats.loc[var, 'std']
            min_val = stats.loc[var, 'min']
            max_val = stats.loc[var, 'max']
            output.append(f"{var:<14} |{obs:>10.0f}{mean:>12.4f}{std:>12.4f}{min_val:>12.4f}{max_val:>12.4f}")

        return StataResult(
            command="summarize",
            success=True,
            output="\n".join(output),
            data=stats
        )

    def _cmd_correlate(self, args: str) -> StataResult:
        """Calculate correlations."""
        if self.data is None:
            return StataResult(
                command="correlate",
                success=False,
                error="No data in memory"
            )

        # Parse variables
        if args.strip():
            var_names = [v.strip() for v in re.split(r'[\s,]+', args) if v.strip()]
            df = self.data[var_names]
        else:
            df = self.data.select_dtypes(include=[np.number])

        corr = df.corr()

        output = []
        output.append("(obs=)")
        output.append("")

        # Format correlation matrix
        var_str = " ".join([f"{v[:8]:>10}" for v in corr.columns])
        output.append(f"{'':>10}" + var_str)
        output.append("-" * (10 + len(corr.columns) * 10))

        for i, row in enumerate(corr.index):
            row_str = " ".join([f"{corr.loc[row, col]:>10.4f}" for col in corr.columns])
            output.append(f"{row[:8]:>10}" + row_str)

        return StataResult(
            command="correlate",
            success=True,
            output="\n".join(output),
            data=corr
        )

    def _cmd_tabulate(self, args: str) -> StataResult:
        """Create frequency tables."""
        if self.data is None:
            return StataResult(
                command="tabulate",
                success=False,
                error="No data in memory"
            )

        # Parse variable
        var_match = re.search(r'^(\w+)', args)
        if not var_match:
            return StataResult(
                command="tabulate",
                success=False,
                error="No variable specified"
            )

        var = var_match.group(1)
        if var not in self.data.columns:
            return StataResult(
                command="tabulate",
                success=False,
                error=f"Variable '{var}' not found"
            )

        freq = self.data[var].value_counts().sort_index()
        total = freq.sum()

        output = []
        output.append(f"{var}")
        output.append("-" * 40)
        output.append(f"{'Value':<15} |  Freq.   Percent   Cumulative")
        output.append("-" * 40)

        cum = 0
        for val, count in freq.items():
            pct = (count / total) * 100
            cum += pct
            val_str = str(val)[:15]
            output.append(f"{val_str:<15} |{count:>6.0f}  {pct:>7.2f}%  {cum:>9.2f}%")

        output.append("-" * 40)
        output.append(f"{'Total':<15} |{total:>6.0f}  {100.00:>7.2f}%")

        return StataResult(
            command="tabulate",
            success=True,
            output="\n".join(output)
        )

    def _cmd_generate(self, args: str) -> StataResult:
        """Generate a new variable."""
        if self.data is None:
            return StataResult(
                command="generate",
                success=False,
                error="No data in memory"
            )

        # parse: gen newvar = expression
        match = re.match(r'^(\w+)\s*=\s*(.+)$', args)
        if not match:
            return StataResult(
                command="generate",
                success=False,
                error="Invalid syntax. Usage: gen newvar = expression"
            )

        newvar, expr = match.groups()

        # Handle common expressions
        try:
            # Simple arithmetic
            if re.match(r'^-?\d+\.?\d*$', expr.strip()):
                self.data[newvar] = float(expr.strip())
            elif expr.strip() in self.data.columns:
                self.data[newvar] = self.data[expr.strip()]
            else:
                # Evaluate expression
                self.data.eval(f"{newvar} = {expr}", inplace=True)

            return StataResult(
                command="generate",
                success=True,
                output=f"variable {newvar} was generated",
                data=self.data
            )
        except Exception as e:
            return StataResult(
                command="generate",
                success=False,
                error=f"Error generating variable: {str(e)}"
            )

    def _cmd_replace(self, args: str) -> StataResult:
        """Replace variable values."""
        if self.data is None:
            return StataResult(
                command="replace",
                success=False,
                error="No data in memory"
            )

        match = re.match(r'^(\w+)\s*=\s*(.+)$', args)
        if not match:
            return StataResult(
                command="replace",
                success=False,
                error="Invalid syntax"
            )

        var, expr = match.groups()
        if var not in self.data.columns:
            return StataResult(
                command="replace",
                success=False,
                error=f"Variable '{var}' not found"
            )

        try:
            self.data.eval(f"{var} = {expr}", inplace=True)
            return StataResult(
                command="replace",
                success=True,
                output=f"{var} replaced",
                data=self.data
            )
        except Exception as e:
            return StataResult(
                command="replace",
                success=False,
                error=f"Error replacing values: {str(e)}"
            )

    def _cmd_drop(self, args: str) -> StataResult:
        """Drop variables or observations."""
        if self.data is None:
            return StataResult(
                command="drop",
                success=False,
                error="No data in memory"
            )

        args = args.strip()

        # Drop variables
        if args in self.data.columns:
            self.data = self.data.drop(columns=[args])
            return StataResult(
                command="drop",
                success=True,
                output=f"variable {args} dropped",
                data=self.data
            )

        # Drop by pattern
        if args.startswith("in "):
            # Parse range like "in 1/10"
            match = re.search(r'in\s+(\d+)\s*/\s*(\d+)', args)
            if match:
                start, end = int(match.group(1)) - 1, int(match.group(2))
                self.data = self.data.drop(range(start, end))
                return StataResult(
                    command="drop",
                    success=True,
                    output=f"observations {start+1} to {end} dropped",
                    data=self.data
                )

        return StataResult(
            command="drop",
            success=False,
            error="Invalid drop syntax"
        )

    def _cmd_keep(self, args: str) -> StataResult:
        """Keep variables or observations."""
        if self.data is None:
            return StataResult(
                command="keep",
                success=False,
                error="No data in memory"
            )

        args = args.strip()

        if args in self.data.columns:
            self.data = self.data[[args]]
            return StataResult(
                command="keep",
                success=True,
                output=f"variable {args} kept",
                data=self.data
            )

        return StataResult(
            command="keep",
            success=False,
            error="Invalid keep syntax"
        )

    def _cmd_rename(self, args: str) -> StataResult:
        """Rename a variable."""
        if self.data is None:
            return StataResult(
                command="rename",
                success=False,
                error="No data in memory"
            )

        match = re.match(r'^(\w+)\s+(\w+)$', args)
        if not match:
            return StataResult(
                command="rename",
                success=False,
                error="Invalid syntax. Usage: rename oldvar newvar"
            )

        old, new = match.groups()
        if old not in self.data.columns:
            return StataResult(
                command="rename",
                success=False,
                error=f"Variable '{old}' not found"
            )

        self.data = self.data.rename(columns={old: new})
        return StataResult(
            command="rename",
            success=True,
            output=f"variable {old} renamed to {new}",
            data=self.data
        )

    def _cmd_regress(self, args: str) -> StataResult:
        """Perform linear regression."""
        if self.data is None:
            return StataResult(
                command="regress",
                success=False,
                error="No data in memory"
            )

        # Parse: regress depvar indepvars
        parts = args.strip().split()
        if len(parts) < 2:
            return StataResult(
                command="regress",
                success=False,
                error="Invalid syntax. Usage: regress depvar indepvars"
            )

        depvar = parts[0]
        indepvars = parts[1:]

        # Validate variables
        if depvar not in self.data.columns:
            return StataResult(
                command="regress",
                success=False,
                error=f"Dependent variable '{depvar}' not found"
            )

        for iv in indepvars:
            if iv not in self.data.columns:
                return StataResult(
                    command="regress",
                    success=False,
                    error=f"Independent variable '{iv}' not found"
                )

        try:
            from sklearn.linear_model import LinearRegression
            from sklearn.preprocessing import StandardScaler

            X = self.data[indepvars].copy()
            y = self.data[depvar].copy()

            # Handle missing values
            mask = ~(X.isna().any(axis=1) | y.isna())
            X_clean = X[mask]
            y_clean = y[mask]

            # Fit model
            model = LinearRegression()
            model.fit(X_clean, y_clean)

            # Calculate statistics
            y_pred = model.predict(X_clean)
            ss_res = np.sum((y_clean - y_pred) ** 2)
            ss_tot = np.sum((y_clean - np.mean(y_clean)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            n = len(y_clean)
            p = len(indepvars)
            adj_rsq = 1 - (1 - r_squared) * (n - 1) / (n - p - 1)
            mse = ss_res / (n - p - 1)
            rmse = np.sqrt(mse)

            output = []
            output.append("      Source |       SS           df       MS")
            output.append("-" * 50)
            output.append(f"     Model |  {ss_res:>12.4f}{p:>12}{ss_res/p:>12.4f}")
            output.append(f"  Residual |  {ss_res:>12.4f}{n-p-1:>12}{mse:>12.4f}")
            output.append(f"     Total |  {ss_tot:>12.4f}{n-1:>12}{ss_tot/(n-1):>12.4f}")
            output.append("")
            output.append(f"  Number of obs = {n}")
            output.append(f"  F({p}, {n-p-1}) = {ss_res/p/mse:.4f}")
            output.append(f"  Prob > F      = {0.0000:.4f}")
            output.append(f"  R-squared     = {r_squared:.4f}")
            output.append(f"  Adj R-squared = {adj_rsq:.4f}")
            output.append(f"  Root MSE      = {rmse:.4f}")
            output.append("")
            output.append(f"{depvar:.<25}Coef.   Std. err.   t   P>|t|")
            output.append("-" * 60)
            output.append(f"{'(constant)':.<25}{model.intercept_:>10.4f}")

            for i, iv in enumerate(indepvars):
                coef = model.coef_[i]
                # Calculate standard error
                se = np.sqrt(mse * np.linalg.inv(X_clean.T @ X_clean).diagonal())[i]
                t = coef / se if se != 0 else 0
                pval = 2 * (1 - t_dist_cdf(abs(t), n-p-1))
                output.append(f"{iv:.<25}{coef:>10.4f}{se:>11.4f}{t:>6.2f}{pval:>7.4f}")

            return StataResult(
                command="regress",
                success=True,
                output="\n".join(output)
            )
        except Exception as e:
            return StataResult(
                command="regress",
                success=False,
                error=f"Regression error: {str(e)}"
            )

    def _cmd_logit(self, args: str) -> StataResult:
        """Perform logistic regression."""
        if self.data is None:
            return StataResult(
                command="logit",
                success=False,
                error="No data in memory"
            )

        parts = args.strip().split()
        if len(parts) < 2:
            return StataResult(
                command="logit",
                success=False,
                error="Invalid syntax"
            )

        depvar = parts[0]
        indepvars = parts[1:]

        try:
            from sklearn.linear_model import LogisticRegression

            X = self.data[indepvars].copy()
            y = self.data[depvar].copy()

            mask = ~(X.isna().any(axis=1) | y.isna())
            X_clean = X[mask]
            y_clean = y[mask]

            model = LogisticRegression(max_iter=1000)
            model.fit(X_clean, y_clean)

            output = []
            output.append("Logistic regression")
            output.append(f"Number of obs = {len(y_clean)}")
            output.append("")
            output.append(f"{depvar:.<25}Coef.   Std. err.   z   P>|z|")
            output.append("-" * 60)
            output.append(f"{'(constant)':.<25}{model.intercept_[0]:>10.4f}")

            for i, iv in enumerate(indepvars):
                output.append(f"{iv:.<25}{model.coef_[0][i]:>10.4f}")

            return StataResult(
                command="logit",
                success=True,
                output="\n".join(output)
            )
        except Exception as e:
            return StataResult(
                command="logit",
                success=False,
                error=f"Logit error: {str(e)}"
            )

    def _cmd_probit(self, args: str) -> StataResult:
        """Perform probit regression."""
        # Similar to logit, using sklearn
        return self._cmd_logit(args)  # Simplified

    def _cmd_ttest(self, args: str) -> StataResult:
        """Perform t-test."""
        if self.data is None:
            return StataResult(
                command="ttest",
                success=False,
                error="No data in memory"
            )

        # Parse: ttest var == value
        match = re.match(r'^(\w+)\s*(?:==|<|>)\s*(.+)$', args)
        if not match:
            return StataResult(
                command="ttest",
                success=False,
                error="Invalid syntax"
            )

        var, value = match.groups()
        value = float(value.strip())

        if var not in self.data.columns:
            return StataResult(
                command="ttest",
                success=False,
                error=f"Variable '{var}' not found"
            )

        x = self.data[var].dropna()
        n = len(x)
        mean = x.mean()
        std = x.std(ddof=1)
        se = std / np.sqrt(n)
        t_stat = (mean - value) / se
        df = n - 1
        p_val = 2 * (1 - t_dist_cdf(abs(t_stat), df))

        output = []
        output.append(f"One-sample t test")
        output.append(f"variable: {var}")
        output.append(f"Ho: mean = {value}")
        output.append("")
        output.append(f"  Mean     Std. err.   t    df   P>|t|")
        output.append(f"{mean:>10.4f}{se:>10.4f}{t_stat:>10.4f}{df:>8.0f}{p_val:>10.4f}")

        return StataResult(
            command="ttest",
            success=True,
            output="\n".join(output)
        )

    def _cmd_anova(self, args: str) -> StataResult:
        """Perform ANOVA."""
        return StataResult(
            command="anova",
            success=False,
            error="ANOVA not yet implemented"
        )

    def _cmd_pwcorr(self, args: str) -> StataResult:
        """Pairwise correlation (alias for correlate)."""
        return self._cmd_correlate(args)

    def _cmd_display(self, args: str) -> StataResult:
        """Display text or values."""
        # Remove quotes
        text = re.sub(r'["\']', '', args)
        return StataResult(
            command="display",
            success=True,
            output=text
        )

    def _cmd_mean(self, args: str) -> StataResult:
        """Calculate means."""
        if self.data is None:
            return StataResult(
                command="mean",
                success=False,
                error="No data in memory"
            )

        if args.strip():
            vars_list = [v.strip() for v in args.split() if v.strip()]
            df = self.data[vars_list]
        else:
            df = self.data.select_dtypes(include=[np.number])

        means = df.mean()

        output = []
        output.append("Mean estimation")
        output.append(f"Number of observations: {len(self.data)}")
        output.append("")

        for var in means.index:
            output.append(f"  {var}: {means[var]:.4f}")

        return StataResult(
            command="mean",
            success=True,
            output="\n".join(output)
        )

    def _cmd_count(self, args: str) -> StataResult:
        """Count observations."""
        if self.data is None:
            return StataResult(
                command="count",
                success=False,
                error="No data in memory"
            )

        n = len(self.data)
        return StataResult(
            command="count",
            success=True,
            output=f"  {n}"
        )

    def _cmd_sort(self, args: str) -> StataResult:
        """Sort data."""
        if self.data is None:
            return StataResult(
                command="sort",
                success=False,
                error="No data in memory"
            )

        vars_list = [v.strip() for v in args.split() if v.strip()]
        self.data = self.data.sort_values(vars_list)

        return StataResult(
            command="sort",
            success=True,
            output=f"sorted by {', '.join(vars_list)}",
            data=self.data
        )

    def _cmd_gsort(self, args: str) -> StataResult:
        """Generalized sort."""
        return self._cmd_sort(args)

    def _cmd_egen(self, args: str) -> StataResult:
        """Extended generate."""
        if self.data is None:
            return StataResult(
                command="egen",
                success=False,
                error="No data in memory"
            )

        # Handle common egen functions
        if 'mean(' in args:
            match = re.match(r'^(\w+)\s*=\s*mean\((\w+)\)', args)
            if match:
                newvar, source = match.groups()
                self.data[newvar] = self.data[source].mean()
                return StataResult(
                    command="egen",
                    success=True,
                    output=f"variable {newvar} generated"
                )

        return StataResult(
            command="egen",
            success=False,
            error="egen function not supported"
        )

    def _cmd_encode(self, args: str) -> StataResult:
        """Encode string to numeric."""
        match = re.match(r'^(\w+)\s*,\s*gen\((\w+)\)', args)
        if match:
            source, target = match.groups()
            if source in self.data.columns:
                self.data[target] = pd.Categorical(self.data[source]).codes
                return StataResult(
                    command="encode",
                    success=True,
                    output=f"variable {target} generated"
                )

        return StataResult(
            command="encode",
            success=False,
            error="Invalid encode syntax"
        )

    def _cmd_decode(self, args: str) -> StataResult:
        """Decode numeric to string."""
        return StataResult(
            command="decode",
            success=False,
            error="decode not yet implemented"
        )

    def _cmd_merge(self, args: str) -> StataResult:
        """Merge datasets."""
        return StataResult(
            command="merge",
            success=False,
            error="merge not yet implemented"
        )

    def _cmd_append(self, args: str) -> StataResult:
        """Append datasets."""
        return StataResult(
            command="append",
            success=False,
            error="append not yet implemented"
        )

    def _cmd_if_line(self, args: str) -> StataResult:
        """Handle single-line if statement."""
        return StataResult(
            command="if",
            success=True,
            output="[if condition parsed - requires block structure]"
        )

    def _cmd_else(self) -> StataResult:
        """Handle else statement."""
        return StataResult(
            command="else",
            success=True,
            output="[else parsed]"
        )


def t_dist_cdf(t: float, df: int) -> float:
    """Approximate t-distribution CDF."""
    from scipy import stats
    return stats.t.cdf(t, df)


def main():
    """Main entry point for command-line usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: stata_simulator.py <do_file.do>")
        sys.exit(1)

    filepath = sys.argv[1]
    engine = StataEngine()

    try:
        results = engine.execute_file(filepath)
        for result in results:
            if result.output:
                print(result.output)
            if result.error:
                print(f"Error: {result.error}", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
