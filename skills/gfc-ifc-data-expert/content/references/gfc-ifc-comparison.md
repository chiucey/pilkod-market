# GFC与IFC数据格式详细对比参考

## 1. GFC与IFC概述对比

| 特性 | GFC | IFC |
|------|-----|-----|
| **开发商** | 广联达科技股份有限公司 | buildingSMART International |
| **版本** | 3.1.1.0 | 4.3 (最新) |
| **适用范围** | 中国建筑市场为主 | 全球通用 |
| **实体数量** | 200+ | 800+ |
| **属性集数量** | 200+ | 700+ |
| **Schema数量** | 20+ | 30+ |
| **SDK支持** | GFC SDK (C++) | IFC SDK (多语言) |
| **标准依据** | GB/T 51269-2017 | ISO 16739 |
| **应用场景** | 设计、施工管理、工程量 | 全生命周期 |

## 1.1 GFC标准体系（安徽省DBXX 10-2025）

### 设计构件分类体系

**附录B - 设计构件分类编码**:
- B.0.1 建筑专业构件分类
- B.0.2 结构专业构件分类
- B.0.3 机电专业公共构件分类
- B.0.4 暖通专业构件分类
- B.0.5 给水排水专业构件分类
- B.0.6 电气专业构件分类
- B.0.7 施工管理构件分类

**附录C - 设计构件属性**:
- C.1 建筑专业属性信息
- C.2 结构专业属性信息
- C.3 机电专业公共属性信息
- C.4 暖通专业属性信息
- C.5 给水排水专业属性信息
- C.6 电气专业属性信息
- C.7 施工管理属性信息

### 施工管理对象分类体系

**附录D - 施工管理业务对象分类编码**:
- D.0.1 虚拟建造对象分类
- D.0.2 设计资料对象分类
- D.0.3 项目预算对象分类
- D.0.4 质量要求对象分类

**附录E - 施工管理业务对象属性**:
- E.1 虚拟建造对象属性
- E.2 设计资料对象属性
- E.3 项目预算对象属性
- E.4 质量要求对象属性

### 工程量构件分类体系

**附录F - 工程量（全专业）构件属性**:
- F.1 工程量建筑专业构件属性
- F.2 工程量结构专业构件属性
- F.3 工程量机电专业公共构件属性
- F.4 工程量给排水专业构件属性
- F.5 工程量暖通专业构件属性
- F.6 工程量电气专业构件属性
- F.7 工程量施工专业构件属性

**附录G - 项目属性**
**附录H - 楼层属性**
**附录I - 枚举值（D.001~D.450）**

## 2. GFC核心实体详细说明

### 2.1 基础几何实体

```
GfcCurve2d/GfcCurve3d     - 基础曲线类型
GfcLine/GfcLine2d/GfcLine3d - 直线
GfcArc2d/GfcArc3d         - 圆弧
GfcCircle                 - 圆
GfcEllipse2d/GfcEllipse3d - 椭圆
GfcPolyline               - 多段线
GfcNurbsCurve2d/GfcNurbsCurve3d - NURBS曲线
GfcOffsetCurve2d          - 偏移曲线
```

### 2.2 曲面与实体

```
GfcSurface                - 基础曲面
GfcNurbsSurface           - NURBS曲面
GfcPlane                  - 平面
GfcRuledSurface           - 直纹曲面
GfcHelicoid               - 螺旋面

GfcSolidShape             - 基础实体
GfcManifoldSolidShape     - 流形实体
GfcBrepBody               - BREP表达实体
GfcCuboidBody             - 长方体
GfcCylinder/GfcCylinderShape - 圆柱
GfcConeShape               - 圆锥
GfcSphere/GfcSphereShape   - 球体
GfcTorus                  - 环面
GfcExtrudedBody           - 拉伸实体
GfcPolyhedronBody         - 多面体
```

### 2.3 建筑构件

```
GfcProject               - 项目
GfcSite                  - 场地
GfcBuilding              - 建筑
GfcFloor                 - 楼层
GfcElement               - 构件(基类)
GfcElementType           - 构件类型
GfcElementShape          - 构件形状
GfcRepresentation        - 表现
GfcRepresentationItem    - 表现项
GfcLayer                 - 图层
GfcBlueprint             - 图纸
GfcInsert                - 插入块
```

### 2.4 截面定义

```
GfcSection                - 截面基类
GfcParameterizedSection    - 参数化截面
GfcArbitrarySection        - 任意截面

矩形截面:
GfcRectangleSection        - 矩形实心截面
GfcRectangleHollowSection   - 矩形空腹截面

圆形截面:
GfcCircleSection           - 圆形实心截面
GfcCircleHollowSection      - 圆形空腹截面

型钢截面:
GfcLShapeSection           - L形截面
GfcTShapeSection           - T形截面
GfcEllipseSection          - 椭圆截面
```

### 2.5 样式与材质

```
材质:
GfcAppearanceMaterial      - 外观材质
GfcPBRAppearanceMaterial   - PBR材质
GfcPHONGAppearanceMaterial - PHONG材质

颜色与填充:
GfcColor                   - 颜色
GfcFillAreaStyle           - 填充区域样式
GfcFillStyle               - 填充样式

线型:
GfcCurveStyle              - 曲线样式
GfcLineType               - 线型
GfcLinePattern             - 线型图案

文本:
GfcTextStyle               - 文本样式
GfcFontStyle               - 字体样式

纹理:
GfcSurfaceTexture          - 表面纹理
GfcImage                   - 图像
GfcImageFile               - 图像文件
```

### 2.6 属性系统

```
属性基类:
GfcProperty               - 属性基类
GfcSimpleProperty         - 简单属性
GfcComplexProperty         - 复杂属性

简单类型属性:
GfcBooleanProperty        - 布尔属性
GfcIntegerProperty         - 整数属性
GfcDoubleProperty          - 双精度属性
GfcStringProperty          - 字符串属性

列表类型属性:
GfcBooleanListProperty     - 布尔列表属性
GfcIntegerListProperty     - 整数列表属性
GfcDoubleListProperty      - 双精度列表属性
GfcStringListProperty      - 字符串列表属性

引用类型属性:
GfcEntityProperty         - 实体引用属性
GfcEntityListProperty      - 实体列表属性

特殊类型属性:
GfcGeoProperty            - 地理属性
GfcGeoListProperty         - 地理列表属性
GfcSectionProperty         - 截面属性
GfcSectionListProperty     - 截面列表属性

属性集:
GfcPropertySet            - 属性集
```

### 2.7 拓扑结构

```
拓扑基类:
GfcTopology               - 拓扑基类

顶点、边、面:
GfcVertex                 - 顶点
GfcEdge                   - 边
GfcFace                   - 面

共边与环:
GfcCoedge                 - 共边
GfcCoedgeList             - 共边列表
GfcCoedgeListEx           - 扩展共边列表
GfcLoop                   - 环
GfcSimpleLoop             - 简单环
GfcPolyhedralLoop         - 多面体环

多面体元素:
GfcPolyhedralFace         - 多面体面
GfcPolyhedralEdge         - 多面体边
```

### 2.8 关系定义

