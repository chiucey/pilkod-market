---
name: catia-development
description: CATIA development skill. Use when users ask to create CATIA automation scripts, macros, VBA macro development, CAA C++ programming, Python-COM interfaces, batch processing CATIA files, or custom CATIA functionality extensions.
---

# CATIA 二次开发技能

## 概述

CATIA 是达索系统开发的高端三维CAD/CAE/CAM软件，广泛应用于航空航天、汽车、船舶等行业。CATIA提供多种二次开发接口，支持VBA宏、CAA C++框架、Python自动化等多种开发方式。

## 开发环境

### VBA/VBScript开发
- **开发工具**: CATIA内置VBA编辑器（Alt+F11）
- **脚本语言**: VBScript, VBA
- **适用版本**: CATIA V5 R10+

### CAA C++开发
- **开发工具**: Visual Studio + CAA SDK
- **语言标准**: C++
- **适用场景**: 企业级二次开发，需要编译成模块

### Python自动化
- **接口方式**: PyWin32 (Windows COM)
- **依赖库**: pythoncom, win32com
- **适用场景**: 数据处理、批量化操作

## 核心对象模型

### CATIA Application 对象
```vba
' 获取CATIA应用对象
Dim CATIA As Object
Set CATIA = GetObject(, "CATIA.Application")

' 新建会话
Set CATIA = CreateObject("CATIA.Application")
CATIA.Visible = True
```

### Documents 集合
```vba
Dim docs As Documents
Set docs = CATIA.Documents

' 创建新文档
Dim partDoc As PartDocument
Set partDoc = docs.Add("Part")
Dim productDoc As ProductDocument
Set productDoc = docs.Add("Product")
Dim drawingDoc As DrawingDocument
Set drawingDoc = docs.Add("Drawing")
```

### Selection 选择对象
```vba
Dim selection As Selection
Set selection = CATIA.ActiveDocument.Selection

' 选择当前几何体
selection.Search "几何体.全部, in"

' 清空选择
selection.Clear

' 遍历选择
Dim i As Integer
For i = 1 To selection.Count
    Dim item As AnyObject
    Set item = selection.Item(i).Value
    Debug.Print item.Name
Next i
```

## 零件设计(PartDesign)

### 创建基础特征
```vba
Sub CreateSketch()
    Dim partDoc As PartDocument
    Set partDoc = CATIA.ActiveDocument
    
    Dim part As Part
    Set part = partDoc.Part
    
    Dim body As Body
    Set body = part.Bodies.Item(1)
    
    ' 创建草图
    Dim sketches As Sketches
    Set sketches = body.Sketches
    
    Dim hsk As HybridSketch
    Set hsk = sketches.Add(part.OriginElements.PlaneXY)
    
    Dim factory2d As Factory2D
    Set factory2d = hsk.OpenEdition
    
    ' 绘制矩形
    factory2d.CreateLine 0, 0, 100, 0
    factory2d.CreateLine 100, 0, 100, 50
    factory2d.CreateLine 100, 50, 0, 50
    factory2d.CreateLine 0, 50, 0, 0
    
    hsk.CloseEdition
    
    ' 拉伸
    Dim shape As Shape
    Set shape = part.Shapes.AddNewPad(hsk, 30)
    
    part.Update
End Sub
```

### 孔特征
```vba
Sub CreateHole()
    Dim partDoc As PartDocument
    Set partDoc = CATIA.ActiveDocument
    
    Dim part As Part
    Set part = partDoc.Part
    
    Dim bodies As Bodies
    Set bodies = part.Bodies
    
    Dim body As Body
    Set body = bodies.Item(1)
    
    ' 创建孔
    Dim hole As Hole
    Set hole = body.Holes.Add("Top.Sketch.1", 10, 0, 0)
    
    With hole
        .Type = catSimpleHole
        .ExtensionDepth = 20
        .BottomType = catHoleBottomFlat
        .BottomAngle = 120
    End With
    
    part.Update
End Sub
```

## 装配设计(Assembly)

