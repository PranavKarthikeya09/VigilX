import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="vigilX API",
        description="Digital Risk Protection Platform — Brand Impersonation Detection across Social & App Ecosystems",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and Timing Middleware
    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # Standardized Exception Handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers or {},
            content={
                "status": exc.status_code,
                "error_code": "AUTHENTICATION_ERROR" if exc.status_code == 401 else "HTTP_ERROR",
                "message": exc.detail,
                "details": [],
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    # Mount Routes
    # Root diagnostic endpoints
    app.include_router(health_router)

    # API v1 Versioned endpoints
    app.include_router(auth_router, prefix="/api/v1")

    return app


app = create_app()
