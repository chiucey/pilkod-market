---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9d34c3582d514f4fb9eba296389992b7
    PropagateID: 9d34c3582d514f4fb9eba296389992b7
    ReservedCode1: 3046022100d8e5365fafca4de4195e1839bb8e1edf89bc8b678d17676c249865377a6f71f90221008a058b3dbc94674ecca554060041d4cf72ff47c5823832268623d59eece5c1d1
    ReservedCode2: 3045022100e6652b735ad83c799fe1635840a5c2fb1edbd93fc0649247a61515ae98183f8c0220563ea97ae3151c8f4110f4ba6b5767112be5034d87382aff9f286201fbc3b9ee
description: Abaqus Python二次开发技能，专注于前处理建模（特别是织物/复合材料模型）和后处理结果提取。当用户询问Abaqus二次开发、使用Python脚本进行Abaqus建模、创建织物模型、复合材料铺层、几何建模、网格划分、边界条件设置、或后处理结果提取时使用。
name: abaqus-python-prepost
---

# Abaqus Python 二次开发技能

## 核心能力

### 1. 前处理建模

#### 1.1 织物模型创建

**典型织物几何建模方法：**

```python
from abaqus import *
from abaqusConstants import *
from caeModules import *

def create_fabric_model():
    """创建织物微观结构模型"""
    model = mdb.Model(name='FabricModel')

    # 方法1：基于刺绣图案创建纱线路径
    # 定义经纱和纬纱的走向
    yarn_paths = []

    # 经纱定义
    for i in range(num_warp_yarns):
        path_points = []
        for j in range(num_points):
            x = i * spacing + offset_x
            y = wave_function(j, amplitude, wavelength)
            z = j * spacing_z
            path_points.append((x, y, z))
        yarn_paths.append(path_points)

    # 方法2：使用洋麻织物几何
    # 创建纱线横截面
    import sketch
    import part

    # 纱线横截面草图
    s = model.ConstrainedSketch(name='YarnProfile', sheetSize=10.0)
    # 定义椭圆形横截面
    s.Ellipse(centerPoint=(0.0, 0.0),
              axisPoint1=(yarn_width/2, 0.0),
              axisPoint2=(0.0, yarn_height/2))

    # 通过扫掠创建纱线
    part = model.Part(name='WarpYarn',
                       dimensionality=THREE_D,
                       type=DEFORMABLE_BODY)

    # 沿路径扫掠
    datum = part.BaseSolidSweep(sketch=s,
                                 path=path_obj)

    return model

def wave_function(x, amplitude, wavelength):
    """正弦波函数模拟纱线波动"""
    return amplitude * sin(2 * PI * x / wavelength)
```

#### 1.2 复合材料铺层建模

```python
def create_laminate_model():
    """创建层合板模型"""
    model = mdb.models['ExistingModel']

    # 创建铺层
    composite_layup = model.parts['LaminatePart'].CompositeLayup(
        name='Layup',
        description='Carbon Fiber Laminate',
        elementType=SOLID,
        region=None,
        thicknessType=MANUAL,
        angle=0.0,
        thickness=1.0,
        materialDirection=SPECIFIED,
        symmetric=False
    )

    # 添加铺层
    layers = [
        {'material': 'CarbonFiber', 'thickness': 0.125, 'angle': 45},
        {'material': 'CarbonFiber', 'thickness': 0.125, 'angle': -45},
        {'material': 'CarbonFiber', 'thickness': 0.125, 'angle': 0},
        {'material': 'EpoxyMatrix', 'thickness': 0.1, 'angle': 0},
    ]

    for i, layer in enumerate(layers):
        composite_layup.Section(
            region=Region(cells=all_cells),
            sectionParameters=SectionParameters(
                materialName=layer['material'],
                thickness=layer['thickness'],
                orientation=LocalOrientation(
                    csys=datum_csys,
                    localAxesData=(0, 0, layer['angle'])
                )
            )
        )
```

#### 1.3 几何体布尔运算与装配

```python
def assembly_operations():
    """装配体布尔运算"""
    # 创建部件实例
    model.rootAssembly.Instance(
        name='YarnInstance',
        part=model.parts['YarnPart'],
        dependent=ON
    )

    # 布尔运算
    model.rootAssembly.InstanceFromCutDeck(
        tool=model.parts['MatrixPart'],
        instanceToBeCut=model.rootAssembly.instances['YarnInstance'],
        originalAssembly=model.rootAssembly
    )
```

