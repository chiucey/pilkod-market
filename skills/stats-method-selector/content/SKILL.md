---
name: stats-method-selector
description: 按数据类型与研究问题引导选择合适的统计方法与检验 | Guide selection of appropriate statistical methods/tests by data type and question.
license: MIT
skill-author: 马拉AI（malaedu.com）
---

# 统计方法选择 Statistical Method Selector

## 使用场景 When to Use
- 数据要开始分析了，但不确定该用哪种检验/模型。
- 需要一份"为什么选这个方法"的可写进论文的说明。

## 能力 What it does
1. 通过提问澄清：结局变量类型（连续/计数/二分类/生存/有序）、组数、配对与否、样本量级、分布假设、协变量。
2. 推荐候选方法（如 t 检验/ANOVA/非参数/回归族/生存分析/混合效应等）与前提假设检查。
3. 提示多重比较校正、效应量与置信区间报告、常见误用。
4. 给出对应软件的实现指引（R / Python），但**不替代统计学家审阅**。

## 说明 Note
- 本 skill 给方法学引导，不对具体个案数据下结论；关键分析建议由持证统计人员复核。

## 用法 Usage
> 「用 stats-method-selector：我有两组连续变量、非正态、样本各 30，比较差异该用什么？」
