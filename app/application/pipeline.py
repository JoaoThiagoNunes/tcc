from typing import Dict, Any
from app.domain.entities.document import Document, DocumentType
from app.domain.entities.analysis_result import AnalysisResult, AnalysisStatus
from app.domain.extraction.nota_fiscal_extractor import NotaFiscalFieldExtractor
from app.domain.extraction.comprovante_extractor import ComprovantePagamentoFieldExtractor
from app.domain.extraction.consulta_cnpj_extractor import ConsultaCNPJFieldExtractor
from app.domain.rules_engine.base_rules import RulesEngine


class AnalysisPipeline:
    def __init__(self):
        self.extractors = {
            DocumentType.NOTA_FISCAL: NotaFiscalFieldExtractor(),
            DocumentType.COMPROVANTE_PAGAMENTO: ComprovantePagamentoFieldExtractor(),
            DocumentType.CONSULTA_CNPJ: ConsultaCNPJFieldExtractor(),
        }
        self.rules_engine = RulesEngine()

    async def execute(self, document: Document) -> AnalysisResult:
        """
        1. Extrai campos do texto OCR conforme o tipo do documento
        2. Valida com regras de negócio
        """
        try:

            extractor = self.extractors.get(document.type)
            if not extractor:
                error_msg = f"Extrator não encontrado para tipo: {document.type}"
                return AnalysisResult(
                    document_id=document.id,
                    document_type=document.type.value if document.type else "unknown",
                    field_extraction=None,
                    rules_validation=None,
                    status=AnalysisStatus.FAILED,
                    errors=[error_msg],
                )

            extraction = await extractor.extract(document)
            rules_result = await self.rules_engine.apply_rules(document, extraction)

            return AnalysisResult(
                document_id=document.id,
                document_type=document.type.value if document.type else "unknown",
                field_extraction=extraction,
                rules_validation=rules_result,
                status=AnalysisStatus.COMPLETED,
            )

        except Exception as e:
            error_msg = str(e)
            return AnalysisResult(
                document_id=document.id,
                document_type=document.type.value if document.type else "unknown",
                field_extraction=None,
                rules_validation=None,
                status=AnalysisStatus.FAILED,
                errors=[error_msg],
            )
