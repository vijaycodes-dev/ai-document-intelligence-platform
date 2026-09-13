import logging

from app.database.session import SessionLocal
from app.services.document_service import DocumentService


logger = logging.getLogger(__name__)


def process_document_task(
    document_id: int,
    user_id: int,
):
    db = SessionLocal()

    try:
        logger.info(
            "Background document processing started: document_id=%s",
            document_id,
        )

        DocumentService.process_document_background(
            db=db,
            document_id=document_id,
            user_id=user_id,
        )

        logger.info(
            "Background document processing completed: document_id=%s",
            document_id,
        )

    except Exception:
        logger.exception(
            "Background document processing failed: document_id=%s",
            document_id,
        )

    finally:
        db.close()