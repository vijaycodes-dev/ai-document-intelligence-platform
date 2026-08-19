from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.core.config import settings
from app.api.v1.documents import router as document_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend application for intelligent document management, AI-powered search, workflow automation, and cloud-native deployment."
)

app.include_router(auth_router)
app.include_router(document_router)
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}"
    }
    

