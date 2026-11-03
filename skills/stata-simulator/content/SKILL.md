---
name: stata-simulator
description: 模拟Stata功能运行do文件代码。当用户要求执行Stata do文件、运行Stata命令、分析数据或进行统计建模时使用。
---

# Stata Do文件模拟器

本技能提供Stata命令的Python模拟实现，支持解析和执行常见的Stata do文件代码。

## 支持的Stata命令

### 数据管理命令
- `use` - 加载数据集
- `save` - 保存数据集
- `describe` - 描述数据结构
- `list` - 列出数据观测值
- `browse` - 打开数据浏览器
- `generate` / `gen` - 生成新变量
- `replace` - 替换变量值
- `drop` - 删除变量或观测值
- `keep` - 保留变量或观测值
- `rename` - 重命名变量
- `encode` - 将字符串转换为数值编码
- `decode` - 将数值编码转换回字符串
- `merge` - 合并数据集
- `append` - 追加数据集

### 数据分析命令
- `summarize` / `sum` - 描述性统计
- `correlate` / `corr` - 相关性分析
- `tabulate` / `tab` - 频数表
- `describe` - 数据描述
- `codebook` - 代码簿生成

### 统计建模命令
- `regress` / `reg` - 线性回归
- `logit` - Logit回归
- `probit` - Probit回归
- `ttest` - t检验
- `anova` - 方差分析
- `pwcorr` - 成对相关

### 程序控制命令
- `if` 条件语句
- `else` 条件语句
- `foreach` 循环
- `forvalues` 循环
- `while` 循环
- `local` 本地宏
- `global` 全局宏

### 输出命令
- `display` - 显示输出
- `di` - display的简写
- `log` - 日志文件管理

## 使用方法

### 基本语法
```
[stata]
use "data.dta", clear
summarize
regress y x1 x2
[/stata]
```

### 或者通过Python脚本
```python
from stata_simulator import StataEngine

engine = StataEngine()
engine.execute_file("analysis.do")
engine.execute("summarize")
```

## 工作流程

1. **接收do文件内容或Stata命令**
   - 用户提供do文件路径或内联代码
   - 支持 `.do` 文件解析

2. **解析命令**
   - 使用正则表达式解析Stata语法
   - 处理宏替换（local/global）
   - 支持缩进和注释

3. **执行模拟**
   - 调用Python统计库（pandas, scipy, statsmodels）
   - 生成模拟输出
   - 返回结果或保存到文件

4. **输出结果**
   - 描述性统计表格
   - 回归结果
   - 数据预览

## 注意事项

- 本技能提供Stata命令的模拟执行，不是完整的Stata实现
- 对于复杂统计方法，结果可能与真实Stata略有差异
- 建议在生产环境使用真实Stata进行验证

## 示例Do文件

参考 `references/examples/` 目录中的示例do文件。