```
关系基类:
GfcRelationShip           - 关系基类

聚合与分解:
GfcRelAggregates          - 聚合关系(整体-部分)
GfcRelDecomposes          - 分解关系

连接关系:
GfcRelConnects            - 基础连接
GfcRelConnectsElements    - 构件间连接
GfcRelConnectsPathElements - 路径连接
GfcRelConnectsWithRealizingElements - 实现连接

空间关系:
GfcRelCoversBldgElements  - 覆盖关系

定义关系:
GfcRelDefines             - 基础定义
GfcRelDefinesByProperties - 属性定义
GfcRelDefinesByType       - 类型定义

几何操作:
GfcRelVoidsElement        - 挖空关系
```

### 2.9 工程量清单

```
清单明细:
GfcBillDetail             - 清单明细
GfcQuotaDetail            - 定额明细
GfcSteelDetail            - 钢筋明细

清单汇总:
GfcBillTotal              - 清单汇总
GfcQuotaTotal             - 定额汇总
GfcSteelTotal             - 钢筋汇总
```

### 2.10 基本数据类型

```
布尔与数值:
GfcBoolean               - 布尔值(true/false)
GfcInteger               - 32位整数
GfcDouble                - 64位双精度浮点数

字符串类型:
GfcString                - 可变长度字符串
GfcText                  - 多行文本
GfcLabel                 - 标签(短文本标识)

日期时间:
GfcDate                  - 日期(YYYY-MM-DD)
GfcTime                  - 时间(HH:MM:SS)
GfcDateTime              - 日期时间

测量类型:
GfcElev                  - 高程值
GfcIdentity              - 全局唯一标识符
```

### 2.11 几何坐标类型

```
坐标类型:
GfcCoordinates2d         - 二维坐标(x,y)
GfcCoordinates3d         - 三维坐标(x,y,z)

向量类型:
GfcVector2d              - 二维向量
GfcVector3d              - 三维向量

几何元素:
GfcPoint                 - 点
GfcMatrix                - 4x4变换矩阵

包围与范围:
GfcBox3d                 - 三维包围盒
GfcIntervald             - 一维区间
```

### 2.12 枚举类型

```
几何枚举:
GfcArcType               - 圆弧类型
GfcBooleanOperator       - 布尔运算类型(并集/差集/交集)
GfcConnectionType        - 连接类型
GfcFragTestFunc          - 片段测试函数
GfcSweepType             - 扫掠类型

对齐枚举:
GfcHorizontalAlignment   - 水平对齐方式
GfcVerticalAlignment     - 垂直对齐方式

渲染枚举:
GfcSceneBlendFactor      - 场景混合因子
GfcTextureType           - 纹理类型
GfcTextGenerationFlag    - 文本生成标志
```

## 3. IFC核心实体详细说明

### 3.1 IfcKernel Schema核心实体

```
IfcRoot                  - 所有实体基类(包含GlobalId, OwnerHistory, Name, Description)
IfcObjectDefinition      - 对象定义基类
IfcObject                - 对象(具有类型)
IfcActor                 - 参与者(人/组织)
IfcControl               - 控制对象(文档、订单等)
IfcProcess               - 过程
IfcProduct               - 产品(具有空间位置)
IfcResource              - 资源

IfcProject               - 项目(根节点)
IfcSite                 - 场地
IfcBuilding             - 建筑
IfcBuildingStorey       - 楼层
IfcSpace                - 空间
IfcAnnotation           - 标注
IfcElement              - 构件(梁、柱、墙等)
IfcElementType          - 构件类型
```

### 3.2 IfcSharedBldgElements共享建筑元素

```
结构构件:
IfcBeam                 - 梁
IfcColumn               - 柱
IfcFooting              - 基础
IfcPile                 - 桩
IfcTendon               - 预应力筋
IfcReinforcingBar       - 钢筋
IfcReinforcingMesh      - 钢筋网片

建筑围护:
IfcWall                 - 墙
IfcWallStandardCase     - 标准墙
IfcWallElementedCase    - 复合墙
IfcRoof                 - 屋面
IfcSlab                 - 板
IfcPlate                - 板(非结构)
IfcCurtainWall          - 幕墙

建筑开口:
IfcDoor                 - 门
IfcDoorLiningProperties - 门框属性
IfcDoorPanelProperties  - 门扇属性
IfcWindow               - 窗
IfcWindowLiningProperties - 窗框属性
IfcWindowPanelProperties - 窗扇属性

楼梯与垂直交通:
IfcStair                - 楼梯
IfcStairFlight          - 楼梯梯段
IfcLandings             - 平台
IfcRamp                  - 坡道
IfcRampFlight           - 坡道梯段
IfcTransportElement     - 运输设备(电梯)

其他建筑元素:
IfcBuildingElementProxy - 建筑元素代理
IfcCovering             - 覆盖物
IfcRailing              - 栏杆
IfcMember               - 构件(非结构)
IfcBuildingElementPart   - 建筑元素部分
```

### 3.3 IfcSharedBldgServiceElements建筑服务元素

```
分布回路:
IfcDistributionCircuit   - 配电回路
IfcDistributionFlowDirectionEnum - 流向枚举

分布控制:
IfcDistributionControlElement - 分布控制元素
IfcController           - 控制器
IfcActuator            - 执行器
IfcAlarm               - 报警器
IfcFlowInstrument      - 流量仪表

分布流动元素:
IfcDistributionFlowElement - 分布流动元素基类
IfcFlowController       - 流动控制器
IfcFlowMovingDevice     - 流动设备
IfcFlowTerminal         - 流动终端
IfcFlowStorageDevice    - 流动存储设备
IfcFlowFitting         - 流动管件
IfcFlowSegment         - 流动管段

暖通类型:
IfcAirTerminal          - 风口
IfcAirTerminalBox       - 空气终端箱
IfcDamper              - 风阀
IfcDuctFitting         - 风管管件
IfcDuctSegment         - 风管段
IfcDuctSilencer        - 风管消声器

管道类型:
IfcPipeFitting         - 管道管件
IfcPipeSegment         - 管道段
IfcValve               - 阀门
IfcSanitaryTerminal    - 卫生终端
IfcShower              - 淋浴
IfcToilet              - 厕所
IfcWashHandSink        - 洗手盆
IfcWaterHeater         - 热水器

电气类型:
IfcElectricGenerator    - 发电机
IfcElectricMotor       - 电动机
IfcElectricDistributionBoard - 配电箱
IfcCableSegment        - 电缆段
IfcProtectiveDevice    - 保护装置
IfcSwitchingDevice     - 开关设备
IfcLightFixture        - 灯具

消防类型:
IfcFireSuppressionTerminal - 消防终端
IfcSprinkler           - 喷头
IfcHydrant             - 消防栓
```

### 3.4 IfcStructuralAnalysisDomain结构分析

