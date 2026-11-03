/**
 * 测试类模板
 * 
 * 使用方式：
 * 1. 复制到 src/test/java/protocol/{protocol}/{Device}CodecTest.java
 * 2. 替换 {Device}Codec 为实际的编解码器类名
 * 3. 替换 hexData 为用户提供的实际报文
 * 4. 编译运行验证解码结果
 */
public class {Device}CodecTest {
    public static void main(String[] args) {
        {Device}Codec codec = new {Device}Codec();

        // 示例报文（替换为用户提供的 HEX 报文）
        String hexData = "用户提供的HEX报文";
        byte[] payload = hexStringToByteArray(hexData);

        // 执行解码
        ExecuteJarResult result = codec.decode(null, payload);

        // 打印解码结果
        System.out.println("解码成功: " + result.isSuccess());
        System.out.println("解码结果: " + result.getResult());
    }
    
    /**
     * HEX字符串 → byte[]
     */
    public static byte[] hexStringToByteArray(String hex) {
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4)
                    + Character.digit(hex.charAt(i + 1), 16));
        }
        return data;
    }
}
