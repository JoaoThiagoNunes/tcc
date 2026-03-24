"""
Document Processor - Orquestra o processamento de documentos
"""
from typing import Optional
from app.domain.classifier.document_classifier import DocumentClassifier
from app.domain.ocr.ocr_service import OCRService
from app.domain.entities.document import Document
from app.domain.entities.analysis_result import AnalysisResult
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Processador principal de documentos"""
    
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.ocr_service = OCRService()
    
    async def process(self, document: Document) -> AnalysisResult:
        """
        Processa um documento completo:
        1. Classifica o tipo de documento
        2. Extrai texto via OCR
        3. Executa análise específica
        """
        try:
            logger.info(f"Processando documento: {document.id}")
            
            # Classificar documento
            doc_type = await self.classifier.classify(document)
            document.type = doc_type
            
            # Extrair texto via OCR
            text = await self.ocr_service.extract_text(document)
            document.extracted_text = text
            
            # TODO: Executar pipeline de análise específica
            
            result = AnalysisResult(
                document_id=document.id,
                document_type=doc_type,
                status="completed"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar documento {document.id}: {str(e)}")
            raise
