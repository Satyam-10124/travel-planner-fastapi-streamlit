#!/usr/bin/env python3
"""
Start only the FastAPI backend server
"""
import subprocess
import sys

def main():
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--reload", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ])

if __name__ == "__main__":
    main()
