from sqlalchemy.orm import Session

from app.ai.embeddings import EmbeddingService
from app.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)


class SemanticSearchService:

    @staticmethod
    def search(
        db: Session,
        query: str,
        document_id: int | None = None,
        limit: int = 5,
    ):
        query_embedding = EmbeddingService.generate_embedding(
            query
        )

        results = DocumentChunkRepository.similarity_search(
            db=db,
            query_embedding=query_embedding,
            document_id=document_id,
            limit=limit,
        )

        return results