```
分析模型:
IfcStructuralAnalysisModel - 结构分析模型
IfcStructuralLoadGroup    - 荷载组
IfcStructuralLoadCase     - 荷载工况
IfcStructuralLoadScene    - 荷载场景

分析结果:
IfcStructuralResultGroup - 分析结果组
IfcStructuralReaction   - 结构反力
IfcStructuralAction      - 结构作用

连接与边界:
IfcStructuralConnection  - 结构连接
IfcStructuralPointConnection - 节点连接
IfcStructuralCurveConnection - 线连接
IfcStructuralSurfaceConnection - 面连接

构件:
IfcStructuralMember      - 结构构件
IfcStructuralCurveMember  - 曲线构件(梁)
IfcStructuralSurfaceMember - 面构件(板/墙)
```

### 3.5 属性集(Pset)示例

```
通用属性集:
Pset_ProjectCommon       - 项目通用属性
Pset_BuildingCommon      - 建筑通用属性
Pset_SiteCommon          - 场地通用属性
Pset_SpaceCommon         - 空间通用属性

建筑构件属性集:
Pset_WallCommon          - 墙通用属性
Pset_WallStandardCase    - 标准墙属性
Pset_SlabCommon          - 板通用属性
Pset_BeamCommon          - 梁通用属性
Pset_ColumnCommon        - 柱通用属性
Pset_DoorCommon         - 门通用属性
Pset_WindowCommon       - 窗通用属性
Pset_RoofCommon         - 屋面通用属性
Pset_StairCommon        - 楼梯通用属性

电气系统属性集:
Pset_ElectricDistributionBoardCommon - 配电箱属性
Pset_LightFixtureProperties - 灯具属性
Pset_CableSegmentProperties - 电缆段属性

HVAC属性集:
Pset_ThermalLoad         - 热负荷
Pset_SpaceThermalLoad     - 空间热负荷
Pset_AirTerminalBox      - 风口箱属性
Pset_DuctSilencer        - 消声器属性

数量集(Qto):
Qto_BuildingBaseQuantities - 建筑基础数量
Qto_WallBaseQuantities     - 墙基础数量
Qto_SlabBaseQuantities     - 板基础数量
Qto_BeamBaseQuantities     - 梁基础数量
```

## 4. GFC SDK API参考

### 4.1 CDocument核心接口

```cpp
// 文档操作
class CDocument {
public:
    // 实体管理
    void remove(const std::vector<EntityRef>& entities);
    EntityRef getMaxRef();
    void setMaxRef(EntityRef maxRefId);
    void clear();

    // 读写操作
    bool ReadFromFile(const char* filePath);
    bool WriteToFile(const char* filePath);

    // 查询操作
    std::vector<EntityRef> GetEntities();
    EntityPtr GetEntity(EntityRef ref);
};
```

### 4.2 构建方法

```bash
# 使用CMake构建
cmake -B ./build -S ./src
cmake --build ./Build

# 指定编译器(Windows)
cmake -B ./build -S ./src -G "Visual Studio 14 2015" -A x64

# 指定构建类型
cmake -B ./build -S ./src -DCMAKE_BUILD_TYPE=Release
```

## 5. Revit API参考

### 5.1 核心命名空间

```csharp
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Autodesk.Revit.ApplicationServices;
```

### 5.2 常用操作

```csharp
// 文档操作
Document doc = commandData.Application.ActiveUIDocument.Document;

// 创建元素
FilteredElementCollector collector = new FilteredElementCollector(doc);
IList<Element> walls = collector.OfClass(typeof(Wall)).ToElements();

// 读取参数
Parameter param = element.get_Parameter("名称");
string name = param.AsString();

// 设置参数
param.Set("新值");

// 几何获取
Options options = new Options();
GeometryElement geom = element.get_Geometry(options);

// IFC导出
IFCExportOptions ifcOptions = new IFCExportOptions();
doc.Export(folderPath, fileName, ifcOptions);
```

## 6. 数据转换映射表

### 6.1 构件类型映射

| GFC构件 | IFC实体 | 说明 |
|---------|---------|------|
| GfcBuilding | IfcBuilding | 建筑 |
| GfcFloor | IfcBuildingStorey | 楼层 |
| GfcSite | IfcSite | 场地 |
| GfcElement | IfcElement | 通用构件 |
| - | IfcWall | 墙 |
| - | IfcSlab | 板 |
| - | IfcBeam | 梁 |
| - | IfcColumn | 柱 |
| - | IfcDoor | 门 |
| - | IfcWindow | 窗 |

### 6.2 属性映射

| GFC属性类型 | IFC属性类型 | 说明 |
|-------------|-------------|------|
| GfcStringProperty | IfcPropertySingleValue | 单值属性 |
| GfcIntegerProperty | IfcPropertySingleValue | 整数属性 |
| GfcDoubleProperty | IfcPropertySingleValue | 数值属性 |
| GfcBooleanProperty | IfcPropertySingleValue | 布尔属性 |
| GfcPropertySet | IfcPropertySet | 属性集 |
| GfcEntityProperty | IfcPropertyReferenceValue | 实体引用 |

### 6.3 几何映射

| GFC几何类型 | IFC几何类型 | 说明 |
|-------------|-------------|------|
| GfcPoint | IfcCartesianPoint | 点 |
| GfcLine | IfcLine | 直线 |
| GfcArc | IfcCircle/IfcArc | 圆/圆弧 |
| GfcPolyline | IfcPolyline | 多段线 |
| GfcNurbsCurve | IfcBSplineCurve | B样条曲线 |
| GfcBrepBody | IfcFacetedBrep/IfcManifoldSolidBrep | BREP实体 |
| GfcExtrudedBody | IfcExtrudedAreaSolid | 拉伸实体 |
| GfcCylinder | IfcCylindricalShaft/IfcRightCircularCylinder | 圆柱体 |

## 7. GFC完整构件分类编码表（依据GB/T 51269-2017）

### 7.1 建筑专业构件完整列表

