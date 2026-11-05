---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8a141621c62237dd8af289fe90d03cd9
    PropagateID: 8a141621c62237dd8af289fe90d03cd9
    ReservedCode1: 3045022100a6ef9fbcf550d51f65fdad7efdeee0e84a9a10f460536dc2b3cfb06d0562b7f4022026d07ee3e6105e8cb2656aa82e8c1e3f86c585c2063955d7ef4d1e6df3764a6f
    ReservedCode2: 304602210088da36c07498b8cdbb5fbfb28b978d7fe7f024d70a6f9d64f0545fbd899c17ba022100eb9578293c23ef494d3e1baa33793b2dda1c65104a832b3c57383529e4d8a762
---

---
name: codec-generator
description: 根据用户提供的私有协议文档或信息，生成基于 AccessProtocolModel 接口的编解码器 JAR 包。适用于水表、电表、传感器等物联网设备的协议编解码实现。解码后的数据格式统一为 DecodedMessage。
---

# Codec Generator

根据用户上传的私有协议文档或信息，自动生成编解码器 Java 代码并打包成 JAR 文件。

## 核心特性

1. **标准数据格式** - 解码后统一返回 `DecodedMessage` 对象
2. **⚠️ 强制测试验证** - 打包 JAR 前**必须**经过测试验证（优先在线测试🧪），**必须等待用户确认**测试结果正确后才能打包
3. **⚠️ 物模型键名严格匹配** - 解码后 data 中的键名必须与物模型属性标识符**完全一致**（大小写、下划线等），否则平台无法识别数据
4. **自带依赖包** - 包含 `dandelion-common-codec` JAR，无需外部依赖
5. **自动生成 lib 目录** - 创建项目时自动复制依赖
6. **多种平台支持** - AEP、OneNET、TCP/UDP直连
7. **丰富的示例模板** - 水表、烟感、车辆等多种设备类型
8. **CRC 校验容错** - 设备 CRC 为 0 或算法不一致时不阻止帧解析（仅 WARN）
9. **ACK 应答编码** - encode() 必须实现 reportResponse 命令类型
10. **JAR 包命名规范** - 使用编解码器类全路径名作为 artifactId
11. **⚠️ 强制人工确认** - 映射检查和测试确认环节必须人工确认，不可自动忽略
12. **🚀 简化编码逻辑** - 9种协议按返回值类型分组为3组，减少重复代码
13. **☕ Java 11 支持** - 使用 Java 11 编译和运行
14. **🧪 在线测试** - 代码生成后提供在线测试页面，输入HEX报文即可验证解码逻辑，无需编译

## 触发条件

当用户请求以下类型任务时触发：
- "生成编解码器 JAR 包"
- "根据协议文档创建编解码器"
- "实现协议编解码"
- "打包编解码器"
- 任何涉及创建物联网设备协议编解码器的请求

## 工作流程概览

```
┌─────────────────────────────────────────────────────────────────┐
│  步骤1: 收集资料     │  必须同时提供协议文档 + 平台物模型      │
├─────────────────────────────────────────────────────────────────┤
│  步骤2: 确认协议类型 │  用户已明确指定时自动确认，否则询问     │
├─────────────────────────────────────────────────────────────────┤
│  步骤3: 分析映射     │  协议字段 ↔ 物模型属性标识符 建立映射   │
│                      │  ⚠️ 资料不足时必须人工确认，不可忽略    │
├─────────────────────────────────────────────────────────────────┤
│  步骤4: 生成代码     │  按协议类型分组生成（3组通用模板）      │
│                      │  byte[] / DownlinkRequest / JSONObject  │
├─────────────────────────────────────────────────────────────────┤
│  步骤5: 测试验证     │  优先使用在线测试（🧪），备选编译测试   │
├─────────────────────────────────────────────────────────────────┤
│  步骤6: 用户确认     │  ⚠️ 必须人工确认测试结果正确，不可忽略  │
├─────────────────────────────────────────────────────────────────┤
│  步骤7: 打包 JAR     │  用户确认后才可执行打包                 │
└─────────────────────────────────────────────────────────────────┘
```

> **重要**：
> - 第2步：如果用户一开始就明确指定了协议类型（如"TCP协议"、"AEP平台"），**无需询问**，直接使用
> - **第3.3步（映射检查）**：资料不足时**必须人工确认**，等待用户选择处理方案，**严禁自动忽略**
> - **第6步（用户确认）**：测试完成后**必须人工确认**结果正确，等待用户明确回复，**严禁自动继续打包**
> - 未经过用户明确确认前，**绝对禁止打包 JAR**

### 1. 收集协议信息 ⚠️ 需要两份资料

**必须同时提供以下两份资料，缺一不可：**

#### 资料一：协议文档

设备通讯协议的详细规格说明：
- **协议文档**：协议规格说明书、数据帧格式文档等
- **协议类型**：TCP/UDP/其他传输层协议
- **平台类型**：AEP/OneNET/私有平台等
- **设备类型**：水表、电表、传感器等
- **关键字段**：设备编码、功能码、数据域等定义

#### 资料二：平台物模型

用户在平台侧构建设备模板时定义的**物模型（Thing Model）**，通常包含：
- **属性列表**：属性的标识符（identifier）、名称、数据类型
- **服务列表**：设备支持的操作指令

> **获取方式**：从平台设备模板页面导出，或截图/复制物模型的属性列表。
> 如果用户无法提供，应明确告知：编解码器的属性编码可能与平台不一致，导致数据无法正确映射。

#### ⚠️ 两份资料的关系

物模型中的**属性标识符（identifier）**就是编解码器解码后 data 中使用的 key。例如：

| 物模型属性标识符 | 协议报文字段 | 编解码器 data 中的 key |
|---|---|---|
| `cumulativeUsageM3` | 数据标识 901F（累计用量） | `"cumulativeUsageM3": "123.45"` |
| `batteryVoltageV` | 数据标识 9020（电池电压） | `"batteryVoltageV": "3.103"` |

**编解码器解码后上报的属性编码必须与平台物模型的属性标识符完全一致**，否则平台无法识别设备上报的数据。

### 2. 协议类型确认

#### 2.1 判断用户是否已明确指定协议类型

**首先检查用户在请求中是否已明确指定协议类型**：

- 如果用户明确提到了协议类型（如"TCP协议"、"MQTT"、"AEP平台"、"OneNET"等），**无需询问**，直接确认并使用该协议类型
- 如果用户未明确说明协议类型，或表述模糊（如只说"物联网设备"、"传感器"），则需要进入2.2节询问确认

