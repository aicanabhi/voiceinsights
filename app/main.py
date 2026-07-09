from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(
    title="VoiceInsights AI",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "VoiceInsights Backend Running 🚀"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


app.include_router(
    api_router,
    prefix="/api/v1"
)