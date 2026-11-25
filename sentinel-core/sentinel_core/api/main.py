"""
Sentinel API - FastAPI Application

Production-grade REST API with WebSocket support for real-time task updates.
"""

from fastapi import Depends, FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routers import scan, plan, preview, execute, undo, tasks, websocket
from .websocket.manager import ws_manager
from .config import settings
from .auth import require_access
from .models.responses import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the WebSocket manager.
    """
    # Startup
    logger.info("Sentinel API starting up...")
    await ws_manager.startup()
    logger.info("Sentinel API ready")
    
    yield
    
    # Shutdown
    logger.info("Sentinel API shutting down...")
    await ws_manager.shutdown()
    logger.info("Sentinel API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Sentinel API",
    description="AI-powered file organization service with real-time updates",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - localhost only for security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After"],
)

# Loopback host validation also applies to WebSocket handshakes.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

# Include routers
app.include_router(scan.router, prefix=settings.api_prefix, dependencies=[Depends(require_access)], tags=["scan"])
app.include_router(plan.router, prefix=settings.api_prefix, dependencies=[Depends(require_access)], tags=["plan"])
app.include_router(preview.router, prefix=settings.api_prefix, dependencies=[Depends(require_access)], tags=["preview"])
app.include_router(execute.router, prefix=settings.api_prefix, dependencies=[Depends(require_access)], tags=["execute"])
app.include_router(undo.router, prefix=settings.api_prefix, dependencies=[Depends(require_access)], tags=["undo"])
app.include_router(tasks.router, prefix=settings.api_prefix, dependencies=[Depends(require_access)], tags=["tasks"])
app.include_router(websocket.router, tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint - redirects to docs."""
    return {
        "message": "Sentinel API",
        "version": "0.1.0",
        "docs": "/docs",
        "websocket": "/ws/events"
    }


@app.get(f"{settings.api_prefix}/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        HealthResponse with server status
        
    Example:
        GET /api/health
    """
    # TODO: Check database connection
    db_connected = True
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        database_connected=db_connected
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "sentinel_core.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info"
    )
