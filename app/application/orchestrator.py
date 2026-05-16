from app.domain.classifier.document_classifier import DocumentClassifier
from app.domain.ocr.ocr_service import OCRService
from app.domain.entities.document import Document, DocumentType
from app.domain.entities.analysis_result import AnalysisResult, AnalysisStatus
from app.application.pipeline import AnalysisPipeline


class PreAnalysisOrchestrator:
    def __init__(self):
        self.classifier = DocumentClassifier()
        self.ocr_service = OCRService()
        self.pipeline = AnalysisPipeline()

    async def run(self, document: Document) -> AnalysisResult:
        try:
            text = await self.ocr_service.extract_text(document)
            document.extracted_text = text

            classification = await self.classifier.classify(document)
            document.type = classification.label
            
            classification_meta = {
                "classification_confidence": classification.confidence,
                "classification_reason": classification.reason,
                "classification_scores": {
                    doc_type.value: score for doc_type, score in classification.scores.items()
                },
            }

            if document.type == DocumentType.UNKNOWN:
                return AnalysisResult(
                    document_id=document.id,
                    document_type=document.type.value,
                    status=AnalysisStatus.COMPLETED,
                    field_extraction=None,
                    rules_validation={"valid": True, "violations": [], "checks": []},
                    metadata=classification_meta,
                    warnings=[
                        "Tipo de documento não reconhecido; regras específicas não foram aplicadas."
                    ],
                )

            result = await self.pipeline.execute(document)
            merged_meta = {**classification_meta, **(result.metadata or {})}
            return AnalysisResult(
                document_id=result.document_id,
                document_type=result.document_type,
                status=result.status,
                field_extraction=result.field_extraction,
                rules_validation=result.rules_validation,
                errors=result.errors,
                warnings=result.warnings,
                metadata=merged_meta,
            )

        except Exception as e:
            dtype = document.type.value if document.type else "unknown"
            return AnalysisResult(
                document_id=document.id,
                document_type=dtype,
                status=AnalysisStatus.FAILED,
                errors=[str(e)],
            )
