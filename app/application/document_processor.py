from app.domain.classifier.document_classifier import DocumentClassifier
from app.domain.ocr.ocr_service import OCRService
from app.domain.entities.document import Document
from app.domain.entities.analysis_result import AnalysisResult, AnalysisStatus
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.ocr_service = OCRService()
    
    async def process(self, document: Document) -> AnalysisResult:
        try:
            logger.info(f"Processando documento: {document.id}")

            # Extrair texto via OCR
            text = await self.ocr_service.extract_text(document)
            document.extracted_text = text

            # Classificar documento com base em nome + texto extraído
            classification = await self.classifier.classify(document)
            document.type = classification.label

            # TODO: Executar pipeline de análise específica

            result = AnalysisResult(
                document_id=document.id,
                document_type=classification.label.value,
                status=AnalysisStatus.COMPLETED,
                metadata={
                    "classification_confidence": classification.confidence,
                    "classification_reason": classification.reason,
                    "classification_scores": {
                        doc_type.value: score for doc_type, score in classification.scores.items()
                    },
                },
            )

            return result

        except Exception as e:
            logger.error(f"Erro ao processar documento {document.id}: {str(e)}")
            raise
