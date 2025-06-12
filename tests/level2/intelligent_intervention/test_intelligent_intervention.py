import unittest
import os
import shutil
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
import subprocess
import json
from dataclasses import asdict

from shared_core.engines.developer_intelligent_intervention import (
    InterventionConfig, GitHelper, CodeScanner, DeveloperIntelligentIntervention
)

class TestGitHelper(unittest.TestCase):
    def setUp(self):
        self.test_repo_path = "/tmp/test_repo"
        if os.path.exists(self.test_repo_path):
            shutil.rmtree(self.test_repo_path)
        os.makedirs(self.test_repo_path)
        
        # Initialize a git repo
        subprocess.run(["git", "init"], check=True, capture_output=True, cwd=self.test_repo_path)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True, capture_output=True, cwd=self.test_repo_path)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True, capture_output=True, cwd=self.test_repo_path)
        
        # Create an initial commit
        with open(os.path.join(self.test_repo_path, "test_file.txt"), "w") as f:
            f.write("initial content")
        subprocess.run(["git", "add", "test_file.txt"], check=True, capture_output=True, cwd=self.test_repo_path)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True, capture_output=True, cwd=self.test_repo_path)

    def tearDown(self):
        if os.path.exists(self.test_repo_path):
            shutil.rmtree(self.test_repo_path)

    def test_get_repo_root(self):
        # Temporarily change directory for this test to simulate being inside the repo
        original_cwd = os.getcwd()
        os.chdir(self.test_repo_path)
        self.assertEqual(GitHelper.get_repo_root(), self.test_repo_path)
        os.chdir(original_cwd)

    def test_get_last_commit_time(self):
        original_cwd = os.getcwd()
        os.chdir(self.test_repo_path)
        commit_time = GitHelper.get_last_commit_time()
        self.assertIsNotNone(commit_time)
        self.assertIsInstance(commit_time, datetime)
        os.chdir(original_cwd)

    def test_get_uncommitted_changes(self):
        original_cwd = os.getcwd()
        os.chdir(self.test_repo_path)
        with open("new_file.txt", "w") as f:
            f.write("new content")
        changes = GitHelper.get_uncommitted_changes()
        self.assertIn("new_file.txt", changes)
        os.chdir(original_cwd)

    def test_auto_commit(self):
        original_cwd = os.getcwd()
        os.chdir(self.test_repo_path)
        with open("another_file.txt", "w") as f:
            f.write("some content")
        self.assertTrue(GitHelper.auto_commit("Test auto commit"))
        changes = GitHelper.get_uncommitted_changes()
        self.assertNotIn("another_file.txt", changes)
        os.chdir(original_cwd)

    # Add more tests for merge conflicts, PR creation, etc.

class TestCodeScanner(unittest.TestCase):
    def setUp(self):
        self.test_dir = "/tmp/test_code_scan"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.config = InterventionConfig()
        self.scanner = CodeScanner(self.config)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_directory_structure_scan(self):
        # Test missing directories
        issues = self.scanner.scan_directory(self.test_dir)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any(issue["type"] == "directory_structure" for issue in issues))

        # Create expected directories
        os.makedirs(os.path.join(self.test_dir, "src", "core"))
        os.makedirs(os.path.join(self.test_dir, "tests", "unit"))
        os.makedirs(os.path.join(self.test_dir, "docs", "api"))
        os.makedirs(os.path.join(self.test_dir, "docs", "user_guides"))
        issues = self.scanner.scan_directory(self.test_dir)
        self.assertFalse(any(issue["type"] == "directory_structure" for issue in issues if "缺少规范目录" in issue["message"]))

    def test_file_naming_scan(self):
        with open(os.path.join(self.test_dir, "BadFileName.py"), "w") as f:
            f.write("print(\"hello\")")
        issues = self.scanner.scan_directory(self.test_dir)
        self.assertTrue(any(issue["type"] == "file_naming" for issue in issues))

    def test_class_function_naming_scan(self):
        code = """
class badClassName:
    def BadFunctionName(self):
        pass
"""
        with open(os.path.join(self.test_dir, "good_file_name.py"), "w") as f:
            f.write(code)
        issues = self.scanner.scan_directory(self.test_dir)
        self.assertTrue(any(issue["type"] == "class_naming" for issue in issues))
        self.assertTrue(any(issue["type"] == "function_naming" for issue in issues))

    def test_manus_reference_removal_scan(self):
        code = """
        print("This is a manus reference.")
        """
        with open(os.path.join(self.test_dir, "test_manus.py"), "w") as f:
            f.write(code)
        issues = self.scanner.scan_directory(self.test_dir)
        self.assertTrue(any(issue["type"] == "manus_reference" for issue in issues))

class TestDeveloperIntelligentIntervention(unittest.TestCase):
    def setUp(self):
        # Pass a dummy config path, as the class expects a path, not an object
        self.config_path = "/tmp/dummy_config.json"
        with open(self.config_path, "w") as f:
            json.dump(asdict(InterventionConfig()), f) # Use asdict to convert dataclass to dict
        self.intervention_engine = DeveloperIntelligentIntervention(self.config_path)

    def tearDown(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    @patch("shared_core.engines.developer_intelligent_intervention.GitHelper")
    def test_git_checkin_reminder(self, mock_GitHelper):
        mock_GitHelper.get_repo_root.return_value = "/mock/repo"
        mock_GitHelper.get_last_commit_time.return_value = datetime.now(timezone.utc) - timedelta(minutes=self.intervention_engine.config.git_checkin_reminder_interval + 1)
        mock_GitHelper.get_uncommitted_changes.return_value = ["file1.txt"]
        mock_GitHelper.auto_commit.return_value = True

        # Simulate a check
        self.intervention_engine._check_git_status()
        mock_GitHelper.auto_commit.assert_called_once_with("Auto-commit by PowerAutomation intelligent intervention engine.")

    # Add more tests for other intervention types

if __name__ == '__main__':
    # Ensure subprocess is available for GitHelper tests
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        print("Git is not installed. Skipping GitHelper tests.")
        # Remove GitHelper tests from the suite if git is not available
        # This part needs to be handled carefully in a real test runner.
        # For this context, we'll assume git is available or the tests will fail.
    
    unittest.main(argv=["first-arg-is-ignored"], exit=False)




