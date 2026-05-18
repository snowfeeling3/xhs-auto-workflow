import os
from pathlib import Path

from dotenv import load_dotenv

# 从项目根目录加载 .env
BASE_DIR = Path(__file__).parent.parent
env_file = BASE_DIR / ".env"
load_dotenv(env_file if env_file.exists() else BASE_DIR / ".env.example")

# LLM 配置
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v4-pro")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# 数据库：生产用 PostgreSQL，开发用 SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./xhs.db")

# Redis（生产环境启用）
REDIS_URL = os.getenv("REDIS_URL", "")

# 业务配置
NEW_USER_CREDITS = int(os.getenv("NEW_USER_CREDITS", "1"))  # 新用户初始免费积分（设为0则不送）
PAYMENT_QR_URL = os.getenv("PAYMENT_QR_URL", "")  # 收款二维码图片路径或URL
PAYMENT_AUTO_VERIFY = os.getenv("PAYMENT_AUTO_VERIFY", "false").lower() == "true"
ADMIN_KEY = os.getenv("ADMIN_KEY", "admin123")  # 管理员验证密钥

# 路径
APP_DIR = Path(__file__).parent
STATIC_DIR = APP_DIR / "static"
TEMPLATE_DIR = APP_DIR / "templates"
PROMPT_DIR = APP_DIR / "prompts"