### 2. 网格划分自动化

```python
def meshing_workflow():
    """网格划分工作流程"""
    part = mdb.models['Model'].parts['Part']

    # 全局网格控制
    part.seedPart(
        size=global_mesh_size,
        deviationFactor=0.1,
        minSizeFactor=0.1
    )

    # 局部网格加密
    region = regionToolset.Region(
        faces=selected_faces
    )
    part.seedFaceBySize(
        region=region,
        size=local_mesh_size,
        deviationFactor=0.05
    )

    # 网格技术选择
    part.setMeshControls(
        regions=elemFaces,
        technique=FREE,
        algorithm=MEDIAL_AXIS,
        elemShape=QUAD_DOMINATED
    )

    # 生成网格
    part.generateMesh()

    # 网格质量检查
    elemTypes = (
        MeshElemType( elemCode=C3D8R, elemShape=HEXAGONAL),
        MeshElemType( elemCode=C3D6, elemShape=WEDGE),
        MeshElemType( elemCode=C3D4, elemShape=TET),
    )
```

### 3. 后处理结果提取

#### 3.1 场变量提取

```python
def extract_field_results():
    """提取场变量结果"""
    odb = openOdb(path='Job-1.odb')

    # 获取指定帧
    last_step = odb.steps.values()[-1]
    last_frame = last_step.frames[-1]

    # 提取位移
    displacement = last_frame.fieldOutputs['U']

    # 提取应力
    stress = last_frame.fieldOutputs['S']

    # 提取特定区域结果
    region = odb.rootAssembly.nodeSets['SET-1']

    # 获取节点数据
    disp_subset = displacement.getSubset(
        region=region,
        position=NODAL
    )

    # 遍历数据
    for value in disp_subset.values:
        node_label = value.nodeLabel
        data = value.data
        print(f"Node {node_label}: U={data}")

    odb.close()

def extract_integration_point_data():
    """提取积分点数据（场输出）"""
    odb = openOdb(path='Job-1.odb')

    # 提取材料应变能
    step = odb.steps['Step-1']
    frame = step.frames[-1]

    # 场输出
    strain_energy = frame.fieldOutputs['SENER']
    plastic_strain = frame.fieldOutputs['PE']

    # 获取单元数据
    elem_region = odb.rootAssembly.elementSets['ELEMENT_SET']
    elem_data = plastic_strain.getSubset(region=elem_region)

    for value in elem_data.values:
        print(f"Element {value.elementLabel}: PE={value.data}")
```

#### 3.2 历史变量提取

```python
def extract_history_data():
    """提取历史变量（时间历程）"""
    odb = openOdb(path='Job-1.odb')

    # 定义感兴趣区域
    node_region = odb.rootAssembly.nodeSets['REF_POINT']

    # 获取历史输出
    history_regions = odb.steps['Step-1'].historyRegions

    # 提取反力
    rf_history = steps['Step-1'].historyOutputs['RF2']

    # 提取位移
    u_history = steps['Step-1'].historyOutputs['U2']

    # 整理数据
    time_points = []
    force_values = []
    displacement_values = []

    for frame in step.frames:
        time_points.append(frame.frameValue)
        # 提取特定点的值
        rf_data = frame.frameValue
        u_data = frame.frameValue

    odb.close()

    return {
        'time': time_points,
        'force': force_values,
        'displacement': displacement_values
    }
```

#### 3.3 结果可视化脚本

```python
def create_contour_plot():
    """创建等值线图"""
    from visualization import *

    viewport = session.Viewport(name='Contour View')
    viewport.makeCurrent()
    viewport.maximize()

    # 打开odb
    odb = session.openOdb(name='Job-1.odb')
    viewport.display.setPrimaryVariable(
        variableLabel='S',
        outputPosition=INTEGRATION_POINT,
        refinement=(INVARIANT, 'Mises')
    )

    # 设置等值线样式
    viewport.odbDisplay.contourOptions.setValues(
        intervalMin=0.0,
        intervalMax=1000.0,
        intervalType=LINEAR,
        autoMinMax=OFF
    )

    # 保存图片
    session.printToFile(
        fileName='contour_result',
        format=PNG,
        canvasItems=[viewport]
    )

def create_xy_plot():
    """创建XY曲线图"""
    from xyPlot import *

    # 从历史数据创建XY
    x_data = [0, 1, 2, 3, 4]
    y_data = [0, 100, 200, 300, 400]

    xy_data = XYData(name='Force-Displacement')
    for x, y in zip(x_data, y_data):
        xy_data.add(x, (x, y))

    # 创建图表
    chart = Session.XYChart(name='FD Curve')
    chart.add([xy_data])
```

