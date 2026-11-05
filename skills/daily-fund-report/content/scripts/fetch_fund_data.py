#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金净值数据获取模块
数据源：天天基金网（东方财富）公开API
"""

import requests
import time
import json
from typing import Dict, List, Optional


class FundDataFetcher:
    """基金净值数据获取器"""

    BASE_URL = "https://fundgz.1234567.com.cn/js/{}.js"
    HISTORY_URL = "https://api.fund.eastmoney.com/f10/lsjz"

    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://fund.eastmoney.com/"
        }

    def get_realtime_nav(self, fund_code: str) -> Optional[Dict]:
        """
        获取基金实时净值估算

        Args:
            fund_code: 基金代码（6位数字）

        Returns:
            包含净值信息的字典，失败返回None
        """
        url = self.BASE_URL.format(fund_code)

        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=10
                )

                if response.status_code == 200:
                    # 解析返回数据：jsonpgz回调({...})
                    text = response.text
                    if text.startswith("jsonpgz("):
                        text = text[7:-2]  # 去除 jsonpgz( 和 )

                    data = json.loads(text)
                    return {
                        "code": data.get("fundcode", fund_code),
                        "name": data.get("name", ""),
                        "nav": float(data.get("gsz", 0)),  # 估算净值
                        "nav_date": data.get("gztime", ""),  # 估算时间
                        "change_pct": float(data.get("gszzl", 0)),  # 日增长率(%)
                        "previous_nav": float(data.get("dwjz", 0))  # 昨日净值
                    }

            except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
                print(f"获取基金 {fund_code} 数据失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        return None

    def get_historical_nav(self, fund_code: str, days: int = 30) -> Optional[List[Dict]]:
        """
        获取基金历史净值

        Args:
            fund_code: 基金代码
            days: 获取天数

        Returns:
            历史净值列表
        """
        params = {
            "callback": "jQuery",
            "fundCode": fund_code,
            "pageIndex": 1,
            "pageSize": days,
            "startDate": "",
            "endDate": ""
        }

        try:
            response = requests.get(
                self.HISTORY_URL,
                params=params,
                headers=self.headers,
                timeout=15
            )

            if response.status_code == 200:
                text = response.text
                # 去除 jQuery({...}) 包装
                if text.startswith("jQuery"):
                    text = text[7:-1]

                data = json.loads(text)
                if data.get("Data"):
                    return [
                        {
                            "date": item.get("FSRQ", ""),
                            "nav": float(item.get("DWJZ", 0)),
                            "acc_nav": float(item.get("LJJZ", 0)),
                            "change_pct": float(item.get("JZZZL", 0))
                        }
                        for item in data["Data"]["LSJZList"]
                    ]

        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"获取基金 {fund_code} 历史数据失败: {e}")

        return None

    def batch_get_realtime(self, fund_codes: List[str], delay: float = 0.5) -> Dict[str, Dict]:
        """
        批量获取基金实时净值

        Args:
            fund_codes: 基金代码列表
            delay: 请求间隔（秒）

        Returns:
            {基金代码: 净值数据} 的字典
        """
        results = {}

        for code in fund_codes:
            data = self.get_realtime_nav(code)
            if data:
                results[code] = data
            time.sleep(delay)  # 避免请求过快

        return results


def fetch_fund_data_cli():
    """命令行入口"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python fetch_fund_data.py <基金代码>")
        print("示例: python fetch_fund_data.py 000001")
        sys.exit(1)

    fund_code = sys.argv[1]
    fetcher = FundDataFetcher()

    print(f"正在获取基金 {fund_code} 净值数据...")
    data = fetcher.get_realtime_nav(fund_code)

    if data:
        print("\n获取成功:")
        print(f"  基金代码: {data['code']}")
        print(f"  基金名称: {data['name']}")
        print(f"  估算净值: {data['nav']:.4f}")
        print(f"  昨日净值: {data['previous_nav']:.4f}")
        print(f"  日增长率: {data['change_pct']:+.2f}%")
        print(f"  估算时间: {data['nav_date']}")
    else:
        print("获取失败，请检查基金代码是否正确")


if __name__ == "__main__":
    fetch_fund_data_cli()