### 约束装配
```vba
Sub AssembleComponents()
    Dim productDoc As ProductDocument
    Set productDoc = CATIA.ActiveDocument
    
    Dim rootProduct As Product
    Set rootProduct = productDoc.Product
    
    ' 添加组件
    Dim product As Product
    Set product = rootProduct.Products.AddNewProduct("Part1")
    
    ' 设置参考产品
    Dim refProduct As Product
    Set refProduct = rootProduct.Products.Item(1)
    
    ' 添加约束
    Dim constraint As Constraint
    Set constraint = rootProduct.Constraints.AddMateConstraint( _
        refProduct.Origin, product.Origin, 0)
End Sub
```

### 产品遍历
```vba
Sub TraverseProductTree()
    Dim productDoc As ProductDocument
    Set productDoc = CATIA.ActiveDocument
    
    Dim rootProduct As Product
    Set rootProduct = productDoc.Product
    
    TraverseProduct rootProduct.Products
    
End Sub

Sub TraverseProduct(products As Products)
    Dim i As Integer
    For i = 1 To products.Count
        Dim prod As Product
        Set prod = products.Item(i)
        
        Debug.Print prod.Name & " - " & prod.PartNumber
        
        ' 递归遍历子产品
        If prod.Products.Count > 0 Then
            TraverseProduct prod.Products
        End If
    Next i
End Sub
```

## 曲面设计(ShapeDesign)

### 创建基础曲面
```vba
Sub CreateSurfaces()
    Dim partDoc As PartDocument
    Set partDoc = CATIA.ActiveDocument
    
    Dim part As Part
    Set part = partDoc.Part
    
    Dim hybFactory As HybridShapeFactory
    Set hybFactory = part.HybridShapeFactory
    
    ' 创建拉伸曲面
    Dim sketch As Sketch
    Set sketch = part.Bodies.Item(1).Sketches.Item(1)
    
    Dim extrude As HybridShapeExtrude
    Set extrude = hybFactory.AddNewExtrude(sketch, 100, 0)
    
    part.Update
End Sub
```

### 曲面操作
```vba
Sub SurfaceOperations()
    Dim partDoc As PartDocument
    Set partDoc = CATIA.ActiveDocument
    
    Dim part As Part
    Set part = partDoc.Part
    
    Dim sel As Selection
    Set sel = partDoc.Selection
    
    ' 缝合曲面
    sel.Search "SurfFilter.List = SweepSurface, BlendSurface, ExtrudeSurface, CylinderSurface, SphereSurface, ConeSurface, RevolveSurface, OffsetSurface, FillSurface, AdaptiveSweepSurface;All"
    
    If sel.Count >= 2 Then
        Dim gsm As GeometricalSet
        Set gsm = part.HybridBodies.Item(1)
        
        Dim sewnSurface As HybridShapeSewnSurface
        Set sewnSurface = part.HybridShapeFactory.AddNewSewedSurface( _
            sel.Item(1).Value, sel.Item(2).Value)
        
        gsm.AppendHybridShape sewnSurface
        part.Update
    End If
End Sub
```

## 批处理

### 批量导出
```vba
Sub BatchExport()
    Dim folderPath As String
    folderPath = "C:\CATIA\Parts\"
    
    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    Dim file As Object
    For Each file In fso.GetFolder(folderPath).Files
        If LCase(fso.GetExtensionName(file.Name)) = "catpart" Then
            ' 打开文件
            Dim doc As Document
            Set doc = CATIA.Documents.Open(file.Path)
            
            ' 导出STP
            Dim expFile As String
            expFile = Left(file.Path, Len(file.Path) - 7) & "stp"
            doc.ExportData expFile, "stp"
            
            doc.Close
        End If
    Next file
End Sub
```

