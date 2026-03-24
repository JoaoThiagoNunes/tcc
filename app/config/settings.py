from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    app_name: str = "Pre Analysis Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    
    # Database Settings
    database_url: Optional[str] = "sqlite:///./pre_analysis.db"
    
    # Logging Settings
    log_level: str = "INFO"
    log_dir: str = "logs"
    
    # File Upload Settings
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
