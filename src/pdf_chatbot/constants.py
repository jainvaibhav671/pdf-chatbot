from dotenv import load_dotenv
import os

load_dotenv()

PUBLIC_FOLDER = os.path.join(os.getcwd(), "public")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
LOGS=os.getenv("LOGS") == "True"

try:
    if not os.path.exists(PUBLIC_FOLDER):
        os.makedirs(PUBLIC_FOLDER)
except Exception as e:
    raise e

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
