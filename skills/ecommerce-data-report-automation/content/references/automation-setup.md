---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2445d0977072acb4b034b1dbfd53ace8
    PropagateID: 2445d0977072acb4b034b1dbfd53ace8
    ReservedCode1: 304502207423c93a6349e26737cf1ab84dd7753eeab4f07cf4d315e5d2f3a8538e9a60500221009b15e45f42f30f8af0be7fbd5ab284445b1ba69e4b284541f10c80db1b2e28c8
    ReservedCode2: 3046022100827f3d36e9f863ceb18a9c648dca169001d90c8d2c8e5420b9c91f42b0a385c1022100d74767aa092d3ef92d5e6387af08ed23a70a34d0cefdd80cc1d7e00a4cb4de80
---

# 自动化部署配置指南

## 一、Python 自动化脚本

### 1.1 项目结构

```
ecommerce-report-automation/
├── config/
│   └── settings.yaml          # 配置文件
├── scripts/
│   ├── data_collector.py      # 数据采集脚本
│   ├── report_generator.py    # 报告生成脚本
│   └── notifier.py           # 通知发送脚本
├── templates/
│   └── daily_report.md       # 日报模板
├── output/
│   └── reports/              # 生成的报告
├── main.py                   # 主入口
└── requirements.txt         # 依赖
```

### 1.2 主脚本 (main.py)

```python
#!/usr/bin/env python3
"""
电商运营日报自动化生成脚本
Usage: python main.py --date 2024-01-15
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path

from scripts.data_collector import DataCollector
from scripts.report_generator import ReportGenerator
from scripts.notifier import Notifier

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(date: str):
    """主流程"""
    logger.info(f"开始生成 {date} 日报")

    # 1. 数据采集
    logger.info("步骤1: 采集数据...")
    collector = DataCollector()
    data = collector.collect(date)

    # 2. 生成报告
    logger.info("步骤2: 生成报告...")
    generator = ReportGenerator()
    report_path = generator.generate(data, date)

    # 3. 发送通知
    logger.info("步骤3: 发送通知...")
    notifier = Notifier()
    notifier.send(report_path, date)

    logger.info(f"日报生成完成: {report_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='电商运营日报自动化')
    parser.add_argument('--date', type=str, default=datetime.now().strftime('%Y-%m-%d'),
                        help='报表日期 (格式: YYYY-MM-DD)')
    args = parser.parse_args()

    main(args.date)
```

### 1.3 数据采集器 (data_collector.py)

```python
import pandas as pd
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class DataCollector:
    """数据采集器"""

    def __init__(self):
        self.platforms = ['jd', 'tmall', 'douyin', 'xiaohongshu', 'bilibili']

    def collect(self, date: str) -> Dict[str, pd.DataFrame]:
        """采集各平台数据"""
        data = {}

        for platform in self.platforms:
            try:
                # 根据数据源类型选择采集方式
                # 方式1: 从数据库查询
                # data[platform] = self._fetch_from_db(platform, date)

                # 方式2: 从API获取
                # data[platform] = self._fetch_from_api(platform, date)

                # 方式3: 从Excel读取
                # data[platform] = self._read_from_excel(platform, date)

                logger.info(f"{platform} 数据采集完成")
            except Exception as e:
                logger.error(f"{platform} 数据采集失败: {e}")
                data[platform] = pd.DataFrame()

        return data

    def _read_from_excel(self, platform: str, date: str) -> pd.DataFrame:
        """从Excel读取数据"""
        file_path = f"data/{platform}_{date}.xlsx"
        return pd.read_excel(file_path)
```

### 1.4 报告生成器 (report_generator.py)

```python
from datetime import datetime
from pathlib import Path
from typing import Dict
import pandas as pd


class ReportGenerator:
    """报告生成器"""

    def __init__(self, template_path: str = 'templates/daily_report.md'):
        self.template_path = Path(template_path)
        self.output_dir = Path('output/reports')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, data: Dict[str, pd.DataFrame], date: str) -> str:
        """生成日报"""
        # 合并数据并计算指标
        combined = self._merge_and_calculate(data)

        # 渲染模板
        content = self._render_template(combined, date)

        # 保存文件
        output_path = self.output_dir / f"日报_{date}.md"
        output_path.write_text(content, encoding='utf-8')

        return str(output_path)

    def _merge_and_calculate(self, data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """合并数据并计算指标"""
        all_data = []
        for platform, df in data.items():
            df['platform'] = platform
            all_data.append(df)

        combined = pd.concat(all_data, ignore_index=True)

        # 计算完成率
        combined['completion_rate'] = (
            combined['actual'] / combined['target'] * 100
        ).round(2)

        return combined

    def _render_template(self, data: pd.DataFrame, date: str) -> str:
        """渲染日报模板"""
        template = self.template_path.read_text(encoding='utf-8')

        # 生成数据表格
        table = self._generate_table(data)

        # 替换模板占位符
        content = template.replace('{{DATE}}', date)
        content = content.replace('{{DATA_TABLE}}', table)

        return content

    def _generate_table(self, data: pd.DataFrame) -> str:
        """生成Markdown表格"""
        # 按产品系汇总
        summary = data.groupby('product_line').agg({
            'actual': 'sum',
            'target': 'sum'
        }).reset_index()

        summary['completion_rate'] = (
            summary['actual'] / summary['target'] * 100
        ).round(2)

        # 生成Markdown表格
        lines = ['| 产品系 | 实际完成 | 目标 | 完成率 |',
                 '|--------|----------|------|--------|']

        for _, row in summary.iterrows():
            lines.append(
                f"| {row['product_line']} | {row['actual']} | {row['target']} | {row['completion_rate']}% |"
            )

        return '\n'.join(lines)
```

