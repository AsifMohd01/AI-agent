#!/usr/bin/env python
"""
Test script for the Autonomous AI Agent functionality.
This script tests the key components of the agent to ensure they work correctly.
"""

import os
import sys
import json
import logging
from app import AIAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_browser_extraction():
    """Test the browser extraction functionality"""
    agent = AIAgent()
    
    # Test headline extraction
    action = "extract headlines from AI news"
    result = agent.browser_execution(action)
    
    logger.info(f"Headline extraction result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action_type"] == "extraction"
    assert result["extraction_type"] == "headlines"
    
    # Test pros/cons extraction
    action = "extract pros and cons from smartphone reviews"
    result = agent.browser_execution(action)
    
    logger.info(f"Pros/cons extraction result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action_type"] == "extraction"
    assert result["extraction_type"] == "pros_cons"
    
    # Test trend analysis
    action = "analyze trends in renewable energy"
    result = agent.browser_execution(action)
    
    logger.info(f"Trend analysis result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action_type"] == "extraction"
    assert result["extraction_type"] == "trends"
    
    # Test summary extraction
    action = "summarize information about climate change"
    result = agent.browser_execution(action)
    
    logger.info(f"Summary extraction result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action_type"] == "extraction"
    assert result["extraction_type"] == "summary"
    
    logger.info("All browser extraction tests passed!")

def test_file_system_operations():
    """Test the file system operations"""
    agent = AIAgent()
    
    # Test creating a directory
    action = "create directory test_dir"
    result = agent.file_system_execution(action)
    
    logger.info(f"Create directory result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action"] == "create_directory"
    assert os.path.exists("test_dir")
    
    # Test creating a file
    action = "create file test_dir/test.txt with content Hello, world!"
    result = agent.file_system_execution(action)
    
    logger.info(f"Create file result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action"] == "create_file"
    assert os.path.exists("test_dir/test.txt")
    
    # Test reading a file
    action = "read file test_dir/test.txt"
    result = agent.file_system_execution(action)
    
    logger.info(f"Read file result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action"] == "read_file"
    assert result["content"] == "Hello, world!"
    
    # Test saving extracted content to a file
    # First, add an extraction result to the history
    extraction_result = {
        "action_type": "extraction",
        "extraction_type": "headlines",
        "extracted_content": [
            {"headline": "Test Headline 1", "source": "test.com", "url": "https://test.com/1"},
            {"headline": "Test Headline 2", "source": "test.com", "url": "https://test.com/2"}
        ]
    }
    agent.history.append(extraction_result)
    
    action = "save headlines to file test_dir/headlines.txt"
    result = agent.file_system_execution(action)
    
    logger.info(f"Save to file result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action"] == "save_to_file"
    assert os.path.exists("test_dir/headlines.txt")
    
    # Test listing a directory
    action = "list directory test_dir"
    result = agent.file_system_execution(action)
    
    logger.info(f"List directory result: {json.dumps(result, indent=2)}")
    assert result["status"] == "success"
    assert result["action"] == "list_directory"
    assert "test.txt" in result["files"]
    assert "headlines.txt" in result["files"]
    
    # Clean up
    os.remove("test_dir/test.txt")
    os.remove("test_dir/headlines.txt")
    os.rmdir("test_dir")
    
    logger.info("All file system tests passed!")

def test_execution_plan():
    """Test the execution plan functionality"""
    agent = AIAgent()
    
    # Create a simple execution plan
    plan = {
        "task_analysis": "Find information about Python and save it to a file",
        "environments_needed": ["browser", "file_system"],
        "execution_steps": [
            {
                "step_number": 1,
                "environment": "browser",
                "action": "search for Python programming language",
                "expected_outcome": "Get search results about Python"
            },
            {
                "step_number": 2,
                "environment": "browser",
                "action": "extract information about Python programming",
                "expected_outcome": "Extract key information about Python"
            },
            {
                "step_number": 3,
                "environment": "file_system",
                "action": "save extracted information as file python_info.txt",
                "expected_outcome": "Save the information to a file"
            }
        ]
    }
    
    # Execute the plan
    result = agent.execute_plan(plan)
    
    logger.info(f"Execution plan result: {json.dumps(result, indent=2)}")
    assert result["status"] == "completed"
    assert len(result["results"]) == 3
    assert os.path.exists("python_info.txt")
    
    # Clean up
    os.remove("python_info.txt")
    
    logger.info("Execution plan test passed!")

def main():
    """Run all tests"""
    try:
        test_browser_extraction()
        test_file_system_operations()
        test_execution_plan()
        
        logger.info("All tests passed!")
        return 0
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())