package protocol.{protocol};

import com.alibaba.fastjson.JSONObject;
import lombok.Data;

/**
 * 解码后的标准数据格式
 * 所有解码器必须返回此格式
 */
@Data
public class DecodedMessage {
    /**
     * 解码之后的消息类型
     * 仅两种取值：
     * - device_report：单设备数据上报
     * - gateway_report：网关聚合多设备上报（报文中包含多个子设备的数据）
     */
    private String type;
    /**
     * 租户编号（平台自动填充，编解码器无需赋值）
     */
    private String tenantCode;
    /**
     * 设备编号（网关模式下为网关编号）
     */
    private String deviceCode;
    /**
     * 平台收到报文后是否需要立刻应答
     * 根据协议资料确定：当设备上报报文要求应答时设为 true
     */
    private boolean confirmable;
    /**
     * 解码之后的数据
     * - device_report 时：JSONObject，包含 "data"（属性键值对的嵌套结构）
     * - gateway_report 时：JSONObject，以子设备编号为 key，值为包含 ts 和 values 的记录数组
     */
    private Object data;

    public DecodedMessage() {
    }

    public DecodedMessage(String type, String deviceCode, Object data) {
        this.type = type;
        this.deviceCode = deviceCode;
        this.data = data;
    }
}
