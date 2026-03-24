"""
Database Models - Modelos de banco de dados
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class DocumentTypeEnum(str, enum.Enum):
    """Enum para tipos de documentos no banco"""
    NOTA_FISCAL = "nota_fiscal"
    COMPROVANTE_PAGAMENTO = "comprovante_pagamento"
    CONSULTA_CNPJ = "consulta_cnpj"
    UNKNOWN = "unknown"


class DocumentModel(Base):
    """Modelo de documento no banco de dados"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    document_type = Column(Enum(DocumentTypeEnum), nullable=True)
    extracted_text = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    metadata = Column(JSON, default={})


class AnalysisResultModel(Base):
    """Modelo de resultado de análise no banco de dados"""
    __tablename__ = "analysis_results"
    
    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, nullable=False, index=True)
    document_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    ai_analysis = Column(JSON, nullable=True)
    rules_validation = Column(JSON, nullable=True)
    errors = Column(JSON, default=[])
    warnings = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.now)
    metadata = Column(JSON, default={})
