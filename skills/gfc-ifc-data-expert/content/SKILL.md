---
name: gfc-ifc-data-expert
description: GFC与IFC数据格式专家技能。当用户询问GFC数据格式、IFC数据格式、BIM数据交换标准、构件数据转换、GFC与IFC对比、建筑信息模型数据格式、Revit API、IFC Schema、GFC SDK、广联达数据接口等话题时使用。提供GFC和IFC的Schema定义、数据结构、实体类型、属性定义、数据组织方式等专业指导，支持BIM数据格式转换和技术实现。
---

# GFC与IFC数据格式专家

## 核心能力

本技能提供GFC（Glodon Framework Classification）和IFC（Industry Foundation Classes）两大BIM数据交换标准的全面技术支持，帮助用户理解和处理建筑信息模型数据。

## GFC数据格式

### 概述

GFC（数字建筑数据交换标准）是由广联达科技股份有限公司开发的建筑行业数据交换标准，版本3.1.1.0，版权1998-2022。

**标准体系**（依据GB/T 51269-2017）:
- 《建设工程BIM数据模型标准（建筑工程篇）》
- 《建设工程BIM数据模型标准（建筑工程篇-交付数据手册）》

**应用场景**:
- 设计阶段：建筑、结构、机电（MEP）全专业构件
- 施工管理：虚拟建造、设计资料、项目预算、质量要求
- 工程量：全专业构件算量

### 应用场景划分

| 应用场景 | 构件/对象划分 |
|---------|--------------|
| 设计 | 建筑专业构件、结构专业构件、机电专业公共构件、暖通专业构件、给排水专业构件、电气专业构件、施工管理构件 |
| 施工管理 | 虚拟建造对象、设计资料对象、项目预算对象、质量要求对象 |
| 工程量 | 工程量建筑/结构/机电/给排水/暖通/电气/施工专业构件 |

### 主要实体类型（200+）

**几何元素**
- 曲线类: GfcCurve2d, GfcCurve3d, GfcLine, GfcLine2d, GfcLine3d, GfcArc2d, GfcArc3d, GfcCircle, GfcEllipse2d, GfcPolyline, GfcNurbsCurve2d, GfcOffsetCurve2d
- 曲面类: GfcSurface, GfcNurbsSurface, GfcPlane, GfcRuledSurface, GfcHelicoid
- 实体类: GfcSolidShape, GfcManifoldSolidShape, GfcBrepBody, GfcCuboidBody, GfcCylinder, GfcCylinderShape, GfcConeShape, GfcSphere, GfcSphereShape, GfcTorus, GfcExtrudedBody, GfcPolyhedronBody

**建筑构件**
- GfcBuilding (建筑), GfcFloor (楼层), GfcSite (场地), GfcElement (构件)
- GfcElementShape, GfcElementType, GfcRepresentation, GfcRepresentationItem

**截面定义**
- GfcSection, GfcParameterizedSection, GfcArbitrarySection
- GfcRectangleSection, GfcRectangleHollowSection
- GfcCircleSection, GfcCircleHollowSection
- GfcLShapeSection, GfcTShapeSection, GfcEllipseSection

**样式与表现**
- GfcAppearanceMaterial, GfcPBRAppearanceMaterial, GfcPHONGAppearanceMaterial
- GfcColor, GfcFillAreaStyle, GfcFillStyle
- GfcCurveStyle, GfcLineType, GfcLinePattern
- GfcTextStyle, GfcFontStyle, GfcSurfaceTexture, GfcImage

**属性系统**
- GfcProperty (属性基类), GfcSimpleProperty, GfcComplexProperty
- GfcBooleanProperty, GfcIntegerProperty, GfcDoubleProperty, GfcStringProperty
- GfcBooleanListProperty, GfcIntegerListProperty, GfcDoubleListProperty, GfcStringListProperty
- GfcEntityProperty, GfcEntityListProperty
- GfcGeoProperty, GfcGeoListProperty, GfcSectionProperty, GfcSectionListProperty
- GfcPropertySet (属性集)

