from sqlalchemy.orm import Session

from app.models.document_metadata import DocumentMetadata

from app.models.document import Document


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
        
    @staticmethod
    def search(
        db: Session,
        key: str,
        value: str,
        user_id: int,
    ):
        return (
            db.query(
                DocumentMetadata,
                Document,
            )
            .join(
                Document,
                Document.id == DocumentMetadata.document_id,
            )
            .filter(
                Document.uploaded_by == user_id,
                DocumentMetadata.key == key,
                DocumentMetadata.value.ilike(f"%{value}%"),
            )
            .all()
        )