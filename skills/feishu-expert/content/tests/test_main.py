#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书全链路自动化技能测试用例
对标 ClawHub gog 技能测试
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock, call

# 添加 src 目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from main import (
    run,
    get_tenant_token,
    create_document,
    create_calendar_event,
    create_approval,
    send_email,
    generate_meeting_summary,
    parse_natural_language_request,
    FeishuAPIError
)


class TestFeishuSkill(unittest.TestCase):
    """飞书技能单元测试"""

    def setUp(self):
        """设置测试环境"""
        os.environ["FEISHU_APP_ID"] = "test_app_id"
        os.environ["FEISHU_APP_SECRET"] = "test_app_secret"
        os.environ["FEISHU_FOLDER_TOKEN"] = "test_folder_token"

    def tearDown(self):
        """清理测试环境"""
        os.environ.pop("FEISHU_APP_ID", None)
        os.environ.pop("FEISHU_APP_SECRET", None)
        os.environ.pop("FEISHU_FOLDER_TOKEN", None)

    # ==================== Token 获取测试 ====================

    @patch("main.requests.post")
    def test_get_tenant_token_success(self, mock_post):
        """测试成功获取token"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "tenant_access_token": "test_token_123",
            "expire": 7200
        }
        mock_post.return_value = mock_response

        token = get_tenant_token("test_id", "test_secret")

        self.assertEqual(token, "test_token_123")
        mock_post.assert_called_once()

    @patch("main.requests.post")
    def test_get_tenant_token_failure(self, mock_post):
        """测试获取token失败"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 999,
            "msg": "invalid app_id or app_secret"
        }
        mock_post.return_value = mock_response

        token = get_tenant_token("test_id", "test_secret")

        self.assertIsNone(token)

    @patch("main.requests.post")
    def test_get_tenant_token_cached(self, mock_post):
        """测试token缓存机制"""
        # 第一次调用
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "code": 0,
            "tenant_access_token": "cached_token",
            "expire": 7200
        }
        mock_post.return_value = mock_response

        token1 = get_tenant_token("test_id", "test_secret")

        # 第二次调用应该使用缓存
        token2 = get_tenant_token("test_id", "test_secret")

        self.assertEqual(token1, token2)
        self.assertEqual(mock_post.call_count, 1)

    # ==================== 文档操作测试 ====================

    @patch("main.get_tenant_token")
    @patch("main._request")
    def test_create_document_success(self, mock_request, mock_token):
        """测试创建文档成功"""
        mock_token.return_value = "fake_token"
        mock_request.side_effect = [
            {"document": {"document_id": "doc123"}},  # 创建文档
            {}  # 添加内容块
        ]

        input_data = {
            "action": "create_document",
            "parameters": {
                "title": "测试文档",
                "content": "# 标题\n\n这是内容"
            },
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("doc123", result["data"]["document_id"])
        self.assertIn("bytedance.feishu.cn", result["data"]["url"])

    @patch("main.get_tenant_token")
    def test_create_document_missing_title(self, mock_token):
        """测试创建文档缺少标题"""
        mock_token.return_value = "fake_token"

        input_data = {
            "action": "create_document",
            "parameters": {"content": "some content"},
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "error")
        self.assertIn("title", result["message_for_user"].lower())

    @patch("main.get_tenant_token")
    def test_create_document_missing_credentials(self, mock_token):
        """测试缺少凭证"""
        os.environ.pop("FEISHU_APP_ID", None)
        os.environ.pop("FEISHU_APP_SECRET", None)

        input_data = {
            "action": "create_document",
            "parameters": {"title": "Test"},
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "error")
        self.assertIn("配置", result["message_for_user"])

    # ==================== 日历操作测试 ====================

    @patch("main.get_tenant_token")
    @patch("main._request")
    def test_create_calendar_event_success(self, mock_request, mock_token):
        """测试创建日历事件成功"""
        mock_token.return_value = "fake_token"
        mock_request.return_value = {
            "event": {
                "event_id": "event123",
                "html_link": "https://calendar.feishu.cn/event/xxx"
            }
        }

        input_data = {
            "action": "create_calendar_event",
            "parameters": {
                "summary": "项目会议",
                "start_time": "2025-03-28T15:00:00+08:00",
                "end_time": "2025-03-28T16:00:00+08:00",
                "attendees": ["user1", "user2"]
            },
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("event123", result["data"]["event_id"])

    @patch("main.get_tenant_token")
    def test_create_calendar_event_missing_params(self, mock_token):
        """测试创建日历事件缺少参数"""
        mock_token.return_value = "fake_token"

        input_data = {
            "action": "create_calendar_event",
            "parameters": {"summary": "只有主题"},
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "error")
        self.assertIn("start_time", result["message_for_user"].lower())

    # ==================== 审批操作测试 ====================

    @patch("main.get_tenant_token")
    @patch("main._request")
    def test_create_approval_need_confirm(self, mock_request, mock_token):
        """测试发起审批需要确认"""
        mock_token.return_value = "fake_token"

        input_data = {
            "action": "create_approval",
            "parameters": {
                "title": "预算审批",
                "approver": "manager001"
            },
            "confirm": False
        }

        result = run(input_data)

        self.assertEqual(result["status"], "need_confirm")
        self.assertIn("confirm", result["message_for_user"])

    @patch("main.get_tenant_token")
    @patch("main._request")
    def test_create_approval_confirmed(self, mock_request, mock_token):
        """测试确认后执行审批"""
        mock_token.return_value = "fake_token"
        mock_request.return_value = {
            "instance_id": "approval123",
            "url": "https://approval.feishu.cn/instance/xxx"
        }

        input_data = {
            "action": "create_approval",
            "parameters": {
                "title": "预算审批",
                "approver": "manager001",
                "form_content": {"金额": "10000"}
            },
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("approval123", result["data"]["instance_id"])

    # ==================== 邮件操作测试 ====================

    @patch("main.get_tenant_token")
    def test_send_email_need_confirm(self, mock_token):
        """测试发送邮件需要确认"""
        mock_token.return_value = "fake_token"

        input_data = {
            "action": "send_email",
            "parameters": {
                "to": "user@example.com",
                "subject": "测试邮件",
                "body": "<h1>测试</h1>"
            },
            "confirm": False
        }

        result = run(input_data)

        self.assertEqual(result["status"], "need_confirm")

    @patch("main.get_tenant_token")
    @patch("main._request")
    def test_send_email_confirmed(self, mock_request, mock_token):
        """测试确认后发送邮件"""
        mock_token.return_value = "fake_token"
        mock_request.return_value = {
            "message_id": "msg123"
        }

        input_data = {
            "action": "send_email",
            "parameters": {
                "to": "user@example.com",
                "subject": "测试邮件",
                "body": "<h1>测试</h1>"
            },
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("msg123", result["data"]["message_id"])

    # ==================== 会议纪要生成测试 ====================

    @patch("main.get_tenant_token")
    @patch("main._request")
    def test_generate_meeting_summary(self, mock_request, mock_token):
        """测试生成会议纪要"""
        mock_token.return_value = "fake_token"
        mock_request.side_effect = [
            {"document": {"document_id": "doc_summary"}},
            {}
        ]

        input_data = {
            "action": "generate_meeting_summary",
            "parameters": {
                "meeting_notes": "今天讨论了项目进度",
                "participants": ["张三", "李四"],
                "meeting_time": "2025-03-27 10:00"
            },
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("summary_content", result["data"])
        self.assertIn("会议纪要", result["data"]["summary_content"])

    def test_generate_meeting_summary_function(self):
        """测试会议纪要生成函数"""
        notes = "讨论了项目进度和下周计划"
        result = generate_meeting_summary(notes)

        self.assertIn("会议纪要", result)
        self.assertIn("会议内容", result)
        self.assertIn("待跟进事项", result)

    # ==================== 自然语言解析测试 ====================

    def test_parse_document_intent(self):
        """测试解析文档意图"""
        result = parse_natural_language_request("帮我把这份会议记录整理成飞书文档")

        self.assertEqual(result["action"], "create_document")
        self.assertGreater(result["confidence"], 0.5)

    def test_parse_calendar_intent(self):
        """测试解析日历意图"""
        result = parse_natural_language_request("帮我预约明天下午3点的会议")

        self.assertEqual(result["action"], "create_calendar_event")
        self.assertGreater(result["confidence"], 0.5)

    def test_parse_approval_intent(self):
        """测试解析审批意图"""
        result = parse_natural_language_request("帮我发起一个预算审批")

        self.assertEqual(result["action"], "create_approval")

    def test_parse_email_intent(self):
        """测试解析邮件意图"""
        result = parse_natural_language_request("给张三发一封邮件")

        self.assertEqual(result["action"], "send_email")

    # ==================== 错误处理测试 ====================

    def test_unsupported_action(self):
        """测试不支持的操作类型"""
        input_data = {
            "action": "unsupported_action",
            "parameters": {},
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "error")
        self.assertIn("不支持", result["message_for_user"])

    def test_no_input_data(self):
        """测试无输入数据"""
        result = run(None)

        self.assertEqual(result["status"], "error")

    @patch("main.get_tenant_token")
    def test_api_error_handling(self, mock_token):
        """测试API错误处理"""
        mock_token.side_effect = FeishuAPIError("API调用失败")

        input_data = {
            "action": "create_document",
            "parameters": {"title": "Test"},
            "confirm": True
        }

        result = run(input_data)

        self.assertEqual(result["status"], "error")


class TestMarkdownConversion(unittest.TestCase):
    """Markdown转换测试"""

    def test_convert_simple_text(self):
        """测试简单文本转换"""
        from main import _convert_markdown_to_docx_blocks

        content = "这是一段普通文本"
        blocks = _convert_markdown_to_docx_blocks(content)

        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["block_type"], 2)  # 段落

    def test_convert_heading(self):
        """测试标题转换"""
        from main import _convert_markdown_to_docx_blocks

        content = "# 一级标题\n## 二级标题\n### 三级标题"
        blocks = _convert_markdown_to_docx_blocks(content)

        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0]["block_type"], 3)  # 标题1
        self.assertEqual(blocks[1]["block_type"], 4)  # 标题2
        self.assertEqual(blocks[2]["block_type"], 5)  # 标题3

    def test_convert_list(self):
        """测试列表转换"""
        from main import _convert_markdown_to_docx_blocks

        content = "- 项目1\n- 项目2\n- 项目3"
        blocks = _convert_markdown_to_docx_blocks(content)

        self.assertEqual(len(blocks), 3)
        self.assertEqual(blocks[0]["block_type"], 12)  # 无序列表


if __name__ == "__main__":
    unittest.main(verbosity=2)
