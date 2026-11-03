/**
 * encode() 方法实现模板
 * 
 * 覆盖平台调用的全部 3 种消息场景：
 *   1) 上报应答(ACK) - confirmable=true, 无 messageType (TCP/CoAP)
 *                     或 messageType="reply" (MQTT)
 *   2) 属性设置(writeProperty) - messageType="writeMessage" (所有协议)
 *   3) 命令下发(command) - messageType="command" (所有协议)
 *
 * ⚠️ 返回值按协议区分：
 *   - TCP/UDP/CoAP: byte[]（编码后的协议帧）
 *   - MQTT: byte[] 或字符串（透传模式）
 *   - LWM2M: DownlinkRequest 对象
 *   - AEP/OneNET HTTP: JSONObject（包含 apiUrl、httpMethod、body 等 API 调用信息）
 * 
 * 📎 详细格式参考：
 *   - references/encode-message-formats.md - 3种消息场景详解
 *   - references/encode-message-formats-detailed.md - 10种协议的完整消息格式
 *   - references/GatewayWritePropertyMessage.java - 平台属性设置消息 DTO
 *   - references/GatewayCommandMessage.java - 平台命令下发消息 DTO
 */
@Override
public ExecuteJarResult encode(Object[] deviceMessage) {
    ExecuteJarResult result = new ExecuteJarResult();
    try {
        String jsonStr = deviceMessage[0].toString();
        log.info("====== Encode start ======");
        log.info("Encode input: {}", jsonStr);
        
        JSONObject msg = JSON.parseObject(jsonStr);
        String msgType = msg.getString("messageType");
        String deviceCode = msg.getString("device");
        
        // ===== 场景判断优先级 =====
        
        // 1) 上报应答（无 messageType，但有 type + confirmable）
        // TCP/CoAP: 传入完整 DecodedMessage JSON
        // 格式: {"type":"device_report","deviceCode":"xxx","data":{},"confirmable":true}
        if (msgType == null || msgType.isEmpty()) {
            String reportType = msg.getString("type");
            boolean confirmable = msg.getBooleanValue("confirmable");
            if (("device_report".equals(reportType) || "gateway_report".equals(reportType)) && confirmable) {
                log.info("Encode scenario: ACK (confirmable report)");
                byte[] ackFrame = buildAckFrame(msg);
                result.setSuccess(true);
                result.setResult(ackFrame);
                log.info("====== Encode end (ACK) ======");
                return result;
            }
        }
        
        // 2) MQTT 上报确认 / reply 类型
        // 格式: {"code":"0","messageType":"reply"}
        if ("reply".equals(msgType)) {
            log.info("Encode scenario: MQTT reply");
            byte[] replyFrame = buildReplyFrame(msg);
            result.setSuccess(true);
            result.setResult(replyFrame);
            log.info("====== Encode end (reply) ======");
            return result;
        }
        
        // 3) 属性设置 writeMessage（所有协议通用）
        // 对应平台 DTO: GatewayWritePropertyMessage
        // 格式: {"messageType":"writeMessage","device":"xxx","messageId":"xxx","properties":{}}
        // AEP/OneNET HTTP: properties 中可能额外包含 productId、imei 等字段
        if ("writeMessage".equals(msgType)) {
            JSONObject properties = msg.getJSONObject("properties");
            String messageId = msg.getString("messageId");
            log.info("Encode scenario: writeProperty, device={}, properties={}", deviceCode, properties);
            
            // AEP/OneNET HTTP 协议特殊处理：返回 HTTP API 调用信息
            // 格式: {"apiUrl":"...","httpMethod":"POST","headers":{},"body":{}}
            // if (isHttpProtocol) {
            //     JSONObject httpResult = buildHttpWriteResponse(deviceCode, properties);
            //     result.setSuccess(true);
            //     result.setResult(httpResult);
            //     log.info("====== Encode end (HTTP writeProperty) ======");
            //     return result;
            // }
            
            byte[] writeFrame = buildWritePropertyFrame(deviceCode, messageId, properties);
            result.setSuccess(true);
            result.setResult(writeFrame);
            log.info("====== Encode end (writeProperty) ======");
            return result;
        }
        
        // 4) 命令下发 command（所有协议通用）
        // 对应平台 DTO: GatewayCommandMessage
        // 格式: {"messageType":"command","device":"xxx","messageId":"xxx","command":"xxx","input":{}}
        // AEP/OneNET HTTP: input 中可能额外包含 productId、imei、MasterKey 等字段
        if ("command".equals(msgType)) {
            String command = msg.getString("command");
            JSONObject input = msg.getJSONObject("input");
            String messageId = msg.getString("messageId");
            log.info("Encode scenario: command, device={}, command={}", deviceCode, command);
            
            // AEP/OneNET HTTP 协议特殊处理：返回 HTTP API 调用信息
            // if (isHttpProtocol) {
            //     JSONObject httpResult = buildHttpCommandResponse(deviceCode, command, input);
            //     result.setSuccess(true);
            //     result.setResult(httpResult);
            //     log.info("====== Encode end (HTTP command) ======");
            //     return result;
            // }
            
            byte[] cmdFrame = buildCommandFrame(deviceCode, messageId, command, input);
            result.setSuccess(true);
            result.setResult(cmdFrame);
            log.info("====== Encode end (command) ======");
            return result;
        }
        
        // 未识别的消息类型
        log.warn("Encode: unknown message type: {}", msgType);
        result.setSuccess(false);
        result.setMessage("Unknown message type: " + msgType);
        
    } catch (Exception e) {
        log.error("====== Encode failed ======", e);
        result.setSuccess(false);
        result.setMessage(e.getMessage());
    }
    return result;
}

