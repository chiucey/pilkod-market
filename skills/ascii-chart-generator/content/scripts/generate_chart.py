#!/usr/bin/env python3
"""
ASCII Chart Generator - Core chart generation engine
Supports: bar, hbar, line, pie, stacked, area charts
"""

import math
from typing import List, Dict, Optional, Union, Tuple


class ASCIIChartGenerator:
    """ASCII Art Chart Generator with customizable styles and colors"""

    # Style character sets
    STYLES = {
        'simple': {
            'h': '-', 'v': '|', 'dot': '*',
            'bar': '#', 'space': ' ',
            'tl': '+', 'tr': '+', 'bl': '+', 'br': '+',
            'lt': '+', 'rt': '+', 'mt': '+', 'mb': '+', 'mv': '+',
            'lm': '+', 'rm': '+', 'mm': '+',
        },
        'elegant': {
            'h': '─', 'v': '│', 'dot': '●',
            'bar': '█', 'space': ' ',
            'tl': '┌', 'tr': '┐', 'bl': '└', 'br': '┘',
            'lt': '├', 'rt': '┤', 'mt': '┬', 'mb': '┴', 'mv': '┼',
            'lm': '├', 'rm': '┤', 'mm': '┼',
        },
        'compact': {
            'h': '━', 'v': '┃', 'dot': '●',
            'bar': '▓', 'space': ' ',
            'tl': '┏', 'tr': '┓', 'bl': '┗', 'br': '┛',
            'lt': '┣', 'rt': '┫', 'mt': '┳', 'mb': '┻', 'mv': '╋',
            'lm': '┣', 'rm': '┫', 'mm': '╋',
        },
        'rounded': {
            'h': '─', 'v': '│', 'dot': '●',
            'bar': '█', 'space': ' ',
            'tl': '╭', 'tr': '╮', 'bl': '╰', 'br': '╯',
            'lt': '├', 'rt': '┤', 'mt': '┬', 'mb': '┴', 'mv': '┼',
            'lm': '├', 'rm': '┤', 'mm': '┼',
        }
    }

    # ANSI color codes
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        # Dark variants
        'dark_red': '\033[31m',
        'dark_green': '\033[32m',
        'dark_yellow': '\033[33m',
        'dark_blue': '\033[34m',
        'dark_magenta': '\033[35m',
        'dark_cyan': '\033[36m',
    }

    # Color sequence for multi-series charts
    COLOR_SEQUENCE = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']

    def __init__(self, width: int = 60, style: str = 'elegant', use_colors: bool = False):
        """
        Initialize the chart generator

        Args:
            width: Chart width in characters (default 60)
            style: Style preset - simple, elegant, compact, rounded (default elegant)
            use_colors: Enable ANSI color output (default False)
        """
        self.width = max(20, min(120, width))
        self.style = style if style in self.STYLES else 'elegant'
        self.use_colors = use_colors
        self.chars = self.STYLES[self.style]

    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled"""
        if not self.use_colors or color not in self.COLORS:
            return text
        return f"{self.COLORS[color]}{text}{self.COLORS['reset']}"

    def _get_bar_color(self, index: int) -> str:
        """Get color for a bar based on its index"""
        return self.COLOR_SEQUENCE[index % len(self.COLOR_SEQUENCE)]

    def bar(self, data: List[Union[int, float]],
            labels: Optional[List[str]] = None,
            title: str = "Bar Chart",
            show_values: bool = True) -> str:
        """
        Generate a vertical bar chart

        Args:
            data: List of numeric values
            labels: Optional labels for each bar
            title: Chart title
            show_values: Whether to show values above bars

        Returns:
            ASCII bar chart string
        """
        if not data:
            return "Error: No data provided"

        data = [max(0, float(v)) for v in data]
        max_val = max(data) if max(data) > 0 else 1
        chart_height = self.width // 2
        scale = chart_height / max_val

        labels = labels or [str(i + 1) for i in range(len(data))]

        lines = []
        lines.append(f"\n  {title}")
        lines.append(f"  {'=' * (len(title) + 2)}\n")

        # Title bar
        top_border = f"  {self.chars['tl']}{self.chars['h'] * (self.width - 2)}{self.chars['tr']}"
        lines.append(top_border)

        # Calculate bar width
        num_bars = len(data)
        available_width = self.width - 4 - max(len(str(max_val)) + 1, 8)
        bar_width = max(1, available_width // num_bars - 1)

        # Draw bars from top to bottom
        for h in range(chart_height, 0, -1):
            threshold = h / scale
            row = f"  {self.chars['v']} "

            for i, val in enumerate(data):
                if val >= threshold:
                    color = self._get_bar_color(i)
                    row += self._color(self.chars['bar'] * bar_width, color)
                else:
                    row += self.chars['space'] * bar_width
                row += self.chars['space']

            # Y-axis label
            row += f"{self.chars['v']} {threshold:>{len(str(max_val))}.1f}"
            lines.append(row)

        # Bottom border with axis
        bottom = f"  {self.chars['bl']}{self.chars['h'] * (self.width - 2)}{self.chars['br']}"
        lines.append(bottom)

        # X-axis labels
        label_row = f"  {self.chars['space']} "
        for label in labels:
            label_row += f"{label:^{bar_width}s}{self.chars['space']}"
        label_row += f"  {self.chars['space']}"
        lines.append(label_row)

        # Show values above bars
        if show_values:
            value_row = f"  {self.chars['space']} "
            for i, val in enumerate(data):
                val_str = f"{val:.1f}" if isinstance(val, float) else str(int(val))
                value_row += f"{self._color(val_str, self._get_bar_color(i)):^{bar_width}s}{self.chars['space']}"
            lines.append(value_row)

        return '\n'.join(lines)

    def hbar(self, data: List[Union[int, float]],
             labels: Optional[List[str]] = None,
             title: str = "Horizontal Bar Chart",
             show_values: bool = True) -> str:
        """
        Generate a horizontal bar chart

        Args:
            data: List of numeric values
            labels: Optional labels for each bar
            title: Chart title
            show_values: Whether to show values at bar ends

        Returns:
            ASCII horizontal bar chart string
        """
        if not data:
            return "Error: No data provided"

        data = [max(0, float(v)) for v in data]
        max_val = max(data) if max(data) > 0 else 1
        max_label_len = max(len(str(l)) for l in (labels or [str(i + 1) for i in range(len(data))]))
        chart_width = self.width - max_label_len - 15
        scale = chart_width / max_val

        labels = labels or [str(i + 1) for i in range(len(data))]

        lines = []
        lines.append(f"\n  {title}")
        lines.append(f"  {'=' * (len(title) + 2)}\n")

        for i, (val, label) in enumerate(zip(data, labels)):
            color = self._get_bar_color(i)
            bar_len = max(1, int(val * scale))
            bar = self._color(self.chars['bar'] * bar_len, color)
            value_str = f"{val:.1f}" if isinstance(val, float) else str(int(val))

            row = f"  {label:>{max_label_len}} {self.chars['v']} {bar} {self.chars['v']} {self._color(value_str, color)}"
            lines.append(row)

        # X-axis
        axis_line = f"  {self.chars['space'] * max_label_len} {self.chars['v']} {self.chars['h'] * chart_width} {self.chars['v']}"
        lines.append(axis_line)

        # X-axis labels
        min_label = "0"
        max_label = f"{max_val:.1f}" if max_val != int(max_val) else str(int(max_val))
        label_line = f"  {self.chars['space'] * max_label_len} {self.chars['space']} {min_label:<{chart_width // 2}}{max_label:>{chart_width - chart_width // 2}}"
        lines.append(label_line)

        return '\n'.join(lines)

    def line(self, data: List[Union[int, float]],
             labels: Optional[List[str]] = None,
             title: str = "Line Chart",
             show_dots: bool = True,
             show_values: bool = True) -> str:
        """
        Generate a line chart

        Args:
            data: List of numeric values
            labels: Optional labels for x-axis
            title: Chart title
            show_dots: Whether to show data point dots
            show_values: Whether to show values at points

        Returns:
            ASCII line chart string
        """
        if not data:
            return "Error: No data provided"

        data = [float(v) for v in data]
        max_val = max(data)
        min_val = min(data)
        val_range = max_val - min_val if max_val != min_val else 1

        chart_height = self.width // 2
        chart_width = len(data) * 4 - 1

        # Normalize data to chart height
        normalized = [int((v - min_val) / val_range * (chart_height - 1)) for v in data]

        labels = labels or [str(i + 1) for i in range(len(data))]

        lines = []
        lines.append(f"\n  {title}")
        lines.append(f"  {'=' * (len(title) + 2)}\n")

        # Draw chart from top to bottom
        for h in range(chart_height - 1, -1, -1):
            row = f"  {self.chars['v']} "

            for i, norm_val in enumerate(normalized):
                if i > 0:
                    row += self.chars['h'] * 2

                if norm_val == h:
                    color = self._get_bar_color(0)
                    row += self._color(self.chars['dot'], color)
                elif show_dots and h == 0:
                    row += self.chars['dot']
                else:
                    # Check for horizontal line connections
                    if i > 0 and (normalized[i-1] <= h < norm_val or norm_val <= h < normalized[i-1]):
                        color = self._get_bar_color(0)
                        row += self._color(self.chars['h'], color)
                    else:
                        row += self.chars['space']

            # Y-axis label
            y_val = min_val + (h / (chart_height - 1)) * val_range
            row += f" {self.chars['v']} {y_val:>6.2f}"
            lines.append(row)

        # X-axis
        axis = f"  {self.chars['bl']}{self.chars['h'] * (chart_width + 2)}{self.chars['br']}"
        lines.append(axis)

        # X-axis labels
        label_row = f"  {self.chars['space']} "
        for i, label in enumerate(labels):
            if i > 0:
                label_row += self.chars['h'] * 2
            label_row += f"{label:^{len(self.chars['dot']) + 2}s}"
        lines.append(label_row)

        # Show values
        if show_values:
            value_row = f"  {self.chars['space']} "
            for i, val in enumerate(data):
                if i > 0:
                    value_row += self.chars['h'] * 2
                val_str = f"{val:.1f}" if isinstance(val, float) else str(int(val))
                value_row += f"{self._color(val_str, self._get_bar_color(0)):^{len(self.chars['dot']) + 2}s}"
            lines.append(value_row)

        return '\n'.join(lines)

    def pie(self, data: Dict[str, Union[int, float]],
            title: str = "Pie Chart",
            style: str = "block") -> str:
        """
        Generate a pie chart (ASCII representation)

        Args:
            data: Dictionary of label -> value
            title: Chart title
            style: Pie style - block, simple, detailed

        Returns:
            ASCII pie chart string
        """
        if not data:
            return "Error: No data provided"

        total = sum(float(v) for v in data.values())
        if total <= 0:
            return "Error: Total value must be positive"

        lines = []
        lines.append(f"\n  {title}")
        lines.append(f"  {'=' * (len(title) + 2)}\n")

        max_label_len = max(len(str(k)) for k in data.keys())
        chart_width = 50

        # Calculate percentages and display
        colors_used = []
        for i, (label, value) in enumerate(data.items()):
            pct = (value / total) * 100
            color = self._get_bar_color(i)
            colors_used.append(color)

            bar_len = int(pct / 100 * chart_width)
            bar = self._color(self.chars['bar'] * bar_len, color)
            empty = self.chars['space'] * (chart_width - bar_len)

            lines.append(f"  {label:>{max_label_len}} |{bar}{empty}| {pct:>5.1f}%  {value}")

        # Simple pie visualization
        lines.append(f"\n  {self.chars['tl']}{self.chars['h'] * 20}{self.chars['tr']}")

        # Create pie segments
        num_segments = 36  # degrees per segment
        segment_chars = ['.', '°', 'o', 'O', '@', '#']

        for row in range(7):
            line = f"  {self.chars['v']} "
            for col in range(18):
                # Simple circular approximation
                dx = col - 9
                dy = row - 3
                dist = (dx * dx + dy * dy) ** 0.5
                if 2 <= dist <= 6:
                    angle = math.atan2(dy, dx)
                    segment_idx = int((angle + math.pi) / (2 * math.pi) * 6) % 6
                    color = self.COLOR_SEQUENCE[segment_idx % len(self.COLOR_SEQUENCE)]
                    line += self._color(segment_chars[row % len(segment_chars)], color)
                elif dist < 2:
                    line += self._color(self.chars['bar'], colors_used[row % len(colors_used)])
                else:
                    line += self.chars['space']
            line += f" {self.chars['v']}"
            lines.append(line)

        lines.append(f"  {self.chars['bl']}{self.chars['h'] * 20}{self.chars['br']}")

        # Legend
        lines.append("\n  Legend:")
        for i, (label, value) in enumerate(data.items()):
            pct = (value / total) * 100
            color = self._get_bar_color(i)
            lines.append(f"    {self._color('■', color)} {label}: {pct:.1f}%")

        return '\n'.join(lines)

    def stacked(self, data: List[Dict],
                series: List[str],
                title: str = "Stacked Bar Chart") -> str:
        """
        Generate a stacked bar chart

        Args:
            data: List of dicts with 'label' and 'values'
            series: List of series names
            title: Chart title

        Returns:
            ASCII stacked bar chart string
        """
        if not data:
            return "Error: No data provided"

        # Calculate totals
        totals = [sum(d['values']) for d in data]
        max_total = max(totals) if max(totals) > 0 else 1

        chart_height = self.width // 3
        max_label_len = max(len(str(d['label'])) for d in data)
        bar_width = 20

        lines = []
        lines.append(f"\n  {title}")
        lines.append(f"  {'=' * (len(title) + 2)}\n")

        # Draw each bar
        for i, d in enumerate(data):
            label = d['label']
            values = d['values']
            row = f"  {label:>{max_label_len}} {self.chars['v']} "

            y = 0
            for j, val in enumerate(values):
                if y / max_total < 1:
                    bar_height = int(val / max_total * chart_height)
                    for _ in range(bar_height):
                        color = self._get_bar_color(j)
                        row += self._color(self.chars['bar'] * bar_width, color)
                        y += 1
                        if y >= chart_height:
                            break
                    if y >= chart_height:
                        break
                    row += '\n' + ' ' * (max_label_len + 3) + self.chars['v'] + ' '

            # Fill remaining with spaces
            while y < chart_height:
                row += self.chars['space'] * bar_width
                y += 1
                if y < chart_height:
                    row += '\n' + ' ' * (max_label_len + 3) + self.chars['v'] + ' '

            lines.append(row)

        # Legend
        lines.append("\n  Legend:")
        for j, s in enumerate(series):
            color = self._get_bar_color(j)
            lines.append(f"    {self._color(self.chars['bar'] * 5, color)} {s}")

        return '\n'.join(lines)

    def area(self, data: List[Union[int, float]],
             labels: Optional[List[str]] = None,
             title: str = "Area Chart",
             fill_char: str = '▓') -> str:
        """
        Generate an area chart

        Args:
            data: List of numeric values
            labels: Optional x-axis labels
            title: Chart title
            fill_char: Character to use for filling

        Returns:
            ASCII area chart string
        """
        if not data:
            return "Error: No data provided"

        data = [float(v) for v in data]
        max_val = max(data)
        min_val = min(data)
        val_range = max_val - min_val if max_val != min_val else 1

        chart_height = self.width // 3
        chart_width = len(data)

        labels = labels or [str(i + 1) for i in range(len(data))]

        lines = []
        lines.append(f"\n  {title}")
        lines.append(f"  {'=' * (len(title) + 2)}\n")

        # Build area map
        area = [[' ' for _ in range(chart_width)] for _ in range(chart_height)]
        normalized = [int((v - min_val) / val_range * (chart_height - 1)) for v in data]

        for x, norm_val in enumerate(normalized):
            for y in range(norm_val):
                area[chart_height - 1 - y][x] = fill_char

        # Draw chart
        for y in range(chart_height):
            row = f"  {self.chars['v']} "
            for x in range(chart_width):
                color = self._get_bar_color(0)
                char = area[y][x]
                if char != ' ':
                    row += self._color(char, color)
                else:
                    row += self.chars['space']
            row += f" {self.chars['v']}"
            lines.append(row)

        # X-axis
        axis = f"  {self.chars['bl']}{self.chars['h'] * chart_width}{self.chars['br']}"
        lines.append(axis)

        # Labels
        label_row = f"  {self.chars['space']} "
        for label in labels:
            label_row += f"{label:^{1}s}{self.chars['space'] * 0}"
        lines.append(label_row)

        return '\n'.join(lines)


# CLI interface
if __name__ == "__main__":
    import sys
    import json

    generator = ASCIIChartGenerator(width=60, style='elegant', use_colors=False)

    # Example usage
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "bar":
            data = [25, 50, 75, 100, 60, 80]
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            print(generator.bar(data, labels, "Monthly Sales"))

        elif command == "hbar":
            data = [100, 75, 50, 25, 90]
            labels = ['Apple', 'Banana', 'Orange', 'Grape', 'Mango']
            print(generator.hbar(data, labels, "Fruit Consumption"))

        elif command == "line":
            data = [3.2, 3.5, 4.1, 3.8, 4.5, 4.2, 4.8]
            labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            print(generator.line(data, labels, "Weekly Temperature"))

        elif command == "pie":
            data = {'Python': 35, 'JavaScript': 25, 'Java': 20, 'C++': 12, 'Other': 8}
            print(generator.pie(data, "Programming Language Popularity"))

        elif command == "stacked":
            data = [
                {'label': 'P1', 'values': [10, 20, 15]},
                {'label': 'P2', 'values': [15, 10, 20]},
                {'label': 'P3', 'values': [20, 15, 10]},
            ]
            print(generator.stacked(data, ['Category A', 'Category B', 'Category C']))

        elif command == "colored":
            gen_colored = ASCIIChartGenerator(width=60, style='elegant', use_colors=True)
            data = [25, 50, 75, 100]
            labels = ['Q1', 'Q2', 'Q3', 'Q4']
            print(gen_colored.bar(data, labels, "Quarterly Results (Colored)"))

        else:
            print(f"Unknown command: {command}")
            print("Available: bar, hbar, line, pie, stacked, colored")
    else:
        # Default demo
        print("ASCII Chart Generator Demo")
        print("=" * 40)

        print(generator.bar([25, 50, 75, 100, 60, 80],
                            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                            "Monthly Sales"))

        print(generator.hbar([100, 75, 50, 25],
                            ['Apple', 'Banana', 'Orange', 'Grape'],
                            "Fruit Consumption"))

        print(generator.pie({'Python': 35, 'JS': 25, 'Java': 20, 'C++': 12, 'Other': 8},
                            "Language Popularity"))
