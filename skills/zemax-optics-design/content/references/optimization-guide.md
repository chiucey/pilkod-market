# 优化技巧指南

## 优化选项卡概述

OpticStudio 优化选项卡提供两种模式：

- **序列模式优化选项卡** (Sequential UI Mode)
- **非序列模式优化选项卡** (Non-Sequential UI Mode)

## 手动调整组

### 快速聚焦 (Quick Focus)

**用途**：快速找到最佳焦点位置。

**使用方法**：
1. 选择要调整的表面
2. 点击快速聚焦
3. 系统自动调整厚度使焦点位于指定位置

**适用场景**：
- 初步对焦
- 快速检查
- 批量处理前准备

### 滑块 (Slider)

**用途**：实时预览参数变化效果。

**功能**：
- 连续调整参数
- 实时更新视图
- 可视化参数影响

### 可视化优化器 (Visual Optimizer)

**用途**：图形化展示优化过程。

**功能**：
- 参数范围显示
- 评价函数可视化
- 约束条件图示

## 自动优化组

### 评价函数编辑器 (Merit Function Editor)

**功能**：定义优化目标和约束条件。

#### 常用操作数分类

##### 光学系统参数

| 操作数 | 说明 | 参数格式 |
|--------|------|----------|
| EFFL | 有效焦距 | (表面, 0, 0, 目标, 权重) |
| WFNO | 工作 F/# | (表面, 0, 0, 目标, 权重) |
| PMNA | 主光线入射角 | (表面, 0, 0, 目标, 权重) |
| EFLX | X 方向焦距 | - |
| EFLY | Y 方向焦距 | - |

##### 厚度控制

| 操作数 | 说明 | 参数格式 |
|--------|------|----------|
| MNEA | 最小边缘空气隙 | (表面, 0, 0, 目标, 权重) |
| MNET | 最小边缘厚度 | (表面, 0, 0, 目标, 权重) |
| MPET | 最小正透镜边缘厚度 | (表面, 0, 0, 目标, 权重) |
| MNCT | 最小中心厚度 | (表面, 0, 0, 目标, 权重) |
| MXCT | 最大中心厚度 | (表面, 0, 0, 目标, 权重) |

##### 像差控制

| 操作数 | 说明 | 参数格式 |
|--------|------|----------|
| OPDC | 光程差 | (表面, 波长, 视场, 目标, 权重) |
| SAXY | 子午球差 | (视场, 0, 0, 目标, 权重) |
| SASX | 弧矢球差 | (视场, 0, 0, 目标, 权重) |
| COMA | 彗差 | (视场, 0, 0, 目标, 权重) |
| ASTI | 像散 | (视场, 0, 0, 目标, 权重) |
| DIST | 畸变 | (视场, 0, 0, 目标, 权重) |

##### 光线控制

| 操作数 | 说明 | 参数格式 |
|--------|------|----------|
| REAY | 光线 Y 坐标 | (表面, 归一化 X, 归一化 Y, 目标, 权重) |
| REAX | 光线 X 坐标 | - |
| REAYB | 光线 Y 坐标（另一组） | - |

##### 色差控制

| 操作数 | 说明 | 参数格式 |
|--------|------|----------|
| LACL | 位置色差 | (表面, 0, 0, 目标, 权重) |
| MACL | 倍率色差 | (视场, 0, 0, 目标, 权重) |

### 优化向导 (Optimization Wizard)

**功能**：快速构建标准评价函数。

**向导选项**：
| 选项 | 说明 |
|------|------|
| RMS 评价标准 | 基于 RMS 值的评价 |
| PTB 评价标准 | 基于 PTB 的评价 |
| GFR 评价标准 | 基于几何的评价 |
| 波长权重 | 各波长相对权重 |
| 视场权重 | 各视场相对权重 |

**使用流程**：
```
1. 打开评价函数编辑器
2. 点击优化向导
3. 选择评价标准类型
4. 设置采样和范围
5. 确定波长和视场权重
6. 生成评价函数
```

### 执行优化 (Optimize!)

**局部优化算法**：

| 算法 | 说明 |
|------|------|
| DLS (阻尼最小二乘法) | 快速局部收敛 |
| Vogel | 另一种局部算法 |

**优化设置**：
| 参数 | 说明 |
|------|------|
| 循环次数 | 最大迭代次数 |
| 增量阈值 | 收敛判断阈值 |
| 变量步长 | 初始步长 |

**优化策略**：
1. **粗优化**：大步长，快速收敛
2. **精优化**：小步长，精细调整
3. **微调**：收敛判断，高精度

### 变量设置

**快捷操作**：
| 功能 | 说明 |
|------|------|
| 设全部半径为变量 | Set All Radii Variable |
| 设全部厚度变量 | Set All Thickness Variable |
| 移除所有变量 | Remove All Variables |

**单个变量设置**：
1. 在 LDE 中选择表面
2. 设置求解类型为"变量"(V)
3. 或使用快捷菜单

## 全局优化组

### 全局优化 (Global Optimizer)

**用途**：在设计空间中搜索全局最优解。

**特点**：
- 跳出局部最优
- 长时间运行
- 资源密集

**使用建议**：
1. 先运行局部优化
2. 启动全局优化
3. 定期检查进度
4. 保存中间结果

