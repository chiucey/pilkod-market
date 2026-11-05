---
name: zemax-optics-design
description: 光学设计软件 ZEMAX OpticStudio 操作技能。当用户要求进行 ZEMAX 光学设计、透镜设计、光学系统分析、像差分析、光线追迹、公差分析、ZMX 文件处理、光学性能评估，或需要批量处理光学设计文件、生成光学报告时使用。触发短语包括："ZEMAX"、"OpticStudio"、"光学设计"、"透镜设计"、"光线追迹"、"光学分析"、"像差分析"、"公差分析"、"镜头设计"、"光学系统"。
---

# ZEMAX OpticStudio 光学设计操作技能

## 技能概述

本技能提供 ZEMAX OpticStudio 光学设计软件的完整操作能力，基于 OpticStudio 19.4 帮助手册，支持从基础透镜设计到高级光学系统分析的全流程工作。

## OpticStudio 主界面结构

### 主要选项卡

| 选项卡 | 英文名称 | 主要功能 |
|--------|----------|----------|
| 文件 | THE FILE TAB | 文件操作、导入导出、存档管理 |
| 设置 | THE SETUP TAB | 系统配置、编辑器、视图、系统诊断 |
| 分析 | THE ANALYZE TAB | 光学分析、像质评估、报告生成 |
| 优化 | THE OPTIMIZE TAB | 手动调整、自动优化、全局优化 |
| 公差 | THE TOLERANCE TAB | 公差分析、加工图纸、数据导出 |
| 库 | THE LIBRARIES TAB | 材料库、镜头库、膜层库、光源库 |
| 零件设计 | THE PART DESIGNER TAB | CAD 零件设计 |
| 编程 | THE PROGRAMMING TAB | ZPL 宏、ZOS-API.NET、扩展程序 |

## 核心功能

### 1. 文件操作与格式

#### 支持的文件格式

| 格式 | 说明 |
|------|------|
| .zmx | OpticStudio 主文件（镜头设计文件） |
| .zda | 配置文件 |
| .cfg | 窗口界面配置文件 |
| .zar | Zemax 存档文件 |
| .zpo/.zso | 零件设计文件 |

#### 文件操作功能

- 新建/打开/保存设计文件（快捷键 Ctrl+N/O/S）
- 创建/加载存档文件
- CAD 文件导出（STEP、IGES、SAT、STL）
- 文件比较器
- CODE V 文件转换导入

### 2. 编辑器系统

OpticStudio 提供 7 个核心编辑器：

| 编辑器 | 英文名称 | 功能 |
|--------|----------|------|
| 镜头数据编辑器 | Lens Data Editor (LDE) | 定义透镜表面、厚度、材料 |
| 非序列元件编辑器 | Non-Sequential Component Editor (NSCE) | 定义非序列光学元件 |
| 视场数据编辑器 | Field Data Editor (FDE) | 定义视场点、类型、大小 |
| 波长数据编辑器 | Wavelength Data Editor | 定义波长和权重 |
| 多重结构编辑器 | Multiple Configuration Editor (MCE) | 定义多重结构和变焦 |
| 评价函数编辑器 | Merit Function Editor (MFE) | 定义优化目标和约束 |
| 公差数据编辑器 | Tolerance Data Editor (TDE) | 定义公差参数 |

### 3. 光学系统分析

#### 像质分析组 (Image Quality)

| 分析类型 | 英文名称 | 用途 |
|----------|----------|------|
| 光线迹点 | Ray Fan | 分析像差引起的像点偏移 |
| 像差分析 | Aberration Analysis | 赛德尔系数分析 |
| 点扩散函数 | Point Spread Function (PSF) | 衍射极限分析 |
| MTF 曲线 | Modulation Transfer Function | 调制传递函数分析 |
| RMS | RMS | 均方根分析 |
| 圈入能量 | Encircled Energy | 能量集中度分析 |
| 扩展图像分析 | Extended Scene Analysis | 场景模拟分析 |

#### 偏振与表面物理组

| 分析类型 | 英文名称 |
|----------|----------|
| 偏振分析 | Polarization |
| 表面分析 | Surface |
| 膜层分析 | Coatings |

#### 激光与光纤组

| 分析类型 | 英文名称 |
|----------|----------|
| 物理光学传播 | Physical Optics Propagation (POP) |

#### 报告组

| 报告类型 | 英文名称 |
|----------|----------|
| 表面数据报告 | Surface Data Report |
| 系统数据报告 | System Data Report |
| 分类数据报告 | Prescribed Data Report |
| 系统数据摘要 | System Summary |
| 基面数据 | Cardinal Data |

### 4. 透镜设计与优化

#### 手动调整工具

- 快速聚焦 (Quick Focus)
- 快速调整 (Quick Adjust)
- 滑块 (Slider)
- 可视化优化器 (Visual Optimizer)

