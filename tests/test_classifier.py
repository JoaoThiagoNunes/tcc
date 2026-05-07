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
        extracted_text="DANFE Nota Fiscal eletronica com chave de acesso e valor total",
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
    assert result.confidence >= 0.75


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
