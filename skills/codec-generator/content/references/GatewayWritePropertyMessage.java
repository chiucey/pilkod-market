package com.inspur.dandelion.business.da.transform.dto;

import com.inspur.dandelion.framework.common.core.entity.da.control.MessageType;
import lombok.Data;
import lombok.experimental.Accessors;

import java.util.HashMap;
import java.util.Map;

/**
 * 平台属性设置消息 DTO
 * 在 encode() 场景的 "writeProperty" 类型中使用
 * 
 * JSON 格式示例：
 * {
 *   "messageType": "writeMessage",
 *   "device": "device123",
 *   "messageId": "msg123",
 *   "properties": {
 *     "temperature": "25.5",
 *     "humidity": "60"
 *   }
 * }
 * 
 * AEP/OneNET HTTP 协议：properties 中可能额外包含 productId、imei 等字段
 */
@Data
@Accessors(chain = true)
public class GatewayWritePropertyMessage {
    private MessageType messageType = MessageType.writeMessage;
    private String device;
    private String messageId;
    private Map<String, String> properties = new HashMap<>();
}