**常见协议类型关键词**：TCP、UDP、MQTT、CoAP、LwM2M、AEP、OneNET、HTTP

---

#### 2.2 9种支持的协议类型

当用户未明确指定协议类型时，根据用户提供的协议文档和平台信息，向用户列出**9种支持的协议类型**，等待用户确认：

| 序号 | 协议类型 | 说明 | 典型场景 |
|------|---------|------|---------|
| 1 | **TCP（服务端）** | 设备作为客户端连接平台TCP服务 | 大多数物联网设备 |
| 2 | **UDP** | 无连接传输协议 | 实时性要求高、可丢包场景 |
| 3 | **MQTT** | 发布订阅模式的消息协议 | 需要低功耗、高并发的场景 |
| 4 | **CoAP** | 受限应用协议，类HTTP | 资源受限设备（NB-IoT） |
| 5 | **LwM2M** | 轻量级M2M协议 | 蜂窝网络设备管理 |
| 6 | **AEP（电信平台HTTP）** | 中国电信AEP平台 | 电信AEP平台接入 |
| 7 | **OneNET（移动平台HTTP）** | 中国移动OneNET平台 | 移动OneNET平台接入 |
| 8 | **TCP客户端** | 平台作为客户端连接设备 | 设备作服务端场景 |
| 9 | **HTTP** | 超文本传输协议 | Web/云平台直连 |

#### 2.3 向用户展示并确认（仅当需要时）

**当用户未明确指定协议类型时**，向用户展示推测的协议类型并请求确认：

```
根据您提供的协议文档和平台信息，推测您的设备使用以下协议类型：

📋 协议类型：[TCP（服务端）]
📋 平台类型：[私有平台/AEP/OneNET/...]
📋 传输方式：[TCP/UDP/MQTT/...]

请确认上述协议类型是否正确？如果不对，请告诉我正确的协议类型序号（1-9）。
```

**⚠️ 重要规则：**
1. **用户已明确指定协议类型时**：直接确认并使用，无需再次询问，立即进入第3步
2. **用户未明确指定协议类型时**：必须等待用户明确确认，不得自动继续执行
3. 用户确认方式：回复"正确"、"是"、"确认"、协议类型名称或序号
4. 如果用户指出协议类型错误，需要根据用户反馈修正后再确认
5. **未获得用户确认前（且用户未明确指定时），禁止进入第3步（分析协议结构）**
6. 协议类型决定了 decode() 的输入格式和 encode() 的返回值格式（byte[] 或 HTTP JSON），必须准确

#### 2.3 协议类型与 encode() 返回值的关系

| 协议类型 | encode() 返回值 | 备注 |
|---------|----------------|------|
| TCP/UDP/CoAP | `byte[]` | 编码后的协议帧字节数组 |
| MQTT | `byte[]` 或 String | 视透传/编解码模式而定 |
| LwM2M | `DownlinkRequest` | LwM2M专用下行请求对象 |
| AEP/OneNET HTTP | `JSONObject` | 包含apiUrl、httpMethod等HTTP调用信息 |
| HTTP | 视具体情况 | 可能透传或不支持 |

📎 **详细格式参考**：`references/encode-message-formats-detailed.md`

---

### 3. 分析协议结构与物模型映射

#### 3.1 分析协议结构

根据协议文档，提取以下关键信息：
- **帧格式**：起始符、长度、帧标识、版本号、设备地址、功能码、数据域、校验码等
- **功能码定义**：主动上报(1)、查询(2)、告警(3)、参数设置等
- **数据类型**：BCD码、HEX、ASCII、加密方式等
- **校验方式**：累加和、CRC等

#### 3.2 分析物模型并建立映射

根据用户提供的物模型，提取所有属性标识符，并与协议文档中的数据域建立对应关系：

```
协议数据标识 / 字段位置  →  物模型属性标识符
----------------------------------------
数据标识 901F（4字节hex） → cumulativeUsageM3
数据标识 9020（2字节BCD） → batteryVoltageV
数据标识 9021（7字节BCD） → realTime
...
```

**映射规则（⚠️ 严格执行）**：

1. **键名必须严格对应物模型属性标识符**
   - 解码后的 `DecodedMessage.data.data` 中的键名（key）**必须**与物模型中的属性标识符（identifier）**完全一致**
   - 包括大小写、下划线、数字等字符都必须一致
   - 示例：物模型中属性标识符是 `cumulativeUsageM3`，则解码后的 JSON 必须是 `"cumulativeUsageM3": "123.45"`，**不能**使用 `"CumulativeUsageM3"`、 `"cumulative_usage_m3"` 或 `"累计用量"`

2. **协议数据标识 → 物模型属性标识符**
   - 协议中的数据标识（如 901F）是解码的输入
   - 物模型属性标识符是解码后 data 中的 key
   - 建立映射关系：`数据标识 901F → cumulativeUsageM3`

3. **禁止上报物模型中不存在的属性（多余字段）⚠️**
   - **只上报物模型中已定义的属性**，协议中解析出但物模型中没有对应属性的字段**不得**放入 data 中
   - 多余字段会导致平台无法识别，可能引发数据存储异常或平台报错
   - 示例：协议解析出 901F（累计用量）、9020（电池电压）、9022（信号强度），但物模型中只有 `cumulativeUsageM3` 和 `batteryVoltageV`，则 data 中**只能**包含这两个字段，**不得**包含 `signalStrength`
   - 如果用户需要上报某些字段，必须先确保物模型中已定义对应的属性标识符

4. **未映射字段处理**
   - 如果协议中有字段在物模型中没有对应属性，**必须忽略不解析**，不得放入 data
   - 如果用户希望上报这些字段，应提醒用户先在物模型中补充对应的属性标识符

**错误示例（严格禁止）**：
```java
// ❌ 错误：使用了自定义命名，与物模型不一致
{"data": {"累计用量": "123.45", "battery_voltage": "3.103"}}

// ❌ 错误：大小写不一致
{"data": {"CumulativeUsageM3": "123.45"}}  // 物模型中是 cumulativeUsageM3（小写c）

// ❌ 错误：命名风格不一致
{"data": {"cumulative_usage_m3": "123.45"}}  // 物模型中是 cumulativeUsageM3（驼峰）

// ❌ 错误：上报了物模型中不存在的属性（多余字段）
// 物模型中只有 cumulativeUsageM3 和 batteryVoltageV
{"data": {
    "cumulativeUsageM3": "123.45", 
    "batteryVoltageV": "3.103",
    "signalStrength": "85"  // ⚠️ 物模型中没有此属性，禁止上报！
}}

// ✅ 正确：与物模型属性标识符完全一致，且不包含多余字段
{"data": {"cumulativeUsageM3": "123.45", "batteryVoltageV": "3.103"}}
```

