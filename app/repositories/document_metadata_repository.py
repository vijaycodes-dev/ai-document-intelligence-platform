from sqlalchemy.orm import Session

from app.models.document_metadata import DocumentMetadata


class DocumentMetadataRepository:

    @staticmethod
    def create(
        db: Session,
        document_id: int,
        key: str,
        value: str,
    ):
        metadata = DocumentMetadata(
            document_id=document_id,
            key=key,
            value=value,
        )

        db.add(metadata)
        db.flush()

        return metadata

    @staticmethod
    def get_by_document_id(
        db: Session,
        document_id: int,
    ):
        return (
            db.query(DocumentMetadata)
            .filter(DocumentMetadata.document_id == document_id)
            .all()
        )

    @staticmethod
    def delete_by_document_id(
        db: Session,
        document_id: int,
    ):
        (
            db.query(DocumentMetadata)
            .filter(DocumentMetadata.document_id == document_id)
            .delete()
        )

        db.flush()