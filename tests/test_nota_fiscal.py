"""
Testes para análise de Nota Fiscal
"""
import pytest
from app.domain.ia_modules.nota_fiscal.analyzer import NotaFiscalAnalyzer
from app.domain.entities.document import Document, DocumentType


@pytest.mark.asyncio
async def test_analyze_nota_fiscal():
    """Testa análise de nota fiscal"""
    analyzer = NotaFiscalAnalyzer()
    document = Document(
        id="test-1",
        filename="nota_fiscal.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        type=DocumentType.NOTA_FISCAL,
        extracted_text="Nota Fiscal Eletrônica..."
    )
    
    result = await analyzer.analyze(document)
    assert result is not None
    assert "document_type" in result
    assert result["document_type"] == "nota_fiscal"