**拓扑结构**
- GfcTopology, GfcFace, GfcEdge, GfcVertex
- GfcCoedge, GfcCoedgeList, GfcCoedgeListEx
- GfcLoop, GfcSimpleLoop, GfcPolyhedralLoop
- GfcPolyhedralFace, GfcPolyhedralEdge

**关系定义**
- GfcRelationShip (关系基类)
- GfcRelAggregates (聚合), GfcRelDecomposes (分解)
- GfcRelConnects, GfcRelConnectsElements, GfcRelConnectsPathElements
- GfcRelCoversBldgElements (覆盖), GfcRelVoidsElement (挖空)
- GfcRelDefines, GfcRelDefinesByProperties, GfcRelDefinesByType

**工程量清单**
- GfcBillDetail, GfcBillTotal (清单明细/汇总)
- GfcQuotaDetail, GfcQuotaTotal (定额明细/汇总)
- GfcSteelDetail, GfcSteelTotal (钢筋明细/汇总)

### 基本数据类型

| 类型 | 说明 |
|------|------|
| GfcBoolean | 布尔值 |
| GfcInteger | 整数 |
| GfcDouble | 双精度浮点数 |
| GfcString | 字符串 |
| GfcText | 文本 |
| GfcLabel | 标签 |
| GfcDate | 日期 |
| GfcTime | 时间 |
| GfcDateTime | 日期时间 |
| GfcElev | 高程 |
| GfcIdentity | 标识符 |

### 几何坐标类

- GfcCoordinates2d, GfcCoordinates3d (坐标)
- GfcVector2d, GfcVector3d (向量)
- GfcPoint (点), GfcMatrix (矩阵)
- GfcBox3d (包围盒), GfcIntervald (区间)

### GFC SDK

**仓库地址**: https://gitee.com/glodon/gfc

**技术规格**:
- 编程语言: C++ (87.8%), C (11.6%)
- 许可证: MIT License
- 最新发布分支: release/2312x3
- 开发分支: v3.0

**目录结构**:
```
bin/          # 可执行文件
build/        # 构建目录
doc/          # 文档
include/      # 头文件
lib/          # 库文件
src/          # 源代码
tests/        # 测试代码
thirdparty/   # 第三方依赖
tools/GenGFCCode/  # 代码生成工具
```

**构建方法**:
```bash
cmake -B ./build -S ./src
cmake --build ./Build
```

## IFC数据格式

### 概述

IFC4x3是buildingSMART国际组织维护的建筑信息模型标准，是国际通用的BIM数据交换标准。

### Schema结构

**统计数据**:
- 总Schema数: 30+
- 总实体数: 800+
- 总类型定义: 500+
- 总属性集: 700+
- 总数量集: 100+

### 核心Schema（Chapter 5）

**IfcKernel** - 核心实体层次
- 49个实体: IfcActor, IfcContext, IfcControl, IfcGroup, IfcObject, IfcProduct, IfcProject, IfcPropertySet等
- 属性集: Pset_ActorCommon, Pset_ProjectCommon

**IfcControlExtension** - 性能和审批关系
- 实体: IfcPerformanceHistory, IfcRelAssociatesApproval

**IfcProcessExtension** - 施工调度
- 11个实体: IfcEvent, IfcEventType, IfcProcedure, IfcTask, IfcWorkCalendar等

**IfcProductExtension** - 空间和产品结构
- 82个实体: IfcAlignment, IfcBridge, IfcBuilding, IfcBuildingStorey, IfcElement, IfcSpace, IfcSite等
- 34个属性集: Pset_BridgeCommon, Pset_BuildingCommon, Pset_SiteCommon等

### 共享元素Schema（Chapter 6）

**IfcSharedBldgElements** - 通用建筑元素
- 45个实体: IfcBeam, IfcDoor, IfcWall, IfcWindow, IfcRoof, IfcStair等
- 24个属性集, 16个数量集

