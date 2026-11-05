# -*- coding: UTF-8 -*-
from __future__ import print_function
import sys
import os

# 设置UTF-8编码解决中文乱码问题
if hasattr(sys, 'setdefaultencoding'):
    reload(sys)
    sys.setdefaultencoding('utf-8')

os.environ['PYTHONIOENCODING'] = 'utf-8'

from abaqus import *
from abaqusConstants import *
import part
import assembly
import material
import sketch
import math
import regionToolset

# ==================== 参数输入 ====================
fields = (
    ('经纱短半轴 (水平方向):', '0.06'),
    ('经纱长半轴 (厚度方向):', '0.12'),
    ('纬纱短半轴 (水平方向):', '0.06'),
    ('纬纱长半轴 (厚度方向):', '0.12'),
    ('经纱列间距 (X方向):', '0.5'),
    ('经纱层间距 (Y方向,厚度):', '0.35'),
    ('纬纱间距 (Z方向):', '0.8'),
    ('纬纱层数:', '4'),
    ('经纱列数:', '6'),
    ('经纱数量 (Z方向):', '10'),
    ('织物长度 (Z方向):', '12.0'),
    ('织物宽度 (X方向):', '6.0'),
    ('波浪高度系数 (0.5-1.0):', '0.8'),
)

dialog = getInputs(fields=fields, label='2.5D Orthogonal Fabric Parameters')
if dialog is None:
    raise ValueError("User cancelled")

a1 = float(dialog[0])  # 经纱短半轴 (X方向)
a2 = float(dialog[1])  # 经纱长半轴 (Y方向，厚度)
b1 = float(dialog[2])  # 纬纱短半轴 (Z方向)
b2 = float(dialog[3])  # 纬纱长半轴 (Y方向，厚度)
warp_spacing_x = float(dialog[4])  # 经纱列间距
warp_spacing_y = float(dialog[5])  # 经纱层间距 (厚度方向)
weft_spacing_z = float(dialog[6]) # 纬纱沿Z方向间距
weft_layers = int(dialog[7])      # 纬纱层数
warp_columns = int(dialog[8])     # 经纱列数
warp_count = int(dialog[9])       # 经纱数量(Z方向)
fabric_length = float(dialog[10]) # Z方向长度
fabric_width = float(dialog[11])   # X方向宽度
wave_factor = float(dialog[12])   # 波浪高度系数

# ==================== 初始化模型 ====================
if mdb.models.has_key("Model-1"):
    myModel = mdb.models["Model-1"]
    for part_name in list(myModel.parts.keys()):
        del myModel.parts[part_name]
else:
    myModel = mdb.Model(name="Model-1", modelType=STANDARD_EXPLICIT)

# ==================== 创建纬纱 Part (平直，沿X轴) ====================
def create_weft_part():
    """创建单根直纬纱 Part，沿X轴，截面为椭圆
    纬纱在X方向平直，高度方向Y有轻微起伏（受经纱挤压）
    """
    p = myModel.Part(name='Weft_Straight', dimensionality=THREE_D, type=DEFORMABLE_BODY)

    # 1. 创建路径草图 (沿X轴方向)
    s_path = p.ConstrainedSketch(name='__path__', sheetSize=200.0)
    s_path.Line(point1=(0.0, 0.0), point2=(fabric_width, 0.0))

    # 2. 创建截面草图 (椭圆，位于起点，垂直于路径即在YZ平面)
    # Transform: 草图X->全局Y(厚度), 草图Y->全局Z(长度)
    transform_matrix = (
        0.0, 1.0, 0.0,   # 草图X轴映射到全局Y（厚度方向）
        0.0, 0.0, 1.0,   # 草图Y轴映射到全局Z（长度方向）
        1.0, 0.0, 0.0,   # 草图Z轴（法向）映射到全局X
        0.0, 0.0, 0.0    # 起点平移
    )

    s_profile = p.ConstrainedSketch(name='__profile__', sheetSize=200.0, transform=transform_matrix)
    s_profile.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
    s_profile.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))

    # 椭圆：长轴沿Y（厚度方向b2），短轴沿X（b1）
    s_profile.EllipseByCenterPerimeter(
        center=(0.0, 0.0),
        axisPoint1=(0.0, b2),  # 长轴（厚度方向）
        axisPoint2=(b1, 0.0)    # 短轴
    )

    # 3. 扫掠生成实体
    p.BaseSolidSweep(sketch=s_profile, path=s_path)

    del p.sketches['__path__']
    del p.sketches['__profile__']

    return p

