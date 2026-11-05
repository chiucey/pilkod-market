# Profinet诊断手册

## 诊断块结构

```pascal
FUNCTION_BLOCK FB_ProfinetDiag
VAR_OUTPUT
    xBusOK      : BOOL;
    xDeviceErr  : ARRAY[0..15] OF BOOL;
    iActiveAlarm: INT;
END_VAR
VAR
    pDeviceData : POINTER TO BYTE;
    iIdx        : INT;
END_VAR

// 读取IO设备状态
FOR iIdx := 0 TO 15 DO
    xDeviceErr[iIdx] := NOT pDeviceData[iIdx*4 + 1] AND 16#01;
END_FOR;

// 总线状态
xBusOK := RDSEQ() = 16#08; // RUN状态
```

## 常见错误代码

| 错误码 | 含义 | 处理措施 |
|--------|------|----------|
| 16#1A00 | 模块故障 | 检查模块插接 |
| 16#1A10 | 模块不一致 | 更新组态 |
| 16#1B00 | 站点故障 | 检查网线连接 |