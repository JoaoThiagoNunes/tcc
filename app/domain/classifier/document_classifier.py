"""
Document Classifier - Classifica o tipo de documento
"""
from typing import Optional
from app.domain.entities.document import Document, DocumentType
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class DocumentClassifier:
    """Classificador de documentos"""
    
    async def classify(self, document: Document) -> DocumentType:
        """
        Classifica o tipo de documento baseado em:
        - Nome do arquivo
        - Conteúdo (se disponível)
        - Metadados
        """
        try:
            # TODO: Implementar lógica de classificação
            # Por enquanto, retorna UNKNOWN
            logger.info(f"Classificando documento: {document.filename}")
            
            # Lógica simples baseada em extensão/nome
            filename_lower = document.filename.lower()
            
            if "nota" in filename_lower or "nf" in filename_lower:
                return DocumentType.NOTA_FISCAL
            elif "comprovante" in filename_lower or "pagamento" in filename_lower:
                return DocumentType.COMPROVANTE_PAGAMENTO
            elif "cnpj" in filename_lower:
                return DocumentType.CONSULTA_CNPJ
            
            return DocumentType.UNKNOWN
            
        except Exception as e:
            logger.error(f"Erro ao classificar documento: {str(e)}")
            return DocumentType.UNKNOWN
