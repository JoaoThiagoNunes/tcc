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
        mime_type="application/pdf"
    )
    
    result = await classifier.classify(document)
    assert result == DocumentType.NOTA_FISCAL


@pytest.mark.asyncio
async def test_classify_comprovante():
    """Testa classificação de comprovante"""
    classifier = DocumentClassifier()
    document = Document(
        id="test-2",
        filename="comprovante_pagamento.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    
    result = await classifier.classify(document)
    assert result == DocumentType.COMPROVANTE_PAGAMENTO
