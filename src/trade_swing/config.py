from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration kept separate from Streamlit state."""

    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = "openai/gpt-oss-120b"
    cache_ttl_seconds: int = 900
    min_history_rows: int = 220


DEFAULT_CONFIG = AppConfig()
