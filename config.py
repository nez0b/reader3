import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    # Convert string "true" (case-insensitive) to boolean
    LLM_DRY_RUN = os.getenv("LLM_DRY_RUN", "false").lower() == "true"

settings = Settings()
