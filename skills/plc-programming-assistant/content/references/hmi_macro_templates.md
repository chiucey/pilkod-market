# HMI宏模板库

## Weinview 宏语言基础

### 按钮宏 - 启动设备

```c
// 按钮按下时执行
macro_command main()
short nDeviceId = 1
bool bStart = true

// 写入设备地址
SetData(bStart, "PLC1", LB, 100, 1)  // 启动位
SetData(nDeviceId, "PLC1", RW, 0, 1) // 设备ID

end macro_command
```

### 数据更新宏

```c
// 周期性更新配方数据
macro_command main()
short i
float fValue

for i = 0 to 15
    GetData(fValue, "PLC1", RW, 100 + i * 2, 1)
    SetData(fValue, "Local HMI", RW, 1000 + i * 2, 1)
next i

end macro_command
```

## TIA Portal HMI 脚本

### 弹窗确认

```vb
Sub ShowConfirmDialog()
    HMIRuntime.UI.Alarm("确认启动?", vbYesNo + vbQuestion)
End Sub

Sub OnConfirm(ReturnValue)
    If ReturnValue = vbYes Then
        SmartTags("StartCmd") = True
    End If
End Sub
```

### 配方切换

```vb
Sub LoadRecipe(sRecipeName As String)
    Dim oRecipe As HMIRuntime.Recipe
    Set oRecipe = HMIRuntime.Recipes.Item(sRecipeName)
    oRecipe.Load
End Sub
```

## Pro-face 宏

### 报警历史

```python
// Pro-face GP-Pro EX 宏
Sub Main
    Dim nIndex As Integer
    For nIndex = 0 To 99
        If Word("PLC1", 1000 + nIndex) = 1 Then
            Call DisplayAlarm(nIndex)
        End If
    Next
End Sub
```

## 常见宏问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 宏不执行 | 触发条件未设置 | 检查按钮/事件绑定 |
| 数据不同步 | 通信周期慢 | 调整PLC扫描周期 |
| 界面卡顿 | 宏逻辑复杂 | 拆分宏/优化算法 |