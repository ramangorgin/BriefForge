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
    image_api_key: str = os.getenv("IMAGE_API_KEY", "") or os.getenv("LLM_API_KEY", "")
    image_base_url: str = os.getenv("IMAGE_BASE_URL", "") or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    image_model: str = os.getenv("IMAGE_MODEL", "gpt-image-1")
    image_size: str = os.getenv("IMAGE_SIZE", "1536x1024")
    language: str = os.getenv("LANGUAGE", "Persian")
    presentation_title: str = os.getenv("PRESENTATION_TITLE", "Computer Science News Briefing")
    max_articles: int = int(os.getenv("MAX_ARTICLES", "35"))
    max_slides: int = int(os.getenv("MAX_SLIDES", "6"))
    days_back: int = int(os.getenv("DAYS_BACK", "7"))
    output_dir: Path = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "output")
    workspace_dir: Path = PROJECT_ROOT / os.getenv("WORKSPACE_DIR", "workspace")
    feeds_file: Path = PROJECT_ROOT / "config" / "feeds.txt"

    def validate(self):
        if not self.llm_api_key or self.llm_api_key == "replace_me":
            raise ValueError("Set LLM_API_KEY in your .env file.")
        if not self.image_api_key or self.image_api_key == "replace_me":
            raise ValueError("Set IMAGE_API_KEY in your .env file.")
        if self.max_slides < 3:
            raise ValueError("MAX_SLIDES must be at least 3.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
