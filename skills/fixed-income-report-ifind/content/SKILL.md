---
name: fixed-income-report-ifind
description: 全自动生成固定收益周报（iFind数据版）。当用户要求自动生成周报、连接iFind数据、或提到"自动更新周报"、"iFind数据"时使用。
---

# 固定收益周报生成器（iFind数据版）

## 触发条件
用户要求连接iFind数据自动生成固定收益周报时使用。

## 前置条件
- MaxClaw已配置iFind连接
- 需要调用`get_all_secrets`获取iFind凭证

## 工作流程

### 阶段1：确认日期范围
1. 用户指定周报日期（如"第16周"）
2. 确认该周的周一至周五日期范围
3. 规则：每周从周一到周日，如果涉及调休则包含周末调整

### 阶段2：调用iFind获取数据
使用`tonghuashun-ifind`技能获取以下数据：

#### 2.1 OMO公开市场操作
- 使用iFind获取该周逆回购操作数据
- 获取MLF、国库定存等操作
- 计算净投放金额

#### 2.2 国债收益率数据
- 获取1Y、3Y、5Y、7Y、10Y、30Y国债收益率
- 获取1周、2周、4周变动数据
- 生成收益率曲线

#### 2.3 信用债/城投债数据
- 获取不同评级(AAA/AA+/AA)的城投债收益率
- 获取历史分位数数据
- 计算1周、2周、4周变动

#### 2.4 同业存单数据
- 获取主要期限CD收益率
- 获取发行量和融资成本

#### 2.5 转债行业数据
- 获取各行业可转债涨跌幅
- 排名表现最好的行业

### 阶段3：生成图表
使用matplotlib生成4个图表：
- `extract/charts/bond_yield.png` - 国债收益率曲线
- `extract/charts/rate_change.png` - 资金利率变动
- `extract/charts/spread_heatmap.png` - 城投债利差热力图
- `extract/charts/cb_industry.png` - 转债行业涨跌幅

### 阶段4：更新PPT幻灯片
更新以下幻灯片添加图表：
- slide-04.js（资金面）→ 添加rate_change.png
- slide-05.js（利率债）→ 添加bond_yield.png
- slide-07.js（信用债）→ 添加spread_heatmap.png
- slide-10.js（转债行业）→ 添加cb_industry.png

### 阶段5：编译输出
运行`node compile.js`生成最终PPT文件到`slides/output/`目录。

## 文件位置
- 幻灯片源码：`/workspace/slides/`
- 输出目录：`/workspace/slides/output/`
- 图表目录：`/workspace/slides/extract/charts/`

## 数据源映射
| PPT页面 | iFind数据 |
|---------|----------|
| Slide-03 宏观经济 | PMI等宏观数据 |
| Slide-04 资金面 | OMO逆回购、货币市场利率 |
| Slide-05 利率债 | 国债收益率曲线 |
| Slide-07 信用债 | 城投债利差 |
| Slide-08 同业存单 | CD发行数据 |
| Slide-10 转债 | 行业涨跌幅 |

## 关键函数
使用`tonghuashun-ifind`技能的以下功能：
- `fn_经济数据_宏观数据` - 获取宏观数据
- `fn_债券数据_利率债数据` - 获取利率债数据
- `fn_信用债数据_城投债` - 获取城投债数据
- `fn_可转债数据_行业数据` - 获取转债数据