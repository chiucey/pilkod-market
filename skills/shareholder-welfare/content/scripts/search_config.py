#!/usr/bin/env python3
"""
搜索配置脚本
获取股东福利搜索所需的关键词和配置参数
"""

import json
from datetime import datetime, timedelta


def get_search_config():
    """
    获取搜索配置
    返回包含搜索关键词、日期范围和排除关键词的字典
    """
    # 计算近30天的日期范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    config = {
        "search_keywords": [
            "回馈股东",
            "股东福利",
            "股东赠礼",
            "股东赠送",
            "股东申领",
            "股东专享",
            "股东试用品",
            "股东礼品",
            "股东权益",
            "股东活动"
        ],
        "exclude_keywords": [
            "分红",
            "派息",
            "送转",
            "股权分派",
            "现金红利",
            "股息",
            "红利发放"
        ],
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "days": 30
        },
        "official_sources": [
            "cninfo.com.cn",
            "szse.cn",
            "sse.com.cn"
        ],
        "search_tips": [
            "优先搜索 site:cninfo.com.cn 或 site:szse.cn 或 site:sse.com.cn",
            "结合日期范围过滤结果",
            "排除包含分红、派息、送转等关键词的结果"
        ]
    }

    return config


def main():
    """主函数：输出搜索配置"""
    config = get_search_config()
    print(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
