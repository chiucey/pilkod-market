# 9种协议的解码器消息格式详细说明

## 一、TCP协议（服务端）

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：原始字节数据
- **传入参数**：
  - `data`：原始字节数据
  - `topic`：租户编码或租户编码:客户端地址

## 二、UDP协议

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：原始字节数据
- **传入参数**：
  - `data`：原始字节数据
  - `topic`：租户编码或租户编码:客户端地址

## 三、MQTT协议

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：原始MQTT消息payload
- **传入参数**：
  - `mqttMessage.getPayload()`：MQTT消息的原始payload
  - `topic`：MQTT消息的topic

## 四、CoAP协议

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：原始CoAP请求payload
- **传入参数**：
  - `data`：原始字节数据
  - `topic`：租户编码或租户编码:客户端地址

## 五、LwM2M协议

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：原始LwM2M消息payload
- **传入参数**：
  - `data`：原始字节数据
  - `topic`：租户编码或租户编码:客户端地址

## 六、AEP协议（电信平台HTTP）

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：JSON字符串的字节数组
- **传入参数**：
  - `message.toString().getBytes()`：JSON字符串转换的字节数组
  - `topic`：租户编码

## 七、OneNet协议（移动平台HTTP）

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：JSON字符串的字节数组
- **传入参数**：
  - `message.toString().getBytes()`：JSON字符串转换的字节数组
  - `topic`：租户编码

## 八、TCP客户端协议

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：原始字节数据
- **传入参数**：
  - `data`：原始字节数据
  - `topic`：租户编码或租户编码:客户端地址

## 九、HTTP协议

### 进入解码器的消息格式
- **消息格式类型**：字节数组 (byte[])
- **格式**：JSON字符串的字节数组
- **传入参数**：
  - `message.toString().getBytes(StandardCharsets.UTF_8)`：JSON字符串转换的字节数组
  - `topic`：格式为 "?/?/?/custom" 的字符串（其中第一个?为"device"或"gateway"）

## 十、相关DTO格式

### MqttMessageBody格式
```json
{
  "timestamp": 1678901234567,
  "data": {
    "temperature": "25.5",
    "humidity": "60"
  }
}
```

### GatewayTs格式
```json
{
  "ts": 1678901234567,
  "values": {
    "temperature": "25.5",
    "humidity": "60"
  }
}
```

### 网关批量上报格式
```json
{
  "device1": [
    {
      "ts": 1678901234567,
      "values": {
        "temperature": "25.5",
        "humidity": "60"
      }
    },
    {
      "ts": 1678901235567,
      "values": {
        "temperature": "25.6",
        "humidity": "59"
      }
    }
  ],
  "device2": [
    {
      "ts": 1678901234567,
      "values": {
        "pressure": "1013",
        "battery": "80"
      }
    }
  ]
}
```

### DecodedMessage格式
```json
{
  "type": "device_report",
  "deviceCode": "device123",
  "confirmable": true,
  "data": {
    "timestamp": 1678901234567,
    "data": {
      "temperature": "25.5",
      "humidity": "60"
    }
  }
}
```

### DecodedMessageType类型
- `device_report`：设备上报属性数据
- `gateway_report`：网关批量上报属性数据

## 十一、解码结果格式

所有协议的解码结果格式均为`DecodedMessage`对象的JSON字符串，包含上述类型。
