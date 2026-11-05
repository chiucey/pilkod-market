# 量化LOF基金买入提醒监控系统 v1.0

自动监控量化类LOF基金的折溢价率、净值回撤等关键指标，当触发预设买入条件时，通过微信/钉钉/邮件等方式实时推送提醒。

---

## 功能特性

- **实时监控**: 每30分钟自动扫描6只核心量化LOF
- **五维评分**: 折溢价率 + 净值回撤 + 流动性 + 规模 + 策略适配
- **智能提醒**: 5种买入条件触发机制，防止过度提醒（冷却时间）
- **多渠道推送**: 支持Server酱(微信)/钉钉/Bark(iOS)/邮件/企业微信
- **数据持久化**: 自动保存90天历史数据，支持回溯分析
- **双数据源**: 集思录(主) + 东方财富(备用)

---

## 监控标的（6只量化LOF）

| 代码 | 名称 | 策略类型 | 跟踪指数 |
|------|------|---------|---------|
| 166107 | 信澳量化多因子LOF-A | 多因子量化 | 中证500 |
| 166109 | 信澳量化先锋LOF-A | 统计套利 | 中证500 |
| 161039 | 富国中证1000增强LOF | 指数增强 | 中证1000 |
| 161035 | 富国中证500增强LOF | 指数增强 | 中证500 |
| 501059 | 西部利得国企红利增强LOF | 红利增强 | 中证国企红利 |
| 160644 | 鹏华港美互联LOF | 跨境量化 | 恒生科技+纳指 |

---

## 买入触发条件

系统内置5种买入触发条件，可在 `config.py` 中自由开关：

| 条件 | 说明 | 默认状态 |
|------|------|---------|
| 深度折价 | 折价率 > 1.5% | 开启 |
| 中度回调 | 回撤 < -8% 且 溢价 < 1% | 开启 |
| 轻度回调+折价 | 回撤 < -5% 且 折价 > 0.5% | 开启 |
| 净值突破 | 突破前高2% | 关闭 |
| 评分跃升 | 综合评分 >65 且 较昨日提升10分 | 开启 |

---

## 快速开始

### 第一步：下载文件

确保目录包含以下文件：
```
quant_lof_monitor/
├── config.py       # 配置文件
├── monitor.py      # 主监控脚本
├── start.bat       # Windows启动
├── start.sh        # Linux/Mac启动
└── test.sh         # 单次测试
```

### 第二步：安装Python和依赖

```bash
# 安装Python 3.8+ (如果未安装)
# https://www.python.org/downloads/

# 安装唯一依赖
pip install requests
```

### 第三步：配置提醒方式

编辑 `config.py`，选择至少一种提醒方式：

#### 方式一：Server酱（推荐，最简单）

1. 访问 https://sct.ftqq.com/ 注册账号
2. 关注公众号获取 SendKey
3. 修改配置：
```python
"server_chan": {
    "enabled": True,
    "send_key": "SCT1234567890abcdef"   # 填入你的SendKey
}
```

#### 方式二：钉钉机器人

1. 在钉钉群设置中添加"智能群助手" -> "自定义机器人"
2. 复制 Webhook 地址和加签密钥
3. 修改配置：
```python
"dingtalk": {
    "enabled": True,
    "webhook": "https://oapi.dingtalk.com/robot/send?access_token=xxx",
    "secret": "SECxxx"
}
```

#### 方式三：Bark（iOS推送，无延迟）

1. App Store搜索"Bark"下载安装
2. 复制设备Key
3. 修改配置：
```python
"bark": {
    "enabled": True,
    "device_key": "your_device_key_here"
}
```

#### 方式四：邮件

```python
"email": {
    "enabled": True,
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender": "your_qq@qq.com",
    "password": "your_auth_code",    # QQ邮箱授权码
    "receiver": "receiver@qq.com"
}
```

### 第四步：启动监控

```bash
# Windows
双击 start.bat

# Linux/Mac
chmod +x start.sh test.sh
./start.sh

# 单次测试（不进入循环，运行一次）
./test.sh
# 或
python monitor.py --once
```

---

## 自定义配置

### 修改监控频率

```python
MONITOR_CONFIG = {
    "interval_minutes": 30,    # 改为15即每15分钟扫描一次
    "alert_cooldown": 3600,    # 同一基金提醒间隔（秒）
}
```

### 添加/删除监控基金

```python
MONITOR_FUNDS = [
    {
        "code": "166107",
        "name": "信澳量化多因子LOF-A",
        "strategy": "多因子量化",
        "index": "中证500",
        "max_premium": 2.0,       # 最高允许溢价率
        "max_drawdown_buy": -8,   # 回撤到-8%以下可买
        "min_amount": 100,        # 最低成交额(万)
        "sharpe_threshold": 1.5,  # 夏普比率最低要求
        "weight": 1.0             # 监控权重
    },
    # 添加你自己的基金...
]
```