**IfcSharedBldgServiceElements** - 建筑MEP系统
- 26个实体: IfcDistributionFlowElement, IfcFlowController, IfcFlowTerminal等
- 28个属性集

**IfcSharedFacilitiesElements** - 家具和资产
- 7个实体: IfcAsset, IfcFurniture, IfcInventory, IfcOccupant等

**IfcSharedInfrastructureElements** - 基础设施元素
- 18个实体: IfcBorehole, IfcCourse, IfcEarthworksCut, IfcPavement等

### 领域特定Schema（Chapter 7）

**IfcArchitectureDomain** - 门窗建筑细节
- 5个实体: IfcDoorLiningProperties, IfcDoorPanelProperties等

**IfcBuildingControlsDomain** - 建筑自动化
- 12个实体: IfcActuator, IfcAlarm, IfcController, IfcSensor, IfcFlowInstrument等
- 49个属性集

**IfcConstructionMgmtDomain** - 施工资源
- 14个实体: IfcConstructionEquipmentResource, IfcLaborResource等

**IfcElectricalDomain** - 电气系统
- 50个实体: IfcCableSegment, IfcDistributionBoard, IfcElectricGenerator等
- 80个属性集

**IfcHvacDomain** - 暖通空调
- 66个实体: IfcAirTerminal, IfcBoiler, IfcChiller, IfcCoolingTower等
- 113个属性集

**IfcPlumbingFireProtectionDomain** - 管道和消防
- 10个实体: IfcFireSuppressionTerminal, IfcSanitaryTerminal等

**IfcStructuralAnalysisDomain** - 结构分析
- 28个实体: IfcStructuralAnalysisModel, IfcStructuralLoadCase等

**IfcStructuralElementsDomain** - 结构元素
- 23个实体: IfcCaissonFoundation, IfcFooting, IfcPile, IfcReinforcingBar等

### 资源定义Schema（Chapter 8）

21个资源Schema，包括:
- IfcGeometryResource: 75个几何实体
- IfcGeometricModelResource: 48个几何模型实体
- IfcProfileResource: 28个截面定义
- IfcMaterialResource: 18个材质定义
- IfcPresentationAppearanceResource: 46个表现样式
- IfcTopologyResource: 20个拓扑定义

## BIM软件API参考

### Revit API

**二次开发平台**: Revit API基于.NET Framework
**主要命名空间**:
- Autodesk.Revit.DB - 核心数据库操作
- Autodesk.Revit.UI - 用户界面
- Autodesk.Revit.ApplicationServices - 应用程序服务

**常用操作**:
- 元素创建、修改、删除
- 参数读取和设置
- 几何提取
- 过滤器查询
- IFC导入导出

### 常用BIM软件API

| 软件 | API类型 | 说明 |
|------|---------|------|
| Revit | .NET API | 最广泛使用的BIM API |
| ArchiCAD | Ruby/GDL | Graphisoft产品 |
| Tekla Structures | API & Open API | 钢结构深化 |
| Navisworks | .NET API | 模型整合与碰撞检测 |
| Rhino/Grasshopper | Python/C# | 参数化设计 |

## 数据转换指南

### GFC到IFC映射原则

1. **构件映射**: 建立GFC构件类型与IFC实体类型的对应关系
2. **属性映射**: 将GFC属性系统转换为IFC属性集(Pset)和属性
3. **几何映射**: GFC几何元素转换为IFC几何表示
4. **关系映射**: GFC关系转换为IFC关系实体

### 转换工具

- GFC SDK提供数据读写接口
- Revit API支持IFC导入导出
- 第三方转换工具需验证数据完整性

## 使用场景

当用户询问以下问题时触发本技能:
- "GFC和IFC有什么区别"
- "如何将GFC转换为IFC"
- "IFC Schema结构是什么"
- "GFC SDK如何使用"
- "Revit如何读取GFC文件"
- "BIM数据格式转换"
- "GFC构件属性定义"
- "IFC实体类型列表"

