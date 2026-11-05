# 运动控制示例库

## 基本运动功能块

### 使能轴 (MC_Power)

```pascal
FUNCTION_BLOCK MC_Power
VAR_INPUT
    Axis        : AXIS_REF;
    Enable      : BOOL;
    bRegulatorOn  : BOOL := TRUE;
    bDriveOn      : BOOL := TRUE;
END_VAR
VAR_OUTPUT
    bEnabled    : BOOL;
    Error       : BOOL;
    ErrorID     : DINT;
END_VAR

// 上升沿使能
IF Enable AND NOT "AxisCtrl".EnablePrev THEN
    "AxisCtrl".Enable := TRUE;
END_IF;
"AxisCtrl".EnablePrev := Enable;

// 读取状态
bEnabled := "AxisStatus".bEnabled;
Error := "AxisStatus".Error;
END_FUNCTION_BLOCK
```

### 绝对位移 (MC_MoveAbsolute)

```pascal
FUNCTION_BLOCK MC_MoveAbsolute
VAR_INPUT
    Axis        : AXIS_REF;
    Execute     : BOOL;
    Position    : LREAL;
    Velocity    : LREAL;
    Acceleration : LREAL := 1000.0;
    Deceleration : LREAL := 1000.0;
END_VAR
VAR_OUTPUT
    Done        : BOOL;
    Busy        : BOOL;
    Error       : BOOL;
END_VAR

IF Execute AND NOT Busy THEN
    MC_MOVE_ABSOLUTE(
        Axis := Axis,
        Execute := Execute,
        Position := Position,
        Velocity := Velocity,
        Acceleration := Acceleration,
        Deceleration := Deceleration
    );
END_IF;

Done := MC_MOVE_ABSOLUTE.Done;
Busy := MC_MOVE_ABSOLUTE.Busy;
Error := MC_MOVE_ABSOLUTE.Error;
END_FUNCTION_BLOCK
```

## 参数计算公式

### 电机转速与线速度转换

```
线速度(m/min) = π × D(mm) × RPM / 1000
RPM = 线速度 × 1000 / (π × D)
```

### 加速时间计算

```
t = V / a
例：速度1000mm/s，加速度500mm/s²
t = 1000 / 500 = 2s
```

## 常见故障处理

| 故障现象 | 可能原因 | 解决方案 |
|----------|----------|----------|
| 轴无法使能 | 轴未回零 | 执行回原功能 |
| 运动抖动 | 加减速过急 | 降低加减速 |
| 定位超差 | 伺服增益不匹配 | 调整伺服参数 |