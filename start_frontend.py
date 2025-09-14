#!/usr/bin/env python3
"""
Start only the Streamlit frontend
"""
import subprocess
import sys

def main():
    print("🎨 Starting Streamlit frontend on http://localhost:8502")
    subprocess.run([
        sys.executable, "-m", "streamlit", 
        "run", 
        "streamlit_app.py",
        "--server.port", "8502",
        "--server.address", "0.0.0.0"
    ])

if __name__ == "__main__":
    main()
