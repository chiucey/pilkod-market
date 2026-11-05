"""
ASCII Chart Generator
Generates ASCII/Unicode art charts with customizable styles and colors.
"""

from typing import List, Dict, Optional, Tuple
from enum import Enum


class StylePreset(Enum):
    SIMPLE = "simple"
    CLASSIC = "classic"
    MODERN = "modern"
    DOUBLE = "double"
    MINIMAL = "minimal"


class ColorMode(Enum):
    NONE = "none"
    ANSI16 = "ansi16"
    ANSI256 = "ansi256"
    TRUECOLOR = "truecolor"


class ChartType(Enum):
    BAR = "bar"
    LINE = "line"
    PIE = "pie"


# ANSI Color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    @staticmethod
    def truecolor(r: int, g: int, b: int) -> str:
        """Generate truecolor ANSI code"""
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def truecolor_bg(r: int, g: int, b: int) -> str:
        """Generate truecolor background ANSI code"""
        return f"\033[48;2;{r};{g};{b}m"


# Style configurations
STYLE_BORDERS = {
    StylePreset.SIMPLE: {
        "top": "+{}-+",
        "bottom": "+{}-+",
        "side": "|{}|",
        "corner_tl": "+",
        "corner_tr": "+",
        "corner_bl": "+",
        "corner_br": "+",
        "hline": "-",
        "vline": "|",
    },
    StylePreset.CLASSIC: {
        "top": "+-{}-+",
        "bottom": "+-{}-+",
        "side": "| {} |",
        "corner_tl": "+",
        "corner_tr": "+",
        "corner_bl": "+",
        "corner_br": "+",
        "hline": "-",
        "vline": "|",
    },
    StylePreset.MODERN: {
        "top": "┌{}┐",
        "bottom": "└{}┘",
        "side": "│ {} │",
        "corner_tl": "┌",
        "corner_tr": "┐",
        "corner_bl": "└",
        "corner_br": "┘",
        "hline": "─",
        "vline": "│",
    },
    StylePreset.DOUBLE: {
        "top": "╔{}╗",
        "bottom": "╚{}╝",
        "side": "║ {} ║",
        "corner_tl": "╔",
        "corner_tr": "╗",
        "corner_bl": "╚",
        "corner_br": "╝",
        "hline": "═",
        "vline": "║",
    },
    StylePreset.MINIMAL: {
        "top": "{}",
        "bottom": "{}",
        "side": " {} ",
        "corner_tl": "",
        "corner_tr": "",
        "corner_bl": "",
        "corner_br": "",
        "hline": "",
        "vline": "",
    },
}

# Fill characters for different styles
STYLE_FILLS = {
    StylePreset.SIMPLE: "█",
    StylePreset.CLASSIC: "#",
    StylePreset.MODERN: "█",
    StylePreset.DOUBLE: "█",
    StylePreset.MINIMAL: "▓",
}


def get_color(color_mode: ColorMode, color: str = Colors.GREEN) -> str:
    """Get color code based on color mode"""
    if color_mode == ColorMode.NONE:
        return ""
    return color


def colorize(text: str, color: str, color_mode: ColorMode) -> str:
    """Apply color to text"""
    if color_mode == ColorMode.NONE:
        return text
    return f"{color}{text}{Colors.RESET}"


class BarChart:
    """ASCII Bar Chart Generator"""

    def __init__(
        self,
        data: Dict[str, float],
        title: str = "",
        width: int = 40,
        height: int = 10,
        style: StylePreset = StylePreset.MODERN,
        color_mode: ColorMode = ColorMode.NONE,
        bar_color: str = Colors.GREEN,
        show_values: bool = True,
        show_labels: bool = True,
    ):
        self.data = data
        self.title = title
        self.width = width
        self.height = height
        self.style = style
        self.color_mode = color_mode
        self.bar_color = bar_color
        self.show_values = show_values
        self.show_labels = show_labels
        self.fill_char = STYLE_FILLS[style]
        self.borders = STYLE_BORDERS[style]

    def generate(self) -> str:
        """Generate the bar chart"""
        lines = []

        # Title
        if self.title:
            lines.append(self._center_text(self.title))

        # Data preparation
        labels = list(self.data.keys())
        values = list(self.data.values())
        max_value = max(values) if values else 1
        max_label_len = max(len(str(l)) for l in labels) if labels else 10

        # Header line
        border_width = self.width + max_label_len + 2
        top_border = self.borders["top"].format(self.hline(border_width))
        lines.append(top_border)

        # Chart area
        for label, value in zip(labels, values):
            bar_len = int((value / max_value) * self.width) if max_value > 0 else 0
            bar = self.fill_char * bar_len

            if self.show_labels:
                label_str = f"{str(label):<{max_label_len}} "
            else:
                label_str = " " * (max_label_len + 1)

            bar_str = colorize(bar, self.bar_color, self.color_mode)

            if self.show_values:
                value_str = f" {value}"
            else:
                value_str = ""

            line = self.borders["side"].format(label_str + bar_str + value_str)
            lines.append(line)

        # Bottom border
        bottom_border = self.borders["bottom"].format(self.hline(border_width))
        lines.append(bottom_border)

        return "\n".join(lines)

    def hline(self, length: int) -> str:
        """Generate horizontal line"""
        return self.borders["hline"] * length

    def _center_text(self, text: str) -> str:
        """Center text"""
        width = self.width + 20
        return text.center(width)


