# 数学动画生成器 - 示例脚本参考

本文档提供常见数学动画的Manim代码示例。

## 1. 几何变换动画

### 1.1 旋转动画

```python
from manim import *

class CircleRotation(Scene):
    def construct(self):
        # 创建红色圆形
        circle = Circle(color=RED, fill_opacity=0.5)

        # 添加标签
        label = Text("旋转的圆形").to_edge(UP)

        self.add(label, circle)

        # 绕中心旋转360度
        self.play(Rotate(circle, angle=TAU), run_time=5)

        # 等待查看
        self.wait()
```

### 1.2 形变动画（圆形→正方形）

```python
from manim import *

class CircleToSquare(Scene):
    def construct(self):
        # 创建圆形和正方形
        circle = Circle(color=BLUE, fill_opacity=0.3)
        square = Square(color=GREEN, fill_opacity=0.3)

        # 叠加在一起
        self.add(circle)

        # 形变动画
        self.play(Transform(circle, square), run_time=3)
        self.wait()
```

### 1.3 平移动画

```python
from manim import *

class TranslationAnimation(Scene):
    def construct(self):
        # 创建三角形
        triangle = Triangle(color=ORANGE, fill_opacity=0.5)
        triangle.to_edge(LEFT)

        # 添加并移动
        self.add(triangle)
        self.play(triangle.animate.to_edge(RIGHT), run_time=2)
        self.play(triangle.animate.shift(UP * 2), run_time=1)
        self.play(triangle.animate.shift(DOWN * 2 + LEFT * 3), run_time=2)
```

## 2. 函数图像绘制

### 2.1 绘制三角函数

```python
from manim import *

class SinCosGraph(Scene):
    def construct(self):
        # 创建坐标系
        axes = Axes(
            x_range=[-2*PI, 2*PI, PI/2],
            y_range=[-2, 2, 0.5],
            x_length=10,
            y_length=5,
            axis_config={"include_tip": True}
        )

        # 添加标签
        labels = axes.get_axis_labels(
            x_label=Text("x"),
            y_label=Text("y")
        )

        # 绘制函数图像
        sin_graph = axes.plot(
            lambda x: np.sin(x),
            color=BLUE,
            x_range=[-2*PI, 2*PI]
        )
        cos_graph = axes.plot(
            lambda x: np.cos(x),
            color=RED,
            x_range=[-2*PI, 2*PI]
        )

        # 添加图例
        sin_label = axes.get_graph_label(sin_graph, Text("sin(x)"))
        cos_label = axes.get_graph_label(cos_graph, Text("cos(x)"))

        # 动画显示
        self.play(Create(axes), Write(labels))
        self.play(Create(sin_graph), Write(sin_label))
        self.play(Create(cos_graph), Write(cos_label))

        self.wait()
```

### 2.2 极坐标玫瑰线

```python
from manim import *

class PolarRose(Scene):
    def construct(self):
        # 创建极坐标平面
        plane = PolarPlane(
            radius_max=3,
            azimuth_step=30
        )

        # 玫瑰线方程: r = cos(2θ)
        rose = plane.plot_graph(
            lambda theta: np.cos(2*theta),
            color=PURPLE,
            use_polar_coordinates=True
        )

        self.add(plane)
        self.play(Create(rose), run_time=3)
        self.wait()
```

## 3. 数学公式动画

### 3.1 公式书写动画

```python
from manim import *

class FormulaWrite(Scene):
    def construct(self):
        # 创建公式
        formula = MathTex(
            r"a^2 + b^2 = c^2",
            font_size=72
        )

        # 书写动画
        self.play(Write(formula), run_time=3)
        self.wait()
```

### 3.2 公式变换动画

```python
from manim import *

class FormulaTransform(Scene):
    def construct(self):
        # 起始公式
        formula1 = MathTex(r"(a + b)^2", font_size=72)

        # 变换公式
        formula2 = MathTex(r"a^2 + 2ab + b^2", font_size=72)

        self.add(formula1)
        self.wait()

        # 变换动画
        self.play(TransformMatchingTex(formula1, formula2))
        self.wait()
```

