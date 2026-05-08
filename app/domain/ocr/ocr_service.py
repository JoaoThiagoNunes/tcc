import importlib
import io
import re
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

import pytesseract
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageSequence, ImageStat

from app.domain.entities.document import Document
from app.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class OCRQualityProfile:
    width: int
    height: int
    area: int
    contrast_stddev: float
    noise_score: float
    low_resolution: bool
    low_contrast: bool
    high_noise: bool
    likely_skewed: bool


@dataclass
class OCRPipelineStrategy:
    name: str
    upscale_factor: float
    contrast_factor: float
    median_filter_size: int
    threshold_bias: int
    psm_sequence: list[int]
    allow_invert_retry: bool


class OCRService:
    RETRY_CONFIDENCE_THRESHOLD = 0.45

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

    def _analyze_image_quality(self, image: Image.Image) -> OCRQualityProfile:
        prepared = ImageOps.exif_transpose(image).convert("L")
        width, height = prepared.size
        area = width * height

        stats = ImageStat.Stat(prepared)
        contrast_stddev = float(stats.stddev[0]) if stats.stddev else 0.0

        blurred = prepared.filter(ImageFilter.GaussianBlur(radius=1))
        diff = ImageChops.difference(prepared, blurred)
        diff_stats = ImageStat.Stat(diff)
        noise_score = float(diff_stats.mean[0]) if diff_stats.mean else 0.0

        likely_skewed = width > 0 and height > 0 and abs((width / max(height, 1)) - 1.414) > 1.0

        return OCRQualityProfile(
            width=width,
            height=height,
            area=area,
            contrast_stddev=contrast_stddev,
            noise_score=noise_score,
            low_resolution=min(width, height) < 1000,
            low_contrast=contrast_stddev < 40.0,
            high_noise=noise_score > 12.0,
            likely_skewed=likely_skewed,
        )

    def _decide_pipeline(self, profile: OCRQualityProfile) -> OCRPipelineStrategy:
        if profile.low_resolution or (profile.low_contrast and profile.high_noise):
            return OCRPipelineStrategy(
                name="aggressive",
                upscale_factor=2.0,
                contrast_factor=1.8,
                median_filter_size=5,
                threshold_bias=-5,
                psm_sequence=[6, 11, 4],
                allow_invert_retry=True,
            )

        if profile.low_contrast or profile.high_noise or profile.likely_skewed:
            return OCRPipelineStrategy(
                name="balanced",
                upscale_factor=1.5,
                contrast_factor=1.45,
                median_filter_size=3,
                threshold_bias=0,
                psm_sequence=[6, 11],
                allow_invert_retry=True,
            )

        return OCRPipelineStrategy(
            name="light",
            upscale_factor=1.0,
            contrast_factor=1.2,
            median_filter_size=3,
            threshold_bias=3,
            psm_sequence=[6],
            allow_invert_retry=False,
        )

    def _build_binary_variant(self, grayscale: Image.Image, threshold_bias: int = 0) -> Image.Image:
        autocontrast = ImageOps.autocontrast(grayscale)
        threshold = int(mean(ImageStat.Stat(autocontrast).mean) + threshold_bias)
        threshold = max(70, min(200, threshold))
        return autocontrast.point(lambda pixel: 255 if pixel > threshold else 0, mode="L")

    def _preprocess_variants(self, image: Image.Image, strategy: OCRPipelineStrategy) -> list[Image.Image]:
        base = ImageOps.exif_transpose(image).convert("RGB")

        if strategy.upscale_factor > 1.0:
            new_size = (
                max(1, int(base.width * strategy.upscale_factor)),
                max(1, int(base.height * strategy.upscale_factor)),
            )
            base = base.resize(new_size, Image.Resampling.LANCZOS)

        grayscale = ImageOps.grayscale(base)
        denoised = grayscale.filter(ImageFilter.MedianFilter(size=strategy.median_filter_size))
        enhanced = ImageEnhance.Contrast(denoised).enhance(strategy.contrast_factor)
        sharpened = enhanced.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=2))
        binary = self._build_binary_variant(sharpened, threshold_bias=strategy.threshold_bias)
        return [sharpened, binary]

    def _score_ocr_text(self, text: str) -> float:
        cleaned = text.strip()
        if not cleaned:
            return 0.0

        total_chars = len(cleaned)
        alpha_num = sum(char.isalnum() for char in cleaned)
        allowed_chars = sum(char.isalnum() or char.isspace() or char in ".,-/:()%$" for char in cleaned)
        words = re.findall(r"[A-Za-zÀ-ÿ0-9]{2,}", cleaned)
        lines = [line.strip() for line in cleaned.splitlines() if line.strip()]

        alnum_ratio = alpha_num / max(total_chars, 1)
        valid_char_ratio = allowed_chars / max(total_chars, 1)
        word_density = min(len(words) / 12.0, 1.0)
        line_quality = min(len(lines) / 6.0, 1.0)

        return max(
            0.0,
            min(
                1.0,
                (0.35 * alnum_ratio) + (0.35 * valid_char_ratio) + (0.2 * word_density) + (0.1 * line_quality),
            ),
        )

    def _validate_ocr_output(self, text: str) -> float:
        return self._score_ocr_text(text)

    def _ocr_with_psm(self, image: Image.Image, lang: str, psm: int) -> str:
        return pytesseract.image_to_string(image, lang=lang, config=f"--oem 3 --psm {psm}")

    def _run_smart_retry(
        self,
        variants: list[Image.Image],
        lang: str,
        strategy: OCRPipelineStrategy,
        initial_best_text: str,
        initial_best_score: float,
    ) -> tuple[str, float]:
        best_text = initial_best_text
        best_score = initial_best_score
        retries_used = 0

        for psm in strategy.psm_sequence[1:]:
            if retries_used >= 2:
                break
            for variant in variants:
                candidate = self._ocr_with_psm(variant, lang=lang, psm=psm)
                score = self._validate_ocr_output(candidate)
                if score > best_score:
                    best_text = candidate
                    best_score = score
            retries_used += 1

        if strategy.allow_invert_retry and retries_used < 2:
            inverted_variants = [ImageOps.invert(variant.convert("L")) for variant in variants]
            for variant in inverted_variants:
                candidate = self._ocr_with_psm(variant, lang=lang, psm=11)
                score = self._validate_ocr_output(candidate)
                if score > best_score:
                    best_text = candidate
                    best_score = score

        return best_text, best_score

    def _ocr_image_file(self, file_path: str, lang: str = "por") -> str:
        collected_texts: list[str] = []
        with Image.open(file_path) as image:
            frame_count = getattr(image, "n_frames", 1)
            logger.info(
                "Processando imagem para OCR: format=%s size=%sx%s frames=%s",
                image.format,
                image.width,
                image.height,
                frame_count,
            )

            for frame_index, frame in enumerate(ImageSequence.Iterator(image)):
                normalized = frame.convert("RGB")
                profile = self._analyze_image_quality(normalized)
                strategy = self._decide_pipeline(profile)
                variants = self._preprocess_variants(normalized, strategy)

                best_text = ""
                best_score = 0.0
                first_psm = strategy.psm_sequence[0]

                for variant in variants:
                    candidate = self._ocr_with_psm(variant, lang=lang, psm=first_psm)
                    score = self._validate_ocr_output(candidate)
                    if score > best_score:
                        best_text = candidate
                        best_score = score

                if best_score < self.RETRY_CONFIDENCE_THRESHOLD:
                    best_text, best_score = self._run_smart_retry(
                        variants=variants,
                        lang=lang,
                        strategy=strategy,
                        initial_best_text=best_text,
                        initial_best_score=best_score,
                    )

                logger.info(
                    "OCR frame=%s strategy=%s confidence=%.2f low_res=%s low_contrast=%s high_noise=%s",
                    frame_index,
                    strategy.name,
                    best_score,
                    profile.low_resolution,
                    profile.low_contrast,
                    profile.high_noise,
                )
                collected_texts.append(best_text.strip())

        return "\n".join(text for text in collected_texts if text).strip()

    async def extract_text(self, document: Document) -> str:
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
