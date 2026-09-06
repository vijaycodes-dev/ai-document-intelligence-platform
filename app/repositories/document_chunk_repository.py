from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:

    @staticmethod
    def similarity_search(
        db: Session,
        query_embedding: list[float],
        user_id: int,
        document_id: int | None = None,
        limit: int = 5,
    ):
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        query = (
            db.query(
                DocumentChunk,
                distance.label("distance"),
            )
            .join(
                Document,
                DocumentChunk.document_id == Document.id,
            )
            .filter(
                Document.uploaded_by == user_id
            )
        )

        if document_id is not None:
            query = query.filter(
                DocumentChunk.document_id == document_id
            )

        return (
            query
            .order_by(distance)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_document_id(
        db: Session,
        document_id: int,
    ):
        return (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id
            )
            .order_by(DocumentChunk.chunk_index)
            .all()
        )