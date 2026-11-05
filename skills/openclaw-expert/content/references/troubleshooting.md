# OpenClaw 故障排查指南

## 常见问题速查表

### 问题 1：Gateway 启动失败

**症状**：
```
Error: Failed to start gateway
Connection refused on port 8080
```

**排查步骤**：
1. 检查端口是否被占用：`lsof -i :8080`
2. 验证配置文件语法
3. 确认所有依赖已安装

**解决方案**：
```bash
# 杀死占用端口的进程
kill -9 <PID>

# 或使用配置文件指定其他端口
openclaw start --port 8081
```

---

### 问题 2：配置字段无效

**症状**：
```
Warning: Invalid config field 'unknown_field'
```

**排查步骤**：
1. 检查配置文件格式（YAML/JSON）
2. 确认字段名拼写正确
3. 查看版本兼容性

**常见有效字段**：
- `name`：技能名称
- `description`：技能描述
- `version`：版本号
- `commands`：命令列表

---

### 问题 3：频道不可用

**症状**：
```
Channel 'slack' is not available
```

**排查步骤**：
1. 确认频道插件已安装
2. 检查 API 密钥配置
3. 验证网络连接

---

### 问题 4：消息无响应

**症状**：
- 发送消息后无任何回应
- Bot 显示在线但不响应

**排查步骤**：
1. 检查日志中的错误信息
2. 确认技能已正确加载
3. 验证权限配置

---

## 日志位置

| 环境 | 日志路径 |
|------|----------|
| Linux | `~/.openclaw/logs/` |
| macOS | `~/.openclaw/logs/` |
| Windows | `%USERPROFILE%\.openclaw\logs\` |

## 诊断命令

```bash
# 检查 OpenClaw 状态
openclaw status

# 查看详细日志
openclaw logs --tail 100

# 验证配置文件
openclaw config validate

# 重置到默认配置
openclaw config reset
```