| 序号 | 构件名称 | 构件代码 | 编码 | 备注 |
|-----|---------|---------|------|------|
| 1 | 基坑大开挖 | PitEarth | 15-31.30.01 | 按国标"工作成果"扩展 |
| 2 | 沟槽土方 | DitchEarth | 15-31.30.02 | 按国标扩展 |
| 3 | 大开挖土方 | LargeExcavationEarthwork | 15-31.30.03 | 按国标扩展 |
| 4 | 大开挖土方回填 | ExcavatedEarthBackfill | 15-31.40.01 | 按国标扩展 |
| 5 | 基槽回填土方 | DitchEarthBackfill | 15-31.40.02 | 按国标扩展 |
| 6 | 基坑回填土方 | PitEarthBackfill | 15-31.40.03 | 按国标扩展 |
| 7 | 房心回填土方 | RoomBackfill | 15-31.40.04 | 按国标扩展 |
| 8 | 幕墙 | CurtainWall | 14-10.20.21 | 国标元素 |
| 9 | 嵌板 | Panels | 14-10.20.21.32 | 按国标扩展 |
| 10 | 竖挺 | Upright | 14-10.20.21.34 | 按国标扩展 |
| 11 | 横梁 | Crossbeam | 14-10.20.21.36 | 按国标扩展 |
| 12 | 预埋件 | EmbeddedParts | 14-10.20.21.38 | 按国标扩展 |
| 13 | 幕墙转接件 | CurtainWallAdapters | 14-10.20.21.40 | 按国标扩展 |
| 14 | 玻璃压块 | GlassBriquetting | 14-10.20.21.42 | 按国标扩展 |
| 15 | 饰面板 | Veneer | 14-10.20.21.44 | 按国标扩展 |
| 16 | 遮阳帘 | Sunshade | 15-10.40.10 | 国标工作成果 |
| 17 | 采光顶 | Sunroof | 14-10.20.15.20 | 按国标屋顶扩展 |
| 18 | 道路 | Road | 11-02.45.10 | 国标 |
| 19 | 绿化种植 | GreenPlanting | 14-10.10.18.03 | 国标 |
| 20 | 场地设施 | SiteFacilities | 14-10.10.21.01 | 按国标扩展 |
| 21 | 停车场 | Parking | 10-21.50.00.01 | 按国标扩展 |
| 22 | 出入口 | Exit | 12-18.20.10.01 | 按国标扩展 |
| 23 | 周边环境 | SurroundingEnv | 11-03.20.00.01 | 按国标扩展 |
| 24 | 户 | Household | 12-02.00.00.01 | 按国标扩展 |
| 25 | 单元 | Unit | 12-02.00.00.02 | 按国标扩展 |
| 26 | 自动扶梯 | Escalator | 14-10.20.30.09 | 国标 |
| 27 | 走廊 | Corridors | 12-18.10.10 | 国标 |
| 28 | 天桥 | Footbridge | 11-02.10.35 | 国标 |
| 29 | 连廊 | Skybridge | 12-18.30.10 | 国标 |
| 30 | 退线 | Offline | 11-03.00.00.01 | 按国标扩展 |
| 31 | 方案指标 | OptionIndex | 20-20.20.00.01 | 按国标扩展 |
| 32 | 地块指标 | SiteIndex | 20-20.15.10.01 | 按国标扩展 |
| 33 | 日照条件 | SunLightConditions | 20-20.15.40.01 | 按国标扩展 |
| 34 | 建筑墙 | Wall | 14-10.20.03 | 国标 |
| 35 | 墙垛 | Pier | 14-10.20.03.01 | 按国标扩展 |
| 36 | 外墙勒脚 | Plinth | 14-10.20.03.02 | 按国标扩展 |
| 37 | 护角防撞板 | Bumper | 15-10.20.40.10 | 国标 |
| 38 | 建筑柱 | Column | 14-10.20.06 | 国标 |
| 39 | 吊顶 | SuspendedCeiling | 14-10.20.24 | 国标 |
| 40 | 屋顶 | Roof | 14-10.20.15 | 国标 |
| 41 | 门 | Door | 14-10.20.09 | 国标 |
| 42 | 门联窗 | DoorWindow | 14-10.20.09.91 | 按国标扩展 |
| 43 | 窗 | Window | 14-10.20.12 | 国标 |
| 44 | 转角窗 | CornerWindow | 14-10.20.12.01 | 按国标扩展 |
| 45 | 天窗 | Skylight | 14-10.20.12.02 | 按国标扩展 |
| 46 | 反檐 | ReverseEaves | 14-10.20.15.14 | 按国标扩展 |
| 47 | 平屋面 | FlatRoof | 14-10.20.15.03 | 国标 |
| 48 | 坡屋面 | SlopingRoof | 14-10.20.15.06 | 国标 |
| 49 | 瓦屋面 | TileRoof | 15-07.30.10 | 国标 |
| 50 | 女儿墙 | Parapet | 14-10.20.15.16 | 按国标扩展 |
| 51 | 排水板 | DrainBoard | 14-40.20.12.01 | 按国标扩展 |
| 52 | 砼挑檐板 | CorniceBoard | 14-10.20.15.18 | 按国标扩展 |
| 53 | 雨水口 | ConcreteSiphonInlet | 14-40.20.12.09 | 国标 |
| 54 | 建筑坡道 | BuildingRamp | 14-10.20.33 | 国标 |
| 55 | 台阶 | FootStep | 14-10.20.36 | 国标 |
| 56 | 檐沟 | Gutter | 14-10.20.45.09 | 国标 |
| 57 | 明沟 | OpenDitch | 14-40.20.12.06 | 国标 |
| 58 | 栏杆扶手 | Balustrade | 14-10.20.42 | 国标 |
| 59 | 散水 | Apron | 14-10.20.39 | 国标 |
| 60 | 雨篷 | Canopy | 14-10.20.48 | 国标 |
| 61 | 阳台 | Balcony | 14-10.20.51 | 国标 |
| 62 | 集水坑 | CoverPlate | 14-40.20.12.10 | 按国标扩展 |
| 63 | 盖板 | BrickMembrane | 14-10.20.18.03 | 国标 |
| 64 | 竖井 | Shaft | 12-17.21.00.01 | 按国标扩展 |
| 65 | 车位 | ParkingLot | 10-21.50.00.02 | 按国标扩展 |
| 66 | 轴网 | Axisnet | 14-10.20.18.15 | 按国标扩展 |
| 67 | 标高 | Elevations | 14-10.20.18.17 | 按国标扩展 |
| 68 | 建筑墙洞 | BuildingWallHole | 14-10.20.03.03 | 按国标扩展 |
| 69 | 房间分割面 | RoomDivisionPlane | 12-02.00.00.03 | 按国标扩展 |
| 70 | 建筑楼板 | BuildingFloor | 14-10.20.18 | 国标 |
| 71 | 建筑板洞 | BuildingFloorHole | 14-10.20.18.01 | 按国标扩展 |
| 72 | 电梯 | Lifts | 14-10.20.30.03 | 国标 |
| 73 | 面域 | Areas | 12-03.00.00.01 | 按国标扩展 |
| 74 | 老虎窗 | LaohuWindow | 14-10.20.12.03 | 按国标扩展 |
| 75 | 项目基点 | ProjectBasePoint | 20-10.00.00.01 | 按国标扩展 |
| 76 | 视图 | View | 20-20.35.00.01 | 按国标扩展 |
| 77 | 楼层 | Floors | 14-10.20.18.02 | 按国标扩展 |
| 78 | 楼栋 | Building | 10-01.00.00.01 | 按国标扩展 |
| 79 | 项目信息 | ProjectInfo | 20-10.35.00.01 | 按国标扩展 |
| 80 | 常规模型 | OrdinaryModel | 14-10.20.00.90 | 按国标扩展 |
| 81 | 工程做法 | EngineeringPractices | 15-01.30.00.01 | 按国标扩展 |
| 82 | 梯段 | Flight | 14-10.20.27.01 | 按国标扩展 |
| 83 | 平台 | Platform | 14-10.20.27.02 | 按国标扩展 |
| 84 | 建筑楼梯 | BuildingStairs | 14-10.20.27 | 国标 |
| 85 | 构造层 | ConstructionLayer | 14-10.20.18.20 | 按国标扩展 |
| 86 | 房间 | Room | 12-02.01.00.01 | 按国标扩展 |
| 87 | 分区 | Partition | 11-03.10.00.01 | 按国标扩展 |
| 88 | 场地 | Site | 14-10.10.00.01 | 按国标扩展 |
| 89 | 装配式建筑墙 | PrefabricatedBuildingWall | 14-10.20.03.04 | 按国标扩展 |
| 90 | 天棚 | ArchSunshade | 14-10.20.24 | 国标 |

