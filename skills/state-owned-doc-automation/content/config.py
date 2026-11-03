"""全局配置文件（CLI 工具版）。"""

# 共享盘与监听目录
SHARED_BASE_PATH = r"F:\桌面（不是\归档"
WATCH_DIR = r"F:\桌面（不是\待归档"
# 可选：非空时，在归档到 SHARED_BASE_PATH 成功后，再复制一份到该目录（双备份）。
PROCESSED_DIR = r".\backup"

# 数据与索引
DB_PATH = "data/file_meta.db"
INDEX_PATH = "index/whoosh"

# 大模型 API（OpenAI 兼容）
AI_API_KEY = "sk-cp-DUB_THJDXNFm_Bwmsa4zkkh_dP56wjUDZx-apMxoQ0TgJEQxoEDqbYFcurA1PvX6wk6ddcl9it0PTP5sZSNdmi5NyWNDD6voIygYHv6qJ9AqsUG3-qdmT1k"  # MiniMax API Key（首次交付建议留空，由使用者自行填写）
AI_BASE_URL = "https://api.minimax.chat/v1"  # MiniMax 的 OpenAI 兼容端点（保持不变）
AI_MODEL = "MiniMax-M2.5"  # 默认先用兼容性更稳的模型，避免账户套餐不支持报错
# --- 备选：DeepSeek ---
# AI_API_KEY = ""  # DeepSeek Key
# AI_BASE_URL = "https://api.deepseek.com/v1"  # DeepSeek 的 OpenAI 兼容端点
# AI_MODEL = "deepseek-chat"  # DeepSeek 模型
# --- 备选：通义千问 ---
# AI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 通义千问 OpenAI 兼容端点（备选）
# AI_MODEL = "qwen-plus"  # 通义千问模型（备选）
AI_MAX_TOKENS = 500
AI_MAX_RETRIES = 3  # 最大重试次数
AI_TIMEOUT = 30  # 请求超时时间（秒）

