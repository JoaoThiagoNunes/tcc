from typing import Dict, Any
from app.domain.entities.document import Document


class ConsultaCNPJRules:
    async def validate(self, document: Document, extraction_payload: Dict[str, Any]) -> Dict[str, Any]:
        extracted_data = extraction_payload.get("extracted_data", {})
        violations = []
        checks = []

        cnpj = extracted_data.get("cnpj")
        checks.append("cnpj_presente")
        if not cnpj:
            violations.append("CNPJ é obrigatório")

        situacao = extracted_data.get("situacao_cadastral")
        checks.append("situacao_cadastral_presente")
        if not situacao:
            violations.append("Situação cadastral é obrigatória")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "checks": checks,
        }
