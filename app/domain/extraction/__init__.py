from app.domain.extraction.base import DocumentFieldExtractor
from app.domain.extraction.nota_fiscal_extractor import NotaFiscalFieldExtractor
from app.domain.extraction.comprovante_extractor import ComprovantePagamentoFieldExtractor
from app.domain.extraction.consulta_cnpj_extractor import ConsultaCNPJFieldExtractor

__all__ = [
    "DocumentFieldExtractor",
    "NotaFiscalFieldExtractor",
    "ComprovantePagamentoFieldExtractor",
    "ConsultaCNPJFieldExtractor",
]
