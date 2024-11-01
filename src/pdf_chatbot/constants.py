from dotenv import load_dotenv
import os

load_dotenv()

PUBLIC_FOLDER = os.path.join(os.getcwd(), "public")
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
LOGS=os.getenv("LOGS") == "True"
SYSTEM_PROMPT = """
    You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer
    the question. If you don't know the answer, say that you
    don't know. Use three sentences maximum and keep the
    answer concise.

    {context}"""

try:
    if not os.path.exists(PUBLIC_FOLDER):
        os.makedirs(PUBLIC_FOLDER)
except Exception as e:
    raise e

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")
