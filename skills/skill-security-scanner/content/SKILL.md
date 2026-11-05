---
name: skill-security-scanner
description: Security vulnerability and privacy risk scanner for Skill files. Used when users request security scans, vulnerability checks, or validation of skill packages, such as "check if this skill is safe", "scan for vulnerabilities", "verify no information leakage", "detect malicious code", or "review installation packages".
---

# Skill 安全检测器

## 概述

此技能用于自动扫描和检测 Skill 文件中的安全漏洞、信息泄露风险和恶意代码模式。确保安装的 Skill 没有隐藏的安全威胁。

## 扫描维度

### 1. 信息泄露检测

检测可能泄露敏感信息的模式：

- **凭证泄露**：硬编码的 API Key、Token、密码、私钥
- **文件路径泄露**：暴露的系统路径、用户目录信息
- **环境变量泄露**：未加密的环境变量、配置 secrets
- **代码注释泄露**：注释中的敏感信息、调试代码

### 2. 代码漏洞检测

识别常见的安全漏洞模式：

- **命令注入**：使用 `eval`、`exec`、`subprocess` 执行未验证的用户输入
- **路径遍历**：不安全的文件路径拼接 (`../`)
- **不安全反序列化**：`pickle.loads`、`yaml.load` 带危险参数
- **危险的系统调用**：未经沙箱化的系统命令执行
- **上传/下载风险**：不安全的文件传输操作
- **网络请求风险**：发送到未知端点的请求

### 3. 文件结构异常

检测可疑的文件结构模式：

- 符号链接逃逸（符号链接指向 `/workspace` 之外）
- 隐藏文件（如 `.hidden_eval.sh`）
- 可执行脚本在非预期位置
- 配置文件中的可疑路径

### 4. 依赖安全检测

检查 `requirements.txt` 或依赖配置：

- 已知漏洞的包版本
- 可疑的第三方包名称
- 过于宽泛的包权限要求

## 扫描流程

```
1. 解压/读取 Skill 包 (.skill 文件)
2. 递归扫描所有文件内容
3. 应用正则表达式和安全规则匹配
4. 检查文件结构完整性
5. 分析依赖安全风险
6. 生成安全报告
```

## 输出格式

检测完成后，输出结构化报告：

```
## 安全扫描报告

### 风险等级
- [高危] 3项
- [中危] 2项
- [低危] 1项

### 问题详情

#### 高危: 命令注入风险
文件: `scripts/update.py`
位置: 第 42 行
描述: 使用 eval() 执行未验证的字符串

#### 中危: API Key 泄露
文件: `config/api.json`
描述: 发现疑似 API Key 暴露
```

## 检测规则文件

详细的检测规则定义在 `references/security-rules.md` 中。

## 使用方法

当用户要求安全检测时：

1. 接收 Skill 文件路径或内容
2. 执行 `scripts/quick_validate.py` 进行快速扫描
3. 如需深度检测，使用完整规则集
4. 生成并展示安全报告

## 注意事项

- 仅提供检测服务，不执行可疑代码
- 保持检测的客观性和准确性
- 发现问题时提供修复建议
