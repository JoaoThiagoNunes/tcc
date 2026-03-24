"""
Camada de entrada (controllers)
"""
from fastapi import APIRouter, Depends, UploadFile, File
from typing import List
from . import schemas, dependencies

router = APIRouter(prefix="/api/v1", tags=["document-processing"])


@router.post("/process", response_model=schemas.AnalysisResponse)
async def process_document(
    file: UploadFile = File(...),
    deps: dict = Depends(dependencies.get_dependencies)
):
    """
    Endpoint principal para processamento de documentos
    """
    # TODO: Implementar processamento
    return schemas.AnalysisResponse(
        status=schemas.AnalysisStatus.PROCESSING,
        document_id="123"
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
