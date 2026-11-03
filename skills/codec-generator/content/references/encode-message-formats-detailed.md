# 9种协议的编码消息格式详细说明

## 一、TCP协议（服务端）

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`GatewayWritePropertyMessage` JSON字符串
    ```json
    {
      "messageType": "writeMessage",
      "device": "device123",
      "messageId": "msg123",
      "properties": {
        "temperature": "25.5",
        "humidity": "60"
      }
    }
    ```
  - **命令下发**：`GatewayCommandMessage` JSON字符串
    ```json
    {
      "messageType": "command",
      "device": "device123",
      "messageId": "msg123",
      "command": "restart",
      "input": {
        "delay": "5"
      }
    }
    ```
- **编码后需要的格式**：字节数组（byte[]）

### 2. 消息应答场景（confirmable=true）
- **传入编码器的消息格式**：解码后的原始JSON字符串
  ```json
  {
    "type": "device_report",
    "deviceCode": "device123",
    "data": {
      "temperature": "25.5",
      "humidity": "60"
    },
    "confirmable": true
  }
  ```
- **编码后需要的格式**：字节数组（byte[]）

## 二、UDP协议

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`GatewayWritePropertyMessage` JSON字符串
  - **命令下发**：`GatewayCommandMessage` JSON字符串
  - 格式同TCP协议
- **编码后需要的格式**：字节数组（byte[]）

### 2. 消息应答场景（confirmable=true）
- **传入编码器的消息格式**：解码后的原始JSON字符串
- **编码后需要的格式**：字节数组（byte[]）

## 三、MQTT协议

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`MqttGatewayWritePropertyMessage` JSON字符串
    ```json
    {
      "device": "device123",
      "properties": {
        "temperature": "25.5",
        "humidity": "60"
      }
    }
    ```
  - **命令下发**：`MqttGatewayCommandMessage` JSON字符串
    ```json
    {
      "device": "device123",
      "command": "restart",
      "input": {
        "delay": "5"
      }
    }
    ```
- **编码后需要的格式**：字节数组（byte[]）

### 2. 消息应答场景（confirmable=true）
- **传入编码器的消息格式**：
  ```json
  {
    "code": "0",
    "messageType": "reply"
  }
  ```
- **编码后需要的格式**：字节数组（byte[]）

## 四、CoAP协议

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`GatewayWritePropertyMessage` JSON字符串
  - **命令下发**：`GatewayCommandMessage` JSON字符串
  - 格式同TCP协议
- **编码后需要的格式**：字节数组（byte[]）

### 2. 消息应答场景（confirmable=true）
- **传入编码器的消息格式**：解码后的原始JSON字符串
- **编码后需要的格式**：字节数组（byte[]）

## 五、LwM2M协议

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`GatewayWritePropertyMessage` JSON字符串
  - **命令下发**：`GatewayCommandMessage` JSON字符串
  - 格式同TCP协议
- **编码后需要的格式**：`DownlinkRequest`对象（LwM2M下行请求对象）

### 2. 消息应答场景（confirmable=true）
- **说明**：未找到确认消息处理实现，可能使用LwM2M内置的确认机制

## 六、AEP协议（电信平台HTTP）

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`GatewayWritePropertyMessage` JSON字符串
  - **命令下发**：`GatewayCommandMessage` JSON字符串
  - 格式同TCP协议
- **编码后需要的格式**：包含HTTP请求信息的JSON对象
  ```json
  {
    "apiUrl": "/aep_device_command/command",
    "httpMethod": "POST",
    "apiVersion": "20190712225145",
    "queryParams": {
      "MasterKey": "xxx"
    },
    "headers": {
      "MasterKey": "xxx"
    },
    "body": {
      "deviceId": "xxx",
      "productId": "xxx",
      "operator": "system",
      "content": "xxx",
      "ttl": 3600
    }
  }
  ```

### 2. 消息应答场景（confirmable=true）
- **说明**：无应答场景（HTTP协议是请求-响应模式）

## 七、OneNet协议（移动平台HTTP）

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`GatewayWritePropertyMessage` JSON字符串
  - **命令下发**：`GatewayCommandMessage` JSON字符串
  - 格式同TCP协议
- **编码后需要的格式**：包含HTTP请求信息的JSON对象
  ```json
  {
    "apiUrl": "/nb-iot/execute",
    "httpMethod": "POST",
    "queryParams": {
      "imei": "xxx",
      "obj_id": "3",
      "obj_inst_id": "0",
      "res_id": "11",
      "timeout": "30"
    },
    "headers": {
      "authorization": "version=2022-05-01&res=products/xxx&et=1678901234&method=sha1&sign=xxx"
    },
    "body": {
      "args": "{\"value\":1}"
    }
  }
  ```

### 2. 消息应答场景（confirmable=true）
- **传入编码器的消息格式**：`GatewayCommandMessage` JSON字符串
  ```json
  {
    "messageType": "reply",
    "device": "device123",
    "command": "confirmMessageCommand",
    "messageId": "-1",
    "input": {
      "decodeResult": "{\"type\":\"device_report\",\"deviceCode\":\"device123\",\"data\":{\"temperature\":\"25.5\"},\"confirmable\":true}"
    }
  }
  ```
- **编码后需要的格式**：包含HTTP请求信息的JSON对象

## 八、TCP客户端协议

### 1. 消息下发场景
- **传入编码器的消息格式**：
  - **属性下发**：`GatewayWritePropertyMessage` JSON字符串
  - **命令下发**：`GatewayCommandMessage` JSON字符串
  - 格式同TCP协议
- **编码后需要的格式**：字节数组（byte[]）

### 2. 消息应答场景（confirmable=true）
- **说明**：未找到确认消息处理实现

## 九、HTTP协议

### 1. 消息下发场景
- **说明**：未找到控制消息提供者实现，可能不支持或透传

### 2. 消息应答场景（confirmable=true）
- **说明**：无应答场景（HTTP协议是请求-响应模式）
