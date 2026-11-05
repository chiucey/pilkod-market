#!/usr/bin/env python3
"""
TM聊天监控与自动回复核心模块
阿里国际站TradeManager聊天自动回复系统

使用方法:
    python tm_monitor.py --config config.json
    python tm_monitor.py --mode monitor  # 仅监控
    python tm_monitor.py --mode auto     # 自动回复
"""

import json
import time
import logging
import os
import sys
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tm_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TMConfig:
    """TM配置管理"""

    DEFAULT_CONFIG = {
        "tm_path": r"C:\Program Files\TradeManager",
        "monitor_interval": 5,  # 监控间隔(秒)
        "auto_reply": True,
        "reply_delay": 30,     # 回复延迟(秒)
        "language": "en",
        "review_mode": True,   # 人工审核模式
        "keywords": {
            "price": ["price", "cost", "报价", "价格"],
            "moq": ["moq", "minimum", "起订量", "MOQ"],
            "sample": ["sample", "样品"],
            "shipping": ["shipping", "delivery", "发货", "物流"],
            "catalog": ["catalog", "catalog", "目录", "产品册"]
        },
        "reply_templates": {
            "price": "Thank you for your inquiry! Our best price will be sent to you soon. Could you please tell me your estimated quantity?",
            "moq": "Our MOQ is {moq}. For smaller quantities, we also offer mixed container options.",
            "sample": "Sample policy: {sample_info}. Please provide your shipping address for sample cost calculation.",
            "shipping": "Shipping time: {lead_time} days. We ship via DHL/FedEx/UPS or your forwarder.",
            "catalog": "I'll send you our latest catalog and price list right away! What products are you interested in?",
            "default": "Thank you for your message! I'm checking and will reply you shortly."
        }
    }

    @classmethod
    def load_config(cls, config_path: str = None) -> Dict:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                return {**cls.DEFAULT_CONFIG, **user_config}
        return cls.DEFAULT_CONFIG

    @classmethod
    def save_config(cls, config: Dict, config_path: str):
        """保存配置文件"""
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class TMChatMonitor:
    """TM聊天消息监控器"""

    def __init__(self, config: Dict):
        self.config = config
        self.tm_path = config.get('tm_path', self._detect_tm_path())
        self.db_path = self._find_chat_database()
        self.processed_messages = set()  # 已处理消息缓存

    def _detect_tm_path(self) -> Optional[str]:
        """检测TM安装路径"""
        possible_paths = [
            r"C:\Program Files\TradeManager",
            r"C:\Program Files (x86)\TradeManager",
            os.path.expanduser("~\\AppData\\Local\\TradeManager"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"检测到TM路径: {path}")
                return path
        logger.warning("未检测到TM安装路径")
        return None

    def _find_chat_database(self) -> Optional[str]:
        """查找聊天数据库"""
        if not self.tm_path:
            return None

        profiles_path = os.path.join(self.tm_path, "profiles")
        if not os.path.exists(profiles_path):
            return None

        # 查找用户数据库
        for user_dir in os.listdir(profiles_path):
            db_path = os.path.join(profiles_path, user_dir, "msg.db")
            if os.path.exists(db_path):
                logger.info(f"找到聊天数据库: {db_path}")
                return db_path
        return None

    def get_chat_windows(self) -> List[Dict]:
        """获取当前打开的聊天窗口"""
        # 尝试通过Windows API获取窗口
        try:
            import win32gui
            import win32con

            windows = []

            def enum_handler(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and "TradeManager" in title:
                        windows.append({
                            'hwnd': hwnd,
                            'title': title
                        })

            win32gui.EnumWindows(enum_handler, None)
            return windows
        except ImportError:
            logger.warning("win32gui未安装，无法获取聊天窗口")
            return []

    def read_new_messages(self) -> List[Dict]:
        """读取新消息"""
        messages = []

        if not self.db_path:
            return messages

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 查询最近消息
            cursor.execute("""
                SELECT msg_id, sender, receiver, content, timestamp, is_read
                FROM messages
                WHERE is_read = 0 AND timestamp > datetime('now', '-1 hour')
                ORDER BY timestamp DESC
                LIMIT 50
            """)

            for row in cursor.fetchall():
                msg_id, sender, receiver, content, timestamp, is_read = row
                msg_hash = hashlib.md5(f"{msg_id}{content}".encode()).hexdigest()

                if msg_hash not in self.processed_messages:
                    self.processed_messages.add(msg_hash)
                    messages.append({
                        'id': msg_id,
                        'sender': sender,
                        'receiver': receiver,
                        'content': content,
                        'timestamp': timestamp,
                        'is_read': bool(is_read)
                    })

            conn.close()
        except Exception as e:
            logger.error(f"读取消息失败: {e}")

        return messages


class TMReplyEngine:
    """TM回复引擎"""

    def __init__(self, config: Dict):
        self.config = config
        self.keywords = config.get('keywords', {})
        self.templates = config.get('reply_templates', {})

    def detect_intent(self, message: str) -> str:
        """检测消息意图"""
        message_lower = message.lower()

        for intent, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    logger.info(f"检测到意图: {intent}")
                    return intent

        return "default"

    def generate_reply(self, intent: str, context: Dict = None) -> str:
        """生成回复"""
        template = self.templates.get(intent, self.templates.get('default'))

        # 如果有上下文，替换模板中的占位符
        if context:
            try:
                return template.format(**context)
            except KeyError:
                pass

        return template

    def ai_enhance_reply(self, original_reply: str, buyer_message: str) -> str:
        """AI增强回复（可选功能）"""
        # 这里可以集成AI API进行回复优化
        # 例如使用MiniMax API进行润色
        return original_reply


class TMAutoReply:
    """TM自动回复主控制器"""

    def __init__(self, config: Dict):
        self.config = config
        self.monitor = TMChatMonitor(config)
        self.reply_engine = TMReplyEngine(config)
        self.is_running = False

    def process_message(self, message: Dict) -> Optional[str]:
        """处理单条消息"""
        logger.info(f"处理消息 from {message['sender']}: {message['content'][:50]}...")

        # 检测意图
        intent = self.reply_engine.detect_intent(message['content'])

        # 生成回复
        reply = self.reply_engine.generate_reply(intent, {
            'moq': '100 pcs',
            'sample_info': 'Sample cost + shipping',
            'lead_time': '7-15'
        })

        return reply

    def send_reply(self, chat_hwnd: int, reply: str):
        """发送回复到聊天窗口"""
        try:
            import win32gui
            import win32clipboard
            import win32con

            # 复制回复到剪贴板
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(reply)
            win32clipboard.CloseClipboard()

            # 粘贴到输入框并发送
            win32gui.SetForegroundWindow(chat_hwnd)
            time.sleep(0.3)

            # Ctrl+V 粘贴
            win32api = __import__('win32api')
            win32api.keybd_event(17, 0, 0, 0)  # Ctrl down
            win32api.keybd_event(86, 0, 0, 0)  # V down
            win32api.keybd_event(86, 0, win32con.KEYEVENTF_KEYUP, 0)  # V up
            win32api.keybd_event(17, 0, win32con.KEYEVENTF_KEYUP, 0)  # Ctrl up

            time.sleep(0.3)

            # Enter发送
            win32api.keybd_event(13, 0, 0, 0)  # Enter down
            win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)  # Enter up

            logger.info(f"回复已发送: {reply[:30]}...")

        except Exception as e:
            logger.error(f"发送回复失败: {e}")

    def start(self):
        """启动自动回复"""
        self.is_running = True
        logger.info("TM自动回复系统已启动")

        while self.is_running:
            try:
                # 读取新消息
                messages = self.monitor.read_new_messages()

                for message in messages:
                    if not self.config.get('auto_reply', True):
                        continue

                    # 生成回复
                    reply = self.process_message(message)

                    if reply:
                        if self.config.get('review_mode', True):
                            logger.info(f"[审核模式] 建议回复: {reply}")
                            logger.info(f"[审核模式] 输入 'y' 确认发送，'n' 跳过")
                            # TODO: 实现审核机制
                        else:
                            # 直接发送
                            pass

                time.sleep(self.config.get('monitor_interval', 5))

            except KeyboardInterrupt:
                logger.info("收到停止信号")
                self.stop()
            except Exception as e:
                logger.error(f"运行时错误: {e}")
                time.sleep(10)

    def stop(self):
        """停止自动回复"""
        self.is_running = False
        logger.info("TM自动回复系统已停止")


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description='TM聊天自动回复系统')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--mode', '-m', choices=['monitor', 'auto'], default='auto',
                       help='运行模式: monitor=仅监控, auto=自动回复')
    parser.add_argument('--tm-path', help='TM安装路径')

    args = parser.parse_args()

    # 加载配置
    config = TMConfig.load_config(args.config)

    if args.tm_path:
        config['tm_path'] = args.tm_path

    if args.mode == 'monitor':
        config['auto_reply'] = False

    # 启动系统
    auto_reply = TMAutoReply(config)

    if not auto_reply.monitor.tm_path:
        logger.error("未找到TM安装，请检查配置")
        return 1

    auto_reply.start()
    return 0


if __name__ == '__main__':
    sys.exit(main())