**重要提醒**：
1. 平台通过物模型属性标识符来识别和展示设备数据。如果键名与物模型不一致，平台将无法正确显示数据，导致设备"上报成功但数据不可见"的问题。
2. 上报物模型中不存在的属性会导致平台无法识别这些字段，可能引发数据存储异常或平台报错。

#### 3.3 ⚠️ 映射完整性检查 —— 资料不足时询问用户

分析完成后，**必须检查映射是否完整**。以下情况视为"资料不足"：

**情况A：协议字段无法映射到物模型**
- 协议文档中定义了数据字段（如数据标识、功能码对应的数据），但在物模型中找不到对应的属性标识符
- 例如：协议中有 "901F=累计流量"，但物模型中只有 "flowRate" 而没有 "cumulativeFlow"

**情况B：物模型属性无法找到协议来源**
- 物模型中定义了属性，但协议文档中没有说明该属性如何解析（无对应数据标识或字段位置）
- 例如：物模型有 "signalStrength" 属性，但协议文档中未提及信号强度字段

**情况C：数据类型不匹配**
- 协议中字段的数据类型与物模型定义的类型明显不兼容
- 例如：协议中是4字节HEX整数，物模型却定义为布尔类型

---

**当发现资料不足时，必须停下来询问用户**：

```
⚠️ 协议资料与物模型映射存在以下问题，需要您补充或确认：

【问题1：协议字段无物模型对应】
协议中的以下数据字段在物模型中找不到对应属性：
- 数据标识 901F（累计用量）→ 物模型中无匹配属性
- 数据标识 9022（信号强度）→ 物模型中无匹配属性

【问题2：物模型属性无协议来源】
物模型中的以下属性在协议文档中未找到对应字段：
- batteryLevel → 协议中无此字段说明

请选择处理方式：
1. 【补充物模型】我已更新物模型，请重新分析（上传新的物模型资料）
2. 【补充协议资料】我提供协议字段的详细说明（文字描述字段含义和数据格式）
3. 【确认忽略】忽略无法映射的字段，继续生成编解码器
4. 【修正映射】某些字段其实是对应的，只是命名不同（如 901F 对应的是 flowRate）
```

---

**⚠️ 重要规则（必须人工确认，不可自动忽略）**：

1. **发现映射问题后必须暂停**，等待用户回复，**不得自动继续生成代码**
2. **必须人工确认**：向用户展示映射问题后，**必须等待用户明确回复**处理方案，严禁超时自动忽略
3. 用户选择后按对应方式处理：
   - 选1（补充物模型）：要求用户上传更新后的物模型，重新执行第3.2节
   - 选2（补充协议资料）：要求用户提供字段说明，手动建立映射关系
   - 选3（确认忽略）：记录忽略的字段，继续下一步
   - 选4（修正映射）：根据用户的对应关系修正映射表，重新检查
4. **必须确保核心字段有映射**：设备编码、时间戳、主要业务数据（如累计用量）等关键字段必须有明确的物模型对应，否则生成的编解码器无法正常使用
5. 如果用户坚持忽略关键字段的映射问题，需在生成的代码注释中注明，并提醒用户可能影响平台数据展示

> 🚫 **严禁**：映射检查环节**禁止设置超时自动忽略**，必须等待用户明确回复后才能继续

---

**映射确认表示例**（询问用户前展示）：

```
已建立的协议-物模型映射关系：

| 协议字段 | 数据格式 | 物模型属性标识符 | 状态 |
|---------|---------|-----------------|------|
| 数据标识 901F | 4字节HEX | cumulativeUsageM3 | ✅ 已映射 |
| 数据标识 9020 | 2字节BCD | batteryVoltageV | ✅ 已映射 |
| 数据标识 9021 | 7字节BCD | realTime | ✅ 已映射 |
| 数据标识 9022 | 1字节INT | （无对应属性） | ⚠️ 待确认 |
| 设备时间字段 | 6字节BCD | （无对应属性） | ⚠️ 待确认 |

请确认上述映射是否正确？如有问题请指出，确认无误后将继续生成代码。
```

### 4. 生成代码结构

创建项目目录结构：

```
{device}-codec/
├── lib/
│   └── dandelion-common-codec-2.2-SNAPSHOT.jar  # 自动复制
├── src/main/java/protocol/{protocol}/
│   ├── {Device}Codec.java          # 主编解码器类，实现 AccessProtocolModel
│   ├── {Device}DataCodec.java      # 数据编解码工具类
│   ├── CodecUtils.java             # 编解码工具类
│   ├── DecodedMessage.java         # 标准解码数据格式（重要！）
│   ├── {Report}Entity.java         # 上报数据实体类
│   └── message/
│       ├── {Device}Message.java    # 消息实体
│       └── MessageType.java        # 消息类型枚举
├── src/test/java/protocol/{protocol}/
│   └── {Device}CodecTest.java      # 测试类（仅用于开发调试）
└── pom.xml                         # Maven配置（已配置 maven.test.skip=true）
```

**⚠️ 目录规范**：
- 测试类**必须**放在 `src/test/java/` 下，**绝不能**放在 `src/main/java/` 下
- `src/main/java/` 只放正式代码，测试代码放 `src/test/java/`

### 5. 实现 DecodedMessage 数据格式

**重要**：所有解码器必须返回 `DecodedMessage` 对象，包含以下字段：

```java
public class DecodedMessage {
    private String type;           // 消息类型，2种取值（见下方）
    private String tenantCode;     // 租户编号（平台自动填充，编解码器无需赋值）
    private String deviceCode;     // 设备编号
    private boolean confirmable;   // 平台收到报文后是否需要立刻应答（根据协议资料确定）
    private Object data;           // 解码后的具体数据（JSONObject 或 JSONObject 的嵌套结构）
}
```

#### type 字段判断规则

解码后 `type` **只有 2 种取值**，需根据报文内容自动判断：

| type 值 | 说明 | 适用场景 |
|---------|------|---------|
| `device_report` | 设备上报属性数据 | 单设备属性上报 |
| `gateway_report` | 网关批量上报属性数据 | 网关代理多设备上报 |

