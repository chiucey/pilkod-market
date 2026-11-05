#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

import os
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = ROOT_DIR / 'data'
CONFIG_DIR = ROOT_DIR / 'config'
SRC_DIR = ROOT_DIR / 'src'

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# 爬虫配置
SCRAPER_CONFIG = {
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 5,
    'max_pages': 5,
    'delay_between_requests': 2,
}

# 调度配置
SCHEDULER_CONFIG = {
    'default_hour': 8,
    'default_minute': 0,
    'check_interval': 60,  # 检查间隔（秒）
}

# 数据配置
DATA_CONFIG = {
    'csv_file': DATA_DIR / 'appointments.csv',
    'state_file': DATA_DIR / 'state.json',
    'log_file': DATA_DIR / 'upload_log.csv',
    'template_file': DATA_DIR / 'template.csv',
}

# CSV字段
CSV_FIELDS = [
    'id',
    'name',
    'position',
    'action',
    'date',
    'doc_no',
    'source',
    'source_url',
    'crawl_time',
    'batch_id',
    'import_method'
]
