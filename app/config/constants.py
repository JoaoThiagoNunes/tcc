from enum import Enum

class DocumentType(str, Enum):
    NOTA_FISCAL = "nota_fiscal"
    COMPROVANTE_PAGAMENTO = "comprovante_pagamento"
    CONSULTA_CNPJ = "consulta_cnpj"
    UNKNOWN = "unknown"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff"
]

OCR_TIMEOUT = 60  # segundos
PRE_ANALYSIS_TIMEOUT = 120  # segundos (OCR + extração + regras)
