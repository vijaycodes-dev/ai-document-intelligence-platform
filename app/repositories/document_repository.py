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