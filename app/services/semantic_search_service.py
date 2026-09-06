from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.embeddings import EmbeddingService
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.repositories.document_repository import DocumentRepository


class SemanticSearchService:

    SIMILARITY_THRESHOLD = 0.15

    @staticmethod
    def search(
        db: Session,
        query: str,
        user_id: int,
        document_id: int | None = None,
        limit: int = 5,
    ):
        query = query.strip()

        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty.",
            )

        # Validate ownership when searching a specific document
        if document_id is not None:
            document = DocumentRepository.get_by_id_and_user(
                db=db,
                document_id=document_id,
                user_id=user_id,
            )

            if document is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found.",
                )

        limit = max(1, min(limit, 10))

        try:
            query_embedding = EmbeddingService.generate_embedding(query)

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Semantic search service is temporarily unavailable.",
            )

        try:
            results = DocumentChunkRepository.similarity_search(
                db=db,
                query_embedding=query_embedding,
                user_id=user_id,
                document_id=document_id,
                limit=limit,
            )

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to perform semantic search.",
            )

        return [
            (chunk, distance)
            for chunk, distance in results
            if (1 - distance) >= SemanticSearchService.SIMILARITY_THRESHOLD
        ]