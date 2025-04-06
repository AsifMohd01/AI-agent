"""
Run script for the Autonomous AI Agent application.
This script checks for dependencies and starts the Flask server.
"""

import os
import sys
import subprocess
import webbrowser
from time import sleep

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import google.generativeai
        import dotenv
        import requests
        import bs4
        print("✅ All dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        install = input("Would you like to install missing dependencies? (y/n): ")
        if install.lower() == 'y':
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            return True
        return False

def check_api_key():
    """Check if the API key is set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables.")
        create_env = input("Would you like to create a .env file now? (y/n): ")
        if create_env.lower() == 'y':
            api_key = input("Enter your Google API key for Gemini 1.5 Flash: ")
            with open(".env", "w") as f:
                f.write(f"GOOGLE_API_KEY={api_key}")
            print("✅ .env file created successfully.")
            return True
        return False
    
    print("✅ API key found in environment variables.")
    return True

def start_server():
    """Start the Flask server"""
    print("🚀 Starting the Autonomous AI Agent server...")

    try:
        # Import the app and check API key validity
        from app import app, api_key_valid

        if not api_key_valid:
            print("\n" + "⚠️ " + "=" * 58 + " ⚠️")
            print("WARNING: API key is missing or invalid.")
            print("The application will run with limited functionality.")
            print("Please set up a valid API key for full functionality.")
            print("⚠️ " + "=" * 58 + " ⚠️" + "\n")
        else:
            print("\n✅ API key is valid. Full functionality is available.\n")

        # Open browser after a short delay
        def open_browser():
            sleep(2)  # Increased delay to ensure server is ready
            print("\n🌐 Opening browser at http://127.0.0.1:5000\n")
            webbrowser.open('http://127.0.0.1:5000')

        import threading
        threading.Thread(target=open_browser).start()

        print("\n" + "=" * 60)
        print("Server is starting... Press CTRL+C to stop the server.")
        print("=" * 60 + "\n")

        # Start Flask app
        app.run(debug=True)

    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")
        print("Please check the error message above and try again.")

if __name__ == "__main__":
    print("=" * 50)
    print("Autonomous AI Agent - Setup and Run")
    print("=" * 50)
    
    if check_dependencies() and check_api_key():
        start_server()
    else:
        print("❌ Setup incomplete. Please resolve the issues and try again.")