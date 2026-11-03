---
name: stata-code-checker
description: Stata代码检测与自动修复技能。当用户需要检查、验证或自动修复Stata代码时使用，包括语法错误检测、常见问题修复、代码优化建议等功能。
---

# Stata代码检测与自动修复技能

## 技能概述

本技能提供全面的Stata代码检测和自动修复能力，模拟Stata运行时的错误检测机制，能够识别语法错误、逻辑问题，并提供自动修正方案。技能涵盖从基础语法到高级编程的最佳实践检查。

## 核心功能

### 1. 语法错误检测

#### 1.1 命令语法检查

技能能够检测以下常见语法错误：

**变量引用错误**：检测未定义的变量、拼写错误的变量名、缺失的引号等。

```
错误示例：
reg y x1 x2  // 变量可能未定义
summarize yra  // 拼写错误：yra应为year

正确示例：
reg y x1 x2
summarize year
```

**命令拼写检查**：识别错误的命令名称并建议正确的Stata命令。

```
错误示例：
regresss y x  // 拼写错误
summry y x    // 拼写错误

正确示例：
regress y x
summarize y x
```

#### 1.2 括号和引号匹配

```
错误示例：
gen newvar = x1 + x2  // 缺失等号后的空格（不影响功能但不符合规范）
replace y = 1 if x > 0 and z < 10  // 逻辑运算符错误

正确示例：
gen newvar = x1 + x2
replace y = 1 if x > 0 & z < 10
```

### 2. 逻辑错误检测

#### 2.1 循环结构检查

**Foreach和forvalues循环**：检测循环变量的使用错误。

```
错误模式：
foreach var of varlist x1-x10 {
    sum `var'
    gen `var'_mean = r(mean)  // 错误：未定义的宏
}

正确模式：
foreach var of varlist x1-x10 {
    sum `var'
    gen `var'_mean = r(mean)
}
```

**While循环终止条件**：确保循环有明确的终止条件，防止无限循环。

```
危险模式：
local i = 1
while `i' < 10 {
    display `i'
    // 缺失 i++ 或 i = `i' + 1
}

安全模式：
local i = 1
while `i' < 10 {
    display `i'
    local i = `i' + 1
}
```

#### 2.2 条件判断逻辑

```
错误示例：
if gender == 1 {
    gen height_m = height / 100
}
else if gender == 0 {  // 错误：else if之间缺少空格或分开写
    gen height_m = height / 100
}

正确示例：
if gender == 1 {
    gen height_m = height / 100
}
else {
    gen height_m = height / 100
}
```

### 3. 数据处理问题检测

#### 3.1 缺失值处理

技能检测未处理的缺失值问题：

```
问题代码：
gen total = x1 + x2 + x3  // 缺失值会导致结果为缺失值

改进代码：
gen total = rowtotal(x1 x2 x3)  // 自动处理缺失值
// 或
egen total = rowmean(x1 x2 x3)  // 计算非缺失值的均值
```

#### 3.2 变量类型检查

```
错误示例：
encode string_var, gen(num_var)  // 字符串变量已包含数值
destring num_string, replace  // 包含非数字字符的字符串

正确示例：
encode string_var, gen(num_var)
destring num_string, replace force  // 使用force处理非数字字符
```

### 4. 编码规范检查

#### 4.1 宏命名规范

```
不规范示例：
local a = 5
global b = 10

规范示例：
local depvar = "income"
global controls "age gender education"
```

#### 4.2 代码结构建议

```
建议的结构：
clear all
cap log close
set more off

// 数据导入
use "data.dta", clear

// 数据处理
// ...

// 分析
// ...

log close
```

### 5. 性能优化建议

#### 5.1 循环效率

```
低效模式：
forvalues i = 1/1000 {
    reg y x`i' if subset == 1
}

