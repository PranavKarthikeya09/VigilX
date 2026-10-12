from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health & Diagnostics"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness check",
    description="Returns ok if the FastAPI server is running.",
)
async def health_check():
    return HealthResponse()


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness check",
    description="Validates active connectivity to the persistent database.",
)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    try:
        # Execute lightweight ping query
        result = await db.execute(text("SELECT 1"))
        _ = result.scalar()
        return ReadyResponse(database="connected")
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "database": f"unreachable: {str(e)}",
                "app_name": "vigilX",
            },
        )
