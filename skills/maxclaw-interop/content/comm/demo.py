#!/usr/bin/env python3
"""
MaxClaw Interop Demo Script

演示多个MaxClaw实例之间的通信和互操作功能。
"""

import sys
import time
import threading
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from comm import MaxClawComm


def simulate_maxclaw_agent(agent_id: str, delay: float = 0):
    """
    模拟一个MaxClaw代理的行为

    Args:
        agent_id: 代理标识符
        delay: 初始延迟（秒）
    """
    if delay > 0:
        time.sleep(delay)

    print(f"\n{'='*60}")
    print(f"  MaxClaw Agent: {agent_id} 启动")
    print(f"{'='*60}")

    # 创建通信管理器
    comm = MaxClawComm(agent_id)

    # 等待其他代理注册
    time.sleep(0.5)

    # 获取所有已注册的代理
    agents = comm.get_registered_agents()
    print(f"\n[{agent_id}] 已注册的代理: {list(agents.keys())}")

    # 如果有其他代理，进行通信测试
    other_agents = [a for a in agents.keys() if a != agent_id]

    if not other_agents:
        print(f"\n[{agent_id}] 没有发现其他代理，结束")
        return

    # 测试1: 点对点消息
    print(f"\n[{agent_id}] 测试1: 发送点对点消息给 {other_agents[0]}")
    msg_id = comm.send_message(
        recipient=other_agents[0],
        action='DATA_REQUEST',
        payload={'data_type': 'status', 'query': 'What is your status?'}
    )
    print(f"[{agent_id}] 消息已发送，ID: {msg_id}")

    # 测试2: 广播消息
    print(f"\n[{agent_id}] 测试2: 广播状态更新")
    comm.broadcast_state(
        key=f'agent_{agent_id}_status',
        value={'status': 'active', 'timestamp': time.time()}
    )
    print(f"[{agent_id}] 广播已发送")

    # 测试3: 状态共享
    print(f"\n[{agent_id}] 测试3: 设置共享状态")
    comm.set_shared_state('global_counter', {
        'value': 0,
        'last_updated_by': agent_id
    })
    print(f"[{agent_id}] 共享状态已设置")

    # 测试4: 任务委托
    if len(other_agents) > 1:
        print(f"\n[{agent_id}] 测试4: 委托任务给 {other_agents[1]}")
        task_id = comm.delegate_task(
            target_agent=other_agents[1],
            task_type='analysis',
            description='分析项目代码质量',
            instructions='请检查代码中的潜在问题',
            context={'project': 'demo'}
        )
        print(f"[{agent_id}] 任务已委托，ID: {task_id}")

    # 测试5: PING测试
    print(f"\n[{agent_id}] 测试5: PING {other_agents[0]}")
    online = comm.ping(other_agents[0], timeout=3)
    print(f"[{agent_id}] {other_agents[0]} 在线状态: {online}")

    # 处理接收到的消息
    time.sleep(0.5)
    print(f"\n[{agent_id}] 检查收件箱...")
    messages, responses = comm.process_messages()

    if messages:
        print(f"[{agent_id}] 收到 {len(messages)} 条消息:")
        for msg in messages:
            print(f"  - {msg['action']} from {msg['sender']}")
    else:
        print(f"[{agent_id}] 没有未处理的消息")

    if responses:
        print(f"[{agent_id}] 发送 {len(responses)} 条响应")
        comm.send_responses(responses)

    # 打印最终状态
    print(f"\n[{agent_id}] 最终状态:")
    states = comm.get_all_states()
    for key, state in states.items():
        print(f"  {key}: {state.get('value')}")

    peer_status = comm.get_peer_status()
    print(f"  对等代理状态: {peer_status}")

    print(f"\n[{agent_id}] 演示完成")
    return comm


def main():
    """主函数：模拟三个MaxClaw代理"""
    print("\n" + "="*60)
    print("  MaxClaw Interoperability Demo")
    print("  模拟三个MaxClaw实例之间的通信")
    print("="*60)

    # 启动三个代理（使用线程模拟）
    agents = []

    # 代理1: 立即启动
    t1 = threading.Thread(target=lambda: agents.append(simulate_maxclaw_agent("maxclaw-1", 0)))
    t1.start()

    # 代理2: 延迟0.5秒启动
    t2 = threading.Thread(target=lambda: agents.append(simulate_maxclaw_agent("maxclaw-2", 0.5)))
    t2.start()

    # 代理3: 延迟1秒启动
    t3 = threading.Thread(target=lambda: agents.append(simulate_maxclaw_agent("maxclaw-3", 1.0)))
    t3.start()

    # 等待所有线程完成
    t1.join()
    t2.join()
    t3.join()

    # 最后一个代理检查所有共享状态
    print("\n" + "="*60)
    print("  最终共享状态总览")
    print("="*60)

    final_comm = MaxClawComm("demo-viewer", auto_register=False)
    all_states = final_comm.get_all_states()
    all_agents = final_comm.get_registered_agents()

    print(f"\n已注册的代理 ({len(all_agents)}):")
    for agent_id, info in all_agents.items():
        print(f"  - {agent_id}: {info.get('status')}")

    print(f"\n共享状态 ({len(all_states)}):")
    for key, state in all_states.items():
        print(f"  - {key}: {state.get('value')}")

    print("\n" + "="*60)
    print("  演示完成！")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
