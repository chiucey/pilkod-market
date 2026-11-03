package protocol.{protocol};

import lombok.Data;

/**
 * {Device} 上报数据实体
 */
@Data
public class {Report}Entity {

    /**
     * 原始上报数据字节数组
     */
    private byte[] reportData;

    /**
     * 原始数据HEX字符串
     */
    private String reportDataStr;

    /**
     * 设备编码
     */
    private String deviceCode;

    /**
     * 功能码
     */
    private int functionCode;

    // TODO: 根据实际协议添加更多字段
    // 示例字段：
    // private int status;           // 状态
    // private double value;         // 数值
    // private String timestamp;     // 时间戳
    // private int signalStrength;   // 信号强度
    // private double batteryVoltage; // 电池电压

    public {Report}Entity() {
    }

    public {Report}Entity(byte[] reportData, String reportDataStr) {
        this.reportData = reportData;
        this.reportDataStr = reportDataStr;
    }

    public byte[] getReportData() {
        return reportData;
    }

    public String getReportDataStr() {
        return reportDataStr;
    }
}