### 7.2 结构专业构件完整列表（节选）

| 序号 | 构件名称 | 构件代码 | 编码 |
|-----|---------|---------|------|
| 1 | 框架梁 | Beam | 14-20.20.06 |
| 2 | 非框架梁 | NonFrameBeam | 14-20.20.06.01 |
| 3 | 连梁 | LinkBeam | 14-20.20.06.03 |
| 4 | 结构柱 | StructuralColumn | 14-20.20.09 |
| 5 | 斜杆 | Bracing | 14-20.30.24.01 |
| 6 | 暗柱 | EmbeddedColumn | 14-20.20.09.04 |
| 7 | 结构墙 | StructuralWall | 14-10.20.03.04 |
| 8 | 现浇板 | Slab | 14-20.20.03 |
| 9 | 垫层 | Cushion | 14-20.10.09.01 |
| 10 | 独立基础 | IsolatedFD | 14-20.10.03.03 |
| 11 | 条形基础 | StripFD | 14-20.10.03.06 |
| 12 | 筏板基础 | RaftFD | 14-20.10.03.09 |
| 13 | 筏板主筋 | RaftMainR | 15-03.30.00.01 |
| 14 | 筏板负筋 | RaftNegativeR | 15-03.30.00.02 |
| 15 | 柱墩 | ColumnBase | 14-20.10.03.91 |
| 16 | 桩 | Pile | 14-20.10.15 |
| 17 | 桩承台 | PileCap | 14-20.10.15.11 |
| 18 | 基础梁 | FDBeam | 14-20.10.06 |
| 19 | 集水坑/电梯坑 | Sump | 14-40.20.12.61 |
| 20 | 挡土墙 | BrickWall | 15-32.10.40.01 |
| 21 | 构造墙 | StructWall | 14-10.20.03.06 |
| 22 | 人防门框墙 | BarAirDefenseWall | 14-10.20.03.07 |
| 23 | 牛腿 | Corbel | 14-20.20.09.01 |
| 24 | 柱帽 | ColumnCap | 14-20.20.09.02 |
| 25 | 构造柱 | TieColumn | 14-20.20.09.03 |
| 26 | 梯梁 | LadderBeam | 14-20.20.06.02 |
| 27 | 圈梁 | TieBeam | 14-20.20.06.05 |
| 28 | 空心楼盖板 | BarHollowFloorSlab | 14-10.20.03.01 |
| 29 | 板受力筋 | PlateMainR | 14-10.20.03.02 |
| 30 | 板负筋 | PlateNegativeReinforcement | 14-10.20.03.03 |
| 31 | 直行梯段 | Flight | 14-10.20.27.01 |
| 32 | 螺旋梯段 | SpiralFlight | 14-10.20.27.02 |
| 33 | 挑檐 | Eave | 14-10.20.15.11 |
| 34 | 栏板 | Parapet | 14-10.20.42.01 |
| 35 | 雨篷 | Canopy | 14-10.20.48 |
| 36 | 飘窗 | SwingWin | 14-10.20.12.03 |
| 37 | 压顶 | Coping | 14-10.20.03.09 |
| 38 | 坡道 | Ramp | 14-10.20.33 |
| 39 | 基础板带 | FDSlabStrip | 14-10.20.03.04 |
| 40 | 楼层板带 | FloorStrip | 14-10.20.03.05 |
| 41 | 后浇带 | PostCastStrip | 14-20.20.21.04 |
| 42 | 保温层 | InsulatingLayer | 14-07.20.10.01 |
| 43 | 板洞 | SlabHole | 14-10.20.18.01 |
| 44 | 板加腋 | PlateAndArmpit | 14-10.20.05.01 |
| 45 | 墙洞 | Opening | 14-10.20.03.10 |
| 46 | 壁龛 | Alcove | 14-10.20.03.11 |
| 47 | 楼梯井 | StairWell | 14-10.20.27.03 |
| 48 | 天井 | Courtyard | 13-05.20.15 |
| 49 | 叠合板 | LaminatedSlab | 14-20.10.03.90 |
| 50 | 预制墙 | PrecastWall | 14-10.20.03.13 |
| 51 | 节点 | Node | 14-20.30.27.02 |
| 52 | 轴线 | Axis | 14-10.20.18.11 |
| 53 | 网格 | Grid | 14-10.20.18.12 |
| 54 | 装配式楼梯 | PrefabricatedStairs | 14-10.20.27.05 |
| 55 | 装配式梯段 | PrefabricatedStairSection | 14-10.20.27.06 |
| 56 | 钢柱 | SteelColumn | 14-20.30.03 |
| 57 | 钢梁 | SteelBeam | 14-20.30.06 |
| 58 | 钢楼板 | Plate | 14-20.30.03.02 |
| 59 | 螺栓 | Bolt | 14-20.10.15.13 |
| 60 | 焊缝 | Weld | 14-20.30.27.01 |
| 61 | 钢构节点 | Joint | 14-20.30.27 |
| 62 | 构件组 | Assembly | 14-20.30.00.01 |
| 63 | 实体切割 | SolidCut | 14-20.30.00.02 |
| 64 | 线切割 | LineCut | 14-20.30.00.03 |
| 65 | 面切割 | PlaneCut | 14-20.30.00.04 |
| 66 | 实体并 | SolidUnion | 14-20.30.00.05 |
| 67 | 实体交 | SolidIntersect | 14-20.30.00.06 |
| 68 | 型钢混凝土框架梁 | SRCFrameBeam | 14-20.20.06.09 |
| 69 | 钢板混凝土剪力墙 | SPRCWalls | 14-10.20.03.16 |
| 70 | 钢网架 | SteelMeshFrame | 14-20.30.12 |
| 71 | 钢屋架 | SteelRoofTruss | 14-20.30.09 |
| 72 | 钢桁架 | SteelTruss | 14-20.30.09 |
| 73 | 钢支撑 | SteelSupport | 14-20.30.25 |
| 74 | 钢檩条 | SteelPurlins | 14-20.30.15 |
| 75 | 钢梯 | SteelLadder | 14-10.20.27.04 |
| 76 | 人防墙 | CivilAirDefenseWall | 14-10.20.03.05 |
| 77 | 暗梁 | EmbedBeam | 14-20.20.06.06 |
| 78 | 组合结构柱 | CompositeStructureColumn | 14-20.20.09.06 |

### 7.3 机电专业构件完整列表

#### 暖通专业

