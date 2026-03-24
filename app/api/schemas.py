from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
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


class AnalysisResponse(BaseModel):
    status: AnalysisStatus
    document_id: str
    document_type: Optional[DocumentType] = None
    analysis_result: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    created_at: datetime = datetime.now()


class ProcessRequest(BaseModel):
    """Requisição de processamento"""
    document_id: str
    metadata: Optional[Dict[str, Any]] = None
