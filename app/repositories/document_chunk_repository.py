from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:

    @staticmethod
    def similarity_search(
        db: Session,
        query_embedding: list[float],
        document_id: int | None = None,
        limit: int = 5,
    ):
        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        )

        query = db.query(
            DocumentChunk,
            distance.label("distance"),
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