# ==================== 创建经纱 Part (波浪形，沿Z轴) ====================
def create_warp_part():
    """创建单根波浪经纱 Part，沿Z轴，在Y方向起伏
    经纱需要穿过所有纬纱层，形成交织结构
    """
    p = myModel.Part(name='Warp_Wavy', dimensionality=THREE_D, type=DEFORMABLE_BODY)

    # 1. 计算波浪路径
    # 纬纱层Y坐标范围：0 到 (weft_layers-1)*spacing_y
    y_min = -b2  # 底部留有余量
    y_max = (weft_layers - 1) * warp_spacing_y + b2  # 顶部留有余量
    y_center = (y_min + y_max) / 2.0
    y_amp = (y_max - y_min) / 2.0 * wave_factor

    # 周期：穿过2列经纱间距完成一个完整波浪
    period = 2.0 * warp_spacing_x

    num_points = 101  # 足够多的点保证平滑
    points = []

    # 生成波浪路径 (X, Y) 坐标，路径沿Z轴
    for i in range(num_points):
        z = (i / float(num_points - 1)) * fabric_length

        # 根据Z位置确定X方向位置（经纱在X方向的列位置）
        x_phase = 2.0 * math.pi * z / period

        # Y方向起伏：模拟穿过纬纱层的波浪
        y = y_center + y_amp * math.sin(x_phase)
        points.append((z, y))

    # 2. 创建路径草图
    s_path = p.ConstrainedSketch(name='__path__', sheetSize=200.0)
    s_path.Spline(points=points)

    # 获取起点坐标
    start_z, start_y = points[0]

    # 3. 创建截面草图 (垂直于路径)
    # Transform: 草图X->全局X, 草图Y->全局Y
    transform_matrix = (
        1.0, 0.0, 0.0,   # 草图X轴映射到全局X
        0.0, 1.0, 0.0,   # 草图Y轴映射到全局Y
        0.0, 0.0, 1.0,   # 草图Z轴（法向）映射到全局Z
        start_z, start_y, 0.0
    )

    s_profile = p.ConstrainedSketch(name='__profile__', sheetSize=200.0, transform=transform_matrix)
    s_profile.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
    s_profile.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))

    # 椭圆：长轴沿Y（厚度方向a2），短轴沿X（a1）
    s_profile.EllipseByCenterPerimeter(
        center=(0.0, 0.0),
        axisPoint1=(0.0, a2),  # 长轴（厚度方向）
        axisPoint2=(a1, 0.0)   # 短轴
    )

    # 4. 扫掠
    p.BaseSolidSweep(sketch=s_profile, path=s_path)

    del p.sketches['__path__']
    del p.sketches['__profile__']

    return p

# ==================== 装配模块 ====================
def create_assembly():
    """在Assembly中创建纬纱层和经纱阵列"""
    a = myModel.rootAssembly
    a.DatumCsysByDefault(CARTESIAN)

    # --- 1. 装配纬纱层 (Weft) ---
    # 纬纱沿X轴方向，水平排列成层
    for layer in range(weft_layers):
        # Y方向层间距
        y_pos = layer * warp_spacing_y

        # Z方向（经纱长度方向）排列
        for i in range(warp_count):
            z_pos = i * weft_spacing_z - (warp_count - 1) * weft_spacing_z / 2.0

            inst_name = 'Weft-L{}-N{}'.format(layer, i)
            inst = a.Instance(name=inst_name, part=myModel.parts['Weft_Straight'], dependent=ON)

            # 平移到正确位置
            a.translate(instanceList=(inst_name,), vector=(0.0, y_pos, z_pos))

    # --- 2. 装配经纱 (Warp) ---
    # 经纱沿Z轴方向（垂直于纬纱），在Y方向波浪起伏
    for col in range(warp_columns):
        # X方向列位置
        x_pos = col * warp_spacing_x - (warp_columns - 1) * warp_spacing_x / 2.0

        # 根据列位置确定波浪相位
        # 相邻列的经纱相位差半个周期，实现交织
        phase_offset = 0.0 if (col % 2 == 0) else math.pi

        # Z方向排列
        for i in range(warp_count):
            # 如果需要更复杂的交织，可以在这里调整相位
            inst_name = 'Warp-C{}-N{}'.format(col, i)
            inst = a.Instance(name=inst_name, part=myModel.parts['Warp_Wavy'], dependent=ON)

            # 平移到指定X位置，Y和Z由Part本身确定
            a.translate(instanceList=(inst_name,), vector=(x_pos, 0.0, 0.0))

    print("Assembly completed: {} layers x {} wefts, {} columns x {} warps".format(
        weft_layers, warp_count, warp_columns, warp_count))

# ==================== 执行 ====================
try:
    print("Creating weft (straight) part...")
    create_weft_part()
    print("Weft part created")

    print("Creating warp (wavy) part...")
    create_warp_part()
    print("Warp part created")

    print("Creating assembly...")
    create_assembly()

    # 设置视图
    session.viewports['Viewport: 1'].setValues(displayedObject=myModel.rootAssembly)
    session.viewports['Viewport: 1'].viewIso()

    print("Fabric model completed successfully!")

except Exception as e:
    print("Error: ", str(e))
    import traceback
    traceback.print_exc()
    raise