| 序号 | 构件名称 | 构件代码 | 编码 |
|-----|---------|---------|------|
| 1 | 冷水机组 | WaterChillingUnit | 15-24.45.20 |
| 2 | 冷却塔 | CoolingTower | 15-24.45.30 |
| 3 | 热泵机组 | HeatPumpUnit | 15-25.20.30 |
| 4 | 锅炉 | Boiler | 15-25.20.10 |
| 5 | 热交换器 | HeatExchanger | 15-25.15.01 |
| 6 | 空调水处理设备 | AirConditioningWaterTreatmentEquipment | 15-25.20.40.01 |
| 7 | 冷热源其他设备 | ColdAndHeatSourceOtherEquipment | 15-25.20.00.91 |
| 8 | 空气处理机组 | AirHandlingUnit | 15-24.45.40 |
| 9 | 风机盘管 | FanCoilUnit | 15-24.10.40 |
| 10 | 室内空气调节设备 | IndoorAirConditioningEquipment | 15-24.45.00.91 |
| 11 | 多联式空调机组 | VRVAirConditioningUnit | 15-24.45.00.92 |
| 12 | 分体空调 | SplitAirConditioner | 15-24.45.00.93 |
| 13 | 风机 | Fan | 15-24.05.00.01 |
| 14 | 空调通风其他设备 | AirConditioningVentilationOtherEquipment | 15-24.00.00.91 |
| 15 | 散热器 | Radiator | 15-25.10.10 |
| 16 | 分集水器 | DistributionManifold | 15-25.15.00.01 |
| 17 | 燃气设备 | GasEquipment | 15-21.30.00.01 |
| 18 | 风管阀门 | DuctValve | 30-43.15.00.01 |
| 19 | 消声器 | Muffler | 15-24.15.10 |
| 20 | 静压箱 | PlenumChamber | 15-24.05.00.02 |
| 21 | 风管其他附件 | DuctOtherAttachment | 15-24.05.00.91 |
| 22 | 地热盘管 | GeothermalCoil | 15-25.00.00.91 |
| 23 | 末端风口 | EndTuyere | 15-24.05.00.03 |
| 24 | 风管 | Duct | 30-43.15.00 |
| 25 | 风管管件 | DuctFitting | 30-43.15.00.03 |
| 26 | 软风管 | FlexibleDuct | 30-43.15.00.05 |
| 27 | 挡烟垂壁 | SmokeBarrier | 15-22.00.00.91 |

#### 给水排水专业

| 序号 | 构件名称 | 构件代码 | 编码 |
|-----|---------|---------|------|
| 1 | 水泵 | Pump | 15-23.35.10 |
| 2 | 组合式供水装置 | CombinedWaterSupplyDevice | 15-23.35.05.01 |
| 3 | 储水设备 | WaterStorageEquipment | 30-30.50.10 |
| 4 | 稳压设备 | VoltageStabilizingEquipment | 14-40.00.00.01 |
| 5 | 给水处理设备 | WaterSupplyTreatmentEquipment | 15-25.20.40.02 |
| 6 | 排水处理设备 | DrainageTreatmentEquipment | 15-23.45.00.01 |
| 7 | 加热贮热设备 | HeatingAndHeatStorageEquipment | 15-25.15.00.02 |
| 8 | 卫浴器具 | BathRoomAppliance | 15-12.20.20 |
| 9 | 收集提升装置 | CollectLiftingDevice | 14-40.00.00.02 |
| 10 | 喷头 | Sprinkler | 14-40.30.27.01 |
| 11 | 消火栓 | Hydrant | 30-30.60.00.01 |
| 12 | 消防炮 | FireMonitor | 30-30.60.00.02 |
| 13 | 气体灭火 | GasFireExtinguishing | 30-30.20.00 |
| 14 | 灭火器 | FireExtinguisher | 30-30.60.10 |
| 15 | 水泵接合器 | PumpAdapter | 15-22.40.00.01 |
| 16 | 水管阀门 | PipeValve | 15-23.05.20.01 |
| 17 | 地漏 | FloorDrain | 15-23.10.40.01 |
| 18 | 雨水斗 | RainBucket | 15-23.15.40 |
| 19 | 水管其他附件 | PipeOtherAttachment | 15-23.05.40.02 |
| 20 | 管道 | Pipe | 15-23.05.10 |
| 21 | 管件 | PipeFitting | 15-23.05.10.01 |
| 22 | 软管 | FlexiblePipe | 15-23.05.10.02 |

#### 电气专业

| 序号 | 构件名称 | 构件代码 | 编码 |
|-----|---------|---------|------|
| 1 | 灯具 | Lighting | 30-51.20.00 |
| 2 | 开关 | Switch | 30-51.40.10 |
| 3 | 插座 | Socket | 30-51.40.20.10 |
| 4 | 配电柜(箱) | DistributionBoard | 15-26.05.10.01 |
| 5 | 变配电设备 | PowerEquipment | 15-26.05.40 |
| 6 | 探测器 | Detector | 15-22.20.00.01 |
| 7 | 火灾报警按钮 | FireAlarmButton | 15-22.20.00.02 |
| 8 | 火灾警报器 | FireAlarmBell | 15-22.20.00.03 |
| 9 | 火灾控制器 | FireAlarmPanel | 15-22.20.00.04 |
| 10 | 消防箱柜 | FireFightingCabinet | 30-30.60.20 |
| 11 | 信息模块 | InformationModule | 30-55.25.00.01 |
| 12 | 广播 | Broadcast | 30-55.25.00.02 |
| 13 | 综合布线 | StructuredCabling | 30-55.25.00 |
| 14 | 安防 | Security | 15-27.20.00.01 |
| 15 | 有线电视 | CATV | 30-55.45.00 |
| 16 | 楼宇自控 | BAS | 15-27.15.00.01 |
| 17 | 停车场管理系统 | ParkingManagementSystem | 15-11.10.10.01 |
| 18 | 弱电箱柜 | WeakCurrentCabinet | 30-55.25.00.03 |
| 19 | 接闪器 | AirTerminal | 15-26.15.00.01 |
| 20 | 等电位端子箱 | EquipotentialBox | 15-26.15.00.02 |
| 21 | 电缆桥架配件 | CableTrayFitting | 15-26.20.30.01 |
| 22 | 线管配件 | ConduitFitting | 15-26.20.10.01 |
| 23 | 导线 | Wire | 15-26.20.05.01 |
| 24 | 电缆桥架 | CableTray | 30-53.20.10 |
| 25 | 线管 | Conduit | 30-53.20.30 |
| 26 | 母线槽 | Busbar | 15-26.20.15.01 |
| 27 | 母线槽配件 | BusbarFitting | 15-26.20.15.02 |

### 7.4 施工管理构件完整列表

