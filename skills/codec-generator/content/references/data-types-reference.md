# 平台数据类型与编解码格式参考

本附录预置了平台支持的全部属性数据类型及其在协议报文编解码中的常见实现方式。生成编解码器时，根据物模型中每个属性的**数据类型**选择对应的编解码方法。

## A.1 平台支持的属性数据类型（DataTypeConstant）

平台物模型中定义的 15 种属性数据类型：

| 数据类型标识 | 说明 | 编码器中 data 的输出格式 | 适用场景 |
|-------------|------|------------------------|---------|
| **int** | 32位整数 | `"123"` (十进制字符串) | 计数值、状态码、信号强度 |
| **int64** | 64位长整数 | `"1765337383000"` (字符串) | 时间戳、大计数器 |
| **float** | 32位浮点数 | `"3.14"` (字符串) | 精度要求不高的浮点值 |
| **double** | 64位双精度浮点 | `"3.1415926"` (字符串) | 高精度测量值(电压、流量、温度) |
| **text** | 文本字符串(≤200字符) | `"hello world"` | 设备描述、错误信息 |
| **string** | 字符串(同 text, ≤200字符) | `"ABCDEF012345"` | 表号、序列号等 |
| **bool** | 布尔值 | `"1"` 或 `"0"` (或 `"true"/"false"`) | 开关状态、报警标志 |
| **enum** | 枚举(整数字符串) | `"0"`, `"1"`, `"2"` ... | 工作模式、故障类型 |
| **date** | 日期 | `"2026-04-07"` | 生产日期、固件日期 |
| **timestamp** | 毫秒级时间戳 | `"1765337383000"` (13位) 或 `"1765337383"` (10位秒级) | 设备上报时间 |
| **BINARY** | 二进制数据 | Base64 或 HEX 字符串 | 图片、签名等二进制载荷 |
| **VARCHAR** | 变长字符串 | 同 string | 兼容旧版 |
| **base64String** | Base64编码字符串 | `"YWJjZGVm..."` | 二进制数据的文本传输 |
| **int2/int4/int8** | 数据库适配类型(同 int/int64) | 同 int/int64 | KaiwDB 适配 |
| **float4/float8** | 数据库适配类型(同 float/double) | 同 float/double | KaiwDB 适配 |

> 数据来源：`DataTypeConstant.java`（core 模块 + TS 模块两个版本）

## A.2 常见协议数据编码格式与 Java 转换方法

物联网设备协议报文中常见的数据存储方式及对应 Java 解析代码：

### 整数类型

| 协议编码方式 | 字节数 | 示例(HEX→值) | Java 解析方法 |
|------------|-------|-------------|--------------|
| **BCD码** (压缩BCD) | 1字节=2位数字 | `0x25` → `25`, `0x99` → `99` | `(byte & 0x0F) * 10 + ((byte >> 4) & 0x0F)` |
| **BCD码** 多字节(小端) | N字节 | `[0x34,0x12]` → `1234` | 从低位字节开始拼接 BCD 数字 |
| **无符号整数** (Big-Endian) | 1/2/4字节 | `[0x00,0xFF]` → `255` | `ByteBuffer.wrap(bytes).getShort() & 0xFFFF` |
| **有符号整数** (Big-Endian) | 2/4字节 | `[0xFF,0xF0]` → `-16` | `ByteBuffer.wrap(bytes).getShort()` |
| **无符号整数** (Little-Endian) | 2/4字节 | `[0xF0,0x00]` → `240` | 反转字序后按 Big-Endian 解析 |
| HEX字符串转整数 | — | `"1A2B"` → `6699` | `Integer.parseInt(hexStr, 16)` |

### 浮点类型

| 协议编码方式 | 字节数 | 示例(HEX→值) | Java 解析方法 |
|------------|-------|-------------|--------------|
| **IEEE754 单精度** (Big-Endian) | 4字节 | `[0x41,0xE4,0x80,0x00]` → `28.5` | `Float.intBitsToFloat(ByteBuffer.wrap(bytes).getInt())` |
| **IEEE754 双精度** (Big-Endian) | 8字节 | 8字节HEX | `Double.longBitsToDouble(...)` |
| **定点数** (缩放因子) | N字节整数 + 缩放 | 整数 `3052` /100 = `30.52` | `rawValue / scaleFactor` |
| **BCD浮点** (高低位组合) | 2字节 | 低=`0x31`, 高=`0x03` → `3.031`V | `low + high / 1000.0` (电压常用) |

