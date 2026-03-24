"""
Pagamento Rules - Regras de validação para comprovantes de pagamento
"""
from typing import Dict, Any
from app.domain.entities.document import Document
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class PagamentoRules:
    """Regras de validação para comprovantes de pagamento"""
    
    async def validate(self, document: Document, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida o comprovante de pagamento conforme regras de negócio
        """
        violations = []
        
        extracted_data = ai_result.get("extracted_data", {})
        
        # Validar campos obrigatórios
        if not extracted_data.get("data"):
            violations.append("Data do pagamento é obrigatória")
        
        if not extracted_data.get("valor"):
            violations.append("Valor do pagamento é obrigatório")
        
        # Validar valor positivo
        valor = extracted_data.get("valor", 0)
        if valor <= 0:
            violations.append("Valor do pagamento deve ser positivo")
        
        # Validar código de barras (se presente)
        codigo_barras = extracted_data.get("codigo_barras", "")
        if codigo_barras and not self._validate_codigo_barras(codigo_barras):
            violations.append("Código de barras inválido")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    def _validate_codigo_barras(self, codigo: str) -> bool:
        """Valida formato básico de código de barras"""
        # Remove caracteres não numéricos
        codigo = ''.join(filter(str.isdigit, codigo))
        return 44 <= len(codigo) <= 48
