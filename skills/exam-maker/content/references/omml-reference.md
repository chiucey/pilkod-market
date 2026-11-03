# OMML（Word 原生公式）参考指南

## 什么是 OMML

OMML（Office Math Markup Language）是 Word 原生公式的 XML 表示方式。与 MathML 类似，但专门针对 Microsoft Word 生态优化。

Word 中插入 → 公式 菜单创建的公式，以及 Pandoc 从 LaTeX 转换来的公式，都是 OMML。

## Pandoc → OMML 自动转换

**本 skill 不需要手动写 OMML**，Pandoc 会自动完成转换：

```bash
pandoc input.md -f markdown+tex_math_dollars --mathml -o output.docx
```

此命令会将 Markdown 中的 `$E=mc^2$` 自动转换为 Word 原生公式对象。

## 常用 LaTeX 公式的 OMML 对照

| LaTeX | 说明 | Word 菜单位置 |
|-------|------|--------------|
| `$x^2$` | 上标 | 上标符号 |
| `$x_n$` | 下标 | 下标符号 |
| `$\frac{a}{b}$` | 分式 | 分数 |
| `$\sqrt{x}$` | 平方根 | 根式 |
| `$\sum_{i=1}^n$` | 求和 | 大运算符 |
| `$\int_a^b$` | 积分 | 微积分 |
| `$\lim_{x \to 0}$` | 极限 | 微积分 |
| `$\vec{a}$` | 向量 | 修饰符 → 箭头 |
| `$\hat{i}$` | 单位向量 | 修饰符 |
| `$\begin{pmatrix} a & b \\ c & d \end{pmatrix}$` | 矩阵 | 矩阵模板 |
| `$\binom{n}{k}$` | 二项式 | 分数（叠放） |

## 手动 OMML 示例

以下为 Word 原生公式的 XML 结构，供参考：

```xml
<!-- 行内公式: E=mc² -->
<w:r>
  <mc:mc>
    <mc:mr>
      <mc:t>E=mc</mc:t>
      <m:sSup>
        <m:sSupPr><m:supSkew 0"/></m:sSupPr>
        <m:e><m:t>2</m:t></m:e>
        <m:sr><m:t>2</m:t></m:sr>
      </m:sSup>
    </mc:mr>
  </mc:mc>
</w:r>
```

```xml
<!-- 分式: 1/2 -->
<w:r>
  <mc:mc>
    <mc:mr>
      <m:f>
        <m:fPr><m:type val="skewed"/></m:fPr>
        <m:num><m:t>1</m:t></m:num>
        <m:den><m:t>2</m:t></m:den>
      </m:f>
    </mc:mr>
  </mc:mc>
</w:r>
```

## 已知限制

以下 LaTeX 语法 Pandoc 支持转换为 OMML：
- 基础数学符号和运算
- 上标 / 下标
- 分式、根号
- 求和、积分、极限
- 矩阵（smallmatrix、pmatrix、bmatrix）
- 希腊字母
- 分段函数 / cases

以下内容**不支持**自动转换（需手动在 Word 中调整）：
- TikZ / pgfplots 图形
- OVERLEAF 特有宏（如 `\血液`、`\percentage`）
- `\verb|...|` 格式化文本
- 复杂多行公式建议拆分为多个公式块
