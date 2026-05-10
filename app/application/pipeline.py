from typing import Dict, Any
from app.domain.entities.document import Document, DocumentType
from app.domain.entities.analysis_result import AnalysisResult, AnalysisStatus
from app.domain.ia_modules.nota_fiscal.analyzer import NotaFiscalAnalyzer
from app.domain.ia_modules.comprovante_pagamento.analyzer import ComprovantePagamentoAnalyzer
from app.domain.ia_modules.consulta_cnpj.analyzer import ConsultaCNPJAnalyzer
from app.domain.rules_engine.base_rules import RulesEngine
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)
class AnalysisPipeline:
    def __init__(self):
        self.analyzers = {
            DocumentType.NOTA_FISCAL: NotaFiscalAnalyzer(),
            DocumentType.COMPROVANTE_PAGAMENTO: ComprovantePagamentoAnalyzer(),
            DocumentType.CONSULTA_CNPJ: ConsultaCNPJAnalyzer()
        }
        self.rules_engine = RulesEngine()
    
    async def execute(self, document: Document) -> AnalysisResult:
        """
        Executa o pipeline completo:
        1. Análise com IA específica do tipo de documento
        2. Validação com regras de negócio
        3. Geração do resultado final
        """
        try:
            logger.info(f"Executando pipeline para documento: {document.id}")

            analyzer = self.analyzers.get(document.type)
            if not analyzer:
                error_msg = f"Analyzer não encontrado para tipo: {document.type}"
                logger.error(error_msg)
                return AnalysisResult(
                    document_id=document.id,
                    document_type=document.type.value if document.type else "unknown",
                    ai_analysis=None,
                    rules_validation=None,
                    status=AnalysisStatus.FAILED,
                    errors=[error_msg],
                )

            ai_result = await analyzer.analyze(document)
            rules_result = await self.rules_engine.apply_rules(document, ai_result)

            result = AnalysisResult(
                document_id=document.id,
                document_type=document.type.value if document.type else "unknown",
                ai_analysis=ai_result,
                rules_validation=rules_result,
                status=AnalysisStatus.COMPLETED
            )

            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Erro no pipeline para documento {document.id}: {error_msg}")
            return AnalysisResult(
                document_id=document.id,
                document_type=document.type.value if document.type else "unknown",
                ai_analysis=None,
                rules_validation=None,
                status=AnalysisStatus.FAILED,
                errors=[error_msg],
            )
