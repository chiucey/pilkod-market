package protocol.{protocol};

import com.alibaba.fastjson.JSONArray;
import com.alibaba.fastjson.JSONObject;
import io.netty.buffer.ByteBuf;
import io.netty.buffer.Unpooled;
import io.netty.util.ReferenceCountUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * {Device} 协议编解码工具类
 * 提供字节数据解析、编码、校验等功能
 */
public class CodecUtils {

    private static final Logger log = LoggerFactory.getLogger(CodecUtils.class);

    // 帧起始符
    private static final byte FRAME_START = (byte) 0x{frameStart};
    // 帧结束符
    private static final byte FRAME_END = (byte) 0x{frameEnd};
    // 设备编码长度（字节）
    private static final int DEVICE_CODE_LENGTH = {deviceCodeLength};
    // CRC多项式（如果有CRC校验）
    private static final int CRC_POLY = 0x{crcPoly};

    /**
     * 解码入口方法
     * @param reportData 原始上报数据字节数组
     * @param originalData 原始数据 HEX 字符串（用于保存）
     * @return 解码后的 DecodedMessage 对象
     */
    public static DecodedMessage decode(byte[] reportData, String originalData) {
        log.info("CodecUtils.decode start, dataLen={}, hex={}", reportData.length, byteArrayToHexString(reportData));
        DecodedMessage message = new DecodedMessage();
        ByteBuf byteBuf = Unpooled.wrappedBuffer(reportData);

        try {
            // 帧校验
            if (!validateFrame(reportData)) {
                throw new RuntimeException("帧校验失败！");
            }

            // 帧起始符
            byte frameStart = byteBuf.readByte();

            // 解析设备编码
            String deviceCode = parseDeviceCode(byteBuf);
            message.setDeviceCode(deviceCode);
            log.info("deviceCode: {}", deviceCode);

            // 功能码（1字节）
            int functionCode = byteBuf.readUnsignedByte();
            log.info("functionCode: 0x{}, name: {}", String.format("%02X", functionCode), getFunctionName(functionCode));

            // 根据功能码解析不同数据
            // parseResult 包含解析出的所有设备和属性数据
            JSONObject parseResult = new JSONObject();
            parseDataByFunctionCode(byteBuf, parseResult, functionCode);

            // 判断 type：根据解析出的设备数量决定
            // 如果 parseResult 中包含多个设备的数据 -> gateway_report
            // 如果只有一个设备的数据 -> device_report
            if (isGatewayReport(parseResult)) {
                message.setType("gateway_report");
                // gateway_report 格式：{ "DeviceNo1": [{ts, values}, ...], "DeviceNo2": [...] }
                message.setData(parseResult);
            } else {
                message.setType("device_report");
                // device_report 格式：{ "data": { "attr1": "val1", ... }, "timestamp": 1637205296895 }
                JSONObject dataWrapper = new JSONObject();
                // 提取单个设备的属性数据
                JSONObject deviceData = extractDeviceData(parseResult);
                dataWrapper.put("data", deviceData);
                // 提取时间戳，放在 wrapper 内层
                long ts = extractTimestamp(parseResult);
                if (ts > 0) {
                    dataWrapper.put("timestamp", ts);
                } else {
                    dataWrapper.put("timestamp", System.currentTimeMillis());
                }
                message.setData(dataWrapper);
            }

            // 原始数据（附加到 data 中）
            if (message.getData() instanceof JSONObject) {
                ((JSONObject) message.getData()).put("originalData", originalData);
            }

            log.info("CodecUtils.decode end, type={}, deviceCode={}", message.getType(), message.getDeviceCode());

        } finally {
            ReferenceCountUtil.release(byteBuf);
        }

        return message;
    }

    /**
     * 判断是否为网关聚合上报（报文中包含多个设备的数据）
     * TODO: 根据实际协议逻辑实现
     */
    private static boolean isGatewayReport(JSONObject parseResult) {
        // 默认实现：根据协议特征判断
        // 例如：如果协议中包含子设备列表或多个设备地址，则为 gateway_report
        // return parseResult.containsKey("subDevices") && parseResult.getJSONArray("subDevices").size() > 1;
        return false;
    }

    /**
     * 提取单个设备的属性数据
     * TODO: 根据实际协议提取属性键值对
     */
    private static JSONObject extractDeviceData(JSONObject parseResult) {
        // 默认实现：去除内部标记字段，只保留属性数据
        JSONObject data = new JSONObject();
        for (String key : parseResult.keySet()) {
            if (!key.equals("timestamp") && !key.equals("subDevices")) {
                Object val = parseResult.get(key);
                data.put(key, val != null ? String.valueOf(val) : "");
            }
        }
        return data;
    }

    /**
     * 从解析结果中提取时间戳
     * TODO: 根据实际协议提取时间戳字段
     */
    private static long extractTimestamp(JSONObject parseResult) {
        if (parseResult.containsKey("timestamp")) {
            return parseResult.getLongValue("timestamp");
        }
        return 0;
    }

    /**
     * 编码方法 - 生成下发指令
     * @param deviceId 设备ID
     * @param command 指令类型
     * @param params 参数
     * @return 编码后的字节数组
     */
    public static byte[] encode(String deviceId, String command, JSONObject params) {
        ByteBuf byteBuf = Unpooled.buffer();
        try {
            // 帧起始符
            byteBuf.writeByte(FRAME_START);

            // 设备编码
            byte[] deviceCodeBytes = parseDeviceCodeToBytes(deviceId);
            byteBuf.writeBytes(deviceCodeBytes);

            // 根据指令类型生成控制码和数据域
            byte[] dataField = encodeCommand(command, params);

            // 控制码
            byteBuf.writeByte(getCommandCode(command));

            // 数据域长度
            byteBuf.writeByte(dataField.length);

            // 数据域
            byteBuf.writeBytes(dataField);

            // 计算校验（CRC或累加和）
            byte[] checksum = calcChecksum(byteBuf);
            byteBuf.writeBytes(checksum);

            // 帧结束符
            byteBuf.writeByte(FRAME_END);

            byte[] result = new byte[byteBuf.writerIndex()];
            byteBuf.readBytes(result);
            return result;

        } finally {
            ReferenceCountUtil.release(byteBuf);
        }
    }

