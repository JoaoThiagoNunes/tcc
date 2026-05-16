from abc import ABC, abstractmethod
from typing import Any, Dict

from app.domain.entities.document import Document


class DocumentFieldExtractor(ABC):
    """Extrai campos estruturados do texto OCR (sem modelos de IA)."""

    @abstractmethod
    async def extract(self, document: Document) -> Dict[str, Any]:
        """Retorna dict com chaves compatíveis com o motor de regras (`extracted_data`)."""
