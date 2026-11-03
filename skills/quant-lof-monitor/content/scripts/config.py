# -*- coding: utf-8 -*-
"""
量化LOF基金买入提醒监控配置
修改此文件自定义监控参数
"""

# ==================== 监控标的 ====================
MONITOR_FUNDS = [
    {
        "code": "166107",
        "name": "信澳量化多因子LOF-A",
        "strategy": "多因子量化",
        "index": "中证500",
        "max_premium": 2.0,      # 最高允许溢价率%
        "max_drawdown_buy": -8,  # 回撤到-8%以下可买
        "min_amount": 100,       # 最低成交额(万)
        "sharpe_threshold": 1.5, # 夏普比率最低要求
        "weight": 1.0            # 监控权重
    },
    {
        "code": "166109",
        "name": "信澳量化先锋LOF-A",
        "strategy": "统计套利",
        "index": "中证500",
        "max_premium": 2.0,
        "max_drawdown_buy": -8,
        "min_amount": 100,
        "sharpe_threshold": 1.5,
        "weight": 1.0
    },
    {
        "code": "161039",
        "name": "富国中证1000增强LOF",
        "strategy": "指数增强",
        "index": "中证1000",
        "max_premium": 2.0,
        "max_drawdown_buy": -8,
        "min_amount": 500,
        "sharpe_threshold": 1.2,
        "weight": 1.5             # 优先监控
    },
    {
        "code": "161035",
        "name": "富国中证500增强LOF",
        "strategy": "指数增强",
        "index": "中证500",
        "max_premium": 2.0,
        "max_drawdown_buy": -8,
        "min_amount": 300,
        "sharpe_threshold": 1.2,
        "weight": 1.2
    },
    {
        "code": "501059",
        "name": "西部利得国企红利增强LOF",
        "strategy": "红利增强",
        "index": "中证国企红利",
        "max_premium": 1.5,
        "max_drawdown_buy": -5,
        "min_amount": 200,
        "sharpe_threshold": 1.0,
        "weight": 0.8
    },
    {
        "code": "160644",
        "name": "鹏华港美互联LOF",
        "strategy": "跨境量化",
        "index": "恒生科技+纳指",
        "max_premium": 3.0,
        "max_drawdown_buy": -10,
        "min_amount": 1000,
        "sharpe_threshold": 0.8,
        "weight": 0.5              # 低风险敞口
    }
]

# ==================== 买入触发条件 ====================
BUY_CONDITIONS = {
    # 触发条件1: 深度折价
    "deep_discount": {
        "enabled": True,
        "description": "深度折价买入",
        "premium_threshold": -1.5,   # 折价率<-1.5%
        "alert_level": "🔥强买入"     # 提醒级别
    },
    # 触发条件2: 中度回调
    "moderate_drawdown": {
        "enabled": True,
        "description": "中度回调+合理溢价",
        "drawdown_threshold": -8,    # 回撤<-8%
        "max_premium": 1.0,          # 溢价<1%
        "alert_level": "✅买入"
    },
    # 触发条件3: 轻度回调+折价
    "mild_discount": {
        "enabled": True,
        "description": "轻度回调+折价",
        "drawdown_threshold": -5,    # 回撤<-5%
        "premium_threshold": -0.5,   # 折价>0.5%
        "alert_level": "⭐轻买入"
    },
    # 触发条件4: 净值突破（右侧买入）
    "breakout": {
        "enabled": False,            # 默认关闭
        "description": "净值突破前高",
        "breakout_ratio": 2.0,       # 突破前高2%
        "max_premium": 0.5,
        "alert_level": "📈趋势买入"
    },
    # 触发条件5: 综合评分跃升
    "score_jump": {
        "enabled": True,
        "description": "综合评分大幅提升",
        "score_threshold": 65,       # 评分>65
        "score_jump": 10,            # 较昨日提升10分+
        "alert_level": "📊评分买入"
    }
}

# ==================== 提醒方式配置 ====================
NOTIFY_CONFIG = {
    # Server酱（微信推送）- 推荐
    # 注册地址: https://sct.ftqq.com/
    "server_chan": {
        "enabled": False,
        "send_key": "YOUR_SEND_KEY_HERE"   # 填入你的SendKey
    },

    # 钉钉机器人
    # 参考: https://open.dingtalk.com/document/robots/custom-robot-access
    "dingtalk": {
        "enabled": False,
        "webhook": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN",
        "secret": "YOUR_SECRET_HERE"
    },

    # Bark推送（iOS）
    # App Store搜索"Bark"安装
    "bark": {
        "enabled": False,
        "device_key": "YOUR_DEVICE_KEY",
        "server": "https://api.day.app"
    },

    # 邮件提醒
    "email": {
        "enabled": False,
        "smtp_server": "smtp.qq.com",
        "smtp_port": 465,
        "sender": "your_email@qq.com",
        "password": "YOUR_AUTH_CODE",   # QQ邮箱授权码
        "receiver": "receiver@qq.com"
    },

    # 企业微信机器人
    "wecom": {
        "enabled": False,
        "webhook": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
    }
}

# ==================== 监控频率配置 ====================
MONITOR_CONFIG = {
    "market_open": "09:30",     # 开盘时间
    "market_close": "15:00",    # 收盘时间
    "interval_minutes": 30,     # 监控间隔(分钟)
    "alert_cooldown": 3600,     # 同一基金提醒冷却时间(秒)
    "data_source": "jisilu"     # 数据源: jisilu/eastmoney
}

# ==================== 历史记录配置 ====================
HISTORY_CONFIG = {
    "save_path": "./data",      # 数据保存路径
    "keep_days": 90             # 保留90天历史
}