### 4. 模块化后处理能量计算

基于模块化架构的后处理脚本，用于在柱坐标系下计算能量分量。

#### 4.1 模块结构

```
abaqus-python-prepost/
├── coord_transform.py      # 坐标变换模块
├── odb_reader.py           # ODB读取模块
├── energy_calculator.py     # 能量计算模块
├── config.py               # 配置文件
├── main_postprocess.py      # 主程序
```

#### 4.2 关键问题修复

**问题1：坐标不匹配**
```python
# 原始代码（错误）- COORD在节点输出，应力/应变在积分点输出
x = C_vals[i].data[0]  # 与积分点数据索引不匹配

# 修复后 - 使用单元质心坐标
from odb_reader import ODBReader
reader = ODBReader('Job-Name')
elem_centroid = reader.get_element_centroid_for_integration_point(frame, i)
x, y = elem_centroid[0], elem_centroid[1]
```

**问题2：应变变换公式错误**
```python
# 原始代码（错误）- 将工程应变当作应力进行变换
le_curr = rotate_to_cyl(LE_vals[i].data[0], ...)  # 错误！

# 修复后 - 正确处理工程应变与张量应变的转换
from coord_transform import rotate_engineering_strain_to_cylindrical
le_curr = rotate_engineering_strain_to_cylindrical(LE_vals[i].data, theta)
```

#### 4.3 完整使用示例

```python
# main_postprocess.py
import sys
sys.path.append('/path/to/modules/')

from odb_reader import ODBReader
from energy_calculator import EnergyAccumulator
from coord_transform import rotate_stress_to_cylindrical, rotate_engineering_strain_to_cylindrical
import math

# 配置
ODB_NAME = 'Job-Name'
OUTPUT_FILE = 'energy_results.xls'

# 初始化
reader = ODBReader(ODB_NAME)
accumulator = EnergyAccumulator()

# 处理每一帧
for kf in range(reader.num_frames):
    curr_data = reader.get_field_data_at_frame(kf)

    if kf > 0:
        prev_data = reader.get_field_data_at_frame(kf - 1)

        for i in range(len(curr_data['IVOL'])):
            # 获取单元质心坐标
            elem_centroid = reader.get_element_centroid_for_integration_point(
                curr_data['frame'], i
            )
            theta = math.atan2(elem_centroid[1], elem_centroid[0])

            # 旋转到柱坐标系
            s_curr = rotate_stress_to_cylindrical(...)
            le_curr = rotate_engineering_strain_to_cylindrical(...)

            # 计算能量增量
            delta_energy = calculate_frame_energy_delta(...)
            accumulator.add_frame_energy(delta_energy)

reader.close()
```

#### 4.4 能量分量说明

| 分量 | 说明 | 坐标方向 |
|------|------|----------|
| rad | 径向能量 | r (径向) |
| cir | 环向能量 | θ (周向) |
| axi | 轴向能量 | z (轴向) |
| tan | 剪切能量 | r-θ, r-z, θ-z |

### 5. 参数化建模模板

```python
class FabricModeler:
    """织物几何参数化建模器"""

    def __init__(self, model_name, params):
        self.model_name = model_name
        self.params = params
        self.model = mdb.Model(name=model_name)

    def create_yarn_geometry(self, yarn_type='warp'):
        """创建纱线几何"""
        spacing = self.params['yarn_spacing']
        width = self.params['yarn_width']
        height = self.params['yarn_height']
        amplitude = self.params['wave_amplitude']

        # 创建纱线横截面
        s = self.model.ConstrainedSketch(
            name=f'{yarn_type}_profile',
            sheetSize=20.0
        )

        # 椭圆形横截面
        s.Ellipse(
            centerPoint=(0.0, 0.0),
            axisPoint1=(width/2, 0.0),
            axisPoint2=(0.0, height/2)
        )

        return s

    def generate_weave_pattern(self):
        """生成织物编织模式"""
        pattern = []
        rows = self.params['rows']
        cols = self.params['cols']

        for i in range(rows):
            row = []
            for j in range(cols):
                # 交替模式：上下交替
                if (i + j) % 2 == 0:
                    row.append('warp_over')
                else:
                    row.append('warp_under')
            pattern.append(row)

        return pattern

    def assign_materials(self, yarn_mat, matrix_mat):
        """分配材料"""
        # 纱线材料
        self.model.Material(name=yarn_mat)
        self.model.materials[yarn_mat].Elastic(
            type=ISOTROPIC,
            table=((170e9, 0.3),)
        )

        # 基体材料
        self.model.Material(name=matrix_mat)
        self.model.materials[matrix_mat].Elastic(
            type=ISOTROPIC,
            table=((3.5e9, 0.35),)
        )
```

