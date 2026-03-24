"""
Base Rules Engine - Motor de regras de negócio
"""
from typing import Dict, Any
from app.domain.entities.document import Document, DocumentType
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RulesEngine:
    """Motor de regras de negócio"""
    
    async def apply_rules(self, document: Document, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica regras de negócio baseadas no tipo de documento
        """
        try:
            logger.info(f"Aplicando regras para documento: {document.id}")
            
            # Importar regras específicas baseadas no tipo
            if document.type == DocumentType.NOTA_FISCAL:
                from .nota_fiscal_rules import NotaFiscalRules
                rules = NotaFiscalRules()
            elif document.type == DocumentType.COMPROVANTE_PAGAMENTO:
                from .pagamento_rules import PagamentoRules
                rules = PagamentoRules()
            else:
                return {"valid": True, "violations": []}
            
            # Aplicar regras
            result = await rules.validate(document, ai_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao aplicar regras: {str(e)}")
            return {"valid": False, "violations": [str(e)]}
