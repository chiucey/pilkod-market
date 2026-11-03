import unittest
import sys
import os
import tempfile
import shutil

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import (
    run, generate_id, get_learnings_dir, log_learning, log_error,
    log_feature_request, promote_learning, review_learnings,
    record_evolution, extract_pattern_key
)


class TestSelfImprovingAgent(unittest.TestCase):
    def setUp(self):
        """Set up temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        # Override environment variable for testing
        os.environ["LEARNINGS_DIR"] = os.path.join(self.test_dir, ".learnings")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_generate_id(self):
        """Test ID generation"""
        entry_id = generate_id("LRN", "20260327")
        self.assertTrue(entry_id.startswith("LRN-20260327-"))
        self.assertEqual(len(entry_id), 16)  # LRN-YYYYMMDD-XXX

    def test_log_learning(self):
        """Test logging a learning entry"""
        input_data = {
            "action": "log_learning",
            "params": {
                "category": "correction",
                "summary": "User corrected the approach",
                "details": "Initial approach was wrong, user provided correct method",
                "priority": "high",
                "area": "backend",
                "source": "user_feedback"
            }
        }

        result = run(input_data)
        self.assertEqual(result["status"], "success")
        self.assertIn("entry_id", result["data"])
        self.assertIn("file_path", result["data"])

        # Verify file was created
        self.assertTrue(os.path.exists(result["data"]["file_path"]))

    def test_log_error(self):
        """Test logging an error entry"""
        input_data = {
            "action": "log_error",
            "params": {
                "skill_or_command": "git_push",
                "summary": "Git push failed due to auth",
                "error_message": "Authentication failed",
                "command_attempted": "git push origin main",
                "priority": "high",
                "area": "config"
            }
        }

        result = run(input_data)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(result["data"]["file_path"]))

    def test_log_feature_request(self):
        """Test logging a feature request"""
        input_data = {
            "action": "log_feature_request",
            "params": {
                "capability_name": "auto_format",
                "requested_capability": "Automatic code formatting on save",
                "user_context": "User wants to avoid manual formatting",
                "complexity": "medium",
                "area": "frontend"
            }
        }

        result = run(input_data)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(result["data"]["file_path"]))

    def test_promote_learning(self):
        """Test promoting a learning to project memory"""
        # Set up target file path
        test_target = os.path.join(self.test_dir, "CLAUDE.md")
        os.environ["PROMOTE_TARGET_CLAUDE"] = test_target

        input_data = {
            "action": "promote_learning",
            "params": {
                "target_type": "claude",
                "content": "## Build & Dependencies\n- Package manager: pnpm (not npm) - use `pnpm install`"
            }
        }

        result = run(input_data)
        self.assertEqual(result["status"], "success")
        self.assertTrue(os.path.exists(test_target))

        # Verify content was written
        with open(test_target, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("Package manager: pnpm", content)

    def test_review_learnings(self):
        """Test reviewing learnings and getting status"""
        # First add some learnings
        input_data = {
            "action": "log_learning",
            "params": {
                "category": "test",
                "summary": "Test learning",
                "details": "This is a test",
                "priority": "low",
                "area": "testing"
            }
        }
        run(input_data)

        # Then review
        input_data = {
            "action": "review_learnings",
            "params": {}
        }
        result = run(input_data)

        self.assertEqual(result["status"], "success")
        self.assertIn("experience_count", result["data"])
        self.assertIn("lesson_count", result["data"])
        self.assertIn("iteration_count", result["data"])

    def test_extract_pattern_key(self):
        """Test pattern key extraction"""
        # Test API pattern
        pattern = extract_pattern_key(
            "API call fails with timeout",
            "The API call times out after 30 seconds"
        )
        self.assertEqual(pattern, "pattern-api")

        # Test command pattern
        pattern = extract_pattern_key(
            "Command fails consistently",
            "Running the command produces an error"
        )
        self.assertEqual(pattern, "pattern-command")

        # Test method pattern
        pattern = extract_pattern_key(
            "This method works for all cases",
            "Using this approach solves the problem"
        )
        self.assertEqual(pattern, "pattern-method")


class TestEvolutionTracking(unittest.TestCase):
    def setUp(self):
        """Set up temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        os.environ["LEARNINGS_DIR"] = os.path.join(self.test_dir, ".learnings")

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.test_dir)

    def test_evolution_count(self):
        """Test evolution count tracking"""
        from main import get_evolution_count

        # Initially 0
        self.assertEqual(get_evolution_count(), 0)

        # After logging a learning, should be 1
        log_learning({
            "category": "test",
            "summary": "Test learning"
        })

        self.assertEqual(get_evolution_count(), 1)


if __name__ == "__main__":
    unittest.main()