📎 详见 **`references/data-format-reference.md`**（含完整 type 表格 + data 格式 JSON 示例）
📎 详见 **`references/decode-message-formats.md`** 第十节（DecodedMessage 完整格式 + DTO 格式）

> **最常用的是 `device_report`**，大多数物联网设备只需实现此类型。
> **当 confirmable=true 时**（仅 device_report/gateway_report 支持），平台会自动调用 encode() 生成 ACK 应答帧。

#### data 字段格式规范

⚠️ **重要：data 中的键名必须与物模型属性标识符完全一致**

**device_report 格式**：
```json
{
  "data": {
    "temperature": "25.5",
    "humidity": "60"
  },
  "timestamp": 1678901234567
}
```
- `data` 对象内的键名（如 `temperature`、`humidity`）**必须**与物模型中的属性标识符**完全一致**
- 所有属性值均应为**字符串**类型
- `timestamp` 为毫秒级时间戳

**gateway_report 格式**：
```json
{
  "device1": [
    { "ts": 1678901234567, "values": {"temperature": "25.5"} }
  ],
  "device2": [
    { "ts": 1678901234567, "values": {"pressure": "1013"} }
  ]
}
```
- `values` 对象内的键名**必须**与物模型中的属性标识符**完全一致**
- 每个子设备的 key 为该设备的设备编号（deviceCode）

📎 详见 **`references/data-format-reference.md`** 和 **`references/decode-message-formats.md`**

### 6. 实现 AccessProtocolModel 接口

主编解码器类必须实现 `AccessProtocolModel` 接口，接口完整路径：

```java
import com.inspur.dandelion.framework.common.codec.jar.AccessProtocolModel;
```

该接口定义了两个必须实现的方法：

```java
public interface AccessProtocolModel {
    // 解码：将设备上报的字节数据解析为 DecodedMessage JSON字符串
    // 平台调用方式: protocolModel.decode(topic, payload)
    //   - topic：租户编码或包含租户编码的字符串
    //   - payload：设备上报的原始字节数组（byte[]）
    ExecuteJarResult decode(String topic, byte[] payload);
    
    // 编码：将平台下发的指令编码为字节数组
    // 平台调用方式: protocolModel.encode(new Object[]{jsonString})
    //   - deviceMessage[0] = JSON字符串（根据 messageType 区分不同格式）
    ExecuteJarResult encode(Object[] deviceMessage);
}
```

#### 6.0 decode() 方法 —— 解码入口 ⚠️ 核心

**平台调用 decode() 的方式**：
- **参数1** `topic`：租户编码或包含租户编码的字符串
- **参数2** `payload`：设备上报的原始字节数组（byte[]）

**不同协议的输入格式差异**：

| 协议 | 输入格式 | 说明 |
|------|---------|------|
| TCP/UDP/CoAP/LwM2M/TCP客户端 | `byte[]` | 原始字节数据 |
| MQTT | `byte[]` | MQTT消息的原始payload |
| AEP/OneNET HTTP | `byte[]` | JSON字符串转换的字节数组 |
| HTTP | `byte[]` | JSON字符串转换的字节数组，topic格式为 "?/?/?/custom" |

📎 **详细输入格式参考**：`references/decode-message-formats.md` 第 1-9 节

**decode() 返回值**：
- 必须返回 `DecodedMessage` 对象的 JSON 字符串
- 通过 `result.setResult(JSON.toJSONString(decodedMessage))` 设置
- 格式示例：
```json
{
  "type": "device_report",
  "deviceCode": "device123",
  "confirmable": true,
  "data": {
    "timestamp": 1678901234567,
    "data": {
      "temperature": "25.5"
    }
  }
}
```

#### 6.1 encode() 方法 —— 必须处理的所有消息场景 ⚠️ 核心

平台会在以下 **3 种消息场景** 调用 `encode()` 方法，编解码器**必须全部处理**。

**不同协议的输入消息格式基本一致，但返回值类型有差异**（特别是 AEP/OneNET HTTP 协议）。

📎 **消息格式参考**：`references/encode-message-formats-detailed.md` - 9种协议的完整消息格式说明（按协议组织）

📎 **平台 DTO 类参考**（属性设置/命令下发的消息结构）：
- `references/GatewayWritePropertyMessage.java` - 属性设置消息 DTO（writeProperty 场景）
- `references/GatewayCommandMessage.java` - 命令下发消息 DTO（command 场景）

---

##### 按返回值类型分组（简化实现）

为减少编码复杂度，将 **9种协议按 encode() 返回值类型** 分为 **3组**，每组使用通用模板：

```
┌─────────────────────────────────────────────────────────────────────────┐
│  分组                       │  包含协议                          │ 返回值类型        │
├─────────────────────────────────────────────────────────────────────────┤
│  【组1】字节数组组          │  TCP、UDP、CoAP、MQTT、TCP客户端   │  byte[]           │
│  （最常用，占80%以上场景）  │                                    │  编码后的协议帧   │
├─────────────────────────────────────────────────────────────────────────┤
│  【组2】LwM2M 专用组        │  LwM2M                             │  DownlinkRequest  │
│                            │                                    │  LwM2M下行请求    │
├─────────────────────────────────────────────────────────────────────────┤
│  【组3】HTTP API 组         │  AEP、OneNET、HTTP                 │  JSONObject       │
│                            │                                    │  HTTP调用信息     │
└─────────────────────────────────────────────────────────────────────────┘
```

**组1：字节数组组（TCP/UDP/CoAP/MQTT/TCP客户端）**
- 适用协议：TCP、UDP、CoAP、MQTT、TCP客户端（5种协议）
- 统一返回值：`byte[]`（编码后的协议帧字节数组）
- 属性设置/命令下发：`GatewayWritePropertyMessage`/`GatewayCommandMessage` JSON 输入
- 上报应答：TCP/CoAP 使用 DecodedMessage JSON；MQTT 使用 `{"code":"0","messageType":"reply"}`

**组2：LwM2M 专用组**
- 适用协议：LwM2M（1种协议）
- 返回值：`DownlinkRequest` 对象（LwM2M 专用下行请求）
- 上报应答：LwM2M 内置确认机制，通常无此场景

**组3：HTTP API 组（AEP/OneNET/HTTP）**
- 适用协议：AEP、OneNET、HTTP（3种协议）
- 返回值：**JSONObject**（包含 `apiUrl`、`httpMethod`、`body` 等 HTTP API 调用信息）
- **不是** `byte[]`，需构造 HTTP 请求信息返回

