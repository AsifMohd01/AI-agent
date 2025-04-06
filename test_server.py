"""
Test script to verify that the server is running correctly.
This script makes a request to the health endpoint and checks the response.
"""

import requests
import sys
import time
import subprocess
import threading
import webbrowser
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_api_key():
    """Check if the API key is set"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("The server will run with limited functionality.")
        return False
    return True

def start_server():
    """Start the server in a separate process"""
    print("Starting server...")
    server_process = subprocess.Popen([sys.executable, "app.py"], 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    return server_process

def check_server_health(max_attempts=10, delay=1):
    """Check if the server is healthy"""
    url = "http://127.0.0.1:5000/api/health"
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Server is running. Status: {data.get('status')}")
                print(f"✅ API key valid: {data.get('api_key_valid')}")
                print(f"✅ Model: {data.get('model')}")
                print(f"✅ Version: {data.get('version')}")
                return True
        except requests.exceptions.ConnectionError:
            print(f"Waiting for server to start (attempt {attempt + 1}/{max_attempts})...")
            time.sleep(delay)
    
    print("❌ Failed to connect to server after multiple attempts")
    return False

def test_basic_instruction():
    """Test a basic instruction"""
    url = "http://127.0.0.1:5000/api/process"
    instruction = "Create a text file named test_output.txt with content Hello, World!"
    
    try:
        response = requests.post(url, json={"instruction": instruction})
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "completed":
                print("✅ Basic instruction test passed")
                return True
            else:
                print(f"❌ Basic instruction test failed: {data.get('message')}")
                return False
        else:
            print(f"❌ Basic instruction test failed with status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to server for basic instruction test")
        return False

def open_browser():
    """Open the browser to the application"""
    print("Opening browser...")
    webbrowser.open("http://127.0.0.1:5000")

def main():
    """Main function"""
    print("=" * 60)
    print("Autonomous AI Agent - Server Test")
    print("=" * 60)
    
    # Check API key
    check_api_key()
    
    # Start server
    server_process = start_server()
    
    try:
        # Check server health
        if check_server_health():
            # Open browser
            open_browser()
            
            # Test basic instruction
            print("\nTesting basic instruction...")
            test_basic_instruction()
            
            print("\n" + "=" * 60)
            print("Server is running. Press Ctrl+C to stop.")
            print("=" * 60)
            
            # Keep the server running until user interrupts
            while True:
                time.sleep(1)
        else:
            print("Server health check failed. Stopping server.")
            server_process.terminate()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server_process.terminate()
        print("Server stopped.")

if __name__ == "__main__":
    main()