### 字符串与时间

| 协议编码方式 | 示例(HEX→值) | Java 解析方法 |
|------------|-------------|--------------|
| **ASCII字符串** | `[0x41,0x42,0x43]` → `"ABC"` | `new String(bytes, StandardCharsets.US_ASCII)` |
| **UTF-8字符串** | UTF-8字节序列 | `new String(bytes, StandardCharsets.UTF_8)` |
| **BCD时间** (7字节: 秒分时日月年世纪) | `[00,30,09,07,04,26,20]` → `2026-04-07 09:30:00` | 逐字段解析 BCD 后组装为 Date/long |

### 布尔与枚举

| 协议编码方式 | 示例 | Java 解析方法 | 输出格式 |
|------------|------|-------------|---------|
| **位标志** (bit flag) | `byte & 0x01 == 1` | `(bytes[pos] >> bitOffset) & 0x01` | `"1"` / `"0"` |
| **单字节枚举** | `0x00`=正常, `0x01`=故障 | 直接读取 byte 值 | `"0"` / `"1"` / `"2"` |
| **多bit位域** | 一个byte包含多个标志 | 逐位提取 | 各自输出 `"1"/"0"` |

## A.3 Modbus 数据类型参考

平台内置 Modbus 协议支持的数据类型常量 (`ModbusDataTypeConstant`)：

| 常量名 | 值 | 含义 | 字节数 | Java 对应类型 |
|-------|---|------|-------|-------------|
| TWO_BYTE_INT_UNSIGNED | 1 | 16位无符号整数 | 2 | `short`(0~65535) |
| TWO_BYTE_INT_SIGNED | 2 | 16位有符号整数 | 2 | `short`(-32768~32767) |
| FOUR_BYTE_INT_UNSIGNED | 3 | 32位无符号整数 | 4 | `int`(0~4294967295) |
| FOUR_BYTE_INT_SIGNED | 4 | 32位有符号整数 | 4 | `int`(-2147483648~2147483647) |
| FOUR_BYTE_FLOAT | 5 | 32位IEEE754浮点 | 4 | `float` |
| BOOL | 6 | 布尔值 | 1/1bit | `boolean` |

> 来源：`ModbusDataTypeConstant.java`

## A.4 平台 DataTypeFormatter 验证规则

平台的 `DataTypeFormatter` 类对编解码器上报的属性值进行校验。编解码器输出的字符串值**必须符合以下规则**，否则平台会拒绝数据：

| 数据类型 | 平台验证规则 | 合法示例 | 非法示例 |
|---------|------------|---------|---------|
| **int** | 正则 `^-?\d+$` (纯整数) | `"123"`, `"-456"` | `"12.3"`, `"abc"` |
| **float/double** | 正则 `^[-+]?[.\d]*$` (数字/小数/点) | `"3.14"`, `".5"`, `"123."` | `"abc"` |
| **bool** | `"1"`, `"0"`, `"true"`, `"false"`, `"1.0"`, `"0.0"` | `"1"` | `"yes"`, `"on"` |
| **enum** | 正则 `^-?\d+$` (非负整数) | `"0"`, `"1"`, `"2"` | `"open"`, `"close"` |
| **string/text** | 长度 ≤ 200 字符 | `"正常字符串"` | 超200字符的字符串 |
| **timestamp** | 长度为 13 位(毫秒) 或 10 位(秒) 的数字 | `"1765337383000"` | `"2026-04-07"` (非法!) |

> **⚠️ 关键注意**：所有属性值在 DecodedMessage.data 中**统一以字符串形式输出**。即使原始数据是整数或浮点数，也必须转为字符串后放入 JSON。
>
> **时间戳陷阱**：如果物模型某属性的类型是 `date`，但编解码器输出了时间戳格式的字符串（如 `"1765337383000"`），平台会将其作为 timestamp 处理而非 date。需要根据物模型实际类型决定输出格式。

来源：
- TS模块版本：`DataTypeFormatter.java` — `dandelion-framework/common-ts/utils/`
- DA模块版本：`DataTypeFormatter.java` — `dandelion-business/da/utils/`

## A.5 常见设备类型的典型属性映射示例

### 水表（智能水表）

