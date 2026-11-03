#!/usr/bin/env python3
"""
GZH 职场万事通 - 邮件发送脚本
⚠️ 本脚本从 config.py 读取收件人和 SMTP 配置，禁止硬编码
用法：python3 scripts/send_email.py <日期> <zip附件路径> <邮件正文>
"""
import sys
import os
from pathlib import Path

# 添加父目录到 sys.path 以导入 config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS, RECIPIENTS, EMAIL_SUBJECT_TEMPLATE

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_email(date_str, zip_path, body_text):
    """发送带附件的邮件，收件人从 config.py 读取"""
    
    # 校验：确保收件人不包含其他技能的邮箱
    FORBIDDEN_RECIPIENTS = ['zhongyan@linewell.com', 'prd@linewell.com', 'ainews@linewell.com']
    for r in RECIPIENTS:
        if r in FORBIDDEN_RECIPIENTS:
            print(f"❌ 安全校验失败：收件人 {r} 不属于 GZH 技能！")
            print(f"   GZH 技能只能发送到：908075606@qq.com, 519010278@qq.com")
            sys.exit(1)
    
    # 校验：确保发件人是 QQ 邮箱
    if 'qq.com' not in SMTP_USER:
        print(f"❌ 安全校验失败：发件人 {SMTP_USER} 不是 QQ 邮箱！")
        print(f"   GZH 技能只能使用 908075606@qq.com 发送")
        sys.exit(1)

    subject = EMAIL_SUBJECT_TEMPLATE.format(date=date_str)
    
    msg = MIMEMultipart('mixed')
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(RECIPIENTS)
    msg['Subject'] = subject

    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    if os.path.exists(zip_path):
        with open(zip_path, 'rb') as f:
            part = MIMEApplication(f.read())
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(zip_path))
            msg.attach(part)
    else:
        print(f"⚠️ 附件不存在：{zip_path}")

    # 重试3次
    for attempt in range(1, 4):
        try:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, RECIPIENTS, msg.as_string())
            print(f"✅ 邮件发送成功！")
            print(f"   发件人：{SMTP_USER}")
            print(f"   收件人：{RECIPIENTS}")
            print(f"   主题：{subject}")
            print(f"   附件：{os.path.basename(zip_path)}")
            return
        except Exception as e:
            print(f"⚠️ 第 {attempt}/3 次发送失败：{e}")
            if attempt == 3:
                print("❌ 3次重试均失败，终止发送")
                sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法：python3 scripts/send_email.py <日期> <zip路径> <正文文件路径>")
        print("示例：python3 scripts/send_email.py 2026-04-26 ~/Desktop/JM/work/GZH内容/2026-04-26.zip body.txt")
        sys.exit(1)
    
    date_str = sys.argv[1]
    zip_path = os.path.expanduser(sys.argv[2])
    body_path = os.path.expanduser(sys.argv[3])
    
    with open(body_path, 'r', encoding='utf-8') as f:
        body_text = f.read()
    
    send_email(date_str, zip_path, body_text)
