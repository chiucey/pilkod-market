#!/usr/bin/env python3
"""
MaxClaw Interop 使用示例

展示各种通信场景的代码示例。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comm import MaxClawComm, safe_send


def example_basic_usage():
    """基本使用示例"""
    # 初始化通信管理器
    comm = MaxClawComm("my-agent-id")

    # 发送消息
    comm.send_message(
        recipient="other-agent",
        action="GREETING",
        payload={"message": "Hello!"}
    )

    # 接收消息
    messages, responses = comm.process_messages()

    # 发送响应
    comm.send_responses(responses)


def example_state_sharing():
    """状态共享示例"""
    comm = MaxClawComm("my-agent-id")

    # 设置共享状态
    comm.set_shared_state("project_info", {
        "name": "My Project",
        "version": "1.0.0"
    })

    # 获取共享状态
    state = comm.get_shared_state("project_info")

    # 获取所有状态
    all_states = comm.get_all_states()


def example_task_delegation():
    """任务委托示例"""
    comm = MaxClawComm("my-agent-id")

    # 委托任务
    comm.delegate_task(
        target_agent="worker-agent",
        task_type="data_processing",
        description="处理数据文件",
        instructions="读取CSV文件并进行统计分析",
        context={"file_path": "/data/input.csv"}
    )


def example_broadcast():
    """广播示例"""
    comm = MaxClawComm("my-agent-id")

    # 广播状态更新
    comm.broadcast_state(
        key="system_status",
        value={"status": "ready", "load": 0.5}
    )


def example_peer_discovery():
    """对等发现示例"""
    comm = MaxClawComm("my-agent-id")

    # 获取所有已注册的代理
    agents = comm.get_registered_agents()

    # 获取对等代理状态
    peer_status = comm.get_peer_status()

    # PING某个代理
    is_online = comm.ping("other-agent")


def example_request_response():
    """请求-响应模式示例"""
    comm = MaxClawComm("my-agent-id")

    # 发送请求
    msg_id = comm.request_data(
        target_agent="data-agent",
        data_type="analytics",
        filters={"date_range": "last_7_days"}
    )

    # 等待并处理响应
    import time
    for _ in range(10):
        messages, responses = comm.process_messages()
        for msg in messages:
            if msg.get('action') == 'DATA_RESPONSE':
                data = msg['payload']['data']
                print(f"Received data: {data}")
        time.sleep(0.5)


if __name__ == '__main__':
    print("请参考 SKILL.md 查看完整的使用文档")
