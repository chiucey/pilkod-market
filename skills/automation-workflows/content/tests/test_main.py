"""
Unit Tests for automation-workflows Skill

Tests cover:
- Normal input handling
- Empty/None input handling
- Error handling
- Skill info retrieval

Author: MiniMax Agent
"""

import unittest
import sys
import os

# Add src directory to Python path for module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import run, get_skill_info


class TestAutomationWorkflowsSkill(unittest.TestCase):
    """Test cases for automation-workflows skill"""

    def test_run_success_normal_input(self):
        """Test successful response with normal input"""
        result = run({"user_query": "帮我设计自动化工作流"})
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertEqual(result["data"]["skill_type"], "instructional_playbook")
        self.assertEqual(result["data"]["skill_name"], "automation-workflows")
        self.assertEqual(result["data"]["version"], "0.2.0")

    def test_run_success_empty_input(self):
        """Test successful response with empty input"""
        result = run({})
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)

    def test_run_success_none_input(self):
        """Test successful response with None input"""
        result = run(None)
        self.assertEqual(result["status"], "success")

    def test_run_success_empty_string_input(self):
        """Test successful response with empty string input"""
        result = run("")
        self.assertEqual(result["status"], "success")

    def test_run_with_various_queries(self):
        """Test response with various query types"""
        queries = [
            {"user_query": "自动化"},
            {"user_query": "workflow automation"},
            {"user_query": "如何减少重复工作"},
            {"query": "Zapier configuration"}
        ]
        for query in queries:
            result = run(query)
            self.assertEqual(result["status"], "success")
            self.assertIn("message_for_user", result)

    def test_skill_info_structure(self):
        """Test skill info returns correct structure"""
        info = get_skill_info()
        self.assertIn("name", info)
        self.assertIn("version", info)
        self.assertIn("description", info)
        self.assertIn("author", info)
        self.assertIn("triggers", info)
        self.assertEqual(info["name"], "automation-workflows")
        self.assertEqual(info["version"], "0.2.0")

    def test_capabilities_in_response(self):
        """Test that response includes all capabilities"""
        result = run({"user_query": "test"})
        capabilities = result["data"]["capabilities"]
        expected_capabilities = [
            "opportunity_identification",
            "tool_selection",
            "workflow_design",
            "building_testing",
            "monitoring_maintenance",
            "roi_calculation",
            "scenario_templates"
        ]
        for cap in expected_capabilities:
            self.assertIn(cap, capabilities)

    def test_supported_tools_in_response(self):
        """Test that response includes supported tools"""
        result = run({"user_query": "test"})
        tools = result["data"]["supported_tools"]
        self.assertIn("Zapier", tools)
        self.assertIn("Make", tools)
        self.assertIn("n8n", tools)


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""

    def test_invalid_input_type(self):
        """Test handling of invalid input types"""
        # Should handle gracefully even with invalid types
        try:
            result = run(123)
            self.assertEqual(result["status"], "success")
        except Exception as e:
            # If exception is raised, status should not be success
            self.fail(f"run() raised exception with integer input: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