### Python批量处理示例
```python
import win32com.client
import os

# 连接CATIA
CATIA = win32com.client.Dispatch("CATIA.Application")
CATIA.Visible = True

def export_part_to_stp(part_path, output_dir):
    """导出零件为STP格式"""
    # 打开零件
    doc = CATIA.Documents.Open(part_path)
    
    # 生成输出路径
    filename = os.path.splitext(os.path.basename(part_path))[0]
    output_path = os.path.join(output_dir, filename + ".stp")
    
    # 导出
    doc.ExportData(output_path, "stp")
    
    # 关闭文档
    doc.Close()

def batch_export(folder_path, output_dir):
    """批量导出文件夹中的所有零件"""
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.catpart'):
            full_path = os.path.join(folder_path, filename)
            export_part_to_stp(full_path, output_dir)
            print(f"Exported: {filename}")

# 使用示例
batch_export(r"C:\CATIA\Parts", r"C:\CATIA\STP_Output")
```

## 错误处理

```vba
Sub ErrorHandling()
    On Error GoTo ErrorHandler
    
    Dim partDoc As PartDocument
    Set partDoc = CATIA.Documents.Add("Part")
    
    ' 正常操作
    Dim part As Part
    Set part = partDoc.Part
    
    ' 故意制造错误
    Dim invalid As Object
    Set invalid = Nothing
    invalid.DoSomething  ' 这里会触发错误
    
ErrorHandler:
    If Err.Number <> 0 Then
        MsgBox "错误编号: " & Err.Number & vbCrLf & _
               "错误描述: " & Err.Description & vbCrLf & _
               "错误来源: " & Err.Source, _
               vbCritical, "CATIA VBA错误"
        
        ' 记录错误日志
        Call LogError(Err.Number, Err.Description, Err.Source)
        
        Err.Clear
    End If
End Sub

Sub LogError(errNum As Long, errDesc As String, errSource As String)
    Dim logFile As Object
    Set logFile = CreateObject("Scripting.FileSystemObject")
    
    Dim file As Object
    Const ForAppending = 8
    
    Set file = logFile.OpenTextFile( _
        "C:\CATIA\ErrorLog.txt", _
        ForAppending, _
        True)
    
    file.WriteLine Now & " - Error " & errNum & ": " & errDesc & " (" & errSource & ")"
    file.Close
End Sub
```

## 常用技巧

### 性能优化
```vba
Sub OptimizePerformance()
    ' 禁用更新以提高速度
    CATIA.RefreshDisplay = False
    
    ' 批量操作
    Dim i As Long
    For i = 1 To 1000
        ' 执行操作
    Next i
    
    ' 恢复更新
    CATIA.RefreshDisplay = True
End Sub
```

### UI交互
```vba
Sub UserInteraction()
    ' 打开文件选择对话框
    Dim fileName As String
    fileName = CATIA.FileSystem.ChooseFile("选择CATIA文件", _
                                           "CATIA Files (*.CATPart;*.CATProduct)|*.CATPart;*.CATProduct", _
                                           "C:\CATIA\")
    
    If fileName <> "" Then
        CATIA.Documents.Open fileName
    End If
End Sub
```

### 监控进度
```vba
Sub ProgressMonitor()
    Dim statusBar As StatusBar
    Set statusBar = CATIA.StatusBar
    
    Dim i As Long
    For i = 1 To 100
        statusBar.Text = "正在处理: " & i & "/100"
        ' 执行操作
    Next i
    
    statusBar.Text = "完成"
End Sub
```

## CAA C++开发基础

### 模块定义
```cpp
// MyModule.h
#include "CATBaseUnknown.h"
#include "CATDocument.h"
#include "CATIContainerOfDocument.h"

class MyModule : public CATBaseUnknown {
public:
    MyModule();
    virtual ~MyModule();
    
    HRESULT __stdcall CreatePart(CATDocument*& oPart);
    HRESULT __stdcall OpenDocument(const char* iFilePath, CATDocument*& oDoc);
};
```

### 注册CAA模块
```cpp
// 在CAA应用初始化时注册
#include "CATAutoBase.h"
#include "CATCommandHeader.h"

// 创建命令头
CreateExternalHeader("MyModule", "MyCreatePart", 
                     "创建零件", MyModule::CreatePart);
```

## 参考资源

- **官方文档**: CATIA V5 Automation Documentation
- **API参考**: CAA V5 Encyclopedia
- **社区资源**: CATIA Forum, 3DExperience Community
- **达索官网**: https://www.3ds.com/products/catia
