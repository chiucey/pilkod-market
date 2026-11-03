#!/usr/bin/env python3
"""
贵金属价格监控脚本
支持工商银行积存金、建设银行贵金属价格监控
"""

import json
import logging
import os
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置文件路径
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')

# 触发记录缓存（内存中，避免重复通知）
trigger_cache: Dict[str, float] = {}
COOLDOWN_SECONDS = 1800  # 30分钟冷却期


class GoldPriceMonitor:
    """贵金属价格监控器"""

    # 数据源URL
    ICBC_URL = "https://mybank.icbc.com.cn/icbc/newperbank/perbank3/gold/goldaccrual_query_out.jsp"
    CCB_URL = "https://gold.ccb.com/cn/gold/hjhq.html"

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def get_icbc_gold_price(self) -> Optional[Dict[str, Dict[str, str]]]:
        """获取工商银行积存金实时价格"""
        try:
            logger.info("正在获取工商银行积存金价格...")
            response = requests.get(
                self.ICBC_URL,
                headers=self.headers,
                timeout=15
            )
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            prices = {}
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # 跳过表头
                    cols = row.find_all('td')
                    if len(cols) >= 9:
                        # 提取产品名称和价格
                        product = cols[0].text.strip()
                        buy_price = cols[1].text.strip()
                        buy_change = cols[2].text.strip()
                        low_price = cols[3].text.strip()
                        high_price = cols[4].text.strip()
                        regular_price = cols[5].text.strip()
                        regular_change = cols[6].text.strip()
                        sell_price = cols[7].text.strip()
                        sell_change = cols[8].text.strip()

                        if product:
                            prices[product] = {
                                '买入价': buy_price,
                                '买入涨跌': buy_change,
                                '最低价': low_price,
                                '最高价': high_price,
                                '定期积存价': regular_price,
                                '赎回价': sell_price,
                                '赎回涨跌': sell_change
                            }

            if prices:
                logger.info(f"成功获取工行积存金价格: {list(prices.keys())}")
            return prices

        except requests.RequestException as e:
            logger.error(f"获取工行积存金价格失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析工行积存金价格异常: {e}")
            return None

    def get_ccb_gold_price(self) -> Optional[Dict[str, Dict[str, str]]]:
        """获取建设银行贵金属实时价格"""
        try:
            logger.info("正在获取建设银行贵金属价格...")
            response = requests.get(
                self.CCB_URL,
                headers=self.headers,
                timeout=15
            )
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            prices = {}

            # 查找积存金数据
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        product = cols[0].text.strip()
                        buy_price = cols[1].text.strip()
                        sell_price = cols[2].text.strip()
                        update_time = cols[3].text.strip()

                        if '积存' in product or '金' in product:
                            prices[product] = {
                                '买入价': buy_price,
                                '赎回价': sell_price,
                                '更新时间': update_time
                            }

            if prices:
                logger.info(f"成功获取建行贵金属价格: {list(prices.keys())}")
            return prices

        except requests.RequestException as e:
            logger.error(f"获取建行贵金属价格失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析建行贵金属价格异常: {e}")
            return None

    def check_price_alert(
        self,
        current_price: float,
        baseline: float,
        threshold: float,
        direction: str
    ) -> Dict[str, Any]:
        """检查是否触发价格提醒"""
        delta = current_price - baseline
        change_percent = (delta / baseline) * 100 if baseline != 0 else 0

        triggered = False
        reason = ""

        if direction == 'above' and delta >= threshold:
            triggered = True
            reason = f"价格{delta:+.2f}元超过阈值{threshold}元"
        elif direction == 'below' and delta <= -threshold:
            triggered = True
            reason = f"价格下降{delta:.2f}元超过阈值{threshold}元"
        elif direction == 'both' and abs(delta) >= threshold:
            triggered = True
            reason = f"价格变动{delta:+.2f}元超过阈值{threshold}元"

        return {
            'triggered': triggered,
            'delta': delta,
            'change_percent': change_percent,
            'reason': reason
        }

    def check_cooldown(self, product_key: str) -> bool:
        """检查是否在冷却期内"""
        if product_key in trigger_cache:
            last_trigger = trigger_cache[product_key]
            elapsed = time.time() - last_trigger
            if elapsed < COOLDOWN_SECONDS:
                remaining = COOLDOWN_SECONDS - elapsed
                logger.info(f"产品 {product_key} 在冷却期内，还需 {remaining:.0f} 秒")
                return True
        return False

    def update_cooldown(self, product_key: str):
        """更新触发记录"""
        trigger_cache[product_key] = time.time()

    def format_alert_message(
        self,
        bank: str,
        product: str,
        price_type: str,
        current_price: float,
        baseline: float,
        delta: float,
        change_percent: float,
        threshold: float,
        direction: str
    ) -> str:
        """格式化告警消息"""
        direction_text = {
            'above': '上涨',
            'below': '下跌',
            'both': '波动'
        }.get(direction, '')

        return (
            f"【金价提醒】{bank}{product}{price_type}已达{current_price:.2f}元/克，"
            f"较基准价{baseline:.2f}元{direction_text}{abs(delta):.2f}元"
            f"（{delta:+:.2f}%，{change_percent:+:.2f}%）"
            f"，已触发阈值{threshold}元"
        )

    def send_notification(
        self,
        alert_data: Dict[str, Any],
        channels: List[str]
    ):
        """发送通知"""
        message = alert_data['message']

        for channel in channels:
            if channel == 'console':
                print("\n" + "=" * 60)
                print("🔔 价格提醒通知")
                print("=" * 60)
                print(message)
                print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 60 + "\n")

            elif channel == 'webhook':
                webhook_url = self.config.get('webhook_url')
                if webhook_url:
                    try:
                        payload = {
                            'msgtype': 'text',
                            'text': {
                                'content': message
                            }
                        }
                        requests.post(webhook_url, json=payload, timeout=10)
                        logger.info(f"已发送webhook通知")
                    except Exception as e:
                        logger.error(f"发送webhook通知失败: {e}")

            elif channel == 'email':
                # 邮件通知（需要配置SMTP）
                email_config = self.config.get('email')
                if email_config:
                    logger.info(f"邮件通知已配置: {email_config.get('to')}")
                    # 实现邮件发送逻辑

    def monitor(self):
        """执行监控检查"""
        logger.info("=" * 50)
        logger.info("开始贵金属价格监控")
        logger.info("=" * 50)

        targets = self.config.get('monitoring', {}).get('targets', [])
        channels = self.config.get('monitoring', {}).get('notify_channels', ['console'])

        all_prices = {
            '工商银行': self.get_icbc_gold_price(),
            '建设银行': self.get_ccb_gold_price()
        }

        for target in targets:
            bank = target.get('bank', '')
            product = target.get('product', '积存金')
            price_type = target.get('price_type', '买入价')
            baseline = float(target.get('baseline', 0))
            threshold = float(target.get('threshold', 0))
            direction = target.get('direction', 'both')

            # 获取当前价格
            price_data = all_prices.get(bank, {})
            product_data = price_data.get(product, {}) if price_data else {}
            price_str = product_data.get(price_type, 'N/A')

            if price_str == 'N/A' or not price_str.replace('.', '').isdigit():
                logger.warning(f"无法获取 {bank} {product} {price_type} 价格")
                continue

            current_price = float(price_str)
            logger.info(f"当前价格: {bank} {product} {price_type} = {current_price} 元/克")

            # 检查是否触发
            check_result = self.check_price_alert(
                current_price, baseline, threshold, direction
            )

            if check_result['triggered']:
                product_key = f"{bank}_{product}_{price_type}"

                # 检查冷却期
                if not self.check_cooldown(product_key):
                    logger.info(f"触发价格提醒: {check_result['reason']}")

                    alert_message = self.format_alert_message(
                        bank=bank,
                        product=product,
                        price_type=price_type,
                        current_price=current_price,
                        baseline=baseline,
                        delta=check_result['delta'],
                        change_percent=check_result['change_percent'],
                        threshold=threshold,
                        direction=direction
                    )

                    alert_data = {
                        'type': 'gold_price_alert',
                        'timestamp': datetime.now().isoformat(),
                        'alert': {
                            'bank': bank,
                            'product': product,
                            'price_type': price_type,
                            'current_price': current_price,
                            'baseline': baseline,
                            'delta': check_result['delta'],
                            'change_percent': check_result['change_percent'],
                            'threshold': threshold,
                            'direction': direction
                        },
                        'message': alert_message
                    }

                    # 发送通知
                    self.send_notification(alert_data, channels)

                    # 更新冷却
                    self.update_cooldown(product_key)
                else:
                    logger.debug(f"跳过重复通知: {product_key}")
            else:
                logger.info(
                    f"未触发提醒: 变动{check_result['delta']:+.2f}元，"
                    f"阈值{threshold}元 (方向: {direction})"
                )

        logger.info("监控检查完成")


