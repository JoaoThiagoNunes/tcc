from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import Settings
from app.api import routes
from app.infrastructure.logging.logger import get_logger

# Configurações
settings = Settings()
logger = get_logger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="TCC",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(routes.router)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Iniciando {settings.app_name} v{settings.app_version}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Encerrando aplicação")


@app.get("/")
async def root():
    return {
        "message": f"{settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs"
    }
