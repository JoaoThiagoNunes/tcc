from typing import Dict, Any
from app.domain.entities.document import Document

class PagamentoRules:
    async def validate(self, document: Document, extraction_payload: Dict[str, Any]) -> Dict[str, Any]:
        violations = []
        
        extracted_data = extraction_payload.get("extracted_data", {})
        
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
        # Remove caracteres não numéricos
        codigo = ''.join(filter(str.isdigit, codigo))
        return 44 <= len(codigo) <= 48
