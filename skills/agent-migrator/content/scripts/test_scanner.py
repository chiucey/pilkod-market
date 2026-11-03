#!/usr/bin/env python3
"""
Test Suite for Agent Migrator Scanner
Tests core functionality including platform detection, component scanning, and report generation.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import (
    _deep_get, _mask, _safe_read_json, _detect_platform,
    _detect_subagents, _detect_mcp_servers, _detect_external_databases,
    scan_extended_components, platform_diff, scan_openclaw, generate_migration_plan,
    __version__
)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""

    def test_deep_get_nested_dict(self):
        """Test safe nested dict access."""
        obj = {"a": {"b": {"c": "value"}}}
        self.assertEqual(_deep_get(obj, "a", "b", "c"), "value")
        self.assertEqual(_deep_get(obj, "a", "b", "d"), None)
        self.assertEqual(_deep_get(obj, "a", "b", "c", "d"), None)

    def test_deep_get_list_access(self):
        """Test safe list access."""
        obj = {"items": [{"name": "first"}, {"name": "second"}]}
        self.assertEqual(_deep_get(obj, "items", 0, "name"), "first")
        self.assertEqual(_deep_get(obj, "items", 5, "name"), None)

    def test_mask_function(self):
        """Test string masking function - keeps 2 at start + remaining chars at end."""
        # "abcdefghij" (10 chars): 2 at start + 4 asterisks + remaining 8 = "ab****efghij"
        self.assertEqual(_mask("abcdefghij"), "ab****efghij")
        self.assertEqual(_mask("short"), "****")
        self.assertEqual(_mask(""), "****")
        self.assertEqual(_mask(None), "****")
        self.assertEqual(_mask("abcdefgh", keep_end=4), "ab****efgh")  # custom keep_end

    def test_safe_read_json_valid(self):
        """Test reading valid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"key": "value"}, f)
            temp_path = f.name

        try:
            result = _safe_read_json(temp_path)
            self.assertEqual(result, {"key": "value"})
        finally:
            os.unlink(temp_path)

    def test_safe_read_json_invalid(self):
        """Test reading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json}")
            temp_path = f.name

        try:
            result = _safe_read_json(temp_path)
            self.assertIsNone(result)
        finally:
            os.unlink(temp_path)

    def test_safe_read_json_nonexistent(self):
        """Test reading non-existent file."""
        result = _safe_read_json("/nonexistent/file.json")
        self.assertIsNone(result)


class TestPlatformDetection(unittest.TestCase):
    """Test platform detection."""

    def test_detect_openclaw(self):
        """Test OpenClaw platform detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(os.path.join(tmpdir, "openclaw.json")).touch()
            Path(os.path.join(tmpdir, "skills")).mkdir()
            detected = _detect_platform(tmpdir)
            self.assertEqual(detected, "openclaw")

    def test_detect_dify(self):
        """Test Dify platform detection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(os.path.join(tmpdir, "docker-compose.yml")).touch()
            detected = _detect_platform(tmpdir)
            self.assertEqual(detected, "dify")

    def test_detect_nothing(self):
        """Test no platform detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detected = _detect_platform(tmpdir)
            self.assertIsNone(detected)


