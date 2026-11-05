# B端常见业务流程模式

## 1. 审批流程类

### 单级审批

```
用户提交 → 自动校验 → 审批人审核 → 审批通过/拒绝 → 结束
```

**Mermaid模板**：
```mermaid
flowchart TD
    Start([开始]) --> Submit[提交申请]
    Submit --> Validate{数据校验}
    Validate -->|不通过| Return[退回修改]
    Validate -->|通过| Approve[审批审核]
    Approve -->|通过| Pass[审批通过]
    Approve -->|拒绝| Reject[审批拒绝]
    Pass --> End([结束])
    Reject --> End
    Return --> Submit
```

### 多级审批（会签）

```
提交申请 → 部门经理审核 → 总监审核 → HR复核 → 结束
```

### 条件审批

```
提交申请 → 根据金额判断
├─ 金额<1万 → 部门经理审批
├─ 1万≤金额<10万 → 部门+总监审批
└─ 金额≥10万 → 全员会签审批
```

## 2. 订单处理类

### 标准订单流程

```
下单 → 支付 → 商家确认 → 打包发货 → 物流运输 → 收货确认 → 评价完成
```

**Mermaid模板**：
```mermaid
flowchart LR
    subgraph 订单流程
        O1[创建订单] --> O2[待支付]
        O2 -->|支付成功| O3[已支付]
        O2 -->|超时关闭| O4[已取消]
        O3 --> O5[待发货]
        O5 -->|商家发货| O6[已发货]
        O6 -->|物流运输| O7[运输中]
        O7 -->|到达| O8[已到达]
        O8 -->|签收| O9[已完成]
    end
```

### 退货退款流程

```
申请退货 → 审核退货 → 退回商品 → 验货 → 退款/拒绝
```

## 3. 权限管理类

### RBAC权限模型

```
用户 → 角色 → 权限
         ↓
      菜单权限
      数据权限
      操作权限
```

**Mermaid模板**：
```mermaid
flowchart TB
    subgraph 用户层
        U1[管理员]
        U2[运营人员]
        U3[普通用户]
    end

    subgraph 角色层
        R1[超级管理员]
        R2[运营主管]
        R3[运营专员]
    end

    subgraph 权限层
        P1[系统管理]
        P2[数据查看]
        P3[数据编辑]
        P4[报表导出]
    end

    U1 --> R1
    U2 --> R2
    U3 --> R3
    R1 --> P1
    R2 --> P2
    R2 --> P3
    R3 --> P2
```

### 资源访问控制

```
请求访问 → 登录校验 → 权限校验 → 资源校验 → 允许/拒绝
```

## 4. 数据管理类

### CRUD增删改查

```
列表查询 → 新增/编辑/删除 → 确认操作 → 更新数据库 → 返回结果
```

**Mermaid模板**：
```mermaid
flowchart TD
    Start([开始]) --> List[查询列表]
    List --> Action{操作选择}
    Action -->|新增| Create[填写表单]
    Action -->|编辑| Edit[修改数据]
    Action -->|删除| Delete{确认删除}

    Create --> Validate{数据校验}
    Edit --> Validate
    Validate -->|通过| Save[保存数据库]
    Validate -->|失败| Error[提示错误]
    Error --> Create
    Delete -->|确认| Del[执行删除]
    Delete -->|取消| List

    Save --> Success[操作成功]
    Del --> Success
    Success --> End([结束])
```

### 数据导入导出

```
上传文件 → 文件解析 → 数据校验 → 预览确认 → 执行导入 → 结果反馈
```

## 5. 消息通知类

### 站内信通知

```
触发事件 → 消息创建 → 消息入库 → 消息推送 → 用户查看 → 标记已读
```

### 邮件通知

```
触发事件 → 邮件生成 → 邮件队列 → 邮件发送 → 发送结果记录
```

## 6. 定时任务类

### 批处理任务

```
定时触发 → 查询待处理 → 分批执行 → 结果记录 → 异常告警 → 任务结束
```

**Mermaid模板**：
```mermaid
flowchart TD
    Start([定时触发]) --> Query[查询待处理数据]
    Query --> Count{数据量}
    Count -->|有数据| Process[分批处理]
    Count -->|无数据| End([结束])

    Process --> Handle[执行处理]
    Handle --> Success{处理成功}
    Success -->|是| Next[下一批]
    Success -->|否| Log[记录异常]
    Log --> Next

    Next --> HasMore{还有数据}
    HasMore -->|是| Process
    HasMore -->|否| Alert[发送执行报告]
    Alert --> End
```

## 7. 工作流引擎类

### 通用工作流

```
发起流程 → 流程节点审批 → 流程变量更新 → 流程分支判断 → 流程结束/退回
```

### 会签与或签

```
会签：所有审批人全部通过才算通过
或签：任一审批人通过即可继续
```

## 8. 异常处理模式

### 标准异常处理

```mermaid
flowchart TD
    A[正常流程] --> B{异常判断}
    B -->|正常| C[正常结束]
    B -->|异常| D[记录日志]
    D --> E[告警通知]
    E --> F[人工介入]
    F --> G[问题处理]
    G --> H[流程恢复]
    H --> C
```

### 重试机制

```
执行失败 → 重试计数 < 最大次数 → 等待重试 → 重新执行
                    ↓
              达到最大次数
                    ↓
               标记失败 → 告警通知
```
