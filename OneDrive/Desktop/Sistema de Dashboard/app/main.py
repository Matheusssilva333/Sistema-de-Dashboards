"""
Sistema de Geração de Dashboards com Segurança Avançada
Ponto de entrada da aplicação
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.routers import auth, campaigns, insights, ad_accounts, reports
from app.security import (
    limiter,
    add_security_headers,
    security_middleware,
    security_logger,
    _rate_limit_exceeded_handler
)


# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    # Startup
    logger.info("🚀 Iniciando Sistema de Geração de Dashboards...")
    logger.info("🔒 Inicializando módulos de segurança...")
    init_db()
    logger.info("✅ Banco de dados inicializado")
    logger.info("✅ Sistema de segurança ativado")
    
    yield
    
    # Shutdown
    logger.info("👋 Encerrando aplicação...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Geração de Dashboards",
    version="2.0.0",
    description="Sistema Avançado de Geração de Dashboards com Segurança Empresarial",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Adicionar rate limiter à aplicação
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Middleware de Segurança (PRIMEIRO)
@app.middleware("http")
async def security_middleware_wrapper(request: Request, call_next):
    return await security_middleware(request, call_next)


# Middleware de Security Headers
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    return await add_security_headers(request, call_next)


# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


# Templates
templates = Jinja2Templates(directory="frontend/templates")


# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ad_accounts.router, prefix="/api/ad-accounts", tags=["Ad Accounts"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])

# Novo router de dashboards
from app.routers import dashboards
app.include_router(dashboards.router, prefix="/api/dashboards", tags=["Dashboards"])


@app.get("/")
async def root(request: Request):
    """Página inicial - Dashboard"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "app_name": settings.APP_NAME}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint para monitoramento"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "message": str(exc) if settings.DEBUG else "Ocorreu um erro inesperado"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
