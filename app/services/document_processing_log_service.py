from sqlalchemy.orm import Session

from app.repositories.document_processing_log_repository import (
    DocumentProcessingLogRepository,
)


class DocumentProcessingLogService:

    @staticmethod
    def log(
        db: Session,
        document_id: int,
        stage: str,
        status: str,
        message: str | None = None,
    ):
        return DocumentProcessingLogRepository.create(
            db=db,
            document_id=document_id,
            stage=stage,
            status=status,
            message=message,
        )

    @staticmethod
    def get_history(
        db: Session,
        document_id: int,
    ):
        return DocumentProcessingLogRepository.get_by_document_id(
            db=db,
            document_id=document_id,
        )

    @staticmethod
    def clear_history(
        db: Session,
        document_id: int,
    ):
        DocumentProcessingLogRepository.delete_by_document_id(
            db=db,
            document_id=document_id,
        )