> **简化原则**：
> 1. 同一组内的协议共用代码逻辑，只需判断返回值类型
> 2. 组内差异通过条件分支处理（如 MQTT 的应答格式不同）
> 3. 优先实现组1（字节数组组），覆盖大多数场景

---

##### 消息场景判断逻辑

| # | 场景 | 判断方式 | 触发协议 |
|---|------|----------|---------|
| **1** | **上报应答(ACK)** | 无 `messageType` 且 `confirmable==true`（TCP/CoAP），或 `messageType=="reply"`（MQTT） | TCP、CoAP、MQTT |
| **2** | **属性设置(writeProperty)** | `messageType=="writeMessage"` + `properties` | 所有协议 |
| **3** | **命令下发(command)** | `messageType=="command"` + `command` + `input` | 所有协议 |

#### 6.2 encode() 实现模板

📎 **详见 `assets/EncodeTemplate.java`**（完整 Java 模板代码，覆盖 3 种消息分支）

核心逻辑：
1. 首先按**协议类型**确定返回值格式（byte[] / DownlinkRequest / JSONObject）
2. 然后按 `messageType` 判断具体场景
3. 分别调用 `buildAckFrame()` / `buildReplyFrame()` / `buildWritePropertyFrame()` / `buildCommandFrame()`

> **AEP/OneNET HTTP 协议特殊处理**：属性设置和命令下发场景需要返回包含 `apiUrl`、`httpMethod`、`body` 等 API 调用信息的 JSON 对象，而非 byte[]。
> 
> 详见：`references/encode-message-formats-detailed.md` 第 6、7 节 - AEP/OneNET 协议详细格式

#### 6.3 encode() 返回值规范

- **TCP/UDP/CoAP**：`result.setResult(byte[])` 返回编码后的**字节数组**
- **MQTT**：`result.setResult(byte[])` 或字符串（透传模式返回消息内容）
- **LWM2M**：返回 `DownlinkRequest` 对象
- **AEP**：返回 **JSON 对象**，包含 `apiUrl`、`httpMethod`、`apiVersion`、`queryParams`、`headers`、`body`
- 平台会调用 `JsFormatUtils.formatScriptObjectMirror2Byte(executeResult.get())` 转换结果
- setResult 设为 byte[] 最安全；设为 HEX 字符串需额外转换，可能失败

### 7. 测试验证流程 ⚠️ 强制环节，不可跳过

**⚠️ 这是强制环节：打包 JAR 之前必须经过测试验证，并等待用户确认测试结果正确。**

**未经过测试验证和用户确认，绝对禁止打包 JAR！**

**测试验证提供两种方式，优先使用在线测试：**

#### 7.1 🧪 在线测试（优先方式）

代码生成后，**立即生成一个在线测试 HTML 页面**，用户无需编译即可验证解码逻辑：

**生成步骤**：

1. **生成测试页面**：在编解码器项目目录下创建 `test.html` 文件
2. **用 JavaScript 实现解码逻辑**：将 Java 解码逻辑翻译为等效的 JavaScript 函数
3. **提供交互界面**：包含报文输入框、解码按钮、结果展示区

**测试页面功能**：

```
┌──────────────────────────────────────────────────────────┐
│  🧪 编解码器在线测试                                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  📥 输入报文（HEX）                                       │
│  ┌──────────────────────────────────────────────────┐    │
│  │ 68 01 00 00 00 00 00 81 0A 90 1F 00 00 01 23... │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  [ 🔍 测试解码 ]                                         │
│                                                          │
│  📤 解码结果（JSON）                                      │
│  ┌──────────────────────────────────────────────────┐    │
│  │ {                                                │    │
│  │   "type": "device_report",                      │    │
│  │   "deviceCode": "01170000610114002019XXXX",     │    │
│  │   "confirmable": true,                          │    │
│  │   "data": {                                     │    │
│  │     "data": {                                   │    │
│  │       "cumulativeUsageM3": "123.45",            │    │
│  │       "batteryVoltageV": "3.103"                │    │
│  │     },                                          │    │
│  │     "timestamp": 1678901234567                  │    │
│  │   }                                             │    │
│  │ }                                                │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  ✅ 验证清单                                              │
│  ✔ type 正确（device_report/gateway_report）             │
│  ✔ deviceCode 提取正确                                   │
│  ✔ data 键名与物模型一致                                  │
│  ✔ 无多余字段                                            │
│  ✔ 属性值为字符串类型                                     │
│  ✔ timestamp 为毫秒级时间戳                               │
│                                                          │
│  💡 可多次输入不同报文测试，确认无误后回复"正确"           │
└──────────────────────────────────────────────────────────┘
```

**⚠️ JavaScript 解码逻辑翻译规则**：

由于在线测试使用 JavaScript 而非 Java，需将 Java 解码逻辑**等效翻译**：

| Java 操作 | JavaScript 等效实现 |
|-----------|-------------------|
| `byte[]` + 位运算 | `Uint8Array` + 位运算 |
| BCD 解码 | 等效 BCD 解析函数 |
| `Integer.parseInt(hex, 16)` | `parseInt(hex, 16)` |
| `String.format("%02X", b)` | `b.toString(16).padStart(2, '0').toUpperCase()` |
| CRC/CS 校验 | 等效校验算法 |
| `JSONObject` | 原生 `Object` |
| `log.info/warn/error` | `console.log/warn/error` |

**关键注意事项**：
1. **解码逻辑必须与 Java 代码等效**：同一段报文在在线测试和最终 JAR 中必须得到相同的解码结果
2. **测试页面仅用于验证**：最终部署到平台的仍然是 Java 编解码器 JAR
3. **多报文测试**：用户可在页面中多次输入不同报文进行测试
4. **真实报文验证**：用户可随时输入真实设备报文进行验证

---

#### 7.2 编译测试（备选方式）

如果在线测试无法满足需求（如涉及复杂的加密解密、Native 方法调用等），使用编译测试作为备选：

**询问用户提供示例报文数据**：
- **原始报文**：HEX 格式的原始数据帧
- **报文说明**：该报文代表什么数据（如：水表读数上报）
- **期望结果**：期望解析出的关键字段值

**编写测试代码**：

测试类**必须放在 `src/test/java/` 下**（不是 src/main）：

📎 **详见 `assets/TestTemplate.java`**（测试代码骨架）

**执行测试并验证输出**：

