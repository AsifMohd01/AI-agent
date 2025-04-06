"""
Test script for the Autonomous AI Agent.
This script tests the AI agent's ability to perform tasks in different environments.
"""

import unittest
import json
from app import AIAgent

class TestAIAgent(unittest.TestCase):
    def setUp(self):
        self.agent = AIAgent()
    
    def test_browser_execution(self):
        """Test browser environment execution"""
        result = self.agent.browser_execution("navigate to https://www.example.com")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["url"], "https://www.example.com")
        self.assertIn("title", result)
    
    def test_terminal_execution(self):
        """Test terminal environment execution"""
        result = self.agent.terminal_execution("echo Hello, World!")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["command"], "echo Hello, World!")
        self.assertIn("Hello, World!", result["stdout"])
    
    def test_file_system_execution(self):
        """Test file system environment execution"""
        # Create a test file
        result = self.agent.file_system_execution("create file test_file.txt with content Hello, World!")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "create_file")
        
        # Read the test file
        result = self.agent.file_system_execution("read file test_file.txt")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "read_file")
        self.assertEqual(result["content"], "Hello, World!")
        
        # Delete the test file
        result = self.agent.file_system_execution("delete file test_file.txt")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "delete_file")
    
    def test_invalid_commands(self):
        """Test handling of invalid commands"""
        # Invalid browser action
        result = self.agent.browser_execution("do something invalid")
        self.assertEqual(result["status"], "error")
        
        # Invalid terminal command
        result = self.agent.terminal_execution("rm -rf /")  # Should be blocked for security
        self.assertEqual(result["status"], "error")
        
        # Invalid file system action
        result = self.agent.file_system_execution("corrupt file system")
        self.assertEqual(result["status"], "error")

if __name__ == "__main__":
    unittest.main()