#!/usr/bin/env python3
"""
ASCII Art Chart Generator Script
用于生成各种类型的 ASCII 艺术图表
"""

import sys
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChartConfig:
    """图表配置"""
    width: int = 60
    height: int = 20
    title: str = ""
    show_values: bool = True
    show_legend: bool = True
    border: bool = True
    theme: str = "classic"
    fill_char: str = "█"
    colors: bool = False


class AsciiChartGenerator:
    """ASCII 图表生成器"""

    # ANSI 颜色代码
    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'gray': '\033[90m',
    }

    # 边框字符
    BORDERS = {
        'classic': {
            'top_left': '┌', 'top_right': '┐',
            'bottom_left': '└', 'bottom_right': '┘',
            'horizontal': '─', 'vertical': '│',
            'left_t': '├', 'right_t': '┤',
            'top_t': '┬', 'bottom_t': '┴',
            'cross': '┼'
        },
        'double': {
            'top_left': '╔', 'top_right': '╗',
            'bottom_left': '╚', 'bottom_right': '╝',
            'horizontal': '═', 'vertical': '║',
            'left_t': '╠', 'right_t': '╣',
            'top_t': '╦', 'bottom_t': '╩',
            'cross': '╬'
        },
        'simple': {
            'top_left': '+', 'top_right': '+',
            'bottom_left': '+', 'bottom_right': '+',
            'horizontal': '-', 'vertical': '|',
            'left_t': '+', 'right_t': '+',
            'top_t': '+', 'bottom_t': '+',
            'cross': '+'
        }
    }

    # 数据点标记
    LINE_MARKERS = ['●', '○', '◆', '◇', '■', '□', '▲', '▼']

    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        self.border = self.BORDERS.get(self.config.theme, self.BORDERS['classic'])

    def _colorize(self, text: str, color: str) -> str:
        """为文本添加颜色"""
        if not self.config.colors:
            return text
        color_code = self.COLORS.get(color, '')
        return f"{color_code}{text}{self.COLORS['reset']}"

    def _wrap_border(self, content: str) -> str:
        """为内容添加边框"""
        if not self.config.border:
            return content

        h_line = self.border['horizontal'] * (self.config.width + 2)
        top = f"{self.border['top_left']}{h_line}{self.border['top_right']}"
        bottom = f"{self.border['bottom_left']}{h_line}{self.border['bottom_right']}"

        lines = content.split('\n')
        bordered = [top]
        for line in lines:
            padded = line.ljust(self.config.width)
            bordered.append(f"{self.border['vertical']} {padded} {self.border['vertical']}")
        bordered.append(bottom)

        return '\n'.join(bordered)

    def _wrap_title(self, text: str) -> str:
        """添加标题"""
        if not text:
            return ""
        return f" {text} ".center(self.config.width, ' ')

    def generate_bar_chart(self, data: Dict[str, float], labels: Optional[List[str]] = None) -> str:
        """生成柱状图"""
        if not data:
            return "No data provided"

        max_value = max(data.values())
        min_value = min(data.values())
        value_range = max_value - min_value if max_value != min_value else 1

        # 计算比例
        chart_height = self.config.height - 3  # 留出标题和标签空间
        bars = []
        colors_list = ['blue', 'green', 'cyan', 'purple', 'yellow', 'red']

        # 存储每个柱形的高度
        bar_heights = []

        for i, (label, value) in enumerate(data.items()):
            # 计算柱状图高度
            normalized = (value - min_value) / value_range
            bar_height = int(normalized * chart_height)
            bar_heights.append(bar_height)

            # 添加数值标签
            value_str = f"{value:,.0f}" if isinstance(value, (int, float)) else str(value)
            label_str = label[:12]  # 截断过长标签

            bars.append((label_str, value_str))

        # 构建图表
        chart_lines = []
        if self.config.title:
            chart_lines.append(self._wrap_title(self.config.title))
            chart_lines.append("")

        # Y轴刻度和条形
        for i in range(chart_height, -1, -1):
            if chart_height > 0:
                y_value = min_value + (value_range * i / chart_height)
            else:
                y_value = min_value
            y_label = f"{y_value:>7,.0f}"
            line = f"{y_label}│"

            for idx, (_, _) in enumerate(bars):
                bar_height = bar_heights[idx]
                color = colors_list[idx % len(colors_list)]

                if i < bar_height:
                    # 显示填充字符（使用颜色）
                    bar_char = self._colorize(self.config.fill_char, color)
                    line += bar_char + " "
                else:
                    line += "  "

            chart_lines.append(line)

        # X轴
        chart_lines.append(" " * 8 + "└" + "──" * len(bars))

        # X轴标签
        x_labels = " " * 8
        for label, _ in bars:
            x_labels += label[:8].center(8)
        chart_lines.append(x_labels)

        # 数值标签
        if self.config.show_values:
            values_line = " " * 8
            for _, value in bars:
                values_line += value.center(8)
            chart_lines.append(values_line)

        return self._wrap_border('\n'.join(chart_lines))

    def generate_line_chart(self, data: Dict[str, List[float]], x_labels: Optional[List[str]] = None) -> str:
        """生成折线图"""
        if not data:
            return "No data provided"

        series_names = list(data.keys())
        num_points = len(list(data.values())[0])

        # 合并所有数据找到范围
        all_values = [v for values in data.values() for v in values]
        max_value = max(all_values)
        min_value = min(all_values)
        value_range = max_value - min_value if max_value != min_value else 1

        chart_height = self.config.height - 3

        # 初始化网格
        grid = [[' ' for _ in range(num_points * 2 + 2)] for _ in range(chart_height + 1)]

        # Y轴刻度线
        for i in range(chart_height + 1):
            grid[i][0] = '│'

        # X轴线
        grid.append(['└'] + ['─'] * (num_points * 2) + ['┘'])

        # 绘制每个系列
        colors_list = ['blue', 'green', 'cyan', 'purple', 'yellow', 'red']

        for series_idx, (series_name, values) in enumerate(data.items()):
            color = colors_list[series_idx % len(colors_list)]
            marker = self._colorize(self.LINE_MARKERS[series_idx % len(self.LINE_MARKERS)], color)

            for point_idx, value in enumerate(values):
                # 计算Y位置
                normalized = (value - min_value) / value_range
                y_pos = chart_height - int(normalized * chart_height)

                x_pos = 1 + point_idx * 2

                # 绘制点
                grid[y_pos][x_pos] = marker

                # 如果不是第一个点，绘制连线
                if point_idx > 0:
                    prev_normalized = (values[point_idx - 1] - min_value) / value_range
                    prev_y = chart_height - int(prev_normalized * chart_height)

                    if prev_y != y_pos:
                        start, end = min(prev_y, y_pos), max(prev_y, y_pos)
                        for y in range(start + 1, end):
                            if grid[y][x_pos - 1] == ' ':
                                grid[y][x_pos - 1] = '─'

        # 添加Y轴标签
        for i in range(chart_height + 1):
            value = min_value + (value_range * (chart_height - i) / chart_height)
            grid[i] = [f"{value:.0f}"] + grid[i]

        # 添加X轴标签
        if x_labels:
            x_label_line = " " * 8
            for label in x_labels[:num_points]:
                x_label_line += label[:6].center(6)
            grid.append(x_label_line)

        # 构建图表
        chart_lines = []
        if self.config.title:
            chart_lines.append(self._wrap_title(self.config.title))

        for line in grid:
            chart_lines.append(''.join(line))

        # 添加图例
        if self.config.show_legend:
            legend = " " * 8
            for idx, name in enumerate(series_names):
                marker = self.LINE_MARKERS[idx % len(self.LINE_MARKERS)]
                color = colors_list[idx % len(colors_list)]
                legend += self._colorize(f" {marker} {name}", color)
            chart_lines.append(legend)

        return '\n'.join(chart_lines)

    def generate_pie_chart(self, data: Dict[str, float]) -> str:
        """生成饼图（简化ASCII版本）"""
        if not data:
            return "No data provided"

        total = sum(data.values())
        colors_list = ['blue', 'green', 'yellow', 'red', 'purple', 'cyan']

        chart_lines = []
        if self.config.title:
            chart_lines.append(self._wrap_title(self.config.title))
            chart_lines.append("")

        # 简单的饼图表示
        chart_lines.append("            ╭─────────────╮")
        chart_lines.append("           ╱               ╲")
        chart_lines.append("          │                 │")
        chart_lines.append("          │      PIE        │")
        chart_lines.append("           ╲               ╱")
        chart_lines.append("            ╰─────────────╯")
        chart_lines.append("")

        # 图例
        chart_lines.append("   图例：")
        for idx, (label, value) in enumerate(data.items()):
            percentage = (value / total * 100) if total > 0 else 0
            color = colors_list[idx % len(colors_list)]
            chart_lines.append(
                f"   {self._colorize('■', color)} {label}: {percentage:.1f}% ({value:,.0f})"
            )

        return self._wrap_border('\n'.join(chart_lines))

    def generate_gantt_chart(self, tasks: List[Dict[str, any]]) -> str:
        """生成甘特图"""
        if not tasks:
            return "No data provided"

        # 计算时间范围
        max_weeks = max(max(t['start'] + t['duration'] for t in tasks), 12)

        chart_lines = []
        if self.config.title:
            chart_lines.append(self._wrap_title(self.config.title))
            chart_lines.append("")

        # 任务条
        colors_list = ['blue', 'green', 'yellow', 'red', 'purple', 'cyan']

        for idx, task in enumerate(tasks):
            name = task.get('name', f'任务{idx + 1}')[:10]
            start = task.get('start', 1)
            duration = task.get('duration', 1)

            # 进度条
            bar = "░" * (start - 1) + "█" * duration + "░" * (max_weeks - start - duration + 1)

            color = colors_list[idx % len(colors_list)]
            chart_lines.append(
                f"  {name:<12} {self._colorize(bar, color)}  "
            )

        # X轴刻度
        week_line = "  " + " " * 12
        for w in range(1, max_weeks + 1):
            week_line += f"W{w:<2}"
        chart_lines.append("")
        chart_lines.append(week_line)

        return self._wrap_border('\n'.join(chart_lines))


