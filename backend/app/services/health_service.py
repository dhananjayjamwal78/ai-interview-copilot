from app.core.config import settings
from app.db import check_database_connection
from app.schemas.health import HealthResponse, ReadinessResponse


def get_health_status() -> HealthResponse:
    database_connected = check_database_connection()
    return HealthResponse(
        status="ok" if database_connected else "degraded",
        service="backend",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION,
        database="connected" if database_connected else "unavailable",
    )


def get_liveness_status() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="backend",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION,
        database="unknown",
    )


def get_readiness_status() -> ReadinessResponse:
    database_connected = check_database_connection()
    return ReadinessResponse(
        status="ok" if database_connected else "degraded",
        service="backend",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION,
        database="connected" if database_connected else "unavailable",
        ready=database_connected,
    )