// ===== 各场景的实现方法（根据实际协议实现） =====

/**
 * 构建上报应答帧（TCP/CoAP 协议）
 * 传入参数: 解码后的 DecodedMessage JSON
 */
private byte[] buildAckFrame(JSONObject decodedMessage) {
    // TODO: 根据协议实现 ACK 帧构建
    // 从 decodedMessage 中提取 deviceCode、data 等信息构建应答帧
    return new byte[0];
}

/**
 * 构建 MQTT 回复帧
 * 传入参数: {"code":"0","messageType":"reply"}
 */
private byte[] buildReplyFrame(JSONObject replyMessage) {
    // TODO: 根据协议实现 MQTT 回复帧
    return new byte[0];
}

/**
 * 构建属性设置帧
 * 传入参数: deviceCode, messageId, properties
 */
private byte[] buildWritePropertyFrame(String deviceCode, String messageId, JSONObject properties) {
    // TODO: 根据协议实现属性设置帧
    // 将 properties 中的属性编码为协议帧
    return new byte[0];
}

/**
 * 构建命令下发帧
 * 传入参数: deviceCode, messageId, command, input
 */
private byte[] buildCommandFrame(String deviceCode, String messageId, String command, JSONObject input) {
    // TODO: 根据协议实现命令下发帧
    // 将 command 和 input 编码为协议帧
    return new byte[0];
}

/**
 * 构建 AEP/OneNET HTTP 属性设置请求（HTTP 协议专用）
 * 返回值: {"apiUrl":"...","httpMethod":"...","headers":{},"body":{}}
 */
private JSONObject buildHttpWriteResponse(String deviceCode, JSONObject properties) {
    // TODO: 根据 AEP/OneNET HTTP API 规范构建请求
    // 从 properties 中提取 productId、imei 等字段
    JSONObject result = new JSONObject();
    // result.put("apiUrl", "/api/command");
    // result.put("httpMethod", "POST");
    // result.put("headers", headers);
    // result.put("body", body);
    return result;
}

/**
 * 构建 AEP/OneNET HTTP 命令下发请求（HTTP 协议专用）
 * 返回值: {"apiUrl":"...","httpMethod":"...","headers":{},"body":{}}
 */
private JSONObject buildHttpCommandResponse(String deviceCode, String command, JSONObject input) {
    // TODO: 根据 AEP/OneNET HTTP API 规范构建请求
    // 从 input 中提取 productId、imei、MasterKey 等字段
    JSONObject result = new JSONObject();
    // result.put("apiUrl", "/api/command");
    // result.put("httpMethod", "POST");
    // result.put("headers", headers);
    // result.put("body", body);
    return result;
}
