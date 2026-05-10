"""
Testes para Rules Engine
"""
import pytest
from app.domain.rules_engine.nota_fiscal_rules import NotaFiscalRules
from app.domain.rules_engine.pagamento_rules import PagamentoRules
from app.domain.rules_engine.base_rules import RulesEngine
from app.domain.entities.document import Document, DocumentType


@pytest.mark.asyncio
async def test_nota_fiscal_rules_valid():
    """Testa validação de nota fiscal válida"""
    rules = NotaFiscalRules()
    document = Document(
        id="test-1",
        filename="nf.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    
    ai_result = {
        "extracted_data": {
            "numero": "123",
            "data_emissao": "2024-01-01",
            "valor_total": 100.0,
            "emitente": {"cnpj": "12345678000190"},
            "itens": [{"valor_total": 100.0}]
        }
    }
    
    result = await rules.validate(document, ai_result)
    assert result["valid"] is True
    assert len(result["violations"]) == 0


@pytest.mark.asyncio
async def test_pagamento_rules_valid():
    """Testa validação de comprovante válido"""
    rules = PagamentoRules()
    document = Document(
        id="test-2",
        filename="comprovante.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    
    ai_result = {
        "extracted_data": {
            "data": "2024-01-01",
            "valor": 50.0
        }
    }
    
    result = await rules.validate(document, ai_result)
    assert result["valid"] is True


@pytest.mark.asyncio
async def test_rules_engine_dispatch_consulta_cnpj():
    rules_engine = RulesEngine()
    document = Document(
        id="test-3",
        filename="consulta.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        type=DocumentType.CONSULTA_CNPJ,
    )
    ai_result = {
        "extracted_data": {
            "cnpj": "12345678000190",
            "situacao_cadastral": "ATIVA",
        }
    }

    result = await rules_engine.apply_rules(document, ai_result)
    assert result["valid"] is True
    assert "checks" in result


@pytest.mark.asyncio
async def test_rules_engine_default_for_unknown_type():
    rules_engine = RulesEngine()
    document = Document(
        id="test-4",
        filename="desconhecido.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        type=DocumentType.UNKNOWN,
    )

    result = await rules_engine.apply_rules(document, {"extracted_data": {}})
    assert result["valid"] is True
    assert result["violations"] == []
    assert result["checks"] == []
