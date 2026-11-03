# ZOS-API 接口参考

## 概述

ZOS-API 是 ZEMAX OpticStudio 提供的编程接口，允许外部程序与 OpticStudio 进行交互。支持 Python、C#、MATLAB 等编程环境。

## 编程选项卡功能

OpticStudio 编程选项卡提供以下功能组：

### ZPL 宏组

| 功能 | 说明 |
|------|------|
| 宏列表 | 显示所有 ZPL 宏文件 |
| 编辑/执行 | 编辑或运行选中的宏 |
| 新建宏 | 创建新的 ZPL 宏 |
| 宏帮助 | ZPL 语言帮助文档 |

### ZOS-API.NET 应用程序组

| 功能 | 说明 |
|------|------|
| 自定义分析 | User Analyses |
| 自定义扩展 | User Extensions |
| 接口文档 | ZOS-API.NET 完整接口文档 |

### 应用程序编译器

| 编译器 | 说明 |
|--------|------|
| C# | C# 项目编译器 |
| MATLAB | MATLAB 连接编译器 |
| Python | Python.NET 连接编译器 |

## 连接模式

### 独立应用程序模式 (Standalone Application)

```csharp
// C# 示例
using ZOSAPI;
using ZOSAPI.Editors;
using ZOSAPI.Analysis;
using ZOSAPI.Objects;

public class ZOSConnection
{
    public static void Main()
    {
        // 连接到 ZEMAX
        IZOSAPI_Application zos = ZOSAPI.ZOSAPI_Application.CreateApplication();

        if (zos == null)
        {
            Console.WriteLine("无法连接到 OpticStudio");
            return;
        }

        // 获取主系统
        IOpticalSystem TheSystem = zos.PrimarySystem;

        // ... 执行操作 ...

        // 关闭连接
        zos.CloseApplication();
    }
}
```

### Python 示例

```python
import clr
clr.AddReference("ZOSAPI")

from ZOSAPI import ZOSAPI

# 连接 OpticStudio
app = ZOSAPI.ZOSAPI_Application.CreateApplication()

if app is None:
    print("无法连接到 OpticStudio")
else:
    # 获取主系统
    TheSystem = app.PrimarySystem
    print(f"系统焦距: {TheSystem.LDE.GetSurfaceAt(1).EffectiveFocalLength}")

    # 关闭连接
    app.CloseApplication()
```

## 核心接口

### IZOSAPI_Application

应用程序主接口。

```csharp
// 主要属性
IZOSAPI_Application.ApplicationDirectory  // OpticStudio 安装目录
IZOSAPI_Application.ApplicationVersion   // 版本信息
IZOSAPI_Application.PrimarySystem         // 主光学系统
IZOSAPI_Application.SystemDirectory       // 当前工作目录

// 主要方法
void CloseApplication()                   // 关闭连接
IZOSAPI_Networking INetworking           // 网络功能
```

### IOpticalSystem

光学系统核心接口。

```csharp
IOpticalSystem TheSystem;

// 主要属性
ILensDataEditor LDE                       // 镜头数据编辑器
INonSeqEditor NSCE                        // 非序列元件编辑器
IEditor MFE                               // 评价函数编辑器
IEditor TDE                               // 公差数据编辑器
IEditor MCE                               // 多重结构编辑器
ISystemData SystemData                    // 系统数据
IAnalyses Analyses                        // 分析功能
IOptics/optics                           // 光学工具

// 主要方法
void LoadFile(string filePath, bool useCurrentDirectory)  // 打开文件
void Save()                                              // 保存
void SaveAs(string filePath)                             // 另存为
IOpticalSystem Mirror()                                   // 创建镜像
```

### ISystemData

系统参数配置。

