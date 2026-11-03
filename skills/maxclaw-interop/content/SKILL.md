---
name: maxclaw-interop
description: MaxClaw多实例互操作通信技能。实现多个MaxClaw代理之间的消息传递、状态共享和互操作协议。当需要让不同MaxClaw实例进行通信、交换信息、协调任务或共享状态时使用。
---

# MaxClaw 互操作通信技能

本技能提供一套完整的机制，使多个MaxClaw实例能够跨越Session和Workspace边界进行可靠的信息交换和互操作。

## 核心架构

### 通信模型

系统采用发布-订阅与请求-响应混合的通信模型。消息通过共享文件系统进行中转，每个MaxClaw实例拥有唯一的标识符（Agent ID），消息按照目标ID进行路由。

### 目录结构

```
/workspace/temp-skills/maxclaw-interop/comm/
├── inbox/              # 接收消息队列
├── outbox/             # 发送消息队列
├── state/              # 共享状态存储
├── lock/               # 分布式锁文件
└── registry/           # 实例注册表
```

## 消息协议

### 消息格式

所有消息均采用JSON格式，包含以下字段：

```json
{
  "msg_id": "uuid-v4",
  "timestamp": "ISO8601格式时间戳",
  "sender": "发送方Agent ID",
  "recipient": "目标Agent ID或'broadcast'",
  "msg_type": "message|request|response|event",
  "action": "操作类型",
  "payload": {},
  "correlation_id": "关联消息ID（用于请求-响应对）"
}
```

### 消息类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| message | 普通消息 | 信息传递、状态更新 |
| request | 请求消息 | 跨Agent任务协调 |
| response | 响应消息 | 请求的回复 |
| event | 事件通知 | 状态变更广播 |

### 操作类型

| 操作 | 说明 |
|------|------|
| PING | 心跳检测 |
| REGISTER | 实例注册 |
| SYNC_STATE | 状态同步 |
| TASK_DELEGATE | 任务委托 |
| DATA_REQUEST | 数据请求 |
| DATA_RESPONSE | 数据响应 |
| BROADCAST | 广播消息 |

## 通信API

### 初始化通信管道

在通信前，每个MaxClaw实例需要初始化通信管道：

```python
import json
import os
import uuid
from datetime import datetime

class MaxClawComm:
    def __init__(self, agent_id: str, comm_base: str = "/workspace/temp-skills/maxclaw-interop/comm"):
        self.agent_id = agent_id
        self.comm_base = comm_base
        self._ensure_dirs()

    def _ensure_dirs(self):
        for subdir in ['inbox', 'outbox', 'state', 'lock', 'registry']:
            os.makedirs(f"{self.comm_base}/{subdir}", exist_ok=True)

    def register(self):
        """注册本实例到注册表"""
        registry_file = f"{self.comm_base}/registry/agents.json"
        agents = {}
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                agents = json.load(f)

        agents[self.agent_id] = {
            'registered_at': datetime.utcnow().isoformat(),
            'last_seen': datetime.utcnow().isoformat(),
            'status': 'active'
        }

        with open(registry_file, 'w') as f:
            json.dump(agents, f, indent=2)

        return True
```

### 发送消息

```python
    def send_message(self, recipient: str, action: str, payload: dict, msg_type: str = "message"):
        """发送消息到指定接收者"""
        msg = {
            'msg_id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'sender': self.agent_id,
            'recipient': recipient,
            'msg_type': msg_type,
            'action': action,
            'payload': payload,
            'correlation_id': None
        }

        outbox_file = f"{self.comm_base}/outbox/{msg['msg_id']}.json"
        with open(outbox_file, 'w') as f:
            json.dump(msg, f, indent=2)

        # 如果是广播消息，复制到inbox供其他实例处理
        if recipient == 'broadcast':
            self._propagate_broadcast(msg)

        return msg['msg_id']

    def _propagate_broadcast(self, msg: dict):
        """将广播消息分发到所有已注册实例"""
        registry_file = f"{self.comm_base}/registry/agents.json"
        if not os.path.exists(registry_file):
            return

        with open(registry_file, 'r') as f:
            agents = json.load(f)

        for agent_id in agents.keys():
            if agent_id != self.agent_id:
                inbox_file = f"{self.comm_base}/inbox/{agent_id}/{msg['msg_id']}.json"
                os.makedirs(os.path.dirname(inbox_file), exist_ok=True)
                with open(inbox_file, 'w') as f:
                    json.dump(msg, f, indent=2)
```

### 接收消息

```python
    def receive_messages(self):
        """接收所有发给本实例的消息"""
        inbox_dir = f"{self.comm_base}/inbox/{self.agent_id}"
        os.makedirs(inbox_dir, exist_ok=True)

        messages = []
        for filename in os.listdir(inbox_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(inbox_dir, filename)
                with open(filepath, 'r') as f:
                    messages.append(json.load(f))
                os.remove(filepath)  # 处理后删除

        # 按时间戳排序
        messages.sort(key=lambda x: x['timestamp'])
        return messages

    def process_messages(self):
        """处理接收到的消息并返回待处理列表"""
        messages = self.receive_messages()
        responses = []

        for msg in messages:
            # 更新发送者最后可见时间
            self._update_last_seen(msg['sender'])

            # 根据消息类型和操作处理
            if msg['action'] == 'PING':
                responses.append(self._handle_ping(msg))
            elif msg['action'] == 'DATA_REQUEST':
                responses.append(self._handle_data_request(msg))
            elif msg['action'] == 'TASK_DELEGATE':
                responses.append(self._handle_task_delegate(msg))
            else:
                # 通用消息处理，返回确认
                responses.append({
                    'recipient': msg['sender'],
                    'action': 'ACK',
                    'payload': {'original_msg_id': msg['msg_id']}
                })

        return messages, responses

    def _update_last_seen(self, agent_id: str):
        """更新指定实例的最后可见时间"""
        registry_file = f"{self.comm_base}/registry/agents.json"
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                agents = json.load(f)
            if agent_id in agents:
                agents[agent_id]['last_seen'] = datetime.utcnow().isoformat()
                with open(registry_file, 'w') as f:
                    json.dump(agents, f, indent=2)
```