```bash
# 编译项目
cd {device}-codec
mvn clean compile

# 运行测试（需要先把依赖复制到 classpath）
mvn dependency:copy-dependencies -DoutputDirectory=target/deps
java -cp "target/classes;target/deps/*;lib/dandelion-common-codec-2.2-SNAPSHOT.jar" \
     protocol.{protocol}.{Device}CodecTest
```

**注意**：`dependency:copy-dependencies` 会清除 target/classes 缓存，如果出现 `ClassNotFoundException`，先重新 `mvn compile` 再运行测试。

---

#### 7.3 用户确认 ⚠️ 强制环节，必须等待用户确认

**向用户展示测试结果：**
- 原始报文
- 解码后的 DecodedMessage JSON 格式
- 关键字段解析结果
- ⚠️ **data 中的键名与物模型属性标识符对比检查**

**测试验证清单（展示给用户前自检）：**
```
✅ 解码是否成功（无异常）
✅ type 是否正确（device_report/gateway_report）
✅ deviceCode 是否提取正确
✅ data.data 中的键名是否与物模型属性标识符完全一致（大小写、下划线等）
✅ data.data 中是否只包含物模型中已定义的属性（无多余字段）
✅ 属性值是否为字符串类型
✅ timestamp 是否为毫秒级时间戳
```

**询问用户确认：**
```
========================================
📋 测试结果如下：
========================================

原始报文：68 01 00 00 00 00 00 81 0A 90 1F 00 00 01 23 45 67 89 ...

type: device_report
deviceCode: 01170000610114002019XXXX
confirmable: true

data:
{
  "data": {
    "cumulativeUsageM3": "123.45",
    "batteryVoltageV": "3.103",
    ...
  },
  "timestamp": 1678901234567
}

========================================
请确认以下内容：

1. 解码结果是否正确？（字段值是否符合预期）
2. data 中的键名是否与物模型属性标识符完全一致？
   - 物模型属性：cumulativeUsageM3, batteryVoltageV, ...
   - data 中的键：cumulativeUsageM3, batteryVoltageV, ...
   - 如果键名不一致，平台将无法识别数据！
3. data 中是否只包含物模型中已定义的属性（无多余字段）？
   - 多余字段（物模型中不存在的属性）会导致平台报错！

✅ 如果都正确，回复"正确"或"打包吧"，我将继续打包 JAR 文件
❌ 如果有问题，请指出具体问题，我将修改后重新测试
💡 可在在线测试页面输入更多报文验证（如需可刷新页面重新测试）
========================================
```

**⚠️ 必须严格遵守以下规则（违反将导致生成错误的编解码器，必须人工确认）**：

1. **展示测试结果后必须停下来等待用户回复，不得自动继续执行后续步骤**
2. **绝对禁止**在展示测试结果后未经用户确认就直接执行 `mvn clean package` 打包
3. **必须人工确认**：向用户展示测试结果后，**必须等待用户明确回复**（如"正确"、"可以"、"没问题"、"打包吧"等），**严禁超时自动继续打包**
4. 用户可能会提供一段**真实设备报文**要求重新测试：
   - **在线测试方式**：用户在在线测试页面中直接输入新报文即可，无需重新编译
   - **编译测试方式**：用真实报文替换测试类中的示例数据，重新编译运行并展示结果
5. 只有当用户**明确确认解码结果正确**后，才能进入下一步打包 JAR
6. 如果用户指出解码有问题，需要根据反馈修改代码、重新测试、再次确认，循环直到用户满意为止
7. **禁止绕过测试环节**：不得以"代码看起来正确"、"我很有信心"等理由跳过用户确认直接打包

> 🚫 **严禁**：测试确认环节**禁止设置超时自动打包**，必须等待用户明确回复后才能继续


### 8. 打包 JAR ⚠️ 必须有用户明确确认才能执行

**🚫 严禁未经测试确认直接打包！**

**只有在满足以下条件后才能打包：**
1. ✅ 已完成第7步的测试验证流程
2. ✅ 已向用户展示测试结果
3. ✅ **用户已明确回复确认**（如"正确"、"可以"、"没问题"、"打包吧"等）

**未收到用户明确确认前，绝对禁止执行 `mvn clean package`！**

> 🚫 **严禁超时自动打包**：即使等待时间较长，也**必须**获得用户明确确认后才能打包

**用户确认测试结果正确后**，执行打包：

#### 8.1 JAR 包命名规范 ⚠️ 重要

**JAR 包的 artifactId（文件名）必须使用编解码器类的全路径名（点号替换为连字符）**。

例如：
- 编解码器类：`protocol.mn100.MN100Codec`
- artifactId：`protocol.mn100.MN100Codec`
- 最终 JAR 文件名：`protocol.mn100.MN100Codec-1.0.jar`

> **原因**：平台通过类路径名加载编解码器 JAR，JAR 文件名必须与类全限定名匹配，否则平台无法识别和加载该编解码器。

#### 8.2 POM 配置中的 artifactId

```bash
cd {device}-codec
mvn clean package
```

POM 模板已配置 `maven.test.skip=true`，会自动跳过测试编译和执行，无需额外参数。

#### 8.3 验证打包结果

```bash
# 检查 JAR 是否生成
ls target/{artifactId}-1.0.jar

# 验证 JAR 内容（确认包含所有业务 class，不包含第三方依赖）
jar tf target/{artifactId}-1.0.jar
```

#### 8.4 打包注意事项

1. **默认使用 maven-jar-plugin**，只打包 `src/main` 下的业务代码，**不包含第三方依赖**（平台 classpath 已有）
2. **JAR 大小通常 20~50KB**，如果超过 1MB 说明可能误打包了依赖
3. **system scope 依赖不会被打入 JAR**，`dandelion-common-codec` 由平台提供
4. **不要使用 fat JAR**（assembly/shade），平台会冲突
5. **如果打包失败**，检查：
   - test 目录代码是否有编译错误 → 应已在 POM 中跳过
   - `src/main` 下是否误放了测试类 → 移到 `src/test`
   - lib 目录下的 jar 是否存在

## DecodedMessage 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | String | 是 | 消息类型，**2 种取值**（见上方 type 判断规则表） |
| tenantCode | String | 否 | 租户编号（平台自动填充，编解码器**无需赋值**） |
| deviceCode | String | 是 | 设备唯一标识（网关模式下为网关编号） |
| confirmable | boolean | 否 | 平台收到报文后是否需要立刻应答，**根据协议资料确定**。当设备上报报文要求应答时设为 true，平台会自动调用 encode() 生成 ACK 应答帧 |
| data | Object | 是 | 解码后的具体业务数据，格式因 type 而异（见上方 type 表格） |