```csharp
ISystemData sysData = TheSystem.SystemData;

// 系统孔径
sysData.Aperture.EPDZ;                    // 入瞳直径
sysData.Aperture.SystemAperture;           // 系统孔径类型
sysData.Aperture.ApertureValue;            // 孔径值

// 视场
IFields fields = sysData.Fields;
fields.NumberOfFields;                     // 视场数量
fields.FieldType;                          // 视场类型
IFieldPoint field = fields.GetFieldAt(i);  // 获取视场点

// 波长
IWavelengths wavelengths = sysData.Wavelengths;
wavelengths.NumberOfWavelengths;           // 波长数量
IWavelength wavelength = wavelengths.GetWavelengthAt(i);

// 环境
sysData.Environment.Temperature;            // 温度
sysData.Environment.Pressure;              // 压力
```

## 编辑器接口

### ILensDataEditor (镜头数据编辑器)

```csharp
ILensDataEditor lde = TheSystem.LDE;

// 添加/删除表面
int surf1 = lde.AddSurface();
int surf2 = lde.AddSurface();
void RemoveSurfaceAt(int surfaceNumber);

// 获取表面
ILDERow SurfaceRow = lde.GetSurfaceAt(int surfaceNumber);

// 表面属性
SurfaceRow.Radius;                         // 曲率半径
SurfaceRow.Thickness;                      // 厚度
SurfaceRow.SemiDiameter;                   // 半口径
SurfaceRow.Material;                       // 材料
SurfaceRow.Comment;                       // 注释

// 求解类型
SurfaceRow.SolveState;                     // 求解状态
SurfaceRow.SolveType;                      // 求解类型

// 变量设置
void SetVariableAt(int surfaceNumber, bool isVariable);
```

### IEditor (通用编辑器接口)

```csharp
IEditor editor = TheSystem.MFE;  // 或 TDE, MCE

int NumberOfSurfaces;            // 编辑器中的行数
IEditorColumnCollection Columns; // 列集合

// 获取单元格
IEditorCell cell = editor.GetCell(rowIndex, columnIndex);

// 设置值
cell.SetValue(double value);
cell.SetValue(string value);

// 获取值
double value = cell.DoubleValue;
string value = cell.StringValue;

// 变量状态
bool isVariable = cell.IsItemActive;
```

## 分析接口

### IAnalyses

```csharp
IAnalyses analyses = TheSystem.Analyses;

// 创建分析
IMtf mtf = analyses.New_Mtf();
ISpotDiagram spot = analyses.New_SpotDiagram();
IRayFan rayFan = analyses.New_RayFan();
IOpd opd = analyses.New_Opd();

// 分析设置
mtf.Settings.SampleSize;           // 采样大小
mtf.Settings.SpatialFrequency;     // 空间频率
mtf.Settings.Field;                // 视场

// 执行分析
mtf.Apply();

// 获取结果
IMtfResults mtfResults = mtf.GetResults();
double[] frequencies = mtfResults.GetAllFrequencies();
double[] tvMtf = mtfResults.GetAllTvMtf();
double[] sagMtf = mtfResults.GetAllSagMtf();
```

### 常用分析方法

| 分析 | 创建方法 | 主要设置 |
|------|----------|----------|
| MTF | New_Mtf() | SampleSize, SpatialFrequency, Field |
| 点列图 | New_SpotDiagram() | Field, Wavelength, DisplayType |
| Ray Fan | New_RayFan() | Field, Wavelength, Coordinate |
| OPD | New_Opd() | Field, Wavelength |
| 赛德尔 | New_Seidel() | - |

## 优化接口

### IOpticalSystem.Optics

```csharp
IOptics optics = TheSystem.Optics;

// 评价函数编辑器
IMeritFunctionEditor mfe = optics.MeritFunctionEditor;

// 创建优化
IOptimization optimization = mfe.CreateOptimization();
optimization.Algorithm = OptimizationAlgorithms.DampedLeastSquares;

// 添加默认评价函数
optimization.AddDefaultMeritFunction();

// 执行优化
optimization.Run();

// 全局优化
IOptimizer hammer = optics.Optimizers.HammerOptimizer;
hammer.Run();

// 局部优化
IOptimizer dls = optics.Optimizers.DampedLeastSquares;
dls.Run();

// 优化参数
optimization.CurrentMeritFunction;     // 当前评价函数值
optimization.NumberOfCycles;           // 迭代次数
```

