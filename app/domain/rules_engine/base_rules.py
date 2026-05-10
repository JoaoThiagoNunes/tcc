"""
Base Rules Engine - Motor de regras de negócio
"""
from typing import Dict, Any
from app.domain.entities.document import Document, DocumentType
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class RulesEngine:
    """Motor de regras de negócio"""

    def _default_result(self) -> Dict[str, Any]:
        return {"valid": True, "violations": [], "checks": []}

    async def apply_rules(self, document: Document, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aplica regras de negócio baseadas no tipo de documento
        """
        try:
            logger.info(f"Aplicando regras para documento: {document.id}")

            if document.type == DocumentType.NOTA_FISCAL:
                from .nota_fiscal_rules import NotaFiscalRules
                rules = NotaFiscalRules()
            elif document.type == DocumentType.COMPROVANTE_PAGAMENTO:
                from .pagamento_rules import PagamentoRules
                rules = PagamentoRules()
            elif document.type == DocumentType.CONSULTA_CNPJ:
                from .consulta_cnpj_rules import ConsultaCNPJRules
                rules = ConsultaCNPJRules()
            else:
                logger.info("Tipo sem regra específica, aplicando validação neutra")
                return self._default_result()

            result = await rules.validate(document, ai_result)
            return {
                "valid": bool(result.get("valid", False)),
                "violations": list(result.get("violations", [])),
                "checks": list(result.get("checks", [])),
            }

        except Exception as e:
            logger.error(f"Erro ao aplicar regras: {str(e)}")
            return {"valid": False, "violations": [str(e)], "checks": []}
