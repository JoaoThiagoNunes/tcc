import re
from typing import Any, Dict
from app.domain.entities.document import Document
from app.domain.extraction.base import DocumentFieldExtractor
from app.domain.extraction import text_utils

_SITUACAO = re.compile(
    r"situac(?:ao|ão)\s+cadastral\s*:?\s*([A-Za-zÀ-ú\s]+)",
    re.IGNORECASE,
)

class ConsultaCNPJFieldExtractor(DocumentFieldExtractor):
    async def extract(self, document: Document) -> Dict[str, Any]:
        text = document.extracted_text or ""

        cnpjs = text_utils.find_cnpjs(text)
        cnpj_norm = text_utils.normalize_cnpj_digits(cnpjs[0]) if cnpjs else None

        situacao_m = _SITUACAO.search(text)
        situacao = situacao_m.group(1).strip() if situacao_m else None
        if situacao is None:
            for hint in ("ATIVA", "BAIXADA", "INAPTA", "SUSPENSA"):
                if re.search(rf"\b{hint}\b", text, re.IGNORECASE):
                    situacao = hint
                    break

        extracted_data: Dict[str, Any] = {
            "cnpj": cnpj_norm,
            "situacao_cadastral": situacao,
        }

        filled = sum(1 for v in (cnpj_norm, situacao) if v)
        parser_confidence = filled / 2.0

        return {
            "document_type": "consulta_cnpj",
            "extracted_data": extracted_data,
            "parser_confidence": parser_confidence,
        }
