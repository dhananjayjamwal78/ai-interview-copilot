from typing import Union

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.health_service import (
    get_health_status,
    get_liveness_status,
    get_readiness_status,
)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return get_health_status()


@router.get("/livez", response_model=HealthResponse)
def liveness_check() -> HealthResponse:
    return get_liveness_status()


@router.get("/readyz", response_model=ReadinessResponse)
def readiness_check() -> Union[ReadinessResponse, JSONResponse]:
    readiness = get_readiness_status()
    if readiness.ready:
        return readiness
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=readiness.model_dump(),
    )
