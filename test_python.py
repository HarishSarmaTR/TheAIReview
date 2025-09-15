#!/usr/bin/env python3
"""
Quick test to verify Python and packages work correctly
"""

print("🐍 Python Test - AI Review Tool v2.1.8")
print("=" * 50)

# Test basic Python
import sys
print(f"✅ Python Version: {sys.version}")
print(f"✅ Python Path: {sys.executable}")

# Test required packages
try:
    import customtkinter
    print("✅ CustomTkinter: OK")
except ImportError:
    print("❌ CustomTkinter: Missing")

try:
    import requests
    print("✅ Requests: OK")
except ImportError:
    print("❌ Requests: Missing")

try:
    import github
    print("✅ PyGithub: OK")
except ImportError:
    print("❌ PyGithub: Missing")

try:
    import pandas
    print("✅ Pandas: OK")
except ImportError:
    print("❌ Pandas: Missing")

try:
    import selenium
    print("✅ Selenium: OK")
except ImportError:
    print("❌ Selenium: Missing")

print("=" * 50)
print("🎉 If you see this, Python is working correctly!")

