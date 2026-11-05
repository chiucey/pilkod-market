"""
职场万事通 (GZH) - 统一配置文件
⚠️ 技能隔离：本配置仅限 GZH 技能使用，禁止被其他技能引用
"""

import os

# ===== 路径配置 =====
BASE_DIR = os.path.expanduser('~/Desktop/JM/work/GZH内容')

# ===== SMTP 邮件配置（GZH 专用）=====
SMTP_SERVER = 'smtp.qq.com'
SMTP_PORT = 465  # SSL端口
SMTP_USER = '908075606@qq.com'
SMTP_PASS = 'zenwiwgyvbmnbeeh'

# ===== 收件人列表（GZH 专用，禁止使用日报/周报收件人）=====
RECIPIENTS = [
    '908075606@qq.com',
    '519010278@qq.com'
]

# ===== 邮件主题模板 =====
EMAIL_SUBJECT_TEMPLATE = '职场万事通 {date} 每日内容已生成'