高效模式：
foreach var of varlist x1-x1000 {
    reg y `var' if subset == 1
}
```

#### 5.2 数据处理效率

```
低效：
gen newvar = .
replace newvar = 1 if condition1
replace newvar = 2 if condition2
replace newvar = 3 if condition3

高效：
gen newvar = cond(condition1, 1, cond(condition2, 2, cond(condition3, 3, .)))
// 或使用egen
egen newvar = group(condition1 condition2 condition3)
```

## 自动修复能力

### 修复级别分类

| 级别 | 说明 | 示例 |
|------|------|------|
| 自动修复 | 无需确认，直接修复 | 拼写错误、格式问题 |
| 建议修复 | 提供修复选项 | 效率优化、代码结构 |
| 需确认修复 | 涉及逻辑变更 | 条件逻辑、条件判断 |

### 常见修复操作

#### 1. 拼写修正

```stata
// 检测到
regresss y x

// 修复为
regress y x
```

#### 2. 逻辑运算符修正

```stata
// 检测到
if a > 0 and b < 10

// 修复为
if a > 0 & b < 10
```

#### 3. 缺失值处理增强

```stata
// 检测到
gen total = x1 + x2

// 修复为
gen total = rowtotal(x1 x2)
```

## 使用场景

本技能适用于以下场景：

1. **代码审查**：在提交或分享代码前进行自动检查
2. **错误调试**：快速定位和修复Stata代码中的错误
3. **代码重构**：优化既有代码的结构和性能
4. **学习辅助**：帮助Stata初学者理解和避免常见错误
5. **批量处理**：对多个Stata脚本进行一致性检查

## 输入格式要求

用户提交代码时，应提供：

1. **Stata代码文本**：完整的do文件内容或代码片段
2. **数据文件信息**（可选）：如果有特定的数据依赖
3. **检查范围**：语法检查、逻辑检查、全部检查
4. **修复偏好**：仅报告、自动修复、交互式修复

## 输出格式

技能将返回以下格式的检测报告：

### 检测结果概览

```
检测完成！
发现错误：3个
发现警告：5个
已自动修复：2个
待确认修复：1个
```

### 详细报告

```
[错误] 第15行：变量"yra"未定义
  建议：是否修正为"year"？

[警告] 第23行：循环可能存在无限循环风险
  建议：检查循环终止条件

[信息] 第45行：建议使用rowtotal()处理缺失值
  当前：gen total = x1 + x2 + x3
  建议：gen total = rowtotal(x1 x2 x3)
```

## 最佳实践建议

### 代码组织

```
好的实践：
1. 在脚本开头设置全局环境（clear all, set more off）
2. 使用清晰的注释分隔代码区块
3. 为变量和宏使用描述性名称
4. 尽早处理缺失值
5. 在关键步骤后进行数据验证
```

### 错误处理

```
推荐模式：
cap program drop myprogram
program myprogram
    version 14.1
    syntax varlist

    // 错误处理
    cap confirm variable `varlist'
    if _rc {
        display as error "变量不存在"
        exit 111
    }

    // 主逻辑
    // ...
end
```

### 可重复性

```
确保代码可重复的关键：
1. 使用相对路径而非绝对路径
2. 设置随机数种子（set seed）
3. 记录数据版本和来源
4. 在代码中包含版本信息
```

## 高级功能

### 自定义检查规则

用户可以添加自定义检查规则：

```
用户定义规则：
- 检查特定变量命名模式
- 验证数据范围
- 检查模型假设
- 自定义警告阈值
```

### 批量检查

支持对整个项目目录进行检查：

```
检查范围：
├── do/
│   ├── data_cleaning.do
│   ├── regression_analysis.do
│   └── sensitivity_analysis.do
└── output/

批量检查将分析所有.do文件的一致性和潜在问题。
```

## 总结

Stata代码检测与自动修复技能是一个全面的代码质量保障工具。它不仅能够检测语法错误，还能识别逻辑问题、数据处理缺陷，并提供自动化的修复方案。通过使用本技能，用户可以显著提高Stata代码的质量、可维护性和执行效率。
