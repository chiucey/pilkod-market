package com.inspur.dandelion.business.da.transform.dto;

import com.inspur.dandelion.framework.common.core.entity.da.control.MessageType;
import lombok.Data;
import lombok.experimental.Accessors;

import java.util.HashMap;
import java.util.Map;

/**
 * 平台命令下发消息 DTO
 * 在 encode() 场景的 "command" 类型中使用
 * 
 * JSON 格式示例：
 * {
 *   "messageType": "command",
 *   "device": "device123",
 *   "command": "restart",
 *   "messageId": "msg123",
 *   "input": {
 *     "delay": "5",
 *     "param1": "value1"
 *   }
 * }
 * 
 * AEP/OneNET HTTP 协议：input 中可能额外包含 productId、imei、MasterKey 等字段
 */
@Data
@Accessors(chain = true)
public class GatewayCommandMessage {
    private MessageType messageType = MessageType.command;
    private String device;
    private String command; // 无参数时命令下发
    private String messageId;
    private Map<String, String> input = new HashMap<>();
}
