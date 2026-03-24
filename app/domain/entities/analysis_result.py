"""
Analysis Result Entity - Resultado da análise
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Status da análise"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalysisResult:
    """Resultado da análise de documento"""
    document_id: str
    document_type: str
    status: AnalysisStatus
    ai_analysis: Optional[Dict[str, Any]] = None
    rules_validation: Optional[Dict[str, Any]] = None
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def is_valid(self) -> bool:
        """Verifica se a análise foi bem-sucedida"""
        return self.status == AnalysisStatus.COMPLETED and len(self.errors) == 0