## GFC构件分类编码

### 建筑专业构件分类

| 构件名称 | 构件代码 | 编码(GB/T 51269-2017) |
|---------|---------|---------------------|
| 基坑大开挖 | PitEarth | 15-31.30.01 |
| 幕墙 | CurtainWall | 14-10.20.21 |
| 建筑墙 | Wall | 14-10.20.03 |
| 建筑柱 | Column | 14-10.20.06 |
| 门 | Door | 14-10.20.09 |
| 窗 | Window | 14-10.20.12 |
| 屋顶 | Roof | 14-10.20.15 |
| 建筑楼板 | BuildingFloor | 14-10.20.18 |
| 建筑楼梯 | BuildingStairs | 14-10.20.27 |
| 建筑坡道 | BuildingRamp | 14-10.20.33 |
| 台阶 | FootStep | 14-10.20.36 |
| 栏杆扶手 | Balustrade | 14-10.20.42 |
| 雨篷 | Canopy | 14-10.20.48 |
| 阳台 | Balcony | 14-10.20.51 |
| 电梯 | Lifts | 14-10.20.30.03 |
| 幕墙嵌板 | Panels | 14-10.20.21.32 |
| 竖挺 | Upright | 14-10.20.21.34 |
| 横梁 | Crossbeam | 14-10.20.21.36 |
| 预埋件 | EmbeddedParts | 14-10.20.21.38 |
| 女儿墙 | Parapet | 14-10.20.15.16 |
| 平屋面 | FlatRoof | 14-10.20.15.03 |
| 坡屋面 | SlopingRoof | 14-10.20.15.06 |
| 天窗 | Skylight | 14-10.20.12.02 |
| 采光顶 | Sunroof | 14-10.20.15.20 |
| 散水 | Apron | 14-10.20.39 |
| 檐沟 | Gutter | 14-10.20.45.09 |
| 竖井 | Shaft | 12-17.21.00.01 |
| 房间 | Room | 12-02.01.00.01 |

### 结构专业构件分类

| 构件名称 | 构件代码 | 编码(GB/T 51269-2017) |
|---------|---------|---------------------|
| 框架梁 | Beam | 14-20.20.06 |
| 非框架梁 | NonFrameBeam | 14-20.20.06.01 |
| 连梁 | LinkBeam | 14-20.20.06.03 |
| 结构柱 | StructuralColumn | 14-20.20.09 |
| 结构墙 | StructuralWall | 14-10.20.03.04 |
| 现浇板 | Slab | 14-20.20.03 |
| 独立基础 | IsolatedFD | 14-20.10.03.03 |
| 条形基础 | StripFD | 14-20.10.03.06 |
| 筏板基础 | RaftFD | 14-20.10.03.09 |
| 桩 | Pile | 14-20.10.15 |
| 桩承台 | PileCap | 14-20.10.15.11 |
| 基础梁 | FDBeam | 14-20.10.06 |
| 钢柱 | SteelColumn | 14-20.30.03 |
| 钢梁 | SteelBeam | 14-20.30.06 |
| 钢支撑 | SteelSupport | 14-20.30.25 |
| 钢檩条 | SteelPurlins | 14-20.30.15 |
| 钢桁架 | SteelTruss | 14-20.30.09 |
| 钢网架 | SteelMeshFrame | 14-20.30.12 |
| 钢筋 | Rebar | 15-03.30.00 |
| 暗柱 | EmbeddedColumn | 14-20.20.09.04 |
| 构造柱 | TieColumn | 14-20.20.09.03 |
| 圈梁 | TieBeam | 14-20.20.06.05 |
| 过梁 | Lintel | 14-20.20.06.04 |
| 预制墙 | PrecastWall | 14-10.20.03.13 |
| 预制柱 | PrecastColumn | 14-20.20.09.05 |
| 预制梁 | PrecastBeam | 14-20.20.06.07 |
| 叠合板 | LaminatedSlab | 14-20.10.03.90 |
| 组合楼板 | CompositeSlab | 14-10.20.03.06 |
| 后浇带 | PostCastStrip | 14-20.20.21.04 |
| 板受力筋 | PlateMainr | 14-10.20.03.02 |
| 板负筋 | PlateNegativeReinforcement | 14-10.20.03.03 |
| 直行梯段 | Flight | 14-10.20.27.01 |
| 螺旋梯段 | SpiralFlight | 14-10.20.27.02 |
| 人防门框墙 | BarAirDefenseWall | 14-10.20.03.07 |
| 挡土墙 | BrickWall | 15-32.10.40.01 |

