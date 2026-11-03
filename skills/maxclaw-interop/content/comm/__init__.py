"""
MaxClaw Interoperability Communication Library

提供多个MaxClaw实例之间的消息传递、状态共享和互操作功能。
支持跨Session和Workspace的可靠通信。
"""

import json
import os
import uuid
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class CommunicationError(Exception):
    """通信异常基类"""
    pass


class MessageDeliveryError(CommunicationError):
    """消息投递失败"""
    pass


class StateLockError(CommunicationError):
    """状态锁获取失败"""
    pass


class MaxClawComm:
    """
    MaxClaw实例间通信管理器

    提供消息队列、状态共享、任务委托等核心功能。
    使用文件系统作为消息中转存储，支持跨Session持久化。
    """

    def __init__(
        self,
        agent_id: str,
        comm_base: str = "/workspace/temp-skills/maxclaw-interop/comm",
        auto_register: bool = True
    ):
        """
        初始化通信管理器

        Args:
            agent_id: 本实例唯一标识符
            comm_base: 通信基础目录
            auto_register: 是否自动注册到实例注册表
        """
        self.agent_id = agent_id
        self.comm_base = Path(comm_base)
        self._ensure_dirs()
        self._lock = threading.Lock()

        if auto_register:
            self.register()

    def _ensure_dirs(self):
        """确保所有必要的目录存在"""
        for subdir in ['inbox', 'outbox', 'state', 'lock', 'registry']:
            (self.comm_base / subdir).mkdir(parents=True, exist_ok=True)
        # 为每个实例创建独立的收件箱
        (self.comm_base / 'inbox' / self.agent_id).mkdir(parents=True, exist_ok=True)

    def register(self) -> bool:
        """
        注册本实例到注册表

        Returns:
            注册是否成功
        """
        registry_file = self.comm_base / 'registry' / 'agents.json'
        agents = {}

        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                agents = json.load(f)

        agents[self.agent_id] = {
            'agent_id': self.agent_id,
            'registered_at': datetime.utcnow().isoformat(),
            'last_seen': datetime.utcnow().isoformat(),
            'status': 'active',
            'version': '1.0'
        }

        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump(agents, f, indent=2, ensure_ascii=False)

        return True

    def heartbeat(self):
        """发送心跳，更新最后可见时间"""
        self._update_last_seen(self.agent_id)

    def _update_last_seen(self, agent_id: str):
        """更新指定实例的最后可见时间"""
        registry_file = self.comm_base / 'registry' / 'agents.json'
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                agents = json.load(f)

            if agent_id in agents:
                agents[agent_id]['last_seen'] = datetime.utcnow().isoformat()
                with open(registry_file, 'w', encoding='utf-8') as f:
                    json.dump(agents, f, indent=2, ensure_ascii=False)

    def get_registered_agents(self) -> Dict[str, Dict]:
        """
        获取所有已注册的MaxClaw实例

        Returns:
            包含所有已注册实例信息的字典
        """
        registry_file = self.comm_base / 'registry' / 'agents.json'
        if registry_file.exists():
            with open(registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def send_message(
        self,
        recipient: str,
        action: str,
        payload: Dict[str, Any],
        msg_type: str = "message",
        correlation_id: Optional[str] = None
    ) -> str:
        """
        发送消息到指定接收者

        Args:
            recipient: 目标Agent ID或'broadcast'
            action: 操作类型
            payload: 消息载荷
            msg_type: 消息类型 (message/request/response/event)
            correlation_id: 关联消息ID（用于请求-响应对）

        Returns:
            发送消息的ID
        """
        msg_id = str(uuid.uuid4())

        msg = {
            'msg_id': msg_id,
            'timestamp': datetime.utcnow().isoformat(),
            'sender': self.agent_id,
            'recipient': recipient,
            'msg_type': msg_type,
            'action': action,
            'payload': payload,
            'correlation_id': correlation_id
        }

        with self._lock:
            if recipient == 'broadcast':
                self._propagate_broadcast(msg)
            else:
                # 写入目标实例的收件箱
                outbox_file = self.comm_base / 'outbox' / f'{msg_id}.json'
                with open(outbox_file, 'w', encoding='utf-8') as f:
                    json.dump(msg, f, indent=2, ensure_ascii=False)

                # 同步到接收者的inbox
                inbox_file = self.comm_base / 'inbox' / recipient / f'{msg_id}.json'
                inbox_file.parent.mkdir(parents=True, exist_ok=True)
                with open(inbox_file, 'w', encoding='utf-8') as f:
                    json.dump(msg, f, indent=2, ensure_ascii=False)

        return msg_id

    def _propagate_broadcast(self, msg: Dict):
        """将广播消息分发到所有已注册实例"""
        agents = self.get_registered_agents()

        for agent_id in agents.keys():
            if agent_id != self.agent_id:
                inbox_file = self.comm_base / 'inbox' / agent_id / f'{msg["msg_id"]}.json'
                inbox_file.parent.mkdir(parents=True, exist_ok=True)
                with open(inbox_file, 'w', encoding='utf-8') as f:
                    json.dump(msg, f, indent=2, ensure_ascii=False)

        # 同时保留在outbox作为记录
        outbox_file = self.comm_base / 'outbox' / f'{msg["msg_id"]}.json'
        with open(outbox_file, 'w', encoding='utf-8') as f:
            json.dump(msg, f, indent=2, ensure_ascii=False)

    def receive_messages(self) -> List[Dict]:
        """
        接收所有发给本实例的消息

        Returns:
            消息列表，按时间戳排序
        """
        inbox_dir = self.comm_base / 'inbox' / self.agent_id
        inbox_dir.mkdir(parents=True, exist_ok=True)

        messages = []
        with self._lock:
            for filename in os.listdir(inbox_dir):
                if filename.endswith('.json'):
                    filepath = inbox_dir / filename
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            messages.append(json.load(f))
                        filepath.unlink()  # 处理后删除
                    except Exception:
                        pass

        messages.sort(key=lambda x: x['timestamp'])
        return messages

    def process_messages(
        self,
        handlers: Optional[Dict[str, callable]] = None
    ) -> tuple:
        """
        处理接收到的消息

        Args:
            handlers: 自定义消息处理器字典 {action: handler_function}

        Returns:
            (messages, responses) 元组
        """
        messages = self.receive_messages()
        responses = []
        unhandled = []

        default_handlers = {
            'PING': self._handle_ping,
            'DATA_REQUEST': self._handle_data_request,
            'TASK_DELEGATE': self._handle_task_delegate,
            'REGISTER': self._handle_register,
            'SYNC_STATE': self._handle_sync_state
        }

        if handlers:
            default_handlers.update(handlers)

        for msg in messages:
            self._update_last_seen(msg['sender'])
            handler = default_handlers.get(msg['action'])

            if handler:
                response = handler(msg)
                if response:
                    responses.append(response)
            else:
                # 默认处理：发送确认
                responses.append({
                    'recipient': msg['sender'],
                    'action': 'ACK',
                    'payload': {'original_msg_id': msg['msg_id']}
                })
                unhandled.append(msg)

        return messages, responses

    def _handle_ping(self, msg: Dict) -> Dict:
        """处理PING请求"""
        return {
            'recipient': msg['sender'],
            'action': 'PONG',
            'payload': {
                'original_msg_id': msg['msg_id'],
                'responder': self.agent_id,
                'timestamp': datetime.utcnow().isoformat()
            }
        }

    def _handle_data_request(self, msg: Dict) -> Dict:
        """处理数据请求"""
        data_type = msg['payload'].get('data_type')
        # 返回请求的数据或错误信息
        return {
            'recipient': msg['sender'],
            'action': 'DATA_RESPONSE',
            'payload': {
                'original_msg_id': msg['msg_id'],
                'data_type': data_type,
                'data': None,  # 这里可以接入实际数据源
                'status': 'received'
            },
            'correlation_id': msg['msg_id']
        }

    def _handle_task_delegate(self, msg: Dict) -> Dict:
        """处理任务委托"""
        task = msg['payload']
        return {
            'recipient': msg['sender'],
            'action': 'TASK_RESPONSE',
            'payload': {
                'task_id': task.get('task_id'),
                'status': 'received',
                'message': f'Task {task.get("task_id")} received by {self.agent_id}',
                'estimated_completion': None
            },
            'correlation_id': msg['msg_id']
        }

    def _handle_register(self, msg: Dict) -> Dict:
        """处理注册请求"""
        return {
            'recipient': msg['sender'],
            'action': 'REGISTER_RESPONSE',
            'payload': {
                'registered': True,
                'agent_id': self.agent_id,
                'peers': list(self.get_registered_agents().keys())
            },
            'correlation_id': msg['msg_id']
        }

    def _handle_sync_state(self, msg: Dict) -> Dict:
        """处理状态同步请求"""
        return {
            'recipient': msg['sender'],
            'action': 'STATE_SYNC_RESPONSE',
            'payload': {
                'states': self.get_all_states()
            },
            'correlation_id': msg['msg_id']
        }

    def send_responses(self, responses: List[Dict]):
        """批量发送响应消息"""
        for resp in responses:
            self.send_message(
                recipient=resp['recipient'],
                action=resp['action'],
                payload=resp['payload'],
                msg_type='response',
                correlation_id=resp.get('correlation_id')
            )

    def set_shared_state(self, key: str, value: Any) -> bool:
        """
        设置共享状态（带文件锁）

        Args:
            key: 状态键名
            value: 状态值

        Returns:
            是否成功
        """
        lock_file = self.comm_base / 'lock' / f'{key}.lock'
        state_file = self.comm_base / 'state' / f'{key}.json'

        max_retries = 10
        for _ in range(max_retries):
            try:
                with open(lock_file, 'w', encoding='utf-8') as f:
                    f.write(self.agent_id)
                break
            except FileExistsError:
                time.sleep(0.1)
        else:
            raise StateLockError(f"Failed to acquire lock for key: {key}")

        try:
            state = {
                'key': key,
                'value': value,
                'updated_by': self.agent_id,
                'updated_at': datetime.utcnow().isoformat(),
                'version': int(datetime.utcnow().timestamp())
            }
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        finally:
            if lock_file.exists():
                lock_file.unlink()

    def get_shared_state(self, key: str) -> Optional[Dict]:
        """
        获取共享状态

        Args:
            key: 状态键名

        Returns:
            状态数据或None
        """
        state_file = self.comm_base / 'state' / f'{key}.json'
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def get_all_states(self) -> Dict[str, Dict]:
        """
        获取所有共享状态

        Returns:
            所有状态的字典
        """
        states = {}
        state_dir = self.comm_base / 'state'

        if state_dir.exists():
            for filepath in state_dir.glob('*.json'):
                key = filepath.stem
                with open(filepath, 'r', encoding='utf-8') as f:
                    states[key] = json.load(f)

        return states

    def delete_shared_state(self, key: str) -> bool:
        """
        删除共享状态

        Args:
            key: 状态键名

        Returns:
            是否成功
        """
        state_file = self.comm_base / 'state' / f'{key}.json'
        if state_file.exists():
            state_file.unlink()
            return True
        return False

    def delegate_task(
        self,
        target_agent: str,
        task_type: str,
        description: str,
        instructions: str,
        context: Optional[Dict] = None,
        priority: str = "normal"
    ) -> str:
        """
        委托任务给其他MaxClaw实例

        Args:
            target_agent: 目标Agent ID
            task_type: 任务类型
            description: 任务描述
            instructions: 执行指令
            context: 上下文信息
            priority: 优先级

        Returns:
            消息ID
        """
        task_id = str(uuid.uuid4())
        return self.send_message(
            recipient=target_agent,
            action='TASK_DELEGATE',
            payload={
                'task_id': task_id,
                'task_type': task_type,
                'description': description,
                'instructions': instructions,
                'context': context or {},
                'priority': priority,
                'delegated_by': self.agent_id,
                'delegated_at': datetime.utcnow().isoformat()
            },
            msg_type='request'
        )

    def request_data(
        self,
        target_agent: str,
        data_type: str,
        filters: Optional[Dict] = None
    ) -> str:
        """
        请求其他实例的数据

        Args:
            target_agent: 目标Agent ID
            data_type: 数据类型
            filters: 过滤条件

        Returns:
            消息ID
        """
        return self.send_message(
            recipient=target_agent,
            action='DATA_REQUEST',
            payload={
                'data_type': data_type,
                'filters': filters or {}
            },
            msg_type='request'
        )

    def broadcast_state(self, key: str, value: Any):
        """
        广播状态更新

        Args:
            key: 状态键名
            value: 状态值
        """
        self.set_shared_state(key, value)
        self.send_message(
            recipient='broadcast',
            action='STATE_UPDATE',
            payload={
                'key': key,
                'value': value,
                'updated_by': self.agent_id
            },
            msg_type='event'
        )

    def ping(self, target_agent: str, timeout: int = 5) -> bool:
        """
        ping目标Agent

        Args:
            target_agent: 目标Agent ID
            timeout: 超时时间（秒）

        Returns:
            是否在线
        """
        msg_id = self.send_message(
            recipient=target_agent,
            action='PING',
            payload={},
            msg_type='request'
        )

        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = self.receive_messages()
            for msg in messages:
                if msg.get('action') == 'PONG' and msg.get('correlation_id') == msg_id:
                    return True
            time.sleep(0.5)

        return False

    def get_peer_status(self) -> Dict[str, Dict]:
        """
        获取所有对等实例的状态

        Returns:
            各实例状态信息
        """
        agents = self.get_registered_agents()
        status = {}

        now = datetime.utcnow()
        for agent_id, info in agents.items():
            if agent_id == self.agent_id:
                continue

            last_seen = datetime.fromisoformat(info.get('last_seen', '1970-01-01'))
            diff_seconds = (now - last_seen).total_seconds()

            status[agent_id] = {
                'online': diff_seconds < 60,  # 60秒内有响应视为在线
                'last_seen': info.get('last_seen'),
                'status': info.get('status', 'unknown')
            }

        return status


def safe_send(
    comm: MaxClawComm,
    recipient: str,
    action: str,
    payload: Dict,
    retries: int = 3
) -> str:
    """
    带重试的消息发送

    Args:
        comm: 通信管理器实例
        recipient: 接收者ID
        action: 操作类型
        payload: 消息载荷
        retries: 重试次数

    Returns:
        消息ID

    Raises:
        MessageDeliveryError: 重试耗尽后失败
    """
    for i in range(retries):
        try:
            return comm.send_message(recipient, action, payload)
        except Exception as e:
            if i == retries - 1:
                raise MessageDeliveryError(f"Failed after {retries} attempts: {e}")
            time.sleep(1 * (i + 1))

    raise MessageDeliveryError("Unexpected error in safe_send")


# 导出主要类和函数
__all__ = [
    'MaxClawComm',
    'CommunicationError',
    'MessageDeliveryError',
    'StateLockError',
    'safe_send'
]
