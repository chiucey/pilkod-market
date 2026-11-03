# -*- coding: utf-8 -*-
"""
技能配置文件
"""

import os

# 获取技能目录
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SKILL_DIR, "data")

# 向量嵌入配置
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
EMBEDDING_DIM = 512

# 搜索配置
TOP_K = 5  # 默认返回结果数量
MAX_SEARCH_RESULTS = 20  # 搜索时从各索引获取的候选数量

# 笔记配置
MAX_CONTENT_LENGTH = 100  # 单条笔记最大字数

# 数据库配置
DB_PATH = os.path.join(DATA_DIR, "notes.db")

# 向量索引配置
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")

# BM25配置
BM25_K1 = 1.5
BM25_B = 0.75

# RRF融合参数
RRF_K = 60  # RRF算法中的参数

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)