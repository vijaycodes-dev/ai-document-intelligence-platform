from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend application for intelligent document management, AI-powered search, workflow automation, and cloud-native deployment."
)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}"
    }