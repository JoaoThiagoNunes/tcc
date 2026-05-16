import re
from typing import Any, Dict
from app.domain.entities.document import Document
from app.domain.extraction.base import DocumentFieldExtractor
from app.domain.extraction import text_utils

_NF_NUMERO = re.compile(
    r"(?:Número\s*(?:da\s*)?(?:NF|nota)?\s*:?\s*|N[º°]\s*|NF\s*-?\s*(?:e|E)?\s+n[º°]\s*)(\d{4,})",
    re.IGNORECASE,
)

class NotaFiscalFieldExtractor(DocumentFieldExtractor):
    async def extract(self, document: Document) -> Dict[str, Any]:
        text = document.extracted_text or ""

        numero_m = _NF_NUMERO.search(text)
        numero = numero_m.group(1) if numero_m else None

        dates = text_utils.find_dates(text)
        valores = text_utils.find_money_values(text)
        cnpjs = text_utils.find_cnpjs(text)

        valor_total = max(valores) if valores else None
        emitente_cnpj = cnpjs[0] if cnpjs else None

        extracted_data: Dict[str, Any] = {
            "numero": numero,
            "data_emissao": dates[0] if dates else None,
            "valor_total": valor_total,
            "emitente": {"cnpj": emitente_cnpj} if emitente_cnpj else {},
            "itens": [{"valor_total": valor_total}] if valor_total is not None else [],
        }

        filled = sum(
            1 for v in (numero, dates[0] if dates else None, valor_total) if v is not None
        )
        parser_confidence = filled / 3.0

        return {
            "document_type": "nota_fiscal",
            "extracted_data": extracted_data,
            "parser_confidence": parser_confidence,
        }
