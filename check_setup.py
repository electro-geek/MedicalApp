#!/usr/bin/env python3
"""
Diagnostic script to check if the setup is correct.
"""
import os
import sys
from pathlib import Path

# Import config loader
sys.path.insert(0, str(Path(__file__).parent))
from backend.config import get_config

print("=" * 60)
print("Medical Appointment Scheduler - Setup Check")
print("=" * 60)
print()

# Check config.properties file
config_file = Path("config.properties")
if config_file.exists():
    print("✅ config.properties file exists")
else:
    print("❌ config.properties file NOT found")
    print("   Create it with: cp config.properties.example config.properties")
    print()

# Load config
config = get_config()

# Check Gemini API Key
api_key = config.get("GEMINI_API_KEY")
if api_key and api_key != "your_gemini_api_key_here":
    print(f"✅ GEMINI_API_KEY is set (length: {len(api_key)})")
else:
    print("❌ GEMINI_API_KEY is NOT set or using placeholder")
    print("   Add your Gemini API key to config.properties file")
    print()

# Check data files
data_files = ["data/clinic_info.json", "data/doctor_schedule.json"]
for file_path in data_files:
    if Path(file_path).exists():
        print(f"✅ {file_path} exists")
    else:
        print(f"❌ {file_path} NOT found")

print()

# Check Python packages
try:
    import fastapi
    print("✅ fastapi installed")
except ImportError:
    print("❌ fastapi NOT installed - run: pip install -r requirements.txt")

try:
    import google.generativeai
    print("✅ google-generativeai installed")
except ImportError:
    print("❌ google-generativeai NOT installed - run: pip install -r requirements.txt")

try:
    import chromadb
    print("✅ chromadb installed")
except ImportError:
    print("❌ chromadb NOT installed - run: pip install -r requirements.txt")


print()

# Test Gemini connection (if key is set)
if api_key and api_key != "your_gemini_api_key_here":
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Gemini client can be created")
        print("   (Note: This doesn't test if the key is valid)")
    except Exception as e:
        print(f"❌ Error creating Gemini client: {str(e)}")
else:
    print("⚠️  Skipping Gemini test - API key not set")

print()
print("=" * 60)
print("Summary")
print("=" * 60)
print()
print("If you see ❌ errors above, fix them before running the app.")
print()
print("Common fixes:")
print("1. Create config.properties file: cp config.properties.example config.properties")
print("2. Add GEMINI_API_KEY to config.properties file")
print("3. Install dependencies: pip install -r requirements.txt")
print()

