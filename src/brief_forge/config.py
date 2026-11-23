from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

@dataclass
class Settings:
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    language: str = os.getenv("LANGUAGE", "Persian")
    max_articles: int = int(os.getenv("MAX_ARTICLES", "35"))
    news_count: int = int(os.getenv("NEWS_COUNT", os.getenv("MAX_NEWS", "10")))
    days_back: int = int(os.getenv("DAYS_BACK", "7"))
    output_dir: Path = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "output")
    feeds_file: Path = PROJECT_ROOT / "config" / "feeds.txt"

    def validate(self):
        if not self.llm_api_key or self.llm_api_key == "replace_me":
            raise ValueError("Set LLM_API_KEY in your .env file.")
        if self.news_count < 1:
            raise ValueError("NEWS_COUNT must be at least 1.")
        self.output_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