> **注意**：DecodedMessage 类**不包含** `timestamp` 字段。对于 `device_report` 类型，timestamp 必须放在 `data` 的内层结构中（即 `{"data": {"data": {...}, "timestamp": 1637205296895}}`），**不能**放在 DecodedMessage 的根级别。

## 代码模板说明

### 1. DecodedMessage 模板 (DecodedMessageTemplate.java)

- 标准解码数据格式
- 包含 type、deviceCode、data 等必填字段
- 所有解码器必须使用此格式

### 2. 主编码器类模板 (CodecTemplate.java)

- 实现 `AccessProtocolModel` 接口
- 支持多种平台数据格式解析（AEP/OneNET/TCP）
- decode 方法返回 `DecodedMessage` JSON字符串
- 包含完整的 decode/encode 方法框架
- 集成日志记录和异常处理

### 3. 数据编解码工具类 (CodecUtilsTemplate.java)

提供通用工具方法：
- `decode()` - 返回 `DecodedMessage` 对象
- `byteArrayToHexString()` - 字节数组转HEX字符串
- `hexStringToByteArray()` - HEX字符串转字节数组
- `parseBcd()` / `bcdToString()` - BCD码解析
- `calcCrc16()` / `calcCs()` - CRC和累加和校验
- `validateFrame()` - 帧校验

### 4. 实体类模板 (EntityTemplate.java)

定义上报数据结构：
- 设备编码、功能码、数据域
- JSON 转换方法
- 数据提取逻辑

## 依赖说明

### pom.xml 关键配置

📎 **详见 `assets/pom_template.xml`**（完整 Maven 配置模板）

**关键点**：
- **Java 11** - 编解码器使用 Java 11 编译（`<java.version>11</java.version>`）
- `maven.test.skip=true` 同时跳过测试编译和执行，避免 test 代码问题阻断打包
- 不需要 assembly/shade/fat-jar 插件，平台 classpath 已有所有运行时依赖
- JAR 只包含业务 class（20~50KB）

## 平台适配说明

### AEP 平台
数据格式：`{"payload": "base64encodeddata"}`
解析方式：Base64解码后解析

### OneNET 平台
数据格式：`{"msg": {"data": "base64orhex"}}`
解析方式：根据内容判断Base64或HEX解码

### TCP/UDP 直连
数据格式：原始字节流
解析方式：直接按协议帧格式解析

## 注意事项

1. **必须提供两份资料**：协议文档 + 平台物模型，缺一不可。物模型决定了解码后 data 中属性的 key 命名
2. **⚠️ 属性键名必须与物模型属性标识符严格一致（关键）**：
   - 解码后 `DecodedMessage.data.data` 中的键名（key）必须与物模型中的属性标识符（identifier）**完全一致**
   - 包括大小写、下划线、数字等都必须一致，**不能有任何差异**
   - 错误示例：物模型中是 `cumulativeUsageM3`，不能使用 `CumulativeUsageM3`、`cumulative_usage_m3`、 `累计用量` 等
   - 如果键名不一致，平台将无法识别和展示设备数据，导致"上报成功但数据不可见"
3. **⚠️ 禁止上报物模型中不存在的属性（关键）**：
   - **只上报物模型中已定义的属性**，协议中解析出但物模型中没有对应属性的字段**必须忽略**，不得放入 data
   - 多余字段会导致平台无法识别，可能引发数据存储异常或平台报错
   - 如果用户需要上报某些字段，必须先确保物模型中已定义对应的属性标识符
4. **⚠️ 映射完整性检查**：第3.3节是强制环节，当协议字段无法映射到物模型（或反之）时，**必须暂停并询问用户**，提供四种处理选项（补充物模型/补充协议资料/确认忽略/修正映射），不得自动跳过
5. **type 只有 2 种取值**：`device_report`(最常用)、`gateway_report`
6. **data 格式与 type 绑定**：每种 type 对应不同的 data 结构（见上方 type 判断规则表）
7. **属性值统一为 String**：data 中 values 内的所有属性值均应以字符串形式输出
8. **时间戳必须解析**：从报文中提取设备上报时间，转换为毫秒级时间戳
9. **标准数据格式**：所有解码器必须返回 DecodedMessage 格式（JSON字符串）
10. **⚠️ 测试验证 + 人工确认（强制）**：打包 JAR 前**必须**完成第7步测试验证流程（优先使用在线测试🧪），**必须等待用户明确确认**测试结果正确后才能打包。严禁未经用户确认直接打包！用户可能会提供真实报文要求重新测试，需支持多轮迭代
11. **依赖管理**：lib目录下的 `dandelion-common-codec-2.2-SNAPSHOT.jar` 必须存在
12. **日志记录**：使用 SLF4J 记录编解码过程中的关键信息
13. **日志规范**（重要）：decode/encode 方法**必须**打印开始和结束标记日志，方便平台排查问题
    - **decode 开始**：`log.info("====== {Device} decode start ======");`
    - **decode 结束**：`log.info("====== {Device} decode end ======");`
    - **decode 失败**：`log.error("====== {Device} decode failed ======", e);`
    - **encode 开始**：`log.info("====== {Device} encode start ======");`
    - **encode 结束**：`log.info("====== {Device} encode end ======");`（每个场景分支的 return 前都要打印）
    - **encode 失败**：`log.error("====== {Device} encode failed ======", e);`
    - CodecUtils.decode 入口也需打印：`log.info("CodecUtils.decode start, dataLen={}, hex={}", ...)` 和 `log.info("CodecUtils.decode end, type={}, deviceCode={}", ...)`
    - encode 各场景分支需打印场景名称：`log.info("Encode scenario: ACK / writeProperty / command")`
14. **异常处理**：捕获并记录编解码异常，返回友好的错误信息
15. **帧校验**：务必实现CRC/CS校验，确保数据完整性。但需注意**CRC 容错处理**：
    - 设备可能发送 CRC=0x0000 或 0xFFFF（不填充校验值），此时应跳过校验仅 WARN
    - 设备可能使用不同的 CRC 算法/初始值/多项式，导致校验不一致
    - **校验失败不应阻止帧解析**，应记录 WARN 日志后继续解析数据域
    - 推荐实现方式：`if (crc != 0x0000 && crc != calculated) { log.warn("..."); }` 而非直接抛异常
16. **decode() 输入格式因协议而异**（见第6.0节）：
    - TCP/UDP/CoAP/LwM2M/TCP客户端：原始字节数组
    - MQTT：MQTT消息的原始payload
    - AEP/OneNET HTTP/HTTP：JSON字符串转换的字节数组
    - 📎 详见 `references/decode-message-formats.md` 第 1-9 节
