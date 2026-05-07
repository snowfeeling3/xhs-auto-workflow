import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v4-pro")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./xhs.db")

FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "3"))

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")
