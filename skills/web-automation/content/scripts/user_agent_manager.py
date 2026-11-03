#!/usr/bin/env python3
"""
User-Agent 管理脚本
提供多平台 User-Agent 池和随机化选择功能
"""

import random
import json
from typing import List, Optional, Dict


class UserAgentManager:
    """User-Agent 管理类"""

    def __init__(self):
        self.user_agents = {
            "windows": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            ],
            "macos": [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
            ],
            "linux": [
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
            ],
            "mobile": [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Linux; Android 14; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (iPad; CPU OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
            ]
        }

        self.current_platform = "windows"
        self.used_agents = set()

    def set_platform(self, platform: str):
        """
        设置当前平台

        Args:
            platform: 平台类型（windows/macos/linux/mobile）
        """
        if platform not in self.user_agents:
            raise ValueError(f"不支持的平台: {platform}")
        self.current_platform = platform
        self.used_agents = set()  # 重置已使用的 UA

    def get_random_user_agent(self, platform: Optional[str] = None) -> str:
        """
        获取随机 User-Agent

        Args:
            platform: 平台类型（可选），默认使用当前平台

        Returns:
            随机 User-Agent 字符串
        """
        if platform:
            agents = self.user_agents.get(platform, self.user_agents["windows"])
        else:
            agents = self.user_agents[self.current_platform]

        # 过滤掉已使用的 UA
        available_agents = [ua for ua in agents if ua not in self.used_agents]

        # 如果所有 UA 都已使用，重置
        if not available_agents:
            available_agents = agents
            self.used_agents = set()

        # 随机选择
        user_agent = random.choice(available_agents)
        self.used_agents.add(user_agent)

        return user_agent

    def get_user_agent_list(self, platform: Optional[str] = None) -> List[str]:
        """
        获取指定平台的所有 User-Agent

        Args:
            platform: 平台类型（可选），默认使用当前平台

        Returns:
            User-Agent 列表
        """
        if platform:
            return self.user_agents.get(platform, [])
        else:
            return self.user_agents[self.current_platform]

    def add_custom_user_agent(self, platform: str, user_agent: str):
        """
        添加自定义 User-Agent

        Args:
            platform: 平台类型
            user_agent: User-Agent 字符串
        """
        if platform not in self.user_agents:
            self.user_agents[platform] = []
        self.user_agents[platform].append(user_agent)

    def get_platforms(self) -> List[str]:
        """
        获取所有支持的平台

        Returns:
            平台列表
        """
        return list(self.user_agents.keys())

    def get_config(self) -> Dict:
        """
        获取配置信息

        Returns:
            配置字典
        """
        return {
            "current_platform": self.current_platform,
            "available_platforms": self.get_platforms(),
            "user_agents_count": {
                platform: len(agents)
                for platform, agents in self.user_agents.items()
            },
            "used_agents_count": len(self.used_agents)
        }

    def export_config(self, output_path: str):
        """
        导出配置到文件

        Args:
            output_path: 输出文件路径
        """
        config = {
            "user_agents": self.user_agents,
            "current_platform": self.current_platform
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✓ 配置已导出到: {output_path}")

    def import_config(self, input_path: str):
        """
        从文件导入配置

        Args:
            input_path: 输入文件路径
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        self.user_agents = config.get("user_agents", self.user_agents)
        self.current_platform = config.get("current_platform", "windows")
        self.used_agents = set()

        print(f"✓ 配置已从 {input_path} 导入")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="User-Agent 管理工具")
    parser.add_argument(
        "--action",
        type=str,
        choices=["get", "list", "add", "export", "import", "config"],
        required=True,
        help="操作类型"
    )
    parser.add_argument(
        "--platform",
        type=str,
        choices=["windows", "macos", "linux", "mobile"],
        help="平台类型"
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        help="User-Agent 字符串"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="文件路径"
    )

    args = parser.parse_args()

    # 创建 User-Agent 管理器
    manager = UserAgentManager()

    # 执行操作
    if args.action == "get":
        user_agent = manager.get_random_user_agent(args.platform)
        print(user_agent)

    elif args.action == "list":
        user_agents = manager.get_user_agent_list(args.platform)
        for i, ua in enumerate(user_agents, 1):
            print(f"{i}. {ua}")

    elif args.action == "add":
        if not args.platform or not args.user_agent:
            print("错误: 添加操作需要 --platform 和 --user-agent 参数")
            return

        manager.add_custom_user_agent(args.platform, args.user_agent)
        print(f"✓ 已添加 User-Agent 到 {args.platform} 平台")

    elif args.action == "export":
        if not args.file:
            print("错误: 导出操作需要 --file 参数")
            return

        manager.export_config(args.file)

    elif args.action == "import":
        if not args.file:
            print("错误: 导入操作需要 --file 参数")
            return

        manager.import_config(args.file)

    elif args.action == "config":
        config = manager.get_config()
        print(json.dumps(config, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