    /**
     * 根据功能码解析数据
     */
    private static void parseDataByFunctionCode(ByteBuf byteBuf, JSONObject data, int functionCode) {
        // TODO: 根据实际协议实现不同功能码的数据解析
        // 示例：
        // if (functionCode == 0x01) { // 上报数据
        //     parseReportData(byteBuf, data);
        // } else if (functionCode == 0x02) { // 告警数据
        //     parseAlarmData(byteBuf, data);
        // }
    }

    /**
     * 编码指令
     */
    private static byte[] encodeCommand(String command, JSONObject params) {
        ByteBuf buf = Unpooled.buffer();
        try {
            // TODO: 根据实际协议实现指令编码
            // 示例：
            // switch (command) {
            //     case "open":
            //         buf.writeByte(0x01);
            //         break;
            //     case "close":
            //         buf.writeByte(0x02);
            //         break;
            // }

            byte[] result = new byte[buf.writerIndex()];
            buf.readBytes(result);
            return result;
        } finally {
            ReferenceCountUtil.release(buf);
        }
    }

    /**
     * 获取功能码名称
     */
    private static String getFunctionName(int functionCode) {
        // TODO: 根据实际协议定义功能码名称
        switch (functionCode) {
            case 0x01: return "上报数据";
            case 0x02: return "告警数据";
            case 0x03: return "心跳数据";
            default: return "未知";
        }
    }

    /**
     * 获取指令代码
     */
    private static byte getCommandCode(String command) {
        // TODO: 根据实际协议定义指令代码
        switch (command) {
            case "open": return (byte) 0x01;
            case "close": return (byte) 0x02;
            default: return (byte) 0x00;
        }
    }

    /**
     * 解析设备编码
     */
    private static String parseDeviceCode(ByteBuf byteBuf) {
        byte[] deviceCodeBytes = new byte[DEVICE_CODE_LENGTH];
        byteBuf.readBytes(deviceCodeBytes);
        // TODO: 根据实际编码方式解析（BCD/ASCII/HEX）
        return bytesToHex(deviceCodeBytes);
    }

    /**
     * 设备编码转字节数组
     */
    private static byte[] parseDeviceCodeToBytes(String deviceCode) {
        // TODO: 根据实际编码方式转换
        return hexStringToByteArray(deviceCode);
    }

    /**
     * 帧校验
     */
    private static boolean validateFrame(byte[] data) {
        if (data.length < {minFrameLength}) return false;
        if ((data[0] & 0xFF) != 0x{frameStart}) return false;
        // TODO: 实现CRC或累加和校验
        return true;
    }

    /**
     * 计算校验码（CRC或累加和）
     */
    private static byte[] calcChecksum(ByteBuf byteBuf) {
        // TODO: 根据实际协议实现CRC或累加和计算
        return new byte[] { 0x00, 0x00 };
    }

    /**
     * 字节数组转HEX字符串
     */
    public static String byteArrayToHexString(byte[] bytes) {
        if (bytes == null) return "";
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b & 0xFF));
        }
        return sb.toString();
    }

    /**
     * HEX字符串转字节数组
     */
    public static byte[] hexStringToByteArray(String hex) {
        if (hex == null || hex.length() % 2 != 0) {
            return new byte[0];
        }
        int len = hex.length() / 2;
        byte[] result = new byte[len];
        for (int i = 0; i < len; i++) {
            result[i] = (byte) Integer.parseInt(hex.substring(i * 2, i * 2 + 2), 16);
        }
        return result;
    }

    /**
     * 字节数组转BCD字符串
     */
    public static String bcdToString(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b & 0xFF));
        }
        return sb.toString();
    }

    /**
     * BCD字符串转字节数组
     */
    public static byte[] stringToBcd(String str, int length) {
        byte[] result = new byte[length];
        String padded = String.format("%" + (length * 2) + "s", str).replace(' ', '0');
        for (int i = 0; i < length; i++) {
            int idx = (length - 1 - i) * 2;
            int high = Character.digit(padded.charAt(idx), 10);
            int low = Character.digit(padded.charAt(idx + 1), 10);
            result[i] = (byte) ((high << 4) | low);
        }
        return result;
    }

    /**
     * 计算CRC16
     */
    public static byte[] calcCrc16(byte[] data) {
        int crc = 0xFFFF;
        for (byte b : data) {
            crc ^= (b & 0xFF) << 8;
            for (int i = 0; i < 8; i++) {
                if ((crc & 0x8000) != 0) {
                    crc = (crc << 1) ^ CRC_POLY;
                } else {
                    crc <<= 1;
                }
            }
        }
        crc &= 0xFFFF;
        return new byte[] { (byte) (crc & 0xFF), (byte) ((crc >> 8) & 0xFF) };
    }

    /**
     * 计算累加和
     */
    public static byte calcSum(byte[] data) {
        int sum = 0;
        for (byte b : data) {
            sum += (b & 0xFF);
        }
        return (byte) (sum & 0xFF);
    }

    /**
     * 字节数组转字符串
     */
    public static String bytesToHex(byte[] bytes) {
        return byteArrayToHexString(bytes);
    }
}