## 共享状态管理

```python
    def set_shared_state(self, key: str, value: dict):
        """设置共享状态"""
        # 使用文件锁保证原子性
        lock_file = f"{self.comm_base}/lock/{key}.lock"
        state_file = f"{self.comm_base}/state/{key}.json"

        with open(lock_file, 'w') as f:
            f.write(self.agent_id)

        try:
            state = {'key': key, 'value': value, 'updated_by': self.agent_id, 'updated_at': datetime.utcnow().isoformat()}
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        finally:
            if os.path.exists(lock_file):
                os.remove(lock_file)

    def get_shared_state(self, key: str) -> dict:
        """获取共享状态"""
        state_file = f"{self.comm_base}/state/{key}.json"
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                return json.load(f)
        return None

    def get_all_states(self) -> dict:
        """获取所有共享状态"""
        states = {}
        state_dir = f"{self.comm_base}/state"
        if os.path.exists(state_dir):
            for filename in os.listdir(state_dir):
                if filename.endswith('.json'):
                    key = filename[:-5]
                    with open(os.path.join(state_dir, filename), 'r') as f:
                        states[key] = json.load(f)
        return states
```

## 任务委托

```python
    def delegate_task(self, target_agent: str, task: dict) -> str:
        """委托任务给其他MaxClaw实例"""
        return self.send_message(
            recipient=target_agent,
            action='TASK_DELEGATE',
            payload={
                'task_id': str(uuid.uuid4()),
                'task_type': task.get('type'),
                'description': task.get('description'),
                'instructions': task.get('instructions'),
                'context': task.get('context', {}),
                'priority': task.get('priority', 'normal')
            },
            msg_type='request'
        )

    def _handle_task_delegate(self, msg: dict) -> dict:
        """处理收到的任务委托"""
        task = msg['payload']
        # 这里可以添加任务执行逻辑
        return {
            'recipient': msg['sender'],
            'action': 'TASK_RESPONSE',
            'payload': {
                'task_id': task['task_id'],
                'status': 'received',
                'message': f'Task {task["task_id"]} received and queued for processing'
            }
        }
```

## 使用示例

### 场景一：实例注册与发现

```python
# MaxClaw A 初始化并注册
agent_a = MaxClawComm("maxclaw-a")
agent_a.register()

# MaxClaw B 初始化并注册
agent_b = MaxClawComm("maxclaw-b")
agent_b.register()

# MaxClaw C 查询已注册实例
agent_c = MaxClawComm("maxclaw-c")
agents = agent_c.get_registered_agents()
# 返回: {"maxclaw-a": {...}, "maxclaw-b": {...}}
```

### 场景二：点对点消息传递

```python
# MaxClaw A 发送消息给 MaxClaw B
agent_a.send_message(
    recipient="maxclaw-b",
    action="DATA_REQUEST",
    payload={"data_type": "project_status"},
    msg_type="request"
)

# MaxClaw B 接收并处理
messages, responses = agent_b.process_messages()
for resp in responses:
    if resp['action'] == 'ACK':
        agent_b.send_message(**resp)
```

### 场景三：广播状态更新

```python
# 所有实例监听状态变更
agent_a.send_message(
    recipient="broadcast",
    action="SYNC_STATE",
    payload={"key": "project_progress", "value": 75},
    msg_type="event"
)
```

### 场景四：任务协作

```python
# MaxClaw A 委托复杂任务给 MaxClaw B
agent_a.delegate_task(
    target_agent="maxclaw-b",
    task={
        "type": "code_review",
        "description": "审查Pull Request #42",
        "instructions": "检查安全性问题",
        "context": {"pr_url": "..."}
    }
)
```

## 最佳实践

### 消息设计原则

1. **原子性**：每条消息应包含处理所需的所有信息，避免依赖外部状态
2. **幂等性**：接收端应能处理重复消息
3. **超时处理**：请求消息应设置合理的超时时间
4. **错误恢复**：实现消息重试机制

### 状态同步策略

1. **最终一致性**：接受短暂的状态不一致
2. **版本控制**：为状态添加版本号便于冲突检测
3. **按需同步**：仅同步需要的状态字段

### 性能优化

1. **批量处理**：定期批处理消息减少IO次数
2. **索引优化**：为高频查询的状态字段建立索引
3. **消息压缩**：大消息考虑压缩处理

## 错误处理

```python
class CommunicationError(Exception):
    """通信异常基类"""
    pass

class MessageDeliveryError(CommunicationError):
    """消息投递失败"""
    pass

class StateLockError(CommunicationError):
    """状态锁获取失败"""
    pass

def safe_send(comm, recipient, action, payload, retries=3):
    """带重试的消息发送"""
    for i in range(retries):
        try:
            return comm.send_message(recipient, action, payload)
        except Exception as e:
            if i == retries - 1:
                raise MessageDeliveryError(f"Failed after {retries} attempts: {e}")
            time.sleep(1 * (i + 1))
```

## 安全考虑

1. **消息签名**：对敏感消息添加数字签名
2. **访问控制**：限制只有授权实例才能访问共享状态
3. **审计日志**：记录所有通信行为便于追踪
4. **消息加密**：敏感数据使用加密传输

---

**作者**: MiniMax Agent
**版本**: 1.0.0
**更新日期**: 2026-04-10