### 调整买入条件参数

```python
BUY_CONDITIONS = {
    "deep_discount": {
        "enabled": True,
        "premium_threshold": -1.5,   # 改成-2.0更严格
        "alert_level": "强买入"
    },
    "moderate_drawdown": {
        "enabled": True,
        "drawdown_threshold": -8,    # 改成-10更保守
        "max_premium": 1.0
    }
}
```

---

## 运行效果示例

```
============================================================
📡 监控轮次: 2026-05-13 14:30:05
============================================================
📥 正在获取实时数据...
   获取到 6 只基金数据
   🔴 信澳量化多因子LO | 价格:1.636 | 净值:1.6364 | 溢价:-0.02% | 回撤:-3.7% | 评分:58
   🟢 富国中证1000增强  | 价格:2.970 | 净值:2.9698 | 溢价:0.01% | 回撤:-5.0% | 评分:72
   🟢 富国中证500增强   | 价格:2.220 | 净值:2.2000 | 溢价:0.91% | 回撤:-4.0% | 评分:66
   🟡 国企红利LOF      | 价格:1.810 | 净值:1.8000 | 溢价:0.56% | 回撤:-3.0% | 评分:50
   🔴 港美互联LOF      | 价格:2.128 | 净值:1.9488 | 溢价:9.20% | 回撤:-12.0% | 评分:44
      🚨 触发2个买入条件，发送提醒...
         ✅ Server酱推送成功

✅ 本轮监控完成，下次检查: 15:00:05
```

---

## 提醒消息示例

```
🔔量化LOF买入提醒: 富国中证1000增强LOF

【基金】富国中证1000增强LOF (161039)
【策略】指数增强 | 跟踪: 中证1000

📊 实时数据:
   场内价格: 2.970元
   最新净值: 2.9698元 (2026-05-12)
   折溢价率: 0.01% ➡️平价
   近期回撤: -5.00%
   成交额: 5000万 | 换手率: 3.2%
   基金规模: 12.64亿

⭐ 综合评分: 72/100

🔔 触发买入条件:
   ✅买入: 中度回调+合理溢价
   触发原因: 回撤-5.0% + 溢价率0.01%

💡 操作建议:
   ✅ 积极买入 - 综合条件优秀

⏰ 数据时间: 2026-05-13 14:30:05
```

---

## 进阶使用

### 部署到云服务器7x24运行

```bash
# 使用screen后台运行
screen -S lof_monitor
./start.sh
# Ctrl+A+D  detached

# 或使用nohup
nohup python monitor.py > monitor.log 2>&1 &

# 或使用systemd服务（推荐）
# 1. 创建服务文件
sudo tee /etc/systemd/system/lof-monitor.service << 'EOF'
[Unit]
Description=量化LOF基金监控系统
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/quant_lof_monitor
ExecStart=/usr/bin/python3 monitor.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

# 2. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable lof-monitor
sudo systemctl start lof-monitor

# 3. 查看状态
sudo systemctl status lof-monitor
sudo journalctl -u lof-monitor -f
```

### 部署到NAS/树莓派

```bash
# 同样的步骤，适合低功耗设备
# 建议搭配docker使用

# Dockerfile示例
cat > Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install requests
CMD ["python", "monitor.py"]
EOF

docker build -t lof-monitor .
docker run -d --name lof-monitor --restart always lof-monitor
```

---

## 注意事项

1. **数据延迟**: 净值数据T+1更新，盘中溢价率为估算值
2. **网络要求**: 需要能访问集思录和东方财富
3. **频率限制**: 不要过于频繁请求，建议间隔>=15分钟
4. **投资有风险**: 本系统仅提供数据监控，不构成投资建议
5. **首次运行**: 建议先用 `--once` 测试确认提醒正常收到

---

## 常见问题

**Q: 为什么收不到提醒？**
A: 检查：1) 是否在交易时间 2) 提醒方式是否已启用并配置正确 3) 用 `--once` 测试

**Q: 可以添加更多基金吗？**
A: 可以，在 `config.py` 的 `MONITOR_FUNDS` 中添加，任何LOF基金都可以

**Q: 会频繁打扰吗？**
A: 不会，有冷却时间（默认1小时），且只在触发买入条件时才提醒

**Q: 手机需要一直开机吗？**
A: 不需要，监控运行在你的电脑/服务器上，手机只接收推送

---

## 更新日志

### v1.0 (2026-05-13)
- 初始版本
- 支持6只核心量化LOF监控
- 5种买入触发条件
- 5种提醒方式
- 双数据源支持

---

**免责声明**: 本系统仅供学习和研究使用，不构成任何投资建议。基金投资有风险，入市需谨慎。
