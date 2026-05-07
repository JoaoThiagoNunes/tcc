from dataclasses import dataclass
import re
from typing import Dict, List
from app.domain.entities.document import Document, DocumentType
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ClassificationResult:
    label: DocumentType
    confidence: float
    reason: str
    scores: Dict[DocumentType, float]


class DocumentClassifier:
    ACCEPT_THRESHOLD = 0.75
    REVIEW_THRESHOLD = 0.55
    AMBIGUITY_MARGIN = 0.15

    KEYWORDS: Dict[DocumentType, List[tuple[str, float]]] = {
        DocumentType.NOTA_FISCAL: [
            ("nota fiscal", 0.25),
            ("danfe", 0.30),
            ("chave de acesso", 0.25),
            ("valor total", 0.15),
        ],
        DocumentType.COMPROVANTE_PAGAMENTO: [
            ("comprovante", 0.30),
            ("pagamento", 0.25),
            ("transferencia", 0.20),
            ("pix", 0.20),
            ("valor pago", 0.20),
        ],
        DocumentType.CONSULTA_CNPJ: [
            ("cnpj", 0.30),
            ("receita federal", 0.25),
            ("situacao cadastral", 0.25),
            ("razao social", 0.15),
        ],
    }

    PATTERNS: Dict[DocumentType, List[tuple[str, float]]] = {
        DocumentType.NOTA_FISCAL: [(r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\b", 0.30)],
        DocumentType.CONSULTA_CNPJ: [(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", 0.25)],
        DocumentType.COMPROVANTE_PAGAMENTO: [(r"\b(id transacao|codigo de autenticacao)\b", 0.20)],
    }

    def _score_filename(self, filename: str, doc_type: DocumentType) -> tuple[float, List[str]]:
        score = 0.0
        evidence: List[str] = []
        filename_lower = filename.lower().replace("_", " ").replace("-", " ")

        for keyword, weight in self.KEYWORDS.get(doc_type, []):
            if keyword in filename_lower:
                score += weight * 0.45
                evidence.append(f"filename:{keyword}")

        return score, evidence

    def _score_text(self, text: str, doc_type: DocumentType) -> tuple[float, List[str]]:
        score = 0.0
        evidence: List[str] = []
        text_lower = text.lower()

        for keyword, weight in self.KEYWORDS.get(doc_type, []):
            if keyword in text_lower:
                score += weight
                evidence.append(f"text:{keyword}")

        for pattern, weight in self.PATTERNS.get(doc_type, []):
            if re.search(pattern, text_lower):
                score += weight
                evidence.append(f"pattern:{pattern}")

        return score, evidence

    @staticmethod
    def _clamp_score(value: float) -> float:
        return max(0.0, min(1.0, value))

    async def classify(self, document: Document) -> ClassificationResult:
        """
        Classifica o tipo de documento baseado em:
        - Nome do arquivo
        - Conteúdo (se disponível)
        - Metadados
        """
        try:
            logger.info(f"Classificando documento: {document.filename}")

            text = document.extracted_text or ""
            scores: Dict[DocumentType, float] = {}
            evidences: Dict[DocumentType, List[str]] = {}

            candidate_types = [
                DocumentType.NOTA_FISCAL,
                DocumentType.COMPROVANTE_PAGAMENTO,
                DocumentType.CONSULTA_CNPJ,
            ]

            for doc_type in candidate_types:
                filename_score, filename_evidence = self._score_filename(document.filename, doc_type)
                text_score, text_evidence = self._score_text(text, doc_type)
                final_score = self._clamp_score(filename_score + text_score)
                scores[doc_type] = final_score
                evidences[doc_type] = filename_evidence + text_evidence

            ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            top_type, top_score = ranked[0]
            second_score = ranked[1][1] if len(ranked) > 1 else 0.0
            margin = top_score - second_score

            if top_score < self.REVIEW_THRESHOLD or margin < self.AMBIGUITY_MARGIN:
                reason = (
                    f"fallback=unknown; top={top_score:.2f}; second={second_score:.2f}; "
                    f"margin={margin:.2f}; thresholds review={self.REVIEW_THRESHOLD:.2f}, ambiguity={self.AMBIGUITY_MARGIN:.2f}"
                )
                return ClassificationResult(
                    label=DocumentType.UNKNOWN,
                    confidence=top_score,
                    reason=reason,
                    scores=scores,
                )

            if top_score < self.ACCEPT_THRESHOLD:
                reason = (
                    f"medium_confidence; top={top_score:.2f}; evidence={', '.join(evidences[top_type][:4]) or 'none'}"
                )
            else:
                reason = (
                    f"high_confidence; top={top_score:.2f}; evidence={', '.join(evidences[top_type][:4]) or 'none'}"
                )

            return ClassificationResult(
                label=top_type,
                confidence=top_score,
                reason=reason,
                scores=scores,
            )

        except Exception as e:
            logger.error(f"Erro ao classificar documento: {str(e)}")
            return ClassificationResult(
                label=DocumentType.UNKNOWN,
                confidence=0.0,
                reason=f"classifier_error:{str(e)}",
                scores={DocumentType.UNKNOWN: 0.0},
            )