### 机电专业公共构件

| 构件名称 | 构件代码 | 编码 |
|---------|---------|------|
| 套管 | Casing | 14-40.20.12.01 |
| 孔洞 | Hole | 14-10.20.03.17 |
| 机电设备基础 | MEPEquipmentFoundation | 14-20.10.09.02 |
| 空间 | Space | 14-10.20.00.90 |
| 支架 | Bracket | 14-20.30.15.10 |
| 未定义构件 | UndefinedObject | 14-10.20.00.99 |

### 暖通专业构件

| 构件名称 | 构件代码 | 编码 |
|---------|---------|------|
| 冷水机组 | WaterChillingUnit | 15-24.45.20 |
| 冷却塔 | CoolingTower | 15-24.45.30 |
| 热泵机组 | HeatPumpUnit | 15-25.20.30 |
| 锅炉 | Boiler | 15-25.20.10 |
| 空气处理机组 | AirHandlingUnit | 15-24.45.40 |
| 风机盘管 | FanCoilUnit | 15-24.10.40 |
| 风机 | Fan | 15-24.05.00.01 |
| 散热器 | Radiator | 15-25.10.10 |
| 消声器 | Muffler | 15-24.15.10 |
| 风管 | Duct | 30-43.15.00 |
| 风管阀门 | DuctValve | 30-43.15.00.01 |
| 风管管件 | DuctFitting | 30-43.15.00.03 |
| 软风管 | FlexibleDuct | 30-43.15.00.05 |
| 末端风口 | EndTuyere | 15-24.05.00.03 |
| 挡烟垂壁 | SmokeBarrier | 15-22.00.00.91 |
| 分集水器 | DistributionManifold | 15-25.15.00.01 |

### 给水排水专业构件

| 构件名称 | 构件代码 | 编码 |
|---------|---------|------|
| 水泵 | Pump | 15-23.35.10 |
| 储水设备 | WaterStorageEquipment | 30-30.50.10 |
| 卫浴器具 | BathRoomAppliance | 15-12.20.20 |
| 喷头 | Sprinkler | 14-40.30.27.01 |
| 消火栓 | Hydrant | 30-30.60.00.01 |
| 气体灭火 | GasFireExtinguishing | 30-30.20.00 |
| 灭火器 | FireExtinguisher | 30-30.60.10 |
| 水管阀门 | PipeValve | 15-23.05.20.01 |
| 地漏 | FloorDrain | 15-23.10.40.01 |
| 雨水斗 | RainBucket | 15-23.15.40 |
| 管道 | Pipe | 15-23.05.10 |
| 管件 | PipeFitting | 15-23.05.10.01 |
| 软管 | FlexiblePipe | 15-23.05.10.02 |
| 消防炮 | FireMonitor | 30-30.60.00.02 |

### 电气专业构件