### 锤形优化 (Hammer Optimizer)

**原理**：结合随机和确定性方法的全局优化。

**特点**：
- 更高效的全局搜索
- 更好的多样性
- 适合复杂设计

### 玻璃替换模板

**功能**：在优化过程中替换玻璃材料。

**设置选项**：
| 选项 | 说明 |
|------|------|
| 首选玻璃库 | 选择使用的玻璃库 |
| 替换次数 | 优化中的替换频率 |
| 玻璃约束 | 成本/可用性约束 |

## 优化工具组

### 寻找最佳非球面 (Find Best Asphere)

**功能**：评估添加非球面的效果。

**流程**：
1. 选择候选表面
2. 系统自动添加非球面系数
3. 运行局部优化
4. 比较优化前后性能

### 非球面类型转换 (Convert Asphere Types)

**功能**：在不同非球面定义之间转换。

**支持的类型**：
| 类型 | 说明 |
|------|------|
| 标准非球面 | Standard Asphere |
| 奇次非球面 | Odd Asphere |
| 双非球面 | Biconic Asphere |
| Zernike 非球面 | Zernike Asphere |

### 库存镜头匹配工具 (Stock Lens Matching)

**功能**：在库存镜头中寻找匹配设计。

**使用流程**：
1. 定义设计需求
2. 设置搜索条件
3. 系统搜索匹配镜头
4. 评估匹配度

## 优化策略

### 初始结构选择

**选择原则**：
```
1. 类似设计改造（优先）
2. 专利/文献参考
3. 解析解计算
4. 库镜头修改
5. 随机初始结构（最后选择）
```

### 分步优化法

```
阶段 1：粗优化
├── 较少变量（主要曲率）
├── 较简单 MF
├── 大步长
└── 快速收敛

阶段 2：精优化
├── 所有变量
├── 完整 MF
├── 细化约束
└── 局部优化

阶段 3：微调
├── 精细边界
├── 局部搜索
└── 收敛判断
```

### 变量分组策略

```
第一组：主要曲率
第二组：厚度
第三组：非球面系数
第四组：间隙调整
第五组：材料参数（如果允许）
```

## 常见问题解决

### 优化发散

**原因**：
- 初始结构太差
- 步长太大
- 约束冲突
- 变量超出物理范围

**解决**：
```
1. 减小步长
2. 放宽约束
3. 改变初始值
4. 简化优化问题
5. 分步优化
```

### 局部最优

**识别**：
- 多次运行结果相同
- 评价函数值不理想
- 无法改进

**解决**：
```
1. Hammer 优化
2. 随机重启
3. 改变变量组合
4. 添加/移除变量
5. 修改初始结构
```

### 边界冲突

**原因**：
- 透镜过薄
- 零件干涉
- 物理不可实现

**解决**：
```
1. 设置合理的边界
2. 使用惩罚函数
3. 添加边界约束操作数
4. 手动调整后再优化
```

## 多重结构优化

### 变焦镜头优化

**策略**：
```
1. 定义所有结构（共焦或变焦）
2. 设置每个结构的变量
3. MFE 中使用 CONF 操作数
4. 同时优化所有结构
5. 使用结构权重
```

### 热优化

**无热化镜头**：
```python
# 使用热拾取求解
surface.SetThermalPickupSolver(
    referenceSurface=1,
    temperatureDelta=50
)
```

## 高级技巧

### 自适应优化

```python
while not converged:
    current_error = system.MFE.CalculateMeritFunction()
    if improving:
        continue
    else:
        adjust_weights()
        reset_algorithm()
        # 可能需要添加新变量
```

### 多目标优化

```python
# Pareto 前沿分析
pareto_solutions = []
for weight in weights:
    solution = optimize(weight)
    pareto_solutions.append(solution)

# 选择最佳平衡点
best_solution = select_pareto_optimal(pareto_solutions)
```

### 约束驱动设计

```python
# 以约束为核心的优化
for constraint in constraints:
    system.MFE.AddOperand(constraint)

# 自动满足所有约束
optimization.Run()
```

## 优化质量评估

### 收敛判断

| 指标 | 说明 |
|------|------|
| 评价函数变化 | < 阈值 |
| 变量变化 | < 阈值 |
| 迭代次数 | 达到上限 |

### 结果验证

```
1. 检查评价函数值
2. 验证关键参数
3. 运行完整分析
4. 对比优化前后
5. 检查约束满足
```

## ZOS-API 优化示例

```python
# Python 示例
import clr
clr.AddReference("ZOSAPI")

from ZOSAPI import ZOSAPI

# 连接
app = ZOSAPI.ZOSAPI_Application.CreateApplication()
system = app.PrimarySystem

# 设置变量
system.LDE.GetSurfaceAt(2).MakeRadiusVariable()
system.LDE.GetSurfaceAt(3).MakeThicknessVariable()

# 构建评价函数
mfe = system.Optics.MeritFunctionEditor
mfe.AddNewOperand()  # EFFL
mfe.SetOperandData(1, Target=50.0, Weight=1.0)

# 执行优化
optimization = mfe.CreateOptimization()
optimization.Algorithm = OptimizationAlgorithms.DampedLeastSquares
optimization.AddDefaultMeritFunction()
optimization.Run()
```
