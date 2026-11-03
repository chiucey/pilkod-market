================================================================
        Commodity Daily Briefing System - User Guide
================================================================

1. First Time Setup
-------------------
1.1 Install Python dependencies:
    pip install requests beautifulsoup4 lxml python-docx

1.2 Configure config.json:
    - Email SMTP settings (QQ/163/enterprise邮箱)
    - Receivers list
    - Focus commodities (optional)
    - Proxy settings (optional)

1.3 For email configuration:
    - QQ邮箱: smtp_server = "smtp.qq.com"
    - 163邮箱: smtp_server = "smtp.163.com"
    - Use "授权码" as password, not login password


2. Daily Usage
--------------
Run the script:
    python daily_briefing.py

Expected runtime: 3-5 minutes depending on network speed


3. Output Files
---------------
output/
├── YYYYMMDD_大宗商品简报XXXX期.docx
├── YYYYMMDD_大宗商品简报XXXX期.html
└── logs/
    └── YYYYMMDD.log


4. Data Sources
---------------
P1 (High Priority):
- 华尔街见闻 (Wall Street CN)
- 财联社 (CLS Telegraph)
- 金十数据 (Jin10)

P2 (Industry News):
- SMM上海有色网 (Non-ferrous metals)
- 我的钢铁网 (Steel/Black metals)
- 隆众资讯 (Energy/Chemicals)
- 中国证券报 (Macro Economy)

P3 (Exchanges & Macro):
- 上期所/大商所/郑商所/上期能源 (Exchange announcements)
- 国家统计局 (National Bureau of Statistics)
- 人民银行 (PBOC)
- 美联储 (Federal Reserve)


5. Configuration Parameters
----------------------------
scraping.min_delay    : Min request interval (seconds), default 3
scraping.max_delay    : Max request interval (seconds), default 8
scraping.max_retries  : Retry count, default 2
scraping.timeout      : Request timeout (seconds), default 15


6. Focus Commodities
-------------------
Default focus:
- 有色金属: 铜, 铝, 镍
- 黑色金属: 螺纹钢, 铁矿石
- 贵金属: 黄金
- 能源: 原油, 天然气
- 农产品: 白糖
- 化工: 橡胶


7. Troubleshooting
-----------------
Q: Some sources show failure
A: Website may be updated, weekend/holiday no data, or network issues.
   Check logs/ directory for details.

Q: All sources fail
A: Check network connection, firewall settings, or proxy configuration.

Q: Email fails to send
A: Verify SMTP settings and authorization code in config.json

================================================================
