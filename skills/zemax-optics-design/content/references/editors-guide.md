# OpticStudio 编辑器使用指南

## 编辑器系统概述

OpticStudio 提供 7 个核心编辑器，用于定义和管理光学系统的各个参数。

## 1. 镜头数据编辑器 (Lens Data Editor, LDE)

### 功能
定义序列模式光学系统的所有表面参数。

### 列说明

| 列名 | 英文名称 | 说明 |
|------|----------|------|
| 表面# | Surf | 表面编号（0=物面，1=第一表面） |
| 半径 | Radius | 曲率半径 |
| 厚度 | Thickness | 表面到下一表面的距离 |
| 材料 | Glass | 透镜材料或"空气" |
| 半口径 | Semi-Diameter | 表面半尺寸 |
| 圆锥系数 | Conic | 圆锥常数 |
| 求解 | Solve | 求解类型 |
| 注释 | Comment | 备注信息 |

### 特殊表面类型

| 类型 | 说明 |
|------|------|
| 标准面 | Standard |
| 非球面 | Asphere |
| 二元光学 | Biconic Aspheric |
| 衍射光栅 | Diffraction Grating |
| 坐标断点 | Coordinate Break |
| 渐变折射率 | Gradient Index |
| 混合模式 | Mixed Mode |

### 求解类型

| 求解 | 说明 |
|------|------|
| 变量 (V) | 优化变量 |
| 拾取 (P) | 从其他参数拾取 |
| 求解 (S) | 自动计算 |
| 固定 (F) | 固定值 |

### 常用操作

```python
# 添加表面
TheSystem.LDE.AddSurface()

# 删除表面
TheSystem.LDE.RemoveSurfaceAt(3)

# 设置变量
TheSystem.LDE.GetSurfaceAt(2).Radius = 50.0
TheSystem.LDE.GetSurfaceAt(2).MakeRadiusVariable()

# 设置材料
TheSystem.LDE.GetSurfaceAt(3).Glass = "N-BK7"
```

## 2. 非序列元件编辑器 (Non-Sequential Component Editor, NSCE)

### 功能
定义非序列光学元件、光源和探测器。

### 列说明

| 列名 | 说明 |
|------|------|
| # | 元件编号 |
| 类型 | 元件类型 |
| X 位置 | X 坐标 |
| Y 位置 | Y 坐标 |
| Z 位置 | Z 坐标 |
| 倾斜 X | X 方向倾斜 |
| 倾斜 Y | Y 方向倾斜 |
| 倾斜 Z | Z 方向倾斜 |
| 材料 | 元件材料 |

### 元件类型

| 类型 | 说明 |
|------|------|
| Source Point | 点光源 |
| Source Diode | 二极管光源 |
| Source Ellipse | 椭圆光源 |
| Lens | 透镜 |
| Mirror | 反射镜 |
| Diffuser | 散射体 |
| Detector | 探测器 |

## 3. 视场数据编辑器 (Field Data Editor, FDE)

### 功能
定义视场点的位置和权重。

### 视场类型

| 类型 | 说明 |
|------|------|
| 角度 | Angle |
| 物高 | Object Height |
| 近轴像高 | Paraxial Image Height |
| 真实像高 | Real Image Height |

### 列说明

| 列名 | 说明 |
|------|------|
| # | 视场编号 |
| X 视场 | X 位置 |
| Y 视场 | Y 位置 |
| 权重 | Weight |
| 渐晕 X | X 渐晕因子 |
| 渐晕 Y | Y 渐晕因子 |
| 渐晕角度 | Vignetting Angle |

### 设置示例

```python
# 设置 5 个视场点
fields = TheSystem.SystemData.Fields
fields.SetFieldType(FieldType.Angle)
fields.AddField(0, 0, 1.0)      # 0° 视场
fields.AddField(0, 5, 1.0)     # 5° 视场
fields.AddField(0, 10, 1.0)    # 10° 视场
fields.AddField(0, 15, 1.0)     # 15° 视场
fields.AddField(0, 20, 1.0)    # 20° 视场
```

## 4. 波长数据编辑器 (Wavelength Data Editor)

### 功能
定义工作波长及其权重。

### 列说明

| 列名 | 说明 |
|------|------|
| # | 波长编号 |
| 波长 | Wavelength (μm) |
| 权重 | Weight |

### 标准波长

| 波长 | 说明 |
|------|------|
| 0.6563 | C (红色) |
| 0.5876 | d (黄色) |
| 0.4861 | F (蓝色) |
| 0.5500 | e (绿色) |

### 设置示例

```python
# 设置标准三波长
wavelengths = TheSystem.SystemData.Wavelengths
wavelengths.AddWavelength(0.6563, 1.0)  # C
wavelengths.AddWavelength(0.5876, 1.0)  # d
wavelengths.AddWavelength(0.4861, 1.0)  # F
wavelengths.SetPrimaryWavelength(2)      # d 作为主波长
```

