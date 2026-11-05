# Modbus RTU 完整指南

## 协议基础

### 帧结构
| 字段 | 长度 | 说明 |
|------|------|------|
| 从站地址 | 1字节 | 1-247 |
| 功能码 | 1字节 | 03/04/06/16常用 |
| 数据 | N字节 | 寄存器地址+数量 |
| CRC | 2字节 | 低字节在前 |

### 常用功能码
- **03**: 读保持寄存器
- **04**: 读输入寄存器
- **06**: 写单个寄存器
- **16**: 写多个寄存器

## SCL实现模板

### 读保持寄存器 (功能码03)

```pascal
FUNCTION_BLOCK FB_ModbusRead03
VAR_INPUT
    xTrigger    : BOOL;
    iSlaveAddr  : INT := 1;
    iStartReg   : INT;
    iRegCount   : INT := 1;
END_VAR
VAR_OUTPUT
    xDone       : BOOL;
    xError      : BOOL;
    iErrorId    : INT;
    aData       : ARRAY[0..19] OF WORD;
END_VAR
VAR
    byTxBuffer  : ARRAY[0..7] OF BYTE;
    byRxBuffer  : ARRAY[0..255] OF BYTE;
    iTxLen      : INT;
    fbCRC       : CRC16;
    tTimeout    : TON;
    iState      : INT := 0;
END_VAR

// 构建请求帧
byTxBuffer[0] := INT_TO_BYTE(iSlaveAddr);      // 从站地址
byTxBuffer[1] := 16#03;                         // 功能码03
byTxBuffer[2] := INT_TO_BYTE(SHR(IN := INT_TO_WORD(iStartReg), N := 8)); // 高字节
byTxBuffer[3] := INT_TO_BYTE(iStartReg AND 16#FF); // 低字节
byTxBuffer[4] := INT_TO_BYTE(SHR(IN := INT_TO_WORD(iRegCount), N := 8));
byTxBuffer[5] := INT_TO_BYTE(iRegCount AND 16#FF);

// CRC计算
fbCRC(u16Data := WORD_TO_UINT(buildWord(byTxBuffer[0], byTxBuffer[1])));
// ... 完整CRC计算省略

CASE iState OF
    0: // 空闲
        IF xTrigger THEN iState := 10; END_IF;
    10: // 发送请求
        // SerialSend(byTxBuffer, iTxLen);
        iState := 20;
    20: // 等待响应
        tTimeout(IN := TRUE, PT := T#500ms);
        IF tTimeout.Q THEN
            xError := TRUE;
            iErrorId := 1; // 超时
            iState := 0;
        END_IF;
    30: // 解析响应
        // 检查从站地址、功能码、CRC
        FOR i := 0 TO iRegCount-1 DO
            aData[i] := buildWord(byRxBuffer[3+i*2], byRxBuffer[4+i*2]);
        END_FOR;
        xDone := TRUE;
        iState := 0;
END_CASE;
END_FUNCTION_BLOCK
```

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 无响应 | 波特率不匹配 | 确认从站9600/19200 |
| CRC错误 | 字节序错误 | 检查高低字节顺序 |
| 数据异常 | 数据类型不匹配 | 确认REAL/INT格式 |
| 偶尔超时 | 干扰/接地不良 | 检查屏蔽线接地 |