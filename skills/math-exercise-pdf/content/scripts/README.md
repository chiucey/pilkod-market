# PDF生成脚本

## html_to_pdf.py

将HTML文件转换为PDF的脚本，使用Microsoft Edge浏览器的headless模式。

### 环境要求

- Windows系统
- Microsoft Edge浏览器已安装

### 使用方法

```bash
# 基本用法
python html_to_pdf.py <输入文件>

# 指定输出文件
python html_to_pdf.py <输入文件> <输出文件>

# 跳过公式语法检查（不推荐）
python html_to_pdf.py <输入文件> --force

# 示例
python html_to_pdf.py my_math_exercise.html
python html_to_pdf.py my_math_exercise.html output.pdf
python html_to_pdf.py my_math_exercise.html --force
```

### 工作原理

1. 读取HTML并检查是否存在“未包裹在 `$...$`/`$$...$$` 中”的可疑LaTeX命令
2. 自动检测数学定界符内的裸 `<` / `>`，必要时生成临时安全副本并转义为 `&lt;` / `&gt;`
3. 使用Edge浏览器headless模式（`file:///` 路径）打开HTML文件
4. 等待JS渲染（KaTeX）完成后打印为PDF
5. 自动去掉页眉页脚

### 注意事项

- 确保HTML文件使用UTF-8编码
- 默认开启公式语法防错检查；发现可疑写法会停止导出
- 数学公式中的不等号建议写为 `\lt` / `\gt`（或 `&lt;` / `&gt;`）；脚本会自动兜底修复裸 `<` / `>`
- KaTeX公式会在浏览器中自动渲染
- 生成的PDF为A4尺寸
