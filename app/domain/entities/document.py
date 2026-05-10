from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    NOTA_FISCAL = "nota_fiscal"
    COMPROVANTE_PAGAMENTO = "comprovante_pagamento"
    CONSULTA_CNPJ = "consulta_cnpj"
    UNKNOWN = "unknown"


@dataclass
class Document:
    id: str
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    type: Optional[DocumentType] = None
    extracted_text: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            raise ValueError("Document ID é obrigatório")
        if not self.filename:
            raise ValueError("Filename é obrigatório")
