from fastapi import FastAPI

from app.core.config import settings
from app.core.logging_config import setup_logging

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as document_router

from sqlalchemy import text
from app.database.session import SessionLocal
from app.core.exceptions import DocumentProcessingError
from fastapi.responses import JSONResponse

setup_logging()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend application for intelligent document management, "
        "AI-powered search, workflow automation, and cloud-native deployment."
    ),
)


@app.exception_handler(DocumentProcessingError)
async def document_processing_exception_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={
            "error": "document_processing_error",
            "message": str(exc),
        },
    )


app.include_router(auth_router)
app.include_router(document_router)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}"
    }
    
    
@app.get("/health")
async def health_check():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "healthy",
        }

    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "unhealthy",
            },
        )

    finally:
        db.close()