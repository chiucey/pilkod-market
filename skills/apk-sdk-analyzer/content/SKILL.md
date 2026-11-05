---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7aa2f2f8470a08e61d1418d895ba217f
    PropagateID: 7aa2f2f8470a08e61d1418d895ba217f
    ReservedCode1: 30460221009272aec9cde9b5890d0f48d6e4768a1b1924be11c02f1714aff8a9531f90829a022100e03d6b24fa2c83a7d962deba42305be00a91ddca0a26ee1a38d4794fa85e1b5a
    ReservedCode2: 30440220420b06a4aacc823e0867c0d587673c2c5173aa1dd6b28022bc894d726ae8b9490220064c181436a0ebfe5b5067b99cc67e917c999df5eb4124ab1fcdd4439d07a2bc
---

---
name: apk-sdk-analyzer
description: 专业的APK逆向分析工具，专注于识别和提取APK文件中的SDK注册ID。特别擅长识别数字天堂（Dcloud）的__UNI__特征、福建分和秒公司的统计类SDK注册ID，以及友盟、百度统计、极光推送等常见SDK的注册标识。当用户需要分析APK中的SDK信息、提取注册ID、识别使用的第三方SDK，或者进行应用安全审计时，一定要使用此技能。
---

# APK SDK 注册ID分析技能

## 功能介绍

此技能用于分析APK文件中包含的SDK注册ID和相关信息，帮助用户识别应用中集成的第三方SDK及其注册标识。

## 支持的SDK类型

### 1. 数字天堂（Dcloud）SDK
- **识别特征**：`__UNI__` 前缀的注册ID
- **常见格式**：`__UNI__[字母数字组合]`
- **示例**：`__UNI__A1B2C3D4`

### 2. 福建分和秒公司SDK
- **识别特征**：统计类SDK的注册ID
- **常见格式**：通常为数字或字母数字组合
- **示例**：`1234567890` 或 `FHMSDK_123456`

### 3. 其他常见SDK
- **百度统计**：`BAIDU_ANALYTICS_ID`
- **友盟统计**：`UMENG_APPKEY`
- **腾讯移动分析**：`TENCENT_ANALYTICS_ID`
- **极光推送**：`JPUSH_APPKEY`
- **个推**：`GETUI_APPID`

## 分析方法

### 1. 反编译APK
- 使用工具如 `apktool` 或 `jadx` 反编译APK文件
- 提取 `AndroidManifest.xml` 和相关资源文件

### 2. 搜索SDK注册ID
- 在反编译后的文件中搜索特定特征字符串
- 重点检查以下位置：
  - `AndroidManifest.xml` 中的 meta-data 标签
  - `strings.xml` 中的字符串资源
  - `build.gradle` 或相关配置文件
  - 代码文件中的常量定义

### 3. 识别SDK类型
- 根据搜索到的特征字符串判断SDK类型
- 提取并整理注册ID信息

## 使用示例

### 输入示例
```
分析这个APK文件中的SDK注册ID：app.apk
```

### 输出示例
```
## APK SDK 注册ID分析结果

### 数字天堂（Dcloud）SDK
- 注册ID：__UNI__A1B2C3D4
- 类型：uni-app 应用

### 福建分和秒公司SDK
- 注册ID：1234567890
- 类型：统计分析SDK

### 其他SDK
- 友盟统计：UMENG_APPKEY=5f8c7d6e5b4a3c2b1a0
- 极光推送：JPUSH_APPKEY=1234567890abcdef

### 分析总结
- 共识别到 4 个SDK注册ID
- 主要功能：应用开发框架、统计分析、消息推送
```

## 分析步骤

1. **接收APK文件**：用户提供APK文件路径或上传APK文件
2. **反编译分析**：使用工具反编译APK并提取相关文件
3. **特征搜索**：在反编译后的文件中搜索SDK特征字符串
4. **识别分类**：根据特征识别SDK类型并提取注册ID
5. **生成报告**：整理分析结果并生成详细报告

## 注意事项

- 分析过程可能需要一定时间，取决于APK文件大小
- 某些SDK可能使用加密或混淆技术隐藏注册ID
- 对于复杂的APK，可能需要更深入的分析方法

## 工具依赖

- Java 运行环境
- apktool 或 jadx（用于反编译APK）
- 文本搜索工具（如 grep 或 PowerShell 搜索命令）

## 输出格式

分析结果应包含以下内容：
- 识别到的SDK类型
- 对应的注册ID
- SDK的功能描述
- 分析总结和建议

## 故障排除

如果分析失败，可能的原因包括：
- APK文件损坏或格式不正确
- 反编译工具配置问题
- SDK使用了特殊的隐藏技术

在这种情况下，建议尝试使用不同的反编译工具或方法进行分析。