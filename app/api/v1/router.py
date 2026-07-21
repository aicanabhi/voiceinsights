from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.organization import router as organization_router
from app.api.v1.team import router as team_router
from app.api.v1.user import router as user_router
from app.api.v1.media import router as media_router
from app.api.v1.transcript import router as transcript_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(organization_router)
api_router.include_router(team_router)
api_router.include_router(user_router)
api_router.include_router(media_router)
api_router.include_router(transcript_router)
api_router.include_router(analysis_router)
api_router.include_router(dashboard_router)