---

## 二、定时任务配置

### 2.1 Crontab 配置

```bash
# 编辑 crontab
crontab -e

# 每日早上9点执行
0 9 * * * /usr/bin/python3 /path/to/main.py --date $(date +\%Y-\%m-\%d) >> /var/log/report.log 2>&1

# 每周一早上9点执行周报
0 9 * * 1 /usr/bin/python3 /path/to/main.py --weekly >> /var/log/weekly_report.log 2>&1
```

### 2.2 systemd 服务配置

```ini
# /etc/systemd/system/ecommerce-report.service
[Unit]
Description=E-commerce Daily Report Automation
After=network.target

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/opt/ecommerce-report
ExecStart=/usr/bin/python3 /opt/ecommerce-report/main.py
StandardOutput=append:/var/log/ecommerce-report.log
StandardError=append:/var/log/ecommerce-report.error.log

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/ecommerce-report.timer
[Unit]
Description=Run E-commerce Report Daily at 9am

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# 启用定时任务
sudo systemctl enable ecommerce-report.timer
sudo systemctl start ecommerce-report.timer
```

---

## 三、通知渠道配置

### 3.1 企业微信 Webhook

```python
import requests
import json


class WeChatNotifier:
    """企业微信通知"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send(self, report_path: str, date: str):
        """发送通知"""
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"### 📊 电商运营日报 - {date}\n\n{content[:2000]}...\n\n[查看完整日报](http://report.example.com/{date})"
            }
        }

        response = requests.post(self.webhook_url, json=message)
        return response.json()
```

### 3.2 邮件通知

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailNotifier:
    """邮件通知"""

    def __init__(self, smtp_server: str, port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password

    def send(self, to_addresses: list, subject: str, content: str, attachments: list = None):
        """发送邮件"""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = subject

        msg.attach(MIMEText(content, 'html', 'utf-8'))

        # 添加附件
        if attachments:
            for file_path in attachments:
                with open(file_path, 'rb') as f:
                    attachment = MIMEText(f.read(), 'base64', 'utf-8')
                    attachment['Content-Type'] = 'application/octet-stream'
                    attachment['Content-Disposition'] = f'attachment; filename="{Path(file_path).name}"'
                    msg.attach(attachment)

        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
```

---

## 四、环境配置

### 4.1 requirements.txt

```
pandas>=1.5.0
openpyxl>=3.0.0
pyyaml>=6.0
requests>=2.28.0
python-dotenv>=0.19.0
schedule>=1.1.0
```

### 4.2 配置管理 (config/settings.yaml)

```yaml
database:
  host: "localhost"
  port: 3306
  user: "readonly_user"
  password: "${DB_PASSWORD}"
  database: "ecommerce"

apis:
  jd:
    app_key: "${JD_APP_KEY}"
    app_secret: "${JD_APP_SECRET}"
  tmall:
    app_key: "${TMALL_APP_KEY}"
    app_secret: "${TMALL_APP_SECRET}"

notification:
  wechat:
    webhook_url: "${WECHAT_WEBHOOK_URL}"
  email:
    smtp_server: "smtp.company.com"
    port: 587
    username: "${EMAIL_USERNAME}"
    password: "${EMAIL_PASSWORD}"

output:
  path: "output/reports"
  format: "md"
```

### 4.3 环境变量 (.env)

```bash
# 数据库
DB_PASSWORD=your_db_password

# API Keys
JD_APP_KEY=your_jd_app_key
JD_APP_SECRET=your_jd_app_secret
TMALL_APP_KEY=your_tmall_app_key
TMALL_APP_SECRET=your_tmall_app_secret

# 通知
WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
EMAIL_USERNAME=report@company.com
EMAIL_PASSWORD=your_email_password
```

---

## 五、日志与监控

### 5.1 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = '/var/log/ecommerce_report.log'):
    """配置日志"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 文件日志
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)

    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )
    logger.addHandler(console_handler)

    return logger
```

### 5.2 健康检查

```python
import psutil
from datetime import datetime

def health_check():
    """健康检查"""
    issues = []

    # 检查磁盘空间
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        issues.append(f"磁盘空间不足: {disk.percent}%")

    # 检查内存
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        issues.append(f"内存使用率过高: {memory.percent}%")

    # 检查上次运行
    last_run_file = Path('output/last_run.txt')
    if last_run_file.exists():
        last_run = datetime.fromisoformat(last_run_file.read_text())
        if (datetime.now() - last_run).hours > 25:
            issues.append("上次运行时间超过25小时")

    return issues
```
