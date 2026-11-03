#!/usr/bin/env python3
"""
Gitee 代码提交脚本

执行 git 操作将本地代码提交到 Gitee 仓库
支持首次初始化和后续更新

注意: 此脚本需要系统安装 git 命令
"""

import os
import sys
import argparse
import subprocess


def run_command(cmd: str, cwd: str = None, check: bool = True):
    """
    执行 shell 命令

    参数:
        cmd: 要执行的命令
        cwd: 工作目录
        check: 是否检查返回码

    返回:
        str: 命令输出
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"命令执行失败: {cmd}\n错误信息: {e.stderr}")


def check_git_installed():
    """检查系统是否安装 git"""
    try:
        run_command("git --version")
        return True
    except Exception:
        return False


def init_repo(local_path: str):
    """
    初始化 git 仓库

    参数:
        local_path: 本地项目路径
    """
    print(f"初始化 git 仓库: {local_path}")
    run_command("git init", cwd=local_path)


def check_git_config(local_path: str):
    """
    检查 git 配置(user.name 和 user.email)

    参数:
        local_path: 本地项目路径

    返回:
        bool: 配置是否完整
    """
    try:
        name = run_command("git config user.name", cwd=local_path)
        email = run_command("git config user.email", cwd=local_path)

        if not name.strip() or not email.strip():
            return False
        return True
    except Exception:
        return False


def add_files(local_path: str):
    """
    添加所有文件到暂存区

    参数:
        local_path: 本地项目路径
    """
    print("添加文件到暂存区...")
    run_command("git add .", cwd=local_path)


def commit_changes(local_path: str, message: str):
    """
    提交更改

    参数:
        local_path: 本地项目路径
        message: 提交信息
    """
    print(f"提交更改: {message}")
    run_command(f'git commit -m "{message}"', cwd=local_path)


def add_remote(local_path: str, repo_url: str, remote_name: str = "origin"):
    """
    添加远程仓库

    参数:
        local_path: 本地项目路径
        repo_url: 远程仓库 URL
        remote_name: 远程仓库名称
    """
    print(f"添加远程仓库: {repo_url}")
    run_command(f"git remote add {remote_name} {repo_url}", cwd=local_path)


def push_to_remote(local_path: str, branch: str = "main", remote_name: str = "origin"):
    """
    推送到远程仓库

    参数:
        local_path: 本地项目路径
        branch: 分支名称
        remote_name: 远程仓库名称
    """
    print(f"推送到远程仓库 {remote_name}/{branch}...")
    run_command(f"git push -u {remote_name} {branch}", cwd=local_path)


def commit_to_gitee(local_path: str, repo_url: str, commit_message: str, branch: str = "main"):
    """
    完整的提交流程

    参数:
        local_path: 本地项目路径
        repo_url: Gitee 仓库 URL
        commit_message: 提交信息
        branch: 分支名称
    """
    # 检查 git 是否安装
    if not check_git_installed():
        raise Exception("系统未安装 git，请先安装 git")

    # 检查本地路径是否存在
    if not os.path.exists(local_path):
        raise Exception(f"本地路径不存在: {local_path}")

    # 检查是否已经是 git 仓库
    git_dir = os.path.join(local_path, ".git")
    is_repo = os.path.exists(git_dir)

    if not is_repo:
        # 初始化仓库
        init_repo(local_path)
    else:
        print(f"检测到现有 git 仓库: {local_path}")

    # 检查 git 配置
    if not check_git_config(local_path):
        print("⚠️  警告: 未检测到 git 用户配置，建议先配置:")
        print("   git config --global user.name \"Your Name\"")
        print("   git config --global user.email \"your.email@example.com\"")

    # 添加文件
    add_files(local_path)

    # 提交更改
    commit_changes(local_path, commit_message)

    # 检查是否已有远程仓库
    try:
        remotes = run_command("git remote", cwd=local_path)
        if "origin" in remotes:
            print("已存在远程仓库 origin，将直接推送")
        else:
            add_remote(local_path, repo_url)
    except Exception:
        add_remote(local_path, repo_url)

    # 推送到远程
    push_to_remote(local_path, branch)

    print("✓ 代码提交成功!")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="提交代码到 Gitee 仓库")
    parser.add_argument("--local-path", default=".", help="本地项目路径(默认为当前目录)")
    parser.add_argument("--repo-url", required=True, help="Gitee 仓库 URL")
    parser.add_argument("--commit-message", required=True, help="提交信息")
    parser.add_argument("--branch", default="main", help="分支名称(默认为 main)")

    args = parser.parse_args()

    try:
        # 转换为绝对路径
        local_path = os.path.abspath(args.local_path)

        # 执行提交
        commit_to_gitee(
            local_path=local_path,
            repo_url=args.repo_url,
            commit_message=args.commit_message,
            branch=args.branch
        )

    except Exception as e:
        print(f"✗ 提交失败: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
