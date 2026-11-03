---
module: 11
title: Cesium for Unreal v2.28.0 — UE 集成 3D Tiles / 全球地理
cesium_version: N/A (独立 SDK,基线 v2.28.0 · ⚠️ 用户原话 "v.29" 已纠正)
last_verified: 2026-09-22
source_url: [https://cesium.com/learn/cesium-unreal/ref-doc, https://github.com/CesiumGS/cesium-unreal]
status: stable
---

# 11 · Cesium for Unreal v2.28.0

> **本模块覆盖**:Cesium for Unreal 插件的安装、核心组件、Blueprint / C++ 用法、Unreal Engine 版本兼容。
> **何时加载**:Unreal Engine 项目需要 3D Tiles / 全球地理 / Cesium ion / 高保真 GIS 渲染。
> **基线版本**:**v2.28.0**(2026-07-01,Cesium for Unreal 最新)。
> ⚠️ **版本号说明**:Cesium for Unreal 走 **v2.x** 编号,**不存在 v0.29**(那是 Cesium for Omniverse)。本基线 v2.28.0 与 Cesium for Unity v1.24.0 同月发布,共享 cesium-native v0.62.0。

---

## 11.1 什么是 Cesium for Unreal?

Cesium for Unreal 是 CesiumGS 官方的 Unreal Engine 插件,把 **3D 地理空间能力** 带入 Unreal Engine:

- ✅ 高精度全比例 WGS84 全球地球
- ✅ 3D Tiles(倾斜摄影 / 建筑 / BIM / 点云)
- ✅ Cesium ion 资源集成(全球地形 / 影像 / OSM Buildings / Google Photorealistic 3D Tiles)
- ✅ **Unreal Engine 物理 / 碰撞 / 角色交互** 完整集成
- ✅ Nanite / Lumen 配合(高保真渲染)
- ✅ Metahumans / 灯光 / 大气散射(影视级真实感)

**典型场景**:建筑可视化(AEC)、游戏化 GIS、仿真训练、智慧城市、影视预可视化、无人机巡检仿真、虚拟制片。

**License**:Apache 2.0(免费商用)。

---

## 11.2 Unreal Engine 版本兼容矩阵

> **Cesium for Unreal 标准策略**:支持 **最近 3 个 Unreal Engine 主版本**。

| Cesium for Unreal | 支持的 UE 版本 | 关键变更 |
|---|---|---|
| **v2.28.0**(基线) | UE 5.5 / 5.6 / 5.7 / 5.8 | **最后一个支持 UE 5.5 的版本**;新增 UE 5.8 支持;cesium-native v0.62.0 |
| v2.27.x | UE 5.5+ | — |
| v2.0.0 ~ v2.26.x | UE 5.1+ | 引入 3D Tiles 1.1 / EXT_mesh_features |
| v1.31.2 | UE 5.0(末班) | 最后一个支持 UE 5.0 |
| UE 4.x | 历史分支 | [ue4-main](https://github.com/CesiumGS/cesium-unreal/tree/ue4-main) |

> ⚠️ **如果项目用 UE 5.5** → **必须**锁 Cesium for Unreal v2.28.0(之后版本不再支持 5.5)。
> ⚠️ **如果用 UE 5.6+** → 可以升级到最新版本。

---

## 11.3 安装

### 方式 A:Unreal Engine Marketplace(推荐)

1. Epic Games Launcher → Unreal Engine → Marketplace
2. 搜索 "Cesium for Unreal"
3. 安装到引擎(`Install to Engine`)或单独项目(`Install to Project`)

### 方式 B:GitHub Release(适合 Linux / 老版本)

```bash
# Linux 用户注意:Marketplace 在 Linux 上不可用,用 GitHub Release
wget https://github.com/CesiumGS/cesium-unreal/releases/download/v2.28.0/CesiumForUnreal-v2.28.0.zip

# 解压到 UE 插件目录
unzip CesiumForUnreal-v2.28.0.zip \
  -d /opt/UnrealEngine/Engine/Plugins/Marketplace/
```

### 启用插件

1. 编辑 `.uproject` 文件 → 添加 plugin:
   ```json
   "Plugins": [
     { "Name": "CesiumForUnreal", "Enabled": true }
   ]
   ```
2. 重新生成 Visual Studio / Xcode 工程文件
3. 编译

### Cesium ion Token 设置

`Edit > Project Settings > Plugins > Cesium for Unreal` → 填入 Cesium ion access token。

---

## 11.4 核心组件 / Actor

### 11.4.1 `ACesiumGeoreference`(地理参考)

> **命名约定**:Actor 前缀 `A`,Component 前缀 `U`

```cpp
// C++ 创建
ACesiumGeoreference* GeoRef = World->SpawnActor<ACesiumGeoreference>();
GeoRef->SetOriginLongitudeLatitudeHeight(
    FVector(116.4, 39.9, 0)  // 北京
);
```

```cpp
// 关键 API
FVector GetOriginLongitudeLatitudeHeight() const;
void SetOriginLongitudeLatitudeHeight(const FVector& LLA);
FMatrix ComputeEastSouthUpToUnrealTransformation(const FVector& OriginLLA) const;  // v2.0+
bool IsValid() const;
```

**Blueprint 用法**:
- 拖 `CesiumGeoreference` Actor 到场景
- Detail 面板 → Origin Longitude / Latitude / Height

### 11.4.2 `ACesium3DTileset`(3D Tiles Actor)

```cpp
// C++ 加载
ACesium3DTileset* Tileset = World->SpawnActor<ACesium3DTileset>();
Tileset->SetUrl("https://your-server/tiles/tileset.json");

// 从 Cesium ion Asset 加载
Tileset->SetIonAssetID(9617);
```

```cpp
// 关键属性(通过 UCesium3DTileset 暴露)
UPROPERTY(EditAnywhere, Category = "Cesium")
FString Url;

UPROPERTY(EditAnywhere, Category = "Cesium")
int32 MaximumScreenSpaceError = 2;  // LOD 阈值

UPROPERTY(EditAnywhere, Category = "Cesium")
int32 MaximumMemoryUsageMB = 256;

UPROPERTY(EditAnywhere, Category = "Cesium")
bool bEnableCollision = false;

UPROPERTY(EditAnywhere, Category = "Cesium")
bool bCullWithChildrenBounds = true;
```

**Blueprint 节点**:
- `Get Url` / `Set Url`
- `Get Tile Loaded Count` / `Get Tile Loading Count`
- `Get Current Level Of Detail`
- `Get Available Levels`

### 11.4.3 `UCesiumGlobeAnchorComponent`(物体锚定)

```cpp
// 在 Actor 上添加
UCesiumGlobeAnchorComponent* Anchor = NewObject<UCesiumGlobeAnchorComponent>(MyActor);
Anchor->RegisterComponent();
Anchor->SetLongitudeLatitudeHeight(FVector(116.4, 39.9, 50));

// 移动 Actor → 自动同步 LLA
MyActor->SetActorLocation(NewLocation);  // Anchor 内自动更新
```

```cpp
// 关键属性
UPROPERTY(EditAnywhere, Category = "Cesium")
FVector LongitudeLatitudeHeight;  // 当前经纬高

UPROPERTY(EditAnywhere, Category = "Cesium")
bool bAdjustOrientationForGlobeWhenMoving = true;
```

### 11.4.4 `ACesiumSunSky`(动态太阳 / 大气)

```cpp
// 加载 HDR 太阳 + 大气散射
ACesiumSunSky* SunSky = World->SpawnActor<ACesiumSunSky>();
SunSky->SetUseTimeOfDayEnabled(true);
SunSky->SetTimeOfDay(12.0);  // 中午
```

> 💡 用于建筑可视化的真实光照 / 阴影分析。

### 11.4.5 `UCesiumCameraController`(相机控制)

挂在 `APlayerCameraManager` 或 `APawn` 上,实现地球感知相机控制。

### 11.4.6 `UCesiumMetadataPickingBlueprintLibrary`(拾取 / 元数据)

> **重点 API**:从 3D Tiles feature 拾取元数据

```cpp
// C++ 通过 BlueprintLibrary
FCesiumMetadataValue GetMetadataValueForHit(
    const FHitResult& Hit,
    const FString& PropertyName
);
```

```cpp
// Blueprint:击中的 Feature 上有 height 属性,获取
Get Metadata Values For Hit → 拿到 Property Table / Texture → 读 property
```

### 11.4.7 Raster Overlay 组件

| 类名 | 数据源 |
|---|---|
| `UCesiumIonRasterOverlay` | Cesium ion 资源 |
| `UBingMapsRasterOverlay` | Bing Maps |
| `UGoogleMapsRasterOverlay` | Google Maps |
| `UCesiumWebMapServiceRasterOverlay` | OGC WMS |
| `UCesiumWebMapTileServiceRasterOverlay` | OGC WMTS |
| `UUrlTemplateRasterOverlay` | 自定义 XYZ 瓦片 |

```cpp
// 示例:加载 Bing Maps Aerial
auto Overlay = NewObject<UBingMapsRasterOverlay>(Tileset);
Overlay->SetMapStyle(EBingMapsStyle::AERIAL);
Overlay->RegisterComponent();
```

### 11.4.8 Sub Level(子关卡)

用于把大型 3D Tiles 分到多个关卡:

```cpp
// CesiumSubLevelComponent 允许把 Cesium3DTileset 放进 Level Instance
// 这是 v2.0 引入的,替换了旧的 World Composition 系统
```

---

## 11.5 Blueprint vs C++

### Blueprint 节点位置

```
右键搜索 "Cesium" →
  ├─ Cesium Georeference → Get Origin Longitude Latitude Height
  ├─ Cesium 3D Tileset → Set Url / Get Loaded Tile Count
  ├─ Cesium Globe Anchor → Set Longitude Latitude Height
  ├─ Cesium Metadata Picking → Get Metadata Values For Hit
  └─ Cesium Web Map Service → ...
```

### C++ 集成示例

```cpp
// MyActor.h
#include "CesiumGlobeAnchorComponent.h"
#include "Cesium3DTileset.h"

UCLASS()
class MYGAME_API ACesiumObject : public AActor {
    GENERATED_BODY()
public:
    ACesiumObject();

    UPROPERTY(VisibleAnywhere)
    UCesiumGlobeAnchorComponent* GlobeAnchor;

    UPROPERTY(VisibleAnywhere)
    UStaticMeshComponent* MeshComponent;

protected:
    virtual void BeginPlay() override;
};

// MyActor.cpp
ACesiumObject::ACesiumObject() {
    PrimaryActorTick.bCanEverTick = false;

    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    GlobeAnchor = CreateDefaultSubobject<UCesiumGlobeAnchorComponent>(TEXT("GlobeAnchor"));
    GlobeAnchor->SetupAttachment(RootComponent);
}

void ACesiumObject::BeginPlay() {
    Super::BeginPlay();

    // 锚定到北京
    GlobeAnchor->SetLongitudeLatitudeHeight(FVector(116.4, 39.9, 50));
}
```

---

## 11.6 v2.28.0 关键变更

> **最后支持 UE 5.5 的版本**;未来版本要求 UE 5.6+

| 类型 | 变更 |
|---|---|
| ➕ **Additions** | Added support for Unreal Engine 5.8 |
| 🔧 **Fixes** | Fixed a crash that could occur when zooming to a tileset with Update in Editor disabled |
| 🔧 **Fixes** | Fixed Gaussian splats not rendering in Standalone Game sessions launched from the editor |
| 🔄 **cesium-native** | v0.61.0 → v0.62.0 |

> 📦 **早期 v2.0 Breaking Changes**(影响从老版本迁移):
> - Feature IDs 和元数据改用 **EXT_mesh_features** + **EXT_structural_metadata**(弃用 EXT_feature_metadata)
> - 旧的 sub-level 系统删除,改用 Level Instance + Cesium Sub Level Component
> - 移除 `Mobility` 属性(用 root component 的 mobility)

---

## 11.7 数据源 / Raster Overlay 典型组合

```
CesiumGeoreference (北京原点)
  └─ Cesium3DTileset (3D 城市模型)
       ├─ BingMapsAerial (影像底图)
       ├─ CesiumIonRasterOverlay (Google Photorealistic 3D Tiles)
       └─ UrlTemplateRasterOverlay (自定义 XYZ)
  └─ Cesium3DTileset (倾斜摄影 OSGB → 3D Tiles)
  └─ Cesium3DTileset (BIM Revit → glTF → 3D Tiles)
  └─ CesiumSunSky (动态光照)
  └─ PlayerPawn (CesiumCameraController)
```

---

## 11.8 Blueprint 实战案例

### 案例 1:鼠标点击 3D Tiles feature 读取属性

```
Event ActorBeginOverlap → [无效场景]
Event InputAction "Left Click" 
  ↓
LineTraceByChannel (Visibility, Distance 100000)
  ↓
Get Metadata Values For Hit (Hit, "PropertyName")
  ↓
Print String
```

### 案例 2:玩家走到某区域触发 LOD 切换

```
Tick → Get Player Pawn Location → Convert to LLA (Cesium Globe Anchor)
  ↓
If LLA within [LngA, LatA, LngB, LatB]:
    Cesium3DTileset.Set Url (Detail URL)
```

### 案例 3:实时光照(随真实时间)

```
CesiumSunSky.Set Time Of Day (CurrentTime.GetTotalHours())
  ↓
自动更新太阳角度 + 大气
```

---

## 11.9 与 Cesium for Unity 对比

| 维度 | Cesium for Unity v1.24.0 | Cesium for Unreal v2.28.0 |
|---|---|---|
| **底层引擎** | Unity (URP / 内置) | Unreal Engine 5.5+ |
| **共享 cesium-native** | v0.62.0 | v0.62.0 |
| **视觉保真度** | 中等 | 高(Nanite / Lumen) |
| **学习曲线** | 平(组件式) | 中(Blueprint + C++) |
| **3D Tiles 性能** | 高 | 高 |
| **物理引擎** | Unity Physics | Unreal Physics (Chaos) |
| **角色交互** | 标准做法 | 更高级(UMG + Pawn) |
| **部署目标** | PC / 移动 / Web | PC / 主机(PS5/Xbox) |
| **典型场景** | 移动端数字孪生 | 主机游戏化 GIS |

**何时选 Unity**:
- 移动端 / Web 优先
- 已有 Unity 团队
- 实时性 > 视觉保真

**何时选 Unreal**:
- 高保真渲染优先(影视 / 主机游戏)
- Lumen / Nanite 需求
- 已有 UE 团队
- 仿真训练 / 建筑可视化

---

## 11.10 性能调优

### 显存

```cpp
// ACesium3DTileset
MaximumMemoryUsageMB = 512;  // 大规模场景调高

// Sub Level 把大型 3D Tiles 拆分,按需加载
```

### CPU

```cpp
// 关闭不必要的功能
bEnableCollision = false;             // 物理碰撞(大场景关闭)
bPreloadAncestors = false;
bPreloadSiblings = false;

// 启用 LOD 优化
MaximumScreenSpaceError = 8;  // 调大省 CPU
```

### 视觉

```cpp
// Nanite 配合(UE 5+)
MeshComponent->SetMobility(EComponentMobility::Movable);
Project Settings → Rendering → Nanite = enabled

// Lumen 配合
Project Settings → Rendering → Global Illumination = Lumen
```

---

## 11.11 已知坑

| 现象 | 原因 | 解决 |
|---|---|---|
| Tileset 加载崩 | URL 错误或 CORS | Nginx 加 CORS 头 |
| UE 5.4 启动报错 | Cesium for Unreal 不支持 UE 5.4 | 升级到 UE 5.5+ 或用老版 Cesium |
| Gaussian splats 不显示 | v2.28.0 已修复,确保升级到 v2.28.0+ | |
| 物体浮在空中 | GlobeAnchor LLA 设置错 | 检查 height 字段 |
| 编辑器缩放崩溃 | 老版本 bug,v2.28.0 已修复 | 升级 |
| Linux 安装失败 | Marketplace 不支持 Linux | 用 GitHub Release ZIP |

---

## 11.12 已知关键功能

| 功能 | 版本 | 备注 |
|---|---|---|
| 3D Tiles 1.1 + EXT_mesh_features | v2.0.0+ | OGC 标准支持 |
| EXT_structural_metadata | v2.0.0+ | 元数据查询 |
| Google Photorealistic 3D Tiles | v1.31.2+ | Quick Add |
| Cesium Sun Sky 动态大气 | v1.0+ | 物理大气散射 |
| Sub Level(Level Instance) | v2.0.0+ | 替换旧 World Composition |
| 16 KB ELF segment | v1.23.3+ | Android 15+ 兼容 |
| Web builds | Unity 仅 v1.20.0+ 实验,Unreal 暂无 | 等待后续 |

---

## 11.13 与 Cesium ion 配合

```cpp
// C++ 加载 Cesium ion Asset
UCesiumIonRasterOverlay* Overlay = NewObject<UCesiumIonRasterOverlay>(Tileset);
Overlay->SetIonAssetID(3830183);  // Google 2D Satellite
Overlay->RegisterComponent();

// Cesium ion 自托管
Overlay->SetIonServerURL("https://your-ion-server.com/");
Overlay->SetIonAccessToken("YOUR_TOKEN");
```

**Token 管理**:
- 同 CesiumJS,推荐后端代理 + 动态注入(详见 `recipes/ion-token-rotation.md`)
- Cesium for Unreal 通过 `UCesiumRuntimeSettings` 持久化 token

---

## 11.14 与 Cesium for Omniverse 对比

| 项 | Cesium for Unreal v2.28.0 | Cesium for Omniverse v0.29.0 |
|---|---|---|
| 目标平台 | UE5(游戏 / 仿真) | NVIDIA Omniverse(协作 / 数字孪生) |
| 工作流 | Blueprint / C++ | USD / Kit |
| 实时协作 | 弱 | 强(Omniverse 核心能力) |
| 渲染 | Lumen / Nanite | RTX |
| 适用 | 主机游戏 / 仿真训练 | 工业数字孪生 / 多人协作 |

---

## 11.15 进一步阅读

- [Cesium for Unreal Quickstart](https://cesium.com/learn/cesium-unreal)
- [Cesium for Unreal Change Log](https://cesium.com/learn/cesium-unreal/ref-doc)
- [Cesium for Unreal Tutorials](https://cesium.com/learn/cesium-unreal)
- [GitHub: CesiumGS/cesium-unreal](https://github.com/CesiumGS/cesium-unreal)
- [Epic Marketplace: Cesium for Unreal](https://www.unrealengine.com/marketplace/cesium-for-unreal)
- [cesium-native 仓库](https://github.com/CesiumGS/cesium-native)
- [Cesium for Unity 章节](./10-cesium-for-unity.md)

---

## 下一步

- CesiumJS Web 端 → `modules/01-foundation.md`
- CesiumJS 数据接入 → `modules/02-data-sources.md`
- 国产封装对比 → `modules/08-domestic-alternatives.md`