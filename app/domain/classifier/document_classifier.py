from dataclasses import dataclass
import difflib
import re
import unicodedata
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
    AMBIGUITY_MARGIN = 0.20
    FUZZY_THRESHOLD = 0.86

    KEYWORDS: Dict[DocumentType, List[tuple[str, float]]] = {
        DocumentType.NOTA_FISCAL: [
            ("nota fiscal", 0.16),
            ("danfe", 0.20),
            ("chave de acesso", 0.22),
            ("valor total", 0.12),
        ],
        DocumentType.COMPROVANTE_PAGAMENTO: [
            ("comprovante", 0.18),
            ("pagamento", 0.16),
            ("transferencia", 0.14),
            ("pix", 0.16),
            ("valor pago", 0.14),
        ],
        DocumentType.CONSULTA_CNPJ: [
            ("cnpj", 0.10),
            ("receita federal", 0.22),
            ("situacao cadastral", 0.22),
            ("razao social", 0.12),
        ],
    }

    STRONG_SIGNALS: Dict[DocumentType, List[tuple[str, float]]] = {
        DocumentType.NOTA_FISCAL: [
            ("danfe", 0.28),
            ("chave de acesso", 0.35),
            ("natureza da operacao", 0.20),
            ("protocolo de autorizacao", 0.22),
            ("inscricao estadual", 0.18),
            ("ncm", 0.18),
            ("cfop", 0.18),
        ],
        DocumentType.COMPROVANTE_PAGAMENTO: [
            ("comprovante", 0.22),
            ("id transacao", 0.20),
            ("codigo de autenticacao", 0.20),
            ("pix", 0.20),
            ("valor pago", 0.18),
        ],
        DocumentType.CONSULTA_CNPJ: [
            ("situacao cadastral", 0.26),
            ("receita federal", 0.24),
            ("data de abertura", 0.18),
            ("nome empresarial", 0.18),
        ],
    }

    PATTERNS: Dict[DocumentType, List[tuple[str, float]]] = {
        DocumentType.NOTA_FISCAL: [(r"\b\d{44}\b", 0.40)],
        DocumentType.CONSULTA_CNPJ: [(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", 0.12)],
        DocumentType.COMPROVANTE_PAGAMENTO: [(r"\b(id transacao|codigo de autenticacao)\b", 0.20)],
    }

    NEGATIVE_RULES: Dict[DocumentType, List[tuple[str, float]]] = {
        DocumentType.CONSULTA_CNPJ: [
            ("danfe", 0.22),
            ("ncm", 0.14),
            ("cfop", 0.14),
            ("chave de acesso", 0.20),
        ],
        DocumentType.NOTA_FISCAL: [
            ("situacao cadastral", 0.20),
            ("data de abertura", 0.14),
        ],
        DocumentType.COMPROVANTE_PAGAMENTO: [
            ("situacao cadastral", 0.10),
            ("danfe", 0.10),
        ],
    }

    @staticmethod
    def _normalize_text(text: object) -> str:
        safe = text if isinstance(text, str) else ""
        lowered = safe.lower()
        no_accents = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode("ascii")
        collapsed = re.sub(r"\s+", " ", no_accents).strip()
        return collapsed

    @staticmethod
    def _extract_digits(text: str) -> str:
        return re.sub(r"\D", "", text)

    @staticmethod
    def _safe_score_add(score: float, delta: float) -> float:
        return max(0.0, min(1.0, score + delta))

    def _fuzzy_contains(self, text: str, term: str, threshold: float) -> bool:
        if not text or not term:
            return False
        if term in text:
            return True

        tokens = text.split()
        term_tokens = term.split()
        window = max(1, len(term_tokens))
        if len(tokens) < window:
            chunks = [" ".join(tokens)] if tokens else []
        else:
            chunks = [" ".join(tokens[idx : idx + window]) for idx in range(0, len(tokens) - window + 1)]

        for chunk in chunks:
            ratio = difflib.SequenceMatcher(None, chunk, term).ratio()
            if ratio >= threshold:
                return True
        return False

    def _score_filename(self, filename: str, doc_type: DocumentType) -> tuple[float, List[str]]:
        score = 0.0
        evidence: List[str] = []
        filename_normalized = self._normalize_text(filename).replace("_", " ").replace("-", " ")

        for keyword, weight in self.KEYWORDS.get(doc_type, []):
            normalized_keyword = self._normalize_text(keyword)
            if self._fuzzy_contains(filename_normalized, normalized_keyword, self.FUZZY_THRESHOLD):
                score = self._safe_score_add(score, weight * 0.35)
                evidence.append(f"filename:{keyword}")

        return score, evidence

    def _score_text(self, text: str, digits_text: str, doc_type: DocumentType) -> tuple[float, List[str]]:
        score = 0.0
        evidence: List[str] = []
        text_normalized = self._normalize_text(text)

        for keyword, weight in self.KEYWORDS.get(doc_type, []):
            normalized_keyword = self._normalize_text(keyword)
            if self._fuzzy_contains(text_normalized, normalized_keyword, self.FUZZY_THRESHOLD):
                score = self._safe_score_add(score, weight)
                evidence.append(f"text:{keyword}")

        for keyword, weight in self.STRONG_SIGNALS.get(doc_type, []):
            normalized_keyword = self._normalize_text(keyword)
            if self._fuzzy_contains(text_normalized, normalized_keyword, self.FUZZY_THRESHOLD):
                score = self._safe_score_add(score, weight)
                evidence.append(f"strong:{keyword}")

        for pattern, weight in self.PATTERNS.get(doc_type, []):
            try:
                if re.search(pattern, text_normalized):
                    score = self._safe_score_add(score, weight)
                    evidence.append(f"pattern:{pattern}")
            except re.error:
                evidence.append(f"pattern_error:{pattern}")

        # robust NF-e key check: detect 44 digits even with OCR separators/noise
        if doc_type == DocumentType.NOTA_FISCAL and len(digits_text) >= 44:
            if re.search(r"\d{44}", digits_text):
                score = self._safe_score_add(score, 0.40)
                evidence.append("digits:nfe44")

        # negative rules
        for token, penalty in self.NEGATIVE_RULES.get(doc_type, []):
            normalized_token = self._normalize_text(token)
            if self._fuzzy_contains(text_normalized, normalized_token, self.FUZZY_THRESHOLD):
                score = max(0.0, score - penalty)
                evidence.append(f"negative:{token}")

        return score, evidence

    def _has_minimum_evidence(self, evidence: List[str]) -> bool:
        strong_hits = sum(1 for item in evidence if item.startswith("strong:") or item == "digits:nfe44")
        medium_hits = sum(1 for item in evidence if item.startswith("text:") or item.startswith("pattern:"))
        return strong_hits >= 1 or medium_hits >= 2

    def _unknown_scores(self) -> Dict[DocumentType, float]:
        return {
            DocumentType.NOTA_FISCAL: 0.0,
            DocumentType.COMPROVANTE_PAGAMENTO: 0.0,
            DocumentType.CONSULTA_CNPJ: 0.0,
            DocumentType.UNKNOWN: 0.0,
        }

    @staticmethod
    def _clamp_score(value: float) -> float:
        return max(0.0, min(1.0, value))

    def _finalize_scores(self, scores: Dict[DocumentType, float]) -> Dict[DocumentType, float]:
        completed = self._unknown_scores()
        for key, value in scores.items():
            completed[key] = self._clamp_score(value)
        return completed

    async def classify(self, document: Document) -> ClassificationResult:
        try:
            filename = document.filename if isinstance(document.filename, str) else ""
            logger.info(f"Classificando documento: {filename}")

            text = document.extracted_text if isinstance(document.extracted_text, str) else ""
            digits_text = self._extract_digits(text)
            scores: Dict[DocumentType, float] = {}
            evidences: Dict[DocumentType, List[str]] = {}

            candidate_types = [
                DocumentType.NOTA_FISCAL,
                DocumentType.COMPROVANTE_PAGAMENTO,
                DocumentType.CONSULTA_CNPJ,
            ]

            for doc_type in candidate_types:
                filename_score, filename_evidence = self._score_filename(filename, doc_type)
                text_score, text_evidence = self._score_text(text, digits_text, doc_type)
                final_score = self._clamp_score(filename_score + text_score)
                scores[doc_type] = final_score
                evidences[doc_type] = filename_evidence + text_evidence

            scores = self._finalize_scores(scores)
            ranked = sorted(
                [(k, v) for k, v in scores.items() if k != DocumentType.UNKNOWN],
                key=lambda item: item[1],
                reverse=True,
            )

            if not ranked:
                return ClassificationResult(
                    label=DocumentType.UNKNOWN,
                    confidence=0.0,
                    reason="fallback=unknown; reason=empty_ranking",
                    scores=scores,
                )

            top_type, top_score = ranked[0]
            second_score = ranked[1][1] if len(ranked) > 1 else 0.0
            margin = top_score - second_score
            has_min_evidence = self._has_minimum_evidence(evidences.get(top_type, []))

            if (
                top_score < self.REVIEW_THRESHOLD
                or margin < self.AMBIGUITY_MARGIN
                or not has_min_evidence
            ):
                reason = (
                    f"fallback=unknown; top={top_score:.2f}; second={second_score:.2f}; "
                    f"margin={margin:.2f}; min_evidence={has_min_evidence}; "
                    f"thresholds review={self.REVIEW_THRESHOLD:.2f}, ambiguity={self.AMBIGUITY_MARGIN:.2f}"
                )
                return ClassificationResult(
                    label=DocumentType.UNKNOWN,
                    confidence=top_score,
                    reason=reason,
                    scores=scores,
                )

            if top_score < self.ACCEPT_THRESHOLD:
                reason = (
                    f"medium_confidence; top={top_score:.2f}; evidence={', '.join(evidences[top_type][:6]) or 'none'}"
                )
            else:
                reason = (
                    f"high_confidence; top={top_score:.2f}; evidence={', '.join(evidences[top_type][:6]) or 'none'}"
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
                reason=f"classifier_error:{type(e).__name__}",
                scores=self._unknown_scores(),
            )
