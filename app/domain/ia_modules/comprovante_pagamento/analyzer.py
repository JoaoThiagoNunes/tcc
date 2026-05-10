from typing import Dict, Any
from app.domain.entities.document import Document
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)
class ComprovantePagamentoAnalyzer:
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.schema = self._load_schema()
        self.prompt = self._load_prompt()
    
    def _load_schema(self) -> Dict[str, Any]:
        return {}
    
    def _load_prompt(self) -> str:
        try:
            with open("app/domain/ia_modules/comprovante_pagamento/prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning("Prompt file not found, using default")
            return "Analise o comprovante de pagamento e extraia as informações relevantes."
    
    async def analyze(self, document: Document) -> Dict[str, Any]:
        try:
            logger.info(f"Analisando comprovante de pagamento: {document.id}")

            if not document.extracted_text:
                raise ValueError("Documento sem texto extraído para análise")

            response = await self.openai_client.analyze(
                text=document.extracted_text,
                prompt=self.prompt,
                schema=self.schema,
            )

            return {
                "document_type": "comprovante_pagamento",
                "extracted_data": response.get("extracted_data", {}),
                "confidence": float(response.get("confidence", 0.0)),
                "raw_response": response.get("raw_response", response),
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar comprovante: {str(e)}")
            raise