class LineChart:
    """ASCII Line Chart Generator"""

    def __init__(
        self,
        data: Dict[str, List[float]],
        title: str = "",
        width: int = 50,
        height: int = 15,
        style: StylePreset = StylePreset.MODERN,
        color_mode: ColorMode = ColorMode.NONE,
        show_points: bool = True,
        show_grid: bool = True,
    ):
        self.data = data
        self.title = title
        self.width = width
        self.height = height
        self.style = style
        self.color_mode = color_mode
        self.show_points = show_points
        self.show_grid = show_grid
        self.borders = STYLE_BORDERS[style]

        # Series colors
        self.series_colors = [
            Colors.RED,
            Colors.GREEN,
            Colors.BLUE,
            Colors.YELLOW,
            Colors.MAGENTA,
            Colors.CYAN,
        ]

    def generate(self) -> str:
        """Generate the line chart"""
        lines = []

        # Title
        if self.title:
            lines.append(self._center_text(self.title))

        # Find data range
        all_values = [v for series in self.data.values() for v in series]
        max_value = max(all_values) if all_values else 10
        min_value = min(all_values) if all_values else 0
        max_value = max_value * 1.1  # Add padding

        # Labels (x-axis)
        labels = list(self.data.keys())
        num_points = len(labels)
        x_step = self.width / max(num_points - 1, 1) if num_points > 1 else self.width

        # Build chart grid
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        # Plot each series
        for series_idx, (series_name, values) in enumerate(self.data.items()):
            color = self.series_colors[series_idx % len(self.series_colors)]

            for point_idx, value in enumerate(values):
                # Calculate position with bounds checking
                x = int(point_idx * x_step)
                x = max(0, min(self.width - 1, x))  # Ensure x is within grid bounds
                y = int((1 - value / max_value) * (self.height - 1))
                y = max(0, min(self.height - 1, y))  # Ensure y is within grid bounds

                marker = "●" if self.show_points else "●"
                grid[y][x] = colorize(marker, color, self.color_mode)

        # Draw grid with Y-axis
        y_labels = [max_value - (max_value / self.height) * i for i in range(self.height + 1)]

        for i in range(self.height - 1, -1, -1):
            y_label = f"{y_labels[i]:>6.1f}"
            row = "".join(grid[i])

            if self.show_grid:
                # Add grid lines
                grid_line = ""
                for j, char in enumerate(row):
                    if char == " " and j > 0:
                        grid_line += "·"
                    else:
                        grid_line += char
                row = grid_line

            lines.append(f"{y_label} │{row}")

        # X-axis
        x_axis_len = self.width + 1
        x_axis = "─" * x_axis_len
        x_axis_line = "       " + self.borders["corner_bl"] + x_axis + self.borders["corner_br"]

        # X-axis labels
        x_labels = ""
        if labels:
            label_step = max(1, len(labels) // min(len(labels), 8))
            for i in range(0, len(labels), label_step):
                x_labels += f"{labels[i][:8]:^8}"
        lines.append(x_axis_line)

        # Legend
        if len(self.data) > 1:
            legend_items = []
            for idx, (series_name, _) in enumerate(self.data.items()):
                color = self.series_colors[idx % len(self.series_colors)]
                legend_items.append(colorize(f"● {series_name}", color, self.color_mode))
            lines.append("       " + "  ".join(legend_items))

        return "\n".join(lines)

    def _center_text(self, text: str) -> str:
        """Center text"""
        width = self.width + 20
        return text.center(width)


class PieChart:
    """ASCII Pie Chart Generator"""

    def __init__(
        self,
        data: Dict[str, float],
        title: str = "",
        style: StylePreset = StylePreset.MODERN,
        color_mode: ColorMode = ColorMode.NONE,
        show_legend: bool = True,
    ):
        self.data = data
        self.title = title
        self.style = style
        self.color_mode = color_mode
        self.show_legend = show_legend

        # Segment colors
        self.segment_colors = [
            Colors.RED,
            Colors.GREEN,
            Colors.BLUE,
            Colors.YELLOW,
            Colors.MAGENTA,
            Colors.CYAN,
        ]

        # Block characters for pie segments
        self.blocks = ["▓", "▒", "░"]

    def generate(self) -> str:
        """Generate the pie chart"""
        lines = []

        # Title
        if self.title:
            lines.append(self._center_text(self.title))

        # Calculate percentages
        total = sum(self.data.values())
        if total == 0:
            return "No data to display"

        items = []
        for label, value in self.data.items():
            percentage = (value / total) * 100
            items.append((label, value, percentage))

        # Sort by size
        items.sort(key=lambda x: x[2], reverse=True)

        # Draw pie (simplified ASCII representation)
        lines.append(self._center_text("┌─────────────────┐"))
        lines.append(self._center_text("│      PIE        │"))

        # Simple pie representation
        pie_row1 = "│  ▓▓▓   " + items[0][0][:6] if items else "│           │"
        lines.append(self._center_text(pie_row1))

        if len(items) > 1:
            pie_row2 = f"│ {'▓' * len(items[1][0][:4])} {items[1][0][:6]}|"
            lines.append(self._center_text(pie_row2))

        lines.append(self._center_text("└─────────────────┘"))

        # Legend
        if self.show_legend:
            lines.append("")
            legend_items = []
            for idx, (label, value, pct) in enumerate(items):
                color = self.segment_colors[idx % len(self.segment_colors)]
                legend_line = colorize(f"■ {label}: {pct:.1f}%", color, self.color_mode)
                legend_items.append(legend_line)

            lines.append("  ".join(legend_items))

        return "\n".join(lines)

    def _center_text(self, text: str) -> str:
        """Center text"""
        width = 35
        return text.center(width)


def generate_chart(
    data: Dict[str, float],
    chart_type: str = "bar",
    title: str = "",
    style: str = "modern",
    color_mode: str = "none",
    show_values: bool = True,
    **kwargs,
) -> str:
    """
    Main function to generate ASCII charts.

    Args:
        data: Dictionary of labels to values
        chart_type: "bar", "line", or "pie"
        title: Chart title
        style: "simple", "classic", "modern", "double", or "minimal"
        color_mode: "none", "ansi16", "ansi256", or "truecolor"
        show_values: Whether to show numeric values
        **kwargs: Additional options per chart type

    Returns:
        ASCII chart string
    """
    # Parse style
    try:
        style_preset = StylePreset(style.lower())
    except ValueError:
        style_preset = StylePreset.MODERN

    # Parse color mode
    try:
        color = ColorMode(color_mode.lower())
    except ValueError:
        color = ColorMode.NONE

    # Parse chart type
    try:
        chart = ChartType(chart_type.lower())
    except ValueError:
        chart = ChartType.BAR

    if chart == ChartType.BAR:
        generator = BarChart(
            data=data,
            title=title,
            style=style_preset,
            color_mode=color,
            show_values=show_values,
            **kwargs,
        )
    elif chart == ChartType.LINE:
        generator = LineChart(
            data=data,
            title=title,
            style=style_preset,
            color_mode=color,
            **kwargs,
        )
    elif chart == ChartType.PIE:
        generator = PieChart(
            data=data,
            title=title,
            style=style_preset,
            color_mode=color,
            **kwargs,
        )
    else:
        return "Unsupported chart type"

    return generator.generate()


# Demo function
def demo():
    """Demo of all chart types"""
    print("=" * 60)
    print("ASCII Chart Generator Demo")
    print("=" * 60)

    # Bar Chart Demo
    print("\n1. BAR CHART (Modern Style)")
    print("-" * 40)
    bar_data = {
        "Jan": 100,
        "Feb": 150,
        "Mar": 120,
        "Apr": 180,
        "May": 200,
    }
    print(generate_chart(bar_data, "bar", "Monthly Sales", style="modern"))

    # Bar Chart with colors
    print("\n2. BAR CHART (Classic Style with Colors)")
    print("-" * 40)
    print(generate_chart(bar_data, "bar", "Monthly Sales", style="classic", color_mode="ansi16"))

    # Line Chart Demo
    print("\n3. LINE CHART")
    print("-" * 40)
    line_data = {
        "Series A": [10, 30, 20, 50, 40, 60],
        "Series B": [20, 15, 35, 25, 45, 55],
    }
    print(generate_chart(line_data, "line", "Performance", style="modern"))

    # Pie Chart Demo
    print("\n4. PIE CHART")
    print("-" * 40)
    pie_data = {
        "Product A": 35,
        "Product B": 45,
        "Product C": 20,
    }
    print(generate_chart(pie_data, "pie", "Sales Distribution", style="modern"))


if __name__ == "__main__":
    demo()
