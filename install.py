"""
Installation script for the Autonomous AI Agent.
This script sets up the environment and installs dependencies.
"""

import os
import sys
import subprocess
import platform

def print_header():
    """Print the installation header"""
    print("=" * 60)
    print("Autonomous AI Agent - Installation")
    print("=" * 60)
    print("This script will set up the environment for the Autonomous AI Agent.")
    print("=" * 60)

def check_python_version():
    """Check if the Python version is compatible"""
    print("\n📋 Checking Python version...")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"❌ Python 3.8 or higher is required. You have Python {major}.{minor}.")
        return False
    
    print(f"✅ Python {major}.{minor} detected.")
    return True

def install_dependencies():
    """Install the required dependencies"""
    print("\n📋 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Set up the environment variables"""
    print("\n📋 Setting up environment variables...")
    
    if os.path.exists(".env"):
        print("ℹ️ .env file already exists.")
        update = input("Would you like to update it? (y/n): ")
        if update.lower() != 'y':
            print("✅ Using existing .env file.")
            return True
    
    api_key = input("Enter your Google API key for Gemini 1.5 Flash: ")
    
    try:
        with open(".env", "w") as f:
            f.write(f"GOOGLE_API_KEY={api_key}")
        print("✅ Environment variables set up successfully.")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_directories():
    """Create necessary directories if they don't exist"""
    print("\n📋 Creating necessary directories...")
    
    directories = ["static/css", "static/js", "templates"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created successfully.")
    return True

def verify_installation():
    """Verify that the installation was successful"""
    print("\n📋 Verifying installation...")
    
    # Check if all required files exist
    required_files = [
        "app.py",
        "requirements.txt",
        ".env",
        "static/css/style.css",
        "static/js/script.js",
        "templates/index.html"
    ]
    
    missing_files = [file for file in required_files if not os.path.exists(file)]
    
    if missing_files:
        print(f"❌ The following files are missing: {', '.join(missing_files)}")
        return False
    
    # Try importing required modules
    try:
        import flask
        import google.generativeai
        import dotenv
        import requests
        import bs4
    except ImportError as e:
        print(f"❌ Failed to import required module: {e.name}")
        return False
    
    print("✅ Installation verified successfully.")
    return True

def main():
    """Main installation function"""
    print_header()
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating directories", create_directories),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment variables", setup_environment),
        ("Verifying installation", verify_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔍 {step_name}...")
        if not step_func():
            print(f"\n❌ Installation failed at step: {step_name}")
            return
    
    print("\n" + "=" * 60)
    print("✅ Installation completed successfully!")
    print("=" * 60)
    print("\nTo run the application, use the following command:")
    print("python run.py")
    print("\nThe application will be available at http://127.0.0.1:5000")

if __name__ == "__main__":
    main()