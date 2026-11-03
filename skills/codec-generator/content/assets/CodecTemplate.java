package protocol.{protocol};

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.inspur.dandelion.framework.common.codec.entity.ExecuteJarResult;
import com.inspur.dandelion.framework.common.codec.jar.AccessProtocolModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.StandardCharsets;
import java.util.Base64;

import static protocol.{protocol}.CodecUtils.byteArrayToHexString;

/**
 * {Device} 协议编解码器
 * 实现 AccessProtocolModel 接口，提供设备数据解码和指令编码功能
 */
public class {Device}Codec implements AccessProtocolModel {

    private static final Logger log = LoggerFactory.getLogger({Device}Codec.class);

    // 帧起始符
    private static final byte FRAME_START = (byte) 0x{frameStart};
    // 帧结束符（如果有）
    private static final byte FRAME_END = (byte) 0x{frameEnd};

    @Override
    public ExecuteJarResult decode(String topic, byte[] payload) {
        ExecuteJarResult result = new ExecuteJarResult();
        try {
            log.info("====== {Device} decode start ======");
            log.info("decode input hex: " + byteArrayToHexString(payload));

            String payloadStr = new String(payload);
            byte[] reportData = null;
            String originalData = null;

            // AEP 平台格式
            if (payloadStr.contains("{") && payloadStr.contains("payload")) {
                log.info("detect AEP format");
                {Report}Entity reportEntity = parseAepPayload(payloadStr);
                reportData = reportEntity.getReportData();
                originalData = reportEntity.getReportDataStr();
            }
            // OneNET 平台格式
            else if (payloadStr.contains("{") && payloadStr.contains("msg")) {
                log.info("detect OneNET format");
                {Report}Entity reportEntity = parseOnenetPayload(payloadStr);
                reportData = reportEntity.getReportData();
                originalData = reportEntity.getReportDataStr();
            }
            // TCP/UDP 直连格式
            else if (payload.length > 0 && (payload[0] & 0xFF) == 0x{frameStart}) {
                log.info("detect TCP/UDP direct format");
                reportData = payload;
                originalData = byteArrayToHexString(reportData);
            }
            // Base64编码的数据
            else {
                try {
                    reportData = Base64.getDecoder().decode(payload);
                    originalData = byteArrayToHexString(reportData);
                } catch (Exception e) {
                    log.warn("data is not Base64 format");
                }
            }

            if (reportData == null) {
                throw new RuntimeException("无法识别数据格式");
            }

            // 调用工具类进行解码 - 返回 DecodedMessage 对象
            DecodedMessage decodedMessage = CodecUtils.decode(reportData, originalData);

            log.info("{Device} decode result: " + JSON.toJSONString(decodedMessage));
            log.info("====== {Device} decode end ======");
            result.setResult(JSON.toJSONString(decodedMessage));
            result.setSuccess(true);

        } catch (Exception e) {
            log.error("====== {Device} decode failed ======", e);
            result.setSuccess(false);
            result.setMessage(e.getMessage());
        }
        return result;
    }

    @Override
    public ExecuteJarResult encode(Object[] deviceMessage) {
        ExecuteJarResult result = new ExecuteJarResult();
        try {
            if (deviceMessage == null || deviceMessage.length < 2) {
                throw new RuntimeException("参数不足，需要topic和message");
            }

            String topic = (String) deviceMessage[0];
            String message = (String) deviceMessage[1];

            log.info("{Device}编码 topic: " + topic);
            log.info("{Device}编码 message: " + message);

            JSONObject msgObj = JSON.parseObject(message);
            String deviceId = msgObj.getString("deviceId");
            String command = msgObj.getString("command");
            JSONObject params = msgObj.getJSONObject("params");

            if (deviceId == null || deviceId.isEmpty()) {
                throw new RuntimeException("deviceId不能为空");
            }

            byte[] encodedData = CodecUtils.encode(deviceId, command, params);

            String hexString = byteArrayToHexString(encodedData);
            log.info("{Device}编码结果：" + hexString);

            result.setResult(hexString);
            result.setSuccess(true);

        } catch (Exception e) {
            log.error("{Device}编码失败：", e);
            result.setSuccess(false);
            result.setMessage(e.getMessage());
        }
        return result;
    }

    /**
     * 解析AEP平台payload
     */
    private {Report}Entity parseAepPayload(String payloadStr) {
        JSONObject json = JSON.parseObject(payloadStr);
        String payload = json.getString("payload");
        byte[] data = Base64.getDecoder().decode(payload);
        return new {Report}Entity(data, byteArrayToHexString(data));
    }

    /**
     * 解析OneNET平台payload
     */
    private {Report}Entity parseOnenetPayload(String payloadStr) {
        JSONObject json = JSON.parseObject(payloadStr);
        JSONObject msg = json.getJSONObject("msg");
        String dataStr = msg.getString("data");
        byte[] data;
        if (dataStr.matches("[0-9A-Fa-f]+") && dataStr.length() % 2 == 0) {
            data = CodecUtils.hexStringToByteArray(dataStr);
        } else {
            data = Base64.getDecoder().decode(dataStr);
        }
        return new {Report}Entity(data, byteArrayToHexString(data));
    }
}