## 公差分析接口

```csharp
// 公差工具
IOpticalSystemTools tools = TheSystem.Tools;

// 公差分析
ITolerancing tolerancing = tools.Tolerancing;

// 设置分析参数
tolerancing.SensitivityOrInverse = SensitivityOrInverseType.Sensitivity;
tolerancing.CompensationType = CompensationTypes.BackFocalLength;
tolerancing.AlgoType = TolerancingAlgorithm.MonteCarlo;
tolerancing.NumberOfTrials = 500;       // 蒙特卡洛次数

// 执行分析
tolerancing.Run();

// 获取结果
ITolerancingResults results = tolerancing.GetResults();
double meanValue = results.GetMeanAt(i);
double stdValue = results.GetStdAt(i);
double minValue = results.GetMinimumAt(i);
double maxValue = results.GetMaximumAt(i);
```

## 文件操作

```csharp
// 打开文件
TheSystem.LoadFile(@"C:\Designs\Lens.zmx", false);

// 保存文件
TheSystem.Save();                                          // 保存当前
TheSystem.SaveAs(@"C:\Designs\Lens_Modified.zmx");        // 另存为

// 创建存档
IZOSAPI_Archive archive = TheSystem.CreateArchive();
archive.Save(@"C:\Designs\Lens.zar");

// 加载存档
TheSystem.LoadArchive(@"C:\Designs\Lens.zar");
```

## 错误处理

```csharp
try
{
    // 打开文件
    TheSystem.LoadFile(filePath, false);

    // 执行操作
    var mtf = TheSystem.Analyses.New_Mtf();
    mtf.Apply();
}
catch (ZOSAPIException ex)
{
    Console.WriteLine($"ZOS-API 错误: {ex.Message}");
    Console.WriteLine($"错误代码: {ex.ErrorCode}");
}
catch (Exception ex)
{
    Console.WriteLine($"通用错误: {ex.Message}");
}
```

## 最佳实践

1. **连接管理**
   - 使用完成后始终调用 `CloseApplication()`
   - 考虑使用 `using` 语句确保资源释放

2. **文件备份**
   - 修改前保存原始文件
   - 使用 `SaveAs` 创建备份

3. **性能优化**
   - 批量操作时减少 UI 更新
   - 使用 `TheSystem.UpdateWindow = false`

4. **批处理**
   - 循环处理前断开 UI 连接
   - 使用进度回调报告状态

5. **数据验证**
   - 检查返回值和错误状态
   - 验证编辑后的参数有效性

## Python 完整示例

```python
import clr
clr.AddReference("ZOSAPI")

from ZOSAPI import ZOSAPI

def main():
    # 连接 OpticStudio
    app = ZOSAPI.ZOSAPI_Application.CreateApplication()

    if app is None:
        print("错误: 无法连接到 OpticStudio")
        return

    print(f"OpticStudio 版本: {app.ApplicationVersion}")

    # 获取主系统
    system = app.PrimarySystem

    # 打开示例文件
    system.LoadFile("C:\\Zemax\\Samples\\Sequential\\Objectives\\Cooke 40 degree field.zmx", False)

    # 获取系统参数
    print(f"入瞳直径: {system.SystemData.Aperture.EPDZ} mm")
    print(f"视场数量: {system.SystemData.Fields.NumberOfFields}")
    print(f"波长数量: {system.SystemData.Wavelengths.NumberOfWavelengths}")

    # 读取 LDE
    lde = system.LDE
    print(f"表面数量: {lde.NumberOfSurfaces}")

    # 运行 MTF 分析
    mtf = system.Analyses.New_Mtf()
    mtf.Apply()

    # 保存修改
    system.Save()

    # 关闭
    app.CloseApplication()
    print("完成!")

if __name__ == "__main__":
    main()
```
