#!/usr/bin/env python3
"""
邮件发送脚本 - 支持 SMTP 和多种邮件服务
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict
import json


class EmailSender:
    """邮件发送器类"""

    def __init__(self, config: Dict[str, str]):
        self.smtp_host = config.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = config.get('SMTP_PORT', 587)
        self.smtp_user = config.get('SMTP_USER')
        self.smtp_password = config.get('SMTP_PASSWORD')
        self.from_email = config.get('FROM_EMAIL', self.smtp_user)
        self.use_tls = config.get('USE_TLS', True)

    def build_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html: bool = True,
        attachments: Optional[List[str]] = None
    ) -> MIMEMultipart:
        """构建邮件对象"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject

        # 添加纯文本版本
        if html:
            text_part = MIMEText(body, 'plain')
            html_part = MIMEText(body, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
        else:
            msg.attach(MIMEText(body, 'plain'))

        # 添加附件
        if attachments:
            for file_path in attachments:
                with open(file_path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    filename = os.path.basename(file_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}'
                    )
                    msg.attach(part)

        return msg

    def send(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html: bool = True,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """发送邮件"""
        try:
            msg = self.build_email(to_emails, subject, body, html, attachments)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return {
                'success': True,
                'sent_to': len(to_emails),
                'message': f'邮件已成功发送至 {len(to_emails)} 个收件人'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'发送失败: {str(e)}'
            }

    def batch_send(
        self,
        recipients: List[Dict[str, any]],
        subject_template: str,
        body_template: str,
        batch_size: int = 50
    ) -> Dict[str, any]:
        """批量发送邮件"""
        results = {
            'total': len(recipients),
            'success': 0,
            'failed': 0,
            'errors': []
        }

        for i in range(0, len(recipients), batch_size):
            batch = recipients[i:i + batch_size]
            for recipient in batch:
                # 替换模板变量
                subject = subject_template.format(**recipient)
                body = body_template.format(**recipient)
                to_email = recipient.get('email')

                if to_email:
                    result = self.send([to_email], subject, body)
                    if result['success']:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append({
                            'email': to_email,
                            'error': result.get('error')
                        })

        return results


def main():
    """示例用法"""
    config = {
        'SMTP_HOST': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', '587')),
        'SMTP_USER': os.getenv('SMTP_USER'),
        'SMTP_PASSWORD': os.getenv('SMTP_PASSWORD'),
        'FROM_EMAIL': os.getenv('FROM_EMAIL'),
        'USE_TLS': os.getenv('USE_TLS', 'true').lower() == 'true'
    }

    sender = EmailSender(config)

    # 发送示例邮件
    result = sender.send(
        to_emails=['recipient@example.com'],
        subject='测试邮件',
        body='<h1>这是一封测试邮件</h1><p>邮件发送功能正常！</p>',
        html=True
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
