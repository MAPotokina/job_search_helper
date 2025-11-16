import os
from dotenv import load_dotenv
import logging

load_dotenv()

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.3
OPENAI_MAX_TOKENS = 1000
OPENAI_TIMEOUT = 30

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/jobs.db")

# Ограничения на длину текста
MAX_JOB_DESCRIPTION_LENGTH = 5000
MAX_RESUME_LENGTH = 5000

# Стоимость для расчёта в статистике
COST_PER_1K_TOKENS = 0.002

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

