"""
Nota Fiscal Rules - Regras de validação para notas fiscais
"""
from typing import Dict, Any, List
from app.domain.entities.document import Document
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class NotaFiscalRules:
    """Regras de validação para notas fiscais"""
    
    async def validate(self, document: Document, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida a nota fiscal conforme regras de negócio
        """
        violations = []
        
        # Validar campos obrigatórios
        extracted_data = ai_result.get("extracted_data", {})
        
        if not extracted_data.get("numero"):
            violations.append("Número da nota fiscal é obrigatório")
        
        if not extracted_data.get("data_emissao"):
            violations.append("Data de emissão é obrigatória")
        
        if not extracted_data.get("valor_total"):
            violations.append("Valor total é obrigatório")
        
        # Validar CNPJ do emitente
        emitente = extracted_data.get("emitente", {})
        cnpj = emitente.get("cnpj", "")
        if cnpj and not self._validate_cnpj(cnpj):
            violations.append("CNPJ do emitente inválido")
        
        # Validar valor total vs soma dos itens
        itens = extracted_data.get("itens", [])
        if itens:
            soma_itens = sum(item.get("valor_total", 0) for item in itens)
            valor_total = extracted_data.get("valor_total", 0)
            if abs(soma_itens - valor_total) > 0.01:
                violations.append("Valor total não confere com a soma dos itens")
        
        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
    
    def _validate_cnpj(self, cnpj: str) -> bool:
        """Valida formato básico de CNPJ"""
        # Remove caracteres não numéricos
        cnpj = ''.join(filter(str.isdigit, cnpj))
        return len(cnpj) == 14
