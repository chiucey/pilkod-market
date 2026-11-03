#!/usr/bin/env python3
"""
Gitee 仓库创建脚本

使用 Gitee API v5 创建新仓库
支持 Personal Access Token 认证

授权方式: ApiKey (Personal Access Token)
凭证Key: COZE_GITEE_TOKEN_7628914829545275402
"""

import os
import sys
import argparse
from coze_workload_identity import requests


def get_access_token():
    """
    从环境变量获取 Personal Access Token

    返回:
        str: access_token
    """
    skill_id = "7628914829545275402"
    access_token = os.getenv("COZE_GITEE_TOKEN_" + skill_id)

    if not access_token:
        raise ValueError("缺少 Gitee Personal Access Token 配置，请先配置凭证")

    return access_token


def create_repository(name: str, description: str, private: bool, auto_init: bool):
    """
    调用 Gitee API 创建仓库

    参数:
        name: 仓库名称
        description: 仓库描述
        private: 是否为私有仓库
        auto_init: 是否自动初始化(创建 README)

    返回:
        dict: 仓库信息
    """
    # 获取 access_token
    access_token = get_access_token()

    # 构建 API URL
    url = "https://gitee.com/api/v5/user/repos"

    # 请求头
    headers = {
        "Authorization": f"token {access_token}",
        "Content-Type": "application/json"
    }

    # 请求参数
    params = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": auto_init
    }

    # 发起请求
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)

        # 检查 HTTP 状态码
        if response.status_code >= 400:
            raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

        data = response.json()

        # 检查 Gitee API 错误
        if isinstance(data, dict) and "error" in data:
            raise Exception(f"API错误: {data.get('message', '未知错误')}")

        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"API调用失败: {str(e)}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="创建 Gitee 仓库")
    parser.add_argument("--name", required=True, help="仓库名称")
    parser.add_argument("--description", default="", help="仓库描述")
    parser.add_argument("--private", type=lambda x: x.lower() in ['true', '1', 'yes'], default=False, help="是否为私有仓库")
    parser.add_argument("--auto-init", type=lambda x: x.lower() in ['true', '1', 'yes'], default=True, help="是否自动初始化(创建 README)")

    args = parser.parse_args()

    try:
        # 创建仓库
        print(f"正在创建仓库: {args.name}...")
        repo_info = create_repository(
            name=args.name,
            description=args.description,
            private=args.private,
            auto_init=args.auto_init
        )

        # 输出结果
        print("✓ 仓库创建成功!")
        print(f"  仓库名称: {repo_info.get('name')}")
        print(f"  仓库地址: {repo_info.get('html_url')}")
        print(f"  克隆地址: {repo_info.get('clone_url')}")
        print(f"  是否私有: {'是' if repo_info.get('private') else '否'}")

        # 返回克隆 URL 供后续使用
        return repo_info.get('clone_url')

    except Exception as e:
        print(f"✗ 创建仓库失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