| 构件名称 | 构件代码 | 编码 |
|---------|---------|------|
| 灯具 | Lighting | 30-51.20.00 |
| 开关 | Switch | 30-51.40.10 |
| 插座 | Socket | 30-51.40.20.10 |
| 配电柜(箱) | DistributionBoard | 15-26.05.10.01 |
| 变配电设备 | PowerEquipment | 15-26.05.40 |
| 探测器 | Detector | 15-22.20.00.01 |
| 火灾报警按钮 | FireAlarmButton | 15-22.20.00.02 |
| 火灾警报器 | FireAlarmBell | 15-22.20.00.03 |
| 火灾控制器 | FireAlarmPanel | 15-22.20.00.04 |
| 电缆桥架 | CableTray | 30-53.20.10 |
| 线管 | Conduit | 30-53.20.30 |
| 导线 | Wire | 15-26.20.05.01 |
| 母线槽 | Busbar | 15-26.20.15.01 |
| 接闪器 | AirTerminal | 15-26.15.00.01 |
| 等电位端子箱 | EquipotentialBox | 15-26.15.00.02 |
| 综合布线 | StructuredCabling | 30-55.25.00 |
| 安防 | Security | 15-27.20.00.01 |
| 楼宇自控 | BAS | 15-27.15.00.01 |

### 施工管理构件

| 构件名称 | 构件代码 | 编码 |
|---------|---------|------|
| 外脚手架 | OuterScaffold | 15-01.20.50 |
| 钢管外脚手架立杆 | SteelTubularStandingTube | 15-01.20.50.01 |
| 钢管外脚手架水平杆 | SteelTubularHorizontalTube | 15-01.20.50.03 |
| 钢管外脚手架剪刀撑 | SteelTubularDiagonalBracing | 15-01.20.50.05 |
| 盘扣式脚手架立杆 | DiskLockStandingTube | 15-01.20.50.02 |
| 盘扣式脚手架水平杆 | DiskLockHorizontalTube | 15-01.20.50.04 |
| 盘扣式脚手架斜杆 | DiskLockDiagonalBracing | 15-01.20.50.06 |
| 内脚手架 | InnerScaffold | 15-01.20.50.10 |
| 满堂脚手架 | FullHallScaffold | 15-01.20.50.20 |
| 附着式升降脚手架 | AttachedLiftScaffold | 15-01.20.50.30 |
| 吊篮 | HangingBasket | 15-01.20.50.40 |
| 基坑支护 | PitSupport | 15-01.10.10 |
| 土钉墙 | SoilNailingWall | 15-01.10.10.01 |
| 钢板桩 | SteelSheetPile | 15-01.10.10.02 |
| 灌注桩 | BoredPile | 15-01.10.10.03 |
| 锚杆 | AnchorRod | 15-01.10.10.04 |
| 地下连续墙 | DiaphragmWall | 15-01.10.10.05 |
| 模板 | Formwork | 15-01.20.10 |
| 木模板 | WoodFormwork | 15-01.20.10.01 |
| 钢模板 | SteelFormwork | 15-01.20.10.02 |
| 铝合金模板 | AluminumFormwork | 15-01.20.10.03 |
| 模板支撑 | FormworkSupport | 15-01.20.10.10 |
| 塔吊 | TowerCrane | 15-01.25.10 |
| 施工电梯 | ConstructionElevator | 15-01.25.20 |
| 卸料平台 | UnloadingPlatform | 15-01.25.30 |

## GFC关键枚举值

### 结构专业枚举

