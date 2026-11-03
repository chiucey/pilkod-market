---
name: free-ride
description: "OpenRouter免费AI模型管理技能。当用户要求管理OpenRouter免费模型、配置模型fallback机制、按质量排序筛选模型、手动切换AI模型、更新MaxClaw模型配置、处理速率限制问题、查询OpenRouter模型列表时使用。触发词包括免费AI模型、OpenRouter模型、模型fallback、速率限制适配、模型排序、切换免费模型、更新模型配置、规避速率限制"
---

# Free-Ride：OpenRouter 免费 AI 模型管理技能

## 概述

本技能为 MaxClaw 提供 OpenRouter 生态免费 AI 模型的智能管理能力，核心功能包括：

- **智能排序**：按模型质量、可用性、速率限制容错性加权排序
- **Fallback 机制**：多级别 fallback 配置，速率限制时无缝切换
- **无损更新**：仅修改模型相关配置，保留所有其他配置
- **安全凭证**：通过 MaxClaw 安全渠道管理 API 密钥

## 执行流程

### 1. 前置准备（Pre-Execution）

```python
# 初始化步骤
1. 初始化 OpenRouter 免费模型元数据库
   - 模型质量评分 (quality_score)
   - 速率限制阈值 (rate_limit_rpm)
   - 兼容性标签 (compatibility_tags)

2. 加载 MaxClaw 当前模型配置
   - 解析现有配置结构
   - 定位模型相关字段（主模型、fallback 列表、白名单）
   - 保留所有非模型相关配置（网关、渠道、插件）

3. 校验 OpenRouter API 密钥
   - 通过 MaxClaw 安全渠道获取
   - 不直接存储或暴露密钥

4. 初始化模型排序算法
   - 质量优先级权重：0.5
   - 可用性权重：0.3
   - 速率限制容错性权重：0.2
```

### 2. 主执行（Main-Execution）

#### 2.1 模型排序算法

```python
def rank_models(models):
    """
    按综合评分排序模型
    综合评分 = 质量分 * 0.5 + 可用性分 * 0.3 + 速率限制容错分 * 0.2
    """
    ranked = []
    for model in models:
        score = (
            model.quality_score * 0.5 +
            model.availability_score * 0.3 +
            model.rate_limit_tolerance * 0.2
        )
        ranked.append((model, score))
    return sorted(ranked, key=lambda x: x[1], reverse=True)
```

#### 2.2 Fallback 配置生成

```python
def generate_fallback_list(ranked_models, count=5):
    """
    生成 fallback 模型列表
    - 首 fallback 设为 OpenRouter 智能路由模型
    - 支持自定义 fallback 数量（默认 5 个）
    """
    fallback = []

    # 第一个使用智能路由模型确保速率限制时无缝切换
    fallback.append("openrouter/auto")

    # 后续使用排序后的免费模型
    for model, score in ranked_models[:count-1]:
        fallback.append(model.id)

    return fallback
```

#### 2.3 配置更新规则

**仅修改以下字段**：
- `model.primary` - 主模型 ID
- `model.fallback` - Fallback 模型列表
- `model.whitelist` - 模型白名单（如有）

**保留不变**：
- 网关配置（gateway.*）
- 渠道配置（channels.*）
- 插件配置（plugins.*）
- 日志配置（logging.*）
- 其他非模型相关配置

### 3. 后置处理（Post-Execution）

```python
# 后置步骤
1. 配置持久化
   - 保存到 MaxClaw 安全存储
   - 保留配置变更历史（时间戳 + 操作类型）

2. 生成操作报告
   - 更新内容摘要
   - 模型排序结果
   - Fallback 列表
   - 注意事项和限制

3. 等待后续指令
   - 强制刷新模型列表
   - 调整 fallback 数量
   - 切换指定模型
```

## 用户指令处理

| 指令 | 处理方式 |
|------|----------|
| `刷新模型列表` | 重新获取 OpenRouter 免费模型，排序后更新 |
| `切换到 <模型>` | 验证模型可用性，设置为主模型 |
| `更新 fallback` | 重新排序并生成 fallback 列表 |
| `查看当前配置` | 返回模型配置状态和排序结果 |
| `设置 fallback 数量 <N>` | 修改 fallback 列表长度为 N |

## 安全规则

1. **数据隔离**：不向外部服务发送敏感信息
2. **凭证加密**：API 密钥通过 MaxClaw 安全渠道管理
3. **最小修改**：仅修改模型相关配置字段
4. **变更日志**：记录所有配置变更历史
5. **无外部调用**：不直接调用第三方 API（仅通过 MaxClaw 渠道）

## 错误处理

| 错误类型 | 处理策略 |
|----------|----------|
| API 密钥无效 | 提示用户通过 MaxClaw 配置 OpenRouter 密钥 |
| 模型不可用 | 自动跳过并使用下一个候选模型 |
| 速率限制触发 | 激活 fallback 机制切换到备用模型 |
| 配置写入失败 | 回滚到原配置，报告错误详情 |

## 示例对话

**用户**："帮我配置 OpenRouter 免费模型"

**执行**：
1. 获取 OpenRouter 免费模型列表
2. 按质量评分排序
3. 生成 5 个 fallback 模型
4. 更新 MaxClaw 模型配置
5. 返回配置结果

**回复**：
```
✅ OpenRouter 免费模型配置完成

📊 模型排序（按质量）：
1. anthropic/claude-3-haiku (Quality: 0.95)
2. google/gemini-pro (Quality: 0.90)
3. ...

🔄 Fallback 列表：
1. openrouter/auto (智能路由)
2. anthropic/claude-3-haiku
3. ...

⚠️ 注意事项：
- 速率限制时自动切换到下一个模型
- 如需调整 fallback 数量，请说"设置 fallback 数量为 N"
```

---

## 参考资料

详细文档位于 `references/` 目录：
- `openrouter-models.md` - OpenRouter 免费模型完整列表
- `fallback-strategy.md` - Fallback 策略详解
- `config-schema.md` - MaxClaw 模型配置结构