| 序号 | 构件名称 | 构件代码 | 编码 |
|-----|---------|---------|------|
| 1 | 外脚手架 | OuterScaffold | 15-01.20.50 |
| 2 | 钢管外脚手架立杆 | SteelTubularStandingTube | 15-01.20.50.01 |
| 3 | 盘扣式立杆 | DiskLockSteelTubularStandingTube | 15-01.20.50.02 |
| 4 | 钢管外脚手架水平杆 | SteelTubularHorizontalTube | 15-01.20.50.03 |
| 5 | 盘扣式水平杆 | DiskLockSteelTubularHorizontalTube | 15-01.20.50.04 |
| 6 | 钢管外脚手架剪刀撑 | SteelTubularDiagonalBracing | 15-01.20.50.05 |
| 7 | 盘扣式竖向斜杆 | DiskLockSteelTubularVerticalDiagonalBracing | 15-01.20.50.06 |
| 8 | 内脚手架 | InnerScaffold | 15-01.20.50.10 |
| 9 | 满堂脚手架 | FullHallScaffold | 15-01.20.50.20 |
| 10 | 附着式升降脚手架 | AttachedLiftScaffold | 15-01.20.50.30 |
| 11 | 吊篮 | HangingBasket | 15-01.20.50.40 |
| 12 | 基坑支护 | PitSupport | 15-01.10.10 |
| 13 | 土钉墙 | SoilNailingWall | 15-01.10.10.01 |
| 14 | 钢板桩 | SteelSheetPile | 15-01.10.10.02 |
| 15 | 灌注桩 | BoredPile | 15-01.10.10.03 |
| 16 | 锚杆 | AnchorRod | 15-01.10.10.04 |
| 17 | 地下连续墙 | DiaphragmWall | 15-01.10.10.05 |
| 18 | 模板 | Formwork | 15-01.20.10 |
| 19 | 木模板 | WoodFormwork | 15-01.20.10.01 |
| 20 | 钢模板 | SteelFormwork | 15-01.20.10.02 |
| 21 | 铝合金模板 | AluminumFormwork | 15-01.20.10.03 |
| 22 | 模板支撑 | FormworkSupport | 15-01.20.10.10 |
| 23 | 塔吊 | TowerCrane | 15-01.25.10 |
| 24 | 施工电梯 | ConstructionElevator | 15-01.25.20 |
| 25 | 卸料平台 | UnloadingPlatform | 15-01.25.30 |

## 8. GFC枚举值详细列表（附录I）

### 8.1 结构专业枚举（D.400-D.450）

| 枚举ID | 枚举名称 | 枚举值 |
|-------|---------|-------|
| D.400 | 导荷方式 | 未设置、单向板、梯形三角形 |
| D.401 | 工况类型 | 恒载、活载、风载、水平地震、竖向地震、人防、吊车、温度、土、水、非线性组合 |
| D.402 | 工况方向类型 | 水平X、水平Y、竖向、其它 |
| D.403 | 工况来源 | 基本工况、建模自定义工况、基础工况、组合梁施工工况、时程工况 |
| D.404 | 截面设计类型 | 正截面设计、斜截面设计 |
| D.405 | 荷载组合类别 | 非地震组合、水平地震为主、竖向地震为主、只有竖向地震、人防组合 |
| D.406 | 工况组合类别 | 单工况、基本组合、标准组合、频遇组合、准永久组合、预组合 |
| D.407 | 构件数据来源 | PM、鉴定加固、优化设计 |
| D.408 | 梁属性 | 普通梁、托墙转换梁、托柱转换梁、门式刚梁、消能梁、组合梁、吊车梁 |
| D.409 | 梁建模类别 | 普通梁、按次梁输入的次梁、空心板肋梁、地基梁 |
| D.410 | 支座约束类型 | 刚接、铰接、滑动、半刚接 |
| D.411 | 支座类型 | 无支座、梁支座、柱支座、边框柱支座、框支柱支座、支撑支座、斜柱支座、水平支撑支座、墙支座 |
| D.412 | 网架类别 | 网架、单层网壳、双层网壳、立体桁架、中心支撑、偏心支撑、一般桁架杆件、门刚支撑、温室大棚 |
| D.413 | 构件重要性类别 | 关键构件、普通竖向构件、重要水平构件、普通水平构件、耗能构件 |
| D.414 | 桁架杆件标志 | 桁架上弦杆、桁架腹杆、桁架中层弦杆、桁架下弦杆、支座腹杆 |
| D.415 | 宽厚比等级 | S1、S2、S3、S4、BS1、BS2、BS3、S5 |
| D.416 | 延性等级 | 延性等级I、II、III、IV、V |
| D.417 | 构件温度 | 升温、降温、防火升温 |
| D.418 | 膨胀类型 | 膨胀型、非膨胀型、水泥砂浆 |
| D.419 | 特殊斜筋类型 | 不配置斜筋、交叉斜筋、对角斜筋、对角暗撑 |
| D.420 | 组合梁连接类型 | 无抗剪连接件、完全抗剪连接、不完全抗剪连接 |
| D.421 | 性能设计标志 | 小震、中震弹性、中震不屈服、中震极限承载力、大震弹性、大震不屈服、大震极限承载力 |
| D.422 | 支撑标志 | 斜柱、斜杆 |
| D.423 | 支撑类型 | 人字形、V形、十字形、一字形 |
| D.424 | 设计构件类型 | 梁、主梁、柱、主柱、支撑、墙梁、墙柱、组合墙、边缘构件、次梁、次主梁、空心板肋梁、板、墙梁主梁、楼梯、空心板、蒙皮、定义支撑的连接、弹性连接、非超单元弹性板、墙身 |
| D.425 | 配筋计算方法 | 单偏压、双偏压 |
| D.426 | 钢筋调整标志 | 未调整、根据楼层受剪承载力调整 |
| D.427 | 配筋与墙柱连接方向 | 与单方向墙相连、与多个方向墙相连 |
| D.428 | 加强区标志 | 非加强区、加强区、加强区上一层 |
| D.429 | 墙属性 | 普通墙、短肢剪力墙、防屈曲钢板墙 |
| D.430 | 边缘构件形状类型 | 一字形、L形、T形、十字交叉形、一字形+柱、L形+柱、T形+柱、十字交叉形+柱、一字形+中柱、Y形、Y形+中柱、工字形、工字形+柱、Z形、Z形+柱 |
| D.431 | 相交墙形式 | 一字形、L形、T形 |
| D.432 | 墙稳定验算位置 | 翼缘、腹板 |
| D.433 | 钢材等级 | Q235、Q345、Q390、Q420、Q460、Q500、Q550、Q620、Q690、Q235GJ~Q460GJ、Q355~Q460M |
| D.434 | 钢筋级别 | HPB235、HPB300、HRB335、HRB400、HRB500、LZDL550、HRB600、HRB635、CRB600H、RRB400、HRBF500、HRBF335、HRBF400、HRBF335E~HRBF500E、YJG、EJG、SJG、XSJG |
| D.435 | 所属构件类型 | 节点、网格、轴线、梁、柱、支撑、墙、楼板、墙洞、板洞、悬挑板 |
| D.436 | 插入点 | 左上、左中、左下、中上、中中、中下、右上、右中、右下 |
| D.437 | 关系类型 | 焊接关系、螺栓关系、构件组关系、节点关系、布尔关系 |
| D.438 | 切角类型 | 内圆角、外圆角、三角形切角 |
| D.439 | 螺栓类型 | 螺栓、锚栓、栓钉、只打孔 |
| D.440 | 螺栓孔类型 | 圆孔、长圆孔、扩大孔 |
| D.441 | 安装类型 | 工地安装、工场安装 |
| D.442 | 焊缝类型 | 对接焊缝、角焊缝 |
| D.443 | 角焊缝类型 | 单面角焊缝、双面角焊缝 |
| D.444 | 对接焊缝类型 | 双边V形、单边V形、双边U形、单边U形、K形、X形、I形、熔嘴电渣焊 |
| D.445 | 布尔类型 | 线切割、面切割、实体减、实体并、实体交 |
| D.446 | 门节能类型 | 外门、阳台门、户门、内门、封闭阳台门 |
| D.447 | 边界条件 | 普通墙、沉降缝、伸缩缝、抗震缝、地下墙、绝热 |
| D.448 | 朝向 | 东、南、西、北 |
| D.449 | 老虎窗类型 | 三角坡、双坡、三坡、梯形坡、平顶窗 |

