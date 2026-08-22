from sqlalchemy.orm import Session

from app.repositories.document_metadata_repository import (
    DocumentMetadataRepository,
)


class DocumentMetadataService:

    @staticmethod
    def save_metadata(
        db: Session,
        document_id: int,
        metadata: dict,
    ):
        # Remove existing metadata first.
        DocumentMetadataRepository.delete_by_document_id(
            db=db,
            document_id=document_id,
        )

        saved_metadata = []

        for key, value in metadata.items():

            # Ignore empty values.
            if value is None or str(value).strip() == "":
                continue

            entry = DocumentMetadataRepository.create(
                db=db,
                document_id=document_id,
                key=key,
                value=str(value).strip(),
            )

            saved_metadata.append(entry)

        return saved_metadata

    @staticmethod
    def get_metadata(
        db: Session,
        document_id: int,
    ):
        return DocumentMetadataRepository.get_by_document_id(
            db=db,
            document_id=document_id,
        )
        
    
    @staticmethod
    def search_metadata(
        db: Session,
        key: str,
        value: str,
        user_id: int,
    ):
        return DocumentMetadataRepository.search(
            db=db,
            key=key,
            value=value,
            user_id=user_id,
        )