def main():
    """主函数 - 演示"""
    config = ChartConfig(
        title="ASCII Art Chart Demo",
        width=70,
        height=20,
        show_values=True,
        show_legend=True,
        colors=True
    )

    generator = AsciiChartGenerator(config)

    # 演示柱状图
    print("=== 柱状图示例 ===")
    bar_data = {
        "一月": 45000,
        "二月": 52000,
        "三月": 48000,
        "四月": 61000,
        "五月": 58000,
        "六月": 72000
    }
    print(generator.generate_bar_chart(bar_data))
    print()

    # 演示折线图
    print("=== 折线图示例 ===")
    line_config = ChartConfig(title="产品趋势", colors=True)
    line_generator = AsciiChartGenerator(line_config)
    line_data = {
        "产品A": [30, 45, 60, 75],
        "产品B": [45, 60, 55, 80]
    }
    print(line_generator.generate_line_chart(line_data, ["Q1", "Q2", "Q3", "Q4"]))
    print()

    # 演示饼图
    print("=== 饼图示例 ===")
    pie_config = ChartConfig(title="市场份额")
    pie_generator = AsciiChartGenerator(pie_config)
    pie_data = {
        "移动端": 45,
        "桌面端": 35,
        "平板端": 15,
        "其他": 5
    }
    print(pie_generator.generate_pie_chart(pie_data))
    print()

    # 演示甘特图
    print("=== 甘特图示例 ===")
    gantt_config = ChartConfig(title="项目进度")
    gantt_generator = AsciiChartGenerator(gantt_config)
    gantt_data = [
        {"name": "需求分析", "start": 1, "duration": 2},
        {"name": "系统设计", "start": 3, "duration": 2},
        {"name": "开发", "start": 5, "duration": 5},
        {"name": "测试", "start": 8, "duration": 3},
        {"name": "部署", "start": 11, "duration": 1}
    ]
    print(gantt_generator.generate_gantt_chart(gantt_data))


if __name__ == "__main__":
    main()