def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    import yaml

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"配置文件不存在: {config_path}")
        # 返回默认配置示例
        return {
            'monitoring': {
                'targets': [
                    {
                        'bank': 'icbc',
                        'product': '积存金',
                        'price_type': '买入价',
                        'baseline': 600.0,
                        'threshold': 10.0,
                        'direction': 'above'
                    }
                ],
                'notify_channels': ['console']
            }
        }
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description='贵金属价格监控工具')
    parser.add_argument(
        '--config',
        '-c',
        default=DEFAULT_CONFIG_PATH,
        help='配置文件路径'
    )
    parser.add_argument(
        '--interval',
        '-i',
        type=int,
        help='检查间隔（秒），单次执行时忽略'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='只执行一次检查'
    )
    args = parser.parse_args()

    config = load_config(args.config)

    if args.interval and not args.once:
        # 循环监控模式
        interval = args.interval
        logger.info(f"启动循环监控模式，间隔 {interval} 秒")
        try:
            while True:
                monitor = GoldPriceMonitor(config)
                monitor.monitor()
                logger.info(f"等待 {interval} 秒后进行下一次检查...")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("监控已停止")
    else:
        # 单次执行模式
        monitor = GoldPriceMonitor(config)
        monitor.monitor()


if __name__ == '__main__':
    main()
