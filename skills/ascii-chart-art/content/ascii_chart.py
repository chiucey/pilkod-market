#!/usr/bin/env python3
"""
ASCII Chart Art Generator
A powerful ASCII art chart generation tool with customizable styles and colors.

Author: MiniMax Agent
Version: 1.0.0
"""

import sys
import json
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ChartStyle:
    """Chart style configuration."""
    name: str = "classic"
    bar_chars: Tuple[str, str, str, str] = ("█", "▓", "▒", "░")
    border_chars: Dict[str, str] = field(default_factory=lambda: {
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
        "horizontal": "─",
        "vertical": "│",
        "top_t": "┬",
        "bottom_t": "┴",
        "left_t": "├",
        "right_t": "┤",
        "cross": "┼"
    })
    point_char: str = "●"
    show_grid: bool = True
    grid_char: str = "·"

    @classmethod
    def from_name(cls, name: str) -> "ChartStyle":
        """Create style from predefined styles."""
        styles = {
            "minimal": cls(
                name="minimal",
                bar_chars=("#", "#", "#", "#"),
                border_chars={
                    "top_left": "+", "top_right": "+",
                    "bottom_left": "+", "bottom_right": "+",
                    "horizontal": "-", "vertical": "|",
                    "top_t": "+", "bottom_t": "+",
                    "left_t": "+", "right_t": "+", "cross": "+"
                },
                point_char="*",
                grid_char=" "
            ),
            "classic": cls(
                name="classic",
                bar_chars=("█", "▓", "▒", "░"),
                border_chars={
                    "top_left": "┌", "top_right": "┐",
                    "bottom_left": "└", "bottom_right": "┘",
                    "horizontal": "─", "vertical": "│",
                    "top_t": "┬", "bottom_t": "┴",
                    "left_t": "├", "right_t": "┤", "cross": "┼"
                },
                point_char="●",
                show_grid=True,
                grid_char="·"
            ),
            "modern": cls(
                name="modern",
                bar_chars=("█", "▸", "▹", "░"),
                border_chars={
                    "top_left": "╔", "top_right": "╗",
                    "bottom_left": "╚", "bottom_right": "╝",
                    "horizontal": "═", "vertical": "║",
                    "top_t": "╦", "bottom_t": "╩",
                    "left_t": "╠", "right_t": "╣", "cross": "╬"
                },
                point_char="◆",
                grid_char="│"
            ),
            "bordered": cls(
                name="bordered",
                bar_chars=("█", "█", "█", "█"),
                border_chars={
                    "top_left": "┏", "top_right": "┓",
                    "bottom_left": "┗", "bottom_right": "┛",
                    "horizontal": "━", "vertical": "┃",
                    "top_t": "┳", "bottom_t": "┻",
                    "left_t": "┣", "right_t": "┫", "cross": "╋"
                },
                point_char="●",
                grid_char="┼"
            ),
            "double": cls(
                name="double",
                bar_chars=("█", "▓", "▒", "░"),
                border_chars={
                    "top_left": "╔", "top_right": "╗",
                    "bottom_left": "╚", "bottom_right": "╝",
                    "horizontal": "═", "vertical": "║",
                    "top_t": "╦", "bottom_t": "╩",
                    "left_t": "╠", "right_t": "╣", "cross": "╬"
                },
                point_char="●",
                grid_char="╪"
            ),
            "rounded": cls(
                name="rounded",
                bar_chars=("█", "▓", "▒", "░"),
                border_chars={
                    "top_left": "╭", "top_right": "╮",
                    "bottom_left": "╰", "bottom_right": "╯",
                    "horizontal": "─", "vertical": "│",
                    "top_t": "┬", "bottom_t": "┴",
                    "left_t": "├", "right_t": "┤", "cross": "┼"
                },
                point_char="●",
                grid_char="·"
            ),
            "dense": cls(
                name="dense",
                bar_chars=("█", "▓", "▒", "░"),
                border_chars={
                    "top_left": "+", "top_right": "+",
                    "bottom_left": "+", "bottom_right": "+",
                    "horizontal": "-", "vertical": "|",
                    "top_t": "+", "bottom_t": "+",
                    "left_t": "+", "right_t": "+", "cross": "+"
                },
                point_char="o",
                grid_char="."
            )
        }
        return styles.get(name, cls(name="custom"))