## 常用Abaqus Python API速查

### 模型对象

| 操作 | API |
|------|-----|
| 创建模型 | `mdb.Model(name='ModelName')` |
| 删除模型 | `del mdb.models['ModelName']` |
| 复制模型 | `mdb.Model(name='New', objectToCopy=mdb.models['Old'])` |

### 部件操作

| 操作 | API |
|------|-----|
| 创建部件 | `model.Part(name='PartName', ...)` |
| 创建草图 | `model.ConstrainedSketch(name='SketchName', ...)` |
| 布尔运算 | `part.Boolean(operation=DIFFERENCE, ...)` |

### 材料定义

```python
# 弹性材料
model.materials['Mat'].Elastic(
    type=ISOTROPIC,
    table=((210e9, 0.3),)
)

# 正交各向异性
model.materials['Mat'].Elastic(
    type=ORTHOTROPIC,
    table=((210e9, 210e9, 210e9, 0.3, 0.3, 0.3, 80e9, 80e9, 80e9),)
)

# 弹塑性材料
model.materials['Mat'].Plastic(
    table=((200e9, 0.0), (250e9, 0.1), (300e9, 0.2))
)
```

### 装配与实例

```python
# 创建装配
assembly = model.rootAssembly
assembly.DatumCsysByDefault(CARTESIAN)

# 创建实例
assembly.Instance(
    name='Part-1-1',
    part=model.parts['Part-1'],
    dependent=ON
)

# 定位实例
assembly.translate(
    instanceList=('Part-1-1',),
    vector=(10.0, 0.0, 0.0)
)

# 旋转实例
assembly.rotate(
    instanceList=('Part-1-1',),
    axisPoint=(0.0, 0.0, 0.0),
    axisDirection=(0.0, 0.0, 1.0),
    angle=90.0
)
```

### 边界条件与载荷

```python
# 创建分析步
model.StaticStep(
    name='LoadStep',
    previous='Initial',
    timePeriod=1.0,
    initialInc=0.01,
    maxInc=1.0
)

# 位移边界条件
region = assembly.instances['Part-1-1'].sets['SET-1']
model.DisplacementBC(
    name='Fixed',
    createStepName='Initial',
    region=region,
    u1=0.0, u2=0.0, u3=0.0
)

# 集中载荷
model.C load(
    name='Force',
    createStepName='LoadStep',
    region=region,
    cf1=1000.0
)

# 分布载荷
model.Pressure(
    name='Pressure',
    createStepName='LoadStep',
    region=region,
    magnitude=10.0
)
```

## 工作流程指南

### 典型前处理流程

1. **几何建模** → 创建或导入几何
2. **材料定义** → 定义材料属性
3. **截面定义** → 分配截面
4. **装配** → 组装部件
5. **网格划分** → 生成网格
6. **边界条件** → 设置边界和载荷
7. **作业提交** → 提交分析

### 典型后处理流程

1. **打开结果** → 打开ODB文件
2. **提取数据** → 获取场变量或历史变量
3. **数据分析** → 计算统计量
4. **可视化** → 创建图表和云图
5. **报告生成** → 输出结果报告

## 故障排查

### 常见错误

| 错误信息 | 解决方案 |
|----------|----------|
| `No module named 'abaqus'` | 在Abaqus CAE环境中运行脚本 |
| `KeyError: 'xxx'` | 检查部件/集合名称是否正确 |
| `Invalid argument` | 检查API参数类型和范围 |

### 调试技巧

```python
# 打印对象属性
print(dir(mdb.models['Model'].parts['Part']))

# 打印对象内容
print(assembly.instances)

# 逐步执行
import traceback
try:
    # 你的代码
except:
    traceback.print_exc()
```
