from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = (
        "Pré-análise de documentos de Prestação de Contas via OCR e motor de regras"
    )
    app_version: str = "1.0.0"
    debug: bool = False

    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: list = [".pdf", ".png", ".jpg", ".jpeg", ".tiff"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
