"""
Testes para Pipeline de análise
"""
import pytest
from app.application.pipeline import AnalysisPipeline
from app.domain.entities.document import Document, DocumentType
from app.domain.entities.analysis_result import AnalysisStatus


def _build_document(document_type: DocumentType) -> Document:
    return Document(
        id="test-1",
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        type=document_type,
        extracted_text="Texto extraído...",
    )


@pytest.mark.asyncio
async def test_pipeline_execution_by_type_success():
    pipeline = AnalysisPipeline()
    document = _build_document(DocumentType.NOTA_FISCAL)

    class AnalyzerStub:
        async def analyze(self, doc: Document):
            return {
                "document_type": doc.type.value,
                "extracted_data": {"numero": "123"},
                "confidence": 0.9,
                "raw_response": {"ok": True},
            }

    pipeline.analyzers[DocumentType.NOTA_FISCAL] = AnalyzerStub()

    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.COMPLETED
    assert result.ai_analysis is not None
    assert result.ai_analysis["document_type"] == DocumentType.NOTA_FISCAL.value
    assert result.rules_validation is not None


@pytest.mark.asyncio
async def test_pipeline_returns_failed_when_analyzer_missing():
    pipeline = AnalysisPipeline()
    document = _build_document(DocumentType.UNKNOWN)

    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.FAILED
    assert result.errors
    assert "Analyzer não encontrado" in result.errors[0]


@pytest.mark.asyncio
async def test_pipeline_returns_failed_when_analyzer_raises():
    pipeline = AnalysisPipeline()
    document = _build_document(DocumentType.CONSULTA_CNPJ)

    class AnalyzerStub:
        async def analyze(self, doc: Document):
            raise RuntimeError("falha no analyzer")

    pipeline.analyzers[DocumentType.CONSULTA_CNPJ] = AnalyzerStub()
    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.FAILED
    assert "falha no analyzer" in result.errors[0]


@pytest.mark.asyncio
async def test_pipeline_returns_failed_when_rules_engine_raises():
    pipeline = AnalysisPipeline()
    document = _build_document(DocumentType.COMPROVANTE_PAGAMENTO)

    class AnalyzerStub:
        async def analyze(self, doc: Document):
            return {"document_type": doc.type.value, "extracted_data": {}, "confidence": 0.5}

    class RulesEngineStub:
        async def apply_rules(self, _document, _ai_result):
            raise RuntimeError("falha nas regras")

    pipeline.analyzers[DocumentType.COMPROVANTE_PAGAMENTO] = AnalyzerStub()
    pipeline.rules_engine = RulesEngineStub()
    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.FAILED
    assert "falha nas regras" in result.errors[0]
