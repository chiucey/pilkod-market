---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5b05942b291fa31dc12dc153f899c6be
    PropagateID: 5b05942b291fa31dc12dc153f899c6be
    ReservedCode1: 3043021f286411827a891bf1c067618bc932f13dd2c387dd7329eb99e68c8df4b1bc3002206c907bacd067cc496186931847bf566b93c7671267bc2b3a06bdaf3522f97d6d
    ReservedCode2: 3045022100ec646f94cdf67ae6577191002ddb772f0cbc47b54c5f888a35ba3dd1b7c48db1022029cc56433b492d51933e2518cd7bf64000c6f71fe9b8d41567f3c9f08cddda00
description: 技能黑名单管理。当用户要求把技能加入黑名单、将技能移出黑名单、查看黑名单列表、管理黑名单、解除技能黑名单、或者技能安装失败提示在黑名单中时使用。
name: skill-blacklist
---

# 技能黑名单管理

管理 MiniMax Agent 技能的黑名单状态，提供友好的交互界面。

## 核心功能

### 1. 黑名单列表管理
- 展示当前在黑名单中的所有技能
- 显示技能名称、加入黑名单时间、加入原因
- 支持分页显示（每页10条）

### 2. 添加到黑名单
- 支持用户指定具体技能加入黑名单
- 用户说"把xxx加入黑名单" → 显示确认框
- 记录加入时间和原因

### 3. 从黑名单移除
- 支持用户指定具体技能移出黑名单
- 用户说"解除xxx黑名单"或"把xxx从黑名单移除" → 显示确认框
- 移除后技能可以正常安装

### 4. 黑名单检查机制（仅安装前检查）
- **只在安装前检查**：每次安装技能前自动检查是否在黑名单中
- **卸载前不检查**：卸载技能时不需要进行黑名单检查
- **拦截规则**：如果技能在黑名单中，阻止安装并提示用户
- **解除方式**：用户必须主动确认解除黑名单后才能安装
- 提供"解除黑名单"按钮让用户选择

## 工作流程

### 显示黑名单管理界面

使用 `genui-form-wizard` 展示黑名单管理：

```
genui-form-wizard (action-id="blacklist_console_main")
  genui-form-page (title="技能黑名单管理")
    genui-radio-group (name="action")
      genui-radio (value="view") → 查看黑名单
      genui-radio (value="add") → 添加到黑名单
      genui-radio (value="remove") → 从黑名单移除
    genui-input (selection-mode="radio", name="skill_name", placeholder="输入技能名称")
```

### 查看黑名单列表

```
genui-form-wizard (action-id="blacklist_view")
  genui-form-page (title="黑名单列表")
    genui-text → 显示黑名单中的技能列表
    genui-radio-group (name="action")
      genui-radio (value="remove_one") → 移除选中技能
      genui-radio (value="back") → 返回
    genui-input (selection-mode="radio", name="selected_skill", placeholder="输入要移除的技能名称")
```

### 添加技能到黑名单

1. **用户输入技能名称**
2. **显示确认框**

```
genui-form-wizard (action-id="blacklist_add_confirm")
  genui-form-page (title="确认添加到黑名单")
    genui-text → 显示技能名称
    genui-radio-group (name="confirm")
      genui-radio (value="add") → 确认添加
      genui-radio (value="cancel") → 取消
    genui-input (selection-mode="radio", name="reason", placeholder="输入添加原因（可选）")
```

3. **执行添加** → 显示添加成功结果

### 从黑名单移除

1. **用户输入技能名称**
2. **显示确认框**

```
genui-form-wizard (action-id="blacklist_remove_confirm")
  genui-form-page (title="确认从黑名单移除")
    genui-text → 显示技能名称和当前状态
    genui-radio-group (name="confirm")
      genui-radio (value="remove") → 确认移除
      genui-radio (value="cancel") → 取消
    genui-input (selection-mode="radio", name="notes", placeholder="备注信息（可选）")
```

3. **执行移除** → 显示移除成功结果

### 安装被黑名单拦截的处理流程

