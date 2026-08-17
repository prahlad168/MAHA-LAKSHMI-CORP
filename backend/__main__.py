"""
MAHA LAKSHMI CORP - Backend Application
Production-grade FastAPI application with unified routing.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

# Add project root to path so 'backend' package imports resolve
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Callable

# Import routers
from backend.auth.routes import router as auth_router
from backend.dashboard.routes import router as dashboard_router
from backend.marketplace.routes import router as marketplace_router
from backend.finance.routes import router as finance_router
from backend.sales.routes import router as sales_router
from backend.products.routes import router as products_router
from backend.ai_factory.routes import router as ai_factory_router
from backend.system.routes import router as system_router
from backend.dashboard.routes import router as dashboard_extended_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from backend.db.connection import init_db
    init_db()
    logger.info("MAHA LAKSHMI CORP API started successfully")
    yield
    # Shutdown
    logger.info("MAHA LAKSHMI CORP API shutting down")

# Create FastAPI app
app = FastAPI(
    title="MAHA LAKSHMI CORP API",
    description="CEO Dashboard and Business Automation Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure for production
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)

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
    response.headers["Permissions-Policy"] = "geolocation=() microphone=() camera=()"
    return response

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = f"req-{int(time.time() * 1000)}"
    return response

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(dashboard_extended_router, prefix="/api/dashboard", tags=["Dashboard Extended"])
app.include_router(marketplace_router, prefix="/api/marketplace", tags=["Marketplace"])
app.include_router(finance_router, prefix="/api/finance", tags=["Finance"])
app.include_router(sales_router, prefix="/api/sales", tags=["Sales"])
app.include_router(products_router, prefix="/api/products", tags=["Products"])
app.include_router(ai_factory_router, prefix="/api/ai-factory", tags=["AI Factory"])
app.include_router(system_router, prefix="/api/system", tags=["System"])

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