16. **encode() 必须处理 3 种消息场景**（见第6.1节）：
    - **场景1 - 上报应答(ACK)**：TCP/CoAP 传入完整 DecodedMessage JSON（`confirmable==true`，无 `messageType`）；MQTT 传入 `{"code":"0","messageType":"reply"}`
    - **场景2 - 属性设置(writeProperty)**：`messageType=="writeMessage"` + `device` + `properties`（所有协议通用）
    - **场景3 - 命令下发(command)**：`messageType=="command"` + `device` + `command` + `input`（所有协议通用）
    - **AEP 特殊**：属性设置/命令下发的输入中会额外包含 `productId`、`imei`、`MasterKey` 等字段
    - 如果 encode() 不处理这些类型，平台回复/下发时会报错
    - 📎 **协议分组详见**：`references/encode-message-formats-detailed.md`（按 TCP/UDP/MQTT/CoAP/LwM2M/AEP/OneNET/TCP客户端/HTTP 组织）
17. **内存管理**：使用 Netty ByteBuf 时注意 `ReferenceCountUtil.release()`
18. **打包规范**：测试类放 `src/test/java/`，正式代码放 `src/main/java/`，**严禁混淆**
19. **打包命令**：使用 `mvn clean package`（POM 已配置跳过测试），**不要用 assembly/shade 打 fat JAR**
20. **JAR 大小**：正常 20~50KB，超过 1MB 需检查是否误打包了第三方依赖
21. **JAR 命名规范**（重要）：artifactId 必须使用编解码器类的**全限定名**
    - 如类为 `protocol.mn100.MN100Codec`，则 artifactId 为 `protocol.mn100.MN100Codec`
    - 最终 JAR 文件名：`protocol.mn100.MN100Codec-1.0.jar`
    - 原因：平台通过类路径名加载编解码器 JAR，文件名不匹配会导致无法识别和加载
22. **encode() 返回值**（按协议区分）：
    - **TCP/UDP/CoAP/TCP客户端**：`result.setResult(byte[])` 返回编码后的字节数组
    - **MQTT**：返回 byte[] 或字符串
    - **LwM2M**：返回 DownlinkRequest 对象
    - **AEP/OneNET HTTP**：返回 JSON 对象（包含 `apiUrl`、`httpMethod`、`body` 等 API 调用信息），详见 `references/encode-message-formats-detailed.md` 第 6、7 节
    - **HTTP**：视具体情况，可能透传或不支持
    - 平台调用 `JsFormatUtils.formatScriptObjectMirror2Byte()` 转换结果
    - setResult 设为 byte[] 最安全；AEP/OneNET 场景必须返回 JSONObject
23. **流程连续性**（重要）：整个编解码器实现过程中**不允许中途突然停止**
    - 从收集协议信息 → **协议类型确认** → **分析映射（含资料不足询问）** → 生成代码 → 实现解码 → 实现编码 → **生成在线测试页面** → 测试确认 → 打包，必须**一气呵成完成所有步骤**
    - 每完成一个步骤后，**立即继续下一个步骤**，不要停下来问用户"是否继续"
    - 需要等待用户确认的节点（**必须人工确认，不可自动跳过**）：
      - **第2步：协议类型确认**（仅当用户未明确指定协议类型时需要等待确认；用户已明确指定时直接使用，无需询问）
      - **第3.3步：映射完整性检查**（资料不足时必须询问用户处理方案，**必须人工确认**，严禁自动忽略）
      - **第7.3步：测试结果确认**（必须等用户**明确确认**解码正确后才打包，严禁自动继续）
    - 如果遇到问题（编译错误、测试失败等），**自动修复并继续**，不要停下来等用户指示
    - 如果步骤较多，用简短的进度提示告知用户当前进展（如 "✅ 代码生成完成，继续实现编码逻辑..."），但不要因此停止
24. **强制人工确认环节**（⚠️ 关键）：
    - **第3.3节映射检查**：资料不足时**必须人工确认**处理方案，不可自动忽略
    - **第7.3节测试确认**：测试完成后**必须人工确认**结果正确，不可自动打包
    - 这两个环节关系到编解码器正确性，**严禁设置超时自动继续**
25. **在线测试页面**（🧪 新增）：
    - 代码生成后**立即生成**在线测试 HTML 页面（`test.html`）
    - 将 Java 解码逻辑**等效翻译**为 JavaScript，确保同一段报文得到相同结果
    - 用户可**多次输入不同报文**进行测试，无需编译
    - 在线测试仅用于验证，最终部署的仍是 Java 编解码器 JAR
    - 如果解码逻辑过于复杂（如加密解密、Native 调用），可退回到编译测试方式

## 参考资料（外部文档）

详细参考内容已拆分到 references/ 和 assets/ 目录，生成编解码器时按需查阅：

### 📖 参考文档（references/）

| 文档 | 内容 |
|------|------|
| **data-types-reference.md** | 平台数据类型与编解码格式参考（A.1~A.6） |
| **decode-message-formats.md** | 9种协议的解码器输入格式 + DecodedMessage 输出格式 |
| **encode-message-formats-detailed.md** | 9种协议的编码消息格式详细说明（按协议组织：TCP/UDP/MQTT/CoAP/LwM2M/AEP/OneNET/TCP客户端/HTTP） |
| **data-format-reference.md** | DecodedMessage data 字段格式规范 + type 2种取值表 |
| **GatewayCommandMessage.java** | 平台命令下发消息 DTO（encode() command 场景使用） |
| **GatewayWritePropertyMessage.java** | 平台属性设置消息 DTO（encode() writeProperty 场景使用） |

### 💻 代码模板（assets/）

| 文件 | 内容 |
|------|------|
| **EncodeTemplate.java** | encode() 完整实现模板（4种消息分支） |
| **TestTemplate.java** | 测试类骨架代码 |
| **DecodedMessageTemplate.java** | 标准解码数据格式类 |
| **CodecTemplate.java** | 主编解码器完整模板 |
| **CodecUtilsTemplate.java** | 工具类模板 |
| **EntityTemplate.java** | 实体类模板 |
| **pom_template.xml** | Maven配置模板 |

### 核心依赖（lib/）

- **dandelion-common-codec-2.2-SNAPSHOT.jar** — 编解码器接口定义（AccessProtocolModel / ExecuteJarResult / DecodedMessage 等）