| 枚举ID | 枚举名称 | 枚举值 |
|-------|---------|-------|
| D.400 | 导荷方式 | 未设置、单向板、梯形三角形 |
| D.401 | 工况类型 | 恒载、活载、风载、水平地震、竖向地震、人防、吊车、温度、土、水 |
| D.408 | 梁属性 | 普通梁、托墙转换梁、托柱转换梁、门式刚梁、消能梁、组合梁、吊车梁 |
| D.409 | 梁建模类别 | 普通梁、按次梁输入的次梁、空心板肋梁、地基梁 |
| D.410 | 支座约束类型 | 刚接、铰接、滑动、半刚接 |
| D.411 | 支座类型 | 无支座、梁支座、柱支座、边框柱支座、框支柱支座、支撑支座、斜柱支座 |
| D.413 | 构件重要性类别 | 关键构件、普通竖向构件、重要水平构件、普通水平构件、耗能构件 |
| D.414 | 桁架杆件标志 | 桁架上弦杆、桁架腹杆、桁架中层弦杆、桁架下弦杆、支座腹杆 |
| D.415 | 宽厚比等级 | S1、S2、S3、S4、BS1、BS2、BS3、S5 |
| D.416 | 延性等级 | 延性等级I~V |
| D.429 | 墙属性 | 普通墙、短肢剪力墙、防屈曲钢板墙 |
| D.433 | 钢材等级 | Q235~Q690、Q235GJ~Q460GJ、Q355~Q460M |
| D.434 | 钢筋级别 | HPB235~HRB500、HRB335E~HRBF500E、RRB400等 |
| D.437 | 关系类型 | 焊接关系、螺栓关系、构件组关系、节点关系、布尔关系 |
| D.439 | 螺栓类型 | 螺栓、锚栓、栓钉、只打孔 |
| D.445 | 布尔类型 | 线切割、面切割、实体减、实体并、实体交 |

### 机电专业枚举

| 枚举ID | 枚举名称 | 枚举值 |
|-------|---------|-------|
| D.185 | 风管类别 | 矩形风管、圆形风管 |
| D.186 | 末端风口类型 | 散流器、单层百叶、双层百叶、格栅风口、旋流风口、条缝风口、喷口 |
| D.187 | 风口箭头方向 | 无、送风、回风 |
| D.189 | 空气处理机组类型 | 组合式空调箱、新风机组、热交换机、恒温恒湿机组 |
| D.194 | 风机类型 | 离心风机、轴流风机、斜流风机、管道风机、屋顶风机、诱导风机 |
| D.197 | 风管阀门类型 | 70°C防火阀、150°C防火阀、280°C防火阀、排烟阀、电动防火阀 |
| D.200 | 冷水机组类型 | 离心式、螺杆式、活塞式 |
| D.201 | 冷却塔类型 | 方形横流、方形逆流、圆形横流、圆形逆流 |
| D.205 | 光源类别 | 荧光灯、LED灯、金属卤化物灯、钠灯、白炽灯、汞灯、HID灯 |
| D.206 | 明/暗装 | 明装、暗装 |
| D.208 | 配电箱类型 | 照明配电箱、动力配电箱、应急照明配电箱、双电源切换箱、控制箱 |

### 给排水专业枚举

| 枚举ID | 枚举名称 | 枚举值 |
|-------|---------|-------|
| D.160 | 排水处理设备类型 | 预处理设备、深度处理设备、消毒设备、油水分离器、污水处理设备 |
| D.162 | 卫浴器具类型 | 坐便器、小便器、蹲便器、浴盆、拖布池、淋浴器、洗手盆、洗涤盆 |
| D.163 | 存水弯 | 无、P型存水弯、S型存水弯 |
| D.166 | 喷头类型 | 下垂式喷头、直立式喷头、开式喷头、闭式喷头、水幕喷头、干式喷头 |
| D.168 | 消火栓类型 | 组合式消火栓箱、普通消火栓箱、消防软管卷盘箱、室外消火栓 |
| D.175 | 水管阀门类型 | 闸阀、蝶阀、球阀、止回阀、二通阀、电磁阀、平衡阀、截止阀等40+种 |
| D.177 | 连接方式 | 螺纹连接、承插连接、粘（熔）连接、法兰连接、焊接连接 |
| D.178 | 地漏类型 | 水封地漏、直通式地漏、地面清扫口 |
| D.179 | 雨水斗类型 | 重力流雨水斗、半有压雨水斗、虹吸雨水斗 |

## 参考资源

- GFC官网: https://gfc.glodon.com/GFC2/
- GFC构件规范: https://gfc.glodon.com/gfc/
- GFC SDK: https://gitee.com/glodon/gfc
- IFC文档: https://ifc43-docs.standards.buildingsmart.org/
- GB/T 51269-2017: 建筑信息模型分类和编码标准