#### 自动优化

- 评价函数编辑器
- 优化向导 (Optimization Wizard)
- 执行优化 (Optimize!)
- 变量设置（半径、厚度、非球面系数）

#### 全局优化

- 全局优化 (Global Optimizer)
- 锤形优化 (Hammer Optimizer)
- 玻璃替换模板

### 5. 公差分析

#### 公差分析工具

- 公差数据编辑器
- 公差分析向导 (Tolerancing Wizard)
- 公差分析 (Tolerancing)
- 公差脚本 (Tolerance Script)
- 公差报告 (Tolerance Report)

#### 分析类型

- 灵敏度分析 (Sensitivity Analysis)
- RSS 估算 (RSS Estimated Changes)
- 反灵敏度分析 (Inverse Sensitivity Analysis)
- 蒙特卡洛分析 (Monte Carlo Analysis)

### 6. 编程接口 (ZOS-API)

#### 支持的编程环境

| 环境 | 说明 |
|------|------|
| Python | 通过 Python.NET 连接 |
| C# | ZOS-API.NET |
| MATLAB | ZOS-API.NET |
| ZPL | 内置宏语言 |

#### 自定义扩展

- 自定义分析 (User Analyses)
- 自定义扩展 (User Extensions)

## 工作流程

### 标准分析流程

```
1. 打开/创建 .zmx 文件
2. 配置系统参数（系统选项）
   - 系统孔径（入瞳直径、F/#）
   - 视场定义
   - 波长配置
3. 在编辑器中定义透镜
4. 运行光学分析
5. 提取分析结果
6. 生成报告
```

### 透镜设计流程

```
1. 定义系统规格
   - 有效焦距 (EFL)
   - F/#
   - 视场角
   - 工作波长
2. 选择初始结构
3. 设置优化变量
4. 构建评价函数
5. 执行优化（局部 → 全局）
6. 验证光学性能
7. 公差分析
8. 导出制造图纸
```

### 公差分析流程

```
1. 打开已优化的设计
2. 设置公差数据编辑器
   - 选择公差类型
   - 定义公差值
3. 设置补偿器
4. 运行公差分析
5. 执行蒙特卡洛模拟
6. 评估良率和风险
```

## 使用示例

### 基本命令

**文件操作：**
- "打开 /path/to/lens.zmx 文件"
- "保存当前设计为 new_lens.zmx"
- "提取系统数据摘要"

**系统配置：**
- "设置入瞳直径为 25mm"
- "添加 5 个视场点（0°, 5°, 10°, 15°, 20°）"
- "配置标准波长 C、d、F"

**透镜编辑：**
- "在第 3 面设置曲率半径为变量"
- "将第 5 面材料改为 N-BK7"
- "添加一个新的透镜表面"

**光学分析：**
- "运行 MTF 分析"
- "生成点列图"
- "计算赛德尔系数"
- "运行 Ray Fan 分析"

**优化：**
- "使用优化向导设置评价函数"
- "执行局部优化"
- "运行全局优化"
- "替换玻璃材料"

**公差分析：**
- "设置灵敏度分析"
- "运行蒙特卡洛模拟（1000 次）"
- "生成公差报告"

### 批量处理

- "批量分析 folder/ 目录下的所有 ZMX 文件"
- "提取所有设计的 EFL 和 F/#"
- "对比多个镜头的 MTF 性能"

## 系统参数说明

### 关键术语

| 中文术语 | 英文术语 | 说明 |
|----------|----------|------|
| 入瞳直径 | Entrance Pupil Diameter | 系统光阑直径 |
| 有效焦距 | Effective Focal Length | 系统焦距 |
| 工作 F/# | Working F/# | 像空间 F/# |
| 主波长 | Primary Wavelength | 主要参考波长 |
| 视场角 | Field Angle | 物点与光轴的夹角 |
| 后焦距 | Back Focal Length | 最后表面到像面距离 |
| 全长 | Total Track | 第一表面到像面距离 |
| 斯特列尔比 | Strehl Ratio | 波前质量评估 |
| 衍射极限 | Diffraction Limit | 理论极限性能 |

### 波长配置

标准三波长（可见光）：
- C (656.3nm) - 红色
- d (587.6nm) - 黄色
- F (486.1nm) - 蓝色

## 参考资源

详细的技术规范请参阅 `references/` 目录：

- `editors-guide.md` - 编辑器使用详解（LDE、NSCE、MFE、TDE 等）
- `api-reference.md` - ZOS-API.NET/Python 接口参考
- `analysis-types.md` - 光学分析类型详解
- `optimization-guide.md` - 优化技巧指南
- `tolerance-analysis.md` - 公差分析方法
- `glossary.md` - 光学术语词汇表