@dataclass
class ColorScheme:
    """ANSI color scheme for terminal output."""
    reset: str = "\033[0m"
    bold: str = "\033[1m"
    dim: str = "\033[2m"
    italic: str = "\033[3m"
    underline: str = "\033[4m"
    inverse: str = "\033[7m"

    # Foreground colors
    black: str = "\033[30m"
    red: str = "\033[31m"
    green: str = "\033[32m"
    yellow: str = "\033[33m"
    blue: str = "\033[34m"
    magenta: str = "\033[35m"
    cyan: str = "\033[36m"
    white: str = "\033[37m"

    # Bright foreground colors
    bright_black: str = "\033[90m"
    bright_red: str = "\033[91m"
    bright_green: str = "\033[92m"
    bright_yellow: str = "\033[93m"
    bright_blue: str = "\033[94m"
    bright_magenta: str = "\033[95m"
    bright_cyan: str = "\033[96m"
    bright_white: str = "\033[97m"

    # Background colors
    bg_black: str = "\033[40m"
    bg_red: str = "\033[41m"
    bg_green: str = "\033[42m"
    bg_yellow: str = "\033[43m"
    bg_blue: str = "\033[44m"
    bg_magenta: str = "\033[45m"
    bg_cyan: str = "\033[46m"
    bg_white: str = "\033[47m"

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """Get color code by name."""
        colors = {
            "black": cls.black, "red": cls.red, "green": cls.green,
            "yellow": cls.yellow, "blue": cls.blue, "magenta": cls.magenta,
            "cyan": cls.cyan, "white": cls.white,
            "bright_black": cls.bright_black, "bright_red": cls.bright_red,
            "bright_green": cls.bright_green, "bright_yellow": cls.bright_yellow,
            "bright_blue": cls.bright_blue, "bright_magenta": cls.bright_magenta,
            "bright_cyan": cls.bright_cyan, "bright_white": cls.bright_white
        }
        return colors.get(color_name.lower(), cls.white)


class ANSIFormatter:
    """Format strings with ANSI color codes."""

    def __init__(self, use_color: bool = True):
        self.use_color = use_color
        self.colors = ColorScheme()

    def colorize(self, text: str, color: str, style: str = "") -> str:
        """Add color and style to text."""
        if not self.use_color:
            return text

        color_code = ColorScheme.get_color(color)
        style_code = getattr(self.colors, style, "") if style else ""
        return f"{style_code}{color_code}{text}{self.colors.reset}"

    def bold_colorize(self, text: str, color: str) -> str:
        """Add bold color to text."""
        return self.colorize(text, color, "bold")

    def dim_colorize(self, text: str, color: str) -> str:
        """Add dim color to text."""
        return self.colorize(text, color, "dim")