| 物模型属性标识 | 数据类型 | 协议字段 | 协议编码 | 解析方法 |
|---------------|---------|---------|---------|---------|
| cumulativeUsageM3 | double | 累计用量(m³) | 4字节 BCD/HEX | 定点数: raw / 10000 |
| instantaneousFlowLh | double | 瞬时流量(L/h) | 2字节 HE | raw / 10.0 |
| batteryVoltageV | double | 电池电压(V) | 2字节 BCD | BCD浮点: low + high/1000 |
| signalStrengthRSRP | int | 信号强度(dBm) | 1字节有符号 | signed byte - 140 (如 25→-115) |
| valveStatus | bool | 阀门状态 | 1字节 | `0`=关, `1`=开 |
| meterNumber | string | 表号 | 7字节 BCD | BCD→字符串 |

### 电表（智能电表）

| 物模型属性标识 | 数据类型 | 协议字段 | 协议编码 | 解析方法 |
|---------------|---------|---------|---------|---------|
| totalEnergyKwh | double | 总电量(kWh) | 4字节 BCD/HEX | 定点数: raw / 100 |
| voltageV | double | 电压(V) | 2字节整数 | raw / 10.0 |
| currentA | double | 电流(A) | 2字节整数 | raw / 1000.0 |
| activePowerW | int | 有功功率(W) | 2字节整数 | 直接使用 |
| powerFactor | double | 功率因数 | 1字节整数 | raw / 100.0 |
| frequencyHz | double | 频率(Hz) | 1字节整数 | raw / 10.0 |

### 传感器（温湿度/烟感）

| 物模型属性标识 | 数据类型 | 协议字段 | 协议编码 | 解析方法 |
|---------------|---------|---------|---------|---------|
| temperatureValue | float | 温度(°C) | 2字节有符号整数 | raw / 10.0 |
| humidityValue | int | 湿度(%RH) | 1字节无符号整数 | 直接使用(0~100) |
| smokeAlarmStatus | bool | 烟雾报警 | 1bit | `0`=正常, `1`=报警 |
| batteryPercent | int | 电池电量(%) | 1字节无符号整数 | 0~100 |

### GPS定位设备

| 物模型属性标识 | 数据类型 | 协议字段 | 协议编码 | 解析方法 |
|---------------|---------|---------|---------|---------|
| longitude | double | 经度 | 4字节(×10^6) | raw / 1000000.0 |
| latitude | double | 纬度 | 4字节(×10^6) | raw / 1000000.0 |
| speedKmh | double | 速度(km/h) | 2字节(×10) | raw / 10.0 |
| headingDeg | int | 方向角(°) | 2字节无符号整数 | 0~360 |

## A.6 编解码工具类通用方法清单

以下是 CodecUtils 中应包含的通用工具方法，覆盖上述所有数据类型的转换：

```java
// ===== BCD 编解码 =====
String parseBcdMeterNumber(byte[] bytes, int offset);     // N字节BCD→表号字符串
String parseBcdTimeStr(byte[] bytes, int offset);         // 7字节BCD→时间字符串
long parseBcdTimeMs(byte[] bytes, int offset);            // 7字节BCD→毫秒时间戳
int parseBcdByte(byte b);                                 // 1字节BCD→整数(0~99)
double parseBcdVoltage(byte low, byte high);              // 2字节BCD→电压(低位+高位/1000)

// ===== 整数编解码 =====
int parseUInt8(byte b);                                   // 无符号字节→int(0~255)
int parseUInt16BE(byte[] bytes, int offset);              // 大端2字节→unsigned int
int parseInt16BE(byte[] bytes, int offset);               // 大端2字节→signed int
int parseUInt16LE(byte[] bytes, int offset);              // 小端2字节→unsigned int
long parseHex4LE(byte[] bytes, int offset);               // 小端4字节HEX→long
int parseIntFromHex(String hexStr);                       // HEX字符串→int

// ===== 浮点编解码 =====
float parseFloatBE(byte[] bytes, int offset);             // IEEE754单精度(Big-Endian)
double parseFixedPoint(int rawValue, int scale);          // 定点数→double (如 raw/100)
double parseFixedPoint(long rawValue, int scale);         // 长整型定点数

// ===== 字节操作 =====
String byteArrayToHexString(byte[] bytes);                // byte[]→HEX字符串(无空格)
byte[] hexStringToByteArray(String hexStr);               // HEX字符串→byte[]
int calcCrc16(byte[] data, int len);                      // CRC16计算
byte calcCs(byte[] data, int start, int end);             // 累加和校验
boolean validateFrame(byte[] frame);                      // 完整帧校验(CRC/CS)

// ===== ACK 帧构建 =====
byte[] buildReportResponseFrame(JSONObject msg);          // 上报应答帧
```
