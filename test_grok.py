"""
Grok to Gemini Migration Wrapper script.
This project has migrated to Google Gemini API.
Executing test_gemini.py logic...
"""
import sys
from test_gemini import test_gemini_api

if __name__ == "__main__":
    print("Notice: Project has migrated to Gemini API. Running test_gemini.py...\n")
    success = test_gemini_api()
    sys.exit(0 if success else 1)