class TestComponentDetection(unittest.TestCase):
    """Test extended component detection."""

    def test_detect_subagents_agents_array(self):
        """Test detecting subagents from agents array."""
        config = {
            "agents": [
                {"name": "subagent1", "type": "subagent", "model": "gpt-4"},
                {"name": "subagent2", "runtime": "agent", "model": "claude-3"}
            ]
        }
        result = _detect_subagents(config)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "subagent1")
        self.assertEqual(result[1]["type"], "agent")

    def test_detect_subagents_sessions(self):
        """Test detecting subagents from sessions."""
        config = {
            "sessions": [
                {"name": "session1", "runtime": "subagent", "model": "gpt-3.5"}
            ]
        }
        result = _detect_subagents(config)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "session1")

    def test_detect_subagents_deduplication(self):
        """Test subagent deduplication by name."""
        config = {
            "agents": [{"name": "agent1", "type": "subagent"}],
            "sessions": [{"name": "agent1", "type": "subagent"}]  # Duplicate name
        }
        result = _detect_subagents(config)
        self.assertEqual(len(result), 1)

    def test_detect_mcp_servers_array(self):
        """Test detecting MCP servers from array format."""
        config = {
            "mcpServers": [
                {"name": "server1", "url": "http://localhost:8080", "token": "secret123"},
                {"name": "server2", "url": "http://localhost:9090"}
            ]
        }
        result = _detect_mcp_servers(config)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(s["migratable"] is False for s in result))

    def test_detect_mcp_servers_object(self):
        """Test detecting MCP servers from object format."""
        config = {
            "mcp": {
                "servers": {
                    "github": {"url": "http://gh-mcp:3000", "auth": "ghp_xxx"}
                }
            }
        }
        result = _detect_mcp_servers(config)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "github")

    def test_detect_databases(self):
        """Test detecting external databases."""
        config = {
            "databases": [
                {"type": "postgresql", "host": "db.example.com", "port": 5432}
            ]
        }
        result = _detect_external_databases(config)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "postgresql")
        self.assertTrue(result[0]["migratable"] is False)

    def test_scan_extended_components_with_warnings(self):
        """Test that warnings are generated for detected components."""
        config = {
            "agents": [{"name": "agent1"}],
            "mcpServers": [{"name": "mcp1"}],
            "databases": [{"type": "supabase"}]
        }
        result = scan_extended_components.__wrapped__() if hasattr(scan_extended_components, '__wrapped__') else None

        # Test with actual files
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)

            # Create test config
            with open("openclaw.json", "w") as f:
                json.dump(config, f)

            result = scan_extended_components()

            self.assertEqual(len(result["subagents"]), 1)
            self.assertEqual(len(result["mcp_servers"]), 1)
            self.assertEqual(len(result["databases"]), 1)
            self.assertTrue(len(result["warnings"]) >= 3)


class TestPlatformDiff(unittest.TestCase):
    """Test platform difference analysis."""

    def test_same_platform_direct_migration(self):
        """Test same platform allows direct migration."""
        result = platform_diff("openclaw", "openclaw")
        self.assertTrue(result["can_direct_migrate"])
        self.assertFalse(result["needs_conversion"])

    def test_different_platform_needs_conversion(self):
        """Test different platforms need conversion."""
        result = platform_diff("openclaw", "coze")
        self.assertFalse(result["can_direct_migrate"])
        self.assertTrue(result["needs_conversion"])

    def test_unknown_pair_has_default_notes(self):
        """Test unknown platform pair has default notes."""
        result = platform_diff("custom1", "custom2")
        self.assertEqual(result["notes"], "暂无预设迁移路径，需人工评估")

    def test_diff_dimensions_structure(self):
        """Test diff dimensions returns correct structure."""
        result = platform_diff("openclaw", "dify")
        self.assertIn("dimensions", result)
        self.assertTrue(len(result["dimensions"]) > 0)
        for dim in result["dimensions"]:
            self.assertEqual(len(dim), 4)  # name, source, target, same?


class TestScanOpenclaw(unittest.TestCase):
    """Test OpenClaw scanning."""

    def test_scan_finds_config_files(self):
        """Test scanning finds required config files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)

            # Create test files
            Path("openclaw.json").write_text(json.dumps({"version": "1.0"}))
            Path(".env").write_text("API_KEY=test\n")
            Path("memory").mkdir()
            Path("memory/chat.md").write_text("# Memory")  # This adds a memory file
            Path("skills").mkdir()
            Path("skills/test-skill").mkdir()

            result = scan_openclaw(".")

            # 3 files: openclaw.json, .env, memory/chat.md
            self.assertEqual(len(result["files"]), 3)
            self.assertEqual(len(result["dirs"]), 1)  # skills/test-skill
            self.assertIn("openclaw.json", result["migration_category"])
            self.assertIn(".env", result["migration_category"])
            self.assertIn("memory/chat.md", result["migration_category"])
            self.assertEqual(result["migration_category"][".env"], "需重建")
            self.assertEqual(result["migration_category"]["openclaw.json"], "需转换")

    def test_scan_warnings_for_secrets(self):
        """Test scanning generates warnings for secrets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            Path(".env").write_text("API_KEY=test\n")
            Path("openclaw.json").write_text(json.dumps({}))

            result = scan_openclaw(".")

            warnings = result.get("warnings", [])
            self.assertTrue(any("敏感信息" in w for w in warnings))


