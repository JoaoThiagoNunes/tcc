from typing import Any, Dict

from app.domain.entities.document import Document
from app.domain.extraction.base import DocumentFieldExtractor
from app.domain.extraction import text_utils
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class ComprovantePagamentoFieldExtractor(DocumentFieldExtractor):
    async def extract(self, document: Document) -> Dict[str, Any]:
        text = document.extracted_text or ""
        logger.info("Extraindo campos de comprovante a partir do OCR")

        dates = text_utils.find_dates(text)
        valores = text_utils.find_money_values(text)
        codigo = text_utils.find_codigo_barras_candidate(text)

        valor = max(valores) if valores else None

        extracted_data: Dict[str, Any] = {
            "data": dates[0] if dates else None,
            "valor": valor,
            "codigo_barras": codigo or "",
        }

        filled = sum(1 for v in (extracted_data["data"], valor) if v is not None)
        parser_confidence = filled / 2.0

        return {
            "document_type": "comprovante_pagamento",
            "extracted_data": extracted_data,
            "parser_confidence": parser_confidence,
        }
