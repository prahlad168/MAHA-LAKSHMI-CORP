"""
MAHA LAKSHMI CORP - Backend API Gateway
Unified FastAPI application for the entire platform.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
import time
import logging
import os
from pathlib import Path
from typing import Callable

from backend.db.connection import init_db, get_db
from backend.shared.config import settings
from backend.auth.routes import router as auth_router
from backend.dashboard.routes import router as dashboard_router
from backend.dashboard.revenue_routes import router as revenue_router
from backend.marketplace.routes import router as marketplace_router
from backend.marketplace.webhooks import router as webhook_router
from backend.finance.routes import router as finance_router
from backend.sales.routes import router as sales_router
from backend.products.routes import router as products_router
from backend.ai_factory.routes import router as ai_factory_router
from backend.system.routes import router as system_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Create FastAPI app
app = FastAPI(
    title="MAHA LAKSHMI CORP API",
    description="CEO Dashboard and Business Automation Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(revenue_router, prefix="/api/dashboard", tags=["Dashboard Revenue"])
app.include_router(marketplace_router, prefix="/api/marketplace", tags=["Marketplace"])
app.include_router(webhook_router, prefix="/api/marketplace", tags=["Marketplace Webhooks"])
app.include_router(finance_router, prefix="/api/finance", tags=["Finance"])
app.include_router(sales_router, prefix="/api/sales", tags=["Sales"])
app.include_router(products_router, prefix="/api/products", tags=["Products"])
app.include_router(ai_factory_router, prefix="/api/ai-factory", tags=["AI Factory"])
app.include_router(system_router, prefix="/api/system", tags=["System"])

# Security Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure for production
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Middleware
_ALLOWED_ORIGINS = settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = f"req-{int(time.time() * 1000)}"
    return response

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next: Callable):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss:; frame-ancestors 'none';"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "MAHA LAKSHMI CORP API"
    }

@app.get("/api/health", tags=["Health"])
async def api_health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "MAHA LAKSHMI CORP API"
    }

# Global exception handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request.headers.get("X-Request-ID", "unknown")
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("MAHA LAKSHMI CORP API started successfully")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("MAHA LAKSHMI CORP API shutting down")

# Static frontend mounts
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
for _static_dir in [_PROJECT_ROOT / "maha-lakshmi", _PROJECT_ROOT / "maha-command-center"]:
    if _static_dir.exists():
        app.mount(
            f"/{_static_dir.name}",
            StaticFiles(directory=str(_static_dir), html=True),
            name=_static_dir.name,
        )

# Serve root index when present
_ROOT_INDEX = _PROJECT_ROOT / "index.html"
if _ROOT_INDEX.exists():
    @app.get("/", include_in_schema=False)
    async def serve_root_index():
        return FileResponse(str(_ROOT_INDEX))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
