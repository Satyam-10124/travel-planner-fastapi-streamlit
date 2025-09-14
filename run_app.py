#!/usr/bin/env python3
"""
Travel Planner Application Runner
Starts both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def run_fastapi():
    """Run the FastAPI backend server"""
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])

def run_streamlit():
    """Run the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend on http://localhost:8502")
    time.sleep(3)  # Wait for FastAPI to start
    subprocess.run([
        sys.executable, "-m", "streamlit", 
        "run", 
        "streamlit_app.py",
        "--server.port", "8502",
        "--server.address", "0.0.0.0"
    ])

def main():
    """Main function to run both servers"""
    print("🧳 Travel Planner - Starting Application...")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Creating from template...")
        example_file = Path("env.example")
        if example_file.exists():
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ .env file created. Please update it with your API keys.")
        else:
            print("❌ env.example not found. Please create .env manually.")
    
    try:
        # Start FastAPI in a separate thread
        fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Start Streamlit in main thread
        run_streamlit()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()
