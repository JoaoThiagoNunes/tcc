from abc import ABC, abstractmethod
from typing import Any, Dict
from app.domain.entities.document import Document

class DocumentFieldExtractor(ABC):
    @abstractmethod
    async def extract(self, document: Document) -> Dict[str, Any]:

