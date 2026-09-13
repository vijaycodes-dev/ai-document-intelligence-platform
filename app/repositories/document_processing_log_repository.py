from sqlalchemy.orm import Session

from app.models.document_processing_log import DocumentProcessingLog


class DocumentProcessingLogRepository:

    @staticmethod
    def create(
        db: Session,
        document_id: int,
        stage: str,
        status: str,
        message: str | None = None,
    ):
        log = DocumentProcessingLog(
            document_id=document_id,
            stage=stage,
            status=status,
            message=message,
        )

        db.add(log)
        db.flush()

        return log

    @staticmethod
    def get_by_document_id(
        db: Session,
        document_id: int,
    ):
        return (
            db.query(DocumentProcessingLog)
            .filter(
                DocumentProcessingLog.document_id == document_id
            )
            .order_by(
                DocumentProcessingLog.created_at.asc()
            )
            .all()
        )

    @staticmethod
    def delete_by_document_id(
        db: Session,
        document_id: int,
    ):
        (
            db.query(DocumentProcessingLog)
            .filter(
                DocumentProcessingLog.document_id == document_id
            )
            .delete(
                synchronize_session=False
            )
        )

        db.flush()