当用户尝试安装被黑名单拦截的技能时：

```
genui-form-wizard (action-id="blacklist_install_blocked")
  genui-form-page (title="技能安装被拦截")
    genui-text → 提示："xxx技能已在黑名单中，无法安装"
    genui-radio-group (name="action")
      genui-radio (value="unblock") → 解除黑名单
      genui-radio (value="cancel") → 取消操作
    genui-input (selection-mode="radio", name="confirm_unblock", placeholder="输入'确认'解除黑名单")
```

### 解除黑名单后提示安装

```
genui-form-wizard (action-id="blacklist_unblocked_success")
  genui-form-page (title="黑名单已解除")
    genui-text → 提示："您已成功解除xxx技能的黑名单，现在可以安装该技能"
    genui-radio-group (name="action")
      genui-radio (value="install_now") → 立即安装
      genui-radio (value="install_later") → 稍后安装
    genui-input (selection-mode="radio", name="notes", placeholder="备注信息（可选）")
```

### 卸载完成后提示加入黑名单

当技能卸载完成后（可选流程），提示用户是否将该技能加入黑名单：

```
genui-form-wizard (action-id="blacklist_uninstall_prompt")
  genui-form-page (title="卸载完成")
    genui-text → 提示："xxx技能已成功卸载"
    genui-radio-group (name="action")
      genui-radio (value="add_to_blacklist") → 加入黑名单
      genui-radio (value="skip") → 跳过
    genui-input (selection-mode="radio", name="confirm_add", placeholder="输入'确认'加入黑名单")
```

如果用户选择加入黑名单，继续显示确认框：

```
genui-form-wizard (action-id="blacklist_add_after_uninstall_confirm")
  genui-form-page (title="确认加入黑名单")
    genui-text → 提示："确定要将xxx技能加入黑名单吗？加入后将无法安装"
    genui-radio-group (name="confirm")
      genui-radio (value="confirm_add") → 确认加入
      genui-radio (value="cancel") → 取消
    genui-input (selection-mode="radio", name="reason", placeholder="添加原因（可选）")
```

## 黑名单数据结构

```json
{
  "blacklist": [
    {
      "skill_name": "skill-name",
      "added_at": "2024-01-01T00:00:00Z",
      "reason": "用户手动添加"
    }
  ]
}
```

## 交互规范

1. **确认机制**：所有黑名单操作必须经过用户确认
2. **即时反馈**：操作完成后立即显示结果
3. **可逆操作**：黑名单操作可以撤销（移除出黑名单）
4. **状态透明**：始终让用户清楚当前技能的黑名单状态

## 示例对话

**用户**：把 github-downloader 加入黑名单
**助手**：显示确认框，用户确认后执行添加，并提示添加成功

**用户**：查看黑名单列表
**助手**：显示当前在黑名单中的所有技能

**用户**：我想移除 minimax-pdf 的黑名单
**助手**：显示确认框，用户确认后执行移除

**用户**：安装 xxx 技能
**助手**：检查发现该技能在黑名单中，显示拦截提示和解除黑名单按钮
**助手**：提示"xxx技能已在黑名单中，无法安装。如果想继续安装，需要先解除黑名单。是否解除？"

**用户**：解除 xxx 技能的黑名单
**助手**：执行解除，显示成功提示"您已成功解除xxx技能的黑名单，现在可以安装该技能"，并询问是否立即安装

**用户**：卸载 xxx 技能
**助手**：执行卸载，卸载完成后提示"xxx技能已成功卸载。是否要将该技能加入黑名单？加入后将无法安装"
**助手**：用户选择"加入黑名单" → 显示确认框 → 用户确认后添加到黑名单

## 技术说明

- 黑名单数据存储在本地配置文件中
- **检查时机**：只在安装前触发黑名单检查，卸载前不检查
- **拦截逻辑**：如果技能在黑名单中，阻止安装，用户必须主动确认解除才能继续
- **卸载提示**：技能卸载完成后，可选提示用户是否加入黑名单
- 黑名单状态变更实时生效
- 支持批量操作（未来扩展）
