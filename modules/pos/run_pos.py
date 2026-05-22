#!/usr/bin/env python3
"""
Quick start launcher for AGAMART Application
"""
import subprocess
import sys
import os

def main():
    print("""
╔════════════════════════════════════════╗
║            AGAMART                     ║
║        Version 1.0.0                   ║
╚════════════════════════════════════════╝
    """)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        sys.exit(1)
    
    # Check for PyQt5
    try:
        import PyQt5
    except ImportError:
        print("Installing required packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    print("Lancement de AGAMART...")
    print()
    
    # Run main application
    subprocess.run([sys.executable, "main.py"])

if __name__ == '__main__':
    main()