class BarChart:
    """ASCII Bar Chart Generator."""

    def __init__(self, style: ChartStyle, formatter: ANSIFormatter,
                 width: int = 60, height: int = 20, horizontal: bool = False):
        self.style = style
        self.formatter = formatter
        self.width = width
        self.height = height
        self.horizontal = horizontal

    def generate(self, data: List[float], labels: List[str],
                 title: str = "", show_values: bool = True,
                 colors: Optional[List[str]] = None) -> str:
        """Generate bar chart."""
        if not data:
            return "No data provided"

        lines = []
        max_value = max(data) if data else 1
        min_value = min(data) if data else 0

        # Add title
        if title:
            lines.append(self.formatter.bold_colorize(title, "cyan"))
            lines.append("")

        # Calculate bar dimensions
        chart_height = self.height - 4  # Reserve space for labels and axis
        chart_width = self.width - 15   # Reserve space for labels

        # Generate chart based on orientation
        if self.horizontal:
            lines.extend(self._generate_horizontal(data, labels, max_value,
                                                   chart_width, show_values, colors))
        else:
            lines.extend(self._generate_vertical(data, labels, max_value, min_value,
                                                 chart_height, chart_width, show_values, colors))

        return "\n".join(lines)

    def _generate_vertical(self, data: List[float], labels: List[str],
                          max_val: float, min_val: float, chart_h: int,
                          chart_w: int, show_values: bool,
                          colors: Optional[List[str]]) -> List[str]:
        """Generate vertical bar chart."""
        lines = []
        b = self.style.border_chars

        # Determine scale
        value_range = max_val - min_val if max_val != min_val else 1
        scale = chart_h / value_range if value_range > 0 else 1

        # Find appropriate unit
        unit = self._find_nice_unit(max_val, chart_h)
        y_ticks = []
        current = 0
        while current <= max_val:
            y_ticks.append(current)
            current += unit

        # Calculate bar width
        num_bars = len(data)
        bar_width = max(1, (chart_w - num_bars) // num_bars)
        spacing = max(0, (chart_w - bar_width * num_bars) // (num_bars + 1))

        # Draw top border
        top_border = (b["top_left"] +
                     b["horizontal"] * chart_w +
                     b["top_right"])
        lines.append(top_border)

        # Draw bars from top to bottom
        for row in range(chart_h, 0, -1):
            line = b["vertical"]

            for i, value in enumerate(data):
                bar_height = int((value - min_val) * scale)
                color = colors[i] if colors and i < len(colors) else "cyan"

                if bar_height >= row:
                    bar_str = self.style.bar_chars[0] * bar_width
                    line += self.formatter.colorize(bar_str, color)
                else:
                    line += " " * bar_width

                # Add spacing
                if i < num_bars - 1:
                    line += " " * spacing

            line += b["vertical"]
            lines.append(line)

        # Draw bottom border
        bottom_border = (b["bottom_left"] +
                        b["horizontal"] * chart_w +
                        b["bottom_right"])
        lines.append(bottom_border)

        # Draw labels
        if labels:
            label_line = " " * (chart_w // 2 - sum(len(l) for l in labels) // 2)
            for i, label in enumerate(labels):
                if show_values and i < len(data):
                    label_line += f"{label}({data[i]})"
                else:
                    label_line += label
            lines.append(label_line)

        return lines

    def _generate_horizontal(self, data: List[float], labels: List[str],
                            max_val: float, chart_w: int,
                            show_values: bool,
                            colors: Optional[List[str]]) -> List[str]:
        """Generate horizontal bar chart."""
        lines = []
        b = self.style.border_chars

        max_label_len = max(len(str(l)) for l in labels) if labels else 0
        chart_area = chart_w - max_label_len - 8  # Space for value display

        for i, (value, label) in enumerate(zip(data, labels)):
            color = colors[i] if colors and i < len(colors) else "cyan"
            bar_len = int((value / max_val) * chart_area) if max_val > 0 else 0

            label_str = f"{label:>{max_label_len}} "
            bar_str = self.style.bar_chars[0] * bar_len
            value_str = f" {value}" if show_values else ""

            line = (f"{label_str}{self.formatter.colorize(bar_str, color)}"
                   f"{value_str}")
            lines.append(line)

        return lines

    def _find_nice_unit(self, max_val: float, num_ticks: int) -> float:
        """Find a nice unit for y-axis ticks."""
        rough_unit = max_val / num_ticks
        magnitude = math.pow(10, math.floor(math.log10(rough_unit)))

        for unit in [1, 2, 5, 10]:
            candidate = magnitude * unit
            if candidate >= rough_unit:
                return candidate
        return magnitude * 10


class LineChart:
    """ASCII Line Chart Generator."""

    def __init__(self, style: ChartStyle, formatter: ANSIFormatter,
                 width: int = 80, height: int = 20):
        self.style = style
        self.formatter = formatter
        self.width = width
        self.height = height

    def generate(self, datasets: List[Dict[str, Any]],
                 labels: List[str], title: str = "",
                 show_points: bool = True,
                 show_grid: bool = True) -> str:
        """Generate line chart."""
        if not datasets:
            return "No data provided"

        lines = []
        b = self.style.border_chars

        # Collect all values to determine scale
        all_values = []
        for ds in datasets:
            all_values.extend(ds.get("data", []))
        max_val = max(all_values) if all_values else 1
        min_val = min(all_values) if all_values else 0

        # Add title
        if title:
            lines.append(self.formatter.bold_colorize(title, "cyan"))
            lines.append("")

        # Calculate chart dimensions
        chart_height = self.height - 4
        chart_width = self.width - 20

        # Draw top border
        top_border = (" " * 10 + b["top_left"] +
                     b["horizontal"] * chart_width +
                     b["top_right"])
        lines.append(top_border)

        # Create grid
        value_range = max_val - min_val if max_val != min_val else 1
        scale = chart_height / value_range

        # Generate chart rows
        for row in range(chart_height, -1, -1):
            value_at_row = min_val + (row / chart_height) * value_range

            # Y-axis label
            if row == chart_height:
                y_label = f"{max_val:>10.1f}"
            elif row == 0:
                y_label = f"{min_val:>10.1f}"
            elif row == chart_height // 2:
                y_label = f"{(max_val + min_val) / 2:>10.1f}"
            else:
                y_label = " " * 10

            line = y_label + b["vertical"]

            # Calculate x positions for each data point
            num_points = len(labels)
            x_step = chart_width / max(1, num_points - 1) if num_points > 1 else 0

            for col in range(chart_width):
                char = " "
                for ds in datasets:
                    data = ds.get("data", [])
                    color = ds.get("color", "cyan")

                    if len(data) >= num_points:
                        for p in range(len(data) - 1):
                            x1 = int(p * x_step)
                            x2 = int((p + 1) * x_step)
                            y1 = int((data[p] - min_val) * scale)
                            y2 = int((data[p + 1] - min_val) * scale)

                            if col == x1 and row == y1:
                                char = self.formatter.colorize(
                                    self.style.point_char, color)
                            elif col == x2 and row == y2:
                                char = self.formatter.colorize(
                                    self.style.point_char, color)
                            elif x1 <= col <= x2:
                                if x1 == x2:
                                    if row == y1:
                                        char = self.formatter.colorize(
                                            self.style.bar_chars[0], color)
                                else:
                                    interp_y = y1 + (y2 - y1) * (col - x1) / (x2 - x1)
                                    if abs(interp_y - row) < 0.5:
                                        char = self.formatter.colorize(
                                            self.style.bar_chars[0], color)

                line += char

            line += b["vertical"]
            lines.append(line)

        # Draw bottom border
        bottom_border = (" " * 10 + b["bottom_left"] +
                        b["horizontal"] * chart_width +
                        b["bottom_right"])
        lines.append(bottom_border)

        # X-axis labels
        x_labels = " " * 10 + b["vertical"]
        label_step = max(1, len(labels) // min(10, len(labels)))
        for i, label in enumerate(labels):
            if i % label_step == 0 or i == len(labels) - 1:
                x_labels += f"{label:^{chart_width // min(10, len(labels))}}"
        x_labels += b["vertical"]
        lines.append(x_labels)

        # Legend
        if len(datasets) > 1:
            legend = "Legend: "
            for ds in datasets:
                name = ds.get("name", "Data")
                color = ds.get("color", "cyan")
                legend += self.formatter.colorize(
                    f"[{self.style.point_char}{name}] ", color)
            lines.append(legend)

        return "\n".join(lines)


class PieChart:
    """ASCII Pie Chart (text representation)."""

    def __init__(self, style: ChartStyle, formatter: ANSIFormatter):
        self.style = style
        self.formatter = formatter

    def generate(self, data: List[Dict[str, Any]], title: str = "") -> str:
        """Generate text-based pie chart."""
        if not data:
            return "No data provided"

        lines = []

        # Add title
        if title:
            lines.append(self.formatter.bold_colorize(title, "cyan"))
            lines.append("")

        # Calculate total and percentages
        values = [d.get("value", 0) for d in data]
        total = sum(values)
        if total == 0:
            return "No data to display"

        # Create pie segments using block characters
        segments = []
        for item in data:
            value = item.get("value", 0)
            name = item.get("name", "Unknown")
            color = item.get("color", "cyan")
            percentage = (value / total) * 100

            # Create visual bar representation
            bar_length = int(percentage / 2)
            bar = self.style.bar_chars[0] * bar_length

            segment = {
                "name": name,
                "value": value,
                "percentage": percentage,
                "bar": self.formatter.colorize(bar, color),
                "color": color
            }
            segments.append(segment)

        # Sort by value (largest first)
        segments.sort(key=lambda x: x["value"], reverse=True)

        # Draw pie circle (simplified ASCII representation)
        lines.append("    ┌─────────────────┐")

        # Create circular layout
        radius = 5
        for row in range(-radius, radius + 1):
            line = "   │"
            width = int(math.sqrt(radius * radius - row * row) + 0.5)
            line += " " * (radius - width) + "●" * (width * 2) + " " * (radius - width)
            line += "│"
            lines.append(line)

        lines.append("    └─────────────────┘")

        # Legend with bars
        lines.append("")
        for seg in segments:
            legend_line = (f"  {seg['bar']} {seg['name']}: "
                          f"{seg['percentage']:.1f}% ({seg['value']})")
            lines.append(legend_line)

        return "\n".join(lines)


class HistogramChart:
    """ASCII Histogram Chart."""

    def __init__(self, style: ChartStyle, formatter: ANSIFormatter,
                 width: int = 60, height: int = 15):
        self.style = style
        self.formatter = formatter
        self.width = width
        self.height = height

    def generate(self, data: List[float], bins: int = 10,
                title: str = "") -> str:
        """Generate histogram."""
        if not data:
            return "No data provided"

        lines = []
        b = self.style.border_chars

        # Add title
        if title:
            lines.append(self.formatter.bold_colorize(title, "cyan"))
            lines.append("")

        # Calculate histogram bins
        min_val = min(data)
        max_val = max(data)
        bin_width = (max_val - min_val) / bins if bins > 0 else 1

        bin_counts = [0] * bins
        for value in data:
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            bin_counts[bin_idx] += 1

        max_count = max(bin_counts) if bin_counts else 1
        chart_height = self.height - 4

        # Draw histogram
        for row in range(chart_height, -1, -1):
            count_at_row = int((row / chart_height) * max_count)

            line = b["vertical"]
            for count in bin_counts:
                if count >= count_at_row:
                    line += self.style.bar_chars[0]
                else:
                    line += " "
            line += b["vertical"]
            lines.append(line)

        # Draw baseline
        baseline = b["bottom_left"] + b["horizontal"] * bins + b["bottom_right"]
        lines.append(baseline)

        # Bin labels
        bin_labels = ""
        for i in range(bins):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            label = f"{bin_start:.0f}-{bin_end:.0f}"
            bin_labels += f"{label:^{bins}}"

        lines.append(bin_labels)

        # Stats
        mean = sum(data) / len(data)
        lines.append(f"Mean: {mean:.2f} | Total: {len(data)} | Bins: {bins}")

        return "\n".join(lines)


class ScatterPlot:
    """ASCII Scatter Plot."""

    def __init__(self, style: ChartStyle, formatter: ANSIFormatter,
                 width: int = 60, height: int = 20):
        self.style = style
        self.formatter = formatter
        self.width = width
        self.height = height

    def generate(self, points: List[Tuple[float, float]],
                title: str = "",
                x_label: str = "X", y_label: str = "Y") -> str:
        """Generate scatter plot."""
        if not points:
            return "No data provided"

        lines = []
        b = self.style.border_chars

        # Add title
        if title:
            lines.append(self.formatter.bold_colorize(title, "cyan"))
            lines.append(f"X-axis: {x_label} | Y-axis: {y_label}")
            lines.append("")

        # Calculate ranges
        x_vals = [p[0] for p in points]
        y_vals = [p[1] for p in points]
        x_min, x_max = min(x_vals), max(x_vals)
        y_min, y_max = min(y_vals), max(y_vals)

        # Normalize points to grid
        chart_width = self.width - 15
        chart_height = self.height - 5

        normalized_points = []
        for x, y in points:
            nx = int(((x - x_min) / (x_max - x_min)) * (chart_width - 1)) if x_max != x_min else 0
            ny = int(((y - y_min) / (y_max - y_min)) * (chart_height - 1)) if y_max != y_min else 0
            normalized_points.append((nx, ny))

        # Draw scatter plot
        for row in range(chart_height - 1, -1, -1):
            if row == chart_height - 1:
                y_label_str = f"{y_max:>6.1f}"
            elif row == 0:
                y_label_str = f"{y_min:>6.1f}"
            else:
                y_label_str = " " * 6

            line = y_label_str + b["vertical"]

            for col in range(chart_width):
                char = " "
                for px, py in normalized_points:
                    if px == col and py == row:
                        char = self.formatter.colorize(
                            self.style.point_char, "cyan")
                        break
                line += char

            line += b["vertical"]
            lines.append(line)

        # Draw bottom
        x_axis = " " * 6 + b["bottom_left"] + b["horizontal"] * chart_width + b["bottom_right"]
        lines.append(x_axis)

        # X-axis labels
        x_axis_label = " " * 6 + " " + f"{x_min:.1f}" + " " * (chart_width - 12) + f"{x_max:.1f}"
        lines.append(x_axis_label)

        return "\n".join(lines)


class StackedChart:
    """ASCII Stacked Bar Chart."""

    def __init__(self, style: ChartStyle, formatter: ANSIFormatter,
                 width: int = 60, height: int = 20):
        self.style = style
        self.formatter = formatter
        self.width = width
        self.height = height

    def generate(self, datasets: List[Dict[str, Any]],
                 labels: List[str], title: str = "") -> str:
        """Generate stacked bar chart."""
        if not datasets:
            return "No data provided"

        lines = []
        b = self.style.border_chars

        # Add title
        if title:
            lines.append(self.formatter.bold_colorize(title, "cyan"))
            lines.append("")

        # Calculate totals and max
        totals = []
        for i in range(len(labels)):
            total = sum(ds.get("data", [0])[i] if i < len(ds.get("data", [])) else 0
                       for ds in datasets)
            totals.append(total)

        max_total = max(totals) if totals else 1
        chart_height = self.height - 4
        chart_width = self.width - 15

        # Color cycle for datasets
        colors = ["cyan", "green", "yellow", "magenta", "red", "blue"]
        for ds in datasets:
            if "color" not in ds:
                idx = datasets.index(ds) % len(colors)
                ds["color"] = colors[idx]

        # Draw stacked bars
        for label_idx, label in enumerate(labels):
            bar_str = f"{label:>10} "

            # Calculate stacked height
            current_height = 0
            for ds in datasets:
                data = ds.get("data", [])
                value = data[label_idx] if label_idx < len(data) else 0
                seg_height = int((value / max_total) * chart_height) if max_total > 0 else 0

                color = ds.get("color", "cyan")
                bar_str += self.formatter.colorize(
                    self.style.bar_chars[0] * seg_height, color)
                current_height = max(current_height, seg_height)

            total = totals[label_idx]
            bar_str += f" {total}"
            lines.append(bar_str)

        # Legend
        legend = "Legend: "
        for ds in datasets:
            name = ds.get("name", "Data")
            color = ds.get("color", "cyan")
            legend += self.formatter.colorize(f"[{name}] ", color)
        lines.append("")
        lines.append(legend)

        return "\n".join(lines)


class BoxPlot:
    """ASCII Box Plot (Statistical Distribution)."""

    def __init__(self, style: ChartStyle, formatter: ANSIFormatter,
                 width: int = 80):
        self.style = style
        self.formatter = formatter
        self.width = width

    def generate(self, datasets: List[Dict[str, Any]], title: str = "") -> str:
        """Generate box plot."""
        if not datasets:
            return "No data provided"

        lines = []
        b = self.style.border_chars

        # Add title
        if title:
            lines.append(self.formatter.bold_colorize(title, "cyan"))
            lines.append("")

        chart_width = self.width - 20

        for ds in datasets:
            name = ds.get("name", "Data")
            data = sorted(ds.get("data", []))
            color = ds.get("color", "cyan")

            if len(data) < 5:
                lines.append(f"{name}: Not enough data points (need at least 5)")
                continue

            # Calculate statistics
            q1 = data[int(len(data) * 0.25)]
            median = data[int(len(data) * 0.5)]
            q3 = data[int(len(data) * 0.75)]
            iqr = q3 - q1
            whiskers_low = max(data[0], q1 - 1.5 * iqr)
            whiskers_high = min(data[-1], q3 + 1.5 * iqr)

            # Create visualization
            scale = chart_width / (whiskers_high - whiskers_low) if whiskers_high != whiskers_low else 1

            def to_pos(val):
                return int((val - whiskers_low) * scale)

            line = f"{name:>15} "

            # Whisker low
            line += self.formatter.colorize("─" * to_pos(whiskers_low), color)
            # Box
            box_start = to_pos(q1)
            box_end = to_pos(q3)
            line += self.formatter.colorize("├", color)
            line += self.formatter.colorize("█" * (box_end - box_start), color)
            line += self.formatter.colorize("┤", color)
            # Whisker high
            line += self.formatter.colorize("─" * (chart_width - to_pos(whiskers_high)), color)

            # Labels
            line += f"  [{whiskers_low:.1f} - {whiskers_high:.1f}]"
            lines.append(line)

            # Median marker
            median_pos = to_pos(median)
            median_line = " " * (16 + median_pos) + "◆" + f" Median: {median:.1f}"
            lines.append(self.formatter.colorize(median_line, color))

        # Legend
        lines.append("")
        lines.append("Legend: ─── Whiskers | ████ IQR (Q1-Q3) | ◆ Median")

        return "\n".join(lines)


class ASCIIChartArt:
    """Main ASCII Chart Art Generator class."""

    CHART_TYPES = ["bar", "line", "pie", "histogram", "scatter", "stacked", "boxplot"]

    def __init__(self, style_name: str = "classic", use_color: bool = True):
        self.style = ChartStyle.from_name(style_name)
        self.formatter = ANSIFormatter(use_color)
        self.chart_width = 60
        self.chart_height = 20
        self.horizontal = False

    def set_dimensions(self, width: int, height: int):
        """Set chart dimensions."""
        self.chart_width = min(width, 200)
        self.chart_height = min(height, 50)
        return self

    def set_horizontal(self, horizontal: bool = True):
        """Set horizontal orientation for bar charts."""
        self.horizontal = horizontal
        return self

    def generate(self, chart_type: str, **kwargs) -> str:
        """Generate chart based on type."""
        chart_type = chart_type.lower()

        if chart_type == "bar":
            chart = BarChart(self.style, self.formatter,
                           self.chart_width, self.chart_height,
                           self.horizontal)
            return chart.generate(
                data=kwargs.get("data", []),
                labels=kwargs.get("labels", []),
                title=kwargs.get("title", ""),
                show_values=kwargs.get("show_values", True),
                colors=kwargs.get("colors")
            )

        elif chart_type == "line":
            chart = LineChart(self.style, self.formatter,
                             self.chart_width, self.chart_height)
            return chart.generate(
                datasets=kwargs.get("datasets", []),
                labels=kwargs.get("labels", []),
                title=kwargs.get("title", ""),
                show_points=kwargs.get("show_points", True),
                show_grid=kwargs.get("show_grid", True)
            )

        elif chart_type == "pie":
            chart = PieChart(self.style, self.formatter)
            return chart.generate(
                data=kwargs.get("data", []),
                title=kwargs.get("title", "")
            )

        elif chart_type == "histogram":
            chart = HistogramChart(self.style, self.formatter,
                                  self.chart_width, self.chart_height)
            return chart.generate(
                data=kwargs.get("data", []),
                bins=kwargs.get("bins", 10),
                title=kwargs.get("title", "")
            )

        elif chart_type == "scatter":
            chart = ScatterPlot(self.style, self.formatter,
                               self.chart_width, self.chart_height)
            return chart.generate(
                points=kwargs.get("points", []),
                title=kwargs.get("title", ""),
                x_label=kwargs.get("x_label", "X"),
                y_label=kwargs.get("y_label", "Y")
            )

        elif chart_type == "stacked":
            chart = StackedChart(self.style, self.formatter,
                                self.chart_width, self.chart_height)
            return chart.generate(
                datasets=kwargs.get("datasets", []),
                labels=kwargs.get("labels", []),
                title=kwargs.get("title", "")
            )

        elif chart_type == "boxplot":
            chart = BoxPlot(self.style, self.formatter, self.chart_width)
            return chart.generate(
                datasets=kwargs.get("datasets", []),
                title=kwargs.get("title", "")
            )

        else:
            return f"Unknown chart type: {chart_type}. Available types: {', '.join(self.CHART_TYPES)}"

    def list_styles(self) -> str:
        """List available styles."""
        styles = ["minimal", "classic", "modern", "bordered", "double", "rounded", "dense"]
        return "Available styles: " + ", ".join(styles)

    def list_chart_types(self) -> str:
        """List available chart types."""
        return "Available chart types: " + ", ".join(self.CHART_TYPES)


def main():
    """Main function for CLI usage."""
    if len(sys.argv) < 2:
        print("ASCII Chart Art Generator")
        print("Usage: python ascii_chart.py <command> [options]")
        print("")
        print("Commands:")
        print("  bar        - Generate bar chart")
        print("  line       - Generate line chart")
        print("  pie        - Generate pie chart")
        print("  histogram  - Generate histogram")
        print("  scatter    - Generate scatter plot")
        print("  stacked    - Generate stacked bar chart")
        print("  boxplot    - Generate box plot")
        print("  list       - List available styles and chart types")
        print("")
        print("Examples:")
        print('  python ascii_chart.py bar --data "[10,20,30,40,50]" --labels "Jan,Feb,Mar,Apr,May"')
        print('  python ascii_chart.py line --datasets \'[{"name":"Sales","data":[10,20,30],"color":"cyan"}]\' --labels "Q1,Q2,Q3"')
        return

    generator = ASCIIChartArt(use_color=True)

    command = sys.argv[1].lower()

    if command == "list":
        print(generator.list_styles())
        print(generator.list_chart_types())
        return

    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="ASCII Chart Art Generator")

    if command == "bar":
        parser.add_argument("--data", required=True, help="Comma-separated values")
        parser.add_argument("--labels", required=True, help="Comma-separated labels")
        parser.add_argument("--title", default="", help="Chart title")
        parser.add_argument("--horizontal", action="store_true", help="Horizontal bars")
        parser.add_argument("--style", default="classic", help="Chart style")
        args = parser.parse_args(sys.argv[2:])

        generator.style = ChartStyle.from_name(args.style)
        generator.set_horizontal(args.horizontal)

        data = [float(x.strip()) for x in args.data.strip("[]").split(",")]
        labels = [x.strip() for x in args.labels.strip("[]").split(",")]

        print(generator.generate("bar", data=data, labels=labels, title=args.title))

    elif command == "line":
        parser.add_argument("--datasets", required=True, help="JSON array of datasets")
        parser.add_argument("--labels", required=True, help="Comma-separated labels")
        parser.add_argument("--title", default="", help="Chart title")
        parser.add_argument("--style", default="classic", help="Chart style")
        args = parser.parse_args(sys.argv[2:])

        generator.style = ChartStyle.from_name(args.style)
        datasets = json.loads(args.datasets)
        labels = [x.strip() for x in args.labels.strip("[]").split(",")]

        print(generator.generate("line", datasets=datasets, labels=labels, title=args.title))

    elif command == "pie":
        parser.add_argument("--data", required=True, help="JSON array of pie segments")
        parser.add_argument("--title", default="", help="Chart title")
        parser.add_argument("--style", default="classic", help="Chart style")
        args = parser.parse_args(sys.argv[2:])

        generator.style = ChartStyle.from_name(args.style)
        data = json.loads(args.data)

        print(generator.generate("pie", data=data, title=args.title))

    elif command == "histogram":
        parser.add_argument("--data", required=True, help="Comma-separated values")
        parser.add_argument("--bins", type=int, default=10, help="Number of bins")
        parser.add_argument("--title", default="", help="Chart title")
        parser.add_argument("--style", default="classic", help="Chart style")
        args = parser.parse_args(sys.argv[2:])

        generator.style = ChartStyle.from_name(args.style)
        data = [float(x.strip()) for x in args.data.strip("[]").split(",")]

        print(generator.generate("histogram", data=data, bins=args.bins, title=args.title))

    elif command == "scatter":
        parser.add_argument("--points", required=True, help="JSON array of (x,y) tuples")
        parser.add_argument("--title", default="", help="Chart title")
        parser.add_argument("--x-label", default="X", help="X-axis label")
        parser.add_argument("--y-label", default="Y", help="Y-axis label")
        parser.add_argument("--style", default="classic", help="Chart style")
        args = parser.parse_args(sys.argv[2:])

        generator.style = ChartStyle.from_name(args.style)
        points = json.loads(args.points)

        print(generator.generate("scatter", points=points, title=args.title,
                                x_label=args.x_label, y_label=args.y_label))

    elif command == "stacked":
        parser.add_argument("--datasets", required=True, help="JSON array of datasets")
        parser.add_argument("--labels", required=True, help="Comma-separated labels")
        parser.add_argument("--title", default="", help="Chart title")
        parser.add_argument("--style", default="classic", help="Chart style")
        args = parser.parse_args(sys.argv[2:])

        generator.style = ChartStyle.from_name(args.style)
        datasets = json.loads(args.datasets)
        labels = [x.strip() for x in args.labels.strip("[]").split(",")]

        print(generator.generate("stacked", datasets=datasets, labels=labels, title=args.title))

    elif command == "boxplot":
        parser.add_argument("--datasets", required=True, help="JSON array of datasets")
        parser.add_argument("--title", default="", help="Chart title")
        parser.add_argument("--style", default="classic", help="Chart style")
        args = parser.parse_args(sys.argv[2:])

        generator.style = ChartStyle.from_name(args.style)
        datasets = json.loads(args.datasets)

        print(generator.generate("boxplot", datasets=datasets, title=args.title))

    else:
        print(f"Unknown command: {command}")
        print("Run 'python ascii_chart.py list' for available commands")


if __name__ == "__main__":
    main()
