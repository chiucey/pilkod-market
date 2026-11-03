# -*- coding: utf-8 -*-
from abaqus import *
from abaqusConstants import *
import part
import assembly
import sketch
import math

def generate_midpoints_3d(p1, p2, n):
    x1, y1, z1 = float(p1[0]), float(p1[1]), float(p1[2])
    x2, y2, z2 = float(p2[0]), float(p2[1]), float(p2[2])

    points = []
    for i in range(1, n + 1):
        t = float(i) / float(n + 1)
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        z = z1 + t * (z2 - z1)
        points.append((x, y, z))
    return points

def create_warp_part():
    s_path = myModel.ConstrainedSketch(name='__wp__', sheetSize=200.0)
    s_path.Line(point1=(0.0, 0.0), point2=(0.0, fabric_length))

    transform = (1.0,0.0,0.0, 0.0,1.0,0.0, 0.0,0.0,1.0, 0.0,0.0,0.0)
    s_prof = myModel.ConstrainedSketch(name='__wf__', sheetSize=200.0, transform=transform)
    s_prof.EllipseByCenterPerimeter(center=(0.0,0.0), axisPoint1=(0.0,warp_short_axis),
                                     axisPoint2=(warp_long_axis,0.0))

    p = myModel.Part(name='Warp', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p.BaseSolidSweep(sketch=s_prof, path=s_path)
    del myModel.sketches['__wp__'], myModel.sketches['__wf__']
    return p

def create_weft_parts():
    period = 2.0 * warp_spacing_x
    warp_columns_calc = max(2, int(round(fabric_width / period)))
    actual_width = float(warp_columns_calc) * period

    points_per_period = 16
    num_pts = warp_columns_calc * points_per_period + 1

    warp_layer_span = float(warp_layers - 1) * warp_spacing_y / 2.0
    y_amp = warp_layer_span + warp_short_axis + weft_short_axis + warp_spacing_y * wave_factor

    pts_a = []
    for i in range(num_pts):
        x = float(i) * actual_width / float(num_pts - 1)
        y = y_amp * math.sin(2.0 * math.pi * x / period)
        pts_a.append((x, y))

    pts_b = []
    for i in range(num_pts):
        x = float(i) * actual_width / float(num_pts - 1)
        y = y_amp * math.sin(2.0 * math.pi * x / period + math.pi)
        pts_b.append((x, y))

    s_path_a = myModel.ConstrainedSketch(name='__pa__', sheetSize=200.0)
    s_path_a.Spline(points=pts_a)
    transform = (0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, pts_a[0][1], 0.0)
    s_prof_a = myModel.ConstrainedSketch(name='__pra__', sheetSize=200.0, transform=transform)
    s_prof_a.ConstructionLine(point1=(-10.0, 0.0), point2=(10.0, 0.0))
    s_prof_a.ConstructionLine(point1=(0.0, -10.0), point2=(0.0, 10.0))
    s_prof_a.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, weft_long_axis),
                                       axisPoint2=(weft_short_axis, 0.0))

    p_a = myModel.Part(name='Weft_TypeA', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p_a.BaseSolidSweep(sketch=s_prof_a, path=s_path_a)

    s_path_b = myModel.ConstrainedSketch(name='__pb__', sheetSize=200.0)
    s_path_b.Spline(points=pts_b)
    transform = (0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, pts_b[0][1], 0.0)
    s_prof_b = myModel.ConstrainedSketch(name='__prb__', sheetSize=200.0, transform=transform)
    s_prof_b.ConstructionLine(point1=(-10.0, 0.0), point2=(10.0, 0.0))
    s_prof_b.ConstructionLine(point1=(0.0, -10.0), point2=(0.0, 10.0))
    s_prof_b.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, weft_long_axis),
                                       axisPoint2=(weft_short_axis, 0.0))

    p_b = myModel.Part(name='Weft_TypeB', dimensionality=THREE_D, type=DEFORMABLE_BODY)
    p_b.BaseSolidSweep(sketch=s_prof_b, path=s_path_b)

    for sk in ['__pa__', '__pra__', '__pb__', '__prb__']:
        if sk in myModel.sketches.keys():
            del myModel.sketches[sk]

    return p_a, p_b, y_amp, pts_a, pts_b, actual_width, warp_columns_calc

def create_assembly(weft_a, weft_b, y_amp, points):
    a = myModel.rootAssembly
    a.DatumCsysByDefault(CARTESIAN)

    for layer, point in enumerate(points[::2]):
        inst = 'W-{}'.format(layer)
        a.Instance(name=inst, part=myModel.parts['Warp'], dependent=ON)
        a.rotate(instanceList=(inst, ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(1.0, 0.0, 0.0), angle=90.0)
        a.translate(instanceList=(inst, ), vector=(point[0], point[1], point[2]))

    for i in range(weft_count):
        z_pos = float(i) * weft_spacing - float(weft_count - 1) * weft_spacing / 2.0

        if i % 2 == 0:
            inst = 'Weft-A-{}'.format(i)
            a.Instance(name=inst, part=weft_a, dependent=ON)
        else:
            inst = 'Weft-B-{}'.format(i)
            a.Instance(name=inst, part=weft_b, dependent=ON)

        a.translate(instanceList=(inst,), vector=(0.0, 0.0, z_pos))

# ==================== 参数输入 ====================
fields = (
    ('Warp short axis (X):', '0.5'),
    ('Warp long axis (Y):', '1'),
    ('Warp X spacing:', '2.0'),
    ('Warp Y spacing:', '0.5'),
    ('Warp layers:', '4'),
    ('Weft short axis (Y):', '0.5'),
    ('Weft long axis (Z):', '1'),
    ('Weft count:', '7'),
    ('Weft spacing:', '2.0'),
    ('Wave gap factor (0=tight, 0.3=gap):', '0'),
)

dialog = getInputs(fields=fields, label='2.5D Weave Parameters')
if dialog is None:
    raise ValueError("User cancelled")

warp_short_axis = float(dialog[0]) / 2.0
warp_long_axis = float(dialog[1]) / 2.0
warp_spacing_x = float(dialog[2])
warp_spacing_y = float(dialog[3])
warp_layers = int(dialog[4])
weft_short_axis = float(dialog[5]) / 2.0
weft_long_axis = float(dialog[6]) / 2.0
weft_count = int(dialog[7])
weft_spacing = float(dialog[8])
wave_factor = float(dialog[9])

fabric_length = weft_long_axis + float(weft_count - 1) * weft_spacing

Z_warp_central_position = -(weft_spacing * float(weft_count - 1) / 2.0 + weft_long_axis / 2.0)

if mdb.models.has_key("Model-1"):
    myModel = mdb.models["Model-1"]
    for name in list(myModel.parts.keys()):
        del myModel.parts[name]
else:
    myModel = mdb.Model(name="Model-1", modelType=STANDARD_EXPLICIT)

try:
    create_warp_part()
    weft_a, weft_b, y_amp, pts_a, pts_b, actual_width, warp_columns_calc = create_weft_parts()

    X_warp_central_position = actual_width
    Central_Begin_Position = [0.0, 0.0, Z_warp_central_position]
    Central_End_Position = [X_warp_central_position, 0.0, Z_warp_central_position]

    points = generate_midpoints_3d(Central_Begin_Position, Central_End_Position, 2*warp_layers-1)
    create_assembly(weft_a, weft_b, y_amp, points)

    session.viewports['Viewport: 1'].setValues(displayedObject=myModel.rootAssembly)

except Exception as e:
    raise
