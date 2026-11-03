#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书全链路自动化技能主入口
完全复刻ClawHub gog技能的交互逻辑，对接飞书开放平台API
"""

import sys
import json
import os
import time
import re
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("请先安装 requests: pip install requests", file=sys.stderr)
    sys.exit(1)

# 全局 token 缓存
_token_cache: Dict[str, Any] = {
    "tenant_token": None,
    "expires_at": 0
}

# API 基础地址
FEISHU_API_BASE = "https://open.feishu.cn"


def get_tenant_token(app_id: str, app_secret: str) -> Optional[str]:
    """
    获取飞书租户访问凭证，带缓存机制
    凭证有效期2小时，提前60秒刷新
    """
    now = time.time()
    if _token_cache["tenant_token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["tenant_token"]

    url = f"{FEISHU_API_BASE}/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") == 0:
            token = data.get("tenant_access_token")
            expire = data.get("expire", 7200)
            _token_cache["tenant_token"] = token
            _token_cache["expires_at"] = now + expire - 60
            return token
        else:
            print(f"获取token失败: code={data.get('code')}, msg={data.get('msg')}", file=sys.stderr)
            return None
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"获取token异常: {e}", file=sys.stderr)
        return None


def _request(method: str, path: str, token: str, data: Dict = None) -> Dict:
    """
    统一的飞书API请求封装
    处理认证、错误码、超时等通用逻辑
    """
    url = f"{FEISHU_API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.request(method, url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()

        if result.get("code") != 0:
            error_msg = result.get("msg", "未知错误")
            raise FeishuAPIError(f"飞书API错误 {result.get('code')}: {error_msg}")

        return result.get("data", {})
    except requests.exceptions.RequestException as e:
        raise FeishuAPIError(f"网络请求失败: {e}")
    except FeishuAPIError:
        raise
    except Exception as e:
        raise FeishuAPIError(f"请求异常: {e}")


class FeishuAPIError(Exception):
    """飞书API异常"""
    pass


def _convert_markdown_to_docx_blocks(content: str) -> List[Dict]:
    """
    将 Markdown 内容转换为飞书 Docx 块结构
    支持：标题、段落、列表、代码块等基础元素
    """
    blocks = []
    lines = content.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blocks.append({
                "block_type": 2,  # 空块
                "text": {"elements": [{"text_run": {"content": ""}}]}
            })
            continue

        # 标题处理
        if stripped.startswith("# "):
            blocks.append({
                "block_type": 3,  # 标题1
                "heading1": {
                    "elements": [{"text_run": {"content": stripped[2:]}}],
                    "style": {}
                }
            })
        elif stripped.startswith("## "):
            blocks.append({
                "block_type": 4,  # 标题2
                "heading2": {
                    "elements": [{"text_run": {"content": stripped[3:]}}],
                    "style": {}
                }
            })
        elif stripped.startswith("### "):
            blocks.append({
                "block_type": 5,  # 标题3
                "heading3": {
                    "elements": [{"text_run": {"content": stripped[4:]}}],
                    "style": {}
                }
            })
        # 列表处理
        elif stripped.startswith("- ") or stripped.startswith("* "):
            blocks.append({
                "block_type": 12,  # 无序列表
                "bullet": {
                    "elements": [{"text_run": {"content": stripped[2:]}}],
                    "style": {}
                }
            })
        elif re.match(r'^\d+\. ', stripped):
            match = re.match(r'^(\d+)\. (.*)', stripped)
            if match:
                blocks.append({
                    "block_type": 13,  # 有序列表
                    "ordered": {
                        "number": int(match.group(1)),
                        "elements": [{"text_run": {"content": match.group(2)}}],
                        "style": {}
                    }
                })
        # 引用处理
        elif stripped.startswith("> "):
            blocks.append({
                "block_type": 14,  # 引用
                "quote": {
                    "elements": [{"text_run": {"content": stripped[2:]}}],
                    "style": {}
                }
            })
        # 代码块处理
        elif stripped.startswith("```"):
            blocks.append({
                "block_type": 15,  # 代码块
                "code": {
                    "elements": [{"text_run": {"content": stripped[3:]}}],
                    "style": {"lang": "python"}
                }
            })
        # 分割线
        elif stripped == "---" or stripped == "***" or stripped == "___":
            blocks.append({
                "block_type": 22,  # 分割线
                "divider": {}
            })
        # 普通段落
        else:
            blocks.append({
                "block_type": 2,  # 段落
                "text": {
                    "elements": [{"text_run": {"content": stripped}}],
                    "style": {}
                }
            })

    return blocks


def create_document(
    token: str,
    title: str,
    content: str = "",
    folder_token: str = None
) -> Dict[str, Any]:
    """
    创建飞书云文档
    - title: 文档标题
    - content: 文档内容（支持Markdown）
    - folder_token: 目标文件夹Token（可选）
    """
    # 1. 创建空文档
    create_url = "/open-apis/docx/v1/documents"
    create_data = {"title": title}
    if folder_token:
        create_data["folder_token"] = folder_token

    doc = _request("POST", create_url, token, create_data)
    document_id = doc.get("document", {}).get("document_id")

    if not document_id:
        raise FeishuAPIError("创建文档失败，未返回document_id")

    # 2. 添加内容块
    if content:
        blocks = _convert_markdown_to_docx_blocks(content)
        if blocks:
            # 分批添加块，避免单次请求过大
            batch_size = 50
            for i in range(0, len(blocks), batch_size):
                batch = blocks[i:i + batch_size]
                block_url = f"/open-apis/docx/v1/documents/{document_id}/blocks"
                block_data = {
                    "children": batch,
                    "index": i
                }
                _request("POST", block_url, token, block_data)

    return {
        "document_id": document_id,
        "url": f"https://bytedance.feishu.cn/docx/{document_id}"
    }


def update_document(
    token: str,
    document_id: str,
    content: str
) -> Dict[str, Any]:
    """
    更新飞书云文档内容
    - document_id: 文档ID
    - content: 新的文档内容（Markdown格式）
    """
    # 获取当前文档块
    get_blocks_url = f"/open-apis/docx/v1/documents/{document_id}/blocks"
    current_blocks = _request("GET", get_blocks_url, token)

    # 删除现有内容块（保留文档根节点）
    block_list = current_blocks.get("items", [])
    if block_list:
        # 获取子块ID
        child_blocks = [b for b in block_list if b.get("parent_id")]
        if child_blocks:
            block_ids = [b["block_id"] for b in child_blocks]
            delete_url = f"/open-apis/docx/v1/documents/{document_id}/blocks/batch_delete"
            _request("POST", delete_url, token, {"start_index": 0, "end_index": len(block_ids)})

    # 添加新内容
    blocks = _convert_markdown_to_docx_blocks(content)
    if blocks:
        batch_size = 50
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            block_url = f"/open-apis/docx/v1/documents/{document_id}/blocks"
            block_data = {
                "children": batch,
                "index": i
            }
            _request("POST", block_url, token, block_data)

    return {
        "document_id": document_id,
        "url": f"https://bytedance.feishu.cn/docx/{document_id}"
    }


def get_document(token: str, document_id: str) -> Dict[str, Any]:
    """
    获取飞书云文档内容
    - document_id: 文档ID
    """
    get_url = f"/open-apis/docx/v1/documents/{document_id}"
    doc = _request("GET", get_url, token)

    return {
        "document_id": document_id,
        "title": doc.get("document", {}).get("title", ""),
        "url": f"https://bytedance.feishu.cn/docx/{document_id}"
    }


def share_document(
    token: str,
    document_id: str,
    member_type: str = "openid",
    member_ids: List[str] = None,
    permission: str = "view"
) -> Dict[str, Any]:
    """
    分享飞书云文档权限
    - document_id: 文档ID
    - member_type: 成员类型 (openid/userid/unionid/email)
    - member_ids: 成员ID列表
    - permission: 权限类型 (view/edit/full_access)
    """
    if not member_ids:
        raise FeishuAPIError("缺少成员ID列表")

    share_url = f"/open-apis/drive/v1/permissions/{document_id}/members?type=docx"
    payload = {
        "member_type": member_type,
        "member_ids": member_ids,
        "permission": permission
    }

    result = _request("POST", share_url, token, payload)

    return {
        "document_id": document_id,
        "shared": True,
        "member_count": len(member_ids)
    }


def create_calendar_event(
    token: str,
    summary: str,
    start_time: Union[str, datetime],
    end_time: Union[str, datetime],
    attendees: List[str] = None,
    calendar_id: str = "primary",
    description: str = "",
    location: str = ""
) -> Dict[str, Any]:
    """
    创建飞书日历事件
    - summary: 事件主题
    - start_time/end_time: ISO格式时间字符串或datetime对象
    - attendees: 参会人ID列表
    - calendar_id: 日历ID（默认为主日历）
    - description: 事件描述
    - location: 会议地点
    """
    # 时间格式转换
    if isinstance(start_time, str):
        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
    else:
        start = start_time

    if isinstance(end_time, str):
        end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    else:
        end = end_time

    # 确保时区信息
    if not start.tzinfo:
        start = start.replace(tzinfo=datetime.timezone(timedelta(hours=8)))
    if not end.tzinfo:
        end = end.replace(tzinfo=datetime.timezone(timedelta(hours=8)))

    start_str = start.strftime("%Y-%m-%dT%H:%M:%S%z")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%S%z")

    url_path = f"/open-apis/calendar/v4/calendars/{calendar_id}/events"
    payload = {
        "summary": summary,
        "start_time": {"timestamp": start_str, "timezone": "Asia/Shanghai"},
        "end_time": {"timestamp": end_str, "timezone": "Asia/Shanghai"},
        "description": description,
        "location": {"name": location} if location else None,
        "attendees": [{"user_id": user_id, "type": "user"} for user_id in (attendees or [])],
        "reminders": [{"minutes": 15}]  # 提前15分钟提醒
    }

    result = _request("POST", url_path, token, payload)

    return {
        "event_id": result.get("event", {}).get("event_id"),
        "url": result.get("event", {}).get("html_link"),
        "summary": summary,
        "start_time": start_str,
        "end_time": end_str
    }


def create_approval(
    token: str,
    title: str,
    approver: str,
    form_content: Dict[str, Any] = None,
    approval_code: str = "standard",
    extra_data: Dict = None
) -> Dict[str, Any]:
    """
    发起飞书审批
    - title: 审批标题
    - approver: 审批人ID
    - form_content: 审批表单内容
    - approval_code: 审批模板代码
    """
    url_path = "/open-apis/approval/v4/instances"

    # 构建表单内容
    if form_content is None:
        form_content = {}

    # 将表单转换为飞书审批格式
    form_items = []
    for key, value in form_content.items():
        form_items.append({
            "id": str(hash(key)) % 1000000,
            "type": "Text",
            "value": str(value)
        })

    payload = {
        "approval_code": approval_code,
        "title": title,
        "approver_id": approver,
        "form_content": json.dumps(form_items),
        "extra_data": extra_data or {}
    }

    result = _request("POST", url_path, token, payload)

    return {
        "instance_id": result.get("instance_id"),
        "url": result.get("url"),
        "title": title
    }


def send_email(
    token: str,
    to: Union[str, List[str]],
    subject: str,
    body: str,
    body_type: str = "html",
    cc: Union[str, List[str]] = None,
    bcc: Union[str, List[str]] = None
) -> Dict[str, Any]:
    """
    发送飞书邮箱邮件
    - to: 收件人邮箱（支持字符串或列表）
    - subject: 邮件主题
    - body: 邮件正文
    - body_type: 正文类型 (html/plain)
    - cc: 抄送
    - bcc: 密送
    """
    # 统一转换为列表格式
    if isinstance(to, str):
        to_list = [to]
    else:
        to_list = to

    if isinstance(cc, str):
        cc_list = [cc]
    elif cc:
        cc_list = cc
    else:
        cc_list = []

    if isinstance(bcc, str):
        bcc_list = [bcc]
    elif bcc:
        bcc_list = bcc
    else:
        bcc_list = []

    url_path = "/open-apis/mail/v1/messages/send"
    payload = {
        "to": [{"email": email} for email in to_list],
        "cc": [{"email": email} for email in cc_list] if cc_list else [],
        "bcc": [{"email": email} for email in bcc_list] if bcc_list else [],
        "subject": subject,
        "body": body,
        "body_type": body_type
    }

    result = _request("POST", url_path, token, payload)

    return {
        "message_id": result.get("message_id"),
        "to": to_list,
        "subject": subject
    }


def generate_meeting_summary(
    meeting_notes: str,
    participants: List[str] = None,
    meeting_time: str = None
) -> str:
    """
    自动生成会议纪要（基于用户提供的会议记录）
    - meeting_notes: 用户提供的原始会议记录
    - participants: 参会人员列表
    - meeting_time: 会议时间
    """
    # 解析并结构化会议记录
    lines = meeting_notes.split("\n")
    summary_parts = []

    # 提取标题
    title_found = False
    for line in lines[:5]:  # 前5行查找标题
        if "# " in line or "标题" in line or "主题" in line:
            title_found = True
            break

    if not title_found:
        summary_parts.append("# 会议纪要\n")

    # 添加会议信息
    if meeting_time or participants:
        summary_parts.append("## 会议信息\n")
        if meeting_time:
            summary_parts.append(f"- **时间**: {meeting_time}\n")
        if participants:
            summary_parts.append(f"- **参会人**: {', '.join(participants)}\n")
        summary_parts.append("\n")

    # 提取关键内容
    summary_parts.append("## 会议内容\n")
    summary_parts.append(meeting_notes)
    summary_parts.append("\n\n")

    # 添加行动项提示
    summary_parts.append("## 待跟进事项\n")
    summary_parts.append("- [ ] \n")

    return "".join(summary_parts)


def parse_natural_language_request(user_input: str) -> Dict[str, Any]:
    """
    解析自然语言请求，提取意图和参数
    这是一个简化的实现，实际项目中可能需要更复杂的NLP处理
    """
    result = {
        "action": None,
        "parameters": {},
        "confidence": 0.0
    }

    # 意图识别
    user_lower = user_input.lower()

    # 文档相关
    if any(kw in user_lower for kw in ["文档", "doc", "整理", "写入"]):
        result["action"] = "create_document"
        result["confidence"] = 0.8

        # 尝试提取标题
        title_match = re.search(r'[把将]?(.+?)[整理写成]', user_input)
        if title_match:
            result["parameters"]["title"] = title_match.group(1).strip()

    # 日历/会议相关
    elif any(kw in user_lower for kw in ["会议", "预约", "日历", "calendar"]):
        result["action"] = "create_calendar_event"
        result["confidence"] = 0.8

        # 尝试提取会议主题
        if "会议" in user_lower:
            result["parameters"]["summary"] = "会议"

    # 审批相关
    elif any(kw in user_lower for kw in ["审批", "approve", "申请"]):
        result["action"] = "create_approval"
        result["confidence"] = 0.8

    # 邮件相关
    elif any(kw in user_lower for kw in ["邮件", "email", "发邮件", "给"]):
        result["action"] = "send_email"
        result["confidence"] = 0.8

    return result


def run(input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    执行Skill的核心功能
    复刻ClawHub gog技能的run逻辑

    input_data 应包含:
        action: str - 操作类型
        parameters: dict - 操作参数
        confirm: bool - 是否已确认
        user_content: str - 用户原始输入（可选，用于自然语言解析）
    """
    try:
        if not input_data:
            return {
                "status": "error",
                "data": None,
                "message_for_user": "未提供有效的输入参数。"
            }

        action = input_data.get("action")
        params = input_data.get("parameters", {})
        confirm = input_data.get("confirm", False)
        user_content = input_data.get("user_content", "")

        # 敏感操作列表
        sensitive_actions = ["create_approval", "send_email"]

        # 如果未指定action但有用户输入，尝试解析自然语言
        if not action and user_content:
            parsed = parse_natural_language_request(user_content)
            if parsed.get("action"):
                action = parsed["action"]
                params = {**parsed.get("parameters", {}), **params}

        if not action:
            return {
                "status": "error",
                "data": None,
                "message_for_user": "无法识别操作类型。请指定具体操作：create_document, create_calendar_event, create_approval, send_email, update_document, share_document, get_document"
            }

        # 敏感操作需确认
        if action in sensitive_actions and not confirm:
            preview = {
                "action": action,
                "description": f"将执行 {action} 操作",
                "parameters": params
            }
            return {
                "status": "need_confirm",
                "data": preview,
                "message_for_user": f"请确认执行以下操作:\n- 操作类型: {action}\n- 参数: {json.dumps(params, ensure_ascii=False, indent=2)}\n\n如确认，请再次调用并设置 confirm=true。"
            }

        # 加载环境变量
        app_id = os.getenv("FEISHU_APP_ID")
        app_secret = os.getenv("FEISHU_APP_SECRET")

        if not app_id or not app_secret:
            return {
                "status": "error",
                "data": None,
                "message_for_user": "请先配置飞书的 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量。"
            }

        token = get_tenant_token(app_id, app_secret)
        if not token:
            return {
                "status": "error",
                "data": None,
                "message_for_user": "获取飞书访问凭证失败，请检查 APP_ID 和 APP_SECRET 是否正确，且应用已在租户内启用。"
            }

        # 路由分发
        if action == "create_document":
            title = params.get("title")
            content = params.get("content", "")
            folder_token = params.get("folder_token") or os.getenv("FEISHU_FOLDER_TOKEN")

            if not title:
                return {"status": "error", "data": None, "message_for_user": "缺少文档标题，请提供 title 参数。"}

            result = create_document(token, title, content, folder_token)
            msg = f"文档已创建成功！\n📄 标题: {title}\n🔗 链接: {result['url']}"
            return {"status": "success", "data": result, "message_for_user": msg}

        elif action == "update_document":
            document_id = params.get("document_id")
            content = params.get("content", "")

            if not document_id:
                return {"status": "error", "data": None, "message_for_user": "缺少文档ID，请提供 document_id 参数。"}

            result = update_document(token, document_id, content)
            msg = f"文档已更新成功！\n🔗 链接: {result['url']}"
            return {"status": "success", "data": result, "message_for_user": msg}

        elif action == "get_document":
            document_id = params.get("document_id")

            if not document_id:
                return {"status": "error", "data": None, "message_for_user": "缺少文档ID，请提供 document_id 参数。"}

            result = get_document(token, document_id)
            msg = f"文档信息:\n📄 标题: {result.get('title', 'N/A')}\n🔗 链接: {result['url']}"
            return {"status": "success", "data": result, "message_for_user": msg}

        elif action == "share_document":
            document_id = params.get("document_id")
            member_ids = params.get("member_ids", [])
            member_type = params.get("member_type", "openid")
            permission = params.get("permission", "view")

            if not document_id:
                return {"status": "error", "data": None, "message_for_user": "缺少文档ID。"}

            result = share_document(token, document_id, member_type, member_ids, permission)
            msg = f"文档权限已设置，已分享给 {result['member_count']} 位成员"
            return {"status": "success", "data": result, "message_for_user": msg}

        elif action == "create_calendar_event":
            summary = params.get("summary")
            start_time = params.get("start_time")
            end_time = params.get("end_time")
            attendees = params.get("attendees", [])
            calendar_id = params.get("calendar_id") or os.getenv("FEISHU_CALENDAR_ID", "primary")
            description = params.get("description", "")
            location = params.get("location", "")

            if not all([summary, start_time, end_time]):
                return {
                    "status": "error",
                    "data": None,
                    "message_for_user": "缺少必要参数。请提供：summary（会议主题）、start_time（开始时间）、end_time（结束时间）。时间格式：ISO 8601"
                }

            result = create_calendar_event(
                token, summary, start_time, end_time,
                attendees, calendar_id, description, location
            )
            msg = f"日历事件已创建！\n📅 主题: {summary}\n🕐 开始: {start_time}\n🕐 结束: {end_time}\n🔗 链接: {result.get('url', '无')}"
            return {"status": "success", "data": result, "message_for_user": msg}

        elif action == "create_approval":
            title = params.get("title")
            approver = params.get("approver")
            form_content = params.get("form_content", {})
            approval_code = params.get("approval_code") or os.getenv("FEISHU_APPROVAL_CODE", "standard")

            if not title or not approver:
                return {
                    "status": "error",
                    "data": None,
                    "message_for_user": "缺少审批标题（title）或审批人（approver）。"
                }

            result = create_approval(token, title, approver, form_content, approval_code)
            msg = f"审批已发起！\n📋 标题: {title}\n🔗 链接: {result.get('url', '无')}"
            return {"status": "success", "data": result, "message_for_user": msg}

        elif action == "send_email":
            to = params.get("to")
            subject = params.get("subject")
            body = params.get("body")
            body_type = params.get("body_type", "html")
            cc = params.get("cc")
            bcc = params.get("bcc")

            if not to or not subject or not body:
                return {
                    "status": "error",
                    "data": None,
                    "message_for_user": "缺少必要参数。请提供：to（收件人）、subject（主题）、body（正文）。"
                }

            result = send_email(token, to, subject, body, body_type, cc, bcc)
            to_display = to if isinstance(to, str) else ", ".join(to)
            msg = f"邮件已发送！\n📧 收件人: {to_display}\n📝 主题: {subject}"
            return {"status": "success", "data": result, "message_for_user": msg}

        elif action == "generate_meeting_summary":
            meeting_notes = params.get("meeting_notes", "")
            participants = params.get("participants", [])
            meeting_time = params.get("meeting_time")

            if not meeting_notes:
                return {
                    "status": "error",
                    "data": None,
                    "message_for_user": "缺少会议记录内容（meeting_notes）。"
                }

            # 自动生成结构化会议纪要
            summary_content = generate_meeting_summary(meeting_notes, participants, meeting_time)

            # 创建飞书文档
            title = params.get("title", "会议纪要")
            folder_token = params.get("folder_token") or os.getenv("FEISHU_FOLDER_TOKEN")
            result = create_document(token, title, summary_content, folder_token)

            msg = f"会议纪要已生成并创建为飞书文档！\n📄 标题: {title}\n🔗 链接: {result['url']}"
            return {"status": "success", "data": {"document": result, "summary_content": summary_content}, "message_for_user": msg}

        else:
            supported_actions = [
                "create_document", "update_document", "get_document", "share_document",
                "create_calendar_event", "create_approval", "send_email", "generate_meeting_summary"
            ]
            return {
                "status": "error",
                "data": None,
                "message_for_user": f"不支持的操作类型: {action}\n支持的操作: {', '.join(supported_actions)}"
            }

    except FeishuAPIError as e:
        error_msg = str(e)

        # 提供友好的错误提示
        if "code=99991663" in error_msg or "权限" in error_msg:
            hint = "\n\n提示: 请检查应用是否已开通相应权限，并在飞书开放平台完成权限配置。"
        elif "code=99991664" in error_msg or "认证" in error_msg:
            hint = "\n\n提示: 请检查 APP_ID 和 APP_SECRET 是否正确。"
        else:
            hint = ""

        return {
            "status": "error",
            "data": None,
            "message_for_user": f"执行失败: {error_msg}{hint}"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"执行异常: {str(e)}"
        }


if __name__ == "__main__":
    # 作为脚本运行时，从标准输入读取JSON参数
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        # 演示模式
        input_data = {}

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
