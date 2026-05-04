                                                                                                                                             
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  # Application Settings
  access_token_expire_minutes: int = 30
  database_url: str = "postgresql://postgres:helloworld123456@localhost:5432/tutorly_db"
  debug: bool = False

  # Chatbot Configuration
  chatbot_llm_provider: str = "gemini"
  google_api_key: str = ""
  chatbot_gemini_model: str = "gemini-2.5-flash"
  chatbot_openrouter_model: str = "google/gemini-2.5-flash"
  openrouter_api_url: str = "https://openrouter.ai/api/v1/chat/completions"

  # Email Configuration
  smtp_server: str = "smtp.gmail.com"
  smtp_port: int = 587
  email_address: str = ""
  email_password: str = ""
  sender_name: str = "TutoratUp"
  enable_email_debug: bool = False
  max_email_retries: int = 3

  # Security Configuration
  secret_key: str = "secret"
  algorithm: str = "HS256"

  # External Services
  telegram_bot_token: str = ""

  _backend_root = Path(__file__).resolve().parents[2]
  model_config = SettingsConfigDict(
    env_file=(str(_backend_root / ".env"), str(_backend_root / ".env.example")),
    case_sensitive=False,
  )


settings = Settings()