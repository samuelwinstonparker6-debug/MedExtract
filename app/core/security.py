from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader
from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name='X-API-Key', auto_error=False)

# Routes that are accessible without an API key
_PUBLIC_PATHS = {'/health', '/docs', '/openapi.json', '/redoc'}
_PUBLIC_PREFIXES = ('/uploads/', '/api/v2/documents', '/api/v2/analytics', '/api/v2/provider-templates', '/api/v2/similarity', '/api/v2/explanation', '/similarity', '/explanation')


async def verify_api_key(request: Request, call_next):
    """
    Middleware that enforces X-API-Key authentication on all routes except
    health check, API docs, and static file serving.

    Apply via:
        app.add_middleware(BaseHTTPMiddleware, dispatch=verify_api_key)
    """
    path = request.url.path

    # Allow public paths, public API routes, and static uploads directory through without auth
    if path in _PUBLIC_PATHS or path.startswith(_PUBLIC_PREFIXES):
        return await call_next(request)

    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != settings.API_KEY:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={'detail': 'Invalid or missing API key. Provide X-API-Key header.'},
        )

    return await call_next(request)
