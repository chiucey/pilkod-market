# Abaqus Energy Post-processing Module

模块化的Abaqus后处理脚本，用于在柱坐标系下计算能量分量。

## 模块结构

```
abaqus-python-prepost/
├── coord_transform.py      # 坐标变换模块
├── odb_reader.py           # ODB读取模块
├── energy_calculator.py     # 能量计算模块
├── config.py               # 配置文件
├── main_postprocess.py      # 主程序
└── README.md               # 本文件
```

## 模块说明

### 1. coord_transform.py
坐标变换模块，包含：
- `cartesian_to_cylindrical()` - 笛卡尔坐标转柱坐标
- `rotate_stress_to_cylindrical()` - 应力张量旋转
- `rotate_engineering_strain_to_cylindrical()` - 应变张量旋转（关键：处理工程应变与张量应变的转换）
- `get_element_centroid_rotation()` - 获取单元质心旋转角

**关键修复**：
- 原始代码将应变当作应力进行变换
- 本模块正确处理工程应变（LE）与张量应变的转换

### 2. odb_reader.py
ODB读取模块，包含：
- `ODBReader` 类 - ODB读取封装
- `build_element_centroid_map()` - 构建单元质心坐标映射
- `get_field_data_at_frame()` - 获取帧数据
- `get_element_centroid_for_integration_point()` - 获取积分点对应的单元质心

**关键修复**：
- 原始代码直接使用节点坐标（COORD）与积分点数据（应力/应变）匹配
- 本模块使用单元质心坐标进行匹配，解决节点-积分点不对应问题

### 3. energy_calculator.py
能量计算模块，包含：
- `EnergyAccumulator` 类 - 能量累加器
- `calculate_frame_energy_delta()` - 计算帧能量增量
- `calculate_integration_point_energy_increment()` - 计算单个积分点能量
- `calculate_error()` - 计算相对误差

**功能**：
- 柱坐标系下的能量分量计算
- 梯形积分法则
- 累加历史记录

### 4. config.py
配置文件，包含所有可调整参数。

### 5. main_postprocess.py
主程序，整合所有模块进行能量后处理。

## 使用方法

### 方式一：命令行运行

```bash
# 在Abaqus CAE中运行
abaqus python main_postprocess.py

# 指定ODB文件名
abaqus python main_postprocess.py Job-Name

# 指定ODB和输出文件
abaqus python main_postprocess.py Job-Name Output.xls
```

### 方式二：在Abaqus CAE中导入

```python
# 在Abaqus CAE的Python环境中
import sys
sys.path.append('/path/to/module/')

import main_postprocess
main_postprocess.ODB_NAME = 'Your-Job-Name'
main_postprocess.process_energy_calculation()
```

### 方式三：直接导入模块使用

```python
from odb_reader import ODBReader
from coord_transform import rotate_stress_to_cylindrical
from energy_calculator import EnergyAccumulator

# 你的自定义处理代码
reader = ODBReader('Your-ODB-Name')
# ... 自定义处理
```

## 输出格式

输出Excel文件包含以下列：
| 列名 | 说明 |
|------|------|
| Frame | 帧序号 |
| Time | 时间 |
| ALLKE | Abaqus动能 |
| ALLIE | Abaqus内能 |
| Calc_E_rad | 计算的径向能量 |
| Calc_E_cir | 计算的环向能量 |
| Calc_E_axi | 计算的轴向能量 |
| Calc_E_tan | 计算的剪切能量 |
| Total_Calc_Work | 计算总能量 |
| Total_Reference_Work | 参考能量(ALLIE) |
| Error_Prop | 相对误差 |

## 关键问题修复

### 问题1：坐标不匹配
**原始问题**：COORD在节点输出，应力/应变在积分点输出，索引不一致

**解决方案**：使用单元质心坐标代替节点坐标

```python
# 原始代码（错误）
x = C_vals[i].data[0]  # C_vals是节点坐标，与积分点不匹配

# 修复后
elem_centroid = reader.get_element_centroid_for_integration_point(frame, i)
x, y = elem_centroid[0], elem_centroid[1]
```

### 问题2：应变变换公式错误
**原始问题**：将工程应变当作应力进行变换

**解决方案**：正确区分工程应变与张量应变

```python
# 原始代码（错误）
le_curr = rotate_to_cyl(LE_vals[i].data[0], ...)

# 修复后
le_curr = rotate_engineering_strain_to_cylindrical(LE_vals[i].data, theta)
```

### 问题3：使用总应变代替塑性应变
**原始问题**：对于弹塑性分析，应使用塑性应变计算能量

**解决方案**：根据分析类型选择正确的应变类型

```python
# 弹塑性分析
STRAIN_TYPE = 'PE'  # 塑性应变

# 纯弹性分析
STRAIN_TYPE = 'LE'  # 总应变
```

## 依赖

- Abaqus Python环境
- xlwt (可选，用于Excel输出)

## 注意事项

1. **必须输出必要的场变量**：
   - S (应力)
   - LE (对数应变) 或 PE (塑性应变)
   - IVOL (积分点体积)
   - COORD (坐标)

2. **柱坐标系假设**：
   - Z轴为旋转对称轴
   - X-Y平面为径向-环向平面

3. **单元类型**：
   - 推荐使用二次单元以获得更准确的积分点结果

4. **运行位置**：
   - 必须在Abaqus工作目录下运行，或将ODB文件复制到当前目录
