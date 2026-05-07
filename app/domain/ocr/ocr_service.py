import importlib
import io
from pathlib import Path

import pytesseract
from PIL import Image

from app.domain.entities.document import Document
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


class OCRService:
    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        pypdf_spec = importlib.util.find_spec("pypdf")
        pypdf2_spec = importlib.util.find_spec("PyPDF2")
        if pypdf_spec is None and pypdf2_spec is None:
            return ""

        if pypdf_spec is not None:
            from pypdf import PdfReader  # type: ignore
        else:
            from PyPDF2 import PdfReader  # type: ignore

        reader = PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = [(page.extract_text() or "") for page in reader.pages]
        return "\n".join(extracted_pages).strip()

    def _ocr_pdf_with_pymupdf(self, pdf_bytes: bytes, lang: str = "por") -> str:
        pymupdf_spec = importlib.util.find_spec("fitz")
        if pymupdf_spec is None:
            return ""

        import fitz  # type: ignore

        text = ""
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                text += pytesseract.image_to_string(img, lang=lang)
        return text.strip()

    def _ocr_image_file(self, file_path: str, lang: str = "por") -> str:
        with Image.open(file_path) as image:
            rgb_image = image.convert("RGB")
            return pytesseract.image_to_string(rgb_image, lang=lang).strip()

    async def extract_text(self, document: Document) -> str:
        """
        Extrai texto do documento usando OCR
        """
        try:
            logger.info(f"Extraindo texto do documento: {document.id}")

            file_path = Path(document.file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {document.file_path}")

            if document.mime_type == "application/pdf":
                pdf_bytes = file_path.read_bytes()
                text = self._extract_text_from_pdf(pdf_bytes)
                if not text:
                    text = self._ocr_pdf_with_pymupdf(pdf_bytes, lang="por")
                return text

            return self._ocr_image_file(document.file_path, lang="por")

        except Exception as e:
            logger.error(f"Erro ao extrair texto: {str(e)}")
            raise