## 5. 多重结构编辑器 (Multiple Configuration Editor, MCE)

### 功能
定义多重结构、变焦系统和环境参数。

### 多重结构操作数

| 操作数 | 说明 |
|--------|------|
| CONF | 结构编号 |
| TEMP | 温度 |
| PRES | 压力 |
| THIC | 厚度 |
| RADI | 曲率半径 |

### 应用场景

| 场景 | 说明 |
|------|------|
| 变焦镜头 | 不同焦距配置 |
| 对焦系统 | 不同物距 |
| 环境变化 | 不同温度/压力 |
| 制造补偿 | 补偿器设置 |

### 示例：变焦镜头

```
CONF  1  2  3        # 3 个结构
THIC 3  10.0 15.0 20.0  # 表面 3 厚度变化
THIC 5  5.0  8.0  12.0  # 表面 5 厚度变化
```

## 6. 评价函数编辑器 (Merit Function Editor, MFE)

### 功能
定义优化目标和约束条件。

### 列说明

| 列名 | 说明 |
|------|------|
| # | 操作数编号 |
| 类型 | 操作数类型 |
| 表面 | 参考表面 |
| 参数 1 | 操作数参数 1 |
| 参数 2 | 操作数参数 2 |
| 目标 | Target Value |
| 权重 | Weight |
| 误差 | Current Error |

### 常用操作数

#### 光学性能

| 操作数 | 说明 |
|--------|------|
| EFFL | 有效焦距 |
| WFNO | 工作 F/# |
| PMNA | 主光线入射角 |

#### 边缘厚度

| 操作数 | 说明 |
|--------|------|
| MNEA | 最小边缘空气间隙 |
| MNET | 最小边缘厚度 |
| MPET | 最小正透镜边缘厚度 |
| MNCT | 最小中心厚度 |

#### 像质控制

| 操作数 | 说明 |
|--------|------|
| OPDC | 光程差 |
| REAY | 光线 Y 坐标 |
| REAX | 光线 X 坐标 |

#### 像差控制

| 操作数 | 说明 |
|--------|------|
| SAXY | 子午球差 |
| SASX | 弧矢球差 |
| COMA | 彗差 |

### 示例：标准镜头评价函数

```
# 焦距约束
EFFL 1 0 0 50.0 1.0

# F/# 约束
WFNO 1 0 0 5.0 1.0

# 球差控制
SAXY 1 0 0 0.0 0.5

# 彗差控制
COMA 1 0 0 0.0 0.5

# 边缘厚度
MPET 2 0 0 2.0 0.1
```

## 7. 公差数据编辑器 (Tolerance Data Editor, TDE)

### 功能
定义公差参数和分析配置。

### 公差类型

| 类型 | 说明 |
|------|------|
| TFRN | 曲率半径公差 |
| TTHI | 厚度公差 |
| TSDX | X 偏心公差 |
| TSDY | Y 偏心公差 |
| TIRR | 不规则公差 |
| TIND | 折射率公差 |
| TABB | 阿贝数公差 |

### 列说明

| 列名 | 说明 |
|------|------|
| # | 公差编号 |
| 表面 | 参考表面 |
| 参数 | 公差参数 |
| 类型 | 公差类型 |
| 修饰符 | 修饰符 |
| 值 | 公差值 |
| 补偿器 | 补偿表面 |

### 示例：典型公差设置

```
# 表面 2 偏心公差
TSDX 2  0.025
TSDY 2  0.025

# 表面 3 厚度公差
TTHI 3  0.050

# 折射率公差
TIND 3  0.0005

# 后焦距补偿器
COMP 0  0.500
```

## 编辑器使用技巧

### 快捷操作

| 操作 | 快捷键 |
|------|--------|
| 新建文件 | Ctrl+N |
| 打开文件 | Ctrl+O |
| 保存 | Ctrl+S |
| 撤销 | Ctrl+Z |
| 重做 | Ctrl+Y |
| 复制 | Ctrl+C |
| 粘贴 | Ctrl+V |

### 变量设置

```python
# 批量设置变量
for surf in range(2, 8):
    lde = TheSystem.LDE
    lde.GetSurfaceAt(surf).MakeRadiusVariable()
    lde.GetSurfaceAt(surf).MakeThicknessVariable()

# 移除所有变量
TheSystem.Optics.MeritFunctionEditor.RemoveAllVariables()
```

### 数据导入导出

```python
# 导出 LDE 数据
TheSystem.SaveData(@"C:\export.txt", DataFileTypes.LDE)

# 导入 LDE 数据
TheSystem.LoadData(@"C:\import.txt", DataFileTypes.LDE)
```

### 编辑器显示设置

```python
# 设置列显示
editor.ShowColumn("TCE", True)    # 显示 TCE 列
editor.ShowColumn("Param1", True) # 显示参数列

# 设置单位
editor.LensUnits = LensUnits.Millimeters
```
