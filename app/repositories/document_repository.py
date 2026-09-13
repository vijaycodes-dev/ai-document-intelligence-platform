from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:

    @staticmethod
    def create(
        db: Session,
        document: Document,
    ):
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    @staticmethod
    def get_by_id(
        db: Session,
        document_id: int,
    ):
        return (
            db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    @staticmethod
    def get_all(
        db: Session,
    ):
        return db.query(Document).all()

    @staticmethod
    def get_all_by_user(
        db: Session,
        user_id: int,
    ):
        return (
            db.query(Document)
            .filter(Document.uploaded_by == user_id)
            .order_by(Document.created_at.desc())
            .all()
        )
        
    @staticmethod
    def get_paginated_by_user(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
        file_type: str | None = None,
    ):
        query = (
            db.query(Document)
            .filter(Document.uploaded_by == user_id)
        )

        # Filter by document status
        if status:
            query = query.filter(
                Document.status == status
            )

        # Filter by file type
        if file_type:
            query = query.filter(
                Document.file_type == file_type
            )

        query = query.order_by(
            Document.created_at.desc()
        )

        total = query.count()

        documents = (
            query
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return documents, total

    @staticmethod
    def get_by_id_and_user(
        db: Session,
        document_id: int,
        user_id: int,
    ):
        return (
            db.query(Document)
            .filter(
                Document.id == document_id,
                Document.uploaded_by == user_id,
            )
            .first()
        )

    @staticmethod
    def delete(
        db: Session,
        document: Document,
    ):
        db.delete(document)
        db.commit()