### 8.2 机电专业枚举（D.150-D.220）

| 枚举ID | 枚举名称 | 枚举值 |
|-------|---------|-------|
| D.160 | 排水处理设备类型 | 预处理设备、深度处理设备、消毒设备、油水分离器、污水处理设备、中水处理设备、游泳池水处理设备 |
| D.161 | 加热贮热设备类型 | 电热水器、太阳能热水器、燃气热水器、空气源热泵热水器、开水器、其他 |
| D.162 | 卫浴器具类型 | 坐便器、小便器、蹲便器、浴盆、拖布池、淋浴器、洗手盆、洗涤盆、化验盆、净身盆、洗衣机、污水池、盥洗槽、淋浴房、其他 |
| D.163 | 存水弯 | 无、P型存水弯、S型存水弯 |
| D.164 | 给水配件类型 | 感应水嘴、延时自闭水嘴、单阀水嘴、混合水嘴、感应冲洗阀、延时自闭式冲洗阀等 |
| D.165 | 收集提升装置类型 | 污水收集罐、污水提升装置、模块组合式雨水池子、雨水提升装置、雨水初期弃流装置 |
| D.166 | 喷头类型 | 下垂式喷头、直立式喷头、开式喷头、闭式喷头、水幕喷头、干式喷头、水喷雾喷头、ESFR喷头、家用喷头、其他 |
| D.167 | 响应时间指数 | 80、50、28±8 |
| D.168 | 消火栓类型 | 组合式消火栓箱、普通消火栓箱、消防软管卷盘箱、轻便消防水龙箱、轻便消防水龙柜、其他、室外消火栓 |
| D.169 | 明装/暗装 | 明装、暗装 |
| D.170 | 灭火器类型 | 手提式、推车式 |
| D.171 | 灭火剂类型 | 干粉-碳酸氢钠、干粉-磷酸铵盐、二氧化碳、泡沫、水型、卤代烷 |
| D.172 | 消防炮类型 | 防水炮、手动消防水炮、电控消防水炮、防爆消防水炮、移动消防水炮、主动灭火装置 |
| D.173 | 气体灭火类型 | 七氟丙烷钢瓶、IG541气体灭火、泄压阀、其它 |
| D.174 | 水泵接合器类型 | 地上式水泵接合器、地下式水泵接合器、墙壁式水泵接合器 |
| D.175 | 水管阀门类型 | 闸阀、蝶阀、球阀、止回阀、二通阀、电磁阀、平衡阀、倒流防止器、温控阀等40+种 |
| D.176 | 控制方式 | 手动、电动 |
| D.177 | 连接方式 | 螺纹连接、承插连接、粘（熔）连接、卡箍（套）连接、法兰连接、焊接连接、无 |
| D.178 | 地漏类型 | 水封地漏、直通式地漏、地面清扫口、其它、侧墙式地漏 |
| D.179 | 雨水斗类型 | 重力流雨水斗、半有压雨水斗、虹吸雨水斗、其它 |
| D.180 | 水管附件类型 | 检查口、流量传感器、水表、水流指示器、压力开关等40+种 |
| D.185 | 风管类别 | 矩形风管、圆形风管 |
| D.186 | 末端风口类型 | 散流器、单层百叶、双层百叶、格栅风口、旋流风口、条缝风口、喷口、多叶风口、板式排烟口、其他 |
| D.187 | 风口箭头方向 | 无、送风、回风 |
| D.188 | 换热方式 | 水-水、水-汽 |
| D.189 | 空气处理机组类型 | 组合式空调箱、新风机组、热交换机、恒温恒湿单元式空调机组、组合式净化空调机组、组合式溶液调湿型空调机组、其他 |
| D.190 | 管制类型 | 二管制、四管制 |
| D.191 | 结构类型 | 风管式、两面出风、四面出风、挂壁式、立式 |
| D.192 | 多联式空调机组类型 | 室内机、室外机 |
| D.193 | 分体空调类型 | 室内机、室外机 |
| D.194 | 风机类型 | 离心风机、轴流风机、斜流风机、管道风机、屋顶风机、诱导风机、排气扇、其他 |
| D.195 | 电机类型 | 单速、双速 |
| D.196 | 散热器类型 | 柱型、翼型、柱翼型、板翼型、板式、扁管式、背篓式、其他 |
| D.197 | 风管阀门类型 | 70°C防火阀、150°C防火阀、280°C防火阀、280°C防火排烟阀、排烟阀、电动常开防火阀、电动常闭防火阀等 |
| D.198 | 消声机理 | 阻性消声、抗性消声 |
| D.199 | 风管其他附件类型 | 风管软接头、压力传感器、压差传感器、其他 |
| D.200 | 冷水机组类型 | 离心式、螺杆式、活塞式、其他 |
| D.201 | 冷却塔类型 | 方形横流、方形逆流、圆形横流、圆形逆流、其他 |
| D.202 | 热泵机组类型 | 空气源热泵、地源热泵、水源热泵 |
| D.203 | 锅炉类型 | 常压热水锅炉、真空热水锅炉、蒸汽锅炉、其他 |
| D.204 | 燃料类型 | 燃气、燃油、燃煤、电能、生物质 |
| D.205 | 光源类别 | 荧光灯、LED灯、金属卤化物灯、钠灯、白炽灯、汞灯、HID灯 |
| D.206 | 明/暗装 | 明装、暗装 |
| D.207 | 插座类型 | 两孔、三孔、五孔 |
| D.208 | 配电箱类型 | 照明配电箱、动力配电箱、应急照明配电箱、双电源切换箱、控制箱、住宅照明箱、电表箱 |
| D.209 | 变压器类型 | 油浸式、干式 |
| D.210 | 调压方式 | 有载调压、无载调压 |
| D.211 | 变配电设备类型 | 变压器、发电机、直流屏、高压柜、低压柜、其他设备 |
| D.212 | 探测器类型 | 感烟探测器、感温探测器、其他探测器、可燃气体探测器 |
| D.213 | 编码方式 | 在线编码、智能编码 |
| D.214 | 火灾警报器类型 | 火灾声光警报器、火灾声警报器 |
| D.215 | 火灾控制器类型 | 火灾报警控制器、消防联动控制器、防火门监控器、电气火灾监控器 |
| D.216 | 材质 | (根据具体材料) |
| D.217 | 综合布线设备类型 | 配线架、语音插座、交换机、放大器、前端设备、连接器、信息插座、其他 |
| D.218 | 摄像机类型 | CCD摄像机、CMOS摄像机、超宽动态摄像机、紫外线摄像机、X射线摄像机 |
| D.219 | 传输方式 | 同轴电缆、双绞线、总线系统、无线网 |
| D.220 | 安防设备类型 | 摄像机、入侵报警器、门禁、巡更、前端设备、安防箱柜 |
