import os
import sys
from dotenv import load_dotenv

# Try importing Google GenAI SDK
try:
    from google import genai
    from google.genai.errors import APIError
except ImportError:
    print("ERROR: 'google-genai' package is not installed. Please run: pip install google-genai")
    sys.exit(1)

try:
    import dotenv
except ImportError:
    print("ERROR: 'python-dotenv' package is not installed. Please run: pip install python-dotenv")
    sys.exit(1)


def mask_key(key: str) -> str:
    """Safely mask API key for output without exposing secrets."""
    if not key:
        return "NO"
    if len(key) <= 8:
        return "****"
    return f"{key[:6]}...****"


def test_gemini_api():
    print("====================================")
    print("GEMINI API TEST")
    print("====================================")

    # 1. Check .env file existence
    env_path = ".env"
    if not os.path.exists(env_path):
        if os.path.exists("useless_project/.env"):
            env_path = "useless_project/.env"
        else:
            print("ERROR: .env file was not found.")
            print("====================================")
            print("FAILED")
            print("====================================")
            return False

    print(f"Detected .env file: YES ({env_path})")

    # 2. Load environment variables
    load_dotenv(dotenv_path=env_path)

    # 3. Retrieve and validate API key
    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("API_KEY")
    )

    if not api_key:
        print("ERROR: GEMINI_API_KEY (or GOOGLE_API_KEY / API_KEY) is missing from .env.")
        print("====================================")
        print("FAILED")
        print("====================================")
        return False

    api_key = api_key.strip()
    if not api_key:
        print("ERROR: API key is empty in .env.")
        print("====================================")
        print("FAILED")
        print("====================================")
        return False

    print(f"API key detected: YES ({mask_key(api_key)})")

    # 4. Initialize Gemini client
    print("Connecting to Gemini API...")
    candidate_models = ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-1.5-flash"]
    client = genai.Client(api_key=api_key)
    prompt_text = "Reply with exactly: GEMINI API IS WORKING"

    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
            )
            output_text = response.text.strip() if response.text else ""

            print("Request successful!")
            print(f"Model used: {model_name}")
            print("\nResponse:")
            print(output_text)
            print("\n====================================")
            print("SUCCESS")
            print("====================================")
            return True
        except APIError as e:
            if "503" in str(e) or "404" in str(e) or "UNAVAILABLE" in str(e) or "NOT_FOUND" in str(e):
                print(f"Model '{model_name}' temporary issue/not found, trying fallback...")
                continue
            print("\n====================================")
            print("GEMINI API ERROR")
            print("====================================")
            print(f"ERROR: {str(e)}")
            print("====================================")
            print("FAILED")
            print("====================================")
            return False
        except Exception as e:
            print("\n====================================")
            print("UNEXPECTED ERROR")
            print("====================================")
            print(f"ERROR: {str(e)}")
            print("====================================")
            print("FAILED")
            print("====================================")
            return False

    print("====================================")
    print("FAILED: All candidate models were unavailable.")
    print("====================================")
    return False


if __name__ == "__main__":
    success = test_gemini_api()
    sys.exit(0 if success else 1)
