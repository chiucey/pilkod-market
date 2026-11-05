#!/usr/bin/env python3
"""
人类行为模拟脚本
模拟真实用户的浏览行为，包括鼠标移动、滚动、点击延迟等
"""

import asyncio
import random
import time
import json
from typing import Optional, Tuple


class HumanSimulation:
    """人类行为模拟类"""

    def __init__(self):
        # 随机参数范围
        self.mouse_move_delay_range = (0.1, 0.5)  # 鼠标移动延迟（秒）
        self.click_delay_range = (0.2, 1.0)  # 点击延迟（秒）
        self.scroll_delay_range = (0.3, 0.8)  # 滚动延迟（秒）
        self.typing_delay_range = (0.05, 0.15)  # 打字延迟（秒）
        self.reading_delay_range = (0.5, 2.0)  # 阅读延迟（秒）

    def get_random_delay(self, delay_range: Tuple[float, float]) -> float:
        """
        获取随机延迟

        Args:
            delay_range: 延迟范围（最小值，最大值）

        Returns:
            随机延迟时间（秒）
        """
        return random.uniform(*delay_range)

    def get_bezier_curve_point(self, t: float, p0: Tuple[int, int], p1: Tuple[int, int],
                               p2: Tuple[int, int], p3: Tuple[int, int]) -> Tuple[float, float]:
        """
        获取贝塞尔曲线上的点（用于平滑鼠标移动）

        Args:
            t: 时间参数（0-1）
            p0: 起始点
            p1: 控制点1
            p2: 控制点2
            p3: 终点

        Returns:
            曲线上的点坐标
        """
        x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
        return (x, y)

    def get_mouse_move_points(self, start: Tuple[int, int], end: Tuple[int, int],
                              steps: int = 10) -> list:
        """
        获取鼠标移动路径点（使用贝塞尔曲线）

        Args:
            start: 起始点 (x, y)
            end: 终点 (x, y)
            steps: 移动步数

        Returns:
            移动路径点列表
        """
        # 生成随机控制点
        p0 = start
        p3 = end
        p1 = (start[0] + random.uniform(-50, 50), start[1] + random.uniform(-50, 50))
        p2 = (end[0] + random.uniform(-50, 50), end[1] + random.uniform(-50, 50))

        # 生成路径点
        points = []
        for i in range(steps + 1):
            t = i / steps
            point = self.get_bezier_curve_point(t, p0, p1, p2, p3)
            points.append((int(point[0]), int(point[1])))

        return points

    def get_mouse_move_script(self, start: Tuple[int, int], end: Tuple[int, int],
                              steps: int = 10) -> str:
        """
        获取鼠标移动 JavaScript 脚本

        Args:
            start: 起始点 (x, y)
            end: 终点 (x, y)
            steps: 移动步数

        Returns:
            JavaScript 脚本
        """
        points = self.get_mouse_move_points(start, end, steps)

        script = f"""
        (async () => {{
            const points = {json.dumps(points)};
            for (let i = 0; i < points.length; i++) {{
                const point = points[i];
                window.dispatchEvent(new MouseEvent('mousemove', {{
                    clientX: point[0],
                    clientY: point[1],
                    bubbles: true
                }}));
                await new Promise(resolve => setTimeout(resolve, {self.get_random_delay(self.mouse_move_delay_range) * 1000}));
            }}
        }})();
        """
        return script

    def get_scroll_script(self, scroll_distance: int = 300, steps: int = 5) -> str:
        """
        获取滚动 JavaScript 脚本

        Args:
            scroll_distance: 滚动距离（像素）
            steps: 滚动步数

        Returns:
            JavaScript 脚本
        """
        step_size = scroll_distance / steps

        script = f"""
        (async () => {{
            const stepSize = {step_size};
            const steps = {steps};
            for (let i = 0; i < steps; i++) {{
                window.scrollBy(0, stepSize);
                await new Promise(resolve => setTimeout(resolve, {self.get_random_delay(self.scroll_delay_range) * 1000}));
            }}
        }})();
        """
        return script

    def get_typing_script(self, text: str, selector: str = None) -> str:
        """
        获取打字 JavaScript 脚本

        Args:
            text: 要输入的文本
            selector: 元素选择器（可选）

        Returns:
            JavaScript 脚本
        """
        script = f"""
        (async () => {{
            const text = {json.dumps(text)};
            const element = {f"document.querySelector('{selector}')" if selector else "document.activeElement"};
            if (!element) return;

            element.value = '';
            element.focus();

            for (let i = 0; i < text.length; i++) {{
                const char = text[i];
                element.value += char;
                element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                await new Promise(resolve => setTimeout(resolve, {self.get_random_delay(self.typing_delay_range) * 1000}));
            }}
            element.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }})();
        """
        return script

    def get_reading_delay(self) -> float:
        """
        获取阅读延迟时间

        Returns:
            随机阅读延迟时间（秒）
        """
        return self.get_random_delay(self.reading_delay_range)

    def get_behavior_sequence_script(self, actions: list) -> str:
        """
        获取行为序列 JavaScript 脚本

        Args:
            actions: 动作列表，每个动作是一个字典：
                - type: "move" | "scroll" | "click" | "type"
                - params: 动作参数

        Returns:
            JavaScript 脚本
        """
        scripts = []

        for action in actions:
            action_type = action.get("type")
            params = action.get("params", {})

            if action_type == "move":
                scripts.append(self.get_mouse_move_script(**params))
            elif action_type == "scroll":
                scripts.append(self.get_scroll_script(**params))
            elif action_type == "type":
                scripts.append(self.get_typing_script(**params))
            elif action_type == "wait":
                delay = params.get("delay", self.get_reading_delay())
                scripts.append(f"""
                await new Promise(resolve => setTimeout(resolve, {delay * 1000}));
                """)

        combined_script = f"""
        (async () => {{
            {chr(10).join(scripts)}
        }})();
        """
        return combined_script


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="人类行为模拟工具")
    parser.add_argument(
        "--action",
        type=str,
        choices=["move", "scroll", "type", "sequence"],
        required=True,
        help="动作类型"
    )
    parser.add_argument(
        "--start",
        type=str,
        help="起始点，格式：x,y"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="终点，格式：x,y"
    )
    parser.add_argument(
        "--distance",
        type=int,
        help="滚动距离（像素）"
    )
    parser.add_argument(
        "--text",
        type=str,
        help="要输入的文本"
    )
    parser.add_argument(
        "--selector",
        type=str,
        help="元素选择器"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="behavior.js",
        help="输出文件路径"
    )

    args = parser.parse_args()

    # 创建人类行为模拟实例
    simulation = HumanSimulation()

    # 根据动作类型生成脚本
    if args.action == "move":
        if not args.start or not args.end:
            print("错误: 移动动作需要 --start 和 --end 参数")
            return

        start = tuple(map(int, args.start.split(",")))
        end = tuple(map(int, args.end.split(",")))
        script = simulation.get_mouse_move_script(start, end)

    elif args.action == "scroll":
        distance = args.distance or 300
        script = simulation.get_scroll_script(distance)

    elif args.action == "type":
        if not args.text:
            print("错误: 打字动作需要 --text 参数")
            return

        script = simulation.get_typing_script(args.text, args.selector)

    else:
        print(f"错误: 不支持的动作类型 {args.action}")
        return

    # 输出脚本
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(script)

    print(f"✓ 行为模拟脚本已生成: {args.output}")
    print(f"✓ 动作类型: {args.action}")


if __name__ == "__main__":
    main()
