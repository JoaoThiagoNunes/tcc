"""
Testes para Document Classifier
"""
import pytest
from app.domain.classifier.document_classifier import DocumentClassifier
from app.domain.entities.document import Document, DocumentType


@pytest.mark.asyncio
async def test_classify_nota_fiscal():
    """Testa classificação de nota fiscal"""
    classifier = DocumentClassifier()
    document = Document(
        id="test-1",
        filename="nota_fiscal_123.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        extracted_text=(
            "DANFE Nota Fiscal eletronica chave de acesso 35191234567890123456789012345678901234567890 "
            "natureza da operacao CFOP 5102 NCM 22030000"
        ),
    )
    
    result = await classifier.classify(document)
    assert result.label == DocumentType.NOTA_FISCAL
    assert result.confidence >= 0.75


@pytest.mark.asyncio
async def test_classify_comprovante():
    """Testa classificação de comprovante"""
    classifier = DocumentClassifier()
    document = Document(
        id="test-2",
        filename="comprovante_pagamento.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        extracted_text="Comprovante de pagamento pix com valor pago",
    )
    
    result = await classifier.classify(document)
    assert result.label == DocumentType.COMPROVANTE_PAGAMENTO
    assert result.confidence >= 0.55


@pytest.mark.asyncio
async def test_classify_consulta_cnpj():
    """Testa classificação de consulta CNPJ"""
    classifier = DocumentClassifier()
    document = Document(
        id="test-4",
        filename="consulta_cnpj.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        extracted_text="Comprovante de inscricao e de situacao cadastral receita federal data de abertura nome empresarial cnpj 12.345.678/0001-90",
    )

    result = await classifier.classify(document)
    assert result.label == DocumentType.CONSULTA_CNPJ
    assert result.confidence >= 0.55


@pytest.mark.asyncio
async def test_classify_unknown_ambiguous():
    """Retorna UNKNOWN quando evidências são ambíguas"""
    classifier = DocumentClassifier()
    document = Document(
        id="test-3",
        filename="documento.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        extracted_text="documento geral sem padrao identificavel",
    )

    result = await classifier.classify(document)
    assert result.label == DocumentType.UNKNOWN
    assert 0.0 <= result.confidence <= 1.0
    assert result.reason
    assert DocumentType.NOTA_FISCAL in result.scores
    assert DocumentType.COMPROVANTE_PAGAMENTO in result.scores
    assert DocumentType.CONSULTA_CNPJ in result.scores


@pytest.mark.asyncio
async def test_classify_ocr_ruim_depende_filename():
    """Quando OCR vem vazio, usa sinais do nome com baixa/média confiança"""
    classifier = DocumentClassifier()
    document = Document(
        id="test-5",
        filename="danfe_nota_fiscal_arquivo.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        extracted_text="",
    )

    result = await classifier.classify(document)
    assert 0.0 <= result.confidence <= 1.0
    assert result.reason


@pytest.mark.asyncio
async def test_classify_internal_error_returns_unknown():
    """Falha interna deve retornar UNKNOWN sem explodir exceção"""
    classifier = DocumentClassifier()
    document = Document(
        id="test-6",
        filename="nota.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        extracted_text="nota fiscal danfe",
    )

    original = classifier._score_text
    try:
        def _boom(*args, **kwargs):  # type: ignore
            raise RuntimeError("forced")

        classifier._score_text = _boom  # type: ignore[assignment]
        result = await classifier.classify(document)
        assert result.label == DocumentType.UNKNOWN
        assert result.reason.startswith("classifier_error:")
    finally:
        classifier._score_text = original  # type: ignore[assignment]
