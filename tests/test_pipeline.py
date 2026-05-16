"""
Testes para Pipeline de análise (extração + regras)
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

    class ExtractorStub:
        async def extract(self, doc: Document):
            return {
                "document_type": doc.type.value,
                "extracted_data": {"numero": "123"},
                "parser_confidence": 0.9,
            }

    pipeline.extractors[DocumentType.NOTA_FISCAL] = ExtractorStub()

    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.COMPLETED
    assert result.field_extraction is not None
    assert result.field_extraction["document_type"] == DocumentType.NOTA_FISCAL.value
    assert result.rules_validation is not None


@pytest.mark.asyncio
async def test_pipeline_returns_failed_when_extractor_missing():
    pipeline = AnalysisPipeline()
    document = _build_document(DocumentType.UNKNOWN)

    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.FAILED
    assert result.errors
    assert "Extrator não encontrado" in result.errors[0]


@pytest.mark.asyncio
async def test_pipeline_returns_failed_when_extractor_raises():
    pipeline = AnalysisPipeline()
    document = _build_document(DocumentType.CONSULTA_CNPJ)

    class ExtractorStub:
        async def extract(self, doc: Document):
            raise RuntimeError("falha no extrator")

    pipeline.extractors[DocumentType.CONSULTA_CNPJ] = ExtractorStub()
    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.FAILED
    assert "falha no extrator" in result.errors[0]


@pytest.mark.asyncio
async def test_pipeline_returns_failed_when_rules_engine_raises():
    pipeline = AnalysisPipeline()
    document = _build_document(DocumentType.COMPROVANTE_PAGAMENTO)

    class ExtractorStub:
        async def extract(self, doc: Document):
            return {"document_type": doc.type.value, "extracted_data": {}, "parser_confidence": 0.5}

    class RulesEngineStub:
        async def apply_rules(self, _document, _extraction_payload):
            raise RuntimeError("falha nas regras")

    pipeline.extractors[DocumentType.COMPROVANTE_PAGAMENTO] = ExtractorStub()
    pipeline.rules_engine = RulesEngineStub()
    result = await pipeline.execute(document)
    assert result.status == AnalysisStatus.FAILED
    assert "falha nas regras" in result.errors[0]