### 3.3 勾股定理推导

```python
from manim import *

class PythagoreanTheorem(Scene):
    def construct(self):
        # 标题
        title = Text("勾股定理", font_size=48)
        title.to_edge(UP)

        # 公式
        theorem = MathTex(r"a^2 + b^2 = c^2", font_size=72)

        # 说明
        explanation = Text(
            "直角三角形的两直角边的平方和等于斜边的平方",
            font_size=24
        )
        explanation.to_edge(DOWN)

        self.play(Write(title))
        self.wait()
        self.play(Write(theorem), run_time=2)
        self.play(Write(explanation))
        self.wait()
```

## 4. 算法可视化

### 4.1 冒泡排序动画

```python
from manim import *

class BubbleSort(Scene):
    def construct(self):
        # 初始数组
        arr = [5, 3, 8, 4, 1]

        # 创建方块表示
        boxes = VGroup(*[
            Square(side_length=0.8, fill_opacity=0.5)
            for _ in arr
        ]).arrange(RIGHT, buff=0.2)

        # 添加数值标签
        labels = VGroup(*[
            Text(str(val)).move_to(box)
            for val, box in zip(arr, boxes)
        ])

        # 添加标题
        title = Text("冒泡排序", font_size=36)
        title.to_edge(UP)

        self.add(title, boxes, labels)
        self.wait()

        # 排序动画
        n = len(arr)
        for i in range(n):
            for j in range(n - i - 1):
                # 高亮比较的两个元素
                boxes[j].set_color(YELLOW)
                boxes[j + 1].set_color(YELLOW)

                if arr[j] > arr[j + 1]:
                    # 交换动画
                    self.play(
                        boxes[j].animate.shift(RIGHT * 0.8),
                        boxes[j + 1].animate.shift(LEFT * 0.8),
                    )
                    # 交换数值
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]

                self.wait(0.5)

                # 取消高亮
                boxes[j].set_color(BLUE_E)
                boxes[j + 1].set_color(BLUE_E)

        # 完成标记
        checkmark = MathTex(r"\checkmark", color=GREEN)
        checkmark.next_to(title, DOWN)
        self.play(Write(checkmark))
        self.wait()
```

## 5. 3D动画

### 5.1 3D球体螺旋运动

```python
from manim import *

class SphereSpiral3D(ThreeDScene):
    def construct(self):
        # 设置相机视角
        self.set_camera_orientation(phi=70*DEGREES, theta=-45*DEGREES)

        # 创建球体
        sphere = Sphere(radius=0.5, color=BLUE)

        # 创建螺旋路径
        spiral = ParametricFunction(
            lambda t: np.array([
                0.5 * np.cos(t),
                0.5 * np.sin(t),
                t/3
            ]),
            t_range=[0, 6*PI],
            color=YELLOW
        )

        # 添加对象
        self.add(spiral)
        self.play(Create(sphere))

        # 沿螺旋路径移动
        self.play(
            MoveAlongPath(sphere, spiral),
            run_time=6
        )

        self.wait()
```

## 常用动画效果

| 效果 | 代码 | 说明 |
|-----|------|------|
| 创建 | `Create(obj)` | 从无到有显示 |
| 书写 | `Write(obj)` | 逐字/逐笔显示 |
| 旋转 | `Rotate(obj, angle)` | 绕点旋转 |
| 位移 | `obj.animate.shift()` | 移动位置 |
| 变换 | `Transform(obj1, obj2)` | 形状变换 |
| 路径动画 | `MoveAlongPath(obj, path)` | 沿路径运动 |
| 环绕 | `Circumscribe(obj)` | 环绕高亮 |
| 淡入淡出 | `FadeIn/Out(obj)` | 透明度变化 |
