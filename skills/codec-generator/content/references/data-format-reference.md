# DecodedMessage data 字段格式规范

⚠️ **重要：data 中的所有键名必须与物模型属性标识符完全一致**

- 包括大小写、下划线、数字等都必须一致，**不能有任何差异**
- 示例：物模型中属性标识符是 `cumulativeUsageM3`，则 data 中必须是 `"cumulativeUsageM3": "123.45"`
- 错误示例（严格禁止）：`"CumulativeUsageM3"`、`"cumulative_usage_m3"`、`"累计用量"`
- 如果键名不一致，平台将无法识别和展示设备数据

---

解码后 `type` **只有 2 种取值**，每种 type 对应不同的 data 格式：

## type 判断规则表

| type | 说明 | 判断条件 | data 格式 |
|------|------|----------|-----------|
| `device_report` | 单设备属性数据上报 | 报文中只包含一个设备的属性数据 | 见下方格式1 |
| `gateway_report` | 网关聚合多设备上报 | 报文中包含多个子设备的数据 | 见下方格式2 |

> **最常用的是 `device_report`**，大多数物联网设备只需实现此类型。
> **当 confirmable=true 时**（仅 device_report/gateway_report 支持），平台会自动调用 encode() 生成 ACK 应答帧。

---

## 格式 1：device_report 的 data

单个设备的属性键值对 + timestamp：

```json
{
    "data": {
        "E_Craft_TT_Comp": "24",
        "E_TotalRunTime": "12372",
        "E_Craft_Ideal_Cycle_Time": "993",
        "E_A": "87"
    },
    "timestamp": 1637205296895
}
```

- `data` 内部是 `String` 类型的键值对，key 为**物模型属性标识符**，value 为字符串形式的属性值
- **key 必须与物模型中的属性标识符完全一致**（大小写、下划线等）
- **⚠️ 禁止上报物模型中不存在的属性**：data 中只能包含物模型中已定义的属性，多余字段必须忽略
- `timestamp` 为毫秒级时间戳，从报文中解析出的设备上报时间

---

## 格式 2：gateway_report 的 data

多个设备的上报数据列表，以设备编号为 key：

```json
{
    "DeviceDemo": [{
        "ts": 1598001814513,
        "values": {
            "temperature": "39",
            "humidity": "21"
        }
    }, {
        "ts": 1598001814622,
        "values": {
            "temperature": "38",
            "humidity": "20"
        }
    }],
    "DeviceDemo2": [{
        "ts": 1598001814513,
        "values": {
            "temperature": "38",
            "humidity": "26"
        }
    }]
}
```

- 每个设备的 key 为该子设备的设备编号（deviceCode）
- 每个子设备的数据是一个数组，包含一条或多条历史记录
- 每条记录包含 `ts`（毫秒时间戳）和 `values`（属性键值对，value 均为 String）
- `values` 中的 key 必须与物模型中的属性标识符**完全一致**
- **⚠️ 禁止上报物模型中不存在的属性**：`values` 中只能包含物模型中已定义的属性，多余字段必须忽略
