---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502201ec54a4a185e8b78794a845b99efb65442ef0b302568561f190486afd7787104022100ebff09f5f73501db9c28a1953d06a7c75976f86f09f3af8a334b87dc7245fad0
    ReservedCode2: 3045022100e4f9ba20bc2590ec49849ebc96358bd6c806c08d83237ff3446b0e61c644f07c02204b962572773b987619352c948e77256b0496e52cc8baa92ceb0a979c1d2f9741
---

# KaTeX 语法速查表

## 基础数学符号

| 用途 | 语法 | 渲染效果 |
|------|------|---------|
| 行内公式 | `\(a^2 + b^2 = c^2\)` | \(a^2 + b^2 = c^2\) |
| 行间公式 | `\[E = mc^2\]` | \[E = mc^2\] |
| 分数 | `\frac{numerator}{denominator}` | \(\frac{a}{b}\) |
| 上下标 | `x^{n}`, `x_{i}` | \(x^{n}\), \(x_{i}\) |
| 平方根 | `\sqrt{x}` | \(\sqrt{x}\) |
| n次方根 | `\sqrt[n]{x}` | \(\sqrt[n]{x}\) |
| 求和 | `\sum_{i=1}^{n}` | \(\sum_{i=1}^{n}\) |
| 积分 | `\int_{a}^{b}` | \(\int_{a}^{b}\) |
| 无穷 | `\infty` | \(\infty\) |

## 矩阵与环境

### aligned（对齐，推荐多行公式）
```latex
\[
\begin{aligned}
ax + by &= e \\
cx + dy &= f
\end{aligned}
\]
```

### cases（分段函数）
```latex
\[
f(x) =
\begin{cases}
x^2 & \text{if } x \geq 0 \\
-x^2 & \text{if } x < 0
\end{cases}
\]
```

### bmatrix（矩阵）
```latex
\[
\begin{bmatrix}
a_{11} & a_{12} \\
a_{21} & a_{22}
\end{bmatrix}
\]
```

## 特殊符号

| 符号 | 语法 |
|------|------|
| \(\times\) | `\times` |
| \(\div\) | `\div` |
| \(\pm\) | `\pm` |
| \(\mp\) | `\mp` |
| \(\cdot\) | `\cdot` |
| \(\leq\) | `\leq` |
| \(\geq\) | `\geq` |
| \(\neq\) | `\neq` |
| \(\approx\) | `\approx` |
| \(\equiv\) | `\equiv` |
| \(\in\) | `\in` |
| \(\notin\) | `\notin` |
| \(\subset\) | `\subset` |
| \(\cup\) | `\cup` |
| \(\cap\) | `\cap` |
| \(\forall\) | `\forall` |
| \(\exists\) | `\exists` |
| \(\rightarrow\) | `\rightarrow` |
| \(\Rightarrow\) | `\Rightarrow` |
| \(\leftrightarrow\) | `\leftrightarrow` |
| \(\Longleftrightarrow\) | `\Longleftrightarrow` |

## 三角函数与特殊函数

| 函数 | 语法 |
|------|------|
| \(\sin\) | `\sin` |
| \(\cos\) | `\cos` |
| \(\tan\) | `\tan` |
| \(\log\) | `\log` |
| \(\ln\) | `\ln` |
| \(\exp\) | `\exp` |

## 文本与空格

| 用途 | 语法 |
|------|------|
| 文本模式 | `\text{中文文本}` |
| 小空格 | `\,` |
| 中空格 | `\;` |
| 大空格 | `\quad` |
| 双空格 | `\qquad` |

## 常见错误规避

### ❌ 禁用
```latex
\begin{align}  <!-- KaTeX不支持 -->
\begin{array}  <!-- KaTeX不支持 -->
\operatorname{}  <!-- 过时 -->
```

### ✅ 正确用法
```latex
\begin{aligned}  <!-- 推荐 -->
\operatorname*{}  <!-- 正确用法 -->
```

## 括号与定界符

| 符号 | 语法 |
|------|------|
| 圆括号 | `(` `)` |
| 方括号 | `[` `]` |
| 花括号 | `\{` `\}` |
| 绝对值 | `|` `|` 或 `\lvert` `\rvert` |
| 双线 | `\|` `\|` 或 `\lVert` `\rVert` |
| 自适应括号 | `\left(` `\right)` |

## 编号与标签

```latex
\[
\tag{1} ax + b = 0
\]
```

## 极限定理

```latex
\lim_{x \to \infty} \frac{1}{x} = 0
```

```latex
\frac{d}{dx}f(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
```