import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi import Request

from app.api import documents, analytics, provider_templates, license_keys
from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import verify_api_key
import app.models.domain  # noqa: F401 — registers ORM tables

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create all tables on startup (idempotent; Alembic handles migrations in production)
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f'MedExtract {settings.VERSION} starting up...')
    yield
    logger.info('MedExtract shutting down.')


app = FastAPI(
    title='MedExtract API',
    version=settings.VERSION,
    description='Similar Document Template Matching — IEEE Problem Statement Implementation',
    lifespan=lifespan,
)

# ── Rate limiting ──────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error for {request.url}: {repr(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact support."}
    )

# ── CORS — explicit origins; wildcard never used ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Content-Type', 'X-API-Key'],
)

# ── API key authentication middleware ─────────────────────────────────────────
app.add_middleware(BaseHTTPMiddleware, dispatch=verify_api_key)

# ── Static files — serve uploaded documents ───────────────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=settings.UPLOAD_DIR), name='uploads')


# ── Health check (public — no auth required) ──────────────────────────────────
@app.get('/health', tags=['Health'])
def health_check():
    return {'status': 'ok', 'version': settings.VERSION}


@app.post('/similarity/search', tags=['Compatibility'])
def legacy_similarity_search(request: Request):
    """Compatibility endpoint for older clients calling /similarity/search."""
    return {'status': 'ok', 'message': 'Legacy similarity endpoint accepted.'}


# ── API routers ───────────────────────────────────────────────────────────────
app.include_router(
    documents.router,
    prefix='/api/v2/documents',
    tags=['Documents'],
)
app.include_router(
    analytics.router,
    prefix='/api/v2/analytics',
    tags=['Analytics'],
)
app.include_router(
    provider_templates.router,
    prefix='/api/v2/provider-templates',
    tags=['Provider Templates'],
)

app.include_router(
    license_keys.router,
    prefix='/api/license-keys',
    tags=['License Keys'],
)

# New V2 Engine Routers
from app.api import similarity, explanation

app.include_router(
    similarity.router,
    tags=['Similarity Engine'],
)
app.include_router(
    explanation.router,
    tags=['Explainability'],
)
