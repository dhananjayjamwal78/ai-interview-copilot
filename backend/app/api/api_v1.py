from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.answers import router as answers_router
from app.api.routes.auth import router as auth_router
from app.api.routes.generation import router as generation_router
from app.api.routes.health import router as health_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.interview_sessions import router as interview_sessions_router
from app.api.routes.parsing import router as parsing_router

api_router = APIRouter()
api_router.include_router(analytics_router)
api_router.include_router(answers_router)
api_router.include_router(auth_router)
api_router.include_router(generation_router)
api_router.include_router(health_router)
api_router.include_router(ingestion_router)
api_router.include_router(interview_sessions_router)
api_router.include_router(parsing_router)
