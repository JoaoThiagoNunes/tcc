from functools import lru_cache
from app.config.settings import Settings


@lru_cache()
def get_settings() -> Settings:
    """Retorna as configurações da aplicação"""
    return Settings()


def get_dependencies():
    """
    Retorna dependências comuns para os endpoints
    """
    return {
        "settings": get_settings()
    }
