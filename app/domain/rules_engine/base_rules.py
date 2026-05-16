from typing import Dict, Any
from app.domain.entities.document import Document, DocumentType

class RulesEngine:
    def _default_result(self) -> Dict[str, Any]:
        return {"valid": True, "violations": [], "checks": []}

    async def apply_rules(self, document: Document, extraction_payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
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
                return self._default_result()

            result = await rules.validate(document, extraction_payload)
            return {
                "valid": bool(result.get("valid", False)),
                "violations": list(result.get("violations", [])),
                "checks": list(result.get("checks", [])),
            }

        except Exception as e:
            return {"valid": False, "violations": [str(e)], "checks": []}
