#!/usr/bin/env python3
"""
PPT转培训视频 - 快速验证脚本
验证PPT文件和生成视频的基本可用性
"""

import os
import sys
import json
import subprocess

def validate_ppt_file(ppt_path):
    """验证PPT文件是否存在且格式正确"""
    if not os.path.exists(ppt_path):
        return False, f"文件不存在: {ppt_path}"

    if not ppt_path.endswith('.pptx'):
        return False, "只支持 .pptx 格式"

    return True, "PPT文件验证通过"

def validate_ffmpeg():
    """验证FFmpeg是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                             capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def main():
    ppt_path = sys.argv[1] if len(sys.argv) > 1 else None

    print("=== PPT转培训视频验证 ===")

    if ppt_path:
        valid, msg = validate_ppt_file(ppt_path)
        print(f"PPT验证: {msg}")
        if not valid:
            sys.exit(1)

    if validate_ffmpeg():
        print("FFmpeg验证: 已安装")
    else:
        print("FFmpeg验证: 未安装（视频合并功能不可用）")

    print("=== 验证完成 ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
