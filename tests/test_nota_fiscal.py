"""
Testes para extrator de Nota Fiscal (texto OCR)
"""
import pytest
from app.domain.extraction.nota_fiscal_extractor import NotaFiscalFieldExtractor
from app.domain.entities.document import Document, DocumentType


@pytest.mark.asyncio
async def test_extract_nota_fiscal_fields():
    extractor = NotaFiscalFieldExtractor()
    document = Document(
        id="test-1",
        filename="nota_fiscal.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        type=DocumentType.NOTA_FISCAL,
        extracted_text=(
            "Nota Fiscal Eletrônica Nº 12345 "
            "Emitente CNPJ 12.345.678/0001-90 "
            "Data emissão 01/01/2025 "
            "Valor total R$ 150,00"
        ),
    )

    result = await extractor.extract(document)
    assert result is not None
    assert result["document_type"] == "nota_fiscal"
    assert result["extracted_data"]["numero"] == "12345"
    assert result["extracted_data"]["data_emissao"] == "01/01/2025"
    assert result["extracted_data"]["valor_total"] == 150.0
