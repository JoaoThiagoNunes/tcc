from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.application.document_processor import DocumentProcessor
from app.domain.entities.document import Document
from . import schemas

router = APIRouter(tags=["Processamento do Documento"])
processor = DocumentProcessor()


async def _build_document(upload_file: UploadFile) -> Document:
    file_bytes = await upload_file.read()
    suffix = Path(upload_file.filename or "upload.bin").suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name

    return Document(
        id=str(uuid4()),
        filename=upload_file.filename or "upload.bin",
        file_path=temp_path,
        file_size=len(file_bytes),
        mime_type=upload_file.content_type or "application/octet-stream",
    )

@router.post("/process", response_model=schemas.AnalysisResponse)
async def process_document(
    file: UploadFile = File(...),
):
    try:
        document = await _build_document(file)
        result = await processor.process(document)

        if not document.extracted_text:
            raise HTTPException(
                status_code=500,
                detail="Nao foi possivel extrair texto do arquivo enviado.",
            )

        return schemas.AnalysisResponse(
            status=schemas.AnalysisStatus(result.status.value),
            document_id=result.document_id,
            document_type=schemas.DocumentType(result.document_type),
            classification_confidence=(result.metadata or {}).get("classification_confidence"),
            classification_reason=(result.metadata or {}).get("classification_reason"),
            classification_scores=(result.metadata or {}).get("classification_scores"),
            errors=result.errors or None,
            text=document.extracted_text,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