class TestMigrationPlanGeneration(unittest.TestCase):
    """Test migration plan generation."""

    def test_generate_plan_basic_structure(self):
        """Test basic plan structure generation."""
        source_results = {
            "platform": "OpenClaw",
            "scan_path": "/test",
            "files": [
                {"path": "openclaw.json", "required": True, "type": "config", "purpose": "Core config"}
            ],
            "dirs": [],
            "warnings": []
        }
        diff_results = {
            "source": "openclaw",
            "target": "coze",
            "can_direct_migrate": False,
            "needs_conversion": True,
            "notes": "需要转换",
            "dimensions": []
        }
        ext_results = {
            "subagents": [],
            "mcp_servers": [],
            "databases": [],
            "warnings": []
        }

        plan = generate_migration_plan(source_results, diff_results, ext_results, "Coze")

        self.assertIn("# 智能体迁移方案", plan)
        self.assertIn("Coze", plan)
        self.assertIn("执行摘要", plan)
        self.assertIn("平台差异分析", plan)

    def test_generate_plan_includes_components(self):
        """Test plan includes extended components."""
        source_results = {
            "platform": "OpenClaw",
            "scan_path": "/test",
            "files": [],
            "dirs": [],
            "warnings": []
        }
        diff_results = {
            "source": "openclaw",
            "target": "coze",
            "can_direct_migrate": False,
            "needs_conversion": True,
            "notes": "需要转换",
            "dimensions": []
        }
        ext_results = {
            "subagents": [{"name": "agent1", "type": "subagent", "model": "gpt-4", "notes": "test"}],
            "mcp_servers": [{"name": "mcp1", "url": "http://test", "note": "test"}],
            "databases": [{"type": "supabase", "host": "test", "note": "test"}],
            "warnings": ["Warning 1"]
        }

        plan = generate_migration_plan(source_results, diff_results, ext_results, "Coze")

        self.assertIn("扩展组件检测", plan)
        self.assertIn("agent1", plan)
        self.assertIn("mcp1", plan)
        # Database type is uppercased in output (SUPABASE)
        self.assertTrue("SUPABASE" in plan or "supabase" in plan)
        self.assertIn("Warning 1", plan)


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    def test_full_scan_workflow(self):
        """Test complete scanning workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)

            # Create test configuration
            config = {
                "agents": [{"name": "test-agent", "type": "subagent", "model": "gpt-4"}],
                "mcpServers": [{"name": "test-mcp", "url": "http://localhost:8080"}],
                "databases": [{"type": "supabase", "host": "test.supabase.co"}]
            }

            with open("openclaw.json", "w") as f:
                json.dump(config, f)

            with open(".env", "w") as f:
                f.write("SUPABASE_URL=https://test.supabase.co\n")
                f.write("API_KEY=secret123\n")

            Path("memory").mkdir()
            Path("memory/daily.md").write_text("# Daily notes")

            # Run scan
            scan_results = scan_openclaw(".")
            ext_results = scan_extended_components()
            diff_results = platform_diff("openclaw", "coze")

            # Generate plan
            plan = generate_migration_plan(scan_results, diff_results, ext_results, "Coze")

            # Assertions
            self.assertGreater(len(plan), 0)
            self.assertIn("test-agent", plan)
            self.assertIn("test-mcp", plan)
            self.assertIn("supabase", plan)


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
