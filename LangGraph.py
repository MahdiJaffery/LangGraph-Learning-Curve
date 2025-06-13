import os
from dotenv import load_dotenv, find_dotenv

try:
    envPath = find_dotenv()

    if not envPath:
        raise ModuleNotFoundError(".env FILE NOT FOUND")
    if not load_dotenv(envPath):
        raise EnvironmentError("FAILED TO LOAD .env")
    
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    openai_model = os.environ.get("OPENAI_MODEL")

    if not openai_api_key:
        raise ValueError("API NOT FOUND")
    if not openai_model:
        raise ValueError("MODEL NOT FOUND")
except Exception as e:
    print(f"ERROR: {e}")
    openai_api_key, openai_model = None, None
