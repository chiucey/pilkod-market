# Stock Scout A股版 - 配置文件
# 所有参数在此管理，换数据源或调权重只需改这里

# ============ Tushare API ============
TUSHARE_TOKEN = "a78cbdbee9fe610ed43aeefb9d5355445f7cbf3da72f20323f443b5e"

# ============ 飞书（待配置）============
FEISHU_APP_ID = ""       # TODO: 飞书应用 App ID
FEISHU_APP_SECRET = ""    # TODO: 飞书应用 App Secret
FEISHU_APP_TOKEN = ""    # TODO: 飞书 Bitable App Token
FEISHU_SCOUT_TABLE = ""  # TODO: Scout结果表 Table ID
FEISHU_WATCH_TABLE = ""  # TODO: 关注列表 Table ID
FEISHU_ALERT_TABLE = ""  # TODO: 警报日志 Table ID

# ============ MiniMax LLM ============
MINIMAX_API_KEY = ""     # TODO: MiniMax API Key
MINIMAX_BASE_URL = "https://api.minimax.chat/v1"

# ============ 选股参数 (Tab7 等效) ============
MIN_INSTITUTIONAL_PCT = 50       # 最低机构持仓%（A股用北向持股代替）
MIN_SCORE = 65                   # 综合评分阈值 ≥65 进入Scout结果
SECTOR = "科技"                  # 申万行业筛选
MAX_FLOAT_MILLION = 500         # 最大流通盘（万股）
MIN_MARGIN_RATIO = 0            # 最低融资余额变动%
MIN_HK_HOLD_PCT = 1             # 最低北向持股%

# ============ 评分权重（可调，无需改代码）===========
WEIGHT_NORTHBOUND  = 0.25   # 北向资金权重
WEIGHT_MONEYFLOW    = 0.25   # 主力资金流权重
WEIGHT_MARGIN      = 0.15   # 融资余额权重（反向指标）
WEIGHT_TECHNICAL   = 0.20   # 技术动能权重
WEIGHT_BROKER      = 0.15   # 券商评级权重

# ============ 系统参数 ============
DB_PATH = "data/scout.db"
LOG_LEVEL = "INFO"
