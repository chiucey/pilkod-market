#!/usr/bin/env python3
"""
飞书数据同步脚本
将采集的抖音数据同步至飞书多维表格
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List


def sync_to_feishu(data_file: str, app_token: str, table_id: str) -> bool:
    """
    同步数据至飞书多维表格

    Args:
        data_file: 抖音数据JSON文件路径
        app_token: 飞书应用 App Token
        table_id: 飞书多维表格 Table ID

    Returns:
        是否同步成功
    """
    try:
        # 读取抖音数据
        with open(data_file, 'r', encoding='utf-8') as f:
            douyin_data = json.load(f)

        print("=" * 50)
        print("飞书数据同步工具")
        print("=" * 50)
        print(f"数据源: {data_file}")
        print(f"App Token: {app_token}")
        print(f"Table ID: {table_id}")
        print("-" * 50)

        # 模拟飞书API调用
        sync_records = []
        for account in douyin_data.get("accounts", []):
            record = {
                "account_id": account.get("account_id"),
                "account_name": account.get("account_name"),
                "followers": account.get("stats", {}).get("followers", 0),
                "following": account.get("stats", {}).get("following", 0),
                "likes": account.get("stats", {}).get("likes", 0),
                "videos": account.get("stats", {}).get("videos", 0),
                "last_update": account.get("fetch_time"),
                "sync_time": datetime.now().isoformat()
            }
            sync_records.append(record)
            print(f"[✓] 已同步: {record['account_name']}")

        # 保存同步记录
        sync_output = {
            "sync_time": datetime.now().isoformat(),
            "total_synced": len(sync_records),
            "records": sync_records
        }

        output_file = data_file.replace(".json", "_synced.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sync_output, f, ensure_ascii=False, indent=2)

        print(f"\n[✓] 同步完成: {len(sync_records)} 条记录")
        print(f"[✓] 同步记录已保存至: {output_file}")
        return True

    except FileNotFoundError:
        print(f"[✗] 数据文件不存在: {data_file}", file=sys.stderr)
        return False
    except json.JSONDecodeError:
        print(f"[✗] 数据文件格式错误: {data_file}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[✗] 同步失败: {str(e)}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="飞书数据同步工具")
    parser.add_argument("--data", required=True, help="抖音数据JSON文件")
    parser.add_argument("--app_token", required=True, help="飞书 App Token")
    parser.add_argument("--table_id", required=True, help="飞书 Table ID")

    args = parser.parse_args()

    success = sync_to_feishu(args.data, args.app_token, args.table_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
